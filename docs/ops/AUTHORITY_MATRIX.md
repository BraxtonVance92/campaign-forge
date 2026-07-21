# CampaignForge Authority Matrix

## Roles

- Founder: Braxton Vance, final product and business authority.
- Controller/CTO: defines packets, architecture and evidence gates; reviews but does not self-approve maker work.
- Maker: Claude Code, implements only the active approved packet.
- R1: independent technical/security/operational reviewer.
- R2: independent product/UX/founder-intent reviewer.

## Standing authority

| Action | Maker | Controller/CTO | Founder |
|---|---|---|---|
| Read repo, docs, CI, public technical sources | Allowed | Allowed | — |
| Create branch/worktree within packet | Allowed | Allowed | — |
| Edit allowed paths, add tests, commit/push feature branch | Allowed | May direct/review | — |
| Open/update draft PR | Allowed | Allowed | — |
| Repair in-scope test/CI failures | Allowed | May issue bounded addendum | — |
| Change product scope, customer, pricing, brand promise | No | Recommend only | Approves |
| Add paid service or exceed $50 project ceiling | No | Recommend only | Approves |
| Access or expose production secrets/user data | Only via approved secret/runtime boundary | Approves design | Approves new access |
| Merge PR | No unless separately granted | Only after R1+R2 exact-SHA approval and branch protection | Founder approval required for first release |
| Deploy production | No | Prepare release; no standing authority yet | Approves each deployment until delegated |
| Submit Devpost entry, publish video, send external message | No | Prepare only | Approves/executes |
| Destructive data deletion, migration, permission broadening | No | Recommend with rollback | Explicit approval required |

## Technical decisions delegated to controller

The controller may select implementation details that preserve canon: libraries, internal schemas, test strategy, retry limits, observability, responsive behavior, and provider/model candidates inside the approved budget and packet. Material vendor addition, architecture rewrite, scope change, or recurring cost needs founder approval.

## Merge/release rule

No material change is `APPROVED` until R1 and R2 approve the exact same candidate SHA. Any commit invalidates both approvals. No change is `COMPLETE` until merged, deployed from main, live-verified, and receipts/current state are updated.

## Credentials and data

- Credentials must be bucket/provider scoped with least privilege and stored only in approved secret stores.
- Never place a real key in chat, code, `.env` committed to Git, logs, screenshots, tests, or receipts.
- The maker may reference environment variable names, never values.
- Public demo access may not expose private originals.

## Founder approval packet format

When approval is required, provide one recommended choice, business impact, cost, risk, rollback, exact SHA/deployment target when relevant, and the precise action requested.
