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
| Remove face or voice generation from core product scope | No | Recommend only | Approves |
| Add paid service or exceed $50 project ceiling | No | Recommend only | Approves |
| Access or expose production secrets/user data | Only via approved secret/runtime boundary | Approves design | Approves new access |
| Merge PR | No unless separately granted | Only after R1+R2 exact-SHA approval and branch protection | Founder approval required for first release |
| Deploy production, including creating a Render service | No | Prepare release; no standing authority yet | Approves each deployment until delegated |
| Submit Devpost entry, publish video, send external message | No | Prepare only | Approves/executes |
| Destructive data deletion, migration, permission broadening | No | Recommend with rollback | Explicit approval required |
| Use a specific person's face or voice without an already-recorded valid consent record | No | No | No — requires that person's own consent, not founder approval |

## Controller/CTO may

- Select routine technical implementation details: libraries, internal schemas, test strategy, retry limits, observability, responsive behavior, and provider/model candidates inside the approved budget and packet.
- Create work packets and require repairs.
- Review code and evidence.
- Manage safe, reversible development actions within approved scope.
- Recommend narrowing technical scope (for example, one authorized creator first) but may not recommend removing face or voice generation from the product without flagging it explicitly as a founder-approval item.

## Claude Code (maker) may

- Inspect the repository, docs, CI, and public technical sources.
- Implement only the approved active packet.
- Test, repair in-scope failures, and rerun checks.
- Push branches and open/update draft PRs.
- Monitor CI.
- Produce receipts.
- Claude Code may not silently narrow or remove face/voice generation, add product scope, or treat a prototype/simulated result as real.

## Founder approval is required for

- Changing core product strategy.
- Removing face or voice generation from core scope (already declined once by the founder; requires an explicit reversal by the founder to reconsider).
- Increasing the total spending ceiling above $50.
- Production/public deployment, including first creation of any Render (or other host) service, if current policy requires it.
- Final contest submission.
- Public launch.
- Pricing commitments.
- Legal-policy commitments (privacy policy, terms, consent language as binding legal text).
- Use of a creator's likeness or voice without already-recorded valid authorization from that specific creator.

## Creator authorization is required for

- Collecting training/reference material (video, image, or audio of a specific person).
- Cloning or synthesizing that person's voice.
- Generating face/avatar output using that person's likeness.
- Expanding permitted use beyond what was originally consented to.
- Retaining that person's data beyond the agreed scope.

No agent may treat the founder's authorization of the CampaignForge project as consent from another creator to use that creator's own face, voice, or likeness. Founder consent and subject/creator consent are separate, and both are required whenever the founder is not the subject.

## Technical decisions delegated to controller

The controller may select implementation details that preserve canon: libraries, internal schemas, test strategy, retry limits, observability, responsive behavior, and provider/model candidates inside the approved budget and packet. Material vendor addition, architecture rewrite, scope change (including removing face/voice generation), or recurring cost needs founder approval.

## Merge/release rule

No material change is `APPROVED` until R1 and R2 approve the exact same candidate SHA. Any commit invalidates both approvals. No change is `COMPLETE` until merged, deployed from main, live-verified, and receipts/current state are updated.

## Credentials and data

- Credentials must be bucket/provider scoped with least privilege and stored only in approved secret stores.
- Never place a real key in chat, code, `.env` committed to Git, logs, screenshots, tests, or receipts.
- The maker may reference environment variable names, never values.
- Public demo access may not expose private originals, including a creator's uploaded face/voice reference material.

## Founder approval packet format

When approval is required, provide one recommended choice, business impact, cost, risk, rollback, exact SHA/deployment target when relevant, and the precise action requested.
