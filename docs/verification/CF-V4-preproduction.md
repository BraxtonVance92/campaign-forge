# CF-V4 pre-production packet (2026-07-22)

Status: preparation only. **Actual spend so far: $0.** No media was uploaded
to any external service, no external generation or cloning API was called,
and no V4 record exists in storage (nothing is marked generated before a
real output file exists).

## Authorization record (founder-attested)

On 2026-07-22 the founder (Braxton Vance) attested, in the V4 work packet:

- Colton authorized synthetic use of his face, likeness, and voice.
- The founder manages Colton's social media and is authorized to manage the
  relevant source material and production workflow.
- Colton authorized use for this CampaignForge prototype.

This is recorded here as a **founder-attested authorization fact**. It
supplements — and does not replace — the existing persisted consent record
`f5a618d6-491b-4e49-bdc6-a763160214f7` ("analysis", "content development
testing"), which remains unchanged. Constraints that still bind V4:

- The first V4 render stays private; no publication, no deployment.
- The video carries a clear, persistent AI-generated disclosure.
- Any provider-side consent/identity-verification step must be genuinely
  completed by Colton personally; provider safeguards are never bypassed.
- Total spend ceiling $50; no paid call before the founder approves the
  exact expected cost.

## Verified identity of the "GMI" credential

`GMI_API_KEY` belongs to **GMI Cloud** (gmicloud.ai) — a GPU/inference
cloud with an OpenAI-compatible LLM endpoint at
`api.gmi-serving.com/v1/chat/completions`. Repo evidence: `app/analysis.py`
(endpoint + docs.gmicloud.ai quickstart reference, verified during CF-02)
and `docs/verification/CF-02-model-candidates.md` (a real `/v1/models` call
returned ~85 text-oriented chat models; none labeled vision/video/TTS/
avatar). It is **not** Google Gemini/AI Studio/Vertex. Account state as
last observed: HTTP 402 "Insufficient balance". Capability findings from
current-web research are appended in the provider-decision section.

## Reference inventory (authorized project material only)

One authorized source video (source `92bc1f7c…`, consent `f5a618d6…`,
sha256 `e9f67ca0…953a`, stored only in project-scoped storage; never
committed to git; **not uploaded anywhere during this packet**):

- 50.52s, 720x1280 vertical, h264 23.98fps, AAC stereo 44.1kHz, 4.08 MB.
- ~50.4s of continuous clean single-speaker speech (11 whisper segments,
  full transcript persisted in the CF-04 analysis run); no overlapping
  speakers or interruptions observed.
- Framing: direct-to-camera, eye-level, medium chest-up, seated; face
  frontal with slight body angle; 12 sampled frames persisted.
- Lighting: neutral front key light on the face over a blue-lit hexagonal
  backdrop; face well exposed, not color-cast.
- Audio: clear voiced delivery; background noise not independently
  measured; no music bed audible per analysis.

Sufficiency assessment against provider requirements is recorded in the
provider-decision section below.

## Final proposed V4 script (~96 words, ≈30s target)

Direct, conversational, easy to speak. No claim that CampaignForge has
learned Colton's style; no income or performance promises. No difficult
pronunciations. Persistent on-video disclosure (all scenes):
**"AI-generated video created with Colton's authorization."**

| # | Time (target) | Line | Delivery note |
|---|---|---|---|
| 1 | 0.0–4.0 | "If you're posting every day and your business still isn't growing — this is probably why." | Energetic hook, slight upward inflection on "why" |
| 2 | 4.0–9.5 | "Right now, every video you make starts from a blank page. One idea, one post — and by tomorrow, it's buried." | Fast, clipped rhythm |
| 3 | 9.5–15.5 | "And here's the worst part: you can't tell which posts actually bring in customers, and which ones just get likes." | Emphasis on "customers" vs "likes" |
| 4 | 15.5–24.0 | "That's what a content system fixes. It studies what actually works, turns one idea into a week of content, and tracks what sells." | Deliberate downshift, measured |
| 5 | 24.0–30.0 | "Want to see it? Comment the word 'system' and I'll walk you through exactly how it works." | Confident, natural CTA |

## Shot / edit spec (full runtime)

Base: Colton's authorized talking avatar, 9:16 at 720x1280 minimum, H.264
+ AAC. The avatar render is the continuous visual anchor; overlays and
reframes prevent a static talking head.

| Shot | Time | Framing / motion | Overlays & captions |
|---|---|---|---|
| S1 | 0.0–4.0 | Medium chest-up (matches source framing); punch-in ~8% on "this is probably why" | Word-timed captions, lower third; "still isn't growing" highlighted |
| S2 | 4.0–9.5 | Slightly wider reframe | Top-third overlay: blank-page card → single post card sinking/fading (V3 asset style); pop SFX on card appear |
| S3 | 9.5–15.5 | Punch-in on "worst part", hold tight | Split mini-chart overlay: "likes" line vs "customers" line diverging (adapted V3 chart); emphasis words in accent color |
| S4 | 15.5–24.0 | Return to medium; slower cut rhythm (downshift) | Side card: one idea branching into a week grid (V3 branching asset); music bed swells slightly |
| S5 | 24.0–30.0 | Tightest framing for CTA | Typed comment bubble "system" with caret + tick SFX per letter; final 1.5s end card "CampaignForge · concept" |
| All | 0–30 | — | Persistent disclosure line, bottom: "AI-generated video created with Colton's authorization."; music ≥14 dB under speech; whoosh on scene changes |

Compositing of overlays/captions/music happens locally with the existing
V3 stack (PIL + ffmpeg) on top of the provider's avatar render, so paid
provider output is consumed once and repairs to captions/overlays cost $0.

## Prepared CampaignForge integration path

Already shipped (PRs #12/#13): append-only versioning (V1–V3 untouched),
project-scoped storage keys, safe `?video_id=` media route with project
isolation and HTTP Range seeking, per-version kind labels.

Prepared in this packet: per-version likeness/narration labeling derived
from record fields (`likeness_used`, `narration_kind`), plus a
`final-render` label branch — so a V4 record renders as "Final render —
AI-generated video / Authorized real likeness of the creator is used ·
Narration: authorized synthetic clone of the creator's voice" while V1–V3
keep their no-likeness labels. Covered by tests.

V4 persistence plan (executed only after a real MP4 exists):
`GeneratedVideoRecord(kind="final-render",
narration_kind="authorized-voice-clone", likeness_used=True,
spec={provider, product, cost_usd_actual, consent_reference:
"f5a618d6-… + founder-attested V4 authorization (this document)",
disclosure_overlay, script, reference_files, deletion_procedure},
render_method="<provider>-avatar-render+local-composite")` via
`repository.save_generated_video` — no schema change required.

## Provider decision (current official docs/pricing, checked 2026-07-22)

### GMI Cloud capability verdict

GMI Cloud's Inference Engine resells avatar/voice models beyond its chat
endpoint (via `console.gmicloud.ai/api/v1/ie/requestqueue`): HeyGen
Avatar 4 talking-photo ($0.05/sec), Kling Custom Voice ($0.07/request,
5–30s sample), Kling Lip Sync, Wan2.2-Animate (sources:
docs.gmicloud.ai/model-quickstarts/video/heygen-avatar-4.md,
…/audio/kling-custom-voice.md, …/video/kling-lip-sync.md). So GMI *can*
technically generate both an authorized face video and a cloned voice.
**It is nevertheless excluded for V4 likeness work** on this packet's own
criteria: (a) GMI publishes no retention/deletion policy for uploaded
media or biometric material (privacy policy is silent; inference-storage
docs state no expiry/deletion terms) — "unclear reference-data handling"
is a hard exclusion; (b) routing through GMI's proxy would sidestep the
upstream providers' subject-level consent verification, which we will not
bypass; (c) the account is prepaid with a current 402 insufficient-balance
state. GMI is not forced into the workflow merely because a key exists.

### Ranked decision

| Option | Total ≤$50? | Face | Voice | Consent rigor | Notes |
|---|---|---|---|---|---|
| **HeyGen Creator $29/mo (PRIMARY)** | Yes ($29) | Avatar IV photo (1 photo) or Digital Twin (needs ≥2 min footage) | Native instant clone (30s audio min) | Digital Twin: subject's own <30s consent video, no delegation; voice: ownership verification/written consent | Watermark-free 1080p, 9:16, 600 credits ≈ 40+ renders, documented biometric destruction + deletion |
| **D-ID Pro $29/mo (FALLBACK)** | Yes ($29) | Photo avatar or V3 Instant (1–2 min footage) | 1 voice clone included | Strongest: live webcam consent + passcode + face-match + voice verification | Small "AI" watermark (aligned with our disclosure), 1080p |
| Captions Max $24.99 | Yes | Twin from photo/short video | Yes | Weakest documented verification; 3-year biometric window, email-only deletion | Excluded on data-handling criteria |
| Synthesia Starter $29 | Yes | Personal avatar (photo or 1–5 min) | Cloning-on-Starter unverified | Live consent video mandatory | Viable third option; voice uncertainty |
| Tavus Starter $59 | **No** | — | — | Verbatim consent statement | Over ceiling |
| Runway Act-Two + ElevenLabs ~$18–21 | Yes | Performance transfer | ElevenLabs IVC $6 | No subject verification for likeness | Needs human driving performance; not purpose-built |
| Google Veo 3.1 | Yes | I2V reference | Native audio only | — | Cannot lip-sync a supplied script/voice; excluded |
| GMI Cloud (HeyGen-4/Kling) | Yes (~$3–6) | Yes | Yes | None documented | Excluded — see verdict above |

**Primary: HeyGen, Creator plan, one month at $29 (billed monthly).**
Face method: Avatar IV photo avatar from one clean frontal frame of the
authorized source video (sufficient today); optional quality upgrade on
the same plan: Digital Twin, if Colton records one continuous 2–5 min
clip (then his personal consent video is mandatory). Voice method:
HeyGen native instant voice clone from the ~50s of clean speech in the
authorized video (meets the 30s minimum; 1–3 min recommended — the new
recording, if made, also improves this). Why it wins: the only option
that does both face and voice at one vendor (minimum biometric
distribution — the packet's stated preference), watermark-free 1080p
vertical export, documented biometric-destruction and deletion policy,
and enough included credits that repair renders cost $0 marginal.
Expected quality: photorealistic lip-synced head/face motion (official
Avatar IV claims); known weaknesses: photo-route body language is
synthesized, not Colton's own gesturing (Digital Twin upgrade fixes
this); render turnaround for ~30s unpublished (expected minutes).
Deletion procedure after completion: delete the voice clone and the
avatar/Digital Twin slot in-app, request likeness removal per
moderation policy; HeyGen's biometric notice commits to permanent
destruction of face-geometry data no longer needed.
Sources: heygen.com/pricing, help.heygen.com articles 12623520,
12089286, 12092609, 9834925, 9380615, 15125761, heygen.com/api-pricing,
heygen.com/biometric-privacy-notice, heygen.com/moderation-policy.

**Fallback: D-ID, Pro plan, one month at $29.** Photo avatar route works
with existing material; V3 Instant Avatar wants 1–2 min footage (50s may
be rejected — would need the same new recording). Strongest identity
verification (live webcam consent with passcode, face match, voice
verification). Its small "AI" watermark is acceptable — we add a
disclosure anyway. Sources: d-id.com/pricing/studio, help.d-id.com
articles 31199170758545, 31467532751889, 30782586495633, 31450804729233,
d-id.com/privacy-policy.

### Cost gate

| Item | Amount |
|---|---|
| Actual spend so far (this packet) | **$0** |
| Optional $0 staging | HeyGen Free includes Avatar IV access + 1 Digital Twin slot (watermarked, 3 videos/mo) — avatar quality can be validated at $0 before paying |
| Unavoidable upfront for clean render | $29 — one HeyGen Creator month, billed monthly (includes avatar, voice clone, 600 credits) |
| Voice setup / avatar setup fee | $0 (plan-included; no one-time fee documented) |
| Expected first-render cost | $0 marginal (~10–14 of 600 credits for 30–40s Avatar IV) |
| Repair renders | $0 marginal (~40+ attempts within included credits) |
| Taxes/fees | Unknown; assume ≤10% → ≤$3 |
| **Maximum total exposure** | **≈$29–32** |
| Remaining under $50 ceiling | ≥$18 |

No paid call happens until the founder approves the exact $29 spend.

### Provider-controlled steps Colton must personally complete

1. HeyGen voice cloning of a third-party voice requires voice-ownership
   verification / written consent from Colton (form of attestation per
   HeyGen's flow) — cannot be skipped or faked.
2. If the Digital Twin route is used: Colton must personally record his
   own sub-30s consent video reading HeyGen's on-screen generated
   statement (no delegation, no screen recordings, submitted with the
   training footage).
3. If the fallback (D-ID) is used: Colton personally completes the live
   webcam consent with dynamic passcode; the platform face-matches him
   against training footage and runs voice verification.

### Reference sufficiency

- Voice clone: **sufficient** (~50s clean single-speaker speech ≥ 30s
  minimum).
- Photo avatar (primary route): **sufficient** — one clean, frontal,
  well-lit frame extracted locally from the authorized video.
- Digital Twin (optional upgrade): **not sufficient** — requires one
  continuous ≥2 min (5 min recommended) take at ≥1080p/30fps. Smallest
  additional recording, only if the founder wants this upgrade: phone
  camera OK, 2–5 min single take, no cuts, 1080p+ (4K if easy), vertical
  9:16 or landscape, eye level, chest-up framing, even front light on the
  face, quiet room with no background speech/music, natural conversational
  speaking with brief pauses and normal head movement, MP4/MOV — plus the
  separate consent video in step 2 above.

### Execution path (after founder approval of $29)

1. Founder subscribes to HeyGen Creator ($29, monthly billing) — founder
   action, uses founder's payment method; Claude never enters payment
   credentials.
2. Extract one frontal reference frame + the clean speech audio from the
   authorized source video locally (ffmpeg; no upload yet).
3. In HeyGen: create instant voice clone (Colton's written consent /
   ownership verification as required by the flow), create Avatar IV
   photo avatar from the reference frame, submit the V4 script
   (five lines, ~96 words) with 9:16 output.
4. Download the avatar render; composite locally with the existing V3
   stack (captions, overlays, music, SFX, persistent disclosure
   "AI-generated video created with Colton's authorization.").
5. Validate (ffprobe + full decode + frame inspection + browser
   play/seek), persist as V4 via `repository.save_generated_video`
   (final-render / authorized-voice-clone / likeness_used=True, spec
   carries provider, actual cost, consent references, deletion
   procedure), verify V1–V3 untouched, run the suite, quiet governance.
6. Delete the voice clone, avatar, and uploaded reference material from
   HeyGen per the deletion procedure once the founder accepts V4.

### The single approval required

> **"Approved: spend $29 (one month of HeyGen Creator, billed monthly) for
> the V4 render."**

Optionally add: "and Colton will record the 2–5 min Digital Twin clip"
for the quality upgrade; otherwise the photo-avatar route proceeds with
existing material.

