# Approved design: Separate immutable executor from current task-content baseline

**Status:** APPROVED DESIGN (2026-10-17, Arizona local time). Issue [#93](https://github.com/Young-Consultations/consulting-playbook/issues/93) is `status:approved`. The approved design does not authorize an existing-tag mutation or cost-bearing execution.
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
is authorized by the design approval.

## Approved decision

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
6. **Bounded draft publication with explicit moving-HEAD reconciliation:**
   independently read the default-branch HEAD immediately before push and
   reject any mismatch with the attested base **without pushing**. Commit
   on that exact parent, record the parent and produced head SHA, and push
   only an identity-bound topic branch without force. Re-read the default
   branch **after push and before PR creation**. If it has moved, do not
   create a draft; quarantine the pushed topic branch with exact ownership,
   SHA, and a safe stale-base outcome for human cleanup/reconciliation. Do
   not auto-delete a branch whose ownership or current SHA cannot be proved.
   If unchanged, create at most one **draft** PR and recheck the main HEAD
   **after PR creation**. If moved, mark the draft stale/blocked for
   independent review, never automatic merge or Codex retry. The human
   merge gate must independently revalidate current parent/mergeability.
   No API sequence can make GitHub's independently moving default-branch
   ref and a different topic ref atomic, so this flow **does not claim
   zero transient branch effects or permanent atomic HEAD stability**.
   It guarantees no deliberate PR publication after an already observed
   stale base and no automatic acceptance of a draft that becomes stale.
   Any remaining branch/draft side effect is recorded durably against the
   original delivery identity and must be reconciled before new execution.
   A fresh scope-changing attempt requires an authorized new logical task.
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
| Split trusted executor root and exact-SHA task-content worktree | **Approved:** preserves policy identity, current work base and explicit merge/retry governance |
| Halt cost-bearing implementation indefinitely | **Safe immediate fallback** while the split design lacks reviewed implementation and evidence |

## Required acceptance tests, all NO_COST until separately approved

- Pinned old trusted executor + newer independently verified default-branch
  content: candidate parent equals the **new** base; existing ledger IDs,
  content IDs, links and newer files are preserved.
- A default-branch SHA moved **before the pre-push read** yields zero remote
  write effects and no second Codex call; a change *after push but before
  draft creation* yields no PR but a quarantined owned topic ref; a change
  *after draft creation* marks the draft stale and blocked. All observed
  races retain exact ownership/provenance and produce no automatic merge or
  second Codex. Tests assert the distinctions, not impossible atomicity.
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

## Approved controls and implementation sign-off gates

1. **Untrusted-worktree execution:** Trusted interpreter/validator commands
   must run from the pinned executable root, with trusted module paths and
   explicit data-path operands. Deny worktree-controlled hooks, imports,
   local executables and build hooks under the ordinary CI identity.
   Where testing necessarily executes task-controlled material, require a
   separate sandbox and credentials-free process. This isolation must be
   independently tested and accepted before execution.
2. **Moved-head policy:** Reject stale-base publication and never auto-rebase,
   rerun Codex or merge; preserve/quarantine partial remote topic effects
   with an exact delivery identity. Fresh scope requires a new approved
   logical task. A verified same-draft reuse path is permitted only under
   the existing 3.1.0 no-second-Codex evidence rules.
3. **Task base provenance:** Authenticate a read-only GitHub API query of the
   target default branch and commit SHA; verify repository identity and exact
   40-hex object ID. Bind the executor SHA and content base SHA locally before
   Codex. A missing/unauthorized/mismatched response denies execution.
4. **Contract visibility:** Record content/executor SHAs and ownership in
   the owned draft and local evidence; do not change `execution-result/v2`
   or append unreviewed schema fields. Control-plane contract changes, if
   subsequently necessary, require separate owner approval.
5. **Release/activation policy:** No existing adapter tag may be modified.
   A new compatible SemVer release classification is required before a
   new immutable target tag, registry and associated control-plane
   publication. Issue approval does **not** enable new REAL dispatch. The
   owner must assess whether to deactivate the affected cost-bearing path
   while implementation remains incomplete.

The security sandbox implementation, independent conformance and publication
proof are **acceptance gates**, not permissions to skip testing because the
high-level design has been approved.

## Decision provenance and supersession

The repository owner approved the split trusted-executor/current-content
design on 2026-10-17 (America/Phoenix). The review-detected P1 race caveat
([PR #95 discussion](https://github.com/Young-Consultations/consulting-playbook/pull/95))
clarifies that independent Git refs cannot be atomically frozen together.
The revised fail-closed and partial-effect reconciliation controls above
are necessary to implement the approved intent safely. Normative requirements
and interface architecture are updated in the same reviewed change.
`AI_CONTEXT.md` may be aligned only after this decision and those normative
changes are merged and verified. DEF-0125 remains investigating until actual
implementation, release, and operational acceptance prove resolution.
