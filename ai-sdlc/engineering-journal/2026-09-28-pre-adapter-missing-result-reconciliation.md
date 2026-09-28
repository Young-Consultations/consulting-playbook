# 2026-09-28 — Missing-result recovery cannot depend on the result path

- **Date:** 2026-09-28
- **Decision status:** resolved
- **SDLC phase:** release-production

## Context

The controlled REAL 3.0.1 acceptance delivery in portfolio issue
[Young-Consultations/portfolio-tasks#159](https://github.com/Young-Consultations/portfolio-tasks/issues/159)
was admitted by the organization router and projected to `status:queued`. The target workflow then
failed before the production adapter started.

The immediate configuration failure was in the GitHub App token-mint step:
`actions/create-github-app-token` rejected the configured result-writer private key with
`Invalid keyData`. That prerequisite problem is separate from the lifecycle defect described here.

## Discovery

The source had a durable admission record but no way to represent the later failed handoff when the
target never produced a canonical `execution-result/v2`. Because normal result delivery depends on
the same result-writer credential whose prerequisite had failed, adding only a target-side synthetic
failure result would not repair the observed case.

The source therefore remained `status:queued` even though the cited target workflow had already
completed unsuccessfully.

## Why it matters

A queued projection communicates that admitted work is still awaiting or undergoing execution.
Leaving it indefinitely after a known failed target workflow obscures the actual recovery state and
forces operators to reconstruct the boundary failure manually.

The more important architectural lesson is that **recovery from a missing result cannot rely solely
on the result channel that may itself be unavailable**. The recovery path must preserve the target
as authority for execution facts while giving the source an independent, bounded way to record that
a terminal result is missing and human reconciliation is required.

## Related defect(s)

- DEF-0067
- Tracking issue:
  [Young-Consultations/portfolio-tasks#160](https://github.com/Young-Consultations/portfolio-tasks/issues/160)

## Evidence

- Source delivery:
  [portfolio-tasks#159](https://github.com/Young-Consultations/portfolio-tasks/issues/159)
- Failed target run:
  [consulting-playbook run 36441714913](https://github.com/Young-Consultations/consulting-playbook/actions/runs/36441714913)
- Failed target job:
  [job 108993619717](https://github.com/Young-Consultations/consulting-playbook/actions/runs/36441714913/job/108993619717)
- Repair:
  [portfolio-tasks PR #161](https://github.com/Young-Consultations/portfolio-tasks/pull/161)

## What implementation or testing exposed

The router had already written the durable admission marker and returned success, so the source
correctly changed its UI projection from approved to queued. In the target, caller admission also
succeeded. The workflow then failed while minting the bounded result-writer GitHub App token, before
Codex, adapter execution, branch creation, validation, publication, or result delivery.

This is the useful boundary condition: the work was **accepted by routing**, but the result-producing
execution path did not get far enough to create a canonical terminal fact.

## Requirement or architecture implications

The approved portfolio requirements already cover the intended behavior. FR-RTE-02 and FR-RTE-04
require ambiguous or partial handoffs to enter reconciliation rather than be treated as completed
execution. BR-17 requires actionable recovery evidence, BR-28 prevents a missing result from
establishing completion, and the Error Handling architecture requires missing terminal results to
preserve confirmed state and reconcile by correlation.

The implementation decision is therefore narrow: portfolio-tasks owns an operator-authorized
reconciliation action that binds one admitted delivery to concrete completed failed target-workflow
evidence, records a durable `ai-sdlc-reconciliation:v1` marker, and clears the queued projection.
It does not create `execution-result/v2`, claim what happened inside the target beyond the workflow
fact, or retry automatically.

An automatic timeout or reconciliation deadline is still a separate governance decision. This
repair intentionally does not invent one.

## Lessons learned

A prerequisite gate prevents wasted cost only if its own failure has a recoverable lifecycle.
Pre-Codex protection is necessary, but a fail-closed stop should still leave enough independent
evidence for the source to distinguish “accepted and still running” from “accepted, no terminal
result, operator action required.”

The recovery plane should depend on less than the execution/result plane it is recovering. Here that
means using durable source admission plus GitHub workflow evidence, under explicit human authority,
instead of introducing an emergency credential that would weaken the existing result-writer trust
boundary.

## `AI_CONTEXT.md` impact

No AI_CONTEXT update is required for DEF-0067. The authoritative portfolio requirements and
architecture already assign reconciliation to the source and prohibit inventing downstream state.
The repair does not change the canonical contract or ownership boundary. The unresolved automatic
reconciliation deadline must remain out of AI_CONTEXT until its owner makes that decision.

## Verification

Portfolio-tasks PR #161 merged to `main` at
`76c2942c7e7a099ce2e940a7470ba2bbf40a801e`. The live recovery workflow was then exercised
against source issue #159 and the original failed target run 36441714913:

- recovery run
  [36478712289](https://github.com/Young-Consultations/portfolio-tasks/actions/runs/36478712289)
  completed successfully;
- the workflow authenticated the human operator and immutable control-plane trust policy;
- it loaded the exact target workflow evidence and revalidated the delivery binding;
- source issue #159 now contains exactly one trusted `ai-sdlc-reconciliation:v1` marker written by
  `github-actions[bot]`;
- `status:queued` was removed; and
- no `execution-result/v2` was fabricated and no Codex, branch, PR, receiver, publication, or
  automatic retry effect was created.

This closes DEF-0067. A later unchanged retry, REAL run
[36480321187](https://github.com/Young-Consultations/consulting-playbook/actions/runs/36480321187),
proved the earlier `Invalid keyData` prerequisite corrected: both result-writer installation-token
mints succeeded, the App identity check passed as `ai-sdlc-result-writer`, and the bounded
result-delivery prerequisite probe passed before Codex.

That run then exposed the separate receiver compatibility defect DEF-0073 /
[Young-Consultations/.github#100](https://github.com/Young-Consultations/.github/issues/100):
the approved 3.0.1 source admission was rejected by the pinned 3.0.0 receiver because the receiver
incorrectly forced source/control-plane release identity to equal receiver implementation release
identity.

## Follow-up

1. Repair DEF-0073 / Young-Consultations/.github#100 through the immutable release process.
2. Preserve the original logical delivery identity for any authorized unchanged retry.
3. Reconcile #159 after failed target attempts as needed, and resume the REAL acceptance sequence
   only after the corrected receiver compatibility path is published and verified.

## Potential consulting or content value

This is a compact example of designing AI delivery systems around failure containment rather than
only happy-path automation. “Check prerequisites before spending tokens” is incomplete unless the
system also has a recovery path when a prerequisite check itself fails after handoff.
