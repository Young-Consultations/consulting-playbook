# Authority docs lagged the published compatibility baseline

**Date:** 2026-08-24  
**Defect:** DEF-0030  
**Repository:** `Young-Consultations/portfolio-tasks`  
**Related:** portfolio-tasks #109, #117, #135, PR #138; consulting-playbook #35

## Observation

A pre-activation backlog review found that the implementation and live compatibility evidence had advanced beyond the active authority/context layer. The `.github` control plane had already published `ai-sdlc-v2.3.2`, the live target registry recorded passing immutable evidence for all four core targets, and the organization compatibility workflow was green. At the same time, active `portfolio-tasks` instructions still described the 2.3.1 recovery as prospective and several executable backlog prompts still pointed at the rejected historical `c609…` baseline.

This was not a code failure. It was a configuration-management and SDLC traceability defect: an AI agent following the repository's mandated reading order could have obeyed stale higher-authority context and attempted to reason from or restore an obsolete compatibility baseline immediately before target activation.

## Detection

The defect was detected during a ChatGPT/GitHub reconciliation review before issue #117 activation. The review compared the published `.github` release manifest and target registry, the latest successful organization target-compatibility workflow, `portfolio-tasks` active release documentation and `AI_CONTEXT.md`, and executable backlog prompts in issues #109, #116, #117, #119, #120, and #121.

The inconsistency was classified high severity because it sat directly on the activation path and could have reversed an otherwise-correct recovery.

## Resolution

`portfolio-tasks` PR #138 reconciled the active repository state to `ai-sdlc-v2.3.2` and was merged at `d0970fcd570cb27b50113f33e1f18f45640e9073`.

The merged change updated the active release baseline, `AI_CONTEXT.md`, README/interface/traceability material, router and receiver immutable pins, conformance pin/report evidence, and tests. Historical `c609…` and 2.3.1 records remain historical evidence rather than current execution guidance. The portfolio backlog prompts were also reconciled and #116 was closed as historical conformance work superseded by accepted current evidence.

No target was enabled by this correction. Activation remains a separate mutable control-plane decision owned by issue #117.

## Prevention rule

Before any compatibility release is considered ready for activation, run a release-to-backlog reconciliation gate in this order:

`release manifest -> registry/conformance evidence -> active requirements/release docs -> AI_CONTEXT.md -> workflow immutable pins -> executable backlog prompts`

The gate must fail if any active source names an older prospective or rejected baseline as current, or if an AI agent's required reading order can produce a different compatibility conclusion from the published release manifest and registry.

This check should occur after release publication/live verification and before mutable target activation. It complements code/CI validation because the defect can exist even when all implementation tests are green.

## AI-SDLC lesson

As AI-assisted delivery matures, defects do not stay concentrated in source code. Requirements, architecture, release metadata, AI context, issue prompts, and verification evidence can become the defect-bearing artifacts. A green implementation can therefore be unsafe to advance when the authority layer is stale.
