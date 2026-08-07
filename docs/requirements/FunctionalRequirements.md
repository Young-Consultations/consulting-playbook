# Functional Requirements

## Requirement record convention

Dependencies cite requirement IDs or external interfaces. Inputs and outputs are
logical information, not prescribed files, screens, or APIs. Unless stated
otherwise, acceptance criteria apply to every supported engagement type.

## Engagement definition

### FR-ENG-01 — Frame an engagement

- **Description:** The product SHALL guide capture of initiating concern,
  desired outcomes, sponsor, decision authorities, urgency, scope, exclusions,
  constraints, success measures, and decisions to be supported.
- **Rationale:** Analysis cannot be evaluated without an agreed purpose.
- **Priority:** P0
- **Dependencies:** BR-01, BR-02
- **Inputs:** Client concern, context, known constraints.
- **Outputs:** Versioned engagement frame with owner and status.
- **Preconditions:** A sponsor or internal owner is identifiable.
- **Postconditions:** Boundaries and decision purpose are reviewable.
- **Acceptance criteria:** (1) Missing required fields are visible; (2) sponsor
  confirms or disputes the frame; (3) changes retain rationale and history.
- **Related vision goals:** VG-01, VG-08.

### FR-ENG-02 — Select and tailor a method

- **Description:** A consultant SHALL be able to select applicable engagement
  types, domains, methods, depth, evidence burden, participants, and outputs and
  MUST record material deviations and rationale.
- **Rationale:** Reuse must not impose one-size-fits-all delivery.
- **Priority:** P1
- **Dependencies:** FR-ENG-01, FR-KM-01
- **Inputs:** Engagement frame, risk, time, information availability.
- **Outputs:** Tailored engagement plan and applicability record.
- **Preconditions:** Engagement frame exists.
- **Postconditions:** Included and excluded methods are explicit.
- **Acceptance criteria:** Two different engagement contexts can share the core
  lifecycle while documenting different depth; no excluded activity appears
  mandatory without an approved plan change.
- **Related vision goals:** VG-01, VG-07.

### FR-ENG-03 — Map stakeholders and authority

- **Description:** The product SHALL distinguish affected, contributing,
  consulted, informed, reviewing, sponsoring, and decision-authority roles.
- **Rationale:** Participation is not approval authority.
- **Priority:** P0
- **Dependencies:** FR-ENG-01
- **Inputs:** Stakeholder identities or role descriptions.
- **Outputs:** Stakeholder/authority map with gaps and conflicts.
- **Preconditions:** Engagement boundaries are known.
- **Postconditions:** Every governed decision has an accountable authority or an
  unresolved-authority flag.
- **Acceptance criteria:** A reviewer can identify who supplies evidence, who
  validates it, and who may decide; conflicting authority blocks final decision
  status.
- **Related vision goals:** VG-06, VG-08.

## Evidence and inquiry

### FR-EVD-01 — Plan proportionate evidence collection

- **Description:** The product SHALL define evidence questions, requested source,
  purpose, proportionality, sensitivity expectation, custodian, and sufficiency
  criteria before or during collection.
- **Rationale:** Unbounded collection increases cost and exposure.
- **Priority:** P0
- **Dependencies:** FR-ENG-01, FR-SEC-01
- **Inputs:** Scope, hypotheses, decisions, classification constraints.
- **Outputs:** Evidence plan and request list.
- **Preconditions:** Scope and intended decisions exist.
- **Postconditions:** Every request has a stated purpose.
- **Acceptance criteria:** Requests outside scope or without purpose are rejected
  or explicitly approved as scope changes; unnecessary sensitive fields are
  excluded.
- **Related vision goals:** VG-02, VG-09.

### FR-EVD-02 — Register evidence and provenance

- **Description:** Each evidence reference MUST identify source, collection date,
  scope, custodian where appropriate, classification, permitted use, relevant
  excerpt or locator, limitations, and validation status without requiring the
  evidence itself to reside in this repository.
- **Rationale:** Findings must be reviewable without duplicating confidential data.
- **Priority:** P0
- **Dependencies:** FR-EVD-01, FR-SEC-01
- **Inputs:** Authorized artifacts, observations, interviews, and measurements.
- **Outputs:** Evidence register entries and access-safe references.
- **Preconditions:** Collection is authorized.
- **Postconditions:** Provenance and handling obligations are known.
- **Acceptance criteria:** Every cited item can be uniquely distinguished; a
  reviewer can tell verified fact, participant assertion, observation, and
  inference apart; inaccessible evidence is flagged.
- **Related vision goals:** VG-02, VG-09.

### FR-EVD-03 — Guide interviews and workshops

- **Description:** The product SHALL support preparation, informed participation,
  facilitation objectives, structured capture, synthesis, attribution choice,
  disagreement capture, participant validation, and follow-up.
- **Rationale:** Consistent inquiry improves evidence quality without scripting judgment.
- **Priority:** P1
- **Dependencies:** FR-ENG-03, FR-EVD-01
- **Inputs:** Session purpose, participants, questions, handling rules.
- **Outputs:** Validated notes, observations, disagreements, and follow-ups.
- **Preconditions:** Participants and capture conditions are authorized.
- **Postconditions:** Claims and interpretations remain distinguishable.
- **Acceptance criteria:** Notes record validation status and limitations;
  disputed statements are not silently converted into facts.
- **Related vision goals:** VG-01, VG-02.

### FR-EVD-04 — Assess evidence sufficiency

- **Description:** The product SHALL enable a consultant to judge relevance,
  corroboration, recency, representativeness, reliability, gaps, and contrary
  evidence for each material line of inquiry.
- **Rationale:** Evidence quantity alone does not establish confidence.
- **Priority:** P0
- **Dependencies:** FR-EVD-02
- **Inputs:** Evidence register and decision needs.
- **Outputs:** Sufficiency assessment, gaps, and collection/limitation decision.
- **Preconditions:** At least one evidence request or explicit absence exists.
- **Postconditions:** Proceed, collect more, narrow conclusion, or stop is explicit.
- **Acceptance criteria:** A recommendation cannot be final when its material
  finding has neither sufficient evidence nor an explicit, authority-accepted
  limitation.
- **Related vision goals:** VG-02.

## Assessment and analysis

### FR-ASMT-01 — Model the current state

- **Description:** The product SHALL support a scoped baseline of relevant
  outcomes, products, people/roles, processes, systems, dependencies, constraints,
  decisions, and observed performance.
- **Rationale:** Follow-up and root-cause analysis require a dated baseline.
- **Priority:** P1
- **Dependencies:** FR-EVD-02, FR-EVD-04
- **Inputs:** Validated evidence and engagement frame.
- **Outputs:** Dated current-state model with sources and omissions.
- **Preconditions:** Scope is agreed or explicitly provisional.
- **Postconditions:** Baseline elements link to evidence and scope.
- **Acceptance criteria:** A reviewer can identify what is observed, inferred,
  excluded, or unknown and the period represented.
- **Related vision goals:** VG-03, VG-05.

### FR-ASMT-02 — Apply domain assessments

- **Description:** The product SHALL offer composable assessment guidance for
  product/vision, backlog, SDLC/delivery, architecture, quality/testing,
  security/risk, DevOps/release, organizational operating model, and AI-assisted
  delivery readiness.
- **Rationale:** These are the repository's intended consulting domains.
- **Priority:** P1
- **Dependencies:** FR-ENG-02, FR-ASMT-01, FR-KM-01
- **Inputs:** Tailored plan, baseline, evidence.
- **Outputs:** Domain observations, capability judgments, risks, and gaps.
- **Preconditions:** Domain applicability is declared.
- **Postconditions:** Domain conclusions share the common reasoning model.
- **Acceptance criteria:** Every supported domain defines purpose, applicability,
  evidence guidance, analysis questions, limitations, outputs, and escalation to
  specialists; unsupported domains are not implied to be assessed.
- **Related vision goals:** VG-03, VG-07.

### FR-ASMT-03 — Contextualize maturity or capability

- **Description:** Capability evaluations MUST state context, observable anchors,
  evidence, uncertainty, and desired outcomes and MUST NOT imply universal
  maturity targets or unsupported numeric precision.
- **Rationale:** Generic scoring can mislead decisions.
- **Priority:** P0
- **Dependencies:** FR-ASMT-02, FR-EVD-04
- **Inputs:** Domain evidence and contextual objectives.
- **Outputs:** Contextual capability profile and improvement considerations.
- **Preconditions:** Assessment basis and purpose are known.
- **Postconditions:** Any rating is explainable through observable anchors.
- **Acceptance criteria:** A reviewer can reproduce the classification from the
  stated anchors; absence of evidence is not scored as poor capability by default.
- **Related vision goals:** VG-02, VG-03.

### FR-ANL-01 — Manage findings and implications

- **Description:** Each finding SHALL identify statement, scope, supporting and
  contrary evidence, confidence, limitations, status, affected outcomes, and
  implication; observations, findings, implications, and recommendations MUST
  remain separately identifiable.
- **Rationale:** A visible reasoning chain prevents advice from being presented as fact.
- **Priority:** P0
- **Dependencies:** FR-EVD-04, FR-ASMT-01
- **Inputs:** Evidence and assessment results.
- **Outputs:** Versioned finding records and implications.
- **Preconditions:** Evidence or an explicit gap exists.
- **Postconditions:** Findings are reviewable, challengeable, and status-controlled.
- **Acceptance criteria:** Each material finding has at least one evidence link or
  is marked unsubstantiated; edits retain disposition and rationale.
- **Related vision goals:** VG-02, VG-03.

### FR-ANL-02 — Analyze causes

- **Description:** The product SHALL guide separation of symptoms, contributing
  conditions, hypotheses, causal evidence, systemic causes, and validation steps.
- **Rationale:** Treating symptoms alone produces weak recommendations.
- **Priority:** P1
- **Dependencies:** FR-ANL-01
- **Inputs:** Findings, baseline, hypotheses, contrary evidence.
- **Outputs:** Cause model with confidence and validation needs.
- **Preconditions:** A material symptom or outcome is identified.
- **Postconditions:** Causal claims are explicitly supported or provisional.
- **Acceptance criteria:** Correlation is not labeled causation without stated
  support; alternative explanations and disconfirming evidence are recorded.
- **Related vision goals:** VG-03.

### FR-ANL-03 — Analyze options

- **Description:** For material decisions, the product SHALL support comparison of
  credible options, including maintaining the status quo, across expected value,
  cost/effort range, risk, dependencies, readiness, reversibility, time horizon,
  uncertainty, and consequence of inaction.
- **Rationale:** Recommendations require transparent alternatives and trade-offs.
- **Priority:** P1
- **Dependencies:** FR-ANL-01; FR-ANL-02 when causal analysis is relevant.
- **Inputs:** Findings, constraints, outcomes, candidate responses.
- **Outputs:** Comparable option analysis.
- **Preconditions:** A decision need exists.
- **Postconditions:** Trade-offs and excluded options are visible.
- **Acceptance criteria:** At least two credible paths, or a rationale for only one,
  are recorded; comparison criteria and uncertainty are explicit.
- **Related vision goals:** VG-03, VG-04.

## Recommendations, decisions, and communication

### FR-REC-01 — Form and prioritize recommendations

- **Description:** A recommendation SHALL link to findings and implications and
  identify intended outcome, beneficiaries, value, urgency, material risks,
  dependencies, readiness, effort range, owner role, sequence, confidence,
  decision needed, and consequence of inaction. Prioritization SHALL use declared
  criteria and preserve human override rationale.
- **Rationale:** Advice must be actionable, transparent, and contextual.
- **Priority:** P0
- **Dependencies:** FR-ANL-01, FR-ANL-03
- **Inputs:** Findings, options, constraints, prioritization criteria.
- **Outputs:** Prioritized recommendation set.
- **Preconditions:** Material findings have passed sufficiency review.
- **Postconditions:** Recommendations are proposals, not approvals.
- **Acceptance criteria:** Ranking can be explained from recorded factors; ties,
  uncertainty, overrides, and dependencies are visible.
- **Related vision goals:** VG-03, VG-04, VG-06.

### FR-DEC-01 — Capture governed decisions

- **Description:** The product SHALL record decision, authority, date, status,
  alternatives, rationale, conditions, assumptions, related recommendations,
  dissent where appropriate, and follow-up trigger.
- **Rationale:** Recommendation and authorization must not be conflated.
- **Priority:** P0
- **Dependencies:** FR-ENG-03, FR-REC-01
- **Inputs:** Recommendation/options and decision-authority response.
- **Outputs:** Versioned decision record.
- **Preconditions:** Authority is established.
- **Postconditions:** Approved, rejected, deferred, conditional, or superseded
  status is explicit.
- **Acceptance criteria:** Only an identified authority can establish approved
  status; changed decisions retain prior state and rationale.
- **Related vision goals:** VG-06, VG-08.

### FR-ROAD-01 — Develop a roadmap

- **Description:** The product SHALL translate approved direction into sequenced
  outcomes, accountable owners, dependencies, decision points, risk responses,
  learning checkpoints, and measures without representing the roadmap as
  execution authorization.
- **Rationale:** Sequenced ownership closes the report-to-action gap.
- **Priority:** P1
- **Dependencies:** FR-DEC-01
- **Inputs:** Approved or conditional decisions and constraints.
- **Outputs:** Outcome-oriented roadmap and unresolved dependencies.
- **Preconditions:** Applicable decisions are recorded.
- **Postconditions:** Sequence and accountability are reviewable.
- **Acceptance criteria:** Every roadmap item has outcome, owner role, dependency,
  measure or exit condition, and authorization status.
- **Related vision goals:** VG-04, VG-06.

### FR-RPT-01 — Produce reconciled audience views

- **Description:** The product SHALL support executive and technical outputs whose
  detail differs by audience while findings, status, priority, and decisions
  remain consistent and traceable to one source reasoning chain.
- **Rationale:** Stakeholders need appropriate detail without contradictory narratives.
- **Priority:** P1
- **Dependencies:** FR-ANL-01, FR-REC-01, FR-DEC-01
- **Inputs:** Assessment records and audience needs.
- **Outputs:** Executive and technical reporting packages.
- **Preconditions:** Report scope and audience are known.
- **Postconditions:** Material conclusions reconcile across views.
- **Acceptance criteria:** Automated or reviewer comparison finds no contradictory
  status/priority; technical detail can be reached from executive conclusions;
  limitations and decision needs appear in both where material.
- **Related vision goals:** VG-04.

## Handoff, follow-up, and knowledge governance

### FR-HO-01 — Prepare recommendation-to-task handoff

- **Description:** For an approved recommendation, the product SHALL support
  decomposition into separately governed, target-specific task proposals with
  objective, rationale, scope, exclusions, expected outcomes, acceptance
  criteria, dependencies, risks, source decision/evidence-safe links, target
  repository, sensitivity classification, and required human authorization.
- **Rationale:** Isolated execution needs complete context and minimal data.
- **Priority:** P0
- **Dependencies:** FR-DEC-01, FR-ROAD-01, FR-SEC-02, Interface-Portfolio-Tasks.
- **Inputs:** Approved recommendation, roadmap, target ownership, classification.
- **Outputs:** One or more non-authorizing handoff packages.
- **Preconditions:** Approval is externally valid and target boundary is known.
- **Postconditions:** Each package is independently reviewable and contains no
  unnecessary sensitive evidence.
- **Acceptance criteria:** Cross-repository work is decomposed; missing target,
  approval, or sensitivity review prevents ready-for-intake status; creation of a
  package alone does not initiate execution.
- **Related vision goals:** VG-06, VG-08, VG-09.

### FR-FU-01 — Measure follow-up

- **Description:** The product SHALL compare follow-up observations with the
  original scope, baseline, intended measures, decisions, and method version and
  SHALL distinguish outcome, activity, capability change, and new context.
- **Rationale:** Consulting value requires evidence of progress and learning.
- **Priority:** P1
- **Dependencies:** FR-ASMT-01, FR-ROAD-01
- **Inputs:** Baseline, measures, subsequent evidence, contextual changes.
- **Outputs:** Progress assessment, residual/new risks, and next decisions.
- **Preconditions:** Baseline and comparison rules exist.
- **Postconditions:** Claims of improvement have a comparable basis or limitation.
- **Acceptance criteria:** Changed scope or measurement is disclosed; incomplete
  measures do not default to success; recommendations can be closed, revised, or
  re-opened with rationale.
- **Related vision goals:** VG-05.

### FR-KM-01 — Catalog reusable knowledge

- **Description:** Each principle, engagement type, domain, method, checklist,
  template, pattern, handoff artifact, and lesson SHALL have purpose, applicability,
  owner, lifecycle status, version, review date, dependencies, variation points,
  and usage guidance.
- **Rationale:** A modular operating system needs findable and governed assets.
- **Priority:** P1
- **Dependencies:** None.
- **Inputs:** Proposed or revised knowledge asset.
- **Outputs:** Cataloged, reviewable asset metadata.
- **Preconditions:** An accountable maintainer is identified.
- **Postconditions:** Consumers can determine suitability and currency.
- **Acceptance criteria:** Assets missing ownership or applicability cannot be
  current/approved; deprecated assets identify replacements or rationale.
- **Related vision goals:** VG-01, VG-07.

### FR-KM-02 — Govern lessons learned

- **Description:** The product SHALL support contribution, review, generalization,
  confidentiality screening, applicability limits, approval, versioning, and
  deprecation of lessons learned.
- **Rationale:** Learning must improve the playbook without leaking client context
  or turning local conclusions into universal prescriptions.
- **Priority:** P1
- **Dependencies:** FR-KM-01, FR-SEC-01
- **Inputs:** Engagement learning and proposed reusable change.
- **Outputs:** Approved generalized knowledge or documented rejection.
- **Preconditions:** Contributor has authority to propose the learning.
- **Postconditions:** Client-specific identifiers and unjustified generalizations
  are excluded.
- **Acceptance criteria:** Every published lesson has confidentiality disposition,
  evidence basis, applicability limits, reviewer, and decision.
- **Related vision goals:** VG-07, VG-09.

## Safety and current target execution

### FR-SEC-01 — Classify and minimize information

- **Description:** The product SHALL guide classification, purpose limitation,
  least necessary collection, access, retention/disposal, redaction, attribution,
  and permitted destinations for engagement information.
- **Rationale:** Client trust and safe reuse depend on deliberate handling.
- **Priority:** P0
- **Dependencies:** Client and organizational handling policy.
- **Inputs:** Information category, intended purpose, destinations, authorities.
- **Outputs:** Handling decision and unresolved restrictions.
- **Preconditions:** Information is contemplated or received.
- **Postconditions:** Use and transfer restrictions are explicit.
- **Acceptance criteria:** Unknown classification is treated as restricted pending
  review; a template never requests sensitive data by default; retention and
  disposal responsibility are named.
- **Related vision goals:** VG-09.

### FR-SEC-02 — Control AI and cross-boundary transfer

- **Description:** Sensitive or confidential information MUST NOT enter an AI
  prompt, executable task, reusable example, or external repository unless a
  designated human has explicitly reviewed and authorized the minimum necessary
  transfer for that destination. AI-derived content SHALL identify AI assistance
  and require professional evidence review.
- **Rationale:** Automation must not bypass confidentiality or judgment.
- **Priority:** P0
- **Dependencies:** FR-SEC-01
- **Inputs:** Classified information, proposed destination/purpose, AI output.
- **Outputs:** Authorized redacted package or denied/pending transfer; review record.
- **Preconditions:** Destination and authority are known.
- **Postconditions:** Transferred content is bounded and attributable.
- **Acceptance criteria:** No implicit approval path exists; fabricated or
  uncited client facts fail professional review; authorization is destination-
  and purpose-specific.
- **Related vision goals:** VG-09, VG-10.

### FR-EXE-01 — Validate target execution authorization

- **Description:** While the repository accepts organization-routed execution, it
  MUST validate a supported canonical contract, correct target, stable approval
  evidence issued by the portfolio authority, routing admission, repository-local
  authorization, assigned executor, non-sensitive status, allowed execution mode,
  draft-only publication, and prohibition of automatic merge before execution.
- **Rationale:** Current delivery infrastructure must remain bounded.
- **Priority:** P0
- **Dependencies:** Interface-Organization-Control-Plane,
  Interface-Portfolio-Tasks.
- **Inputs:** Versioned execution request, immutable approval evidence, and any
  freshness/revocation evidence required by the canonical contract.
- **Outputs:** Authorization decision and sanitized failure category.
- **Preconditions:** An organization router dispatches a request.
- **Postconditions:** Unauthorized work has no mutation/publication effect.
- **Acceptance criteria:** Unsupported versions, malformed evidence, wrong target,
  invalid authority, stale evidence, material source edits, withdrawal or revocation
  fail closed without executor or publication effects. A mutable workflow label is
  never the sole proof. Verify mode does not invoke Codex or mutate/publish.
- **Related vision goals:** VG-08, VG-10.

### FR-EXE-02 — Publish an idempotent draft result

- **Description:** An authorized implementation request MUST map one canonical
  delivery identity to one deterministic managed branch and at most one valid
  open draft pull request, MUST NOT overwrite ambiguous work or merge, and SHALL
  emit a canonical traceable result for success or failure.
- **Rationale:** Retries must not create uncontrolled publication effects.
- **Priority:** P0
- **Dependencies:** FR-EXE-01, Interface-Organization-Control-Plane.
- **Inputs:** Authorized request, delivery/correlation identity, validation/test results.
- **Outputs:** Draft pull request or reusable prior draft; canonical result.
- **Preconditions:** Implement mode is authorized and preflight is unambiguous.
- **Postconditions:** Human review remains required; result links request and run.
- **Acceptance criteria:** Orphaned branches, conflicting ownership, multiple
  drafts, or closed/merged prior deliveries fail closed for manual recovery;
  redelivery reuses exactly one valid managed draft; no direct push to `main` or
  automatic merge occurs. Every terminal attempt produces or durably exposes the
  organization canonical result (not a local schema) for verify success, implement
  success, reused draft, no changes, contract/authorization/policy rejection,
  validation/execution/publication failure, or interrupted/ambiguous execution.
  The result carries correlation and delivery identities, target, timestamps,
  validation evidence, safe failure details, reconciliation guidance, and PR
  metadata when applicable. Duplicate delivery/result processing creates neither
  a second draft nor a second externally visible lifecycle transition.
- **Related vision goals:** VG-08, VG-10.
