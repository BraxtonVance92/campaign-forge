# Active Work Packet

## CF-BOOT-001 — Correct CampaignForge sources of truth to restore authorized face-and-voice scope

Classification: `DOCS-ONLY`

Consumer: GPT controller/CTO and every later Claude Code runtime packet.

Status: `IN_PROGRESS` — amended following a binding founder correction; pending controller review.

### Amendment note

This packet originally committed the seven draft sources of truth. The founder subsequently rejected D-005 (excluding face and voice cloning) as incorrect and issued a binding correction: authorized face-and-voice video generation is the core product, not optional or deferred scope. This amendment corrects `docs/canon/FOUNDER_CANON.md`, `docs/canon/PRODUCT_CANON.md`, `docs/ops/DECISION_LOG.md`, `docs/roadmap/CURRENT_ROADMAP.md`, `docs/ops/CURRENT_STATE.md`, and `docs/ops/AUTHORITY_MATRIX.md` to reflect that correction. It remains docs-only.

### Founder intent and business outcome

Make every source of truth coherent and truthful about the founder's actual product — authorized creator replication into new playable video via cloned voice and face/avatar generation — so the controller can write a dispatchable provider-verification packet, and so Claude never re-derives or re-proposes the rejected no-face/no-voice direction.

### Base

- Repository: `BraxtonVance92/campaign-forge`
- Base branch: `main`
- Exact base SHA: `269d2900b1131c793d7cdf2e87655891f5256149`
- Prior candidate SHA (before this amendment): `7ffd242ed90c8955fbc027997d03eb9529bcc6b9`
- Maker must fetch and stop if `main` has changed until the controller reconciles the new base.

### Allowed paths

- `docs/canon/FOUNDER_CANON.md`
- `docs/canon/PRODUCT_CANON.md`
- `docs/roadmap/CURRENT_ROADMAP.md`
- `docs/ops/AUTHORITY_MATRIX.md`
- `docs/ops/CURRENT_STATE.md`
- `docs/ops/ACTIVE_WORK_PACKET.md`
- `docs/ops/DECISION_LOG.md`
- `README.md` only to keep the documentation index accurate; do not claim runtime functionality.

### Forbidden paths

- `CLAUDE.md`
- Any runtime source, deployment, CI, secret, bucket, provider, billing, or infrastructure change.
- No Render service creation, no deployment, no paid provider calls.

### Dependencies and constraints

- The founder's correction is binding and does not require further approval to record; it is itself the approval.
- Official rules and current primary technical sources beat summaries.
- Preserve the exact distinction between repository-verified facts, reported history, assumptions, and plans.
- Do not copy secrets or personal data into documentation.
- Do not invent founder approval for any decision the founder has not actually made (for example, specific providers, models, or the technical stack remain `PROPOSED`).

### Required behavior

Every changed document agrees that authorized face-and-voice video generation is core, undeferred product scope, subject to verified per-person consent. No document may state or imply that face or voice generation is excluded, optional, or contest-only.

### Acceptance checks

1. All seven files exist at the exact paths named by `CLAUDE.md`.
2. `rg` finds no unresolved angle-bracket placeholders, no planning stand-ins, and no invented secret values in `README.md`, `CLAUDE.md`, or `docs/` (see the test command below for the exact literal patterns checked).
3. A contradiction scan finds no remaining statement that excludes face cloning, excludes voice cloning, defers face/voice until after the contest, or reduces the product to generic branded imagery.
4. `docs/ops/CURRENT_STATE.md` does not claim source, CI, deployment, analysis, consent, voice, face, video, or billing evidence that is absent.
5. `docs/canon/FOUNDER_CANON.md`, `docs/canon/PRODUCT_CANON.md`, and `docs/roadmap/CURRENT_ROADMAP.md` describe the same corrected golden path.
6. `docs/ops/AUTHORITY_MATRIX.md` requires founder approval for removing face/voice from scope, exceeding the $50 ceiling, production deployment, and contest submission, and requires creator-specific consent for likeness/voice use.
7. `git diff --check` is clean.
8. Markdown links and tables render/read cleanly.

### Test commands

```bash
test -f docs/canon/FOUNDER_CANON.md
test -f docs/canon/PRODUCT_CANON.md
test -f docs/roadmap/CURRENT_ROADMAP.md
test -f docs/ops/AUTHORITY_MATRIX.md
test -f docs/ops/CURRENT_STATE.md
test -f docs/ops/ACTIVE_WORK_PACKET.md
test -f docs/ops/DECISION_LOG.md
! rg -ni '<PROJECT''_NAME>|<FOUNDER''_NAME>|TO''DO|T''BD|IN''SERT|CHANGE''ME' README.md CLAUDE.md docs
! rg -ni 'exclu(de|ded|des|ding)[^.]*(face|voice)|(face|voice)[^.]*exclu(de|ded|des|ding)' docs
! rg -ni 'outside the contest MVP|deferred until after the contest' docs
git diff --check
```

No browser, API, security, or accessibility proof is required because the packet is docs-only. Repository/secret hygiene inspection is required.

### Workflow and receipt

1. Inspect `main` and confirm base SHA unchanged.
2. Amend the existing `docs/cf-boot-001` branch (already pushed; do not force-push).
3. Edit only allowed files, run checks, commit, push, and update draft PR #1.
4. Return the standard receipt from `CLAUDE.md`, with local/remote head equality.

### Rollback

Close draft PR #1 or revert the correction commit(s). No runtime behavior or external system is affected; `main` is untouched.

### Authority boundary

Claude may edit allowed paths, test, commit, push the existing feature branch, and update the draft PR. It may not merge, deploy, submit, spend, create a Render service, or alter secrets.

### Required receipt additions

- Confirmation that the earlier no-face/no-voice direction (D-005) is recorded as REJECTED/SUPERSEDED.
- Confirmation that no runtime code was implemented.
- Confirmation that no Render service was created and no deployment occurred.
- Exact changed files and checks run.

### Next dependent block

`CF-VERIFY-001`: provider capability and architecture verification for authorized voice cloning and face/avatar generation (Roadmap Phase 0.5) — answer, with cited evidence, which provider(s) support these capabilities, their input/output/cost/latency shape, and the narrowest Render-deployable architecture, before any runtime implementation packet is written.
