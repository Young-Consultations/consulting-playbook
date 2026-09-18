# 2026-09-17 — Release prerequisite existed but was not enforceable

- **Date:** 2026-09-17
- **Decision status:** partially resolved — CI implementation complete; required-check configuration pending
- **Decision owner:** Joseph Young, control-plane repository owner, tracked by [Young-Consultations/.github issue #65](https://github.com/Young-Consultations/.github/issues/65)
- **SDLC phase:** release / acceptance review

## Context

DEF-0039 established that a repaired target implementation is not production-active until the immutable target release, control-plane release, and source-consumer repin all complete in order. During the 2.4.2 repair, [Young-Consultations/.github PR #64](https://github.com/Young-Consultations/.github/pull/64) documented that sequence explicitly and reviewers independently flagged the missing `codex-adapter-v2.4.2` tag as a merge blocker.

## Discovery

[PR #64](https://github.com/Young-Consultations/.github/pull/64) nevertheless merged at [`6d7a3153ee2686137b45737c68710825d15dd028`](https://github.com/Young-Consultations/.github/commit/6d7a3153ee2686137b45737c68710825d15dd028) while [Young-Consultations/consulting-playbook PR #53](https://github.com/Young-Consultations/consulting-playbook/pull/53) was still open and the required `codex-adapter-v2.4.2` tag did not exist. Review fixes then moved #53's candidate head from `5ee5d8aacaa9293d162ed371bc73ddb1483e9c98` to its final merge commit [`6ce0bf941c10c0c37b51c90d433d39f377ccad85`](https://github.com/Young-Consultations/consulting-playbook/commit/6ce0bf941c10c0c37b51c90d433d39f377ccad85), proving why the control-plane binding must occur only after the target release identity is final.

This is a real SDLC defect, not merely an unfinished release step. The intended prerequisite was known, documented, and reviewed, but it was advisory rather than technically enforced.

## Why it matters

The early control-plane merge temporarily described a candidate composition that referenced an unresolved immutable target ref. Production remained protected because `portfolio-tasks` main continued to consume the published `ai-sdlc-v2.4.1` router, so no REAL delivery switched to the incomplete 2.4.2 chain. The escape therefore did not activate the bad composition, but it demonstrated that prose merge blockers and review comments were insufficient release controls.

The target tag was subsequently published at the final reviewed target commit, and [Young-Consultations/.github PR #66](https://github.com/Young-Consultations/.github/pull/66) reconciled the binding and implemented an all-pull-request release-evidence check. The implementation is complete, but DEF-0040 remains open because [issue #65](https://github.com/Young-Consultations/.github/issues/65) still requires that check to be configured and demonstrated as a required merge rule.

## Related defect(s)

- DEF-0040 — Control-plane release candidate merged before required target tag existed.
- DEF-0039 — Repaired adapter was merged but production remained pinned to the pre-repair immutable release.

## Evidence

- [Young-Consultations/.github PR #64](https://github.com/Young-Consultations/.github/pull/64) and merge commit [`6d7a3153ee2686137b45737c68710825d15dd028`](https://github.com/Young-Consultations/.github/commit/6d7a3153ee2686137b45737c68710825d15dd028)
- [Review comment 4043217755](https://github.com/Young-Consultations/.github/pull/64#discussion_r4043217755): missing immutable target tag
- [Review comment 4043219615](https://github.com/Young-Consultations/.github/pull/64#discussion_r4043219615): new control-plane release and source-consumer repin required
- [Young-Consultations/consulting-playbook PR #53](https://github.com/Young-Consultations/consulting-playbook/pull/53), which produced published target commit [`6ce0bf941c10c0c37b51c90d433d39f377ccad85`](https://github.com/Young-Consultations/consulting-playbook/commit/6ce0bf941c10c0c37b51c90d433d39f377ccad85)
- [Young-Consultations/.github PR #66](https://github.com/Young-Consultations/.github/pull/66), merge commit [`1ea59832996dc398923c2d1516eb464546e30877`](https://github.com/Young-Consultations/.github/commit/1ea59832996dc398923c2d1516eb464546e30877), and the passing [target-compatibility run](https://github.com/Young-Consultations/.github/actions/runs/35375868023)
- [Young-Consultations/.github issue #65](https://github.com/Young-Consultations/.github/issues/65), which remains open for required-check configuration and proof
- [Young-Consultations/portfolio-tasks PR #146](https://github.com/Young-Consultations/portfolio-tasks/pull/146), which remains the draft source-consumer repin

## What implementation or testing exposed

No automated required check prevented #64 from merging while its registered enabled target pointed at an unpublished tag. The existing candidate checks validated internal registry/runtime consistency but did not require remote resolution of the target adapter tag before merge.

## Requirement or architecture implications

The release sequence itself is already documented correctly, so no new architecture decision is required. The missing piece is executable enforcement of the existing release dependency.

PR #66 added the release-aware candidate check. It runs on every pull request and fails when an enabled registry `workflow_ref` tag does not exist, does not resolve to the reviewed commit, or lacks the expected evidence binding. The check also resolves the exact Git tag ref, validates the explicit unpublished-candidate state, and avoids exposing a repository token to pull-request-controlled code.

The remaining decision is operational enforcement: configure `AI-SDLC Target Compatibility` as a required ruleset or branch-protection check and demonstrate that GitHub blocks a nonpassing candidate merge. Joseph Young owns that decision through issue #65. Until that evidence exists, DEF-0040 remains open.

## Lessons learned

A merge blocker written in prose is evidence of intent, not enforcement. When an immutable release dependency is safety-critical to the next state transition, the dependency must be represented as an executable gate that GitHub can require.

This is also a useful example of the broader intent/evidence model: the release intent was correct, the evidence identified the problem before merge, but the state transition still occurred because enforcement was not connected to that evidence.

## `AI_CONTEXT.md` impact

PR #66 updated the control-plane `AI_CONTEXT.md` with the published target identity and the remaining 2.4.2 publication boundary. No consulting-playbook `AI_CONTEXT.md` change is required because this entry records control-plane enforcement state and does not change consulting-playbook authority or architecture.

## Follow-up

1. **Completed:** publish `codex-adapter-v2.4.2` at the exact reviewed target commit.
2. **Completed:** merge PR #66 with the reconciled binding and all-PR release-evidence check.
3. Configure `AI-SDLC Target Compatibility` as a required ruleset or branch-protection check for control-plane merges.
4. Demonstrate that GitHub blocks a candidate whose required release-evidence check fails, and attach that evidence to issue #65.
5. Keep portfolio-tasks PR #146 draft until `ai-sdlc-v2.4.2` publication attestation and Runtime Preflight pass.
6. Close DEF-0040 only after the required merge gate itself is verified.

## Potential consulting or content value

This is a strong concrete example of why evidence without enforcement is incomplete. Reviewers found the defect before merge, but the system still allowed the state transition. In an AI-assisted SDLC, verification evidence should feed an explicit state-transition gate rather than relying on a human to remember a prose blocker.
