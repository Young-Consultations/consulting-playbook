# 2026-10-17: Immutable executor identity is not task-content freshness

- **Date:** 2026-10-17 (Arizona local date; GitHub runs occurred 2026-10-18 UTC)
- **Decision status:** approved design on 2026-10-17; implementation pending
- **SDLC phase:** release-production discovery and architecture-design rework

## Context

The source migration to `ai-sdlc-v3.1.0`, deployed
[Runtime Preflight #39086605325](https://github.com/Young-Consultations/.github/actions/runs/39086605325),
[SIM #39087269988](https://github.com/Young-Consultations/.github/actions/runs/39087269988)
and [no-Codex REAL-readiness #39087311313](https://github.com/Young-Consultations/.github/actions/runs/39087311313)
all passed. These prove the release's controlled configuration and
simulation/evidence path, not that generated work is based on current content.

## Discovery

[Consulting issue #93](https://github.com/Young-Consultations/consulting-playbook/issues/93)
records production E2E [run 38996859486](https://github.com/Young-Consultations/consulting-playbook/actions/runs/38996859486):
the prior immutable executor revision `f11852c7` was also the content
checkout. Codex generated outdated ledger and content assumptions instead of
working from the then-current default branch. No valid draft was published.

This is not fixed by pinning newer executor code. The current reviewed
`codex-adapter-v3.1.0` workflow still has one checkout and
`GitHubEffects.codex`, candidate validation, and publication all operate
under `ROOT`. A future main commit beyond the pinned release reproduces the
architectural coupling. An immutable executor and mutable task content have
distinct freshness, trust and review requirements.

## Why it matters

Stale workbase errors can corrupt cumulative IDs, undo newer content and
waste cost-bearing model execution. Passing offline contract/SIM or an
authentication/readiness gate does not establish content provenance or
concurrent-branch safety. Reliability requires *both* trusted policy identity
and task-workbase currency before paying for implementation.

## Related defect(s)

- Canonical [DEF-0125](../defects/defect-ledger.csv): this stale baseline
  coupling, high severity and still investigating
- [DEF-0119](../defects/defect-ledger.csv): narrower consulting-path validator
  false rejection, already resolved
- [Organization issue #111](https://github.com/Young-Consultations/.github/issues/111):
  separate terminal-result replay / cost-bearing guard, released 3.1.0 but
  without new REAL acceptance

## Evidence

- [Production failure run](https://github.com/Young-Consultations/consulting-playbook/actions/runs/38996859486)
  and [source issue](https://github.com/Young-Consultations/portfolio-tasks/issues/167)
- `.github/workflows/codex-execute.yml` single checkout on the immutable
  target adapter
- `scripts/codex_target_adapter.py`: `GitHubEffects.codex` uses `-C ROOT`;
  `has_candidate_changes`, `validate_candidate` and `publish` also use
  `ROOT`
- [Issue #93](https://github.com/Young-Consultations/consulting-playbook/issues/93)
  for the stale DEF/CONTENT ID examples and independent scope

## What implementation or testing exposed

The trusted release identity was functioning as designed. The flaw was the
unjustified implication that trusted executable commit also represented the
current desired task-content base. The failed E2E validation correctly stopped
the draft, but detected the stale candidate **after** a paid model call.

## Requirement or architecture implications

**Approved design.** The architecture in
[`docs/architecture/proposals/issue-93-dual-baseline-executor.md`](../../docs/architecture/proposals/issue-93-dual-baseline-executor.md)
separates immutable trusted executable root from a read-verified exact-SHA
content checkout, validates draft provenance and denies publication if the
default branch moved. The owner has approved a separate trusted executor and content workbase.
A Codex P1 review corrected the initial impossible claim of atomic
default-branch freeze: stale branches are quarantined as partial effects,
and a moving HEAD cannot guarantee zero transient refs. Normative requirements,
interface and ADR-013 are updated in this PR; runtime acceptance is pending.

## Lessons learned

Release compatibility and repository content freshness are orthogonal.
Pre-execution validation must include the cost-bearing model's actual **work
baseline**, not just credentials, result delivery and immutable code. Distinct
worktrees need distinct trust models; treating all checks as one green status
can create false confidence.

## `AI_CONTEXT.md` impact

Not updated in this decision PR. The owner-approved normative requirements
and ADR-013 are being reviewed; update AI_CONTEXT only once that authority
merges, and distinguish approved design from unimplemented runtime behavior.

## Follow-up

After reviewed owner-approved architecture merges, implement in a separate
reviewed draft PR, with fake-Codex/fake-publisher tests for stale base and
moved-head races. Require immutable target release, exact registry/report
digest, compatible control-plane adoption and post-deployment verification.
Do **not** rerun terminal source #167 or pay for fresh REAL until issue #93's
repair passes applicable governance gates.

## Potential consulting or content value

The case illustrates a general AI-SDLC design risk: *immutable execution
policy is not the same thing as an accurate problem snapshot*. Evidence for
both must be checked, independently, before expensive API execution.
