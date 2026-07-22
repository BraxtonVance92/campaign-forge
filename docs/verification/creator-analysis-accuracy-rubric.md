# Creator analysis accuracy rubric and performance-metric import format (draft)

Prepared ahead of `CF-06`/`CF-07` (`docs/roadmap/CAMPAIGNFORGE_EXECUTION_LEDGER.md`),
while `CF-02`/`CF-03` remain blocked on credentials. This is a draft
methodology only — no video has been evaluated against it yet, and no
data has been imported. Nothing here implies any of this ran.

## Part 1 — Accuracy rubric (`CF-06`)

Applied per-video, then rolled up across the small batch (5-10 videos,
`CF-05`). Score each dimension 1-5; 1 note per dimension is required, not
optional, so scores are traceable to a reason rather than a bare number.

| Dimension | 1 (poor) | 3 (mixed) | 5 (strong) | Note required |
|---|---|---|---|---|
| Factual accuracy | Invents facts not in the video | Mostly correct, minor errors | Everything checkable is correct | Cite the specific claim checked |
| Style/tone recognition | Generic, could describe any creator | Partially recognizable | Clearly matches this creator's real voice | Quote the profile text being judged |
| Hook recognition | Misses or misidentifies the opening hook | Identifies a hook but mischaracterizes it | Correctly identifies hook type and why it works | Reference the video's actual opening seconds |
| Content-pattern recognition | No real structure identified | Partial structure identified | Structure matches what a human reviewer sees | — |
| Actionable insight | Vague, not usable | Somewhat usable with editing | Directly usable as-is | — |
| Hallucination severity | Severe fabricated claim (e.g. wrong topic entirely) | Minor unsupported embellishment | No fabrication detected | Any hallucination found must be logged even at score 5 elsewhere |
| Overall usefulness | Not worth using | Worth using with heavy editing | Worth using with light or no editing | — |

**Kill-gate thresholds (from the ledger, do not loosen without founder approval):**
Continue past `CF-06` only if:
- Overall usefulness ≥ 4/5 (creator-rated, not self-rated by the model).
- No severe fabricated claim across the batch.
- At least 80% of checkable claims correct across the batch.

Otherwise: improve the prompt/provider once and repeat. After two failed
rounds, stop and reassess the product premise — do not attempt a third
round without founder review.

## Part 2 — Performance-metric import format (`CF-07`)

Prefer an authorized platform API/export. If unavailable, accept a single
CSV with these columns (header row required, extra columns ignored,
missing values left blank rather than guessed):

```csv
video_id,platform,publish_date,views,reach,impressions,watch_time_seconds,retention_pct,likes,comments,shares,saves,follower_count_at_publish
```

- `video_id` must match the `source_asset_hash` or an explicit mapping
  recorded alongside the import — metrics must join deterministically to
  a real persisted source, never by guessed filename similarity.
- Any column left blank for a row is treated as "not available" and
  displayed as such — never zero-filled, never inferred.
- Normalization (e.g. views-per-follower, watch-time-as-percent-of-length)
  is computed and displayed separately from the raw imported values, and
  is clearly labeled as a derived correlation, not a causal claim.
- No founder or creator is ever asked to hand-type more than this one
  small export per batch — manual population of a large table is
  explicitly out of scope per the ledger's binding doctrine.

This format is a draft and has not been implemented or tested against
real data. It exists so `CF-07` has a concrete starting point rather than
being designed from scratch once `CF-06` passes.
