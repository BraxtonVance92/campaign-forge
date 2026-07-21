# CampaignForge Product Canon

Status: the product outcome below is founder-directed and binding (`docs/ops/DECISION_LOG.md` D-010, D-011). Specific technical implementation choices marked `PROPOSED` remain controller recommendations pending founder or evidence-based confirmation.

## Product definition

CampaignForge is a consent-first AI content studio for creators. It learns an editable creator profile — style, voice, and appearance — from authorized source content and verified consent, uses that profile to help generate a new video featuring the creator's authorized voice and face, and records the entire lineage in durable storage.

## Primary user and job

Primary user: a solo creator or small creator-led brand who wants new on-brand video content featuring themselves without re-recording every idea.

Job: "Use what already works about me — how I look, sound, and deliver — to help me create the next video without losing my style or starting from a blank page."

## Target end-to-end flow

1. **Start project.** User names the creator/project and completes a rights/consent attestation, including explicit consent to analyze and use their face and voice.
2. **Upload authorized source.** Accept authorized reference video/audio/image material with clear limits. Store originals and metadata in B2.
3. **Verify consent.** Capture and persist a specific, verifiable consent record tied to the creator identity and the exact permitted uses (analysis, voice cloning, face/avatar generation, public demo).
4. **Analyze.** Extract a structured, editable creator profile: audience, content pillars, hook style, tone, structure, visual cues, appearance cues, CTA patterns, evidence notes, confidence, and uncertainty.
5. **Review profile.** Show the result, source evidence, and editable fields. Persist edits as a new version.
6. **Idea and script.** User supplies or selects a new topic; CampaignForge helps generate a script consistent with the creator profile.
7. **Voice generation.** Produce authorized cloned-voice audio for the script using the creator's verified voice profile.
8. **Face/avatar generation.** Produce a face/avatar video using the creator's verified authorized likeness, combined with the generated voice.
9. **Render.** Produce one playable final video.
10. **Inspect.** Show the output, pipeline stages, real status, cost estimate/record if available, and a "why this matches" explanation.
11. **Restore.** Refresh or revisit the project and see the persisted profile, script, voice, video, manifest, and history from B2-backed state, playable on demand.

## Required user-visible objects

- Creator Project
- Authorized Source Example
- Consent Record
- Creator Profile and version (style, voice, appearance)
- Content Idea and Script
- Voice Generation Run and Asset
- Face/Avatar Generation Run and Asset
- Final Rendered Video
- Provenance/lineage view

## System stage contract

The product is built and evidenced stage by stage. Each stage is distinct and must not be conflated with a later or earlier stage in any status report:

- Authorized source ingestion
- Consent verification
- Creator/style analysis
- Editable creator profile
- Idea generation
- Script generation
- Voice generation
- Face/avatar video generation
- Final rendering
- B2 persistence
- Provenance/lineage
- Restore and playback

No stage may be reported as working, tested, or complete until it is repository-verified through the real boundary (real provider call, real persisted object, real playback), per `docs/ops/CURRENT_STATE.md`.

## Creator profile contract

The analysis result must be structured JSON validated server-side and contain:

- `audience`
- `content_pillars[]`
- `voice_traits[]`
- `appearance_traits[]`
- `hook_patterns[]`
- `structure_patterns[]`
- `visual_patterns[]`
- `cta_patterns[]`
- `avoid[]`
- `evidence[]` with source reference and observation
- `confidence` and `limitations[]`
- analysis provider, model, prompt/schema version, timestamps, and source asset hash
- linked consent record identifier and permitted-use scope

It must not claim certainty from one example. Labels should say "initial profile" and make uncertainty visible.

## Functional acceptance

- A supported file uploads without exposing permanent B2 credentials.
- B2 contains the original with content type, size, checksum/hash, project key, and authorization/consent metadata.
- A real model analyzes the actual uploaded content or a technically valid derived representation; no fixture or canned response can satisfy production acceptance.
- The creator profile survives refresh and can be restored by project ID.
- A real cloned-voice audio asset is produced from the verified voice profile and persisted in B2.
- A real face/avatar video is produced from the verified authorized likeness and persisted in B2.
- The final rendered video is playable directly from B2-backed storage after restore.
- The final run has a valid Genblaze manifest with SHA-256-covered assets and parent/source lineage where supported.
- The UI distinguishes queued, running, succeeded, failed, and retry states.
- A judge can complete the golden path free of charge with clear instructions.

## Safety rules

- No unauthorized face or voice cloning. Every cloned voice and generated face/avatar must trace to a specific consent record for that specific person.
- No cloning public figures or third parties without verified authority and consent from that person.
- No impersonation intended to deceive, defraud, harass, or bypass identity controls.
- Store consent evidence and generation lineage alongside every generated asset.
- Clearly identify AI-generated output where disclosure is legally or platform-required.
- Never place secrets, credentials, raw tokens, or private customer data in commits, prompts, logs, screenshots, fixtures, or receipts.
- Provide deletion and revocation requirements in the product roadmap: a creator must be able to revoke consent and have their profile, voice model, and generated assets deleted.
- Generated content must remain attributable to its source creator profile and consent record.

Do not falsely claim that any stage currently works.

## B2 must be load-bearing

B2 stores:

- authorized source media;
- consent records and their permitted-use scope;
- derived thumbnails or analysis inputs when needed;
- versioned creator profile JSON (style, voice, appearance);
- generated script;
- generated voice audio asset;
- generated face/avatar video asset(s);
- final rendered video;
- Genblaze canonical manifest/provenance record;
- a minimal project index or references needed to restore and play back the experience.

Recommended object layout:

```text
projects/{project_id}/sources/{source_id}/original
projects/{project_id}/sources/{source_id}/metadata.json
projects/{project_id}/consent/{consent_id}.json
projects/{project_id}/profiles/v{n}.json
projects/{project_id}/runs/{run_id}/script.json
projects/{project_id}/runs/{run_id}/voice/...
projects/{project_id}/runs/{run_id}/video/...
projects/{project_id}/runs/{run_id}/manifest.json
projects/{project_id}/project.json
```

No application code should use direct `boto3` for generative run assets when Genblaze's B2/S3 backend can own that path. Raw authorized uploads may use secure presigned multipart upload if needed.

## Genblaze must be load-bearing

- Use the current released Genblaze packages pinned to tested versions.
- Use `Pipeline`/`Step` for generative voice/face/video work, provider adapters instead of direct model HTTP calls where an adapter exists, and `ObjectStorageSink`/B2 backend for output persistence.
- Persist and expose the canonical manifest and lineage.
- Use real step events for progress.
- If Genblaze/GMI Cloud does not directly support authorized voice cloning or face/avatar generation, document the exact boundary and identify which orchestrated provider fills the gap, while keeping Genblaze meaningfully load-bearing for the parts it does support (pipeline structure, manifest, B2 sink).

Primary implementation references:

- https://github.com/backblaze-labs/genblaze
- https://github.com/backblaze-labs/genblaze-gmicloud-pipeline

## Recommended technical shape

- Web: Next.js/React user interface. `PROPOSED` — not yet founder-approved as binding; see `docs/ops/DECISION_LOG.md` D-006.
- API/worker: Python 3.11+ FastAPI service because Genblaze is a Python SDK. `PROPOSED` — see D-006.
- Job/status: server-sent events or polling with durable run state; no fake progress.
- Storage: private Backblaze B2 bucket using bucket-scoped credentials.
- AI: the provider(s) capable of authorized voice cloning and face/avatar generation are not yet selected. GMI Cloud via `genblaze-gmicloud` is a candidate for image/video steps; exact providers and models must be selected only after a live capability test with the actual supported input, per the verification block in `docs/roadmap/CURRENT_ROADMAP.md` (Phase 0.5).
- Composition: avoid adding ffmpeg until a final composed artifact needs it.

This is a recommendation, not proof of the current repository, which has no runtime source at the recorded checkpoint.

## Quality, accessibility, and reliability

- Desktop and mobile responsive judge path.
- Keyboard reachable controls, visible focus, labeled inputs, useful errors, sufficient contrast.
- File type and size validation on client and server.
- Idempotency key per upload and run; retry does not duplicate successful assets.
- Timeouts, bounded retries with backoff, and a hard per-run spend guard.
- Structured logs without secrets or user media.
- Health endpoint and environment validation.
- Empty, loading, failure, refresh, and restored states covered by tests.

## Data and deletion

The contest build may be single-tenant only if labeled clearly. Before general SaaS launch, every record and object key must include tenant identity, authorization must be enforced server-side, users must be able to delete a project and all its assets (including voice and face models) and revoke consent, and retention must be documented.

## Analytics for product validation

Track without sensitive content: project started, source uploaded, consent captured, analysis completed/failed, profile edited, script generated, voice generation started/completed/failed, face/avatar generation started/completed/failed, final video rendered, asset approved/downloaded, time to first result, cost per successful run, and return use. Analytics are post-pilot unless needed for contest proof.

## SaaS hypotheses to validate

- The creator profile (style, voice, appearance) produces meaningfully more on-brand and authentic results than a generic prompt or generic avatar.
- Users value editability and evidence, not just output novelty.
- A creator can reach an approved video faster than re-recording themselves.
- Gross margin remains healthy after model, storage, support, and retry costs.
- Customers will return weekly and maintain more than one project.
- Consent and revocation controls are trusted enough that creators are willing to upload their face and voice.
