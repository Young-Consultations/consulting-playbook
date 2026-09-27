# 2026-08-25 — E2E SIM bypassed the router path it claimed to prove

- **Date:** 2026-08-25
- **Decision status:** resolved
- **SDLC phase:** acceptance-review

## Context

TC-MVP-E2E-001 SIM was intended to share orchestration semantics with REAL and
replace only explicit provider/external effects with deterministic fakes.

## Discovery

The first SIM implementation constructed an execution input directly from a
checked-in example and invoked the target adapter. It bypassed production router
task admission, activation/registry checks, target selection, concurrency
construction, and canonical execution-input construction.

## Why it matters

A green end-to-end label is misleading if the harness skips a major production
boundary. The test could have certified target behavior while leaving the
production admission/routing path untested.

## Related defect(s)

- DEF-0060
- Historical proposed ID: DEF-0035 in consulting-playbook issue #40

## Evidence

- consulting-playbook issue #40
- portfolio-tasks #119
- Young-Consultations/.github PR #54
- TC-MVP-E2E-001 Acceptance run 32905851105
- merge commit `df0ca3f66d16223412f190fef36e03acbad5f22b`

## What implementation or testing exposed

PR #54 made SIM start from canonical `valid-task.json`, execute production
`codex_router.validate()`, registry/activation selection, target/workflow
selection, and execution-input construction, then cross only a deterministic
fake dispatch/provider boundary. Evidence records `shared_router_path: true`.

## Requirement or architecture implications

No architecture change was required. The acceptance implementation was brought
back into conformance with the already-approved single-orchestration design.

## Lessons learned

Simulation fidelity should be defined by preserved architecture, not by how much
code executes. Fake external effects are compatible with high-fidelity SIM;
bypassing internal production boundaries is not.

## `AI_CONTEXT.md` impact

No additional update required beyond the merged .github acceptance-path context.

## Follow-up

Resolved. Future SIM changes must prove shared production routing before they can
contribute acceptance evidence.

## Potential consulting or content value

Strong case study for “green test, wrong system”: verification can be internally
correct while proving a materially different path.
