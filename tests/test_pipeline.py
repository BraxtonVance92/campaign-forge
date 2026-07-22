"""CF-04 pipeline tests. Media stages (probe, audio extraction, frame
sampling) are exercised against REAL tiny generated fixtures (ffmpeg
color+tone sources -- non-identifying synthetic media, never creator
footage). Transcription uses an injected fake engine so no model is
downloaded in tests; the transcriber interface itself is what's under
test, and the real faster-whisper engine is exercised separately in the
recorded acceptance run (docs/verification/CF-04 receipt)."""

import hashlib
import json
import subprocess

import pytest
from fastapi.testclient import TestClient

from app import pipeline, repository
from app.main import app, templates
from app.models import (
    AnalysisRun,
    ConsentRecord,
    FrameEvidence,
    PipelineObservation,
    Project,
    SourceAsset,
    TranscriptSegment,
)
from app.routes import projects as projects_routes
from app.storage import InMemoryStorage, LocalDiskStorage


def _ffmpeg():
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


@pytest.fixture(scope="session")
def fixture_video_with_audio(tmp_path_factory):
    """Real 1.2s 160x284 (vertical) h264+aac video: color test source +
    440Hz tone. Synthetic and non-identifying."""
    path = tmp_path_factory.mktemp("media") / "fixture_av.mp4"
    subprocess.run(
        [_ffmpeg(), "-y",
         "-f", "lavfi", "-i", "testsrc=size=160x284:rate=12:duration=1.2",
         "-f", "lavfi", "-i", "sine=frequency=440:duration=1.2",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(path)],
        capture_output=True, check=True,
    )
    return path.read_bytes()


@pytest.fixture(scope="session")
def fixture_video_no_audio(tmp_path_factory):
    path = tmp_path_factory.mktemp("media") / "fixture_v.mp4"
    subprocess.run(
        [_ffmpeg(), "-y",
         "-f", "lavfi", "-i", "testsrc=size=160x120:rate=12:duration=1.0",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)],
        capture_output=True, check=True,
    )
    return path.read_bytes()


def fake_transcriber(segments=None):
    def _t(wav_path):
        segs = segments if segments is not None else [
            TranscriptSegment(start_seconds=0.0, end_seconds=0.6, text="hello there everyone"),
            TranscriptSegment(start_seconds=0.6, end_seconds=1.1, text="comment below for more"),
        ]
        return segs, {"transcription_engine": "fake-test-engine", "transcription_model": "none"}
    return _t


def failing_transcriber(wav_path):
    raise RuntimeError("simulated engine crash")


def _setup_source(storage, video_bytes, permitted_uses=("analysis",), project=None):
    project = project or Project(name="Pipeline Test")
    repository.save_project(storage, project)
    consent = ConsentRecord(
        project_id=project.id, statement="I authorize this for testing.",
        permitted_uses=list(permitted_uses),
    )
    repository.save_consent(storage, consent)
    source = SourceAsset(
        project_id=project.id, consent_id=consent.id, original_filename="clip.mp4",
        content_type="video/mp4", size_bytes=len(video_bytes),
        checksum_sha256=hashlib.sha256(video_bytes).hexdigest(),
        storage_key=repository.source_original_key(project.id, "sid", "clip.mp4"),
        storage_backend="local-disk-fallback",
    )
    source.storage_key = repository.source_original_key(project.id, source.id, "clip.mp4")
    repository.save_source(storage, source, video_bytes)
    return project, source


# --- rejection paths (no run persisted) ---

def test_missing_source_rejected():
    storage = InMemoryStorage()
    with pytest.raises(pipeline.PipelineRejected, match="Source not found"):
        pipeline.run_analysis(storage, "nope", "nope")
    assert repository.get_analysis_run(storage, "nope", "nope") is None


def test_consent_without_analysis_use_rejected(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(
        storage, fixture_video_with_audio, permitted_uses=("display only",)
    )
    with pytest.raises(pipeline.PipelineRejected, match="does not include analysis"):
        pipeline.run_analysis(storage, project.id, source.id)
    assert repository.get_analysis_run(storage, project.id, source.id) is None


def test_missing_consent_record_rejected(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    source.consent_id = "does-not-exist"
    repository.save_source(storage, source, fixture_video_with_audio)
    with pytest.raises(pipeline.PipelineRejected, match="No consent record"):
        pipeline.run_analysis(storage, project.id, source.id)


def test_duplicate_run_rejected(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())
    with pytest.raises(pipeline.PipelineRejected, match="already exists"):
        pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())


def test_failed_run_can_be_retried(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    corrupt = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 500
    storage.put_object(source.storage_key, corrupt, "video/mp4")
    source.checksum_sha256 = hashlib.sha256(corrupt).hexdigest()
    repository.save_source(storage, source, corrupt)
    first = pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())
    assert first.state == "failed"
    # A failed run does not block a retry.
    storage.put_object(source.storage_key, corrupt, "video/mp4")
    second = pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())
    assert second.state == "failed"  # still corrupt, but the retry was allowed


# --- honest failure states ---

def test_corrupt_media_fails_honestly(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    corrupt = b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 2048
    storage.put_object(source.storage_key, corrupt, "video/mp4")
    source.checksum_sha256 = hashlib.sha256(corrupt).hexdigest()
    repository.save_source(storage, source, corrupt)
    run = pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())
    assert run.state == "failed"
    assert any("probing failed" in e.lower() for e in run.errors)
    persisted = repository.get_analysis_run(storage, project.id, source.id)
    assert persisted.state == "failed"


def test_checksum_mismatch_fails_before_any_processing(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    source.checksum_sha256 = "0" * 64
    repository.save_source(storage, source, fixture_video_with_audio)
    run = pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())
    assert run.state == "failed"
    assert any("checksum" in e.lower() for e in run.errors)
    assert run.media_probe is None  # failed before probing


def test_transcription_engine_failure_is_partial_not_fake(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    run = pipeline.run_analysis(storage, project.id, source.id, transcriber=failing_transcriber)
    assert run.state == "partially_completed"
    assert any("Transcription failed" in e for e in run.errors)
    assert run.transcript == []  # nothing invented
    # Media stages still produced real evidence.
    assert run.media_probe is not None
    assert run.frames


def test_video_without_audio_completes_with_limitation(fixture_video_no_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_no_audio)
    run = pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())
    assert run.media_probe["has_audio"] is False
    assert run.transcript == []
    assert "transcribing" not in run.stage_timestamps  # stage honestly skipped
    assert any("No audio stream" in l for l in run.limitations)
    assert run.state == "completed"


# --- successful pipeline, real media stages ---

def test_probe_reports_real_media_facts(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    run = pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())
    p = run.media_probe
    assert p["has_video"] and p["has_audio"]
    assert (p["width"], p["height"]) == (160, 284)
    assert p["orientation"] == "vertical"
    assert 1.0 <= p["duration_seconds"] <= 1.6
    assert run.engine_info["transcription_engine"] == "fake-test-engine"


def test_transcript_schema_and_timestamps(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    run = pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())
    assert all(isinstance(s, TranscriptSegment) for s in run.transcript)
    for s in run.transcript:
        assert 0 <= s.start_seconds < s.end_seconds


def test_frame_sampling_is_deterministic_and_bounded(fixture_video_with_audio):
    ts1 = pipeline.choose_frame_timestamps(50.0, [
        TranscriptSegment(start_seconds=float(i * 4), end_seconds=float(i * 4 + 3), text="x")
        for i in range(1, 12)
    ])
    ts2 = pipeline.choose_frame_timestamps(50.0, [
        TranscriptSegment(start_seconds=float(i * 4), end_seconds=float(i * 4 + 3), text="x")
        for i in range(1, 12)
    ])
    assert ts1 == ts2  # deterministic
    assert len(ts1) <= pipeline.MAX_SAMPLED_FRAMES
    assert ts1 == sorted(ts1)


def test_frames_extracted_with_checksums_and_timestamps(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    run = pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())
    assert run.frames
    for f in run.frames:
        frame_bytes = storage.get_object(f.storage_key)
        assert hashlib.sha256(frame_bytes).hexdigest() == f.checksum_sha256
        assert frame_bytes[:3] == b"\xff\xd8\xff"  # real JPEG magic
        assert 0 <= f.timestamp_seconds <= run.media_probe["duration_seconds"]


def test_observations_are_evidence_linked_and_visual_topics_stay_unknown(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    run = pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())
    assert run.state == "completed"
    topics = {o.topic for o in run.observations}
    assert {"opening_hook", "pacing", "call_to_action", "audio_treatment", "format"} <= topics
    for o in run.observations:
        assert o.evidence_ref  # every claim ties to evidence
    # No vision model: visual topics must be classified unknown, never invented.
    for vt in ("framing", "background_studio", "on_screen_captions", "gestures_expressions", "editing_rhythm"):
        ob = next(o for o in run.observations if o.topic == vt)
        assert ob.classification == "unknown"
        assert ob.evidence_type == "frame_available_for_human_review"
    # CTA in the fake transcript ("comment below") is detected with evidence.
    cta = next(o for o in run.observations if o.topic == "call_to_action")
    assert cta.classification == "directly_observed"
    # Single-example limitation is always present.
    assert any("single example" in l for l in run.limitations)


def test_stage_timestamps_recorded_in_order(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    run = pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())
    order = ["queued", "probing", "transcribing", "sampling_frames", "analyzing", "completed"]
    stamps = [run.stage_timestamps[s] for s in order]
    assert stamps == sorted(stamps)


# --- persistence, restart, separation ---

def test_run_survives_restart_via_disk_storage(tmp_path, fixture_video_with_audio):
    storage = LocalDiskStorage(str(tmp_path))
    project, source = _setup_source(storage, fixture_video_with_audio)
    run = pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())
    assert run.state == "completed"
    # "Restart": a brand-new storage instance over the same directory.
    reloaded_storage = LocalDiskStorage(str(tmp_path))
    reloaded = repository.get_analysis_run(reloaded_storage, project.id, source.id)
    assert reloaded is not None
    assert reloaded.state == "completed"
    assert reloaded.id == run.id
    assert [f.checksum_sha256 for f in reloaded.frames] == [f.checksum_sha256 for f in run.frames]


def test_projects_are_separated(fixture_video_with_audio, fixture_video_no_audio):
    storage = InMemoryStorage()
    p1, s1 = _setup_source(storage, fixture_video_with_audio)
    p2, s2 = _setup_source(storage, fixture_video_no_audio)
    pipeline.run_analysis(storage, p1.id, s1.id, transcriber=fake_transcriber())
    assert repository.get_analysis_run(storage, p2.id, s2.id) is None
    assert repository.get_analysis_run(storage, p1.id, s2.id) is None


# --- routes ---

def _client_with(storage):
    app.dependency_overrides[projects_routes.get_storage] = lambda: storage
    return TestClient(app)


def test_pipeline_route_runs_and_page_displays_result(fixture_video_with_audio, monkeypatch):
    monkeypatch.setattr(pipeline, "_default_transcriber", fake_transcriber())
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    try:
        with _client_with(storage) as client:
            resp = client.post(
                f"/projects/{project.id}/sources/{source.id}/pipeline-analyze",
                follow_redirects=False,
            )
            assert resp.status_code == 303
            html = client.get(f"/projects/{project.id}").text
            assert "Automated pipeline analysis" in html
            assert "COMPLETED" in html
            assert "hello there everyone" in html          # real transcript text shown
            assert "for human review" in html               # honest visual-topic labeling
            assert "single example" in html                 # limitation shown
            assert "analysis-frame/0" in html               # frame evidence linked
    finally:
        app.dependency_overrides.clear()


def test_pipeline_route_409_on_duplicate(fixture_video_with_audio, monkeypatch):
    monkeypatch.setattr(pipeline, "_default_transcriber", fake_transcriber())
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    try:
        with _client_with(storage) as client:
            first = client.post(
                f"/projects/{project.id}/sources/{source.id}/pipeline-analyze",
                follow_redirects=False,
            )
            assert first.status_code == 303
            second = client.post(
                f"/projects/{project.id}/sources/{source.id}/pipeline-analyze",
                follow_redirects=False,
            )
            assert second.status_code == 409
    finally:
        app.dependency_overrides.clear()


def test_frame_route_serves_real_jpeg_and_404s_safely(fixture_video_with_audio, monkeypatch):
    monkeypatch.setattr(pipeline, "_default_transcriber", fake_transcriber())
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    try:
        with _client_with(storage) as client:
            client.post(
                f"/projects/{project.id}/sources/{source.id}/pipeline-analyze",
                follow_redirects=False,
            )
            ok = client.get(f"/projects/{project.id}/sources/{source.id}/analysis-frame/0")
            assert ok.status_code == 200
            assert ok.content[:3] == b"\xff\xd8\xff"
            # Out-of-range and path-shaped indices are safe 404/422s, never
            # filesystem access.
            assert client.get(
                f"/projects/{project.id}/sources/{source.id}/analysis-frame/999"
            ).status_code == 404
            assert client.get(
                f"/projects/{project.id}/sources/{source.id}/analysis-frame/-1"
            ).status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_page_offers_pipeline_button_before_any_run(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    try:
        with _client_with(storage) as client:
            html = client.get(f"/projects/{project.id}").text
            assert "Run pipeline analysis" in html
            assert "Not yet run" in html
    finally:
        app.dependency_overrides.clear()


def test_failed_run_displayed_honestly_with_retry(fixture_video_with_audio):
    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    failed = AnalysisRun(
        project_id=project.id, source_id=source.id, consent_id=source.consent_id,
        input_checksum_sha256=source.checksum_sha256, state="failed",
        errors=["Media probing failed: simulated"],
    )
    repository.save_analysis_run(storage, failed)
    try:
        with _client_with(storage) as client:
            html = client.get(f"/projects/{project.id}").text
            assert "Pipeline failed honestly" in html
            assert "Media probing failed: simulated" in html
            assert "Try again" in html
    finally:
        app.dependency_overrides.clear()


# --- backward compatibility ---

def test_existing_records_unaffected_by_pipeline_addition(fixture_video_with_audio):
    """CF-02 extended analysis and generated videos coexist with a
    pipeline run on the same source -- distinct keys, no clobbering."""
    from app.models import ExtendedCreatorAnalysis, GeneratedVideoRecord

    storage = InMemoryStorage()
    project, source = _setup_source(storage, fixture_video_with_audio)
    extended = ExtendedCreatorAnalysis(
        project_id=project.id, source_id=source.id,
        sections={"transcript": [{"text": "old cf-02 result"}]},
        analysis_provider="local-fallback-pipeline", analysis_model="manual",
        prompt_schema_version="cf-02-extended-v1-local-fallback",
        source_asset_hash=source.checksum_sha256,
    )
    repository.save_extended_analysis(storage, extended)
    gv = GeneratedVideoRecord(
        project_id=project.id, source_id=source.id, kind="animatic",
        narration_kind="synthetic-generic-tts", likeness_used=False,
        filename="v1.mp4", size_bytes=3, checksum_sha256="ab", duration_seconds=1.0,
        width=720, height=1280,
        storage_key=repository.generated_video_file_key(project.id, source.id, "v1.mp4"),
        spec={"topic": "t"}, render_method="m",
    )
    repository.save_generated_video(storage, gv, b"abc")

    pipeline.run_analysis(storage, project.id, source.id, transcriber=fake_transcriber())

    still_extended = repository.get_extended_analysis(storage, project.id, source.id)
    assert still_extended.sections["transcript"][0]["text"] == "old cf-02 result"
    assert len(repository.list_generated_video_records(storage, project.id, source.id)) == 1
    assert repository.get_analysis_run(storage, project.id, source.id) is not None
