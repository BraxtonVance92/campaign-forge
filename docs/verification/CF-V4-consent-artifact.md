# CF-V4 — Colton's direct consent artifact (to be recorded by Colton personally)

Status: **NOT YET RECORDED.** This is the prepared script and procedure only.
Nothing may be uploaded to any provider until this artifact exists and is
persisted as a consent record (canon D-011; decision D-027 precondition 0).
Claude/CampaignForge must never fabricate, self-sign, edit, or simulate
this recording on Colton's behalf.

## The statement Colton records (read verbatim, filling in brackets)

> "My name is [FULL LEGAL NAME]. Today is [DATE].
> I knowingly authorize CampaignForge, managed by Braxton Vance, to use
> the reference videos, images, and audio recordings of me that I have
> approved.
> I authorize the creation of an AI-generated likeness and avatar of me,
> and the cloning of my voice to generate synthetic speech that sounds
> like me.
> I understand my approved reference material may be sent to HeyGen and
> to GMI Cloud for this processing.
> This permission is for private testing of CampaignForge only. Nothing
> may be published or shared publicly without my separate approval.
> I can revoke this permission for future use at any time, and I
> understand that removing anything already generated may require an
> explicit deletion request.
> I agree that every generated video will carry a visible disclosure that
> it is AI-generated."

Approximate reading time: 45–60 seconds at a natural pace.

## Recording instructions

- Quiet room; no background music, TV, or other voices.
- Face fully visible, centered, looking at the camera; no filters,
  no sunglasses, no hat brim shadowing the face.
- Portrait (9:16) framing, matching the provider requirement for
  vertical output; landscape is acceptable if a provider flow demands it.
- 1080p or higher; phone camera is fine; prop the phone or use a tripod
  so the shot is steady.
- Even, front-facing light on the face.
- One continuous take, no cuts or edits.
- File format: MP4 or MOV.
- Duration: the full statement in one take (roughly 45–60s).

## Handling after recording

1. The founder uploads the file into CampaignForge project-scoped
   storage (never committed to git) and a consent record is persisted
   referencing it (same mechanism as record `f5a618d6…`), with
   `permitted_uses` extended to: analysis, content development testing,
   AI likeness/avatar generation, synthetic voice cloning and speech
   generation — private testing only, publication excluded.
2. Separately from this artifact, Colton must still personally complete
   any provider-controlled verification when prompted (e.g. HeyGen's
   voice-ownership verification, and HeyGen's consent video if the
   Digital Twin route is used; D-ID's live webcam consent if the
   fallback is used). Those provider steps are in addition to — not a
   substitute for — this record.
3. Revocation: Colton can revoke at any time by telling the founder;
   the founder then deletes provider-side assets per the deletion
   procedures in `CF-V4-preproduction.md` and records the outcome.
