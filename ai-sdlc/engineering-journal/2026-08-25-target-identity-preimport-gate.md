# 2026-08-25 — Immutable target identity must gate code loading

- **Date:** 2026-08-25
- **Decision status:** resolved
- **SDLC phase:** acceptance-review

## Context

The E2E SIM dynamically checked out the registry-selected target adapter and
validated its immutable identity before execution.

## Discovery

The initial harness collected an identity mismatch error but continued into
`_load_target_adapter()`, allowing module-level code from the mismatched
checkout to execute before the run eventually failed. `git rev-parse` errors
could also escape instead of becoming controlled fail-closed evidence.

## Why it matters

Identity validation is not a security boundary unless it gates trust escalation.
Loading code before the identity decision means unverified content executes
inside the harness even though the final status is failure.

## Related defect(s)

- DEF-0061
- Historical proposed ID: DEF-0036 in consulting-playbook issue #41

## Evidence

- [consulting-playbook issue #41](https://github.com/Young-Consultations/consulting-playbook/issues/41)
- [Young-Consultations/.github PR #54](https://github.com/Young-Consultations/.github/pull/54)
- [TC-MVP-E2E-001 Acceptance run 32905851105](https://github.com/Young-Consultations/.github/actions/runs/32905851105)
- [merge commit `df0ca3f...`](https://github.com/Young-Consultations/.github/commit/df0ca3f66d16223412f190fef36e03acbad5f22b)

## What implementation or testing exposed

PR #54 made identity validation catch Git/process errors, stop before adapter
import on any identity failure, and added tests that prove the loader is not
called after missing, unreadable, or mismatched identity. REAL preflight also
binds execution to the immutable published control-plane tag commit.

## Requirement or architecture implications

Existing fail-closed and immutable-adapter requirements were sufficient. The
implementation was corrected to enforce them at the proper pre-import boundary.

## Lessons learned

“Validate then continue” is not fail-closed. Security-relevant validation must
control the next trust transition, especially before importing executable code.

## `AI_CONTEXT.md` impact

None required beyond already merged control-plane guidance.

## Follow-up

Resolved. Keep negative tests that assert the adapter loader is never called
after identity failure.

## Potential consulting or content value

Useful security-review example: evidence collection and enforcement are
different responsibilities even when they inspect the same identity.
