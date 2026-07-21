# CampaignForge Decision Log

Only founder-approved decisions are binding. `PROPOSED` entries are recommendations awaiting approval. Every entry records status, date, authority, rationale, and supersession links where applicable. Never overwrite history silently — corrections are recorded as new rows.

| ID | Date | Status | Decision | Reason / consequence | Authority | Supersedes / Superseded by |
|---|---|---|---|---|---|---|
| D-001 | 2026-07-21 | APPROVED-HISTORICAL | CampaignForge focuses on an AI content studio that learns from authorized creator videos/carousels. | Preserves the founder's chosen product direction. | Founder | — |
| D-002 | 2026-07-21 | APPROVED-HISTORICAL | Spending ceiling is $50 unless the founder changes it. | Cost estimates and actual recorded charges remain separate. | Founder | — |
| D-003 | 2026-07-21 | APPROVED-HISTORICAL | GPT is controller/CTO; Claude Code is maker; founder is final product authority. | Separates implementation from review and prevents unsupported completion claims. | Founder | — |
| D-004 | 2026-07-21 | SUPERSEDED by D-010 | Contest MVP golden path is authorized example -> initial fingerprint -> new idea -> branded generated asset -> B2 persistence/restore with Genblaze provenance. | Covered the creator problem and contest criteria without face/voice generation. | Founder (original; since corrected) | Superseded by D-010 |
| D-005 | 2026-07-21 | REJECTED, SUPERSEDED by D-011 | Face and voice cloning are excluded from the contest MVP. | Consent, quality, schedule, and deception risks were judged to outweigh contest value; the founder subsequently rejected this judgment as incorrect. | Founder (original; since rejected by the same founder) | Superseded by D-011 |
| D-006 | 2026-07-21 | PROPOSED | Use Python/FastAPI for the Genblaze service and a React/Next.js web UI, based on current official samples. | Minimizes integration risk with the Python SDK while providing a polished web journey. Technical stack choice, delegated to controller; not yet founder-approved as binding. | Controller/CTO (recommendation) | — |
| D-007 | 2026-07-21 | PROPOSED | Use GMI Cloud through the Genblaze adapter for image/video generation; select exact models only after live capability/cost tests. | GMI is contest-supported and one key is reportedly available, but current access, model behavior, and whether it supports voice cloning or face/avatar generation are not verified. See Phase 0.5 in `docs/roadmap/CURRENT_ROADMAP.md`. | Controller/CTO (recommendation) | — |
| D-008 | 2026-07-21 | PROPOSED | Feature freeze July 31; target submission August 2, one day before deadline. | Preserves final-day buffer. Schedule guidance only; does not authorize cutting face or voice generation to hit the date. | Controller/CTO (recommendation) | — |
| D-009 | 2026-07-21 | PROPOSED | Pricing, billing, publishing, teams, analytics scraping, and multi-model fan-out are post-contest. | Keeps the submission complete and reliable. This list explicitly excludes face and voice generation, which are core and not deferred (see D-011). | Controller/CTO (recommendation) | Clarified by D-011 |
| D-010 | 2026-07-21 | APPROVED | CampaignForge's target end-to-end flow is: one authorized creator -> authorized reference inputs and consent -> real creator analysis -> editable creator profile -> idea and script -> cloned voice -> face/avatar generation -> playable final video -> B2 persistence and restoration with provenance. | Founder correction: authorized creator replication (face and voice) is the core product, not a generic branded-asset generator. The initial implementation narrows to one authorized creator to fit schedule, without removing face or voice generation. | Founder | Supersedes D-004 |
| D-011 | 2026-07-21 | APPROVED | The earlier proposal excluding face and voice cloning (D-005) is REJECTED and SUPERSEDED. Authorized face-and-voice generation is the core product. Verified, person-specific creator consent is mandatory before analysis, cloning, or generation involving that person. The narrow first version supports one authorized creator rather than removing the capability. | Delivered directly by the founder as a binding correction. Consent remains a non-negotiable safety control, distinct from the founder's own project-level authorization. | Founder | Supersedes D-005 |
| D-012 | 2026-07-21 | APPROVED | PR #1 (the CF-BOOT-001 docs-only bootstrap pack, including the D-010/D-011 correction) is approved as-is at exact SHA `9ae223920b0f71aed1831070a5ba9f4924683aec` and merged into `main` at merge commit `3e06fc2e076f09c7b077d3f5e803583cd0ada5e4`. | Founder review confirmed the corrected canon is coherent; this is the first release/merge to `main`, which required founder approval per `docs/ops/AUTHORITY_MATRIX.md`. | Founder | — |
| D-013 | 2026-07-21 | APPROVED | `CF-VERIFY-001` (live provider capability verification) is dispatched as the next active work packet, narrower than full runtime implementation, gated behind founder resolution of the provider-split, new-paid-service, ceiling-scope, and GMI-key items listed in `docs/ops/ACTIVE_WORK_PACKET.md`. | Founder directed this as the next action after merge, per the CF-VERIFY-001 research dossier's identified unknowns. | Founder | — |

## Superseded or corrected claims

- "Daily spending report scheduled" is not verified and must not be repeated as completed.
- "GMI key connected" and "B2 upload works" are reported historical user tests, not repository-verified current capabilities.
- A mock video is not real generation.
- No agent works after a chat turn ends unless an explicit automation exists and is verified.
- The D-005 decision to exclude face and voice cloning is corrected: authorized face-and-voice video generation is core, undeferred product scope, subject to verified per-person consent (see D-010, D-011). Any document or statement implying face/voice is optional, contest-only, or removed is stale and must be corrected on sight.

## Founder approval record

When the founder approves a proposed decision, change its status to `APPROVED`, add the approval date/context, and record any correction as a new row. Never overwrite history silently.

- 2026-07-21: Founder Braxton Vance issued a binding correction rejecting D-005 and approving D-010/D-011, delivered directly in the maker session and recorded here per the standing instruction to record founder rulings durably.
