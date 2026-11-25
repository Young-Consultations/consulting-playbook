# 2026-11-24 — Compatibility authentication across workflow triggers

- **Date:** 2026-11-24
- **Decision status:** unresolved for deployed schedule acceptance; resolved for mandatory lint enforcement
- **SDLC phase:** release-production / acceptance-review

## Context
The organization compatibility workflow had recurring scheduled failures while its offline tests remained green. Prior [control-plane #88](https://github.com/Young-Consultations/.github/issues/88) repaired the pull-request path, not scheduled/manual execution.

## Discovery
[Portfolio #172](https://github.com/Young-Consultations/portfolio-tasks/issues/172) recorded the Nov 3 failure. The Nov 24 failure independently showed authentication not configured and HTTP 403 rate limiting, not proven interface incompatibility. The scheduled/manual path used the execution router credential; the PR path already used the built-in read-only token. During repair acceptance, a successful CI step also disclosed that Actionlint had not actually run.

## Why it matters
Read-only verification should not depend on a dispatch credential. A green conditional step does not establish that the named verification occurred. Evaluate each trigger and inspect actual tool execution rather than inferring verification from job color.

## Related defects
- DEF-0147: investigating until deployed scheduled evidence passes.
- DEF-0148: resolved at the verified implementation/merge boundary; post-merge CI is separate.

## Evidence
- [Original scheduled job](https://github.com/Young-Consultations/.github/actions/runs/45452014161/job/138651354104).
- [Initial CI with skipped lint](https://github.com/Young-Consultations/.github/actions/runs/45494331920).
- [Repair PR #118](https://github.com/Young-Consultations/.github/pull/118).
- [Exact-head actual Actionlint job](https://github.com/Young-Consultations/.github/actions/runs/45495574753/job/138805712163).
- [Exact-head manual all-target run](https://github.com/Young-Consultations/.github/actions/runs/45499123052/job/138817385611): all four passed, authentication configured.
- [Exact-head review](https://github.com/Young-Consultations/.github/pull/118#issuecomment-7145720076): zero findings.
- [Merged commit](https://github.com/Young-Consultations/.github/commit/dd9d4b4fed70d0316d7f84d338ef7041a4e06859): same tree as reviewed candidate 3e73652b641f62d3182187a8144d380caa75fd9f (8ca9d22430e4800de5c8d1d943bc2ddc06898f3b).

## What implementation or testing exposed
The built-in token authenticated cross-repository reads for all four registered public repositories. Missing authentication and HTTP failures now fail closed. CI installs pinned Actionlint v1.7.7 and requires its execution, with a static regression guard. No target activation, registry or release changes were introduced.

## Requirement or architecture implications
Existing control-plane verification and least-privilege policy is sufficient; no approved authority or interface change is proposed. The control plane owns verification; this repository owns learning capture.

## Lessons learned
Verify all networked workflow triggers independently. Require evidence that mandatory tools actually ran. Distinguish unavailable evidence from actual incompatibility, and distinguish reviewed candidate success from deployed scheduled acceptance.

## AI_CONTEXT.md impact
Not required: no ownership, authority or active contract changed.

## Follow-up
Verify post-merge CI and a fresh scheduled all-target run at the deployed main SHA before resolving DEF-0147 and closing #172. Preserve Pi Phase 6 observation and target activation. No private evidence is included.

## Potential consulting or content value
A concrete example of green CI versus actual verification, and of trigger-specific test coverage.
