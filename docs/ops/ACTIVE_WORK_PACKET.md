# Active Work Packet

## CF-VERIFY-001 — Live GMI/Genblaze capability test: voice cloning and avatar output format

Classification: `VERIFICATION`

Consumer: the next runtime packet (`CF-RUN-001`, the single-authorized-creator pilot), which needs enough evidence to choose the first working video path — not a complete answer to every open research question.

Status: `IN_PROGRESS` — documentation authorized and pushed; live testing begins once `GMI_API_KEY` is confirmed present in the environment without its value being exposed.

### Predecessor

`CF-BOOT-001` is `MERGED` at main SHA `3e06fc2e076f09c7b077d3f5e803583cd0ada5e4` (Controller/CTO-approved at exact SHA `9ae223920b0f71aed1831070a5ba9f4924683aec`; see `docs/ops/DECISION_LOG.md` D-012). A read-only documentation research dossier (Genblaze/GMI Cloud, voice-clone providers, face/avatar providers, Backblaze B2, Render, official documentation only) was produced in the maker session on 2026-07-21. This packet resolves only the subset of that dossier's open questions needed to pick a working first video path, using real GMI/Genblaze API calls.

### Founder/controller decisions already resolved (do not re-ask)

- The existing GMI inference key was created for CampaignForge and is the credential to use.
- GMI is the first and only provider to test in this packet. HeyGen is explicitly **not** approved and no HeyGen account is to be created. HeyGen becomes a live option only if this packet's GMI testing proves GMI cannot produce the required reusable face/avatar video result.
- The $50 spending ceiling covers total project spending (not merely API-calls-only), so hosting and provider costs both draw from the same ceiling.
- This packet's own live-test spend is separately capped at **$5 maximum**, recorded call-by-call, as a sub-limit within the $50 total ceiling — not an additional $50.

### Base

- Repository: `BraxtonVance92/campaign-forge`
- Base branch: `main`
- Exact base SHA: `3e06fc2e076f09c7b077d3f5e803583cd0ada5e4`
- Maker must fetch and stop if `main` has changed until the controller reconciles the new base.

### Allowed paths

- `docs/roadmap/CURRENT_ROADMAP.md` (record verified findings against the Phase 0.5 verification block)
- `docs/ops/CURRENT_STATE.md`
- `docs/ops/ACTIVE_WORK_PACKET.md`
- `docs/ops/DECISION_LOG.md`
- `docs/verification/CF-VERIFY-001.md` (create for detailed live-test findings)
- `.gitignore` only to ensure any local secret/env file used for the live test is excluded (no other content changes)

Any throwaway script needed to make the live API calls is written outside the repository (session scratch space), not committed — this packet produces evidence, not application source.

### Forbidden paths

- `CLAUDE.md`, `docs/canon/*`, `docs/ops/AUTHORITY_MATRIX.md`
- Any runtime application source, CI, deployment, or infrastructure-as-code file
- No Render service creation, no production deployment
- No HeyGen account creation or HeyGen API call

### Required behavior

Run the smallest, cheapest real GMI/Genblaze API calls that answer exactly two questions:

1. **Voice cloning**: does GMI's `minimax-audio-voice-clone-speech-2.6-hd` (invoked directly and, if feasible, through Genblaze's `Pipeline`/`Step` via the `genblaze-gmicloud` adapter) produce real cloned-voice audio end to end? Use a short, non-personal, synthetic placeholder reference clip for this connectivity/capability test — not a real creator's voice — since no verified creator consent record exists yet (per `docs/canon/PRODUCT_CANON.md`'s consent-first rule, Phase 2 of the roadmap has not run). This test proves the mechanism works; it does not produce a usable creator asset.
2. **Avatar output format**: does GMI's avatar model (for example `heygen-avatar-4`) return a downloadable/playable video file in any request mode, or only a live WebRTC streaming session? A minimal, cheapest-available request is sufficient to answer this — the goal is determining output shape, not producing a finished video.

Stop as soon as these two questions are answered, or the $5 cap is reached, whichever comes first. Do not attempt to resolve every remaining item from the original research dossier (GMI console pricing, exact HeyGen constraints, disclosure/watermarking rules, etc.) — those remain `UNKNOWN`/deferred and are not gates for `CF-RUN-001` unless they turn out to block the chosen first path.

### Acceptance checks

1. Both questions above have a real-evidence answer (actual API request/response), or an explicit note of exactly what blocked the test within the $5 cap.
2. Actual recorded spend is logged call-by-call (provider, model, request purpose, cost) and the running total is checked against the $5 sub-cap before each subsequent call.
3. `GMI_API_KEY`'s value never appears in any file, commit, log, command output captured to a file, or receipt — only the environment-variable name.
4. No HeyGen account, credential, or API call exists anywhere in the evidence trail.
5. `git diff --check` is clean; no placeholder or contradiction regressions in the five live canon/state files.
6. Findings are labeled `VERIFIED (live test)`, `VERIFIED (official docs)`, `REPORTED`, or `UNKNOWN`.

### Test commands

```bash
test -f docs/ops/CURRENT_STATE.md
test -f docs/roadmap/CURRENT_ROADMAP.md
! rg -ni '<PROJECT''_NAME>|<FOUNDER''_NAME>|TO''DO|T''BD|IN''SERT|CHANGE''ME' README.md CLAUDE.md docs
! rg -n 'sk-[A-Za-z0-9]{10,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY|GMI_API_KEY\s*=\s*[\"'"'"'][A-Za-z0-9]' docs
git diff --check
```

### Workflow and receipt

1. Confirm base SHA unchanged on `main`.
2. Confirm `GMI_API_KEY` is present in the environment via a presence-only check (non-empty, never echoed) before any call.
3. Run the voice-clone test call, record result and actual cost.
4. Run the avatar-endpoint test call, record result and actual cost.
5. Stop at $5 cumulative actual spend or once both questions are answered.
6. Write findings to `docs/verification/CF-VERIFY-001.md`, update `CURRENT_STATE.md` and `CURRENT_ROADMAP.md` Phase 0.5 accordingly, commit, push, update the draft PR.
7. Return the standard receipt from `CLAUDE.md`, separating actual recorded spend from any remaining estimate.

### Rollback

Close the draft PR or revert the findings commit. Real paid calls made under this authorization are one-off provider charges with no rollback beyond not repeating them; the $5 cap bounds that exposure.

### Authority boundary

Claude may make the two GMI/Genblaze live test calls described above, up to $5 total actual spend, using the existing GMI key once its presence (not value) is confirmed. Claude may not create a HeyGen account or call a HeyGen endpoint, may not exceed the $5 sub-cap without a new explicit authorization, and may not treat this packet as license to run further exploratory paid calls beyond the two questions above.

### Required receipt additions

- Actual recorded spend, call-by-call, with provider, model, and cost.
- Explicit answer (or explicit block reason) for each of the two required questions.
- Confirmation that no HeyGen account/call was created.
- Confirmation that no runtime code was implemented and no service was deployed.

### Next dependent block

`CF-RUN-001`: single-authorized-creator runtime pilot, scoped using whichever first working video path this packet's findings support (GMI end-to-end if proven, or a documented fallback if not). Not to be written until this packet's two questions are answered or explicitly blocked.
