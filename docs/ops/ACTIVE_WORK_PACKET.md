# Active Work Packet

## CF-VERIFY-001 — Live provider capability verification for authorized voice cloning and face/avatar generation

Classification: `VERIFICATION`

Consumer: the next runtime packet (`CF-RUN-001`, the single-authorized-creator pilot), which must not be written or dispatched until this packet's findings exist.

Status: `PLANNED` — dispatched by the founder following merge of `CF-BOOT-001`; has open items requiring founder resolution before live paid calls can run (see "Founder items to resolve" below).

### Predecessor

`CF-BOOT-001` is `MERGED` at main SHA `3e06fc2e076f09c7b077d3f5e803583cd0ada5e4` (founder-approved at exact SHA `9ae223920b0f71aed1831070a5ba9f4924683aec`). A read-only documentation research dossier was already produced in the maker session on 2026-07-21, covering Genblaze/GMI Cloud, voice-clone providers, face/avatar providers, Backblaze B2, and Render, using official documentation only. This packet exists to resolve that dossier's `UNKNOWN — live test required` items with real, minimal, budgeted API calls — it is narrower than a full runtime build.

### Founder intent and business outcome

Before any runtime code is written, prove with real (not documentation-inferred) evidence which providers can actually deliver authorized voice cloning and face/avatar video generation end to end, at what cost and latency, so `CF-RUN-001` can be scoped accurately instead of discovered mid-build.

### Base

- Repository: `BraxtonVance92/campaign-forge`
- Base branch: `main`
- Exact base SHA: `3e06fc2e076f09c7b077d3f5e803583cd0ada5e4`
- Maker must fetch and stop if `main` has changed until the controller/founder reconciles the new base.

### Allowed paths

- `docs/roadmap/CURRENT_ROADMAP.md` (record verified findings against the Phase 0.5 verification block)
- `docs/ops/CURRENT_STATE.md`
- `docs/ops/ACTIVE_WORK_PACKET.md`
- `docs/ops/DECISION_LOG.md`
- A new `docs/verification/CF-VERIFY-001.md` findings file (create if useful for the length of evidence gathered)

### Forbidden paths

- `CLAUDE.md`, `docs/canon/*`, `docs/ops/AUTHORITY_MATRIX.md` (no product/authority redefinition in a verification packet)
- Any runtime application source, CI, deployment, or infrastructure-as-code file
- No Render service creation, no production deployment

### Founder items to resolve before any paid call runs

1. **Provider split confirmation**: the dossier recommends HeyGen's direct API (not GMI's `heygen-avatar-4` wrapper) for face/avatar video, plus MiniMax voice-clone via GMI/Genblaze for voice — a different combination than `docs/canon/PRODUCT_CANON.md`'s original GMI-only assumption. Needs a founder/controller nod before it's treated as binding.
2. **New paid service**: HeyGen is a new provider with no existing credentials in this project. Creating an account and API key is a new paid service under `docs/ops/AUTHORITY_MATRIX.md` ("Add paid service or exceed $50 project ceiling" — Founder approves). Claude Code will not sign up for or fund a HeyGen account without this approval.
3. **Ceiling scope**: does the $50 ceiling cover hosting (Render Starter/worker, ~$7-14/month) or only one-off provider API calls? This changes which architecture option from the dossier is viable and must be a founder ruling, not an assumption.
4. **GMI key**: a GMI inference key was reported (not repository-verified) as already saved in a hosted environment. If the founder wants that key reused rather than a new one issued, they must confirm it is still valid and provide it only through an approved secret-store mechanism — never in chat, commit, or receipt.

### Required behavior (once resolved)

Answer, with cited evidence from an actual API response (not documentation alone), each `UNKNOWN` item from the CF-VERIFY-001 dossier:

- Does Genblaze's `Pipeline`/`Step` successfully invoke the MiniMax voice-clone model through the `genblaze-gmicloud` adapter end to end (not just the image/video sample path)?
- Does GMI's `heygen-avatar-4` model return a downloadable/playable video file in any mode, or only a live WebRTC session?
- What are HeyGen's actual training-footage constraints (length, resolution, format) per a live API response or authoritative reference page, not a secondhand summary?
- What is the actual measured latency for: a MiniMax voice-clone call; a HeyGen Digital Twin creation; a HeyGen Avatar V video render?
- What is the actual current per-model price shown in the GMI console for the specific models used (GMI's console-only pricing was not visible to documentation-only research)?
- What disclosure/watermarking requirements, if any, are stated in either provider's current terms?

### Acceptance checks

1. Every `UNKNOWN — live test required` item from the dossier has either a cited real-evidence answer or an explicit note that it remains blocked on a founder item above.
2. Any real API call made is the smallest and cheapest that answers the question (e.g., the shortest allowed reference clip, the shortest test video), with its exact cost recorded against actual, not estimated, spend.
3. Cumulative actual spend recorded and reconciled against the $50 ceiling before and after each paid call.
4. No credential value appears in any file, commit, log, or receipt — only environment-variable names.
5. `git diff --check` is clean; no placeholder or contradiction regressions in the five live canon/state files (same scan as `CF-BOOT-001`).
6. Findings are written as evidence, distinctly labeled `VERIFIED (live test)`, `VERIFIED (official docs)`, `REPORTED`, or `UNKNOWN`, per the discipline established in the CF-BOOT-001 correction.

### Test commands

```bash
test -f docs/ops/CURRENT_STATE.md
test -f docs/roadmap/CURRENT_ROADMAP.md
! rg -ni '<PROJECT''_NAME>|<FOUNDER''_NAME>|TO''DO|T''BD|IN''SERT|CHANGE''ME' README.md CLAUDE.md docs
! rg -n 'sk-[A-Za-z0-9]{10,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY' docs
git diff --check
```

### Workflow and receipt

1. Confirm base SHA unchanged on `main`.
2. Resolve the founder items above, or proceed only with the zero-cost/no-new-credential sub-questions if the founder has not yet responded (for example, re-fetching a HeyGen reference page that failed to render fully in the prior research pass costs nothing and needs no new credential).
3. For any item requiring spend or new credentials, wait for explicit founder authorization naming the exact provider, exact estimated cost, and exact ceiling headroom before making the call.
4. Record findings, commit, push, open/update a draft PR.
5. Return the standard receipt from `CLAUDE.md`, including actual recorded spend separated from estimates.

### Rollback

Close the draft PR or revert the findings commit. No runtime behavior or external system is affected by the documentation side of this packet; any real paid call made under explicit authorization is a one-off provider charge with no rollback beyond not repeating it.

### Authority boundary

Claude may branch, research, run free/already-authorized-cost read-only checks, commit, push, and open a draft PR without further approval. Claude may not create a HeyGen (or other new provider) account, spend against the $50 ceiling, or use the reported GMI key until the founder resolves the four items above with an explicit, named authorization.

### Required receipt additions

- Actual recorded spend (if any), separated from estimated spend, with provider, model, and exact cost per call.
- Explicit confirmation of which founder items remain unresolved, if any.
- Confirmation that no runtime code was implemented and no service was deployed.

### Next dependent block

`CF-RUN-001`: single-authorized-creator runtime pilot (consent capture -> B2 upload -> real analysis -> script -> cloned voice -> face/avatar video -> B2 persistence -> restore/playback), scoped using this packet's live-verified findings. Not to be written until CF-VERIFY-001 is `REVIEW_READY`.
