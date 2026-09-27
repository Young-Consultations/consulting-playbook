# 2026-08-27 — Duplicated approval state created two human approval actions

- **Date:** 2026-08-27
- **Decision status:** resolved — simplified path live-verified on 2026-09-26
- **SDLC phase:** release-production

## Context

The first real production-path portfolio test used an authorized human approval
label to route an exact issue revision.

## Discovery

Admission required both the `status:approved` label and an issue-body
`Execution status` field set to `approved`. A valid authorized label approval
therefore failed solely because the human had not performed a second body edit.
The duplicate representations could disagree and the body edit also interacted
poorly with edit-triggered approval revocation.

## Why it matters

Security controls should make authority explicit without multiplying mutable
representations of the same decision. Duplicate approval state increases
operator work and creates inconsistent lifecycle combinations without adding
independent assurance.

## Related defect(s)

- DEF-0062
- portfolio-tasks issue #141

## Evidence

- [portfolio-tasks issue #141](https://github.com/Young-Consultations/portfolio-tasks/issues/141)
- [portfolio-tasks PR #142](https://github.com/Young-Consultations/portfolio-tasks/pull/142), merge commit [`278fa1b...`](https://github.com/Young-Consultations/portfolio-tasks/commit/278fa1baa47900a58a51368b1c370f01d36a45c8)
- [fresh portfolio issue #154](https://github.com/Young-Consultations/portfolio-tasks/issues/154) approved with the single label action
- [target run 36279165335](https://github.com/Young-Consultations/consulting-playbook/actions/runs/36279165335) and resulting [consulting-playbook PR #66](https://github.com/Young-Consultations/consulting-playbook/pull/66)
- PR #66 merge commit [`6d3d969...`](https://github.com/Young-Consultations/consulting-playbook/commit/6d3d9694057e787eab74ae45999ad73c804c6067)

## What implementation or testing exposed

PR #142 removed the issue-form execution-status field, made
`status:approved` the single human approval action, bound approval to the
latest authorized label event and exact material revision, retained current
issue reread/stale-event checks, and preserved edit revocation. The later 2.4.5
REAL issue #154 exercised that path successfully without a duplicate body-state
edit.

## Requirement or architecture implications

The source repository now has one human approval source of truth for v2:
authorized application of `status:approved` to the exact current revision.
Task construction still derives canonical `status: approved` only after the
event/revision authority checks pass. No second approval path was added.

## Lessons learned

Redundant representations are not automatically defense in depth. When two
fields represent the same authority decision, they can become conflicting state
rather than independent controls.

## `AI_CONTEXT.md` impact

Required and completed in portfolio-tasks PR #142. The repository context now
describes label-based approval, revision binding, and edit invalidation as one
coherent boundary.

## Follow-up

Resolved and live-verified. Keep the single-action approval tests and avoid
reintroducing a second mutable approval field.

## Potential consulting or content value

Strong example of simplifying a governance control while preserving or
increasing assurance by binding one authority decision to immutable material
identity.
