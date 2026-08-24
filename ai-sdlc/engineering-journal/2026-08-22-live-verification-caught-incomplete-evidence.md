# 2026-08-22 — Live verification caught incomplete conformance evidence

- **Date:** 2026-08-22
- **Decision status:** resolved at target evidence; 2.3.2 control-plane recovery merged and tagged; merged-registry rerun evidence is a separate gate
- **SDLC phase:** release-production

## Context

Issue [portfolio-tasks #135](https://github.com/Young-Consultations/portfolio-tasks/issues/135)
recovered the four-target AI-SDLC compatibility chain and published immutable
2.3.1 adapter evidence. A manually initiated organization workflow then resolved
each tag and rechecked the workflow, receiver, report, pin, and every bound blob
instead of trusting repository-local green checks.

## Discovery

The live workflow rejected `portfolio-tasks` and `slugger`. Both checked-in
reports said the complete 29-scenario oracle passed with zero prohibited effects,
but each conformance pin omitted the exact
`scripts/run_tc_mvp_ci_001.py` file that produced the report. The local harness
and local validator shared the same incomplete required-file set, so they agreed
with each other while failing to prove the executed harness identity.

The repositories were not disabled or unavailable. The failure was expected
fail-closed behavior from an independent verifier and exposed a genuine evidence
integrity defect after immutable publication.

## Why it matters

A report is not trustworthy merely because its scenarios pass. Reviewers must
also be able to prove which executable produced it. Otherwise an unbound harness
can change report construction or effect trapping without changing the claimed
adapter revision. Local agreement between generator and validator is weaker than
independent reconstruction from an externally defined minimum evidence set.

The defect is classified **high severity** because the incomplete evidence
escaped local and pull-request checks into immutable published adapter tags. If
the independent verifier had not failed closed, release or activation review
could have accepted evidence that did not cryptographically bind the executable
that generated the report.

## Related defect(s)

- DEF-0027 — Portfolio and Slugger conformance pins omitted the executed harness

## Evidence

- [Fail-closed live verification run](https://github.com/Young-Consultations/.github/actions/runs/32551751500/job/96979533542)
- [Portfolio repair PR #137](https://github.com/Young-Consultations/portfolio-tasks/pull/137)
- [Slugger repair PR #112](https://github.com/Young-Consultations/slugger/pull/112)
- [Control-plane 2.3.2 recovery PR #52](https://github.com/Young-Consultations/.github/pull/52)
- [Issue #135 recovery checkpoint recording successful 2.3.2 live verification](https://github.com/Young-Consultations/portfolio-tasks/issues/135#issuecomment-5382561301)
- `portfolio-tasks@codex-adapter-v2.3.2` resolves to
  `a7b632eb6f51b750ed863c0f43353d6d931e8e5b`; report SHA-256
  `9baf2c58d8e0ea055e01eee686610468ed739ae41768140d1e1cf2685092bba1`.
- `slugger@codex-adapter-v2.3.2` resolves to
  `797f239579bf56fbd5d11d98a1a6b5bad36d98a8`; report SHA-256
  `8283c78bc9dcea9c2424d0ca250ff6031abecd68495692dd809ee03e06060f3c`.

The issue checkpoint records that both repaired tags passed live compatibility
verification with the report digests above. This journal does **not** currently
preserve the exact successful GitHub Actions run URL, so it does not claim that
an auditor can reconstruct that specific successful run from this entry alone.
The failed run remains the direct workflow evidence for discovery; the checkpoint,
immutable tag/commit bindings, and report digests are the recorded resolution
evidence until the successful run URL is added.

## What implementation or testing exposed

The independent live verifier required the report-producing harness even though
the target-local required-file constants did not. That asymmetry was valuable:
the external verifier tested the assurance claim, while the local checks tested
only internal consistency. The issue #135 checkpoint records that both new
immutable tags subsequently passed the same live tag/commit/receiver/report/pin/blob
verification.

## Requirement or architecture implications

No payload or router architecture changed. The existing exact-file evidence
model was correct; two consumers implemented an incomplete minimum file set.
The target repair therefore uses new patch tags and preserves 2.3.1 tags as
immutable history. The control-plane recovery then rebounded the affected
registry records, updated 2.3.2 release metadata, self-pinned the result receiver
to `ai-sdlc-v2.3.2`, and updated the verify-only router smoke workflow. These
release-coordination changes did not alter target activation state.

## Lessons learned

- Define the minimum evidence set in one organization-owned verifier and test
  that every consumer pin is a superset of it.
- Bind the exact report generator, adapter, transport wrapper, validator, and
  contract test files; do not let a generator define away its own identity.
- Run immutable-tag verification from outside the target repository before
  recording release acceptance or considering activation.
- Preserve the URL of both the fail-closed run and the successful recovery run in
  the defect record before declaring the evidence chain audit-complete.
- Treat a failing cross-repository verifier as useful evidence, not as proof
  that a repository or workflow is disabled.
- Repair published evidence with a new immutable patch tag. Never move, delete,
  or recreate the failed tag.
- Keep evidence publication, compatibility release, credentials, activation,
  and controlled end-to-end execution as distinct gates.

## `AI_CONTEXT.md` impact

The context records that Consulting Playbook's own 2.3.1 evidence passed live
verification, while Portfolio and Slugger required 2.3.2 evidence tags. This is
a resolved evidence-history fact, not a new architecture decision. No additional
AI-context architecture change is required by this documentation correction.

## Follow-up

1. Preserve the exact successful 2.3.2 live-verification Actions run URL in the
   ledger/journal if it is recovered from Actions history.
2. Preserve the merged-registry live-verification run as separate release
   acceptance evidence for `ai-sdlc-v2.3.2`.
3. Keep all activation and credential work under the separate issue #117 gate,
   one target at a time.

## Potential consulting or content value

This is a concise case study in assurance independence: green local tests can
prove internal consistency while an external acceptance gate reveals that the
evidence chain never bound the executable that produced the result.
