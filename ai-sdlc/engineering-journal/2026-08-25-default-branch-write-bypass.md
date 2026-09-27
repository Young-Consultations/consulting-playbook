# 2026-08-25 — Default-branch write bypassed review change control

- **Date:** 2026-08-25
- **Decision status:** unresolved — incident reverted; prevention control still open
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

The Young-Consultations repository owner / maintainer is the accountable decision owner for [tracking issue #80](https://github.com/Young-Consultations/.github/issues/80) and must decide the durable prevention
boundary: repository ruleset/branch protection, connector/tool guard, mandatory
pre-write branch validation, or a combination. Until that decision is made,
this journal does not promote a proposed mechanism to authoritative policy.

## Lessons learned

A process convention is weaker than an enforced mutation boundary. AI-assisted
repository tools need explicit destination identity before write effects, and
defaulting a missing branch is unsafe for governed implementation work.

## `AI_CONTEXT.md` impact

Unresolved. Do not add a speculative control to AI context until the
requirement/architecture decision is approved and implemented.

## Follow-up

Keep DEF-0056 open and track the decision/implementation in [Young-Consultations/.github #80](https://github.com/Young-Consultations/.github/issues/80). Select and implement the authoritative fail-closed control,
add executable evidence that omitted/default-branch implementation writes are
blocked, and then determine whether repository AI context requires an update.

## Potential consulting or content value

Strong example of a governance defect where the code change was harmless but
the automation authority boundary was not.
