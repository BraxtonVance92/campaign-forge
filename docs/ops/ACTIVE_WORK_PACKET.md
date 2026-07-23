# Active Work Packet

This file tracks status against the block IDs defined in the founder's
`docs/roadmap/CAMPAIGNFORGE_EXECUTION_LEDGER.md` (D-023), which is the
controlling execution plan. Prior ad-hoc names (`CF-RUN-001`,
`CF-RUN-002`) map onto that ledger's blocks as noted below.

## CF-00 — Repository and state reconciliation

Status: `COMPLETE` as of this update (2026-07-21). Local `main` verified equal to remote at `e5b26eafd2917cd8bbfffa607f554195106c6a47`, then at `f201ba5fbca15326f81ef3605dd281c88f0d0f4b` after merging PR #6 (docs-only, CI green, mergeable, within already-granted documentation-synchronization authority — D-023). No other open PRs; no dirty working-tree changes found. The 84-test baseline was re-run and confirmed. The styled home and project pages were re-verified live through a running local server (`http://127.0.0.1:8734/`), never by opening raw template files. `docs/roadmap/CURRENT_ROADMAP.md` was annotated (not rewritten) to flag its contest-phase framing as not yet explicitly reconciled against the ledger's dad's-content-accuracy-first sequencing.

## CF-RUN-001 — Smallest real product flow: upload → analysis → persist → display

Status: `MERGED` — approved as-is at exact SHA `1cb15c937422517657c3e85463df4e440a11bfb0` (76 tests passing locally and in CI) and merged into `main` at merge commit `c9ae8bb3926c2589043d8467244dc7f51586543f` with explicit founder confirmation (D-020). Its UI was subsequently refined in PR #5 (desktop layout width fix, restructured result display, accessibility fixes, 84 tests passing) merged at `e5b26eafd2917cd8bbfffa607f554195106c6a47` (D-021). Not deployed; not live-verified. This is the concrete implementation that `CF-01`/`CF-02`/`CF-03` below now build on.

---

## CF-01 — Credential readiness without secret exposure

Classification: `RUNTIME`

Consumer: the CampaignForge product itself. This is the ledger's `CF-01` block (D-023), superseding the ad-hoc `CF-RUN-002` label (D-022) for the same substance.

Status: `BLOCKED_ON_CREDENTIALS`. No further code change is required to unblock this packet — the full upload → analyze → persist → display flow (including honest blocking on every real GMI/network/contract failure mode) is already implemented, tested, and merged. This packet's only remaining action is external: the founder supplying real `GMI_API_KEY` and B2 credentials (exact instructions in `docs/ops/CURRENT_STATE.md`'s "Founder setup instruction").

The ledger's `CF-01` also asks whether the provider can receive uploaded bytes directly, so B2 is not made a prerequisite merely because the current implementation assumes a URL. Researched 2026-07-21 (current official docs, re-fetched):

- `nemotron-3-nano-omni`'s own quickstart page (`docs.gmicloud.ai/model-quickstarts/text/nvidia-nvidia-nemotron-3-nano-omni.md`) still does not document video input at all — no `video_url` schema, and its one `image_url` example uses an illustrative `file:///path/to/image.jpg` placeholder, not a real base64 or hosted-URL example.
- A *different* model family on the same platform — GMI's video-*generation* API (`inference-engine/api-reference/video-api-reference.md`, e.g. `Veo3`) documents three real input mechanisms for file references: (1) an inline base64 data URI ("convenient for small files; large payloads may slow requests"), (2) a hosted `https://` URL, and (3) GMI's own two-step Upload API (request an upload URL, `PUT` raw bytes, get back a stable public URL) — a potential alternative to Backblaze B2 for getting a fetchable URL.
- **It is unverified whether either mechanism (base64 data URI or GMI's own Upload API) extends to `nemotron-3-nano-omni`'s chat-completions endpoint**, since that model's own documentation is silent on video input entirely. Writing speculative code against an unconfirmed capability on the wrong model's documented pattern would violate the "cite current official docs, don't guess" standard (D-014) — so no code change is made on this basis alone.
- **Practical effect on the founder instruction**: `docs/ops/CURRENT_STATE.md` is corrected below — it is not certain that B2 is required for the very first experiment. `GMI_API_KEY` alone may be sufficient if a small test video can be sent as a base64 data URI, but this is unverified and must be tested live, not assumed. B2 remains required by Product Canon for durable, restorable storage regardless of this experiment's outcome.
- **Recommendation for `CF-02`'s two-attempt rule**: attempt (a) a small base64 data-URI `video_url` block first (costs nothing extra, needs no B2 setup) and (b) a real hosted URL (via B2 presigned URL or GMI's own Upload API) second, if (a) fails — this satisfies the ledger's "two materially different documented approaches before declaring `BLOCKED`" rule with an evidence-based plan rather than a guess.

### Founder intent and business outcome

Move from "the real analysis path is implemented and tested against mocked/contract fixtures" to "one real, authorized creator video has actually been analyzed by GMI, live, with the true response persisted and displayed" — the first genuinely non-simulated result in this product's history.

### Base

- Repository: `BraxtonVance92/campaign-forge`
- Base branch: `main`
- Exact base SHA: `f201ba5fbca15326f81ef3605dd281c88f0d0f4b` (merge commit for PR #6 — updated from PR #5's `e5b26ea`, per R1/R2's shared non-blocking note on PR #7)
- Branch: (to be created when credentials are supplied and this packet becomes actionable — no branch exists yet for this packet, since there is no code change to make ahead of that)

### Scope

Exactly the same one video / one analysis result / one project slice as `CF-RUN-001` — this packet does not add new product surface. Its only job is to take that already-implemented flow from "tested against mocks/fixtures" to "actually run once against real GMI, live":

1. When real `GMI_API_KEY` and B2 credentials are supplied (by the founder, per the setup instruction in `docs/ops/CURRENT_STATE.md`), confirm `/health` reports both configured.
2. Upload one real authorized creator video through the running app.
3. Trigger analysis and confirm it produces a real, rendered creator profile — not a blocked card.
4. Capture sanitized evidence of that real call (provider, model, confidence value, whether contract validation passed) — never the raw provider response body, never a secret.
5. Only then, flip `app.analysis.REQUEST_SHAPE_VERIFIED` from `False` to `True` in `app/analysis.py`, and record the change in `docs/ops/DECISION_LOG.md`.
6. If B2 is configured but GMI is not (or vice versa), stop only the half that's missing and report exactly which credential is still absent — do not treat a partial configuration as a full blocker requiring no further explanation.

No code change is anticipated to be needed to reach this state — inspection on 2026-07-21 confirmed the upload/analyze/persist/display path, the credential-presence gate, and the honest-blocking behavior for every real failure mode are already implemented and tested (see `CF-RUN-001` above). If live testing reveals a real defect (e.g., the `video_url` request shape actually rejected by GMI — flagged as unverified in `app/analysis.py`'s module docstring), fixing that specific, evidenced defect is in scope; speculative pre-emptive changes are not.

### Allowed paths

- `app/analysis.py` — only to fix a real, live-evidenced defect in the request/response handling, or to flip `REQUEST_SHAPE_VERIFIED` after a real success
- `docs/ops/ACTIVE_WORK_PACKET.md`, `docs/ops/CURRENT_STATE.md`, `docs/ops/DECISION_LOG.md` — status/evidence updates only, no product redefinition
- `tests/` — new focused tests proving the real call's evidence-capture and any live-evidenced fix
- No new CI/workflow file is anticipated; this is a manual, credential-gated, founder-triggered action, not an automated pipeline, consistent with `CF-VERIFY-001`'s established pattern (D-014) of never letting live provider calls run unattended or on every push/PR

### Forbidden paths and scope

- `CLAUDE.md`, `docs/canon/*`, `docs/ops/AUTHORITY_MATRIX.md`
- Voice cloning, avatar/face generation, any HeyGen integration
- Publishing/distribution features, billing/payment code, authentication expansion, any unrelated UI
- Render service creation, production deployment
- Any new CI/workflow file — a real live GMI call must never run unattended in an automated pipeline; it stays a manual, founder-supervised action
- Real B2 or GMI credentials in any file, log, test, commit, or receipt — environment-variable names only, values only ever in the local, gitignored `.env`
- Fabricating, inventing, or reusing a non-authorized "test" creator video to exercise this flow — the consent chain in `docs/canon/FOUNDER_CANON.md`/D-011 requires a real, person-specific authorization, which only the founder can supply

### External dependencies and blockers, stated up front

- `GMI_API_KEY`: not present in this environment (re-confirmed 2026-07-21). Required for any real call.
- Real Backblaze B2 credentials (`B2_KEY_ID`, `B2_APPLICATION_KEY`, `B2_BUCKET_NAME`, `B2_ENDPOINT`): also not present (re-confirmed 2026-07-21). Required alongside GMI — see the "both together" note in `docs/ops/CURRENT_STATE.md`.
- A real, authorized creator video to upload: this packet cannot supply one on its own; it requires the founder (or another verified-authorized creator) to provide it, consistent with the consent requirement above.

### Required behavior

- No real call may ever be simulated, faked, or inferred from a mocked fixture and then described as live. If credentials are absent, this packet stays `BLOCKED_ON_CREDENTIALS` and says so plainly — it does not manufacture partial progress.
- Consent attestation (already enforced at upload time by `CF-RUN-001`) is not weakened or bypassed to make testing more convenient.

### Acceptance checks

1. `/health` shows `gmi_configured: true` and `b2_configured: true` before any live call is attempted.
2. One real analysis produces a rendered, non-blocked creator profile, observed directly (screenshot or equivalent), not merely inferred from logs.
3. `app.analysis.REQUEST_SHAPE_VERIFIED` is flipped to `True` only after step 2, in the same change that records the evidence.
4. No secret value or raw provider response body appears in any file, test, log, commit, or receipt.
5. Full test suite still passes after any change.

### Workflow and receipt

1. Confirm the founder has supplied credentials per the setup instruction (or stop here and report the blocker, taking no further action on this specific packet).
2. Verify `/health` reports both configured.
3. Perform the one real analysis through the running app with a founder-supplied authorized video.
4. Capture sanitized evidence; flip `REQUEST_SHAPE_VERIFIED`; update the three ops docs and `DECISION_LOG.md` in the same change.
5. Run the full test suite; commit, push, open/update a draft PR; return the standard receipt from `CLAUDE.md`.

### Rollback

Revert the `REQUEST_SHAPE_VERIFIED` flip and any accompanying doc changes; no deployment or irreversible external action occurs as part of this packet.

### Authority boundary

Claude may check `/health`, run the one real analysis once credentials and an authorized video are supplied, capture sanitized evidence, flip `REQUEST_SHAPE_VERIFIED`, update docs, commit, push, and open/update a draft PR without further per-step approval, per standing authority in `docs/ops/AUTHORITY_MATRIX.md` and the founder's standing instruction (D-022). Claude may not merge this PR, deploy, create a Render service, add any new CI/workflow file, spend money, or fabricate/claim a live result without direct evidence.

### Next dependent block

Once this slice is genuinely live-verified: extend to the Genblaze generation leg (script → voice → face/avatar video) per `docs/roadmap/CURRENT_ROADMAP.md` Phases 2-4, informed by what this real GMI call reveals about actual response shape and quality.

## CF-V4 (active, 2026-07-23)

Colton V4: first private video using his authorized likeness and voice.
Preparation MERGED (PRs #14, #15; decision D-027). Generation BLOCKED on
the four-part founder/Colton action in
`docs/verification/CF-V4-runbook.md` (consent artifact -> GMI $10 ->
B2 credentials -> HeyGen $29 approval). Local reference candidates
extracted and hashed 2026-07-23 (see
`docs/verification/CF-V4-preproduction.md`, Reference sufficiency).
Consumer: founder (blocker actions), then the maker session (runbook).

Update 2026-07-23 (batch analysis, PR #17): five authorized reference
videos ingested and analyzed locally ($0, nothing uploaded); frontal
reference frames now exist; a GMI lip-sync route is PROPOSED as primary
(pending founder ratification of face-footage-to-GMI exposure — see
`docs/verification/CF-V4-batch-analysis-receipt.md`); the D-027 HeyGen
likeness route remains the standing default until ratified. Blocker is
now: consent artifact -> route ratification -> GMI $10 -> B2 credentials
-> (route 2 only) HeyGen $29.
