# Active Work Packet

## CF-BOOT-001 — Commit and reconcile CampaignForge sources of truth

Classification: `DOCS-ONLY`

Consumer: GPT controller/CTO and every later Claude Code runtime packet.

Status: `PLANNED` pending founder approval of the draft content.

### Founder intent and business outcome

Give Claude complete, contest-aware instructions so it can build the intended product without inventing scope, violating contest rules, confusing prototypes with real capability, or repeatedly asking the founder to design the system.

### Base

- Repository: `BraxtonVance92/campaign-forge`
- Base branch: `main`
- Expected base SHA: `269d2900b1131c793d7cdf2e87655891f5256149`
- Maker must fetch and stop if main has changed until the controller reconciles the new base.

### Allowed paths

- `docs/canon/FOUNDER_CANON.md`
- `docs/canon/PRODUCT_CANON.md`
- `docs/roadmap/CURRENT_ROADMAP.md`
- `docs/ops/AUTHORITY_MATRIX.md`
- `docs/ops/CURRENT_STATE.md`
- `docs/ops/ACTIVE_WORK_PACKET.md`
- `docs/ops/DECISION_LOG.md`
- `README.md` only to add a short documentation index; do not claim runtime functionality.

### Forbidden paths

- `CLAUDE.md`
- Any runtime source, deployment, CI, secret, bucket, provider, billing, or infrastructure change.

### Dependencies and constraints

- Founder approval or corrections to these drafts.
- Official rules and current primary technical sources beat summaries.
- Preserve the exact distinction between repository-verified facts, reported history, assumptions, and plans.
- Do not copy secrets or personal data into documentation.

### Required behavior

The repository root contract can resolve all seven referenced files. The documents agree on the focused product, contest requirements, $50 ceiling, current state, authority boundaries, smallest pilot, and next packet. Links work in GitHub.

### Acceptance checks

1. All seven files exist at the exact paths named by `CLAUDE.md`.
2. `rg` finds no unresolved angle-bracket templates, planning placeholders, or invented secret values.
3. Current State does not claim source, CI, deployment, analysis, generation, or billing evidence that is absent.
4. Product Canon, Roadmap, and Founder Canon define the same golden path.
5. Authority Matrix requires founder approval for first production deployment and contest submission.
6. Markdown links and tables render/read cleanly.

### Test commands

```bash
test -f docs/canon/FOUNDER_CANON.md
test -f docs/canon/PRODUCT_CANON.md
test -f docs/roadmap/CURRENT_ROADMAP.md
test -f docs/ops/AUTHORITY_MATRIX.md
test -f docs/ops/CURRENT_STATE.md
test -f docs/ops/ACTIVE_WORK_PACKET.md
test -f docs/ops/DECISION_LOG.md
! rg -n '<PROJECT''_NAME>|<FOUNDER''_NAME>|TO''DO|T''BD' README.md CLAUDE.md docs
git diff --check
```

No browser, API, security, or accessibility proof is required because the packet is docs-only. Repository/secret hygiene inspection is required.

### Workflow and receipt

1. Inspect main and confirm base SHA.
2. Create `docs/cf-boot-001` from the exact base.
3. Add only allowed files, run checks, commit, push, and open/update a draft PR.
4. Return the standard receipt from `CLAUDE.md`, with local/remote head equality.

### Rollback

Close the draft PR or revert the documentation commit. This packet changes no runtime behavior or external system.

### Authority boundary

Claude may branch, edit allowed paths, test, commit, push the feature branch, and open a draft PR. It may not merge, deploy, submit, spend, or alter secrets.

### Required receipt additions

- List official external sources used and access date.
- List every statement corrected from the supplied draft.
- State that no runtime behavior changed.

### Next dependent block

`CF-RUN-001`: establish tested web/API/CI foundation and prove the real upload -> analysis -> persist -> display pilot. The controller writes that packet only after this docs packet is approved and merged.
