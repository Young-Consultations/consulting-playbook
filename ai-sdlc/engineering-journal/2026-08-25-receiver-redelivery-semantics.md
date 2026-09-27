# 2026-08-25 — Receiver retry semantics contradicted target redelivery

- **Date:** 2026-08-25
- **Decision status:** resolved
- **SDLC phase:** integration-verification

## Context

TC-MVP-E2E-001 SIM was changed to exercise the real organization result receiver
rather than a simplified receiver test double.

## Discovery

The target correctly produced `draft-pr-created` on first successful delivery
and `duplicate-reused` when the same managed draft was found on redelivery.
The receiver, however, rejected every non-identical second result digest for a
delivery as ambiguous. Correct producer and consumer behavior could therefore
not compose.

## Why it matters

Retry/idempotency semantics live at an interface boundary. A simplified test
double had hidden a contradiction that would have rejected a valid target
redelivery and undermined REAL retry evidence.

## Related defect(s)

- DEF-0057
- Historical proposed ID: DEF-0032 in consulting-playbook issue #37

## Evidence

- [consulting-playbook issue #37](https://github.com/Young-Consultations/consulting-playbook/issues/37)
- [portfolio-tasks #119](https://github.com/Young-Consultations/portfolio-tasks/issues/119)
- [Young-Consultations/.github PR #54](https://github.com/Young-Consultations/.github/pull/54)
- [TC-MVP-E2E-001 Acceptance run 32905851105](https://github.com/Young-Consultations/.github/actions/runs/32905851105)
- [merge commit `df0ca3f...`](https://github.com/Young-Consultations/.github/commit/df0ca3f66d16223412f190fef36e03acbad5f22b)

## What implementation or testing exposed

Using the actual receiver path showed that canonical-result identity and
visible-effect identity are related but not identical. PR #54 refined the
contract so identical replay remains a no-op and
`draft-pr-created -> duplicate-reused` is accepted only for the same delivery,
target, correlation, managed branch/PR, validation result, test result, and
failure category. No second source projection is emitted.

## Requirement or architecture implications

The interface contract was corrected in .github PR #54. Every other
non-identical result remains ambiguous and fails closed. No target-local
alternative receiver semantics are permitted.

## Lessons learned

Test doubles that simplify stateful interfaces can erase the very retry
semantics an end-to-end test is meant to validate. The real contract
implementation should be exercised whenever deterministic effect seams allow it.

## `AI_CONTEXT.md` impact

The control-plane context was reconciled in PR #54. No additional
consulting-playbook AI context change is required by this recovery entry.

## Follow-up

Resolved. Preserve the refined receiver semantics in compatibility tests and
future REAL redelivery exercises.

## Potential consulting or content value

Useful example of an interface/specification defect found only after replacing a
friendly test double with the real integration boundary.
