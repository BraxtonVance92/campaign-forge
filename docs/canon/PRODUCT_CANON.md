# CampaignForge Product Canon

Status: proposed source of truth for the hackathon MVP. Founder approval makes product choices binding.

## Product definition

CampaignForge is a consent-first AI content studio for creators. It learns a visible creator fingerprint from authorized source content, uses that fingerprint to help generate a new branded media asset, and records the entire lineage in durable storage.

## Primary user and job

Primary user: a solo creator or small creator-led brand with existing videos or carousel posts.

Job: "Use what already works in my content to help me create the next post without losing my style or starting from a blank page."

## Hackathon MVP journey

1. **Start project.** User names the creator/project and accepts rights/consent attestation.
2. **Upload one example.** Accept one supported video or image/carousel example with clear limits. Store original and metadata in B2.
3. **Analyze.** Extract a structured creator fingerprint: audience, content pillars, hook style, tone, structure, visual cues, CTA patterns, evidence notes, confidence, and uncertainty.
4. **Review fingerprint.** Show the result, source evidence, and editable fields. Persist edits as a new version.
5. **Enter an idea.** User supplies one new topic or goal.
6. **Generate.** Build a creative brief from the fingerprint, generate one branded anchor image, and optionally turn it into one short vertical motion clip using GMI Cloud through Genblaze.
7. **Inspect.** Show the output, stages, real status, cost estimate/record if available, and "why this matches" explanation.
8. **Restore.** Refresh or revisit the project and see the persisted fingerprint, output, manifest, and history from B2-backed state.

## Required user-visible objects

- Creator Project
- Authorized Source Example
- Creator Fingerprint and version
- Content Idea
- Generation Run
- Generated Asset
- Provenance/lineage view

## Creator fingerprint contract

The analysis result must be structured JSON validated server-side and contain:

- `audience`
- `content_pillars[]`
- `voice_traits[]`
- `hook_patterns[]`
- `structure_patterns[]`
- `visual_patterns[]`
- `cta_patterns[]`
- `avoid[]`
- `evidence[]` with source reference and observation
- `confidence` and `limitations[]`
- analysis provider, model, prompt/schema version, timestamps, and source asset hash

It must not claim certainty from one example. Labels should say "initial fingerprint" and make uncertainty visible.

## Functional acceptance

- A supported file uploads without exposing permanent B2 credentials.
- B2 contains the original with content type, size, checksum/hash, project key, and authorization metadata.
- A real model analyzes the actual uploaded content or a technically valid derived representation; no fixture or canned response can satisfy production acceptance.
- The fingerprint survives refresh and can be restored by project ID.
- At least one real image or video generation runs through a Genblaze `Pipeline` step and lands in B2 through the Genblaze storage sink.
- The final run has a valid Genblaze manifest with SHA-256-covered assets and parent/source lineage where supported.
- The UI distinguishes queued, running, succeeded, failed, and retry states.
- A judge can complete the golden path free of charge with clear instructions.

## B2 must be load-bearing

B2 stores:

- authorized source media;
- derived thumbnails or analysis inputs when needed;
- versioned fingerprint JSON;
- creative brief and run metadata;
- every generated intermediate and final asset;
- Genblaze canonical manifest/provenance record;
- a minimal project index or references needed to restore the experience.

Recommended object layout:

```text
projects/{project_id}/sources/{source_id}/original
projects/{project_id}/sources/{source_id}/metadata.json
projects/{project_id}/fingerprints/v{n}.json
projects/{project_id}/runs/{run_id}/brief.json
projects/{project_id}/runs/{run_id}/assets/...
projects/{project_id}/runs/{run_id}/manifest.json
projects/{project_id}/project.json
```

No application code should use direct `boto3` for generative run assets when Genblaze's B2/S3 backend can own that path. Raw authorized uploads may use secure presigned multipart upload if needed.

## Genblaze must be load-bearing

- Use the current released Genblaze packages pinned to tested versions.
- Use `Pipeline`/`Step` for generative image/video work, provider adapters instead of direct model HTTP calls, and `ObjectStorageSink`/B2 backend for output persistence.
- Persist and expose the canonical manifest and lineage.
- Use real step events for progress.
- A provider switch or bounded retry may demonstrate production value; model fan-out is optional.
- If the analysis provider cannot be a Genblaze pipeline step, document the boundary and ensure the generation path still uses Genblaze meaningfully.

Primary implementation references:

- https://github.com/backblaze-labs/genblaze
- https://github.com/backblaze-labs/genblaze-gmicloud-pipeline

## Recommended technical shape

- Web: Next.js/React user interface.
- API/worker: Python 3.11+ FastAPI service because Genblaze is a Python SDK.
- Job/status: server-sent events or polling with durable run state; no fake progress.
- Storage: private Backblaze B2 bucket using bucket-scoped credentials.
- AI: GMI Cloud via `genblaze-gmicloud` for image/video generation. The analysis model must be selected only after a live capability test with the actual supported input.
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

The contest build may be single-tenant only if labeled clearly. Before general SaaS launch, every record and object key must include tenant identity, authorization must be enforced server-side, users must be able to delete a project and its assets, and retention must be documented.

## Analytics for product validation

Track without sensitive content: project started, source uploaded, analysis completed/failed, fingerprint edited, generation started/completed/failed, asset approved/downloaded, time to first result, cost per successful run, and return use. Analytics are post-pilot unless needed for contest proof.

## SaaS hypotheses to validate

- The fingerprint produces meaningfully more on-brand results than a generic prompt.
- Users value editability and evidence, not just output novelty.
- A creator can reach an approved asset in fewer than ten minutes.
- Gross margin remains healthy after model, storage, support, and retry costs.
- Customers will return weekly and maintain more than one project.
