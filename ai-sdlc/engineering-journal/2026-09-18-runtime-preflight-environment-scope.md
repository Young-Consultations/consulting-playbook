# 2026-09-18 — Runtime Preflight modeled the wrong credential scope

- **Date:** 2026-09-18
- **Decision status:** unresolved — repair merged; deployed rerun pending
- **Decision owner:** Joseph Young, control-plane repository owner, tracked by [Young-Consultations/.github issue #69](https://github.com/Young-Consultations/.github/issues/69)
- **SDLC phase:** release-production

## Context

The 2.4.2 release procedure requires a deployed Runtime Preflight after publication attestation and before the portfolio source-consumer repin. The gate verifies the published tag, activation boundary, and required credential metadata without reading secret values.

`OPENAI_API_KEY` is intentionally isolated in the protected `consulting-playbook-codex` environment. The target execution and authentication-preflight jobs both select that environment before resolving the secret.

## Discovery

[Runtime Preflight run 35399327896](https://github.com/Young-Consultations/.github/actions/runs/35399327896/job/105775369065) passed activation, release publication, and remote tag identity, then failed with `credentials: Young-Consultations/consulting-playbook secret OPENAI_API_KEY is missing`.

The message was accurate only for repository scope. [Authentication run 34929448831](https://github.com/Young-Consultations/consulting-playbook/actions/runs/34929448831/job/104254409000) had already resolved the same name through `consulting-playbook-codex`, stored the credential, and completed a read-only provider probe. The credential existed at the intended boundary; the audit inspected the wrong boundary.

## Why it matters

The false negative correctly kept portfolio PR #146 blocked, so no unsafe runtime transition occurred. A tempting workaround would be to duplicate the key as a repository secret, but that would weaken the deliberate protected-environment boundary merely to satisfy an inaccurate audit.

## Related defect(s)

- DEF-0041 — Runtime Preflight ignored environment-scoped credential metadata.
- DEF-0034 — Codex credential readiness lacked a live provider preflight.
- DEF-0038 — Production adapter did not reproduce the verified Codex authentication boundary.

## Evidence

- [Control-plane issue #69](https://github.com/Young-Consultations/.github/issues/69)
- [Merged repair PR #70](https://github.com/Young-Consultations/.github/pull/70) and merge commit [`78fe6d67adb3a3ddbdc611b9d8cdff14a24c678e`](https://github.com/Young-Consultations/.github/commit/78fe6d67adb3a3ddbdc611b9d8cdff14a24c678e)
- [Failed deployed Runtime Preflight](https://github.com/Young-Consultations/.github/actions/runs/35399327896/job/105775369065)
- [Successful protected-environment authentication preflight](https://github.com/Young-Consultations/consulting-playbook/actions/runs/34929448831/job/104254409000)

## What implementation or testing exposed

The credential-role manifest described every secret in a flat repository collection. `runtime_preflight.py` consequently queried only repository Actions secret and variable endpoints. Neither the manifest nor its tests represented an environment name or exercised the environment metadata endpoint.

## Requirement or architecture implications

The intended architecture remains correct: provider credentials belong in the protected target environment, and the control plane may audit names and scopes but must never read values. The repair makes that existing boundary executable by distinguishing repository credentials from environment credentials and checking each through its matching metadata endpoint.

No target workflow, provider credential, release tag, activation state, or source-consumer pin should change as part of this repair.

## Lessons learned

A credential inventory is not complete when it records only names. Scope is part of the credential contract. A green presence check at the wrong scope can miss a required credential; a red check at the wrong scope can pressure operators toward broader access than intended.

## `AI_CONTEXT.md` impact

The control-plane `AI_CONTEXT.md` is updated in PR #70 because agents need to preserve the environment boundary and understand why the deployed gate remains blocked. No consulting-playbook `AI_CONTEXT.md` change is required; its workflow already selects the correct protected environment.

## Follow-up

1. **Completed:** review and merge control-plane PR #70.
2. Rerun `AI-SDLC Runtime Preflight` on `main` with `candidate_mode: false`.
3. Require the environment credential-metadata boundary to pass.
4. Update DEF-0041 with the successful run and resolve it.
5. Only then move portfolio PR #146 forward.

## Potential consulting or content value

This is a concise example of evidence fidelity: the automation correctly stopped the release, but its model omitted a security-relevant dimension. Improving the evidence did not require weakening the control; it required representing the real boundary more accurately.
