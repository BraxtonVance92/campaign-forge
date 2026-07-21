# CampaignForge Current State

Last updated: 2026-07-21 (CF-BOOT-001 merged; CF-VERIFY-001 dispatched).

## State: IN_PROGRESS — CF-VERIFY-001 (live GMI/Genblaze capability test)

The controller/CTO reviewed and approved the corrected sources of truth at exact SHA `9ae223920b0f71aed1831070a5ba9f4924683aec` ("APPROVE AS-IS"), and PR #1 was merged into `main` (`docs/ops/DECISION_LOG.md` D-012). The bootstrap gate is now cleared. Authorized face-and-voice video generation remains recorded as core product scope (D-010, D-011). CF-VERIFY-001 is authorized to run its two smallest GMI/Genblaze live test calls (voice cloning; avatar output format) up to a $5 sub-cap, using the existing GMI key (D-013); HeyGen is deferred and not to be used unless GMI proves unable to produce the required result.

### Repository-verified (as of this inspection)

- Repository: `BraxtonVance92/campaign-forge`.
- Default branch: `main`.
- Main head SHA: `3e06fc2e076f09c7b077d3f5e803583cd0ada5e4` (merge commit for PR #1, containing the CF-BOOT-001 docs pack).
- PR #1: `MERGED` (was draft/open; approved by controller/CTO at head `9ae223920b0f71aed1831070a5ba9f4924683aec`, then merged via standard merge commit — no branch protection was configured on `main` at merge time).
- Active packet branch: `docs/cf-verify-001`, created from the merged `main`.
- The exact current candidate SHA for any in-flight branch is not recorded in this file. A commit cannot contain its own resulting SHA, so any SHA written here as "current" becomes stale the instant that commit is made. The exact current candidate SHA is maintained in the relevant PR's metadata (`headRefOid`) and in checkpoint/review receipts, generated after the commit exists.
- At the merged main SHA, the repository contains `README.md`, root `CLAUDE.md`, and the seven canonical `docs/` files. No runtime application source exists on `main`.
- Render reports repository access to `BraxtonVance92/campaign-forge`. No Render service has been created or verified as existing.

### Reported history, not repository-verified

- A prior ChatGPT Sites prototype was reported live.
- A user test reportedly uploaded files to Backblaze B2.
- Backblaze settings and a GMI inference key were reportedly saved in a hosted environment.
- Historical prototype output included a mock video.

These claims do not establish that the GitHub repository contains the implementation, that any deployment maps to a repository SHA, or that real creator analysis, voice cloning, face/avatar generation, or Genblaze orchestration exists.

### Explicitly not verified/built in this repository

- Real creator analysis.
- Real consent capture and storage.
- Real cloned-voice generation.
- Real face/avatar video generation.
- Real playable rendered video output.
- Genblaze orchestration.
- Versioned creator profile persistence.
- Real GMI image/video generation.
- Exact automated spend reporting.
- CI, reviewed merge (of runtime code — the CF-BOOT-001 merge was docs-only), repo-linked deployment, live acceptance, or any Render service.

## External facts verified 2026-07-21

- Hackathon deadline: August 3, 2026 at 5:00 p.m. Eastern.
- Required stack: Backblaze B2 plus Genblaze; GMI Cloud is optional but supported.
- Required submission: working URL, repository/setup instructions, providers/models, B2/Genblaze explanation, and public demo video under three minutes.
- Judging criteria are equally weighted: utility, production readiness, B2 orchestration, Genblaze use.
- Genblaze SDK v0.5.0 (released 2026-07-17) is an orchestration framework (Pipeline/Step/ObjectStorageSink/Manifest); it does not generate media itself. It has provider adapters for GMICloud, NVIDIA NIM, OpenAI, Google, Runway, Luma, Decart (video/image) and GMICloud, ElevenLabs, MiniMax, NVIDIA NIM, OpenAI, Stability, LMNT, Hume, AssemblyAI (audio). Source: https://github.com/backblaze-labs/genblaze (accessed 2026-07-21).
- GMI Cloud REST API base is `https://api.gmi-serving.com/v1`, Bearer-token auth, OpenAI-compatible for chat models. Source: https://docs.gmicloud.ai/ (accessed 2026-07-21).
- GMI Cloud lists a voice-clone model (`minimax-audio-voice-clone-speech-2.6-hd`) and an avatar model (`heygen-avatar-4`, delivered as a persistent WebRTC streaming session, not confirmed to produce a downloadable batch video file). Whether Genblaze's `Pipeline`/`Step` can actually invoke either of these end-to-end is UNKNOWN — the only public Genblaze/GMI sample repository demonstrates image-to-video only, not voice or avatar steps. Source: https://github.com/backblaze-labs/genblaze-gmicloud-pipeline; https://www.gmicloud.ai/en/blog/managed-generative-media-api (accessed 2026-07-21).
- HeyGen's own direct API (outside Genblaze) offers a Digital Twin/Avatar V product with officially quoted pricing (Digital Twin creation $1.00/call; Avatar V video $0.0667/sec; pay-as-you-go, no free tier) and a consent flow where Level 1 (hosted webcam recording) is available to all customers without an Enterprise account. Training-footage length/resolution constraints (reported as 2-5 minutes, 720p+) were not confirmed on a directly-fetched official reference page this pass and remain to be re-verified. Sources: https://developers.heygen.com/docs/pricing; https://developers.heygen.com/docs/avatar-consent (accessed 2026-07-21).
- Backblaze B2 storage costs $0.005/GB/month with 10GB free; download $0.01/GB with 1GB/day free and free egress up to 3x average storage. CORS rules (up to 100/bucket) and scoped application-key capabilities (`readFiles`, `writeFiles`, `listFiles`, etc.) are documented. Sources: https://www.backblaze.com/docs/cloud-storage-cross-origin-resource-sharing-rules; https://www.backblaze.com/docs/cloud-storage-application-keys (accessed 2026-07-21).
- Render background workers and persistent disks require a paid plan (not available on the free tier); free web services get 750 instance-hours/month and spin down after 15 minutes idle. Starter web service is reported at $7/month, persistent disk at $0.25/GB/month. Sources: https://render.com/docs/background-workers; https://render.com/docs/free; https://render.com/docs/blueprint-spec (accessed 2026-07-21).

Full findings, architecture options, and cost/latency estimates are recorded in the CF-VERIFY-001 research dossier delivered in the maker session on 2026-07-21; that dossier is the working reference until its findings are folded into a future revision of this file or `docs/roadmap/CURRENT_ROADMAP.md`.

## Actual recorded spend

Unknown. No billing export or provider dashboard evidence was supplied. The $50 ceiling remains binding; do not subtract estimates from it as if they were charges. All costs cited above are estimates or officially published rates, not actual recorded charges — no paid provider call has been made.

## Blocker

None from founder/controller input — provider (GMI first), credential (existing GMI key), and budget (part of the overall $50 ceiling, with a $5 sub-cap for this packet) are all resolved per D-013. The only remaining gate is technical: `GMI_API_KEY` must be confirmed present in the environment, without its value ever being exposed in chat, commits, or logs, before the first live call runs. The prior Sites source has not been recovered into GitHub.

## Next safe action

Confirm `GMI_API_KEY` is present (presence-only check, value never displayed), then run the two smallest GMI/Genblaze live test calls authorized in `CF-VERIFY-001`: voice cloning, and whether the GMI avatar endpoint can return a downloadable video. Record actual spend call-by-call against the $5 sub-cap.
