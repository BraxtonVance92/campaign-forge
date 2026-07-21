# CampaignForge Current State

Last updated: 2026-07-21 (canon repair in progress following a founder product correction).

## State: IN_PROGRESS — canon repair, pending controller review

The founder issued a binding correction rejecting the prior no-face/no-voice decision (D-005). Authorized face-and-voice video generation is now recorded as core product scope (`docs/ops/DECISION_LOG.md` D-010, D-011). This correction is reflected in `docs/canon/FOUNDER_CANON.md`, `docs/canon/PRODUCT_CANON.md`, `docs/roadmap/CURRENT_ROADMAP.md`, `docs/ops/AUTHORITY_MATRIX.md`, and this file. The bootstrap gate remains blocked pending controller approval.

### Repository-verified (as of this inspection)

- Repository: `BraxtonVance92/campaign-forge`.
- Default branch: `main`.
- Main head SHA: `269d2900b1131c793d7cdf2e87655891f5256149` (unchanged since the original bootstrap audit; re-verified before this correction).
- Active correction branch: `docs/cf-boot-001`.
- Predecessor candidate SHA: `09fd09594591b1f08e6f4a23fd2284813d1f9e35` (an earlier head of `docs/cf-boot-001`, since superseded by further commits on the branch; not the current head).
- The exact current candidate SHA is not recorded in this file. A commit cannot contain its own resulting SHA, so any SHA written here as "current" becomes stale the instant that commit is made. The exact current candidate SHA is maintained in PR #1's metadata (`headRefOid`) and in checkpoint/review receipts, which are generated after the commit exists.
- Pull request: #1 (draft, open), targeting `main`.
- At the recorded main SHA, the repository contains a minimal `README.md` and root `CLAUDE.md` operating contract. No runtime application source exists on `main`.
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
- CI, reviewed merge, repo-linked deployment, live acceptance, or any Render service.

## External facts verified 2026-07-21

- Hackathon deadline: August 3, 2026 at 5:00 p.m. Eastern.
- Required stack: Backblaze B2 plus Genblaze; GMI Cloud is optional but supported.
- Required submission: working URL, repository/setup instructions, providers/models, B2/Genblaze explanation, and public demo video under three minutes.
- Judging criteria are equally weighted: utility, production readiness, B2 orchestration, Genblaze use.
- Genblaze's current public repository describes a Python 3.11+ SDK, B2/S3 storage backend, provider adapters including GMI Cloud, pipeline events, and canonical provenance manifests.
- Whether Genblaze/GMI Cloud directly support authorized voice cloning or face/avatar generation is Unknown — verification required (see `docs/roadmap/CURRENT_ROADMAP.md` Phase 0.5).

Sources:

- https://backblaze-generative-media.devpost.com/rules
- https://github.com/backblaze-labs/genblaze
- https://github.com/backblaze-labs/genblaze-gmicloud-pipeline

## Actual recorded spend

Unknown. No billing export or provider dashboard evidence was supplied. The $50 ceiling remains binding; do not subtract estimates from it as if they were charges.

## Blocker

The corrected sources of truth must be reviewed by the controller for coherence, then approved and merged. Provider capability verification for authorized voice cloning and face/avatar generation (Phase 0.5) has not started. The prior Sites source has not been recovered into GitHub.

## Next safe action

Controller reviews the corrected canon on PR #1 for coherence with the founder's face-and-voice correction. Once approved and merged, the next packet is provider capability and architecture verification (Phase 0.5), not runtime implementation.
