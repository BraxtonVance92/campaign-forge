# CampaignForge Decision Log

Only founder-approved decisions are binding. `PROPOSED` entries are recommendations awaiting approval.

| ID | Date | Status | Decision | Reason / consequence |
|---|---|---|---|---|
| D-001 | 2026-07-21 | APPROVED-HISTORICAL | CampaignForge focuses on an AI content studio that learns from authorized creator videos/carousels. | Preserves the founder's chosen product direction. |
| D-002 | 2026-07-21 | APPROVED-HISTORICAL | Spending ceiling is $50 unless the founder changes it. | Cost estimates and actual recorded charges remain separate. |
| D-003 | 2026-07-21 | APPROVED-HISTORICAL | GPT is controller/CTO; Claude Code is maker; founder is final product authority. | Separates implementation from review and prevents unsupported completion claims. |
| D-004 | 2026-07-21 | PROPOSED | Contest MVP golden path is authorized example -> initial fingerprint -> new idea -> branded generated asset -> B2 persistence/restore with Genblaze provenance. | Covers the creator problem and all four contest criteria in one visible flow. |
| D-005 | 2026-07-21 | PROPOSED | Face and voice cloning are excluded from the contest MVP. | Consent, quality, schedule, and deception risks outweigh contest value. |
| D-006 | 2026-07-21 | PROPOSED | Use Python/FastAPI for the Genblaze service and a React/Next.js web UI, based on current official samples. | Minimizes integration risk with the Python SDK while providing a polished web journey. |
| D-007 | 2026-07-21 | PROPOSED | Use GMI Cloud through the Genblaze adapter for image/video generation; select exact models only after live capability/cost tests. | GMI is contest-supported and one key is reportedly available, but current access and model behavior are not verified. |
| D-008 | 2026-07-21 | PROPOSED | Feature freeze July 31; target submission August 2, one day before deadline. | Preserves final-day buffer. |
| D-009 | 2026-07-21 | PROPOSED | Pricing, billing, publishing, teams, analytics scraping, and multi-model fan-out are post-contest. | Keeps the submission complete and reliable. |

## Superseded or corrected claims

- "Daily spending report scheduled" is not verified and must not be repeated as completed.
- "GMI key connected" and "B2 upload works" are reported historical user tests, not repository-verified current capabilities.
- A mock video is not real generation.
- No agent works after a chat turn ends unless an explicit automation exists and is verified.

## Founder approval record

When the founder approves a proposed decision, change its status to `APPROVED`, add the approval date/context, and record any correction as a new row. Never overwrite history silently.
