# 2026-11-24 — Terminal replay safety at the preflight/adapter seam

- **Decision status:** offline experiment and durable regression accepted by owner on 2026-11-25; canonical reconciliation subject to review
- **SDLC phase:** release-production verification
- **Related defect:** DEF-0151 (canonical ledger), organization issue [#111](https://github.com/Young-Consultations/.github/issues/111)

## Goal and evidence
The historical #167 delivery was charged for a second model execution after a terminal failure. Verify the existing v4.0.0 guard rather than replay the actual failure. [Evidence and test results](https://github.com/Young-Consultations/.github/issues/111#issuecomment-7147665434).

The immutable control-plane commit is 6e51f058bf828b0732cb1b773ba1835acaa1d5cd and immutable consulting adapter is 84964d3ba099630cd5c6101e598bfca5433c74c5. Relevant local snapshot source/test/schema/workflow/policy blobs matched immutable GitHub tree entries.

## Observation
64 focused regression tests passed: 50 receiver/preflight and 14 adapter tests. One history-dependent conformance test was excluded after failing because the ZIP lacked the approved Git revision; local git init supplied the adapter askpass test directory. A new synthetic seam probe executed the actual preflight main, run_adapter and receiver with fake journal and effect interfaces; all 20 scenarios passed. All unsafe states stopped with zero model/publication/projection effects. One fresh admitted synthetic delivery produced exactly one fake model call, fake draft and projection; owned-draft redelivery produced no additional effects. Subprocess and socket traps observed zero external attempts in the seam probe.

## Learning and next decision
Trusted terminal receipts are a pre-execution boundary, not merely a receiver deduplication concern. Test both rejection and positive control, including the preflight-to-adapter output and receiver-visible idempotency. Do not replay finalized #167 or #170 to prove safety. The fake journal and runner seam do not prove live credential behavior or every race. Review the evidence and retain the reproducible regression probe before deciding closure of #111. #77 cost-bearing prerequisites remain separate. No new normative policy, activation, release, or Pi changes.

## 2026-11-25 — Governed A2.1 acceptance
Owner explicitly authorized acceptance conditional on exact post-merge CI. Organization [PR #125](https://github.com/Young-Consultations/.github/pull/125) added durable synthetic admission-to-receiver coverage. [PR SIM run](https://github.com/Young-Consultations/.github/actions/runs/45684632291) passed; issue #111 reports 24 new and 90 existing tests, retained JUnit artifact 15055811950 (contents not independently downloaded for this acceptance). Actual router, preflight, pinned adapter and receiver share a synthetic journal; strict fake transport, subprocess/socket traps, no real model/publication/projection. Independent [Codex review](https://github.com/Young-Consultations/.github/pull/125#issuecomment-7172716175) completed with zero findings at `3ac02ad508e89e0860510318d8a09ae117c90334`. Merge `c29cdade8e38e8b5b6ec3a831b9dc3be24266981` has identical tree `30cf36c00db6eff2007784b2e570ef8e744f752d`. [Exact main push Contract Tests](https://github.com/Young-Consultations/.github/actions/runs/45689236095) completed successfully on attempt 1, five of five jobs. SIM is PR evidence for identical tree, not a main rerun. Formal self-approval was rejected; owner explicitly authorized the merge. Separate security review not performed.

Acceptance is limited to the existing guard and deterministic offline regression; no claim of live permission/scheduling/atomicity assurance. Resolve DEF-0151 on this evidence and close #111 after canonical reconciliation review. A2.1 evidence gate satisfied; A2 completion is an offline checkpoint only, not v5 publication/adoption. DEF-0105 accepted-risk remains unchanged. #77 and v5 publication prerequisites remain separate. Never replay #167/#170; no live dispatch, paid AI implementation, publication, activation, tag, credential or Pi change.
