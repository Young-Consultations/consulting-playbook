# 2026-09-15 — Repaired source was not the active immutable runtime

- **Date:** 2026-09-15
- **Decision status:** resolved
- **SDLC phase:** release-production

## Context

Portfolio issue #145 was the first governed delivery attempted after production adapter repair PR #51 merged into `consulting-playbook`. The repair changed the production Codex authentication boundary and pinned the current client/model path, but the organization control plane continued to select the previously published immutable adapter release.

## Discovery

Issue #145 routed correctly through the portfolio and organization control plane, then the target workflow checked out `codex-adapter-v2.4.1` at commit `f34ceacc310dff0ce66bad8d623230af7143071d`. That immutable release predates PR #51. The run therefore launched `gpt-5.1-codex` and failed with `401 Unauthorized` before creating a branch, running validation or tests, or publishing a draft pull request.

The repaired implementation existed on `main` at `9a45a8e56c4cbfddf30229b0c23a171097b93868`, but no new immutable target adapter release had been published and bound into the active registry/runtime composition.

## Why it matters

A merged source repair and a production repair are different lifecycle states when execution is intentionally pinned to immutable artifacts. A green repair PR can be technically correct yet operationally absent until release identity, registry binding, and runtime composition all point to that repaired artifact.

This is exactly the kind of state transition that can look complete to a human reviewing source history while remaining incomplete to the running system.

## Related defect(s)

- DEF-0039
- DEF-0038, which repaired the production adapter authentication boundary itself

## Evidence

- Portfolio issue: https://github.com/Young-Consultations/portfolio-tasks/issues/145
- Failed target run: https://github.com/Young-Consultations/consulting-playbook/actions/runs/35036928406
- Adapter repair PR: https://github.com/Young-Consultations/consulting-playbook/pull/51
- Repaired commit: https://github.com/Young-Consultations/consulting-playbook/commit/9a45a8e56c4cbfddf30229b0c23a171097b93868
- Control-plane repair PR: https://github.com/Young-Consultations/.github/pull/64

## What implementation or testing exposed

The end-to-end acceptance attempt exposed release identity drift that source-level tests could not. The target logs showed the exact immutable ref and commit selected by the control plane, proving that the old runtime was functioning as configured rather than the repaired runtime failing.

## Requirement or architecture implications

No new execution path or architecture is required. The existing immutable-release design is correct. The operational rule must be enforced consistently: a production repair is not complete until the repaired target has a new immutable adapter tag, the control-plane registry and generated runtime record bind that tag and exact conformance evidence, and release-aware target verification passes.

The repair sequence is therefore:

1. publish `codex-adapter-v2.4.2` at repaired commit `9a45a8e56c4cbfddf30229b0c23a171097b93868`;
2. bind the new tag, commit, and conformance digest in the control plane;
3. verify the active runtime resolves that immutable adapter;
4. use a fresh governed delivery identity for the original task because #145 already has a terminal failed result.

## Lessons learned

Immutable execution makes release state explicit, but it also means source completion cannot be treated as deployment completion. Verification should ask not only “is the repair merged?” but “which immutable artifact will the next REAL execution actually select?”

A useful acceptance check for future production-path repairs is to compare the intended repair commit with the registry-bound adapter commit before authorizing a REAL delivery.

## `AI_CONTEXT.md` impact

Do not update repository AI context to claim `codex-adapter-v2.4.2` is active until the immutable tag exists, the control-plane repin is merged, and runtime verification passes. After that state transition, affected context files should be reconciled to the new active adapter identity.

## Follow-up

- Create immutable `codex-adapter-v2.4.2` at the exact reviewed repair commit.
- Complete and verify Young-Consultations/.github#64.
- Confirm current runtime resolves v2.4.2.
- Create a fresh governed delivery for the original #145 outcome.
- Resolve DEF-0039 only after the active production path proves the repaired adapter through a successful governed delivery.

## Potential consulting or content value

This is a strong example of evidence-driven delivery: source code, tests, merge state, release identity, active configuration, and runtime evidence are separate facts. AI-assisted development increases the value of proving each state transition rather than inferring deployment from a green PR.
