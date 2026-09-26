# 2026-09-26 — REAL #151 spent Codex work before publication transport failed

- **Date:** 2026-09-26
- **Decision status:** target repair defined; 2.4.5 release and live verification pending
- **Decision owner:** Joseph, repository owner and release approver
- **SDLC phase:** REAL acceptance, defect investigation, and release repair

## Context

Portfolio issue [#151](https://github.com/Young-Consultations/portfolio-tasks/issues/151)
was the first harmless REAL implementation under the published 2.4.4 path after
the sandbox and empty-outcome repairs. The target invoked Codex, produced the
requested six-line documentation change, passed repository validation and target
adapter checks, then failed while publishing the delivery branch.

## Discovery

The [REAL target run](https://github.com/Young-Consultations/consulting-playbook/actions/runs/35882723971)
recorded 16,035 Codex tokens and a local delivery commit, then returned
`ambiguous-rejected` with the message
`Delivery ownership is ambiguous after publication create race`. Independent
post-run discovery found neither the deterministic remote branch nor a matching
pull request.

Inspection of the 2.4.4 adapter found two implementation discrepancies:

1. The pre-Codex publication readiness check used GitHub repository permission
   metadata only. It did not exercise the authenticated Git transport used later
   by `git push`.
2. The publication askpass helper returned one combined
   `x-access-token:<token>` string for every Git credential prompt. It did not
   distinguish username and password prompts. Any nonzero push exit was then
   converted to `create-race`, hiding authentication and other transport
   failures behind an ownership diagnosis.

## Historical comparison

This failure repeated a previously learned pattern in Slugger.

[Slugger PR #71](https://github.com/Young-Consultations/slugger/pull/71) was
merged on 2026-07-23 after publication failed following an expensive Codex
generation with HTTP 403. That repair added an authenticated
`git push --dry-run` before Codex because API permission metadata alone did not
prove the actual Git transport.

During later canonical target convergence, [Slugger PR #108](https://github.com/Young-Consultations/slugger/pull/108)
preserved a safer publication credential boundary: its current publisher uses a
prompt-aware askpass helper, supplies username and password separately through
the publication subprocess environment, disables terminal prompting, captures
push stderr, and distinguishes non-fast-forward races from ordinary push
failures. The earlier transport-level pre-Codex dry-run did not survive into the
current canonical Slugger adapter.

The consulting target therefore both missed a previously demonstrated
pre-execution safeguard and used a weaker publication implementation than the
current Slugger publisher.

## Related defect(s)

- DEF-0048 — REAL 2.4.4 publication transport failed after cost-bearing Codex execution.
- DEF-0047 — release-state documentation drift discovered while preparing this
  repair; the 2.4.4 publication has since been verified and the stale candidate
  wording is reconciled in the 2.4.5 repair.

## Evidence

- [Source issue #151](https://github.com/Young-Consultations/portfolio-tasks/issues/151)
- [REAL 2.4.4 target run](https://github.com/Young-Consultations/consulting-playbook/actions/runs/35882723971)
- [Slugger PR #71](https://github.com/Young-Consultations/slugger/pull/71)
- [Slugger PR #108](https://github.com/Young-Consultations/slugger/pull/108)
- [Organization 2.4.4 candidate PR #75](https://github.com/Young-Consultations/.github/pull/75)
- [Organization 2.4.4 publication attestation PR #76](https://github.com/Young-Consultations/.github/pull/76)
- Defective published target commit
  `70ea4342abf7115f6848ea32bb958bbf6be696c1`.

## Repair decision

The immediate repair remains inside the existing target architecture rather than
adding a new control plane:

1. Keep the repository permission metadata check.
2. Before consuming the OpenAI credential or invoking Codex, use the publication
   identity to execute a non-mutating authenticated `git push --dry-run` against
   a disposable run-specific ref.
3. Use the same prompt-aware, secret-free askpass shape proven by Slugger:
   username and password are supplied separately in the publication subprocess
   environment, the token is absent from command arguments and helper content,
   and terminal prompting is disabled.
4. During real publication, treat only a non-fast-forward/fetch-first response as
   a possible create race that enters ownership reconciliation. Other push
   failures remain ordinary failed publication outcomes.
5. Preserve published 2.4.4 identities and prepare a new immutable 2.4.5 target
   candidate with regenerated exact-file conformance evidence and a future
   matching 2.4.5 receiver pin.

## Requirement and architecture implications

The target requirement is clarified narrowly: before cost-bearing Codex
execution, the publication identity must both report repository push permission
and prove the authenticated Git push transport with a non-mutating dry-run.
Failure or indeterminate readiness stops before Codex.

No new architectural component or ADR is required for this repair. It restores a
preflight responsibility already consistent with the target's fail-closed,
least-privilege publication boundary.

A broader organization rule such as “all downstream cost-bearing API
prerequisites must be proven before AI execution,” including proof of draft-PR
creation and result transport, remains a separate requirements/architecture
decision. It is intentionally not inferred from this implementation repair.

## `AI_CONTEXT.md` impact

The release state is no longer speculative: 2.4.4 is published and was exercised
by REAL #151. After updating the normative Next-MVP and interface architecture,
`AI_CONTEXT.md` is reconciled to the published 2.4.4 identities, the reviewed
2.4.5 candidate boundary, and the transport-level pre-Codex readiness rule.

## Follow-up

Review and merge the 2.4.5 target repair only after exact-head conformance
passes. Publish a new immutable target tag, prepare and publish the matching
organization 2.4.5 control-plane release, run deployed Runtime and REAL
preflights, then use a fresh portfolio delivery identity for the next harmless
REAL execution. Issue #151 remains terminal failure evidence and must not be
reused.

Separately audit the current Slugger canonical adapter to decide whether the
pre-Codex transport dry-run lost during convergence should be restored there.

## Potential consulting or content value

This is a concrete example of cost-bearing AI work succeeding while a later
delivery dependency fails, and of a previously learned safety mechanism being
lost during architecture convergence. It supports the emerging concept of
cost-bearing API execution safeguards without treating that broader concept as
an approved standard yet.
