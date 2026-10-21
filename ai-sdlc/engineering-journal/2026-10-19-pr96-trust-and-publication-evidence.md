# PR #96: observation is not authorization or durable reconciliation

- Date: 2026-10-19
- Phase: implementation review
- Defects: DEF-0126, DEF-0127, DEF-0128 (investigating pending acceptance)
- Evidence: [current-head Codex review](https://github.com/Young-Consultations/consulting-playbook/pull/96#pullrequestreview-5563872096)

The review found three distinct implementation discrepancies under approved
ADR-013: local executor HEAD was recorded without registry authorization; a final
publication race returned an error without updating its draft; and managed draft
evidence omitted both immutable baseline identities. These warrant separate
ledger entries because authorization, reconciliation state and provenance have
different acceptance evidence.

The repair uses an external protected-environment control-plane commit binding
before local imports, records executor/content SHAs on generated drafts, and
persists explicit blocked evidence on owned stale drafts. No-cost publisher tests
exercise all three race windows, unavailable HEAD reads, blocking API failure,
blocked reuse and durable draft provenance. Workflow-gate tests reject missing
policy, mutable refs, wrong tags, wrong workflow SHA and wrong checkout SHA.

Requirements remain ADR-013; the architecture proposal and AI_CONTEXT describe
the resolved implementation and its deployment prerequisite. Protected environment
ref restrictions, Git metadata isolation and complete partial-effect ownership
proof remain independent deployment gates. None of these changes authorizes REAL,
replays terminal source #167, modifies tags or closes parent DEF-0125.

## Follow-up review: DEF-0129

[Codex finding](https://github.com/Young-Consultations/consulting-playbook/pull/96#discussion_r4320471842)
exposed a regression introduced by the executor-binding repair: GitHub runner
workflow refs include `refs/tags/`, but both comparison and positive fixture used
the registry short-tag representation. This would reject every authorized release.
The corrected comparison constructs the exact fully qualified tag ref from the
registered repository/workflow path and adapter tag. The updated positive case
fails against the previous guard and passes against the correction; negative
cases reject short refs, branch refs (including a branch with the tag's name),
wrong tags, wrong repository and mismatched SHAs. Existing requirements and ADR-013
already require the intended identity boundary; implementation guidance and
AI_CONTEXT now clarify the two representations. No deployed release is changed.

## Follow-up review: DEF-0130 and DEF-0131

Codex review of f0976fe identified two integration gaps: lost PR-create responses
could lead recovery to bypass final HEAD reconciliation; baseline suboperations
could each restart the admitted timeout. Both are implementation defects under
existing requirements, requiring no new architectural decision.

The actual publisher/recovery regression creates a remote draft then loses all
three CLI responses, verifies one model call and one topic push, and checks the
final HEAD after discovery. Unchanged HEAD permits reuse; moved/unreadable HEAD
persists blocking evidence and returns ambiguous rejection with partial identity.
A clock-controlled integration test proves executor observation, two API reads
and successive Git commands consume budgets 10, 8, 5, 2, 1 and stop at expiry,
cleaning up the worktree. Another test stops before the second API read when the
first consumes the deadline. Defect Ledger, architecture guidance and AI_CONTEXT
record the unreleased implementation; independent review/acceptance remain open.

## Follow-up review: DEF-0132 and DEF-0133

The review of cecd739 found two remaining implementation discrepancies: post-push
quarantine reporting preserved a mutable ref but omitted the pushed object SHA;
final HEAD attestation and draft blocking could each restart the timeout budget.
Existing ADR-013 provenance and timeout requirements govern both corrections.

The publisher now captures the candidate SHA, verifies that exact object's parent,
pushes the captured SHA, and emits structured intent/completion workflow records.
Canonical partial failure messages bind candidate SHA and payload digest to the
executor/content SHAs, alongside delivery and branch in existing result fields.
No contract fields were added. A local bare-Git integration test deletes the topic
ref immediately after push and proves the immutable object and digest remain in
canonical evidence and workflow log records. Quarantine wording now describes the
required human review rather than claiming a remote quarantine effect.

A single monotonic deadline now covers final HEAD attestation and both PR blocking
commands. Clock-controlled tests prove budgets 10/7/5, no blocking call when HEAD
consumes the deadline, and no edit when view consumes the remainder. Every outcome
preserves partial identity and immutable evidence; expiry reports blocking as
unconfirmed. Architecture implementation guidance and AI_CONTEXT reflect these
unreleased corrections; parent DEF-0125 and deployment/security gates stay open.

## 2026-10-20 follow-up: DEF-0134 and DEF-0135

Completed Codex review of 236a7a0 found that tests still exercised pinned executor
content, and a locally timed-out push could lose partial identity despite remote
acceptance. Both violate existing ADR-013 intent; implementation corrections and
verification are required before advancing the draft.

Candidate test execution now uses a disposable snapshot in a namespace sandbox,
not untrusted code in the credential-bearing host process. A readiness probe
checks namespace/runtime dependencies before model login. CI requires real
candidate-content, deletion, host-state isolation and timeout integration tests.
The local host prohibits network namespace setup, so local skips are explicitly
insufficient for that evidence. Trusted policy checks remain pinned and other
Git metadata/ownership security blockers are unchanged.

Push timeout reserves budget for one read-only exact-ref reconciliation. Local
bare-Git tests accept the push and then simulate lost response/timeout, covering
exact remote candidate, a changed ref and unavailable read, with one push and one
model invocation. All outcomes preserve canonical branch/candidate/digest evidence
and require human reconciliation. An exhausted deadline makes no further API call.
Defect Ledger, architecture guidance and AI_CONTEXT reflect the unreleased behavior;
no tag, registry, credential binding, REAL task or source #167 replay is changed.

## 2026-10-21: source-completion security evidence

The owner requested completion of PR #96. Codex's remaining finding showed that
user-site package mounts exposed runner-home descendants (DEF-0136). The completion
audit also established three distinct source discrepancies behind the listed gates:
post-model Git still used model-writable metadata (DEF-0137, high); a normal push
could fast-forward a competing ref despite the no-force rule (DEF-0138); and marker-only
reuse did not bind the mutable draft/ref to its immutable object/parent (DEF-0139).

The source repair excludes home-derived runtime mounts, materializes an independent
publisher checkout, copies only final regular working-tree data without Git metadata,
and validates/publishes from that protected snapshot. A pinned create-only pre-push
guard refuses nonzero remote old OIDs; normal Git server object comparison covers
concurrent creation after negotiation. Reuse checks the PR head/repository/ref,
parent, default base and immutable delivery/digest/executor/content commit trailers.

Regression evidence uses real Git repositories to demonstrate that malicious model
hooks, filters, fsmonitor and URL rewrites never execute in host publication; existing
refs cannot be fast-forwarded while new refs can be created; links/nested metadata
are rejected; and inconsistent/unsupported API ownership records cannot reach a second
model call. Existing staged/unstaged/untracked validators and mandatory namespace CI
cover the other candidate trust boundaries. These are implementation corrections
under ADR-013, not a new contract schema or production authorization.

The merge decision requires fresh exact-head CI and independent code/security review.
Do not conflate those source gates with the subsequent immutable release/environment
binding, deployed preflight and controlled new-identity REAL acceptance. Parent
DEF-0125 remains investigating after source merge; no terminal #167 replay is allowed.
