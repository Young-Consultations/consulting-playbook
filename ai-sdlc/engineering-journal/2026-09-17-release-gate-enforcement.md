# 2026-09-17 — Release prerequisite existed but was not enforceable

- **Date:** 2026-09-17
- **Decision status:** unresolved
- **SDLC phase:** release / acceptance review

## Context

DEF-0039 established that a repaired target implementation is not production-active until the immutable target release, control-plane release, and source-consumer repin all complete in order. During the 2.4.2 repair, Young-Consultations/.github PR #64 documented that sequence explicitly and reviewers independently flagged the missing `codex-adapter-v2.4.2` tag as a merge blocker.

## Discovery

PR #64 nevertheless merged at commit `6d7a3153ee2686137b45737c68710825d15dd028` while Young-Consultations/consulting-playbook PR #53 was still open and the required `codex-adapter-v2.4.2` tag did not exist.

This is a real SDLC defect, not merely an unfinished release step. The intended prerequisite was known, documented, and reviewed, but it was advisory rather than technically enforced.

## Why it matters

The control-plane main branch can now describe a candidate composition that references an unresolved immutable target ref. Production remains protected because `portfolio-tasks` main still consumes the published `ai-sdlc-v2.4.1` router, so no REAL delivery has been switched to the incomplete 2.4.2 chain. The escape therefore did not activate the bad composition, but it demonstrates that prose merge blockers and review comments are insufficient release controls.

## Related defect(s)

- DEF-0040 — Control-plane release candidate merged before required target tag existed.
- DEF-0039 — Repaired adapter was merged but production remained pinned to the pre-repair immutable release.

## Evidence

- Young-Consultations/.github PR #64 and merge commit `6d7a3153ee2686137b45737c68710825d15dd028`
- Review comment 4043217755: missing immutable target tag
- Review comment 4043219615: new control-plane release and source-consumer repin required
- Young-Consultations/consulting-playbook PR #53 remained open at the time of #64 merge
- Young-Consultations/portfolio-tasks PR #146 remains the staged source-consumer repin

## What implementation or testing exposed

No automated required check prevented #64 from merging while its registered enabled target pointed at an unpublished tag. The existing candidate checks validated internal registry/runtime consistency but did not require remote resolution of the target adapter tag before merge.

## Requirement or architecture implications

The release sequence itself is already documented correctly, so no new architecture decision is required. The missing piece is executable enforcement of the existing release dependency.

The .github control-plane implementation should add a required release-aware candidate check that fails when an enabled registry `workflow_ref` uses an immutable target tag that does not exist, resolves to a different commit than the reviewed registry binding, or lacks the expected evidence binding. Repository/branch protection should require that check before a release-candidate PR can merge.

Until that implementation decision is completed, this remains unresolved. Do not encode speculative mechanics into `AI_CONTEXT.md`.

## Lessons learned

A merge blocker written in prose is evidence of intent, not enforcement. When an immutable release dependency is safety-critical to the next state transition, the dependency must be represented as an executable gate that GitHub can require.

This is also a useful example of the broader intent/evidence model: the release intent was correct, the evidence identified the problem before merge, but the state transition still occurred because enforcement was not connected to that evidence.

## `AI_CONTEXT.md` impact

No update yet. The context already distinguishes published production state from pending 2.4.2 state. Update context only after the release-gate enforcement design is resolved and implemented.

## Follow-up

1. Add a control-plane CI check that resolves every enabled target's immutable registry ref and compares it with the reviewed commit/evidence binding.
2. Make that check required for release-candidate merges.
3. Keep portfolio-tasks PR #146 draft until `ai-sdlc-v2.4.2` publication attestation and Runtime Preflight pass.
4. Complete target PR #53, publish the exact target tag, and reconcile the already-merged control-plane candidate before publishing the control-plane tag.
5. Close DEF-0040 only after the required merge gate itself is verified.

## Potential consulting or content value

This is a strong concrete example of why evidence without enforcement is incomplete. Reviewers found the defect before merge, but the system still allowed the state transition. In an AI-assisted SDLC, verification evidence should feed an explicit state-transition gate rather than relying on a human to remember a prose blocker.
