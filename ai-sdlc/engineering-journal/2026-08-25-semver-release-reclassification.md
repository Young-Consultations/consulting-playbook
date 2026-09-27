# 2026-08-25 — Receiver correction required a MINOR release, not PATCH

- **Date:** 2026-08-25
- **Decision status:** resolved
- **SDLC phase:** acceptance-review

## Context

The receiver retry correction changed an observable accepted result transition
without changing the closed v2 payload schemas.

## Discovery

The candidate was initially prepared as `2.3.3` PATCH. The repository release
policy states that PATCH releases must not change accepted interface or
observable policy, while backward-compatible added behavior belongs in MINOR.

## Why it matters

Immutable release identity communicates compatibility expectations. Publishing a
behavioral policy change under the wrong SemVer category would make release
metadata contradict the repository's own governance rules.

## Related defect(s)

- DEF-0059
- Historical proposed ID: DEF-0034 in consulting-playbook issue #39

## Evidence

- [consulting-playbook issue #39](https://github.com/Young-Consultations/consulting-playbook/issues/39)
- [Young-Consultations/.github PR #54](https://github.com/Young-Consultations/.github/pull/54)
- [authoritative release policy](https://github.com/Young-Consultations/.github/blob/main/docs/releases.md)
- [Contract Tests run 32905851061](https://github.com/Young-Consultations/.github/actions/runs/32905851061)
- [merge commit `df0ca3f...`](https://github.com/Young-Consultations/.github/commit/df0ca3f66d16223412f190fef36e03acbad5f22b)

## What implementation or testing exposed

Review reconciled the behavioral change with the release policy before
publication. PR #54 reclassified the candidate as `2.4.0` and updated the
manifest, package version, receiver self-pin, tests, acceptance design,
interface/release documentation, and AI context consistently.

## Requirement or architecture implications

The release policy itself did not change. The candidate was corrected to comply
with the already-authoritative SemVer decision.

## Lessons learned

Release classification is part of implementation readiness. A change can be
schema-compatible yet still require a MINOR release because observable policy
changed.

## `AI_CONTEXT.md` impact

Required and completed in .github PR #54 after the release/interface decision
was resolved.

## Follow-up

Resolved. Preserve behavioral compatibility review as part of immutable release
preparation.

## Potential consulting or content value

Useful example of requirements/governance review catching a release defect
before any code-level failure occurred.
