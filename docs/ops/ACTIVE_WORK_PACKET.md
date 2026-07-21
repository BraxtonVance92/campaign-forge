# Active Work Packet

## CF-RUN-001 — Smallest real product flow: upload → analysis → persist → display

Classification: `RUNTIME`

Consumer: the CampaignForge product itself — this is the first runtime application code in this repository. Founder/controller dispatched this packet directly, in the same message that authorized merging its predecessor (`CF-VERIFY-001`, merged at main SHA `f195833bd67236346f9865485be5b6a8424e3573`), explicitly instructing continuous work without waiting for a separately-formatted packet.

Status: `IN_PROGRESS`.

### Founder intent and business outcome

Prove the golden path's first real slice, narrowly: one authorized creator uploads one video, a real analysis runs (or is cleanly blocked and marked as such if the credential isn't available), the structured result persists, and it can be retrieved/displayed. This is not the full contest MVP — it is the smallest vertical slice that is real rather than simulated.

### Base

- Repository: `BraxtonVance92/campaign-forge`
- Base branch: `main`
- Exact base SHA: `f195833bd67236346f9865485be5b6a8424e3573` (merge commit for PR #2)
- Branch: `feat/cf-run-001`

### Scope

Exactly one video, one analysis result, one project. No multi-example learning, no multi-tenant concerns yet.

Required flow:

1. Upload one authorized creator video with a required consent attestation.
2. Validate the upload (file type, size, consent present).
3. Persist the original and its metadata.
4. Run real analysis via GMI/Genblaze if `GMI_API_KEY` is available; if not, implement and test everything up to that call and mark it as an explicit, honest blocker — never a fake or placeholder result.
5. Persist the structured analysis result (or the "blocked" state) if analysis ran.
6. Retrieve and display the source + result (or the honest not-yet-analyzed/blocked state) through a minimal interface.

### Allowed paths

- New application source under `app/` (or equivalent minimal FastAPI project layout)
- New `tests/` directory
- `requirements.txt` / `pyproject.toml` and a `.env.example` (names only, no values)
- `README.md` — update to reflect that runtime code now exists and how to run it
- `docs/ops/ACTIVE_WORK_PACKET.md`, `docs/ops/CURRENT_STATE.md`, `docs/ops/DECISION_LOG.md` — status/evidence updates only, no product redefinition

### Forbidden paths and scope

- `CLAUDE.md`, `docs/canon/*`, `docs/ops/AUTHORITY_MATRIX.md`
- Voice cloning, avatar/face generation, any HeyGen integration
- Publishing/distribution features, billing/payment code, authentication expansion beyond what this flow strictly needs (no new user-account system)
- Any unrelated UI beyond what this one flow needs
- Render service creation, production deployment, `.github/workflows/*` changes (CI remains out of scope for this packet)
- Real B2 or GMI credentials in any file, log, test, commit, or receipt — environment-variable names only

### Technical stack

No existing application stack exists in this repository to reuse — `CF-BOOT-001`/`CF-VERIFY-001` were docs/CI-only. The closest documented direction is `docs/canon/PRODUCT_CANON.md`'s "Recommended technical shape" (D-006 in `docs/ops/DECISION_LOG.md`, still `PROPOSED`, not founder-approved as binding): Python 3.11+ FastAPI. This packet follows that recommendation for the API/backend since it is the only documented direction and Genblaze (the required orchestration SDK) is a Python package; the UI is kept to the minimum needed to satisfy "display it" — a server-rendered page, not a separate frontend framework, to avoid adding scope not required by this narrow flow.

### External dependencies and blockers, stated up front

- `GMI_API_KEY`: not present in this environment. The analysis call is implemented and unit-tested against a documented response-contract fixture, but the real external call is gated behind this credential's presence and marked blocked if absent.
- Real Backblaze B2 credentials (`B2_KEY_ID`, `B2_APPLICATION_KEY`, `B2_BUCKET_NAME`, `B2_ENDPOINT`): also not present in this environment — this is an additional blocker beyond the one named in the dispatch instruction, surfaced here rather than silently assumed. The storage layer is built against a real B2 (S3-compatible) client for production use, with a fake in-memory implementation of the same interface used for tests, so persistence logic is proven without needing live credentials.

### Required behavior

- Every stage from `docs/canon/PRODUCT_CANON.md`'s "System stage contract" that this packet touches must be evidenced through its real boundary (real validation, real parsing logic against the documented contract, real persistence logic) or explicitly marked blocked — never asserted as working without evidence.
- Consent attestation is required at upload time, consistent with `docs/canon/FOUNDER_CANON.md`'s trust/consent rules — not optional, not deferred.

### Acceptance checks

1. Focused tests exist and pass for: upload validation, analysis-response parsing, persistence, and result retrieval/display.
2. No fake analysis result is ever presented as real; the blocked state is explicit and visible wherever the real result would otherwise appear.
3. No secret value appears in any file, test, log, or commit.
4. `git diff --check` is clean.
5. README accurately reflects what now exists and how to run/test it.

### Workflow and receipt

1. Confirm base SHA unchanged on `main`.
2. Implement in focused commits: storage abstraction → upload/consent endpoint → analysis client/parsing → persistence → display/restore.
3. Run the full test suite; record real pass/fail output.
4. Commit and push checkpoints as work progresses; open a draft PR (not merged).
5. Return the standard receipt from `CLAUDE.md`, clearly separating what is real/tested from what is blocked.

### Rollback

Close the draft PR or revert its commits; `main` is unaffected until a future, separately-reviewed merge.

### Authority boundary

Claude may implement, test, commit, and push this feature branch and open/update its draft PR without further approval, per standing authority in `docs/ops/AUTHORITY_MATRIX.md`. Claude may not merge this PR, deploy, create a Render service, add or modify CI workflows, or use real GMI/B2 credentials that are not actually present in the environment.

### Next dependent block

Once this slice is real and reviewed: extend to the Genblaze generation leg (script → voice → face/avatar video) per `docs/roadmap/CURRENT_ROADMAP.md` Phases 2-4, informed by whatever `CF-VERIFY-001` live testing eventually finds.
