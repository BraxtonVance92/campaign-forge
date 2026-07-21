# CampaignForge Founder Canon

Status: binding founder intent. Corrected 2026-07-21 following a binding founder correction that supersedes the original no-face/no-voice draft (see `docs/ops/DECISION_LOG.md` D-010, D-011).

## Mission

CampaignForge is an AI content studio that learns from a creator's authorized videos, face, voice, delivery, visual appearance, and content style, then helps that creator produce new playable videos featuring an authorized representation of themselves. Authorized creator replication for content production is the core product — not an optional, deferred, or contest-only feature. The Backblaze Generative Media Hackathon is an opportunity to accelerate and showcase the real product; contest scoring optimization may not remove or replace the core product. The founder intends to build a real, standalone SaaS business; the contest submission is a milestone toward that goal, not the goal itself.

## Founder authority and constraints

- Braxton Vance is founder and final authority over product strategy, budget, public claims, launch, pricing, and production deployment.
- GPT acts as controller/CTO. Claude Code is the maker. No agent may silently add or remove product scope, including face or voice generation.
- Technical implementation details (providers, models, architecture, sequencing) may be narrowed or resequenced by the controller to fit schedule, cost, or evidence. The core customer outcome — authorized creator replication into a new playable video — may not be replaced with a lesser substitute (for example, a generic branded image generator) without explicit founder approval.
- The project spending ceiling is USD $50 unless the founder explicitly changes it. Estimates and actual recorded spend must be shown separately. No tool may invent billing totals.
- Speed matters, but evidence matters more. A prototype, simulated workflow, or planned integration may never be described as working product.
- The contest submission deadline is August 3, 2026 at 5:00 p.m. Eastern. The plan must protect a submission-ready build before optional polish, but schedule pressure may not be used to silently cut face or voice generation from scope.

## Product belief

Creators do not mainly need another generic prompt box. They need a reusable, consent-based memory of what makes their content theirs — their face, voice, delivery, tone, visual patterns, structure, and boundaries — used to produce new videos that are recognizably and authentically theirs. CampaignForge should make that memory visible and editable, then use it to generate a traceable, playable video output.

## Focused customer

The first customer is a serious solo creator, coach, educator, or small creator-led brand who wants to produce more on-brand video content without re-recording themselves for every idea. Colton/The WGR is the authorized design partner and demo case only if written permission covers every uploaded asset, the use of his face and voice specifically, and public demo use.

The product is not initially for agencies managing hundreds of clients, fully autonomous publishing, cloning any person without that person's own verified authorization, or general-purpose media generation unrelated to an authorized creator's own likeness.

## Winning submission promise

The demo must prove one complete, truthful loop:

> Upload authorized creator reference material and consent -> analyze it into an editable creator profile (style, voice, appearance) -> enter a new content idea and script -> generate an authorized cloned voice -> generate an authorized face/avatar video -> render one playable video -> persist source, profile, script, voice, video, metadata, and provenance in Backblaze B2 -> restore and play the result.

The initial implementation targets one authorized creator and one complete real workflow end to end, rather than a broad multi-creator system. This is a narrowing of scope to fit the schedule, not a removal of face or voice generation.

## Experience principles

- One obvious next action per screen.
- Show progress as real pipeline stages, never decorative fake activity.
- Let users inspect and edit the creator profile before generation.
- Explain why an output matches the creator, using evidence from authorized examples.
- Preserve every run in a simple project library with status, cost estimate, output, and lineage.
- Fail honestly and recoverably. A failed model call must retain the project and offer retry.
- The judge path must require no payment and ideally no login; if login is required, provide a test account and instructions.

## Trust, consent, and safety

- Users must attest that they own or are authorized to use uploaded media, including their own face and voice.
- Founder consent (authorizing the CampaignForge project) and creator/subject consent (authorizing use of a specific person's likeness or voice) are different things. The person whose face or voice is used must provide their own verified, specific consent before that material is used for analysis, cloning, or generation — the founder's authorization for the project does not itself authorize using any individual's likeness.
- Public demo content requires documented permission from every recognizable person and rights holder, covering the specific use shown in the demo.
- Face and voice generation are core product scope, not deferred features. They may only be built and used once verified consent, disclosure, revocation, and deletion controls exist for the specific creator whose likeness is used.
- Never enable impersonation, deceptive media, hidden AI use where disclosure is required, cloning of a person without that person's own verified authorization, copyrighted uploads without authorization, or generated claims presented as facts.
- Secrets remain server-side and never enter code, logs, screenshots, prompts, tests, receipts, or client bundles.
- Uploaded originals are private by default. Asset access must use controlled URLs or an explicitly approved public demo bucket.

## Contest facts that bind scope

The Backblaze Generative Media Hackathon requires a working generative media application using both Backblaze B2 and Genblaze, a judge-accessible app, repository with source and setup instructions, provider/model list, explanation of B2 and Genblaze usage, and a public demo video under three minutes. Existing projects must explain significant B2 and Genblaze additions made during the submission period.

Judging first applies a viability pass/fail, then equally weights:

1. Real-world utility.
2. Production readiness.
3. B2 storage and data orchestration.
4. Meaningful Genblaze use.

Tie-breaking begins with real-world utility. Therefore CampaignForge must lead with the creator problem, not infrastructure, while making B2 and Genblaze visibly load-bearing.

Authoritative contest sources:

- https://backblaze-generative-media.devpost.com/
- https://backblaze-generative-media.devpost.com/rules

## Non-goals before the initial release

- Automated social publishing, analytics scraping, billing, team workspaces, mobile apps, marketplaces, and large-scale multi-tenant administration.
- Cloning any person's face or voice without that specific person's own verified, recorded consent — this applies to every creator, including the founder's first authorized design partner.
- Supporting more than one authorized creator in the initial implementation.
- Model fan-out merely to look sophisticated. Each model step must improve the user outcome or reliability.

## Business direction after the contest

The commercial wedge is authorized creator replication — a durable, consent-based profile of a creator's face, voice, and style used to produce new videos — not a generic AI generator. The likely value metric is active authorized creator profiles and monthly generation allowance. Pricing is unapproved until customer evidence exists. A working hypothesis is a free proof experience, a solo tier, and a higher creator-team tier; this is a hypothesis, not a commitment.

The defensible asset is the structured, consent-based creator profile (face, voice, style), feedback history, and provenance graph. Durable value depends on better consistency, authenticity, and faster approval over repeated use, not access to the same public models competitors can call.

## Success definitions

Contest success means an eligible, on-time submission with a live flow that behaves exactly as shown, a clear three-minute story, complete README, real Genblaze orchestration, meaningful B2 persistence, and no unsupported claim — demonstrating real progress toward the authorized creator replication product, not a substitute product built solely to score contest points.

Product success means authorized creators repeatedly use CampaignForge to produce approved videos featuring their own likeness faster than their old production workflow, and are willing to pay more than the marginal model/storage/support cost.

Winning cannot be guaranteed. The team must optimize for the published criteria and produce evidence, not claim certainty.
