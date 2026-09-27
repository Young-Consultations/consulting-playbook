# 2026-09-26 — Cross-repository 2.4.5 authority drift

- **Date:** 2026-09-26
- **Decision status:** resolved
- **SDLC phase:** acceptance-review

## Context

AI-SDLC 2.4.5 was published and attested, deployed Runtime Preflight and immutable
REAL preflight passed, portfolio-tasks advanced its source consumer to 2.4.5, and
fresh issue #154 completed the initial live source → router → consulting target →
managed draft → receiver → source-projection path.

That operational progress outpaced the authority/context layer across the four
repositories. Historical recovery text, candidate-era guidance, and earlier
activation assumptions remained active after their underlying state had changed.

## Discovery

The drift surfaced during the post-REAL repository review and then repeatedly
during PR review:

- consulting-playbook PR #67 found current target requirements, architecture,
  README, and AI_CONTEXT still describing 2.4.5 as a candidate or 2.4.4 as the
  operative state;
- .github PR #81 found active release/acceptance guidance that still treated
  2.4.4 as current, 2.4.0 publication gates as active, 2.4.3 special-case
  validation as current guidance, and 2.4.5 as more fully accepted than the
  preserved evidence supported;
- portfolio-tasks PR #155 found approved requirements/architecture still
  presenting 2.3.2 and pending activation/live verification as current while the
  source router was already on 2.4.5;
- Slugger PR #114 found README, AI_CONTEXT, next-MVP, integration, and ADR status
  text still describing an unpublished/unregistered 2.3.1 recovery candidate
  even though Slugger was registry-bound as immutable
  `codex-adapter-v2.3.2` and remained disabled.

The deeper reviews were important: several lower-level documents had already been
updated, but higher-authority requirements, architecture, or AI context still
contradicted them.

## Why it matters

This was not cosmetic documentation debt. In this project, AI agents and humans
use repository authority/context as execution guidance. Stale active text could:

- select an obsolete release or activation model;
- overstate or understate what REAL evidence actually proved;
- treat immutable historical target evidence as current source/runtime state;
- incorrectly resume cost-bearing work on a known-unsafe rollback;
- block valid work because an already-completed gate still appeared pending; or
- cause a disabled target to be treated as live-ready.

The severity is high because stale authority can directly alter engineering
decisions even when the underlying implementation is correct.

## Related defect(s)

- DEF-0063
- Related but separate unresolved rollback-metadata defect:
  Young-Consultations/.github#82
- Historical related authority drift: DEF-0055

## Evidence

- [portfolio-tasks #120](https://github.com/Young-Consultations/portfolio-tasks/issues/120)
- [consulting-playbook PR #67](https://github.com/Young-Consultations/consulting-playbook/pull/67),
  merge commit `3fbeba99bc1ada5ce5774b61d2174a32d48fa97c`
- [.github PR #81](https://github.com/Young-Consultations/.github/pull/81),
  merge commit `bca6843565b65c06eb38f9ea6a07538a6e6e4e48`
- [portfolio-tasks PR #155](https://github.com/Young-Consultations/portfolio-tasks/pull/155),
  merge commit `aa47591a1a1d5482cdb170ae2029e546615b7f44`
- [Slugger PR #114](https://github.com/Young-Consultations/slugger/pull/114),
  merge commit `16dcda99e750c7862e4f4e1df7c396d0a8f3a67b`
- consulting-playbook exact-head conformance run 36282219828
- .github exact-head contract run 36285970677
- portfolio-tasks exact-head CI run 36287590086
- Slugger exact-head CI run 36289961839

## What implementation or testing exposed

The runtime itself was already substantially healthier than the authority layer.
The reconciliation showed that successful implementation and green CI are not
enough to declare the SDLC state coherent. PR review repeatedly found stale
higher-authority text after lower-level context had been updated.

The most important implementation-readiness lesson was that immutable release and
conformance artifacts must be preserved while current operational guidance is
updated around them. An early consulting reconciliation attempt changed a
comment inside a pinned workflow and invalidated its exact conformance pin;
DEF-0054 captured that error. Later repository reconciliations therefore treated
pinned workflow/adapter/report blobs as release artifacts rather than editorial
surfaces.

## Requirement or architecture implications

The repositories now distinguish four different kinds of state explicitly:

1. current published source/control-plane release;
2. target-specific immutable compatibility evidence;
3. mutable router-owned activation; and
4. live acceptance evidence and its remaining gates.

The current shared source/control-plane release is `ai-sdlc-v2.4.5`.
Only `Young-Consultations/consulting-playbook` is enabled. Portfolio-tasks and
Slugger retain older target-specific immutable compatibility evidence while
remaining disabled as targets. Issue #154 proves the initial live path, but full
REAL acceptance still requires the equivalent redelivery/idempotency exercise
tracked by portfolio-tasks #121.

No new architecture was introduced by this reconciliation. The work restored
the documentation/context layer to the already-resolved architecture and
evidence.

## Lessons learned

Post-release reconciliation needs to be treated as an SDLC state transition, not
an optional documentation sweep. The important question is not merely whether a
release/tag/workflow changed, but whether every active authority layer now tells
the same truth about:

- what is current;
- what is historical immutable evidence;
- what is mutable state;
- what has actually been verified live; and
- what remains unresolved.

Review should move from lower-level docs upward through requirements,
architecture, release guidance, and AI_CONTEXT, because a stale higher-authority
document can silently override otherwise-correct implementation context.

## `AI_CONTEXT.md` impact

Required and completed in all affected repositories as part of the four
reconciliation PRs. No unresolved architectural speculation was added. Slugger
AI_CONTEXT explicitly preserves its disabled state and does not borrow live
evidence from consulting-playbook.

## Follow-up

- Merge the consolidated DEF-0063 capture PR and close portfolio-tasks #120 as
  reconciliation-complete.
- Keep portfolio-tasks #121 open for the equivalent same-delivery
  redelivery/idempotency exercise and final human MVP acceptance.
- Resolve Young-Consultations/.github#82 before treating any predecessor as an
  execution-safe rollback for cost-bearing REAL work.
- Consider adding an explicit release-completion reconciliation checklist or
  executable documentation/state check in a future process improvement, but do
  not encode a mechanism into AI_CONTEXT until that decision is approved.

## Potential consulting or content value

High. This is a strong example of why AI-assisted SDLC needs state reconciliation
after release: implementation can be correct while requirements, architecture,
release guidance, and AI context still tell different versions of reality.
