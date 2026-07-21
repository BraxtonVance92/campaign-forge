# campaign-forge
AI campaign builder using Genblaze and Backblaze B2

## Status

`CF-RUN-001` (in progress): the smallest real product slice — upload one authorized creator video, run real analysis (or an honest blocked state if `GMI_API_KEY` isn't configured), persist the result, and display/restore it. This is a narrow, unpolished proof slice, not the full contest MVP. Real Backblaze B2 credentials are also not configured in the environment this was built in; storage falls back to local disk in that case, clearly labeled as such in the running app (never presented as B2).

## Running it locally

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in real values if you have them; safe to leave blank
uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/` to create a project, upload a short `.mp4`/`.mov`/`.webm` with a consent attestation, and run analysis. Without `GMI_API_KEY` set, analysis will honestly report itself as blocked rather than fake a result. Without B2 credentials set, uploads persist to `./.local_storage/` (gitignored) instead of a real B2 bucket.

## Running the tests

```bash
pytest tests/ -v
```

## Documentation index

- [`CLAUDE.md`](CLAUDE.md) — Claude Code operating contract
- [`docs/canon/FOUNDER_CANON.md`](docs/canon/FOUNDER_CANON.md) — founder intent and constraints
- [`docs/canon/PRODUCT_CANON.md`](docs/canon/PRODUCT_CANON.md) — product definition and acceptance criteria
- [`docs/roadmap/CURRENT_ROADMAP.md`](docs/roadmap/CURRENT_ROADMAP.md) — ordered build plan
- [`docs/ops/AUTHORITY_MATRIX.md`](docs/ops/AUTHORITY_MATRIX.md) — who may approve what
- [`docs/ops/CURRENT_STATE.md`](docs/ops/CURRENT_STATE.md) — exact verified repository state
- [`docs/ops/ACTIVE_WORK_PACKET.md`](docs/ops/ACTIVE_WORK_PACKET.md) — the current approved work block
- [`docs/ops/DECISION_LOG.md`](docs/ops/DECISION_LOG.md) — founder-approved and proposed decisions
