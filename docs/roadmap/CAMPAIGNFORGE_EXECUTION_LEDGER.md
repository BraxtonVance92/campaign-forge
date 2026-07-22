# CampaignForge Execution Ledger

Binding founder document, issued 2026-07-21. Supersedes ad-hoc packet naming
(e.g. the previously-drafted `CF-RUN-002`) with the block IDs (`CF-00`
through `CF-22`) defined here. Where this ledger and any other doc
conflict on sequencing or gates, this ledger controls; where repository
evidence contradicts a claim in this ledger, repository evidence controls
and this file's "Verified starting point" section must be corrected. See
`docs/ops/DECISION_LOG.md` D-023.

## Purpose

This is the controlled path from CampaignForge's verified state on July 21,
2026 to the founder's desired end result: an AI content studio that can
ingest a creator's authorized videos and carousels, learn the creator's
real style and performance patterns, generate useful ideas and scripts in
that style, and eventually produce reviewable content assets — first
proving accuracy on the founder's dad's content, then becoming a
repeatable product for other authorized creators and businesses.

This ledger prevents two recurring mistakes:

1. Building a large business before proving the analysis is accurate
   enough to matter.
2. Calling mocked, local, experimental, or merely implemented behavior
   "working" without real evidence.

## Binding product doctrine

- The immediate objective is accuracy validation on the founder's dad's
  authorized content, not launching a broad SaaS.
- Avoid manual busywork. The system should extract metadata, transcripts,
  frames, hooks, structure, and other usable signals automatically
  wherever technically and legally possible.
- Start with a small representative batch, not a manually labeled library
  of twenty "top performers." Performance comparisons are a later test and
  require trustworthy platform metrics or a minimal imported data file.
- Face and voice generation remain out of scope until creator consent is
  verified and analysis/script value is proven.
- Do not claim that AI output is the creator's actual voice, opinion, or
  endorsement. Preserve human review and required disclosure.
- Founder spending ceiling: $50 total unless explicitly changed. Report
  estimated cost separately from recorded spend.
- One active execution block at a time. Later blocks may be prepared, but
  implementation cannot jump a failed gate.

## Verified starting point

Use these as reported facts that Claude must re-verify against GitHub
before changing anything:

- Remote `main` was reported at merge SHA
  `e5b26eafd2917cd8bbfffa607f554195106c6a47` after PR #5.
- PR #6 was reported open as a draft at
  `15babb68b48bb4343d12478a86e0a95cbc8fb234`, with passing CI.
- The styled local app reportedly supports project creation, one
  authorized video upload, real file-signature validation, persistence
  across refresh, and an honest analysis blocked/error state.
- The test suite reportedly has 84 passing tests.
- A real GMI analysis has not been verified.
- The experimental GMI video request shape has not been verified.
- Real Backblaze B2 persistence has not been verified.
- No public deployment has been verified.
- No real face or voice generation has been verified; earlier rendered
  video output was a mockup.

If repository evidence contradicts any item, repository evidence wins and
Claude must update the ledger/state documents before continuing.

## Evidence-state vocabulary

Use only: `PLANNED`, `IN_PROGRESS`, `REVIEW_READY`, `APPROVED`, `MERGED`,
`DEPLOYED`, `LIVE_VERIFIED`, `COMPLETE`, or `BLOCKED`.

No block is complete merely because code exists. Every block has its own
proof gate.

## Master block ledger

### Phase 0 — Reconcile truth and unblock the first experiment

**CF-00 — Repository and state reconciliation**
Status: IN_PROGRESS until re-verified
Owner: Engineer; CTO reviews
Depends on: None
Objective: Establish one uncontested starting SHA and one truthful active
work packet.
Work: Fetch the repository and verify local `main` equals remote `main`;
verify PR #6 head, diff, CI, and mergeability; confirm there are no other
open PRs or dirty local changes that would be overwritten; verify the
reported 84-test baseline; verify the styled home and project pages
through a running server, never by opening raw template files; reconcile
`Founder Canon`, `Product Canon`, `Authority Matrix`, `Roadmap`, `Current
State`, `Decision Log`, and `Active Work Packet`.
Proof gate: Exact local/remote main SHA, open-PR table, terminal test
result, localhost acceptance, and contradiction scan.
Tonight: Execute immediately. If PR #6 is docs-only, accurate, green, and
already within granted merge authority, merge it; otherwise leave it open
and name the exact blocker. Do not let doc cleanup consume the whole
session.

**CF-01 — Credential readiness without secret exposure**
Status: BLOCKED if credentials are absent
Owner: Engineer; Founder supplies protected values
Depends on: CF-00
Objective: Make the existing real-analysis path executable without
committing or printing secrets.
Work: Validate `.env.example`, startup configuration, `/health`, and
provider-specific error messages; confirm the minimum credentials
actually required for one experiment; determine whether the provider can
receive uploaded bytes directly — if it can, B2 must not be made a
prerequisite merely because the current implementation assumes a URL; if
URL-based input is required, verify private B2 upload and time-limited
presigned fetch behavior; ensure logs, exception pages, tests,
screenshots, and receipts redact secrets and provider payloads.
Proof gate: A sanitized configuration report showing only
configured/unconfigured booleans; no secrets in Git history or logs;
exact founder setup steps if blocked.
Founder input: Only the missing credential values, entered locally — not
pasted into chat or committed.

**CF-02 — Provider capability and request-shape probe**
Status: PLANNED
Owner: Engineer; CTO reviews
Depends on: CF-01
Objective: Prove the selected provider/model can actually understand an
authorized video using the exact request format implemented.
Work: Re-verify current official provider documentation for model
capability, endpoint, limits, supported video inputs, pricing, retention,
and data-use terms; use one short authorized test video with a known
transcript and easily checked visual facts; run the smallest possible
real call; capture sanitized request metadata (model, endpoint class,
input mechanism, file duration/size, response status, latency,
token/usage fields, recorded cost if available); validate returned JSON
against the persisted Creator Profile contract; preserve the raw response
only in a protected local evidence location if necessary, never commit it
or include secrets.
Proof gate: The model correctly identifies at least the known spoken
topic, opening hook, basic tone, and visible format; the response parses
and persists; `REQUEST_SHAPE_VERIFIED` changes only after this real test.
Failure rule: If the provider cannot accept or understand the video after
two materially different documented request approaches, mark this block
`BLOCKED` and recommend a provider change. Do not keep guessing endpoints.

**CF-03 — First real end-to-end creator analysis**
Status: PLANNED
Owner: Engineer; CTO reviews; Founder judges usefulness
Depends on: CF-02
Objective: Prove the truthful product flow on one of the founder's dad's
authorized videos.
Work: Upload through the real browser UI with consent recorded; perform
the real provider call; persist the result; refresh and display the same
result; show summary, audience, tone, hooks, content patterns, visual
style, and recommendations using only real persisted fields; make
provider failure recoverable without losing the source.
Proof gate: Browser-recorded upload → real analysis → persistence →
refresh → display, tied to exact code SHA, with sanitized provider
evidence and actual cost.
Founder decision gate: Founder answers one question: "Is this analysis
accurate and useful enough to test on a small batch?" Recommended approval
threshold: no major factual invention and at least 4/5 usefulness.

### Phase 1 — Validate whether the intelligence is actually valuable

**CF-04 — Automatic evidence extraction pipeline**
Status: PLANNED
Depends on: CF-03 approved
Objective: Remove the manual busywork the founder rejected.
Work: Automatically derive video duration, technical metadata, transcript
with timestamps, representative frames/scene changes, on-screen text
where feasible, opening hook, CTA, content structure, visual format, and
source checksum; preserve the original authorized upload and derived
artifacts with provenance.
Proof gate: Five representative videos process without manual field
entry; every extracted claim links to transcript timestamps or frames
where applicable; retry and partial-failure states are visible.

**CF-05 — Small-batch creator profile**
Status: PLANNED
Depends on: CF-04
Objective: Learn stable patterns from a small representative set before
attempting "creator intelligence."
Work: Ingest 5-10 authorized examples selected for variety, not manually
labeled as winners; produce per-video analyses and one aggregate creator
profile that distinguishes repeated evidence from one-off behavior.
Proof gate: The aggregate profile cites supporting videos, avoids
unsupported claims, and remains materially stable when one video is
removed.

**CF-06 — Accuracy evaluation harness**
Status: PLANNED
Depends on: CF-05
Objective: Decide with evidence whether the model is accurate enough to
justify continued construction.
Work: Build a short founder/creator rubric covering factual accuracy,
style recognition, hook recognition, tone, actionable insight,
hallucination severity, and overall usefulness; blindly evaluate model
outputs where practical; record corrections without forcing the founder
to populate a large dataset.
Proof gate / kill gate: Continue only if the creator rates the output at
least 4/5 overall, no severe fabricated claims occur, and at least 80% of
checkable claims are correct across the batch. Otherwise improve the
prompt/provider once and repeat; after two failed rounds, stop and
reassess the product premise.

**CF-07 — Performance-metric import and hook correlation**
Status: PLANNED
Depends on: CF-06 passes
Objective: Learn what performs, not merely what appears stylistically
common.
Work: Prefer authorized API/export ingestion; if unavailable, accept a
simple CSV export with video identifier, publication date, views,
reach/impressions if available, watch time/retention if available, likes,
comments, shares, saves, and follower count/context; never ask the
founder to hand-type twenty records; normalize cautiously for age, reach,
and platform differences.
Proof gate: Metrics join deterministically to sources; missing metrics
are labeled; correlations are described as correlations, not causal
truths; at least one useful pattern survives a sensitivity check.

### Phase 2 — Turn intelligence into creation help

**CF-08 — Evidence-grounded idea generator**
Status: PLANNED
Depends on: CF-06; CF-07 optional enhancement
Objective: Generate new, non-duplicative content ideas aligned with the
creator's proven patterns.
Work: Generate ideas with rationale, target audience, hook type, format,
source evidence, novelty check, and confidence; allow thumbs-up/down and
short corrections.
Proof gate: Creator accepts at least 5 of 10 ideas as worth developing;
no idea is presented as proven to perform.

**CF-09 — Script studio**
Status: PLANNED
Depends on: CF-08
Objective: Produce editable scripts that sound recognizably aligned
without impersonating or copying past scripts.
Work: Hook variants, full script, shot beats, on-screen text, CTA
options, duration target, evidence references, and an explicit
creator-approval workflow; preserve revision history.
Proof gate: Creator approves at least 3 scripts with only light edits;
plagiarism/near-duplicate checks pass; the interface distinguishes AI
draft from creator-approved copy.

**CF-10 — Content workspace and feedback learning**
Status: PLANNED
Depends on: CF-09
Objective: Make the workflow repeatable without silently retraining on
mistakes.
Work: Idea → draft → reviewed → approved → produced lifecycle; searchable
library; comments; structured rejection reasons; versioning; provenance;
feedback summaries; creator corrections may influence future generation
only through explicit, reversible profile updates.
Proof gate: A creator can complete three idea-to-approved-script cycles
and recover prior versions.

### Phase 3 — Create media safely

**CF-11 — Production-assist package**
Status: PLANNED
Depends on: CF-09
Objective: Deliver useful production assets before introducing synthetic
identity risk.
Work: Shot list, B-roll suggestions, captions, title/caption variants,
thumbnail concepts, edit decision list, and export package; no generated
face or voice.
Proof gate: One approved script becomes a usable creator production
package and is exported correctly.

**CF-12 — Authorized voice evaluation**
Status: PLANNED
Depends on: CF-11 and explicit creator consent
Objective: Evaluate whether authorized synthetic voice adds enough value
to justify its risk and cost.
Work: Verify identity and scoped consent; document provider
retention/deletion terms; create revocation and deletion controls;
generate a clearly labeled private sample; require creator review before
every release.
Proof gate: Creator explicitly approves quality and use; consent,
revocation, provenance, disclosure, and deletion are live-verified.
Otherwise reject voice cloning and retain normal voiceover workflows.

**CF-13 — Authorized avatar/face evaluation**
Status: PLANNED
Depends on: CF-12 or independent explicit approval; CF-11
Objective: Test authorized avatar video without deception.
Work: Verified consent, private generation, visible provenance/
disclosure, review gate, watermark/label where appropriate, misuse
controls, deletion, and provider safety review.
Proof gate: One playable private output is reviewed and approved by the
creator; no publishing automation; no claim of authentic footage.

**CF-14 — Rendered content assembly**
Status: PLANNED
Depends on: CF-11 and whichever of CF-12/13 are approved
Objective: Assemble approved assets into a playable draft with traceable
inputs.
Work: Render queue, status, retry, cost estimate/record, asset
provenance, captions, audio mix, preview, download, deletion, and creator
sign-off.
Proof gate: One authorized script produces a playable, correctly labeled
output that survives refresh and download. Mockups do not count.

### Phase 4 — Convert the proven workflow into a product

**CF-15 — Multi-creator isolation and consent lifecycle**
Status: PLANNED
Depends on: CF-10; media blocks only if retained
Objective: Safely support more than one creator.
Work: Authentication, organizations/workspaces, strict tenant isolation,
consent scope, audit log, export, account deletion, retention controls,
encrypted secrets, rate limits, backup/restore, and abuse reporting.
Proof gate: Cross-tenant access tests fail safely; consent can be
revoked; data export/deletion are live-tested; security review approves
exact SHA.

**CF-16 — Reliability, observability, and cost controls**
Status: PLANNED
Depends on: CF-15
Objective: Make failures supportable and unit economics measurable.
Work: Job queue, idempotency, timeouts, retry policy, monitoring,
alerting, provider fallbacks where justified, per-job costs, budget caps,
data retention, backups, restore drill, and incident runbook.
Proof gate: Failure injection, restore drill, cost ceiling enforcement,
and operator runbook pass.

**CF-17 — Private alpha deployment**
Status: PLANNED
Depends on: CF-15 and CF-16; Founder deployment approval
Objective: Run the proven workflow for the founder's dad and a tiny
number of invited authorized creators.
Work: Production hosting, domain/TLS, secrets, database/object storage,
privacy/terms drafts reviewed as needed, monitoring, rollback, support
channel, feedback capture.
Proof gate: Deployment tied to main SHA; CI green; R1/R2 exact-SHA
approvals; live acceptance through the real flow; rollback tested; no
unapproved public signup.

**CF-18 — Product/value validation**
Status: PLANNED
Depends on: CF-17
Objective: Determine whether creators repeatedly use and value the
workflow.
Work: Measure time-to-first-useful-output, analysis usefulness, idea
acceptance, script approval, weekly repeat use, cost per useful output,
failure rate, and founder support burden. No vanity-metric substitution.
Proof gate: Define before testing. Suggested threshold: 5 authorized
alpha users, 4 complete two weekly cycles, median usefulness ≥4/5, and
unit cost compatible with a credible gross margin.

**CF-19 — Offer, pricing, and billing design**
Status: PLANNED
Depends on: CF-18 passes; Founder pricing/spend approval
Objective: Create an honest offer based on measured value and cost.
Work: Segmentation, packaging, usage limits, contribution-margin model,
refunds, billing failure states, tax/legal review requirements, and
customer-facing claims limited to proven capabilities.
Proof gate: Conservative path to durable profit; billing sandbox passes;
Founder approves pricing and public claims. Do not activate paid billing
yet.

**CF-20 — Controlled paid beta**
Status: PLANNED
Depends on: CF-19; Founder launch approval
Objective: Test whether real customers pay, retain, and receive value.
Work: Limited onboarding, billing activation, support, analytics,
cancellation, refunds, abuse handling, weekly economics review, and
acquisition experiments within an approved budget.
Proof gate: Paying users complete the real workflow; refunds/support/
costs are tracked; contribution margin and repeat use meet predeclared
thresholds.

**CF-21 — Publishing integrations**
Status: PLANNED / optional
Depends on: CF-20 plus separate platform/legal review
Objective: Reduce approved publishing friction without removing human
control.
Work: OAuth, least privilege, draft scheduling, disclosure metadata,
audit log, revocation, rate limits, and explicit final confirmation;
start with export/download if API access adds disproportionate risk.
Proof gate: Sandbox or private account publishing test; correct
disclosure; revocation and failure recovery; Founder approval before any
public post.

**CF-22 — Scale toward durable $10K monthly net profit**
Status: PLANNED
Depends on: CF-20 proves repeatable positive economics
Objective: Scale only behavior that is useful, repeatable, and
profitable.
Work: Improve activation, retention, margins, acquisition, support
automation, referral/content loops, capacity planning, provider
negotiation, and churn reduction. Track net business profit, not revenue
alone.
Proof gate: At least $10,000 monthly net business profit before personal
taxes for three consecutive months, with a credible durable path and no
safety/quality degradation.

## Tonight's execution order for Claude

Claude must work only in this order:

1. CF-00: Verify/reconcile GitHub truth and prevent stale documentation.
2. CF-01: Make configuration readiness exact and safe.
3. CF-02: If credentials already exist, run the smallest real provider
   capability probe.
4. CF-03: If CF-02 passes and an authorized video is available, run the
   first real end-to-end analysis.
5. CF-04 preparation only: If external execution is blocked, improve only
   the independent extraction scaffolding/tests that are directly useful
   for a five-video validation and do not require a premature
   architecture rewrite.
6. Stop when a real founder-only input is required. Do not begin CF-05 or
   any later phase tonight unless the founder explicitly approves the
   CF-03 usefulness gate.

## Safe independent work allowed tonight

- Repository reconciliation and truthful documentation.
- Tests, security scans, error handling, redaction, configuration
  validation, and local acceptance.
- Provider documentation verification and a cost estimate.
- A protected evidence schema and sanitized experiment receipt.
- Automated transcript/frame/metadata extraction exploration in an
  isolated branch, provided no paid API call or heavy new dependency is
  committed without justification.
- Drafting the five-video evaluation rubric and import format.

## Prohibited tonight

- Voice cloning, face/avatar generation, publishing, billing, public
  deployment, public launch, multi-tenant auth, marketing pages, fake
  analytics, fake results, or broad dashboard work.
- Manual collection of twenty top videos or manual population of large
  metadata tables.
- Spending beyond the existing $50 ceiling or accepting a paid plan.
- Merging new runtime work without exact-SHA R1 and R2 approvals and
  granted merge authority.
- Treating local server output as public deployment.

## Founder decision checkpoints

The founder should be interrupted only at these checkpoints:

1. Enter missing credentials and supply/select one authorized video.
2. Judge whether the first real analysis is useful enough to run a 5-10
   video validation.
3. Approve continued investment after the accuracy kill gate.
4. Approve verified creator voice/face consent experiments.
5. Approve deployment, pricing, spend, or public launch.

Everything else is team execution and evidence gathering.
