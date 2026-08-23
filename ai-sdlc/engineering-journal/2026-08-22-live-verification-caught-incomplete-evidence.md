# 2026-08-22 — Live verification caught incomplete conformance evidence

- **Date:** 2026-08-22
- **Decision status:** resolved at target evidence; control-plane release pending review
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

## Related defect(s)

- DEF-0027 — Portfolio and Slugger conformance pins omitted the executed harness

## Evidence

- [Fail-closed live verification run](https://github.com/Young-Consultations/.github/actions/runs/32551751500/job/96979533542)
- [Portfolio repair PR #137](https://github.com/Young-Consultations/portfolio-tasks/pull/137)
- [Slugger repair PR #112](https://github.com/Young-Consultations/slugger/pull/112)
- [Control-plane 2.3.2 recovery PR #52](https://github.com/Young-Consultations/.github/pull/52)
- `portfolio-tasks@codex-adapter-v2.3.2` resolves to
  `a7b632eb6f51b750ed863c0f43353d6d931e8e5b`; report SHA-256
  `9baf2c58d8e0ea055e01eee686610468ed739ae41768140d1e1cf2685092bba1`.
- `slugger@codex-adapter-v2.3.2` resolves to
  `797f239579bf56fbd5d11d98a1a6b5bad36d98a8`; report SHA-256
  `8283c78bc9dcea9c2424d0ca250ff6031abecd68495692dd809ee03e06060f3c`.

## What implementation or testing exposed

The independent live verifier required the report-producing harness even though
the target-local required-file constants did not. That asymmetry was valuable:
the external verifier tested the assurance claim, while the local checks tested
only internal consistency. After the repairs, both new immutable tags passed the
same live tag/commit/receiver/report/pin/blob verification.

## Requirement or architecture implications

No payload or router architecture changed. The existing exact-file evidence
model was correct; two consumers implemented an incomplete minimum file set.
The repair therefore uses new patch tags, preserves 2.3.1 tags as immutable
history, updates only the affected registry records, and leaves all targets
disabled. Activation remains a separate human-governed decision.

## Lessons learned

- Define the minimum evidence set in one organization-owned verifier and test
  that every consumer pin is a superset of it.
- Bind the exact report generator, adapter, transport wrapper, validator, and
  contract test files; do not let a generator define away its own identity.
- Run immutable-tag verification from outside the target repository before
  recording release acceptance or considering activation.
- Treat a failing cross-repository verifier as useful evidence, not as proof
  that a repository or workflow is disabled.
- Repair published evidence with a new immutable patch tag. Never move, delete,
  or recreate the failed tag.
- Keep evidence publication, compatibility release, credentials, activation,
  and controlled end-to-end execution as distinct gates.

## `AI_CONTEXT.md` impact

The context now records that Consulting Playbook's own 2.3.1 evidence passed
live verification, while Portfolio and Slugger required 2.3.2 evidence tags.
It removes stale unpublished-tag claims from `AI_CONTEXT.md`, `README.md`, and
the corresponding current-status sections in requirements and architecture docs.

## Follow-up

1. Review and merge the 2.3.2 control-plane registry/release PR.
2. Create `ai-sdlc-v2.3.2` only from its reviewed merge commit; do not move 2.3.1.
3. Re-run the manual live verifier against the merged registry.
4. Return to the issue #117 activation sequence one disabled target at a time.

## Potential consulting or content value

This is a concise case study in assurance independence: green local tests can
prove internal consistency while an external acceptance gate reveals that the
evidence chain never bound the executable that produced the result.
