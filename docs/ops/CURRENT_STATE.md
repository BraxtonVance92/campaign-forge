# CampaignForge Current State

Last updated: 2026-07-21 (CF-VERIFY-001 merged; CF-RUN-001 in progress).

## State: IN_PROGRESS — CF-RUN-001 (smallest real product flow)

`CF-BOOT-001` and `CF-VERIFY-001` are both `MERGED`. `main` is at `f195833bd67236346f9865485be5b6a8424e3573` (merge commit for PR #2). `CF-RUN-001` — the first runtime application code in this repository — was dispatched directly by the founder/controller and is in progress on branch `feat/cf-run-001` (not yet merged).

### Repository-verified (as of this inspection)

- Repository: `BraxtonVance92/campaign-forge`.
- Default branch: `main`.
- Main head SHA: `f195833bd67236346f9865485be5b6a8424e3573`.
- PR #1: `MERGED`. PR #2: `MERGED`.
- Active packet branch: `feat/cf-run-001`, created from the merged `main`.
- The exact current candidate SHA for any in-flight branch is not recorded in this file — see the standing rationale in prior revisions of this file and in PR descriptions; it is maintained in the relevant PR's metadata (`headRefOid`) and checkpoint receipts.
- `main` now contains: `README.md`, root `CLAUDE.md`, the seven canonical `docs/` files, `docs/verification/CF-VERIFY-001.md`, and `.github/workflows/cf-verify-001.yml` (prepared, not executed — no `GMI_API_KEY` secret has been added, no account funded, nothing triggered).
- Render reports repository access to `BraxtonVance92/campaign-forge`. No Render service has been created or verified as existing.

### CF-RUN-001: what is real and evidenced (as of this commit, on `feat/cf-run-001`, not yet merged)

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
- CI, reviewed merge of runtime code (`feat/cf-run-001` is not yet merged), repo-linked deployment, live acceptance, or any Render service.

## External facts verified 2026-07-21

- Hackathon deadline: August 3, 2026 at 5:00 p.m. Eastern.
- Required stack: Backblaze B2 plus Genblaze; GMI Cloud is optional but supported.
- Required submission: working URL, repository/setup instructions, providers/models, B2/Genblaze explanation, and public demo video under three minutes.
- Judging criteria are equally weighted: utility, production readiness, B2 orchestration, Genblaze use.
- Full GMI/Genblaze/HeyGen/B2/Render research, including the disclosed GMI blog-vs-quickstart-docs pricing discrepancy, is recorded in `docs/verification/CF-VERIFY-001.md`.

## Actual recorded spend

Unknown/zero. No paid provider call has been made in this repository's history. The $50 total ceiling and CF-VERIFY-001's $20 prepaid-credit sub-boundary remain binding and unused.

## Blocker

`CF-RUN-001`'s real analysis and real persistence both require credentials not present in this environment (`GMI_API_KEY`; `B2_KEY_ID`/`B2_APPLICATION_KEY`/`B2_BUCKET_NAME`/`B2_ENDPOINT`). Everything up to those external calls is implemented and tested. Separately, `CF-VERIFY-001`'s live GMI test workflow remains unexecuted pending account funding (up to $20) and the `GMI_API_KEY` GitHub secret.

## Next safe action

Controller/founder reviews `feat/cf-run-001`'s draft PR. If real credentials become available, wire them in and re-verify the previously-blocked paths for real; otherwise the next dependent block (Genblaze generation leg) can proceed once this slice is reviewed.
