"""CF-04: the smallest truthful reusable local analysis pipeline.

Replaces the one-time manual CF-02 process with real application code:
validate consent/media -> probe -> extract audio -> transcribe (local
faster-whisper) -> sample frames deterministically -> produce
evidence-linked observations -> persist with explicit per-stage state.

Honesty rules enforced here, not just documented:
- Every stage transition is persisted immediately, so a crash leaves an
  honest partial state ("transcribing", "failed"), never a false
  "completed".
- Observations only claim what the real media supports. This pipeline has
  NO vision model: visual topics (framing, background, captions,
  gestures, editing) are persisted as `unknown` with extracted frames
  attached as evidence for human review -- never invented.
- Single-example findings are labeled as such; nothing is promoted to a
  stable creator habit from one video.
- No network service is called. Transcription runs locally; the model in
  use is recorded in engine_info.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from app import repository
from app.models import (
    MAX_UPLOAD_BYTES,
    AnalysisRun,
    FrameEvidence,
    PipelineObservation,
    SourceAsset,
    TranscriptSegment,
)
from app.storage import StorageBackend

MAX_ANALYSIS_DURATION_SECONDS = 15 * 60
MAX_SAMPLED_FRAMES = 12
WHISPER_MODEL = "base"
CTA_KEYWORDS = ("comment", "follow", "subscribe", "like", "share", "link", "dm", "sign up")


class PipelineRejected(RuntimeError):
    """Raised for conditions that prevent even starting a run (missing
    source, inadequate consent, duplicate in-flight run). The caller maps
    this to an honest HTTP error; nothing is persisted as a run."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ffmpeg_exe() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def _default_transcriber(wav_path: str) -> tuple[list[TranscriptSegment], dict[str, str]]:
    """Real local transcription. Imported lazily so tests can inject a
    fake without ever loading the model."""
    from faster_whisper import WhisperModel

    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    segments, info = model.transcribe(wav_path, word_timestamps=False)
    out = [
        TranscriptSegment(
            start_seconds=round(s.start, 2), end_seconds=round(s.end, 2), text=s.text.strip()
        )
        for s in segments
    ]
    engine = {
        "transcription_engine": "faster-whisper",
        "transcription_model": WHISPER_MODEL,
        "transcription_device": "cpu int8",
        "detected_language": getattr(info, "language", "unknown"),
    }
    return out, engine


def probe_media(video_path: str) -> dict:
    """Parse real media metadata from ffmpeg's stream analysis. Raises
    ValueError for media ffmpeg cannot parse at all."""
    result = subprocess.run(
        [_ffmpeg_exe(), "-i", video_path, "-f", "null", "-t", "0.1", "-"],
        capture_output=True,
        text=True,
    )
    stderr = result.stderr
    probe: dict = {"has_audio": False, "has_video": False}

    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", stderr)
    if not m:
        raise ValueError("ffmpeg could not determine a duration for this file")
    h, mi, s = m.groups()
    probe["duration_seconds"] = round(int(h) * 3600 + int(mi) * 60 + float(s), 2)

    vm = re.search(r"Stream #[^\n]*Video: (\w+)[^\n]*?(\d{2,5})x(\d{2,5})", stderr)
    if vm:
        probe["has_video"] = True
        probe["video_codec"] = vm.group(1)
        probe["width"] = int(vm.group(2))
        probe["height"] = int(vm.group(3))
        probe["orientation"] = (
            "vertical" if probe["height"] > probe["width"] else "horizontal-or-square"
        )
        fm = re.search(r"([\d.]+) fps", stderr)
        if fm:
            probe["fps"] = float(fm.group(1))
    am = re.search(r"Stream #[^\n]*Audio: (\w+)[^\n]*?(\d+) Hz, (\w+)", stderr)
    if am:
        probe["has_audio"] = True
        probe["audio_codec"] = am.group(1)
        probe["audio_sample_rate_hz"] = int(am.group(2))
        probe["audio_channels"] = am.group(3)
    if not probe["has_video"]:
        raise ValueError("no video stream found in this file")
    return probe


def choose_frame_timestamps(duration: float, transcript: list[TranscriptSegment]) -> list[float]:
    """Deterministic sampling: near-start, each transcript-segment start,
    and near-end -- deduplicated, capped at MAX_SAMPLED_FRAMES by even
    thinning (never random)."""
    candidates = [min(0.5, duration / 2)]
    candidates += [s.start_seconds for s in transcript if 0 < s.start_seconds < duration]
    candidates.append(max(duration - 0.5, duration / 2))
    seen: list[float] = []
    for t in candidates:
        t = round(min(max(t, 0.0), max(duration - 0.05, 0.0)), 2)
        if all(abs(t - existing) > 0.75 for existing in seen):
            seen.append(t)
    if len(seen) > MAX_SAMPLED_FRAMES:
        step = len(seen) / MAX_SAMPLED_FRAMES
        seen = [seen[int(i * step)] for i in range(MAX_SAMPLED_FRAMES)]
    return sorted(seen)


def build_observations(
    probe: dict, transcript: list[TranscriptSegment], frames: list[FrameEvidence]
) -> tuple[list[PipelineObservation], list[str]]:
    obs: list[PipelineObservation] = []
    limitations = [
        "All findings come from a single example and must not be treated as "
        "stable creator habits until multiple videos confirm them.",
    ]
    single = "Observed in this video only."

    if transcript:
        first = transcript[0]
        obs.append(PipelineObservation(
            topic="opening_hook",
            statement=f'The video opens with: "{first.text}"',
            evidence_type="transcript_segment",
            evidence_ref=f"{first.start_seconds}-{first.end_seconds}s",
            confidence="medium",
            classification="directly_observed",
            limitation="Transcript text comes from local ASR and may mishear words. " + single,
        ))

        total_words = sum(len(s.text.split()) for s in transcript)
        spoken_span = transcript[-1].end_seconds - transcript[0].start_seconds
        if spoken_span > 0:
            obs.append(PipelineObservation(
                topic="pacing",
                statement=(
                    f"{total_words} words across {round(spoken_span, 1)}s of speech "
                    f"(~{round(total_words / spoken_span * 60)} words/minute overall)."
                ),
                evidence_type="derived_metric",
                evidence_ref=f"transcript segments 0-{len(transcript) - 1}",
                confidence="medium",
                classification="directly_observed",
                limitation="Derived from ASR segment timing, not a manual count. " + single,
            ))
            rates = [
                (s, len(s.text.split()) / max(s.end_seconds - s.start_seconds, 0.1))
                for s in transcript
            ]
            fastest = max(rates, key=lambda r: r[1])
            slowest = min(rates, key=lambda r: r[1])
            if fastest[1] > slowest[1] * 1.4:
                obs.append(PipelineObservation(
                    topic="pacing",
                    statement=(
                        f"Speech rate varies noticeably: fastest around "
                        f"{fastest[0].start_seconds}s, slowest around {slowest[0].start_seconds}s."
                    ),
                    evidence_type="derived_metric",
                    evidence_ref=f"{fastest[0].start_seconds}s vs {slowest[0].start_seconds}s",
                    confidence="medium",
                    classification="inferred",
                    limitation="Rate inferred from ASR timestamps per segment. " + single,
                ))

        tail_text = " ".join(s.text.lower() for s in transcript[-2:])
        hit = next((k for k in CTA_KEYWORDS if k in tail_text), None)
        if hit:
            obs.append(PipelineObservation(
                topic="call_to_action",
                statement=f'The closing lines contain a call to action ("{hit}"): '
                          f'"{transcript[-1].text}"',
                evidence_type="transcript_segment",
                evidence_ref=f"{transcript[-1].start_seconds}-{transcript[-1].end_seconds}s",
                confidence="medium",
                classification="directly_observed",
                limitation=single,
            ))
        else:
            obs.append(PipelineObservation(
                topic="call_to_action",
                statement="No explicit call-to-action keyword was detected in the closing lines.",
                evidence_type="transcript_segment",
                evidence_ref="final two transcript segments",
                confidence="low",
                classification="inferred",
                limitation="Keyword scan only; a visual or implied CTA would not be detected. " + single,
            ))

        obs.append(PipelineObservation(
            topic="content_structure",
            statement=f"{len(transcript)} spoken segments across "
                      f"{probe.get('duration_seconds', '?')}s of video.",
            evidence_type="derived_metric",
            evidence_ref="full transcript",
            confidence="high",
            classification="directly_observed",
            limitation=single,
        ))

    obs.append(PipelineObservation(
        topic="audio_treatment",
        statement=(
            f"Audio present: {probe.get('audio_codec', 'unknown codec')}, "
            f"{probe.get('audio_sample_rate_hz', '?')} Hz, {probe.get('audio_channels', '?')}."
            if probe.get("has_audio")
            else "This video has no audio stream."
        ),
        evidence_type="media_probe",
        evidence_ref="ffmpeg stream analysis",
        confidence="high",
        classification="directly_observed",
        limitation=None,
    ))
    if probe.get("has_video"):
        obs.append(PipelineObservation(
            topic="format",
            statement=f"{probe.get('width')}x{probe.get('height')} "
                      f"({probe.get('orientation')}), {probe.get('fps', '?')} fps, "
                      f"{probe.get('video_codec')}.",
            evidence_type="media_probe",
            evidence_ref="ffmpeg stream analysis",
            confidence="high",
            classification="directly_observed",
            limitation=None,
        ))

    frame_refs = ", ".join(f"{f.timestamp_seconds}s" for f in frames) or "none"
    for visual_topic in ("framing", "background_studio", "on_screen_captions", "gestures_expressions", "editing_rhythm"):
        obs.append(PipelineObservation(
            topic=visual_topic,
            statement=(
                "This pipeline has no vision model and cannot determine this "
                "automatically. Frames were extracted at the listed timestamps "
                "for human review."
            ),
            evidence_type="frame_available_for_human_review",
            evidence_ref=frame_refs,
            confidence="low",
            classification="unknown",
            limitation="Requires human review of the extracted frames or a future vision-capable stage.",
        ))

    if not transcript and probe.get("has_audio"):
        limitations.append("Audio was present but transcription produced no segments.")
    if not probe.get("has_audio"):
        limitations.append("No audio stream: transcript-based observations are unavailable.")
    return obs, limitations


def run_analysis(
    storage: StorageBackend,
    project_id: str,
    source_id: str,
    transcriber: Callable[[str], tuple[list[TranscriptSegment], dict[str, str]]] | None = None,
) -> AnalysisRun:
    """Execute the full pipeline for one uploaded source. Persists state
    after every stage; returns the final persisted run."""
    source = repository.get_source(storage, project_id, source_id)
    if source is None:
        raise PipelineRejected("Source not found for this project.")
    consent = repository.get_consent(storage, project_id, source.consent_id)
    if consent is None:
        raise PipelineRejected("No consent record exists for this source.")
    if not any("analysis" in u.lower() for u in consent.permitted_uses):
        raise PipelineRejected(
            "The persisted consent record does not include analysis in its permitted uses."
        )
    existing = repository.get_analysis_run(storage, project_id, source_id)
    if existing is not None and existing.state not in ("failed",):
        raise PipelineRejected(
            f"An analysis run already exists for this source (state: {existing.state}). "
            "Duplicate concurrent analysis is not allowed."
        )

    run = AnalysisRun(
        project_id=project_id,
        source_id=source_id,
        consent_id=source.consent_id,
        input_checksum_sha256=source.checksum_sha256,
    )

    def advance(state):
        run.state = state
        run.stage_timestamps[state] = _now()
        repository.save_analysis_run(storage, run)

    advance("queued")

    video_bytes = storage.get_object(source.storage_key)
    if hashlib.sha256(video_bytes).hexdigest() != source.checksum_sha256:
        run.errors.append("Stored video bytes do not match the recorded upload checksum.")
        advance("failed")
        return run
    if len(video_bytes) > MAX_UPLOAD_BYTES:
        run.errors.append("Stored video exceeds the maximum analyzable size.")
        advance("failed")
        return run

    with tempfile.TemporaryDirectory(prefix="cf04_") as tmp:
        video_path = str(Path(tmp) / "input_video")
        Path(video_path).write_bytes(video_bytes)

        advance("probing")
        try:
            run.media_probe = probe_media(video_path)
        except (ValueError, OSError) as exc:
            run.errors.append(f"Media probing failed: {exc}")
            advance("failed")
            return run
        if run.media_probe["duration_seconds"] > MAX_ANALYSIS_DURATION_SECONDS:
            run.errors.append(
                f"Video duration {run.media_probe['duration_seconds']}s exceeds the "
                f"{MAX_ANALYSIS_DURATION_SECONDS}s analysis cap."
            )
            advance("failed")
            return run
        run.engine_info["media_tool"] = "ffmpeg (imageio-ffmpeg bundled binary)"

        transcription_failed = False
        if run.media_probe.get("has_audio"):
            advance("transcribing")
            wav_path = str(Path(tmp) / "audio.wav")
            extract = subprocess.run(
                [_ffmpeg_exe(), "-y", "-i", video_path, "-ar", "16000", "-ac", "1", wav_path],
                capture_output=True,
            )
            if extract.returncode != 0 or not Path(wav_path).exists():
                run.errors.append("Audio extraction failed.")
                transcription_failed = True
            else:
                try:
                    segments, engine = (transcriber or _default_transcriber)(wav_path)
                    run.transcript = segments
                    run.engine_info.update(engine)
                except Exception as exc:  # noqa: BLE001 -- any engine failure must persist honestly
                    run.errors.append(f"Transcription failed: {type(exc).__name__}: {exc}")
                    transcription_failed = True

        advance("sampling_frames")
        timestamps = choose_frame_timestamps(run.media_probe["duration_seconds"], run.transcript)
        for i, ts in enumerate(timestamps):
            frame_path = str(Path(tmp) / f"frame_{i:02d}.jpg")
            grab = subprocess.run(
                [_ffmpeg_exe(), "-y", "-ss", f"{ts:.2f}", "-i", video_path,
                 "-frames:v", "1", "-q:v", "3", frame_path],
                capture_output=True,
            )
            if grab.returncode != 0 or not Path(frame_path).exists():
                run.errors.append(f"Frame extraction failed at {ts}s.")
                continue
            frame_bytes = Path(frame_path).read_bytes()
            key = repository.analysis_frame_key(project_id, source_id, run.id, i)
            storage.put_object(key, frame_bytes, "image/jpeg")
            run.frames.append(FrameEvidence(
                timestamp_seconds=ts,
                storage_key=key,
                checksum_sha256=hashlib.sha256(frame_bytes).hexdigest(),
            ))

        advance("analyzing")
        run.observations, run.limitations = build_observations(
            run.media_probe, run.transcript, run.frames
        )

        if transcription_failed or (run.media_probe.get("has_audio") and not run.transcript):
            advance("partially_completed")
        elif run.errors:
            advance("partially_completed")
        else:
            advance("completed")
    return run
