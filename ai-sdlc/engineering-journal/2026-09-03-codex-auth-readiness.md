# 2026-09-03 — Codex authentication readiness

- **Date:** 2026-09-03
- **Decision status:** unresolved
- **SDLC phase:** release-production

## Context

The target adapter's ordinary conformance suite intentionally uses fakes, makes
no Codex request, and requires no provider credential. The protected
`consulting-playbook-codex` environment supplied `OPENAI_API_KEY` during the
first live approved deliveries.

## Discovery

A non-empty environment secret did not establish provider acceptance. The live
Codex client exhausted its retries with `401 Unauthorized`; no repository
change, validation run, branch, or draft pull request followed. The successful
GitHub Actions transport and offline conformance checks answered different
questions and could not establish runtime authentication readiness.

## Why it matters

A failed approved delivery consumes a governed task and delivery identity and
creates reconciliation work even when it makes no repository change. Testing
credential readiness before that delivery reduces avoidable failure while
preserving the rule that ordinary conformance stays deterministic and offline.

## Related defect(s)

- `DEF-0034`

## Evidence

- [Issue #139](https://github.com/Young-Consultations/portfolio-tasks/issues/139)
- [Retry issue #144](https://github.com/Young-Consultations/portfolio-tasks/issues/144)
- [Failed live Codex job](https://github.com/Young-Consultations/consulting-playbook/actions/runs/33712638274/job/100522985041)

## What implementation or testing exposed

The target workflow proved that the secret reference resolved, but the first
provider-backed operation proved that the credential was not accepted. Existing
fake tests correctly established contract, policy, idempotency, and no-effect
behavior; they were never evidence of external provider authentication.

## Requirement or architecture implications

No new product requirement or cross-repository interface is needed. Existing
NFR-OBS-01/02, NFR-TST-02, UC-10, and the Security, Configuration, Error
Handling, and Observability architecture already require isolated secrets,
dependency authentication health, sanitized categories, and controlled
verification. A separate manual workflow is an operational verification aid;
it is not a second execution interface or an activation switch.

## Lessons learned

- Secret presence, credential syntax, provider authentication, account quota,
  model authorization, and network reachability are distinct checks.
- Offline conformance and live dependency readiness should remain separate and
  be labeled by the claim each can support.
- A safe preflight must use the production client and protected environment but
  omit repository checkout, publication credentials, and automatic triggers.
- Provider output should be reduced to stable categories rather than copied
  into durable logs or task records.

## `AI_CONTEXT.md` impact

No change is required. It already states that credentials are unconfirmed and
forbids production-readiness claims from local evidence. Update that statement
only after merged, controlled evidence supports a narrower claim.

## Follow-up

1. Review and merge the manual preflight workflow.
2. Run it through the protected environment after restoring the credential.
3. Close `DEF-0034` only when a controlled run passes; retain the run as
   time-specific readiness evidence.
4. Create and approve a new delivery identity for any later implementation
   retry; do not reuse a terminal failed delivery.

## Potential consulting or content value

This is a reusable example of why configuration presence, simulated contract
tests, transport success, and live dependency readiness must be reported as
different evidence rather than collapsed into one green status.
