# CampaignForge Current State

Last updated: 2026-07-22 (PR #7 merged — CF-01 credential-readiness research; CF-02 executed live — real GMI probes found two account-level blockers, not a code defect; a local-fallback analysis pipeline built and proven on one real authorized video, pending R1/R2 on branch `feat/cf-02-extended-analysis`).

## State: BLOCKED ON GMI ACCOUNT FUNDING/MODEL DEPLOYMENT — CF-02 real analysis produced via local fallback

`CF-BOOT-001`, `CF-VERIFY-001`, `CF-RUN-001`, the PR #5 UI refresh, PR #6 (CF-00), and PR #7 (CF-01) are all `MERGED`. `main` is at `220d7fca8572e5bbeff6b4607f2983ffac8c056d` (merge commit for PR #7). `CF-02` (the real live provider probe) has been executed for real against the founder's actual GMI credential and one real authorized video: the originally-coded model (`nvidia/nemotron-3-nano-omni`) is not deployed on this account (HTTP 404), and two other real, unrelated models (`openai/gpt-4o-mini`, `google/gemini-3.1-flash-lite-preview`) both returned HTTP 402 "Insufficient balance" — an account-wide funding gate, not a code or format defect. Full sanitized evidence: `docs/verification/CF-02-experiment-receipt.md`, `docs/verification/CF-02-model-candidates.md`. Rather than stop, a local fallback pipeline (real `ffmpeg` audio/frame extraction + real `faster-whisper` transcription + direct visual frame review) produced a genuine, non-fabricated, timestamped analysis of the same real video, persisted and displayed on the website, honestly labeled as a local-fallback result (not GMI) and distinct from the three failed GMI attempts, which remain visibly recorded on the same page. This work is on branch `feat/cf-02-extended-analysis`, pending R1/R2 exact-SHA review before merge.

### Repository-verified (as of this inspection)

- Repository: `BraxtonVance92/campaign-forge`.
- Default branch: `main`.
- Main head SHA: `220d7fca8572e5bbeff6b4607f2983ffac8c056d`.
- PR #1: `MERGED`. PR #2: `MERGED`. PR #3: `MERGED`. PR #4: `CLOSED` (unmerged, superseded — see D-021). PR #5: `MERGED`. PR #6: `MERGED`. PR #7: `MERGED`.
- CI on `main` post-merge: `SUCCESS` at `220d7fca8572e5bbeff6b4607f2983ffac8c056d` (https://github.com/BraxtonVance92/campaign-forge/actions/runs/29935000188).
- Open branch (not yet a PR at time of writing): `feat/cf-02-extended-analysis` — extended analysis model/route/template, base64 fallback, real CF-02 experiment receipts, local-fallback pipeline result. 102 tests passing.
- The exact current candidate SHA for any future in-flight branch is not recorded in this file — see the standing rationale in prior revisions of this file and in PR descriptions; it is maintained in the relevant PR's metadata (`headRefOid`) and checkpoint receipts.
- `main` now contains the seven canonical `docs/` files, `docs/verification/CF-VERIFY-001.md`, two workflows (`cf-verify-001.yml` — prepared, not executed; `cf-run-001-tests.yml` — real, passing), and the full `app/`/`tests/` runtime application described below, including the PR #5 UI refresh (desktop layout width fix, restructured result display, accessibility fixes).
- Render reports repository access to `BraxtonVance92/campaign-forge`. No Render service has been created or verified as existing.

### CF-RUN-001: what is real and evidenced (merged into `main` at `c9ae8bb3926c2589043d8467244dc7f51586543f`, UI refined in PR #5 at `e5b26eafd2917cd8bbfffa607f554195106c6a47`)

- A FastAPI application (`app/`) implementing: project creation, authorized-video upload with a required consent attestation, checksum computation, structured persistence, an analysis trigger, and a minimal HTML display/restore page plus a JSON retrieval endpoint.
- Upload validation (content type, real file-signature check against magic bytes — not just the client-supplied MIME header —, size, non-empty file, required consent, one-source-per-project enforcement) is real and covered by automated tests.
- Uploaded filenames are sanitized to a safe basename (`app/security.py`) before use in any storage key, with a defense-in-depth root-containment check in `LocalDiskStorage` itself; both are tested against real traversal payloads (`../../etc/passwd` and similar).
- The creator-profile response contract from `docs/canon/PRODUCT_CANON.md` is implemented as a validated Pydantic model and its parsing logic is tested against both valid and deliberately malformed fixtures.
- Persistence uses a storage abstraction with three implementations: `B2Storage` (real, production-intended, Backblaze B2 via its S3-compatible API, with paginated object listing so results aren't silently truncated at 1000 keys, and real time-limited presigned URL generation — see below), `LocalDiskStorage` (an explicitly labeled fallback used automatically when B2 credentials are absent — as they are in this environment), and `InMemoryStorage` (tests only). 76 automated tests pass (`pytest tests/`), and the full flow was additionally exercised manually against a running local server, including the path-traversal, one-source-enforcement, and signature-validation fixes from an earlier review round.
- **Private-object fetch design corrected after review**: `get_source_original_url()` previously joined the bucket endpoint and key into a plain URL, which would 403 against a private B2 object — Product Canon requires originals to be private by default, so this was a real functional blocker, not just a hygiene issue. Now generates a real, time-limited presigned URL through `B2Storage.get_presigned_url()` (boto3 `generate_presigned_url`), bounded to 1 second–7 days with a 15-minute default, validated before ever reaching boto3. `LocalDiskStorage`/`InMemoryStorage` raise `PresignedUrlUnsupportedError` rather than returning an unusable URL.
- **Analysis client explicitly marked experimental, code-level not just prose**: `app.analysis.REQUEST_SHAPE_VERIFIED = False` is threaded onto every `CreatorProfile.request_shape_verified` this client produces, and the display page shows an "EXPERIMENTAL" badge on any analyzed result where that flag is false — visible in the UI, not just a code comment. Must only flip to `True` after an authorized live test actually confirms the `video_url` request shape.
- **GMI analysis endpoint/model corrected after review, both now VERIFIED**: `https://api.gmi-serving.com/v1/chat/completions` with model `nvidia/nemotron-3-nano-omni` — directly quoted from `https://docs.gmicloud.ai/model-quickstarts/text/nvidia-nvidia-nemotron-3-nano-omni.md` (accessed 2026-07-21). An earlier version of this code used `gemini-omni-flash-preview`, which is actually a video **generation** model on GMI's separate request-queue domain (`console.gmicloud.ai`), not a video-understanding model — a real error caught in review, corrected, and documented in `app/analysis.py`'s module docstring so it isn't repeated. The exact JSON shape for passing *video* (as opposed to image) input to `nemotron-3-nano-omni` remains UNDOCUMENTED on the page fetched; the client's `video_url` content-block follows the documented `image_url` pattern as the closest verified analogue but is explicitly not claimed to be production-ready until exercised against a live response.
- **Real GMI analysis has not run.** `GMI_API_KEY` is not present in this environment. Every failure mode (missing credential, unfetchable source, HTTP error, network error, malformed response shape, missing required field, contract validation failure) is caught inside `GMIAnalysisClient.analyze()` and converted to an honest `AnalysisBlockedError` with a sanitized message — never an unhandled exception, never the raw provider response body, never a secret. One test proves the success-path parsing/response-handling logic using a mocked HTTP layer, clearly labeled as such and never conflated with a real call.
- **Real Backblaze B2 persistence has not run.** B2 credentials are also not present in this environment — a second blocker beyond the one named in the dispatch instruction, surfaced here rather than assumed away. `B2Storage` is implemented against boto3's S3-compatible client but has not been exercised against a real bucket.
- **CI**: `.github/workflows/cf-run-001-tests.yml` runs the full test suite on every PR/push to `main` (no secrets required or read). Authorized as the one exception to this packet's CI prohibition — `docs/ops/DECISION_LOG.md` D-019.
- Not built, per explicit scope: voice cloning, avatar/face generation, publishing, billing, authentication expansion, any other CI/deployment changes.

### Reported history, not repository-verified

- A prior ChatGPT Sites prototype was reported live.
- A user test reportedly uploaded files to Backblaze B2.
- Backblaze settings and a GMI inference key were reportedly saved in a hosted environment.
- Historical prototype output included a mock video.

These claims do not establish that the GitHub repository contains the implementation, that any deployment maps to a repository SHA, or that real creator analysis, voice cloning, face/avatar generation, or Genblaze orchestration exists.

### Explicitly not verified/built in this repository

- Real GMI/Genblaze creator analysis against a live API (client implemented, gated, untested live).
- Real Backblaze B2 persistence against a live bucket (client implemented, gated, untested live).
- Real cloned-voice generation.
- Real face/avatar video generation.
- Real playable rendered video output.
- Genblaze orchestration (no Genblaze SDK call has been made yet; CF-RUN-001's analysis client calls GMI's chat API directly, not through Genblaze's `Pipeline`/`Step` — a documented gap to close in a later packet).
- Exact automated spend reporting.
- Repo-linked deployment, live acceptance (a customer/judge actually using the deployed app), or any Render service. Runtime code (CF-RUN-001 and the PR #5 UI refresh) is merged and CI-passing, but merged-and-tested is not the same as deployed-and-live-verified — no deployment of any kind has occurred yet.

## External facts verified 2026-07-21

- Hackathon deadline: August 3, 2026 at 5:00 p.m. Eastern.
- Required stack: Backblaze B2 plus Genblaze; GMI Cloud is optional but supported.
- Required submission: working URL, repository/setup instructions, providers/models, B2/Genblaze explanation, and public demo video under three minutes.
- Judging criteria are equally weighted: utility, production readiness, B2 orchestration, Genblaze use.
- Full GMI/Genblaze/HeyGen/B2/Render research, including the disclosed GMI blog-vs-quickstart-docs pricing discrepancy, is recorded in `docs/verification/CF-VERIFY-001.md`.

## Actual recorded spend

Unknown/zero. No paid provider call has been made in this repository's history. The $50 total ceiling and CF-VERIFY-001's $20 prepaid-credit sub-boundary remain binding and unused.

## Blocker

`CF-01`'s real analysis and real persistence both require credentials not present in this environment (`GMI_API_KEY`; `B2_KEY_ID`/`B2_APPLICATION_KEY`/`B2_BUCKET_NAME`/`B2_ENDPOINT`). Everything up to those external calls is implemented, tested, and now merged to `main`. Separately, `CF-VERIFY-001`'s live GMI test workflow remains unexecuted pending account funding (up to $20) and the `GMI_API_KEY` GitHub secret. Re-confirmed present-but-empty in this environment on 2026-07-21 (checked `.env` and the shell environment directly — no value found for any of the five variable names; only `.env.example`'s blank names exist).

### Founder setup instruction (exact, current as of 2026-07-21)

No Render or other hosted deployment exists yet, so the only place these currently need to go is this repository's local `.env` file (already `.gitignore`d — never commit it):

1. In the repo root, copy `.env.example` to `.env` if you have not already (`cp .env.example .env`).
2. Set `GMI_API_KEY=` to your real GMI Cloud API key. **This alone may be enough for the very first small test** — see the correction below; B2 is the current code's requirement, not a confirmed GMI requirement.
3. Set all four B2 variables together — `B2_KEY_ID=`, `B2_APPLICATION_KEY=`, `B2_BUCKET_NAME=`, `B2_ENDPOINT=` — from your Backblaze B2 bucket's Application Key page, if/when you want durable, restorable storage (Product Canon's long-term requirement regardless of this experiment).
4. Restart the server so it re-reads the environment: `uvicorn app.main:app --reload`.
5. Confirm what's recognized: open `http://127.0.0.1:8000/health` — `"gmi_configured": true` confirms the key is read; `"b2_configured": true` confirms B2 is read. Neither is a live-call test by itself, only a presence check.
6. Confirm a real analysis actually runs: create a project, upload one authorized creator video, click "Run creator analysis." A rendered creator profile (not the "Analysis blocked" card) confirms the real call succeeded. Only at that point should `app.analysis.REQUEST_SHAPE_VERIFIED` be flipped to `True` (D-022/D-023) — never speculatively.

**Correction (2026-07-21, `CF-01` research, `docs/ops/ACTIVE_WORK_PACKET.md`):** the *current code* requires both credential sets together, because `GMIAnalysisClient.analyze()` only accepts a `https://` `video_url` and local-disk-fallback storage can't produce one. But it is **unverified, not confirmed impossible**, that GMI's `nemotron-3-nano-omni` endpoint could accept a small video directly as a base64 data URI instead of a hosted URL — a pattern documented for a *different* GMI model family (video generation), not this one, so it is not assumed to work here without a live test. If you only have `GMI_API_KEY` and want to try the smallest possible experiment before setting up B2, say so — CF-02's live test is designed to try base64 first specifically because it needs no B2 setup, and only falls back to a hosted URL if that fails.

## Next safe action

Controller/founder supplies the credentials per the instruction above (or explicitly declines/defers). Once supplied, wire them in and run `CF-02`/`CF-03` (the first real, live, non-fabricated analysis, per D-023), capturing sanitized evidence and flipping `REQUEST_SHAPE_VERIFIED`. Until then, the next dependent block (Genblaze generation leg) remains available to plan but not to build against real provider behavior.
