# Engineering Journal: control-plane release tag policy drift

**Date:** 2026-09-26  
**Defect:** DEF-0052  
**Affected repository:** `Young-Consultations/.github`  
**Detection:** automated PR review followed by cross-release audit

## What happened

Publication-attestation PR #79 recorded `ai-sdlc-v2.4.5` at reviewed candidate
merge commit `afe09d320268581bc83021cbfc80bf2a0f0bff91`. Copilot review observed
that the tag is lightweight while `docs/releases.md` said the controlled
release procedure required an annotated tag.

The first response treated that as a release-policy violation and added
annotated-only enforcement to lifecycle tests, target compatibility, and
Runtime Preflight.

A cross-release inspection then showed that `ai-sdlc-v2.4.0` through
`ai-sdlc-v2.4.5` are all lightweight tags. The authoritative software
requirement for the atomic release unit requires an immutable published identity
and tag-integrity evidence, but does not require an annotated Git tag object.

The release owner clarified that annotated tags are not required.

## Actual defect

The defect was not the 2.4.5 tag. The defect was release-procedure
documentation that had become more restrictive than the approved requirement
and established release mechanism.

The procedure introduced an untraced implementation detail, "annotated tag",
and review correctly detected the textual contradiction. Because that detail
was not backed by an approved requirement or ADR, enforcing it would have
created unnecessary release work and encouraged rewriting an otherwise correct
immutable release identity.

## Resolution

PR #79 now defines the control-plane release policy explicitly:

- the release tag name is immutable after publication;
- the tag must independently resolve to the exact reviewed candidate merge
  commit recorded in the manifest/runtime evidence;
- lightweight and annotated Git tags are both acceptable;
- no published tag may be moved, deleted, or recreated as part of normal
  release handling.

The temporary annotated-only enforcement added during investigation was
removed. Existing commit-identity checks remain in the release lifecycle,
release-aware compatibility verifier, and Runtime Preflight.

`ai-sdlc-v2.4.5` is intentionally left unchanged at
`afe09d320268581bc83021cbfc80bf2a0f0bff91`.

## SDLC learning

Documentation can create false requirements just as code can violate real
requirements. A procedural rule should not become an executable gate unless it
traces to an approved requirement, architecture decision, security boundary, or
explicit owner decision.

When review identifies a contradiction, compare the requirement hierarchy,
historical implementation, and release evidence before turning the review
comment into new enforcement. The useful invariant here is immutable exact
commit identity, not Git tag object type.

## Closure

DEF-0052 was resolved on 2026-09-26 when .github PR #79 merged at
`75815fdc83ebd28f53e483b6de71e0107e74356f`. Before merge, exact-head AI-SDLC
Contract Tests, Target Compatibility, and TC-MVP-E2E-001 all passed with the
clarified lightweight-or-annotated tag policy and exact commit-identity checks.
