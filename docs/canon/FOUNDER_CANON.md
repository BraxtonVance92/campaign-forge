# CampaignForge Founder Canon

Status: binding founder intent, drafted for founder review on 2026-07-21.

## Mission

CampaignForge is an AI content studio that learns from a creator's authorized examples and turns a new idea into on-brand, editable social media. The immediate goal is a truthful, working submission to the Backblaze Generative Media Hackathon. The durable goal is a focused SaaS that helps creators and lean content teams produce more consistent content without repeatedly rebuilding their voice, visual direction, and workflow from scratch.

## Founder authority and constraints

- Braxton Vance is founder and final authority over product strategy, budget, public claims, launch, pricing, and production deployment.
- GPT acts as controller/CTO. Claude Code is the maker. No agent may silently add product scope.
- The project spending ceiling is USD $50 unless the founder explicitly changes it. Estimates and actual recorded spend must be shown separately. No tool may invent billing totals.
- Speed matters, but evidence matters more. A prototype, simulated workflow, or planned integration may never be described as working product.
- The contest submission deadline is August 3, 2026 at 5:00 p.m. Eastern. The plan must protect a submission-ready build before optional polish.

## Product belief

Creators do not mainly need another generic prompt box. They need a reusable, consent-based memory of what makes their content theirs: audience, promises, topics, hooks, structure, tone, visual patterns, calls to action, and boundaries. CampaignForge should make that memory visible and editable, then use it to generate traceable media.

## Focused customer

The first customer is a serious solo creator, coach, educator, or small creator-led brand that already has useful content but struggles to convert past examples into a repeatable production system. Colton/The WGR is the authorized design partner and demo case only if written permission covers every uploaded asset and public demo use.

The product is not initially for agencies managing hundreds of clients, fully autonomous publishing, celebrity cloning, or general-purpose media generation.

## Winning submission promise

The demo must prove one complete, truthful loop:

> Upload an authorized creator example -> analyze it into an editable creator fingerprint -> enter a new content idea -> generate one on-brand media asset through Genblaze -> persist source, fingerprint, output, metadata, and provenance in Backblaze B2 -> restore and display the result.

The first shippable generation may be a branded vertical visual or short motion clip. It must not depend on cloning a person's face or voice.

## Experience principles

- One obvious next action per screen.
- Show progress as real pipeline stages, never decorative fake activity.
- Let users inspect and edit the creator fingerprint before generation.
- Explain why an output matches the creator, using evidence from authorized examples.
- Preserve every run in a simple project library with status, cost estimate, output, and lineage.
- Fail honestly and recoverably. A failed model call must retain the project and offer retry.
- The judge path must require no payment and ideally no login; if login is required, provide a test account and instructions.

## Trust, consent, and safety

- Users must attest that they own or are authorized to use uploaded media.
- Public demo content requires documented permission from every recognizable person and rights holder.
- Face or voice cloning is outside the contest MVP. It may only enter a later roadmap after verified consent, disclosure, revocation, and deletion controls exist.
- Never enable impersonation, deceptive media, hidden AI use where disclosure is required, copyrighted uploads without authorization, or generated claims presented as facts.
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

## Non-goals before submission

- Automated social publishing, analytics scraping, billing, team workspaces, mobile apps, marketplaces, and large-scale multi-tenant administration.
- Indistinguishable avatar or voice generation.
- Ten-example onboarding as a requirement. The judge flow starts with one example; multiple examples may be supported only after the one-example flow works.
- Model fan-out merely to look sophisticated. Each model step must improve the user outcome or reliability.

## Business direction after the contest

The commercial wedge is a creator memory plus production workspace, not a generic AI generator. The likely value metric is active creator profiles and monthly generation allowance. Pricing is unapproved until customer evidence exists. A working hypothesis is a free proof experience, a solo tier, and a higher creator-team tier; this is a hypothesis, not a commitment.

The defensible asset is the structured, consent-based creator fingerprint, feedback history, and provenance graph. Durable value depends on better consistency and faster approval over repeated use, not access to the same public models competitors can call.

## Success definitions

Contest success means an eligible, on-time submission with a live flow that behaves exactly as shown, a clear three-minute story, complete README, real Genblaze orchestration, meaningful B2 persistence, and no unsupported claim.

Product success means authorized creators repeatedly use CampaignForge to reach approved content faster than their old workflow and are willing to pay more than the marginal model/storage/support cost.

Winning cannot be guaranteed. The team must optimize for the published criteria and produce evidence, not claim certainty.
