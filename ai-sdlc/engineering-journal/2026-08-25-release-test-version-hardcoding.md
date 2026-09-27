# 2026-08-25 — Compatibility tests became a second release authority

- **Date:** 2026-08-25
- **Decision status:** resolved
- **SDLC phase:** integration-verification

## Context

During .github PR #54, the receiver candidate advanced beyond the published
2.3.2 identity.

## Discovery

Compatibility tests still hard-coded `ai-sdlc-v2.3.2`. They rejected the
valid candidate self-pin before exercising the intended behavior, and the
immutability mutation test attempted to replace a version string no longer
present.

## Why it matters

Tests should enforce the authoritative release manifest, not independently
define release identity. Hard-coded expected versions make executable
verification a competing source of truth and create avoidable release-candidate
failures.

## Related defect(s)

- DEF-0058
- Historical proposed ID: DEF-0033 in consulting-playbook issue #38

## Evidence

- consulting-playbook issue #38
- Young-Consultations/.github PR #54
- failing run 32878019201
- succeeding Contract Tests run 32905851061
- merge commit `df0ca3f66d16223412f190fef36e03acbad5f22b`

## What implementation or testing exposed

PR #54 changed the tests to derive the expected receiver release from
`release/release-manifest.json`. The negative immutability test now mutates the
derived tag to `@main`, so the security assertion survives future release
versions without embedding a second release identifier.

## Requirement or architecture implications

No requirement or architecture change was needed. The implementation was
brought back into conformance with the existing manifest-authority model.

## Lessons learned

Executable tests can drift into policy ownership when constants duplicate
authoritative configuration. Prefer assertions derived from the governing
artifact, with negative tests mutating the derived value.

## `AI_CONTEXT.md` impact

None required.

## Follow-up

Resolved. Continue treating the release manifest as the single release identity
authority.

## Potential consulting or content value

A compact example of verification becoming the defect-bearing artifact.
