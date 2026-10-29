# DEF-0125 live acceptance and closure

DEF-0125 is resolved following independent evidence review on 2026-10-28
(America/Phoenix). The earlier journal entries describe historical investigation;
their pending-acceptance dispositions are superseded by this record.

## Evidence chain

- ADR-013 / PR #95 approved executor/content separation; PR #96 implemented it.
- Adapter `codex-adapter-v4.0.0`: `84964d3ba099630cd5c6101e598bfca5433c74c5`.
- Control plane `ai-sdlc-v4.0.0`: `6e51f058bf828b0732cb1b773ba1835acaa1d5cd`;
  organization PR #117 attested publication; portfolio PR #169 migrated source.
- Deployed runtime [40800598820](https://github.com/Young-Consultations/.github/actions/runs/40800598820)
  and readiness [40800767847](https://github.com/Young-Consultations/.github/actions/runs/40800767847) passed.
- Marker PR #98 advanced main to `bcad36dca1faf911499b09e0cf02b5d32fc69ae3`.
- Fresh source [#171](https://github.com/Young-Consultations/portfolio-tasks/issues/171)
  ran [40802447762](https://github.com/Young-Consultations/consulting-playbook/actions/runs/40802447762).
  One model invocation produced candidate `15d705e970c1dc25f3048738643f4773e25056da`;
  its sole parent equals the newer content base while executor SHA stays fixed.
  It copied `DEF0125-CURRENT-CONTENT-20261029-A`, absent from the executor.
- Original candidate CI 40802535720 passed. One owned PR #99 and one matching
  receipt, forwarding marker and receiver-validated source projection were verified.
- Operator corrected the source-issue and relative marker links in `229833d`,
  without a second model invocation. Final CI 40802724235 and Codex review passed;
  PR #99 merged as `c56870f2eb1bd622a4c67bae7eb47563322ebde2`.

## Learning and limits

Source #170 failed because the marker prerequisite had not been prepared and the
task mixed operator acceptance work with model instructions. Preserve its terminal
failure evidence. The replacement separated a bounded edit from operator checks
and merged the prerequisite before approval. A green readiness test did not prove
that task-specific prerequisites were present.

The live run proves current-content execution under an older trusted executor and
single publication/receipt for this delivery. Offline race/security regressions
remain complementary evidence. It does not prove every other defect resolved,
test terminal-failure replay again, or enable disabled targets. Never replay
finalized sources #167 or #170. Source #167's original editorial task remains
unfulfilled and must not be closed as completed by this acceptance.
