# CF-VERIFY-001 Findings

Status: pricing/endpoint research complete (documentation-only); live test results pending execution.

## Endpoint (VERIFIED official docs, accessed 2026-07-21)

Both `minimax-audio-voice-clone-speech-2.6-hd` and `heygen-avatar-4` are invoked through the identical endpoint:

```
POST https://console.gmicloud.ai/api/v1/ie/requestqueue/apikey/requests
```

Sources: `https://docs.gmicloud.ai/model-quickstarts/audio/minimax-audio-voice-clone-speech-2-6-hd`, `https://docs.gmicloud.ai/model-quickstarts/video/heygen-avatar-4.md`.

An earlier draft of this packet's workflow hardcoded a different, wrong domain (`api.gmi-serving.com`) based on the general GMI Cloud API-overview page rather than the model-specific quickstart docs. That was corrected before any call was attempted.

## Pricing (accessed 2026-07-21)

| Model | Source | Statement | Confidence |
|---|---|---|---|
| `heygen-avatar-4` | gmicloud.ai blog (`/en/blog/managed-generative-media-api`) | "$0.0667 per request on GMI Cloud... without a session minimum commitment" | VERIFIED quote; implies **flat per-request** |
| `heygen-avatar-4` | docs.gmicloud.ai quickstart page for this exact model | "$0.05/sec (Photo Avatar), $0.0667/sec" for other modes | VERIFIED quote; implies **per-second** |
| `minimax-audio-voice-clone-speech-2.6-hd` | its own official quickstart page | No pricing shown | Confirmed absent |
| `minimax-audio-voice-clone-speech-2.6-hd` | general web-search synthesis | ~$0.10/request | **REPORTED only** — not traceable to a directly-quotable official page |

**Open discrepancy, disclosed rather than silently resolved**: GMI's own two published sources disagree on whether the avatar model bills per-request or per-second. This was not resolved by picking one interpretation — see "Real spending boundary" below for how this packet handles that instead.

## Minimum required amount / account funding minimum

**Unknown.** No official static documentation page states a minimum prepaid-credit top-up amount, and this project has no GMI console credentials, so account-specific billing/funding minimums could not be checked. If, when funding the account, GMI requires more than $20 as a minimum top-up, that is a reportable blocker per `docs/ops/ACTIVE_WORK_PACKET.md`, not something to resolve by unilaterally increasing the authorized budget.

## Real spending boundary (per controller direction, 2026-07-21)

Rather than compute a precise-but-uncertain worst-case dollar ceiling from the conflicting pricing statements above, the authorized boundary is structural: the GMI account is funded with **at most $20 in prepaid credit**. Neither test call can draw more than what is actually funded, regardless of which billing interpretation is correct. This is a sub-limit within the overall $50 project ceiling in `docs/canon/FOUNDER_CANON.md`, not an addition to it.

## Live test results

Not yet available — no paid call has been made as of this writing. Once the workflow (`.github/workflows/cf-verify-001.yml`) is executed, this section will be updated with: request_id, model, status, output_type (downloadable file vs. streaming session, for the avatar question), latency, and actual recorded cost per the GMI console, for each of the two authorized calls.
