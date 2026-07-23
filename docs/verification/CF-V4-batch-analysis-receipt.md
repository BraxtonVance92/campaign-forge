# CF-V4 — five-video reference batch analysis receipt (2026-07-23)

All processing was local; **$0 spent; nothing uploaded to any provider**;
originals preserved byte-identical in project-scoped storage
(`reference_batch_2026-07-23/`, gitignored) under consent `f5a618d6…`
permitted uses (analysis, content development testing). Provider upload
remains gated on D-027 precondition 0 (Colton's recorded consent).

## Batch manifest (5 files, 603.16s combined, all 720x1280 H.264 + AAC 44.1kHz stereo)

| File (prefix) | sha256 (prefix) | Duration | FPS | Decode |
|---|---|---|---|---|
| AQMBflM12t… | `3507640e2419…` | 156.89s | 30 | **clean — the externally reported near-end decode error did NOT reproduce** (`-v error` and `-err_detect explode` null decodes both exit 0); all frames usable |
| AQNBu_CobX… | `62734d4cb57c…` | 49.59s | 23.98 | clean |
| AQNKqwWqTv… | `e9f67ca09a8e…` | 50.52s | 23.98 | clean (byte-identical duplicate of the already-ingested CF-02/CF-04 source) |
| AQNLIgrCa9… | `6e566a062fc1…` | 177.56s | 30 | clean |
| AQOshxtmiL… | `8304013402a9…` | 168.60s | 30 | clean |

Full metadata + decode logs: `reference_batch_2026-07-23/batch_manifest.json`.

## Layout finding (changes the V4 picture materially)

The three long files are **green-screen composites: Colton front-facing,
gaze at lens, over news-article screenshots**, with caption overlays. This
supersedes the 2026-07-23 "no clean frontal frame exists" finding, which
was true only of the one previously-available side-angle interview video.
Frontal reference material now exists in quantity.

## Selected frames (2fps sampling → 1,006 frames → computational rank →
top-20 visual inspection → full-res finalist review)

Pose/gaze/mouth/occlusion were judged visually (no local landmark model);
sharpness/brightness/motion were computed. Crops persisted with hashes in
`reference_batch_2026-07-23/selected_frames/`.

| Rank | File | t (s) | sha256 (prefix) | Weaknesses |
|---|---|---|---|---|
| 1 | AQMBflM12t… | 152.5 | `d1d259e44c9b…` | near-neutral mouth (slight part), mild glasses glare, caption below chin (croppable) |
| 2 | AQNLIgrCa9… | 58.0 | `f2d6310d5441…` | small mouth opening; hand entering lower-right; mild glare |
| 3 | AQMBflM12t… | 113.5 | `703f0b767a6b…` | slight mouth opening |
| 4 | AQOshxtmiL… | 74.5 | `99db6536658d…` | mouth open mid-word; stronger outdoor glasses glare; smaller face scale |
| 5 | AQMBflM12t… | 50.5 | `946ff8167300…` | expressive alternate: brows raised, teeth visible |

Constant across all footage: backwards cap + translucent-frame glasses —
his signature look, which aids identity stability.

## Voice findings (all five transcribed with faster-whisper base, VAD on)

- ~595s of usable single-speaker speech; **zero clipping in every file**;
  no overlapping speakers; no background music bed detected (commentary
  videos; high transcription confidence; source separation judged
  unnecessary — originals untouched).
- Cleanliness ranking by mean transcription confidence:
  AQNLIgr (−0.117) > AQMBflM (−0.152) > AQNKqw (−0.161) >
  AQNBu (−0.222) > AQOshxt (−0.269, outdoor ambience).
- Measured delivery: **~200 wpm**, median clause 10 words, direct
  rhetorical moves ("I want you to consider this", "Me, though…",
  "The question you have to ask yourself").

Built references (`voice_references/`, conservative single-gain
normalization to ~−3 dB peak, no EQ/compression/denoise):

| Artifact | Duration | Peak/RMS | sha256 (prefix) | Source ranges |
|---|---|---|---|---|
| `clean_reference_45s.wav` | 45.70s | −3.26 / −20.7 dB | `490cfa4fa160…` | AQNLIgr 54.3–100.0s |
| `voice_dataset_297s.wav` | 297.47s | −2.60 / −20.4 dB | `4aad212985ac…` | AQNLIgr 0–177.56s + AQMBflM 0–120.0s |

Full transcripts with timestamps: `reference_batch_2026-07-23/transcripts.json`.

## Workflow decision (revised by the new material)

| Route | Verdict |
|---|---|
| **1. Existing-video dubbing / lip-sync (PROPOSED PRIMARY — requires founder ratification, see below)** | Genblaze → GMI: MiniMax voice clone generates the new script in Colton's voice (`minimax-audio-voice-clone-speech-2.6-hd`, first-class in the adapter), then **Kling Lip Sync** (`kling-identify-face` → `kling-lip-sync`, via the adapter's documented verbatim passthrough) re-syncs the mouth in a real continuous frontal segment (base: AQNLIgr 54.3–100.0s). Preserves Colton's REAL face motion, blinks, gestures, and identity — the strongest realism route — makes Genblaze/GMI genuinely load-bearing for BOTH generation steps (contest), and costs cents-level. Local composite then adds reframing, captions, disclosure, music. |
| 2. Photo-avatar (FALLBACK) | HeyGen Avatar IV from rank-1 frame + voice clone, $29 — now backed by a genuinely frontal frame. Used only if route 1's lip-sync quality fails review. |
| 3. Digital Twin | **Blocked on resolution**: HeyGen requires ≥1080p training footage; all five files are 720x1280. Excluded without new footage (which this packet forbids requesting). |

**Ratification required for route 1 (not a settled decision).** Route 1
uploads a ~45s segment of Colton's **face footage** to GMI Cloud, whose
media-retention/deletion policy is unpublished. That exceeds the founder's
recorded retention acceptance, which is scoped verbatim to "Colton's
reference audio sample," and departs from the D-027-ratified architecture
("HeyGen (direct) for Colton's authorized likeness"). GMI performs no
subject-level verification of its own for this route; the D-011 consent
artifact (which names GMI as a permitted recipient of approved reference
material) plus founder ratification is therefore the entire authorization
chain, and both must exist before any face-footage upload. Until the
founder explicitly ratifies route 1, **the D-027 architecture (route 2,
HeyGen for likeness) remains the standing default.** No route requires new
work from Colton beyond the already-required consent artifact.

Honest capability states for route 1: MiniMax clone = adapter-registered +
request-shape locally verified; Kling Lip Sync = **adapter passthrough
documented but not first-class registered; request shape NOT yet verified
locally** — it is the first thing the zero-cost validation of the next
execution step must pin down (the GMI quickstart documents the
identify-face → lip-sync flow). Neither has been executed live (funding).

## V4 script v2 (cadence-matched: ~112 words ≈ 34s at his measured ~200 wpm)

| # | Time | Line |
|---|---|---|
| 1 | 0–6s | "If you're posting every single day and your business still isn't growing, I want you to consider this." |
| 2 | 6–12s | "Every video you make starts from a blank page. One idea becomes one post, and by tomorrow it's buried." |
| 3 | 12–19s | "And here's the part nobody tracks: you can't tell which posts actually bring in customers and which ones just collect likes." |
| 4 | 19–27s | "Me, though? I'm focused on systems. A content system learns what works, turns one idea into a week of content, and tracks what sells." |
| 5 | 27–34s | "So the question you have to ask yourself is simple: who's building yours? Comment the word 'system' and I'll show you exactly how it works." |

Persistent disclosure throughout: "AI-generated video created with
Colton's authorization." Rhetorical frames are quoted from his own
measured usage across five videos — not invented from one example.

## Cost impact

If route 1 is ratified, HeyGen drops out of the first test. Decomposed
first-test exposure under route 1: $10 GMI top-up (of which expected
consumption ≈$0.50–2.00: voice clone + speech + identify-face + lip-sync
+ ≤1 repair) + ~$0 B2 at MB scale + ≤$3 tax/fees buffer = **≈$13
maximum**, vs ≈$42 under the standing route 2 (HeyGen $29 + GMI $10 +
≤$3). Stop condition unchanged (any single call >$5 halts); $50 ceiling
and all D-011/D-027 gates unchanged.

## Remaining blocker

1. Colton records the consent artifact (`CF-V4-consent-artifact.md`) —
   with route 1 it no longer needs to double as the avatar reference;
   existing footage suffices.
2. **Founder decision:** either (a) ratify route 1 — explicitly accepting
   that ~45s of Colton's face footage goes to GMI under its unpublished
   retention posture (with the same post-run deletion request + recorded
   outcome commitment as the audio sample), max first-test exposure ≈$13
   — or (b) keep the standing D-027 route 2 (HeyGen likeness, ≈$42).
   The ratification, either way, gets a DECISION_LOG row before
   execution.
3. Founder funds GMI $10.
4. Founder configures B2 bucket-scoped credentials in `.env`.
5. (Route 2 only:) HeyGen $29 approval.
