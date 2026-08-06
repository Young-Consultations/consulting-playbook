# Use Cases

## Actors

Consultant, consulting lead, client sponsor, decision authority, participant,
product/engineering/program practitioner, specialist reviewer, delivery team,
knowledge maintainer, portfolio governance system/owner, organization control
plane, target repository, and bounded AI agent.

## UC-01 — Frame and tailor an engagement

- **Primary actors:** Consultant, sponsor; **value:** shared purpose and
  proportionate effort; **requirements:** FR-ENG-01–03.
- **Primary flow:** Capture concern/outcomes → establish boundaries and measures
  → map stakeholders/authority → select engagement type/domains/depth → sponsor
  validates frame and consultant records tailoring.
- **Alternatives:** Scope remains provisional; authority gap is escalated; a
  domain is excluded with rationale; conditions cause approved re-scoping.
- **Failures:** No sponsor/decision purpose; irreconcilable authority; prohibited
  information required. The engagement remains proposed/blocked and no final
  conclusion is represented.
- **Outcome:** Versioned, reviewable engagement frame and plan.

## UC-02 — Collect and evaluate evidence

- **Primary actors:** Consultant, participant, custodian, specialist; **value:**
  defensible conclusions with controlled exposure; **requirements:** FR-EVD-01–04,
  FR-SEC-01.
- **Primary flow:** Define questions/sufficiency → minimize and authorize requests
  → conduct artifact review/interviews/workshops → register provenance and
  classification → corroborate/challenge → decide whether evidence is sufficient.
- **Alternatives:** Use authorized reference rather than copy; anonymize or redact;
  narrow scope; record participant disagreement; seek specialist review.
- **Failures:** Access denied, unreliable/stale evidence, unknown classification,
  insufficient corroboration. The finding is narrowed, marked provisional, or
  excluded; absence is not silently treated as proof.
- **Outcome:** Evidence register, gaps, limitations, and collection disposition.

## UC-03 — Assess current state and capability

- **Primary actors:** Consultant, practitioners, specialist reviewer; **value:**
  contextual baseline across relevant domains; **requirements:** FR-ASMT-01–03.
- **Primary flow:** Establish dated baseline → apply tailored domain questions →
  map observable capability anchors → validate with participants/specialists →
  record risk, uncertainty, and exclusions.
- **Alternatives:** Qualitative profile replaces scoring; multiple perspectives
  remain unresolved; domain escalates to a qualified specialist.
- **Failures:** Generic score lacks anchors; scope/evidence cannot support a
  conclusion. The product rejects precision and reports limitation.
- **Outcome:** Evidence-linked, contextual current-state/capability profile.

## UC-04 — Develop findings, causes, and options

- **Primary actors:** Consultant, consulting lead, reviewers; **value:** transparent
  reasoning rather than prescribed answers; **requirements:** FR-ANL-01–03.
- **Primary flow:** Draft findings → attach support/contradiction and confidence →
  separate implications → test causal hypotheses/alternatives → compare response
  options and status quo → review and disposition challenges.
- **Alternatives:** Finding remains provisional; cause remains a hypothesis;
  reviewer rejects or requests evidence; only one credible option is justified.
- **Failures:** Fabricated fact, conflated symptom/cause, or unsupported material
  conclusion. It cannot progress to a final recommendation.
- **Outcome:** Reviewable finding/cause/option chain.

## UC-05 — Recommend, decide, and report

- **Primary actors:** Consultant, sponsor, decision authority, executive and
  technical audiences; **value:** informed, accountable decisions;
  **requirements:** FR-REC-01, FR-DEC-01, FR-RPT-01.
- **Primary flow:** Prioritize transparently → prepare reconciled audience views →
  present impacts/trade-offs/uncertainty → authority approves, rejects, defers, or
  conditions → record rationale and follow-up.
- **Alternatives:** Authority overrides ranking with rationale; dissent is
  recorded; recommendation is revised; decision is deferred pending evidence.
- **Failures:** No authority, contradictory reports, sensitive disclosure, or
  recommendation presented as approval. Decision remains unresolved and output
  is corrected before distribution.
- **Outcome:** Reconciled reports and an attributable decision record.

## UC-06 — Roadmap and governed portfolio handoff

- **Primary actors:** Consultant, authority, program/product owner, portfolio
  owner; **value:** approved advice becomes accountable work without bypassing
  governance; **requirements:** FR-ROAD-01, FR-HO-01.
- **Primary flow:** Select approved direction → sequence outcomes/owners/
  dependencies/checkpoints → decompose by target → minimize context and classify
  → validate task completeness → submit to external intake → retain returned link.
- **Alternatives:** Conditional decision yields gated roadmap; portfolio rejects
  or asks clarification; external dependency remains pending.
- **Failures:** Missing approval/target, sensitive content, duplicate identity, or
  multi-target task. Handoff is blocked; no execution authority is inferred.
- **Outcome:** Traceable, self-contained proposal and external governance status.

## UC-07 — Conduct follow-up

- **Primary actors:** Consultant, sponsor, practitioners; **value:** measured
  outcomes and learning; **requirements:** FR-FU-01.
- **Primary flow:** Reconfirm scope/measure comparability → collect follow-up
  evidence → compare baseline → distinguish activity/capability/outcome/context →
  update recommendation status/risks → identify next decisions.
- **Alternatives:** Measure changed with disclosed bridge; recommendation is
  revised or reopened; no change is a valid result.
- **Failures:** Baseline unavailable or incomparable. No improvement claim is
  made; limitation and recovery action are documented.
- **Outcome:** Progress assessment tied to original intent.

## UC-08 — Maintain consulting knowledge

- **Primary actors:** Maintainer, consulting lead, assurance reviewers;
  **value:** current, safe reusable practice; **requirements:** FR-KM-01–02.
- **Primary flow:** Propose from need/lesson → generalize and screen confidentiality
  → review evidence/applicability/accessibility → approve/version → publish →
  measure/review → revise or deprecate.
- **Alternatives:** Keep engagement-specific; publish with limited applicability;
  reject; replace with migration guidance.
- **Failures:** No owner, leaked context, universalized local claim, or broken
  trace. Asset cannot become current.
- **Outcome:** Governed knowledge with explicit lifecycle and history.

## UC-09 — Use AI as bounded assistance

- **Primary actors:** Consultant, AI agent, reviewer; **value:** faster drafting
  without surrendering judgment; **requirements:** FR-SEC-02, NFR-AI-01–02.
- **Primary flow:** Define purpose → classify/minimize context → obtain transfer
  authorization where required → request bounded assistance → mark provenance →
  validate claims/evidence → human accepts, revises, or rejects.
- **Alternatives:** Use synthetic/redacted context or no AI.
- **Failures:** Unknown sensitivity, fabricated fact, missing citation, attempted
  autonomous decision. Transfer/output is blocked or rejected.
- **Outcome:** Reviewable assistance, never autonomous authority.

## UC-10 — Execute an approved repository task

- **Primary actors:** Control plane, portfolio source, target workflow, AI agent,
  human reviewer; **value:** safe change proposal; **requirements:** FR-EXE-01–02.
- **Primary flow:** Receive/version-validate → revalidate live authorization →
  preflight identity → verify without mutation or implement bounded change →
  validate/test → publish/reuse one draft → emit result → human reviews.
- **Alternatives:** Valid prior draft is reused; no-op receives the allowed bounded
  retry; verify mode stops after checks.
- **Failures:** Wrong target, revoked approval, sensitive state, incompatible
  contract, test failure, orphan/conflict. Fail closed, report sanitized failure,
  and require manual recovery where ambiguous.
- **Outcome:** Non-mutating verification or one traceable draft; never merge.
