# 2026-07-28 — PR #39 CI hardening exposed validation gaps

- **Date:** 2026-07-28
- **Decision status:** resolved
- **SDLC phase:** integration-verification

## Context

Portfolio Tasks PR #39 hardened the canonical target workflow, pinned third-party actions, added actionlint, and added compatibility/security checks.

## Discovery

The hardening PR itself exposed three distinct defects: mandatory actionlint initially failed because of ShellCheck interaction, an issue-sync checkout still persisted credentials, and the newly enforced Ruff gate found code that violated the active lint rules.

## Why it matters

The sequence is a useful AI-SDLC example: adding stronger verification can surface defects in both the product/workflow and in the verification change itself. A local success claim is weaker than reproducing the exact CI environment and final branch state.

## Related defect(s)

DEF-0008, DEF-0009, DEF-0010

## Evidence

- https://github.com/Young-Consultations/portfolio-tasks/pull/39
- PR review discussion and CI log on 2026-07-28
- Follow-up commits `346552b` and `948a250`

## What implementation or testing exposed

GitHub-hosted CI and PR review exposed behavior that the authoring environment could not reproduce because external tool installation was blocked. The exact hosted-runner checks therefore became essential evidence.

## Requirement or architecture implications

No new architecture decision is required. CI-equivalent validation instructions should explicitly distinguish checks actually executed from checks deferred to hosted CI, and security invariants such as checkout credential persistence should be repository-wide assertions.

## Lessons learned

A verification gate should be treated as production code: prove the gate itself, pin its behavior, and add regression tests for the invariant it is meant to enforce.

## `AI_CONTEXT.md` impact

No unresolved architectural correction is required from these three historical defects. Keep the general rule that CI-equivalent checks and least-privilege workflow constraints are mandatory.

## Follow-up

Use this incident as a case-study candidate for verification-induced defect discovery and AI-assisted CI repair loops.

## Potential consulting or content value

Strong candidate for a post on why AI code-generation speed shifts the bottleneck toward deterministic verification, environment parity, and evidence quality.
