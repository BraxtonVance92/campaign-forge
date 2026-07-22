# CF-02 Live Experiment Receipt (real data, 2026-07-22)

Sanitized record of real GMI Cloud calls made against the founder's real
`GMI_API_KEY` (never shown, never committed) using one real authorized
video of the founder's stepdad (uploaded through the real CampaignForge
app, never committed to this repository). This is the CF-02 block per
`docs/roadmap/CAMPAIGNFORGE_EXECUTION_LEDGER.md`.

## Attempt 1 — real end-to-end app flow, base64 data-URI video input

- Timestamp: 2026-07-22T16:55:24Z
- Endpoint: `https://api.gmi-serving.com/v1/chat/completions`
- Requested model: `nvidia/nemotron-3-nano-omni`
- Input type: base64 `data:video/mp4;base64,...` URI (4,083,914-byte real video, under the 8 MB `MAX_DATA_URI_BYTES` cap), built by `GMIAnalysisClient.analyze_extended()`
- HTTP status: `404`
- Sanitized response body: `GMI returned HTTP 404. The real analysis call did not produce a usable result.` (raw provider body was not persisted, per `app/analysis.py`'s security design)
- Runtime: ~0.98s (measured via the app's real HTTP round trip, including FastAPI request overhead) — a near-instant failure, consistent with a pre-inference routing error rather than a real model invocation
- Usable output produced: **no**
- Persisted as: `AnalysisBlockedRecord` at `.local_storage/projects/adf66ff2-41ba-4baa-b7d0-e8da83ad2fcc/sources/92bc1f7c-4b2a-4c0c-9793-19a42bddbfa5/extended_analysis.json`, displayed honestly on the website as "Analysis needs attention"

## Attempt 2 — direct diagnostic, text-only, same model

Run outside the app to isolate whether the failure was video-input-specific or more fundamental.

- Endpoint: `https://api.gmi-serving.com/v1/chat/completions`
- Requested model: `nvidia/nemotron-3-nano-omni`
- Input type: plain text message (`"Say OK."`), no image/video content block at all
- HTTP status: `404`
- Sanitized response body (non-JSON, plain text): `No matching target server found for model nvidia/nemotron-3-nano-omni`
- Runtime: not separately measured (sub-second)
- Usable output produced: no
- **Conclusion**: this 404 is not about video input at all — the model itself has no running/deployed instance on this account. This rules out "video shape is wrong" as the explanation and points to "model not deployed" instead.

## Attempt 3 — real models-list call

- Endpoint: `GET https://api.gmi-serving.com/v1/models`
- HTTP status: `200`
- Result: real list of ~85 model IDs actually available on this account (GPT-5.x family, Claude family, Gemini family, DeepSeek, Qwen, GLM, Kimi, `nvidia/nemotron-3-ultra-550b-a55b`, etc.)
- `nvidia/nemotron-3-nano-omni` is **absent** from this list — confirms Attempt 2's conclusion with an independent method, not just an error-message string.
- No model in the list is explicitly labeled vision/multimodal/omni/video in its name.

## Actual recorded spend

**Unknown, not confirmed $0.** No GMI billing dashboard was checked (none is accessible from this environment). Provider behavior is consistent with these being free, pre-inference routing failures (a "no matching target server" 404 for a non-deployed model typically occurs before any model instance is invoked in inference-serving architectures like GMI's), which makes an actual charge unlikely for these three calls specifically — but this is an inference from behavior, not a verified statement from a billing record. Treat as "no recorded charge observed," not "confirmed $0."

## Phase 2 — model capability probes (real, 2026-07-22)

Candidate ranking and rationale: `docs/verification/CF-02-model-candidates.md`. Probe image: `frame_03.jpg` (84,190 bytes), extracted from the same real authorized video at approximately 00:00:25.

### Probe 1 — openai/gpt-4o-mini

- Endpoint: `https://api.gmi-serving.com/v1/chat/completions`
- Input type: base64 `data:image/jpeg;base64,...` image_url content block + short text prompt, `max_tokens: 150`
- HTTP status: **402**
- Sanitized response body: `{"error": "Insufficient balance"}`
- Runtime: 0.95s
- Usable output produced: no
- **This is materially different from the nemotron 404**: the model is real/deployed (no "target server" routing error) but the account itself has no funded balance to run a paid call.

### Probe 2 — google/gemini-3.1-flash-lite-preview

- Same request shape and image, different vendor/model family, to confirm whether Probe 1's result was model-specific or account-wide.
- HTTP status: **402**
- Sanitized response body: `{"error": "Insufficient balance"}`
- Runtime: 0.52s
- Usable output produced: no
- **Conclusion: confirmed account-wide, not model-specific.** No further model was probed live: repeating the same request shape against different models would return the identical account-level 402 with no new information, which is exactly the "do not waste money/requests repeating equivalent failing requests" instruction. Probes 3-5 (`openai/gpt-4o`, `google/gemini-3-flash-preview`, `anthropic/claude-haiku-4.5`) were not run for this reason.

**Two independent GMI blockers are now confirmed, not one:**
1. `nvidia/nemotron-3-nano-omni` (the originally-coded model) is not deployed on this account at all (404).
2. Even a deployed, working model (`gpt-4o-mini`, confirmed real via the 402 rather than 404) cannot be called because the account has no funded balance (402, account-wide).

Fixing blocker 2 (funding the account) would not by itself fix blocker 1, and vice versa. Both require founder action: either enabling/deploying a vision-capable model on this GMI account, or funding the account balance (previously bounded at a $20 prepaid maximum per D-017), or both.

### Actual recorded spend (Phase 2)

Unknown, not confirmed $0 -- same reasoning as Phase 1: a 402 "insufficient balance" response is, by definition, a rejection before any billable inference occurs (there is no balance to draw from), which makes a real charge for these two specific calls extremely unlikely -- but this remains an inference from provider behavior, not a verified billing statement.

## Total real external calls made this session: 5 (all GMI Cloud: 3 diagnostic/routing checks in Phase 1, 2 real image-capability probes in Phase 2)
