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

## PR #96 implementation review safeguards (unreleased)

The production workflow must compare its workflow ref, workflow SHA and executor
checkout HEAD with `conformance.adapter_commit_sha` and `workflow_ref` in the
organization registry **before importing target code or supplying model,
publication or result-writer credentials**. `CODEX_AUTHORIZED_CONTROL_PLANE_SHA`
is a protected `consulting-playbook-codex` environment variable selecting an
independently approved 40-hex control-plane commit; it is never a dispatch input
or a value inferred from target content. Missing, inaccessible or mismatched
binding fails closed. The adapter separately requires that bound executor SHA
before establishing task content. Existing workflow permissions remain read-only.

This adds a deployment prerequisite: environment protection and an approved
registry commit binding the new immutable adapter must be reviewed before use.
The current 3.1.0 registry authorizes only the existing 3.1.0 adapter; it cannot
authorize this unreleased branch. No environment variable is configured by this PR.
A mutable workflow can change its own checks, so this gate does not replace
protected-environment restrictions on which workflow refs may access credentials.

New drafts retain the original delivery/digest marker and add durable executor
and content-base SHA metadata. If the final HEAD observation is stale or
unverifiable, the publisher verifies the exact branch, delivery, digest, open
state and draft state before prepending explicit blocked evidence to the PR body.
Blocked drafts cannot be reused as successful deliveries. Failed blocking writes
return ambiguous rejection with branch and PR URL for human reconciliation;
there is no automatic model retry. Successful body updates are durable evidence,
not an unconditional GitHub enforcement against a human marking the draft ready.
Release/preflight/acceptance must establish the corresponding review protections.

Runner/registry representation detail (DEF-0129): the registry workflow reference
uses a short adapter tag, while `github.workflow_ref` is fully qualified. Compare
the runner identity with the exact registered repository/workflow path followed
by `@refs/tags/` and `conformance.adapter_ref`; do not accept a branch ref or strip
arbitrary ref prefixes. Workflow and checkout SHA checks remain mandatory.

Ambiguous-create recovery must apply the same after-PR HEAD reconciliation as a
successful create response before returning duplicate reuse. A discovered owned
draft is evidence of a remote effect, not proof of baseline currency. Preserve
partial branch/PR identity and block stale or unreadable observations.

The baseline setup uses one monotonic admitted deadline through executor HEAD
observation, both provenance API reads and each Git checkout command. Each receives
only decreasing remaining time; check expiry before subsequent operations and
after returns, clean up temporary content, and report a canonical timeout.

Publication object identity: capture a validated exact candidate SHA before push,
verify its parent against the attested content base, and push that exact object.
Emit structured workflow log evidence before/after push binding delivery, payload
digest, branch, executor/content SHAs and candidate SHA. Preserve immutable SHA
and digest evidence in canonical partial failure messages (existing contract,
maximum 500 characters) so a moved/deleted topic ref cannot erase which object
was published. Existing authenticated result delivery persists that canonical
failure on the source receipt; logs remain subject to normal workflow retention.
A stale post-push topic requires human quarantine review; do not claim that a
remote quarantine was executed when only a fail-closed disposition was returned.

One deadline spans final HEAD attestation and stale-draft blocking, including PR
view and PR edit. Each operation consumes decreasing remaining time. An exhausted
deadline prevents further commands, returns ambiguous rejection with immutable
partial-effect identity, and explicitly marks blocking as unconfirmed for human
reconciliation instead of restarting an execution budget to attempt cleanup.

Candidate-facing tests must exercise candidate content. The pinned orchestrator
runs the candidate's fixed `scripts/test_codex_execute_contract.py` entrypoint in
a disposable snapshot under bubblewrap. The sandbox clears environment, isolates
PID/network/IPC/user namespaces, drops capabilities, and mounts only read-only
OS/Python runtime directories and explicit dependency package directories, plus
a writable snapshot, temporary home and private /proc and /dev. It does not expose
host home, runner temporary files, original checkouts or parent-process /proc.
Capture/discard test output rather than forwarding untrusted workflow commands.
Copying and test execution share the remaining validation deadline. Sandbox or
runtime dependency readiness is checked before model authentication. Candidate
code/test changes still require review; a passing candidate suite is not proof
of test completeness or permission to bypass other security gates.

Production and conformance CI install bubblewrap. CI prepares the same userns
prerequisites as production and requires real integration tests for broken and
deleted candidate code/tests, blocked host credentials/network/process access,
snapshot-only writes and timeout. Local namespace restrictions may skip those
integration cases, but cannot stand in for mandatory CI evidence.

A Git push timeout may occur after remote acceptance. Reserve 20% of the current
publication budget for read-only exact-ref reconciliation. If time remains, read
the topic ref and compare its commit SHA with the captured candidate. Exact,
different and unverifiable results all retain partial-effect identities and
return ambiguous rejection requiring human reconciliation. If the deadline is
exhausted, issue no further remote command and preserve unverified evidence.
Never retry the push, automatically create a PR, or invoke a second model call.

## Source implementation completion and acceptance

The final source candidate keeps model Git metadata outside the trusted boundary.
After model completion, materialize a second independently fetched exact-base
checkout outside the writable model root. Copy final working-tree regular files
only, with descriptor-relative `O_NOFOLLOW` reads, no source index/config/hooks,
no nested repositories, and no symlinks or special files. The protected checkout
retains its own metadata and becomes the sole validation/publication snapshot.
This deliberately discards model staging metadata: staged-only data absent from
the final working tree is never published. Candidate tests use a separate disposable
copy of this snapshot; they cannot change the validated publisher checkout.

All host Git operations after the model run use protected metadata and isolated
system/global configuration. Model filters, fsmonitor, hooks and URL rewrites do
not cross into that checkout. The one permitted publisher hook is pinned policy:
it accepts only the expected remote ref with an advertised all-zero old OID.
The server then enforces its old-OID compare-and-swap during creation. This rejects
even fast-forward updates to a competing branch without any force option.

Generated commits include delivery/digest/executor/content trailers. Draft reuse
must bind the provenance marker to the PR head SHA, the same-repository remote
topic ref, exactly one recorded content parent, current default base, and those
immutable commit trailers. Ambiguous/missing legacy evidence fails closed before
model execution. Draft blocking also verifies the expected candidate head/repository
before modifying a PR; mutable refs cannot supply global atomicity.

Sandbox runtime/dependency mounts must be trusted system/prefix paths under `/usr`
or `/opt`, excluding the host home, its ancestors/descendants and symlink aliases.
The host user site is not a dependency source. Production/CI must install dependencies
in the trusted runtime. A missing dependency or unavailable sandbox fails readiness
before the paid boundary.

Premerge evidence is provided by `test_publication_isolation.py` (real local Git
malicious metadata, safe create-only publication, links and API-backed reuse proof),
`test_task_content_checkout.py` (all publication race windows and partial timeouts),
`test_validate_repository.py` (staged/unstaged/untracked path/secret checks), and
mandatory CI namespace tests in `test_candidate_test_sandbox.py`. Require exact-head
conformance and a fresh independent code/security review before source merge.

Source merge is not activation. Immutable target tagging, registry/control-plane
composition, environment workflow-ref/authorized-SHA binding, release compatibility,
deployed preflight and a fresh governed REAL identity remain subsequent acceptance
gates. Parent DEF-0125 stays investigating until those gates pass; #167 stays terminal.

Final validation coverage also requires complete nested untracked-path enumeration,
NUL-delimited rename source/destination parsing, and raw final-file/stage-zero secret
inspection. Binary diffs alone supply no added content; a safe working-tree file
must not hide a credential staged in the index. External diff and text conversion
are disabled. `test_validate_repository.py` includes nested untracked forbidden
paths/values, binary values and split read-boundary/staged-replacement regressions.

Path status/name metadata is strict UTF-8 and fails closed on decoding errors;
raw blob and diff contents use a reversible byte mapping. Credential checks cover
path values before diagnostics can echo them. For binary content, compare complete
token occurrence counts against baseline counts rather than exempting every copy
of a known value. Streaming must count a cross-chunk token once and retain partial
prefixes; the index and final working tree are independent checks.

Reusable draft freshness compares its recorded content parent with the current
default HEAD. Name equality alone does not prove freshness. A timeout during PR
creation is an ambiguous remote effect rather than a no-effect failure: reserve
part of the existing deadline for exact ownership discovery and after-PR HEAD
reconciliation, including blocking an owned stale draft. Never retry a timed-out
create or restart model execution; retain known branch/PR evidence on rejection.
