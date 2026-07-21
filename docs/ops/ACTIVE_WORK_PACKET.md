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
- `.github/workflows/cf-verify-001.yml` — see amendment below. This is the one narrow exception to this packet's own general CI/infrastructure-as-code prohibition.

Any other throwaway script needed to make live API calls is written outside the repository (session scratch space), not committed.

### Amendment: authorized CI file for secret entry and execution

This packet's original "Forbidden paths" list (below) excluded all CI files. That is amended for exactly one file: `.github/workflows/cf-verify-001.yml`, a `workflow_dispatch`-only (manually triggered, never on push/PR/schedule) GitHub Actions workflow that reads `GMI_API_KEY` from GitHub's own repository-secret store — the only secure, click-only secret-entry mechanism actually available for this project, since this session has no secret-entry UI and the founder/controller declined terminal and manual-file-based approaches. No other CI, deployment, or infrastructure-as-code file is authorized by this amendment.

### Amendment 2: merging this PR before execution is authorized

`workflow_dispatch` cannot be reliably triggered for a workflow that exists only on a feature branch — GitHub's manual-dispatch UI and API both expect the workflow file to be registered from the default branch. Merging PR #2 (containing only this packet's documentation and the one reviewed workflow file) into `main` is therefore authorized as the next step, distinct from and prior to actually triggering the workflow. Merging is not the same action as execution: merging only makes the workflow dispatchable; a human with repository write access still has to separately add the `GMI_API_KEY` secret and click "Run workflow." Claude Code may merge once this revision's diff has been reviewed, but has not done so as part of producing this revision itself — see Authority boundary.

### Forbidden paths

- `CLAUDE.md`, `docs/canon/*`, `docs/ops/AUTHORITY_MATRIX.md`
- Any runtime application source, CI, deployment, or infrastructure-as-code file, **except** the single `.github/workflows/cf-verify-001.yml` file described in the amendment above
- No Render service creation, no production deployment
- No HeyGen account creation or HeyGen API call
- No other GitHub Actions workflow, no changes to any existing CI/CD configuration beyond the one new file

### Required behavior

Run the smallest, cheapest real GMI/Genblaze API calls that answer exactly two questions:

1. **Voice cloning**: does GMI's `minimax-audio-voice-clone-speech-2.6-hd` produce real cloned-voice audio end to end? Uses a single fixed, hardcoded call (no user-editable text, source, or repeat count) against the verified endpoint `https://console.gmicloud.ai/api/v1/ie/requestqueue/apikey/requests`, with a predetermined non-personal synthetic reference clip generated on the runner itself — not a real creator's voice, since no verified creator consent record exists yet (per `docs/canon/PRODUCT_CANON.md`'s consent-first rule, Phase 2 of the roadmap has not run). This test proves the mechanism works; it does not produce a usable creator asset. Documented worst-case cost ceiling: $1.00 (the ~$0.10/request figure found is REPORTED, not independently verified on an official static page; budgeted at 10x as a safety margin).
2. **Avatar output format**: a single fixed, real `heygen-avatar-4` request (same verified endpoint, hardcoded short phrase, no user-editable duration) that determines whether GMI returns a downloadable/playable media file or only live session/stream fields — not a metadata-only guess. Documented worst-case cost ceiling: $0.20 (VERIFIED official rate $0.0667/sec, docs.gmicloud.ai quickstart and gmicloud.ai blog agree, for a ~1-2 second fixed phrase).

Combined documented worst-case ceiling: **$1.20**, well under the $5 CF-VERIFY-001 sub-cap — this is an enforced property of using two fixed, hardcoded, non-repeatable calls, not merely a reminder logged after the fact. If either question is answered, or if a call cannot be made safely (e.g., the endpoint fails the runtime host-allowlist check, or the synthetic clip can't be published), stop; do not attempt to resolve every remaining item from the original research dossier (GMI console pricing, exact HeyGen constraints, disclosure/watermarking rules, etc.) — those remain `UNKNOWN`/deferred and are not gates for `CF-RUN-001` unless they turn out to block the chosen first path.

### Acceptance checks

1. Both questions above have a real-evidence answer (actual API request/response, polled to a terminal status), or an explicit note of exactly what blocked the test.
2. Actual recorded spend is logged call-by-call (provider, model, request purpose, cost) and compared against the $1.20 documented worst-case ceiling; both calls are fixed/hardcoded so no runtime spend-tracking loop is needed to stay under the $5 sub-cap.
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
3. Run the fixed voice-clone test call, record result and actual cost.
4. Run the fixed avatar test call, record result and actual cost.
5. Both calls are hardcoded and non-repeatable within a single run, so cumulative spend cannot exceed the documented $1.20 worst-case ceiling without a separate, deliberate re-run.
6. Write findings to `docs/verification/CF-VERIFY-001.md`, update `CURRENT_STATE.md` and `CURRENT_ROADMAP.md` Phase 0.5 accordingly, commit, push, update the draft PR.
7. Return the standard receipt from `CLAUDE.md`, separating actual recorded spend from any remaining estimate.

### Rollback

Close the draft PR or revert the findings commit. Real paid calls made under this authorization are one-off provider charges with no rollback beyond not repeating them; the fixed, hardcoded, non-repeating design of both calls bounds that exposure to the documented $1.20 worst-case ceiling, well inside the $5 sub-cap.

### Authority boundary

Claude may make the two GMI/Genblaze live test calls described above, up to $5 total actual spend, using the existing GMI key once its presence (not value) is confirmed. Claude may not create a HeyGen account or call a HeyGen endpoint, may not exceed the $5 sub-cap without a new explicit authorization, and may not treat this packet as license to run further exploratory paid calls beyond the two questions above.

For the GitHub Actions execution path specifically: Claude may **prepare, push, and (per Amendment 2, once this revision is reviewed) merge** `.github/workflows/cf-verify-001.yml` and this packet's documentation into `main`, since the workflow cannot be reliably dispatched from a feature branch. Merging is authorized as a distinct step from triggering. Claude may **not** trigger (`workflow_dispatch`) the workflow under any circumstance, whether before or after merge. Execution is a separately authorized action — someone with repository write access clicks "Run workflow" in the GitHub UI after adding the `GMI_API_KEY` repository secret and reviewing the merged workflow file. Claude cannot click that button itself (no such control is exposed to any tool available to it) and is not authorized to attempt to trigger it via the API either.

### Required receipt additions

- Actual recorded spend, call-by-call, with provider, model, and cost.
- Explicit answer (or explicit block reason) for each of the two required questions.
- Confirmation that no HeyGen account/call was created.
- Confirmation that no runtime code was implemented and no service was deployed.

### Next dependent block

`CF-RUN-001`: single-authorized-creator runtime pilot, scoped using whichever first working video path this packet's findings support (GMI end-to-end if proven, or a documented fallback if not). Not to be written until this packet's two questions are answered or explicitly blocked.
