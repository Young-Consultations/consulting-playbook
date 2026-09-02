# 2026-09-02 — Semantic validation at versioned JSON boundaries

- **Date:** 2026-09-02
- **Decision status:** resolved
- **SDLC phase:** release-production

## Context

The first controlled REAL path used the published `ai-sdlc-v2.4.1` control plane to route portfolio issue [#139](https://github.com/Young-Consultations/portfolio-tasks/issues/139) through `Young-Consultations/consulting-playbook` and return its canonical result. The control-plane admission journal enriched the stable v2 binding with `activation_revision`, `activation_sha256`, and `control_plane_release` evidence.

## Discovery

The source projection rebuilt only the five stable admission-binding fields and searched all issue comments for that serialized object as a literal substring. Because canonical JSON sorting placed the new activation fields before `contract_version`, the valid enriched marker could never contain the reconstructed five-field serialization. [Run 33637803492, job 100411953201](https://github.com/Young-Consultations/portfolio-tasks/actions/runs/33637803492/job/100411953201) therefore authenticated the receiver and validated the result, but failed while applying the result and added the quarantine state.

## Why it matters

The failure was safe—it failed closed—but it blocked valid portfolio state projection. More importantly, it exposed representation coupling across a versioned repository boundary: the consumer depended on byte arrangement rather than the semantic fields it owned. Additive audit evidence should not invalidate a stable binding unless the authoritative contract declares the complete marker closed.

## Related defect(s)

DEF-0033 — Result projection rejected release-enriched admission marker.

## Evidence

- [Issue #139](https://github.com/Young-Consultations/portfolio-tasks/issues/139), especially admission comment `5503021140`
- [Failed source-projection job](https://github.com/Young-Consultations/portfolio-tasks/actions/runs/33637803492/job/100411953201)
- [Draft repair PR #143](https://github.com/Young-Consultations/portfolio-tasks/pull/143)

## What implementation or testing exposed

Authentication and exact execution-result/v2 validation passed. The failure occurred in `Apply once or visibly quarantine conflicting evidence`. Existing repository tests checked that the workflow mentioned an admission marker, but none executed the current release-enriched marker against the source consumer. The first live end-to-end result exposed that missing interface case.

PR #143 replaces substring matching with JSON marker parsing. It requires an exact match for all five stable binding fields, ignores additive control-plane evidence owned outside the source, counts malformed or conflicting markers as nonmatches, and preserves the existing unique-marker fail-closed rule. Its regression uses the exact v2.4.1 marker shape observed on issue #139.

## Requirement or architecture implications

No authoritative requirement, architecture, ownership, security boundary, or active contract change is needed. The existing source requirement already calls for semantic admission-binding validation. The repair aligns implementation with that requirement.

The architecture and contract decision is resolved: no authoritative change is required. DEF-0033 implementation and verification remain open until PR #143 passes CI, merges, and a controlled result redelivery proves one source projection without duplicate effects.

## Lessons learned

- Parse structured boundary records before comparing them.
- Compare the fields owned by the consumer; preserve additive evidence owned by the producer.
- Test a consumer with the exact currently published producer shape, not only locally reconstructed fixtures.
- Static checks for marker text are not behavioral interface evidence.
- A fail-closed outcome can still be a material availability and state-projection defect.

## `AI_CONTEXT.md` impact

No update is required. The authoritative operational guidance already requires exact schema and admission-binding validation and fail-closed ambiguity handling. Recording the implementation defect as resolved context before live verification would be premature.

## Follow-up

1. Require PR #143 CI, including actionlint, to pass.
2. Merge PR #143 through normal human review.
3. Redeliver the same receiver-validated result or run the controlled REAL acceptance path without creating a new logical task.
4. Confirm exactly one source result projection and remove the quarantine label only after evidence shows the conflict condition is resolved.
5. Update DEF-0033 with the merge commit, successful workflow evidence, resolution date, and resolved status.

## Potential consulting or content value

This is a compact example of why interface tests should validate meaning rather than serialized layout. It supports the broader consulting message that AI-assisted delivery needs evidence at repository boundaries: schemas alone are insufficient when consumers add brittle assumptions about ordering, optional metadata, or representation.
