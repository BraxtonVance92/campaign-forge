# CF-V4 — credential/funding checklist and post-approval execution runbook

Status: prepared 2026-07-23. **Nothing in this document has been executed.**
Actual recorded spend: $0. Execution begins only after every item in the
"Preconditions" section is satisfied.

## Preconditions (all four; none are satisfied yet)

1. Colton's direct consent artifact recorded and persisted
   (`CF-V4-consent-artifact.md`; D-027 precondition 0).
2. GMI account funded (checklist below).
3. B2 bucket-scoped credentials configured (checklist below).
4. Founder's explicit HeyGen purchase approval (checklist below).

## Founder credential and funding checklist

### 1. GMI Cloud funding

- Recommended top-up: **$10** at console.gmicloud.ai → Credits & Coupons.
  Do not add more.
- Expected first-call range: MiniMax voice-clone request + a ~30s speech
  generation — documented sibling rates are cents-level (e.g. Kling
  Custom Voice $0.07/request; Seedance $0.07–0.152/sec); exact MiniMax
  rates are console-gated and will be recorded from the console/invoice
  before the call. Working estimate: **$0.10–$1.00 for the first
  attempt**; stop condition: if console pricing shows any single call
  above **$5**, stop and report before calling.
- Evidence to capture: console credit balance before/after (screenshot
  with account identifiers cropped), the per-call charge line — never
  the API key, never card details.
- Funding is account balance, not consumed spend; the receipt reports
  actual consumption from provider evidence only.

### 2. Backblaze B2

- Create (or confirm) one **private** bucket, e.g. `campaignforge-prod`
  (any name; record it in `.env` only).
- Create a **bucket-scoped application key** limited to that bucket with
  read/write object capabilities only — not the master key, no
  account-level or all-bucket permissions, no key-management capability.
- Put values in `.env` (never in git, logs, receipts, screenshots, or
  chat): `B2_KEY_ID`, `B2_APPLICATION_KEY`, `B2_BUCKET_NAME`,
  `B2_ENDPOINT` (the bucket's S3 endpoint, e.g.
  `https://s3.us-west-004.backblazeb2.com`). The Genblaze SDK uses
  `B2_BUCKET` / `B2_REGION` / `B2_KEY_ID` / `B2_APP_KEY` — the runbook
  maps app names to SDK names explicitly at execution time; both sets
  live only in `.env`.
- Safe verification (no secret printed): `/health` reports
  `b2_configured: true`, then one `head_bucket`/list call whose output
  is only a boolean recorded in the receipt.

### 3. HeyGen

- Plan: **Creator, $29/month, billed monthly** (not annual).
- Maximum approved charge: **$29 + tax** (~$32). Anything above requires
  new approval.
- Billing confirmation: select monthly billing explicitly; set a
  reminder to cancel before the renewal date (cancellation mechanics
  were not verifiable on official pages — treat the renewal date as the
  hard deadline for a cancel decision).
- Colton-controlled steps: voice-ownership verification for the voice
  clone; consent video only if the Digital Twin route is chosen.
- The founder performs the purchase and enters payment details;
  Claude never handles payment credentials.

## Final cost gate (current official pricing, checked 2026-07-22/23)

| Item | Amount |
|---|---|
| HeyGen Creator (unavoidable subscription, 1 month) | $29.00 |
| GMI top-up (account funding, not consumed spend) | $10.00 |
| Expected GMI voice-generation consumption | ~$0.10–$1.00 |
| Possible GMI repair attempt | ~$0.10–$1.00 |
| B2 at pilot scale (tens of MB) | ~$0.00 (cents at most) |
| Taxes/fees | ≤ ~$3 (assumed ≤10% on HeyGen; not separately documented) |
| **Maximum authorized exposure** | **≈ $42** |
| Remaining headroom below the $50 ceiling | ≥ $8 |
| Actual recorded spend to date | **$0.00** |
| Spend requiring further approval | anything beyond the above |

Unconsumed GMI balance remains account credit (refundability not
documented — treat as sunk once topped up for exposure math; that is
why the top-up is capped at $10).

## Post-approval execution runbook (exact sequence)

Repository root: the CampaignForge working clone (main). All commands
run from the repo root with `.venv` active. `$PID`/`$SID` are the
existing project/source ids recorded in `CF-V4-preproduction.md`.

1. **Validate consent record** — load the new consent record via
   `repository.get_consent`; assert its permitted uses include likeness
   generation + voice cloning and that the recording file exists in
   project-scoped storage. Abort if not.
2. **Verify secrets exist without printing values** —
   `python -c "from app.config import load_settings; s=load_settings(); print(s.gmi_configured, s.b2_configured)"`
   must print `True True`.
3. **Extract reference inputs locally** (no upload yet):
   ffmpeg frame extraction at a reviewed timestamp for the avatar photo;
   ffmpeg audio extraction of the clean speech segment(s) to WAV.
4. **Hash all authorized inputs** — `shasum -a 256` each; record in the
   receipt draft.
5. **Upload only approved inputs** — reference audio to the location the
   Genblaze GMI step requires; frame to HeyGen only within its flow.
6. **Execute the real Genblaze → GMI voice step** — Pipeline with
   `GMICloudAudioProvider`, model `minimax-audio-voice-clone-speech-2.6-hd`,
   `reference_audio=<uploaded sample>`, script lines as `prompt`,
   sink = `ObjectStorageSink(S3StorageBackend.for_backblaze(...))`.
7. **Capture evidence** — sanitized request (no key), terminal response,
   provider charge from console, output sha256, `step.cost_usd`.
8. **Store the GMI artifact in B2** — confirmed by reading back
   `sink.read_manifest(run)` and the asset object.
9. **Colton's HeyGen verification** — provider-controlled; wait for him.
10. **Execute the HeyGen avatar render** (script/audio → 9:16 render).
11. **Download and hash the real MP4** (`shasum -a 256`).
12. **Assemble** captions, punch-ins, disclosure, B-roll/overlays, music,
    SFX per the shot spec — as Genblaze custom steps (HeyGen
    `BaseProvider` wrapper + ffmpeg compositor step) so the final MP4 is
    a manifest asset with full lineage.
13. **Encode 9:16 H.264/AAC** at ≥720×1280.
14. **Full decode verification** — `ffmpeg -v error -i out.mp4 -f null -`
    exit 0.
15. **Inspect representative frames and audio** across every scene
    (same procedure as V3: frame extraction review + whisper
    transcription of the final mix).
16. **Store final V4 + canonical manifest in B2**; `manifest.verify()`
    must pass with SHA-256-covered assets.
17. **Append V4 as a new version** — `repository.save_generated_video`
    with `kind="final-render"`, `narration_kind="authorized-voice-clone"`,
    `likeness_used=True`, spec carrying provider/model/cost/consent
    references/deletion procedure. V1–V3 untouched.
18. **Verify in browser** — play, seek, resume; 404 on missing id;
    project isolation (foreign project id serves nothing).
19. **Run focused tests + the complete suite.**
20. **Secret and private-media scans** (same commands as the
    verification battery in the CF-V4 receipts).
21. **Update the V4 receipt and `docs/ops/CURRENT_STATE.md`** with
    provider evidence and truthful states.
22. **Commit bounded changes** on a feature branch; push.
23. **R1 and R2 review at the exact candidate SHA** (D-024 lane).
24. **Merge only if approvals + CI are green** (Authority Matrix).
25. **Deploy only from approved main** — and only with separate founder
    approval (deployment remains founder-reserved).
26. **Run live acceptance** against the deployed URL if/when deployed.
27. **Update the final receipt only after live verification** — until
    then the highest truthful state is MERGED.

Post-run cleanup (after founder accepts V4): delete the HeyGen voice
clone/avatar and uploaded references; file the GMI deletion request via
support and record the outcome; keep B2 artifacts (private) as the
provenance record.
