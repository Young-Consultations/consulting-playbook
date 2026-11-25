# 2026-11-24 — Terminal replay safety at the preflight/adapter seam

- **Decision status:** offline experiment passed; issue acceptance pending
- **SDLC phase:** release-production verification
- **Related defect:** DEF-0151 (candidate ledger), organization issue [#111](https://github.com/Young-Consultations/.github/issues/111)

## Goal and evidence
The historical #167 delivery was charged for a second model execution after a terminal failure. Verify the existing v4.0.0 guard rather than replay the actual failure. [Evidence and test results](https://github.com/Young-Consultations/.github/issues/111#issuecomment-7147665434).

The immutable control-plane commit is 6e51f058bf828b0732cb1b773ba1835acaa1d5cd and immutable consulting adapter is 84964d3ba099630cd5c6101e598bfca5433c74c5. Relevant local snapshot source/test/schema/workflow/policy blobs matched immutable GitHub tree entries.

## Observation
64 focused regression tests passed: 50 receiver/preflight and 14 adapter tests. One history-dependent conformance test was excluded after failing because the ZIP lacked the approved Git revision; local git init supplied the adapter askpass test directory. A new synthetic seam probe executed the actual preflight main, run_adapter and receiver with fake journal and effect interfaces; all 20 scenarios passed. All unsafe states stopped with zero model/publication/projection effects. One fresh admitted synthetic delivery produced exactly one fake model call, fake draft and projection; owned-draft redelivery produced no additional effects. Subprocess and socket traps observed zero external attempts in the seam probe.

## Learning and next decision
Trusted terminal receipts are a pre-execution boundary, not merely a receiver deduplication concern. Test both rejection and positive control, including the preflight-to-adapter output and receiver-visible idempotency. Do not replay finalized #167 or #170 to prove safety. The fake journal and runner seam do not prove live credential behavior or every race. Review the evidence and retain the reproducible regression probe before deciding closure of #111. #77 cost-bearing prerequisites remain separate. No new normative policy, activation, release, or Pi changes.
