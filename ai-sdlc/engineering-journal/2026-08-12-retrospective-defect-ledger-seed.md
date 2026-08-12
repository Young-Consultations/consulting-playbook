# 2026-08-12 — Retrospective defect-ledger seed

- **Date:** 2026-08-12
- **Decision status:** resolved
- **SDLC phase:** retrospective

## Context

The new AI-SDLC Defect Ledger was empty, while recent project work already contained evidence-backed discrepancies across routing, idempotency, repository ownership, immutable interfaces, secrets, shared conformance assets, and CI.

## Discovery

A retrospective audit found eleven defensible historical/current defects. The audit also found one current defect in consulting-playbook: `AI_CONTEXT.md` still describes the pre-issue-#114 fail-closed target workflow even though the latest snapshot contains the implemented canonical adapter.

Issue #114 and Portfolio Tasks PR #39 are related to the same broader target-hardening history but are not the same implementation event: PR #39 was merged on 2026-07-28, while issue #114 was created on 2026-08-09. They should remain separately traceable.

## Why it matters

Without retrospective seeding, metrics would start from zero and erase the defects that motivated the current architecture. Preserving evidence also prevents later AI agents from treating resolved lessons as speculation.

## Related defect(s)

DEF-0001 through DEF-0011

## Evidence

- https://github.com/Young-Consultations/portfolio-tasks/issues/55
- https://github.com/Young-Consultations/portfolio-tasks/issues/74
- https://github.com/Young-Consultations/portfolio-tasks/issues/75
- https://github.com/Young-Consultations/portfolio-tasks/issues/76
- https://github.com/Young-Consultations/portfolio-tasks/issues/77
- https://github.com/Young-Consultations/portfolio-tasks/issues/112
- https://github.com/Young-Consultations/portfolio-tasks/issues/113
- https://github.com/Young-Consultations/portfolio-tasks/issues/114
- https://github.com/Young-Consultations/portfolio-tasks/pull/39
- Latest consulting-playbook snapshot, `AI_CONTEXT.md` and `.github/workflows/codex-execute.yml`

## What implementation or testing exposed

The project repeatedly exposed defects downstream of code generation: event semantics, replay ownership, contract release discipline, workflow credential boundaries, shared test-oracle completeness, and context/documentation reconciliation.

## Requirement or architecture implications

The current single-active-contract, immutable-compatibility/mutable-activation, bounded-repository-authority architecture already captures most resolved decisions. The current required correction is to reconcile consulting-playbook `AI_CONTEXT.md` with the completed #114 adapter.

## Lessons learned

The defect ledger should be updated at discovery time, not reconstructed later. Failed workflows and code-review investigations should default to defect investigation, with a row created only when evidence confirms a discrepancy.

## `AI_CONTEXT.md` impact

`Young-Consultations/consulting-playbook/AI_CONTEXT.md` was reconciled with the confirmed #114 implementation state. The update preserves the separate, externally owned mutable activation boundary and adds no unresolved speculation.

## Follow-up

1. Continue seeding only where a concrete issue, PR, workflow, file, or project artifact proves a discrepancy.
2. Add measured rework hours later if reliable timestamps or work logs are available; do not backfill invented estimates.

## Potential consulting or content value

The historical set strongly supports the consulting thesis that AI-native delivery bottlenecks move upstream and downstream of code generation: requirements/authority, interfaces, verification, security boundaries, and reconciliation become the dominant sources of rework.
