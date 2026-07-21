# CampaignForge Current Roadmap

Date: 2026-07-21. Contest deadline: 2026-08-03 17:00 ET. Corrected 2026-07-21 to reflect the founder's binding product correction (`docs/ops/DECISION_LOG.md` D-010, D-011): authorized face-and-voice video generation is core product scope, not deferred.

## Priority rule

Protect a complete, testable, truthful phase before moving to the next. Each phase must end in durable evidence. Schedule pressure may narrow scope (for example, one authorized creator instead of many) but may not silently remove face or voice generation.

## Phase 0 — Bootstrap and evidence

- Customer-visible result: none yet; this phase produces a coherent, truthful basis for implementation.
- Prerequisites: founder-approved canon; repository access.
- Acceptance evidence: coherent canon/authority/roadmap/state files; repository baseline confirmed; CI baseline; secret-handling approach documented; provider capability spike plan; cost/latency measurement plan.
- Principal risks: canon drift, unverified claims treated as fact, scope silently narrowed.
- Estimated external cost: $0 (documentation and read-only research only).
- Authority boundary: Claude may inspect, document, and open draft PRs; founder approves canon corrections; no runtime, deployment, or spend.
- Next dependent phase: Phase 0.5.
- State: `IN_PROGRESS`.

## Phase 0.5 — Provider capability and architecture verification (proposed, next dependent block)

This phase must run before broad runtime implementation. It answers, with cited evidence rather than assumption:

- Which currently available provider can create an authorized persistent or reusable creator face/avatar? Unknown — verification required.
- Which provider can create an authorized cloned voice? Unknown — verification required.
- Does GMI Cloud/Genblaze directly support these capabilities, or will it orchestrate models/services that do? Unknown — verification required.
- What input formats, sample lengths, consent mechanisms, output formats, latency, and costs apply? Unknown — verification required.
- What assets and provenance records belong in B2? Answerable in outline from `docs/canon/PRODUCT_CANON.md`'s B2 object layout; must be confirmed against the chosen providers' actual output shapes.
- What is the narrowest deployable architecture supported by Render? Unknown — verification required. Render has repository access but no service has been created.
- Which pieces can be implemented within the founder's $50 ceiling? Unknown — verification required; depends on the provider costs above.
- What disclosure or watermarking requirements apply? Unknown — verification required against current platform and legal guidance.

Do not answer these with guesses. The verification packet must cite current official provider/API documentation and, where safe and low-cost, live capability tests.

- Customer-visible result: none; this is an internal evidence-gathering phase.
- Prerequisites: Phase 0 canon coherent and approved.
- Acceptance evidence: a written verification receipt answering each question above, either with a cited source or "Unknown — verification required" if still unanswered.
- Principal risks: guessing provider capability instead of testing it; underestimating cost or latency for voice/face generation.
- Estimated external cost: Unknown — should be near $0 if verification uses free-tier or documentation-only checks; any paid capability test requires a confirmed cost estimate first.
- Authority boundary: no runtime implementation packet may be written until this phase's findings exist.
- Next dependent phase: Phase 1.
- State: `PLANNED`.

## Phase 1 — Truthful analysis pilot

- Customer-visible result: upload one authorized creator example and see a real, persisted analysis result.
- Prerequisites: Phase 0.5 findings on the analysis provider; runtime foundation (web/API app, CI, env contract, health checks, no secrets in repo).
- Acceptance evidence: API/browser end-to-end proof of upload -> real analysis -> persist -> restore/display; B2 object evidence.
- Principal risks: treating a fixture or canned response as real analysis; missing consent capture.
- Estimated external cost: low (a single small analysis call); exact figure pending Phase 0.5.
- Authority boundary: Claude implements within an approved runtime packet; no production deploy or spend beyond the packet's approved estimate.
- Next dependent phase: Phase 2.
- State: `PLANNED`.

## Phase 2 — Consent and creator profile

- Customer-visible result: creator completes a specific consent attestation (covering analysis, voice cloning, and face/avatar generation) and can view/edit their profile.
- Prerequisites: Phase 1 persistence layer.
- Acceptance evidence: consent record persisted and linked to creator identity and permitted uses; editable profile UI; revocation/deletion path documented.
- Principal risks: conflating founder authorization with subject consent; missing a revocation path.
- Estimated external cost: near $0 (no new provider calls).
- Authority boundary: no runtime change to production data handling without controller review of the consent design.
- Next dependent phase: Phase 3.
- State: `PLANNED`.

## Phase 3 — Script and voice

- Customer-visible result: creator gets a generated script and hears real cloned-voice audio of themselves reading it.
- Prerequisites: Phase 0.5 voice-provider selection; Phase 2 consent record covering voice use.
- Acceptance evidence: a real generated script; real persisted, playable cloned-voice audio; provider/model/input/timing/cost/output lineage recorded.
- Principal risks: using a generic text-to-speech voice and mislabeling it as a clone of the creator; missing cost guardrails.
- Estimated external cost: Unknown — verification required (depends on the selected voice provider's pricing).
- Authority boundary: real paid voice-generation calls require a confirmed cost estimate and, if exceeding remaining budget headroom, founder approval.
- Next dependent phase: Phase 4.
- State: `PLANNED`.

## Phase 4 — Face/avatar video

- Customer-visible result: creator gets a real, playable video of an authorized avatar of themselves speaking the generated script in their cloned voice.
- Prerequisites: Phase 0.5 face/avatar-provider selection; Phase 2 consent record covering face/avatar use; Phase 3 voice asset.
- Acceptance evidence: real face/avatar video generated and combined with voice; persisted and restorable through B2; truthful queued/running/succeeded/failed/retry states.
- Principal risks: this is the highest-risk phase for cost, latency, and consent; must not proceed without a specific, recorded consent covering face/avatar generation.
- Estimated external cost: Unknown — verification required (likely the largest single cost item; must be checked against the $50 ceiling before any paid run).
- Authority boundary: founder approval required before any paid face/avatar generation call whose estimated cost, combined with prior spend, could approach the $50 ceiling.
- Next dependent phase: Phase 5.
- State: `PLANNED`.

## Phase 5 — End-to-end contest flow

- Customer-visible result: a judge can execute the complete real journey — authorized upload, consent, analysis, profile, script, voice, face/avatar video, B2 persistence, restore/playback — free of charge.
- Prerequisites: Phases 1-4 complete and stable.
- Acceptance evidence: meaningful B2 orchestration; meaningful Genblaze/GMI use where verified; provenance manifest; judge-ready demo; failure recovery; deployment verification tied to an exact SHA.
- Principal risks: schedule compression tempting a silent scope cut back to a face/voice-free output — not permitted per the founder correction.
- Estimated external cost: sum of Phases 1-4 estimates, to be reconciled against actual recorded spend.
- Authority boundary: production deployment and contest submission remain founder-approval actions per `docs/ops/AUTHORITY_MATRIX.md`.
- Next dependent phase: Phase 6 (post-contest).
- State: `PLANNED`.

## Phase 6 — Public SaaS launch foundation

- Customer-visible result: a durable, multi-tenant product ready for paying authorized creators.
- Prerequisites: Phase 5 complete and live-verified.
- Acceptance evidence: authentication; tenant isolation; usage budgets; rate limits; observability; privacy policy and terms; consent management and revocation/deletion; pricing and billing only after founder approval; public release readiness review.
- Principal risks: launching before consent/deletion controls and unit economics are proven.
- Estimated external cost: Unknown — verification required; depends on hosting, provider, and support costs at scale.
- Authority boundary: pricing, billing activation, and public launch are founder-approval actions.
- Next dependent phase: none defined yet; founder-directed.
- State: `PLANNED`.

## Target calendar

Schedule guidance, not a redefinition of product scope. Dates are estimates and may shift if Phase 0.5 verification reveals longer lead times for voice/face providers.

- July 21: approve corrected canon; begin Phase 0.5 provider verification.
- July 22-24: Phase 0.5 verification plus Phase 1 foundation and truthful analysis pilot.
- July 25-27: Phase 2 consent/profile and Phase 3 script/voice.
- July 28-29: Phase 4 face/avatar video — the highest-risk phase; may require schedule reallocation if provider lead times are long.
- July 30: Phase 5 reliability, judge path, cost controls.
- July 31: feature freeze; record demo and complete submission draft using whatever real phases are stable.
- August 1: independent R1/R2, repair, final deployment.
- August 2: live dry run and submit one day early.
- August 3: emergency buffer only.

If Phase 4 cannot be completed truthfully by the freeze date, the submission must show the real state actually reached (for example, real voice cloning with face/avatar generation in progress) rather than fabricate a face/voice result or silently revert to a generic image-only product.

## Contest score strategy

### Real-world utility

Demonstrate that the creator profile (face, voice, style) changes the generated script/voice/video and lets a creator produce a new video of themselves without re-recording. Show the authorized reference, extracted profile, editable correction, generated voice, generated face/avatar video, and final playable result.

### Production readiness

Show consent capture and revocation, file validation, real states, persisted restore, failure/retry, idempotency, a tested deployment, setup documentation, and judge-friendly access.

### B2 storage and orchestration

Make B2 visible as the durable project memory: source, consent, profile versions, script, voice asset, face/avatar video, final render, and manifest. Demonstrate refresh/restore and lineage, not just a hidden upload.

### Genblaze use

Use Genblaze for at least a multi-step pipeline (script/reference -> voice -> face/avatar video) with real events, provider adapter(s), B2 sink, canonical manifest, and lineage, per the Phase 0.5 findings on what Genblaze directly supports versus orchestrates.

## Cut line

Required: Phases 0-5 for one authorized creator, judge-ready essentials, README/video/submission, live deployment.

Cut first for schedule reasons, in order, before ever cutting face or voice: supporting more than one authorized creator, social publishing, analytics dashboards, teams, billing, multiple model fan-out, fancy editing, and more than one output format. Face and voice generation are not on this cut list.

## Post-contest roadmap

1. Interview/test with 5-10 authorized creators and compare generic versus authorized-replication outputs.
2. Add multi-creator support, multi-example learning, feedback-driven profile versions, and project deletion.
3. Add collaboration/approval and export workflows.
4. Validate pricing and unit economics before billing implementation.
5. Add publishing integrations only after content approval and retention are proven.
