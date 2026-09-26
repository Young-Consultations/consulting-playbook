# 2026-09-26 — Control-plane release tag policy drift

- **Date:** 2026-09-26
- **Decision status:** resolved
- **Decision owner:** release owner / repository maintainer
- **SDLC phase:** acceptance-review

## Context

Publication-attestation PR Young-Consultations/.github#79 recorded
`ai-sdlc-v2.4.5` at reviewed candidate commit
`afe09d320268581bc83021cbfc80bf2a0f0bff91`. Automated review observed that
the tag is lightweight while `docs/releases.md` said the controlled release
procedure required an annotated tag.

The first repair response treated that wording as authoritative and added
annotated-only enforcement to lifecycle tests, target compatibility, and
Runtime Preflight.

## Discovery

Cross-release inspection showed that `ai-sdlc-v2.4.0` through
`ai-sdlc-v2.4.5` are all lightweight tags. Review of the authoritative
release requirements showed that they require an immutable published identity
and exact tag-to-commit integrity, but do not require an annotated Git tag
object.

The release owner resolved the discrepancy by confirming that annotated tags
are not required. Lightweight and annotated tags are both acceptable when the
published tag name is immutable and independently resolves to the exact
reviewed commit recorded in release evidence.

## Why it matters

Treating an untraced procedural detail as a requirement would have blocked a
valid release and encouraged rewriting an otherwise correct immutable release
identity. The useful invariant is exact immutable commit identity, not Git tag
object representation.

## Related defect(s)

- DEF-0052 — Release procedure over-specified annotated tags contrary to
  established immutable-tag policy.

## Evidence

- Young-Consultations/.github PR #79:
  https://github.com/Young-Consultations/.github/pull/79
- Review discussion:
  https://github.com/Young-Consultations/.github/pull/79#discussion_r4112913500
- GitHub ref inspection confirmed `ai-sdlc-v2.4.0` through
  `ai-sdlc-v2.4.5` resolve as lightweight refs.
- GH-FR-014 requires an immutable compatibility unit and tag-integrity evidence
  but does not require an annotated tag object.
- PR #79 merged at
  `75815fdc83ebd28f53e483b6de71e0107e74356f` after exact-head Contract Tests,
  Target Compatibility, and TC-MVP-E2E-001 passed.

## What implementation or testing exposed

The initial PR #79 repair added checks that deliberately failed when GitHub
reported the release ref object type as `commit`. Those failures proved the
new checks enforced the written procedure, but the cross-release audit showed
that the written procedure itself was the defective artifact.

PR #79 then removed the temporary annotated-only checks while retaining exact
tag-to-commit verification. The existing `ai-sdlc-v2.4.5` tag was not moved,
deleted, or recreated.

## Requirement or architecture implications

No new architecture decision was required. The approved release invariant is:

- publish one immutable `ai-sdlc-vX.Y.Z` tag at the reviewed candidate commit;
- independently resolve the tag to the exact commit recorded in the release
  manifest/runtime evidence;
- do not move, delete, or recreate a published tag during normal release
  handling;
- permit either lightweight or annotated Git tag representation.

PR #79 reconciled `docs/releases.md` with that decision.

## Lessons learned

Documentation can create false requirements just as implementation can violate
real requirements. A procedural rule should not become an executable gate
unless it traces to an approved requirement, architecture decision, security
boundary, or explicit owner decision.

When review identifies a contradiction, compare the authority hierarchy,
historical implementation, and release evidence before converting the review
comment into new enforcement.

## `AI_CONTEXT.md` impact

Required and completed in Young-Consultations/.github PR #79. The context now
states the resolved lightweight-or-annotated policy and preserves exact
commit-identity verification. No unresolved tag-policy speculation should be
added to repository context.

## Follow-up

DEF-0052 is resolved. Its origin phase and escape distance remain blank in the
ledger because the phase in which the unsupported annotated-tag wording was
originally authored or approved has not been established from evidence.

The separate organization-level cost-bearing executor prerequisite policy
remains owned by Young-Consultations/.github issue #77.

## Potential consulting or content value

Useful as an example of requirements traceability applying to governance
documentation itself: an executable check can be internally consistent and
still enforce the wrong requirement.
