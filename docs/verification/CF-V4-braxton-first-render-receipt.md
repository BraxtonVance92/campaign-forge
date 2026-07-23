# CampaignForge — first REAL generated video (Braxton pilot), 2026-07-23

This records the first genuinely generated CampaignForge video: a real
private ~7-second vertical clip reproducing Braxton Vance's own face and
cloned voice. Not published, not deployed. Artifacts live in project-scoped
storage (gitignored) and the private B2 bucket — never committed to git.

## Authorization — BRAXTON_SELF_AUTHORIZATION

The subject is the account owner himself, Braxton Vance, and his own
recorded consent is in the supplied footage (`videos/IMG_5152.mp4`,
`IMG_5153.mp4`), first person, verbatim: *"I'm Braxton… I authorize
CampaignForge to use my face, voice, photos, and this recording to create
AI-generated content for me. I understand the system may generate videos of
me delivering scripts that I did not originally record."* This is the
subject's own verified, recorded consent — it satisfies D-011 directly
(subject = requester), unlike the deferred Colton work. No other person
appears in either video; the ten photos were not used for generation.
Nothing is claimed to be signed; this is recorded consent by the subject.

## Inputs used (SHA-256, verified against SHA256SUMS.txt)

- Voice reference: `braxton_voice_ref_30s.wav`, sha `304356e915f1…`
  (30s, mono 44.1k, peak −5.48 dB, no clipping), derived locally from
  `IMG_5152.mp4` (sha `a132a9b0…`, 38.61s, 512×910, h264/aac, clean decode).
- Face base segment: 7s from `IMG_5152.mp4` (10–17s), the frontal
  direct-to-camera section.

## Providers, models, jobs, real charges

| Step | Provider / model | request_id | Result | Charge |
|---|---|---|---|---|
| Voice clone | GMI Cloud / `minimax-audio-voice-clone-speech-2.6-hd` | `1fa29dc8-4806-4727-8468-68aaec961c1a` | success, 5.08s MP3 | not itemized in API response (console-gated); cents-level |
| Identify face | GMI Cloud / `kling-identify-face` | (persisted) | 1 face (id "0" = Braxton) | **$0.05** (`final_unit_deduction`) |
| Lip-sync | GMI Cloud / `kling-lip-sync` | `282e85bc-e0cb-4f85-94c0-c8c79114eb3e` (and a retried id) | success, 6.97s MP4 | not itemized in API response; two earlier attempts failed on param validation (no output) |

**Actual spend:** only identify-face is itemized by the API ($0.05). The
voice and lip-sync charges are not returned in their API responses and GMI
exposes no balance endpoint to this key, so the exact total is
console-only. Each individual request is bounded well under the $5/call
limit (a 5s voice clip and a ~7s lip-sync); the confirmed+estimated total
is a few dollars at most, far under the $50 ceiling. This is reported
honestly rather than asserted as an exact figure.

## Real outputs (in private B2 + project storage; not in git)

| Artifact | sha256 | B2 key |
|---|---|---|
| Cloned narration (5.08s MP3) | `ee63ab2076a7…` | `campaignforge/braxton-pilot/generated/braxton_voice_test_001.mp3` |
| Raw lip-sync (6.97s MP4) | `cff594c69c6b…` | `…/braxton_lipsync_test_001.mp4` |
| **Final disclosed MP4 (6.90s)** | `cbd0c94123e7…` | `…/braxton_v1_final.mp4` |
| Provenance manifest | — | `…/braxton_provenance_manifest.json` |

Local final path:
`.local_storage/projects/braxton-pilot-2026-07-23/generated/braxton_v1_final.mp4`

## Final video technical + validation

- 6.90s, 512×896 vertical, H.264 (yuv420p) + AAC stereo 44.1kHz, 1.29 MB.
- Full ffmpeg decode: **clean, zero errors**.
- Word-timed captions + persistent disclosure burned in:
  *"AI-generated video created with Braxton Vance's authorization."*
- Cloned-voice audio track (narration), original background muted.
- Browser (headless Chromium): plays, decodes, correct dimensions
  (512×896), no media error; seek accepted.

## Quality review (measured)

- **Voice:** intelligible, transcribes exactly to the script; clean, no
  clipping; a real clone of Braxton's reference (not stock). Full timbre/
  cadence resemblance is a listening judgment I can't fully self-assess.
- **Face/lip-sync:** identity is stable and clearly Braxton across frames;
  mouth moves naturally with the narration; lighting/background/hair
  preserved from the real footage. Ranked visible weaknesses: (1) mild
  softening around the mouth during fast phonemes (typical lip-sync
  artifact); (2) the clip is short (~7s) — a first test, not the full
  25–40s script; (3) minor caption-timing looseness vs. exact phoneme
  onsets. No frozen/black/corrupted frames; audio/video in sync.

## State

First real generated artifact = **DONE and verified** (real, decodable,
disclosed, private). Not published, not deployed. Natural next step (now
proven feasible and funded): generate the full ~30s script narration and
lip-sync a longer base segment for a 25–40s cut.
