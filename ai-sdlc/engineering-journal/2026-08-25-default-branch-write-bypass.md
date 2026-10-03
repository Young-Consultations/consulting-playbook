# 2026-08-25 — Default-branch write bypassed review change control

- **Date:** 2026-08-25
- **Decision status:** resolved — live fail-closed prevention verified 2026-10-03
- **SDLC phase:** implementation
- **Decision owner:** Young-Consultations repository owner / maintainer
- **Tracking:** [Young-Consultations/.github #80](https://github.com/Young-Consultations/.github/issues/80)

## Context

While implementing portfolio-tasks #119, a GitHub connector file-write call was
issued without an explicit branch. The repository workflow expected
implementation changes to occur on a feature branch and reach `main` only
through pull-request review.

## Discovery

The connector committed directly to the portfolio-tasks default branch.
Commit `1e13cedebaadf992564578325149fa444142a925` introduced the unintended
content, `170edce0e536b6f8cca76242eb84c1c0087aae82` removed it, and
`d2b072dbca93a588e1dcc3a1428ec3313a675e17` was produced while verifying
recovery. The intended #119 work was subsequently performed on a feature branch
and reviewed through Young-Consultations/.github PR #54.

## Why it matters

A tool invocation error could bypass the review boundary even when the intended
SDLC requires branch → PR → review → merge. Content recovery does not prove the
governance control is fixed because the repository/tool boundary still needs an
evidence-backed fail-closed prevention rule.

## Related defect(s)

- DEF-0056
- Historical proposed ID: DEF-0031 in consulting-playbook issue #36

## Evidence

- [consulting-playbook issue #36](https://github.com/Young-Consultations/consulting-playbook/issues/36)
- [portfolio-tasks #119](https://github.com/Young-Consultations/portfolio-tasks/issues/119)
- direct-main commits [`1e13ced...`](https://github.com/Young-Consultations/portfolio-tasks/commit/1e13cedebaadf992564578325149fa444142a925), [`170edce...`](https://github.com/Young-Consultations/portfolio-tasks/commit/170edce0e536b6f8cca76242eb84c1c0087aae82), and [`d2b072d...`](https://github.com/Young-Consultations/portfolio-tasks/commit/d2b072dbca93a588e1dcc3a1428ec3313a675e17)
- [Young-Consultations/.github PR #54](https://github.com/Young-Consultations/.github/pull/54) for the intended implementation path
- [tracking issue Young-Consultations/.github #80](https://github.com/Young-Consultations/.github/issues/80)

## What implementation or testing exposed

The file-write tool accepted an omitted branch scope and selected the default
branch rather than rejecting the mutation. Immediate tool-result review exposed
the discrepancy before additional implementation depended on the unintended
content.

## Requirement or architecture implications

The prevention decision is now resolved by ADR-018 in Young-Consultations/.github.
The authoritative mutation boundary is an active GitHub branch ruleset on every
core AI-SDLC repository targeting the default branch, with no bypass actors,
a required-pull-request rule, review-thread resolution, deletion protection,
and non-fast-forward protection. Repository-local prompts and tool conventions
remain defense-in-depth only; they are not the authoritative fail-closed control.

The implementation and verifier landed in .github PR #110 at merge commit
`45320ce266968234335bb2fe35dd58e86ae142d5`.

## Lessons learned

A process convention is weaker than an enforced mutation boundary. AI-assisted
repository tools need explicit destination identity before write effects, and
defaulting a missing branch is unsafe for governed implementation work.

## `AI_CONTEXT.md` impact

No additional AI_CONTEXT change is required for this resolution. The current
control-plane AI_CONTEXT already states that automation must not push directly
to a protected default branch. ADR-018 and the default-branch governance
document own the durable mechanism; live GitHub settings remain mutable
external configuration and should not be duplicated as a snapshot in AI context.

## Resolution evidence

The prevention control is complete.

- .github PR #110 implemented ADR-018, the machine-readable policy, fail-closed
  audit, regression tests, and manual evidence workflow.
- Default Branch Governance Audit run
  [37134811435](https://github.com/Young-Consultations/.github/actions/runs/37134811435)
  checked merged commit `45320ce266968234335bb2fe35dd58e86ae142d5`.
- The audit passed 12/12 governance regression tests and returned
  `compliant: true` with no errors for `.github`, `portfolio-tasks`,
  `consulting-playbook`, and `slugger`.
- Independent GitHub API verification on 2026-10-03 confirmed all four
  repositories have an active `Default branch change control` ruleset with
  `~DEFAULT_BRANCH`, no exclusions, no bypass actors, deletion protection,
  non-fast-forward protection, and a required-pull-request rule requiring
  review-thread resolution.

DEF-0056 may therefore be closed as resolved. The historical direct-main
commits remain durable incident evidence, but the same omitted/default-branch
implementation write now fails at GitHub's mutation boundary instead of relying
on agent behavior.

## Potential consulting or content value

Strong example of a governance defect where the code change was harmless but
the automation authority boundary was not.
