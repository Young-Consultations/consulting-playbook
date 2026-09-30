# 2026-09-29 — Cross-release admission reuse

- **Date:** 2026-09-29
- **Decision status:** resolved
- **SDLC phase:** release-production

## Context

Portfolio issue #159 is the controlled REAL delivery used to prove the corrected
result-writer and same-delivery redelivery path. Its original durable admission
was created by `ai-sdlc-v3.0.1`.

After receiver-compatibility repair 3.0.2 was published and the portfolio source
consumer advanced to 3.0.2, source reconciliation run
https://github.com/Young-Consultations/portfolio-tasks/actions/runs/36666315992
successfully cleared the queued projection from failed target run 36480321187
without fabricating a terminal result.

## Discovery

The successful reconciliation left the intended state:

- one durable 3.0.1 admission for the original logical delivery;
- no `status:queued` label;
- reconciliation evidence for both prior failed target attempts; and
- no terminal source result.

Inspection of immutable 3.0.2 router code then showed the next authorized retry
would fail before target dispatch. The router constructs a new admission binding
from the current release and activation evidence, then compares the existing
router-owned admission for exact object equality. The preserved 3.0.1 admission
therefore cannot equal a newly generated 3.0.2 binding.

This contradicts the published 3.0.2 acceptance procedure, which explicitly
requires #159 to preserve the original 3.0.1 admission/delivery identity during
recovery.

## Why it matters

Admission evidence is not an attempt-local artifact. It is durable authorization
evidence for the logical delivery.

A release cutover can legitimately change router implementation, activation
snapshot, target adapter, or receiver composition while the same logical
delivery remains authorized for an unchanged retry. Regenerating admission
release/activation evidence on every retry changes the meaning of the original
authorization and can make a correct cross-release recovery impossible.

The converse is equally important: preserving an old admission must not become
an unrestricted bypass. The current target composition must explicitly declare
which predecessor admission releases it can safely process.

## Related defect(s)

- DEF-0086
- https://github.com/Young-Consultations/.github/issues/103
- https://github.com/Young-Consultations/portfolio-tasks/issues/159

## Evidence

- Reconciliation run:
  https://github.com/Young-Consultations/portfolio-tasks/actions/runs/36666315992
- Reconciled failed target run:
  https://github.com/Young-Consultations/consulting-playbook/actions/runs/36480321187
- Router repair:
  https://github.com/Young-Consultations/.github/pull/104
- Published 3.0.2 acceptance authority:
  `Young-Consultations/.github/docs/acceptance/TC-MVP-E2E-001.md`
- Published 3.0.2 release authority:
  `Young-Consultations/.github/docs/releases/3.0.2.md`

The canonical structured defect record is DEF-0086 in the Defect Ledger. This
journal entry links that record and primary evidence rather than duplicating the
ledger as a second source of truth.

## What implementation or testing exposed

The issue was found before reapplying `status:approved`, by tracing the actual
3.0.2 router path after reconciliation.

The relevant behavior was:

1. construct current-release admission binding;
2. read existing admission markers for the same delivery;
3. post a new current-release marker to establish router credential identity;
4. select existing markers owned by that identity;
5. reject if any owned marker differs from the new binding.

That logic works only when retries occur under identical release and activation
evidence. It does not implement the documented cross-release recovery model.

## Requirement or architecture implications

The resolved rule is:

- the first trusted admission is durable evidence for the logical delivery;
- an unchanged authorized retry reuses that admission instead of replacing its
  release/activation evidence;
- immutable contract, delivery, correlation, source, and target identity must
  still match exactly;
- the current target's immutable registry policy declares the exact predecessor
  admission releases reusable for that target;
- ambiguous, malformed, unsupported, or conflicting admissions fail closed;
- new logical deliveries still receive a new admission owned by the current
  control-plane release.

This policy belongs at the target idempotency/compatibility boundary because the
safe predecessor set depends on the current target/receiver composition.

## Lessons learned

Idempotency identity and release identity are related but not interchangeable.

The retry question is not, "Can the current release regenerate exactly the same
admission object?" The correct question is, "Does this unchanged logical
delivery still have one trusted durable admission, and does the current target
composition explicitly support that admission release?"

Cross-release recovery therefore needs compatibility policy at both ends:

- source/operator reconciliation must recognize the predecessor admission; and
- router/target dispatch must preserve and explicitly accept that same durable
  admission before any cost-bearing execution.

Testing only same-release duplicate delivery is insufficient. Release tests need
at least one predecessor-admission redelivery scenario whenever a release claims
backward-compatible recovery.

## `AI_CONTEXT.md` impact

Yes. Once the 3.0.3 repair policy is integrated into authoritative release and
router documentation, affected control-plane and source AI context should state
that durable admission evidence is preserved across compatible release retries
and that predecessor reuse is target-bound, immutable policy rather than
operator input.

Do not record 3.0.3 as published or adopted until its release gates actually
complete.

## Follow-up

1. Complete .github PR #104 implementation and regression coverage.
2. Produce a new immutable control-plane PATCH and matching target adapter whose
   receiver compatibility policy includes the reviewed current/predecessor
   admission releases.
3. Run candidate CI, target compatibility, and SIM.
4. Merge, tag, and attest the new release without moving prior tags.
5. Run deployed Runtime Preflight and immutable REAL preflight.
6. Repin portfolio source routing only after those gates pass.
7. Reauthorize unchanged #159 and prove one corrected terminal projection.
8. Reauthorize the unchanged delivery once more and prove
   `duplicate-reused` before Codex with no second visible effect.

## Potential consulting or content value

High. This is a compact example of a broader AI-SDLC principle: retries across
software or policy versions should preserve the original authorization identity
while independently revalidating compatibility with the current execution
environment. The same pattern applies to workflow engines, payment systems,
queued jobs, and other cost-bearing APIs where "retry" must not silently become
"new authorization."
