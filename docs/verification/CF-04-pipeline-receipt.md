# CF-04 Reusable Analysis Pipeline — Receipt (2026-07-22)

## Evidence-state (per the ledger's vocabulary, never collapsed)

- **Implemented**: yes — `app/pipeline.py` (+ models/repository/routes/template integration), real application code with pinned dependencies (`imageio-ffmpeg==0.6.0`, `faster-whisper==1.2.1`).
- **Tested with synthetic fixtures**: yes — 23 automated tests using real, tiny, non-identifying generated media (ffmpeg testsrc + sine tone); transcription mocked in tests so CI never downloads a model.
- **Verified with a genuinely authorized creator video**: yes — one real end-to-end run through the real HTTP route on the one authorized video (consent `f5a618d6`, permitted use "analysis"), detailed below. This satisfies "the pipeline works on real creator media once"; it does NOT satisfy the ledger CF-04 proof gate (five representative videos), which remains open.
- **Merged**: see PR/CI section (recorded at merge time).
- **Deployed / live-verified**: **no** — local only, nothing external.

## The real acceptance run

- Route: `POST /projects/adf66ff2-…/sources/92bc1f7c-…/pipeline-analyze` → HTTP 303, total wall time ~4.9s.
- Input: the authorized 4,083,914-byte video, checksum `e9f67ca0…953a` (verified against stored bytes before any processing).
- Probe (real): 50.52s, 720x1280 vertical, h264 23.98fps, aac 44100Hz stereo — matches all independently known facts about this file.
- Transcription (real, local): faster-whisper `base`, cpu int8, detected language `en`, 11 timestamped segments, 176 words (~210 wpm overall).
- Frames (real): 12 deterministic samples at 0.5–50.02s, each persisted with its own sha256, served via `GET …/analysis-frame/{index}`.
- Observations: 12 evidence-linked entries. Transcript/probe-supported topics (hook, pacing, CTA, structure, audio, format) are `directly_observed`/`inferred` with evidence refs; all five visual topics (framing, background, captions, gestures, editing) are honestly `unknown` — **this pipeline has no vision model and never invents visual claims**; frames are attached for human review instead.
- Spot-checks performed: the frame at 45.52s shows the on-screen caption "TO BUILD A BUSINESS" while the transcript at 45.52s reads "build a business model like this" — timestamp/content correspondence confirmed against real media. Transcript matches the CF-02 manually-verified transcript, including the known ASR artifact ("Infopinor") which remains flagged at medium confidence rather than silently corrected.
- Duplicate prevention: a second POST for the same source returned HTTP 409.
- Restart persistence: run-record sha256 identical before/after a real `kill -9` + clean restart; page still displays the completed result (HTTP 200).
- CF-02/V1/V2 coexistence: the run persists under its own key; the CF-02 extended analysis and both animatics remain untouched and displayed (covered by an automated backward-compatibility test as well).

## Second-video acceptance step — BLOCKED (persisted here)

A search of the authorized project storage found exactly one video with adequate consent. **The ledger CF-04 proof gate (five representative videos, and even a two-video comparison) is blocked on additional authorized creator videos.** No cross-video pattern claims were made. Upload request: to proceed, upload one (ideally more) additional authorized video of the same creator through the normal CampaignForge upload flow — a new project per video under the current one-source-per-project constraint — with a consent statement that includes "analysis" in its permitted uses. The pipeline will then run on it with one click and results can be compared example-to-example.

## Cost

- Actual financial spend: $0 (all local; no network service called — the transcription model was already cached locally from CF-02; CI mocks transcription and downloads no model).
- Local compute: ~5s CPU for the real 50s video (recorded separately from money, per instruction).

## Known limitations (also persisted in every run record)

- Single-example findings are labeled and never promoted to stable habits.
- No vision stage: visual topics require human review of the extracted frames or a future vision-capable stage (e.g., a funded GMI account).
- ASR proper nouns are unreliable (flagged medium/low confidence in observations).
