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
