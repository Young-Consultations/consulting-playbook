# Proposed ADR: Separate immutable executor from current task-content baseline

**Status:** PROPOSED, NOT APPROVED. Issue [#93](https://github.com/Young-Consultations/consulting-playbook/issues/93) remains `status:proposed`.
**Owner for decision:** consulting-playbook repository owner and organization AI-SDLC control-plane owner, with portfolio approval owner consulted for any change to dispatch authority.
**Scope:** repository-local `workflow_dispatch` target, adapter, and draft publication only. No contract/v2 or activation change is approved here.

## Problem, observation and safety consequence

A cost-bearing implementation task is currently executed inside the immutable
executor checkout. [Target run 38996859486](https://github.com/Young-Consultations/consulting-playbook/actions/runs/38996859486)
for source #167 selected the old `codex-adapter-v3.0.3` revision
`f11852c7f563df16ea4afa9ab75bf766242e7327`, and generated proposed
changes based on outdated ledger and content IDs while default-branch material
had advanced. Current tag `codex-adapter-v3.1.0` points to
`4f15841efcba4883770b5e32c0582f733d73eb91`, but
`.github/workflows/codex-execute.yml` still performs a single checkout.
`GitHubEffects.codex` runs `codex exec ... -C ROOT`;
`has_candidate_changes`, `validate_candidate` and `publish` also operate
at `ROOT`. The same checkout is incorrectly serving as **trusted executable
policy** and **mutable task-content base**.

This is separate from the fixed consulting-root validator defect DEF-0119,
and separate from the terminal replay guard addressed by 3.1.0 under
[.github #111](https://github.com/Young-Consultations/.github/issues/111).
Passing [SIM 39087269988](https://github.com/Young-Consultations/.github/actions/runs/39087269988)
and [REAL-readiness preflight 39087311313](https://github.com/Young-Consultations/.github/actions/runs/39087311313)
do **not** test content-baseline freshness. No new cost-bearing REAL call
is authorized by this proposal.

## Proposed decision

**Two independently attested checkout identities** rather than treating a
versioned executor checkout as a current source tree:

1. **Trusted executable root:** read-only trusted adapter, schema, test
   oracle, policy and validator code from the reviewed and registry-pinned
   immutable `codex-adapter` release. Never import modules, execute
   scripts or read permission policy from a task-content checkout. The
   code identity is the exact adapter release SHA, independently checked
   against the active control-plane registry and conformance report.
2. **Task-content worktree:** independently query the target's authorized
   default-branch commit from GitHub using a read-capable identity, retrieve
   that **exact 40-hex SHA**, and materialize a separate, clean content
   checkout at that SHA. Treat all files in this checkout as untrusted data
   until validated by trusted code. Reject branch names, mutable refs,
   missing SHA, uncommitted initial changes, invalid ancestry, wrong
   repository and ambiguous resolution as inputs to this boundary.
3. **Pre-execution bound proof:** before any model invocation, bind
   `target_repository`, `delivery_id`, approved task scope, immutable
   executor SHA, default branch name, initial content base SHA, and the
   publisher's ownership/permission preflight to one local execution
   evidence record. Resolve the base *after* authenticated result-journal
   and existing-draft checks; do not fetch/execute cost-bearing work when a
   terminal failure or reusable draft already forbids it.
4. **Bounded Codex write access:** use only the task-content worktree for
   model-generated file changes and code-context reading. The trusted
   adapter controls process execution and may supply the minimal declared
   requirements/context needed. Do not expose publisher/result-writer tokens,
   trusted policy files as writable working material, or unrestricted runner
   host paths to model-launched subprocesses. Any unavoidable validator or
   build execution from the untrusted worktree requires a separately reviewed
   sandbox policy.
5. **Validate before publication:** apply repository/path/secret/content
   policies from the immutable executable root against the generated
   task-content candidate; validate intended modifications and
   preserved ledger/content IDs without importing executable policy from
   the mutable checkout. Require `git diff --check`, deterministic
   scenario tests, and repository-specific validators. Report test inputs
   and outcomes, not presumed success.
6. **Race-free draft publication:** immediately before push, independently
   reread target default-branch HEAD. If it differs from the attested task
   base SHA, **fail closed** with a safe stale-base result; do not force
   push, auto-rebase, retry Codex or create a PR with stale content.
   Commit on top of the verified task base SHA, record both candidate parent
   and produced head SHA, create at most one owned **draft** PR, and verify
   remote branch/PR ownership. Only a new governed retry with fresh
   approval/identity or an explicitly reviewed deterministic reconciliation
   may resolve changes of scope.
7. **Existing-draft reuse remains separate:** prior trusted managed-draft
   receipts allow only exact ownership-verified reconciliation, never a
   second model call; prior non-managed terminal receipts block execution.
   Respect the previously published 3.1.0 terminal-receipt guard unchanged.

**Release consequence:** this changes target executor/worktree behavior.
It must be developed on a review branch, with new local conformance and
cross-repository compatibility evidence. Do not change an existing adapter
tag; publication requires a **new reviewed immutable target tag, updated
registry digest/SHA, compatible control-plane release decision and deployed
preflight**, followed by separately approved fresh REAL acceptance.

## Alternatives considered

| Approach | Assessment |
| --- | --- |
| Continue editing immutable executor checkout | **Reject:** proven stale content, incorrect ledger IDs |
| Move all execution to the latest `main` checkout | **Reject:** runs unreviewed mutable executor and policy; loses immutable trust |
| Automatically `git pull` / `git rebase` inside executor | **Reject:** code trust drift and ambiguous publication after races |
| Split trusted executor root and exact-SHA task-content worktree | **Proposed:** preserves policy identity, current work base and explicit merge/retry governance |
| Halt cost-bearing implementation indefinitely | **Safe immediate fallback** while the split design lacks reviewed implementation and evidence |

## Required acceptance tests, all NO_COST until separately approved

- Pinned old trusted executor + newer independently verified default-branch
  content: candidate parent equals the **new** base; existing ledger IDs,
  content IDs, links and newer files are preserved.
- A default-branch SHA that moves between first read and publication is
  detected *before push* and returns a deterministic safe failure with zero
  PR/branch effects; no second Codex invocation.
- Missing or conflicting base API evidence, invalid/mutable ref, wrong
  repository, inaccessible or dirty checkout, or unsupported policy cannot
  cross into Codex; effect counters stay at zero.
- Worktree does not execute `scripts/*.py`, hooks, package lifecycle scripts,
  or imported modules from the untrusted content root outside a separately
  defined sandbox. The trusted executable code/policy SHA is independently
  verified and recorded.
- Regression for `consulting/` path acceptance plus forbidden roots,
  secret-name/value scans, `git diff --check`, link/reference checks,
  canonical Defect Ledger uniqueness and content ID conservation.
- Pre-existing managed draft and same-delivery failed journal result still
  produce their established no-Codex outcomes, with one logical draft maximum.
- Exact adapter candidate SHA passes all 29 shared `TC-MVP-CI-001`
  scenarios with zero real effects, security regression and race fixtures,
  CI, independent reviewer, and cross-repository target compatibility.
- Release and source activation remain unmodified until the separately
  governed immutable publication and deployment process completes.

## Explicit open decisions for owner review

1. **Repository write sandbox:** which existing trusted validator commands
   are safe against untrusted task content, and what isolation policy
   prevents content-controlled scripts from running as the runner identity?
2. **Default branch movement:** fail closed until a *new approved task
   identity* versus a version-bound deterministic no-Codex reconciliation
   operation. Proposed default is fail closed.
3. **Task base provenance:** identify the authenticated read token and exact
   GitHub API response that establishes the default branch and commit SHA;
   it must not grant unrestricted task writes.
4. **Contract visibility:** determine whether base/executor SHAs can be
   captured solely in draft PR provenance or require an additive,
   separately versioned organization-facing result field. Do not change
   `execution-result/v2` without its owner’s approval.
5. **Release order:** decide whether the incompatible trusted-worktree
   behavior merits a SemVer MINOR or MAJOR target release and whether
   3.1.0's still-enabled consulting target should be held administratively
   inactive until correction. Do not alter active routing by this PR.

## Approval / supersession rule

This document is **a decision proposal**, not an authoritative change to
`NextMVP.md`, `InterfaceArchitecture.md`, or `AI_CONTEXT.md`. Upon
owner approval, revise the approved requirements, normative interfaces,
architecture/ADR and acceptance traceability *before* implementation, then
update AI_CONTEXT only with verified resolved decisions. Maintain the issue
and Defect Ledger as open/investigating until tested publication and
accepted production evidence establish resolution.
