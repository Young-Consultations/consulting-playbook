# Architectural Decision Records

## ADR-001 — Portable knowledge core with optional runtime

**Context:** The vision requires reusable practice and offline/implementation-neutral use; hosted collaboration needs are unknown.
**Decision:** Canonical knowledge and exchange artifacts remain open, human-readable and tool-independent. A runtime is an optional adapter/application realization.
**Alternatives:** Runtime-first SaaS; unstructured documents only.
**Tradeoffs:** Portability and longevity over rich collaboration; structured conventions add authoring discipline.
**Consequences:** Validators and stable metadata are essential. Runtime-only semantics are prohibited.
**Open questions:** Required exports, accessibility, localization and future engagement-record storage.

## ADR-002 — Clean modular-monolith domain architecture

**Context:** Capabilities share strong invariants while scale and deployment needs are unvalidated.
**Decision:** Organize cohesive domain/application modules behind ports; deploy together unless evidence justifies separation.
**Alternatives:** Microservices; scripts/templates without a model.
**Tradeoffs:** Lower operational/cross-service complexity; requires discipline against internal coupling.
**Consequences:** Infrastructure depends inward; modules have explicit contracts and test seams.
**Open questions:** Whether any future workload needs independent deployment.

## ADR-003 — Separate reusable knowledge from engagement instances

**Context:** Client material carries distinct confidentiality, retention and ownership while reusable assets are repository-owned.
**Decision:** Use separate bounded contexts, repositories/stores and promotion workflow. No ordinary copy/save promotes client content.
**Alternatives:** One repository/store; tenant tags in a shared content tree.
**Tradeoffs:** Safer ownership and reuse; more explicit linking/generalization work.
**Consequences:** Client-derived lessons require authorization, minimization, confidentiality and content review.
**Open questions:** Approved engagement storage locations and policies.

## ADR-004 — Explicit typed reasoning graph

**Context:** The product must distinguish epistemic types and trace evidence to action.
**Decision:** Model stable typed records and links for evidence, findings, implications, hypotheses, options, recommendations and decisions.
**Alternatives:** Narrative-only reports; a single assessment document; score-centric model.
**Tradeoffs:** Integrity and multiple projections over simpler authoring.
**Consequences:** Link/invariant validation and usability guidance are required. Reports are projections, not separate truth.
**Open questions:** Minimum required fields by engagement type.

## ADR-005 — Human authority as an explicit policy boundary

**Context:** Recommendations, AI and automation must not become approval.
**Decision:** Governed transitions require authenticated, freshly resolved scoped authority and immutable rationale/history.
**Alternatives:** Role inferred from participation; approval keywords; AI/autocalculated decisions.
**Tradeoffs:** Safety/accountability over frictionless automation.
**Consequences:** Unresolved authority blocks; narrative never grants rights.
**Open questions:** Identity provider, authority taxonomy and specialist thresholds.

## ADR-006 — Classification-first, minimum-data integration

**Context:** Consulting may encounter confidential client material and cross-boundary AI/external systems.
**Decision:** Unknown classification is restricted; transfers require purpose-, destination-, content- and time-specific authorization. References are preferred to copies.
**Alternatives:** Open-by-default; repository-wide blanket consent.
**Tradeoffs:** Reduced exposure versus additional review and limited automation.
**Consequences:** Governance checks precede retrieval, AI and handoff. Telemetry excludes content.
**Open questions:** Classification taxonomy, jurisdictions, retention and approved AI providers.

## ADR-007 — Contract-first anti-corruption adapters

**Context:** External repositories are independently owned and unavailable for inspection.
**Decision:** Define required semantics as ports; implement only against owner-approved versioned contracts and fixtures. Translate external models at adapters.
**Alternatives:** Import shared internals; infer APIs from references; duplicate schemas.
**Tradeoffs:** Independence and testability versus adapter work.
**Consequences:** Unknown details are acceptance blockers, not design blanks to invent.
**Open questions:** Every external schema, transport, auth and SLA listed in Integration Architecture.

**Next-MVP application:** The target pins package, schema, workflow interface,
registry expectation, and shared consumer fixtures to one immutable compatible
organization release. Only its documented public API is consumable; internal or
observed module paths and copied schemas are prohibited. Unsupported or unverified
APIs fail closed. Public API and release details remain an external enablement gate.

## ADR-008 — Idempotent external effects with reconciliation

**Context:** Network retries/lost acknowledgements can duplicate portfolio submissions or publications.
**Decision:** Assign stable logical effect identities, reconcile indeterminate outcomes before retry, and block ambiguous ownership.
**Alternatives:** At-most-once attempt; workflow-run IDs; blind retries; last-write-wins.
**Tradeoffs:** Safety and traceability over automatic recovery in ambiguous cases.
**Consequences:** External contracts must support deduplication/query or documented manual recovery. Concurrency is not correctness.
**Open questions:** Portfolio deduplication contract and retention window.

**Next-MVP application:** At-least-once deliveries and result replay converge on
one draft and one externally visible result transition. No-change has no
publication effect; interruption or uncertain publication is reconciled before
retry and reports canonical recovery guidance.

## ADR-009 — Domain events and regenerable audience projections

**Context:** Executive and technical reports need different detail but identical material truth.
**Decision:** Commit governed state/history once and derive versioned access-filtered projections; use events for audit/rebuild.
**Alternatives:** Independently authored reports; direct database views as contracts.
**Tradeoffs:** Consistency over manual freedom; eventual projection freshness must be visible.
**Consequences:** Semantic reconciliation tests and source revisions are mandatory.
**Open questions:** Required output formats and acceptable projection latency.

## ADR-010 — AI is a replaceable assistance port

**Context:** AI can accelerate analysis but cannot be authoritative and providers evolve.
**Decision:** Place AI behind a provider-neutral gateway with minimized authorized context, labeled provenance and mandatory professional review. Human workflows remain complete without it.
**Alternatives:** Embed model calls in domain modules; autonomous agent state changes; prohibit AI entirely.
**Tradeoffs:** Controlled benefit and portability versus less autonomy.
**Consequences:** AI cannot invoke decision transitions; evaluation/security tests are required.
**Open questions:** Approved models, evaluation thresholds, residency/retention and disclosure formats.

## ADR-011 — Stable approval proof across mutable workflow state

**Context:** Portfolio approval truth and routing admission have different owners,
and queue processing may replace an approval label after admission.
**Decision:** Treat control-plane admission as necessary but insufficient. Validate
stable canonical repository-change approval evidence plus local policy; never use
a mutable label as the sole proof. Bind proof to authority, approved revision/scope,
target and decision time and fail closed for edits, staleness, withdrawal,
revocation, invalid authority or mismatch.
**Alternatives:** Recheck only `status:approved`; trust routing without target checks;
reuse consulting recommendation approval.
**Tradeoffs:** Race-safe accountability over simpler label checks; depends on an
organization decision if the canonical contract lacks sufficient evidence.
**Consequences:** Live registry enablement is blocked until proof and revocation
semantics are externally confirmed. Consulting and execution approvals remain
distinct audit records.

## ADR governance

Each accepted change records status, date, deciders and supersession links when the architecture is operationalized. A decision may be superseded but not silently edited. Open questions remain explicit validation work and cannot be treated as acceptance.
