# CF-02 / CF-03 Live Experiment Receipt (template — no real data yet)

Fill this in at the time of the first real, live GMI analysis call
(`CF-02`) and the first real end-to-end browser flow (`CF-03`), per
`docs/roadmap/CAMPAIGNFORGE_EXECUTION_LEDGER.md`. Never paste a secret
value or the raw provider response body into this file or any commit —
only the sanitized fields below.

## Provider documentation checked (cite exact URL + date)

- Endpoint: `https://api.gmi-serving.com/v1/chat/completions` — verified `https://docs.gmicloud.ai/model-quickstarts/text/nvidia-nvidia-nemotron-3-nano-omni.md` (accessed 2026-07-21)
- Model: `nvidia/nemotron-3-nano-omni`
- Pricing: UNDOCUMENTED on the quickstart or LLM API reference pages checked 2026-07-21 (`llm-api-reference.md`) — no per-token/per-request/per-second figure found for this model. Do not invent one; if a billing dashboard becomes available after account funding, that is the authoritative source (same precedent as D-017 for CF-VERIFY-001's voice/avatar pricing).

## Attempt 1 — base64 data-URI video input (no B2 required)

- Attempted: [ ] yes [ ] no
- Video duration/size used: ___
- Request content-block shape sent: ___ (record the literal JSON shape used, minus any secret)
- Response HTTP status: ___
- Result: [ ] parsed successfully [ ] contract validation failed [ ] HTTP error [ ] network error [ ] other: ___
- Sanitized response fields captured (never the raw body): model, confidence value, whether required fields were present — ___

## Attempt 2 — hosted URL (B2 presigned or GMI Upload API), only if Attempt 1 failed

- Attempted: [ ] yes [ ] no
- Mechanism used: [ ] B2 presigned URL [ ] GMI Upload API [ ] other: ___
- Response HTTP status: ___
- Result: ___

## Failure rule applied

Per the ledger: if neither attempt above succeeds, this block is marked
`BLOCKED` and a provider change is recommended — no third guess.

## Accuracy spot-check (CF-03 only, requires a video with a known transcript/visual facts)

- Known spoken topic correctly identified: [ ] yes [ ] no
- Known opening hook correctly identified: [ ] yes [ ] no
- Basic tone correctly identified: [ ] yes [ ] no
- Visible format correctly identified: [ ] yes [ ] no

## Cost and evidence

- Actual recorded cost for this call: ___ (from account billing/usage dashboard, not estimated)
- Running total spend against the $50 ceiling: ___
- `REQUEST_SHAPE_VERIFIED` flipped to `True`: [ ] yes, after a successful parse — commit SHA ___ [ ] not yet
- Screenshot/evidence location (local, never committed if it contains a raw response): ___

## Founder usefulness verdict (CF-03 gate)

- "Is this analysis accurate and useful enough to test on a small batch?" — Founder answer: ___
- Recorded in `docs/ops/DECISION_LOG.md` as: D-___
