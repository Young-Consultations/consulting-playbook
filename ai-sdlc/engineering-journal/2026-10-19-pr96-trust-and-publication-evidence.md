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
