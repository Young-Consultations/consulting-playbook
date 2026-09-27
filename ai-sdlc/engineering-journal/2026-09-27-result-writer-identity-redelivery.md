# Result-writer identity is part of idempotency

**Date:** 2026-09-27  
**Defect:** DEF-0064  
**Status:** Open until corrective release and REAL redelivery acceptance

## Context

The published AI-SDLC 2.4.5 path had already demonstrated one successful REAL
delivery through portfolio issue #154. Portfolio issue #156 was then used to
exercise the remaining same-delivery redelivery acceptance condition while its
first managed draft remained open.

The target behaved as intended. The first delivery created consulting-playbook
PR #70. Reapplying the approved state for the unchanged logical delivery caused
the target to rediscover that same managed draft and return
`duplicate-reused`. It did not invoke Codex a second time and did not create a
second branch or pull request.

The source nevertheless quarantined the second terminal result.

## Evidence

- Source acceptance issue: https://github.com/Young-Consultations/portfolio-tasks/issues/156
- First target run: https://github.com/Young-Consultations/consulting-playbook/actions/runs/36292681735
- Redelivery target run: https://github.com/Young-Consultations/consulting-playbook/actions/runs/36293462493
- Reused managed draft: https://github.com/Young-Consultations/consulting-playbook/pull/70
- Control-plane defect: https://github.com/Young-Consultations/.github/issues/83
- Receiver/preflight repair: https://github.com/Young-Consultations/.github/pull/84
- Stable visible-effect digest on both attempts:
  `3f64ad25762d6ac50c5bca8b64fca901809b60aa9e015da948526fc7c15f27ae`

## What failed

The 2.4.5 receiver's stable-effect redelivery logic was correct, but the durable
journal evidence it depended on was not recognized on the second attempt.

The immutable receiver trust policy allowed result-journal markers from
`github-actions[bot]`. The deployed result credential instead caused those
comments to be authored as `mightyjoe909`. On redelivery, the receiver
therefore treated its own prior receipt and forwarded markers as untrusted,
recorded another receipt, and forwarded the equivalent result again. The source
projector received a different canonical result digest and correctly failed
closed rather than overwriting the first terminal evidence.

This was not a failure of the target's implementation idempotency. It was a
trust-boundary failure in the evidence path.

## SDLC lesson

Idempotency is not only an algorithm over delivery IDs and effect digests.
When durable evidence is authenticated, the identity that writes that evidence
is part of the idempotency mechanism.

A system can have correct retry logic and still lose retry safety when its
deployed writer identity disagrees with the verifier's immutable trust policy.
Credential names are not security roles by themselves. The runtime principal
must be bound to the role and verified before a cost-bearing operation begins.

This extends the existing cost-bearing execution rule: prerequisite APIs are
not ready merely because endpoints exist. The exact credential that will
preserve the result must be able to exercise the required path under the
identity the downstream verifier will trust.

## Architectural decision

The dedicated result writer is the organization-owned GitHub App
`ai-sdlc-result-writer`, App ID `5100679`, installed only on
`Young-Consultations/portfolio-tasks`.

The target candidate will mint a short-lived installation token scoped to that
repository with only the permissions required for result journaling and
projection. Before the OpenAI credential reaches the adapter, the
organization-owned preflight will use that token to:

1. bind execution to the governed portfolio source issue;
2. create and delete a bounded marker comment and verify GitHub's returned
   comment author against the immutable result-author policy; and
3. emit a dedicated no-op repository-dispatch event to prove the forwarding
   capability.

The installation token is deliberately not passed into the Codex adapter.

GitHub App installation tokens are short-lived, while a Codex execution can be
substantially longer. The result receiver therefore must mint a fresh
installation token after execution rather than rely on the pre-Codex token
still being valid. The long-lived App private key remains protected as Actions
secret material and is never committed, placed in task/result payloads, or
recorded in this journal.

## Acceptance consequence

Repository implementation and SIM evidence are necessary but are not sufficient
to resolve DEF-0064. Resolution requires:

- a reviewed immutable `codex-adapter-v2.4.6`;
- a matching reviewed and published `ai-sdlc-v2.4.6` control-plane release
  whose result trust policy names the GitHub App bot identity;
- successful deployed prerequisite preflight; and
- a controlled REAL same-delivery redelivery proving one managed draft, no
  second Codex execution, one trusted receiver effect, and one source
  projection.

Until that evidence exists, 2.4.5 remains the published runtime and the REAL
redelivery acceptance gate remains open.
