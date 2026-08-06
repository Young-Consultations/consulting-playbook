# Component Design

## Component contract standard

Every component has one accountable repository owner, publishes versioned interfaces, sanitizes failures, emits audit/diagnostic signals and is independently testable. “Lifecycle” below is conceptual and does not prescribe a runtime.

## Consulting components

| Component | Purpose and responsibilities | Inputs → outputs | Dependencies | Lifecycle / failure / scale | Ownership |
|---|---|---|---|---|---|
| Knowledge Catalog | Discover and govern methods, templates, domains and patterns. Enforce applicability, review and compatibility. | Asset proposals, reviews → immutable releases, catalog index, deprecations | Governance policy, asset repository | Draft→review→published→deprecated/withdrawn. Invalid/confidential content is quarantined. Cache immutable releases; index separately. | Consulting knowledge maintainers |
| Engagement Context | Establish scope, outcomes, exclusions, success and decision purpose; tailor plan and authority map. | Concern, stakeholders, constraints → versioned frame and plan | Knowledge Catalog, Authority service | Proposed→active→paused/closed. Missing sponsor or authority is visible/blocking where required. Partition by engagement. | Engagement owner |
| Evidence Registry | Plan collection and retain access-safe provenance, kind, use and limitations. | Questions, references, observations → evidence plan/register | Information Governance, external locator verifier | Requested→received→validated/disputed/inaccessible/retired. Never treats inaccessible as absent. Scale indexes/metadata, not raw evidence. | Engagement evidence custodian |
| Assessment Engine | Build dated baseline and apply composable domain methods and contextual capability anchors. | Frame, plan, evidence → baseline, observations, risks/gaps | Catalog, Evidence Registry | Draft→reviewed→superseded. Unsupported domain or insufficient evidence yields limitation, not fabricated result. Parallelize independent domains. | Consulting method owner + practitioner |
| Reasoning Graph | Preserve typed links among evidence, findings, implications, causal hypotheses and options. | Evidence assessments → traceable analysis | Assessment, policy | Findings follow explicit states; broken links/contradictions block finalization. Graph queries can be indexed/read-scaled. | Engagement lead |
| Recommendation Service | Form and prioritize actionable recommendations with criteria, alternatives and uncertainty. | Reasoning graph, constraints → recommendation revisions | Authority, Reasoning Graph | Proposed→approved/rejected/deferred/conditional/superseded/closed via Decision. Calculation errors never decide priority. | Consultant proposes; authority decides |
| Decision Register | Record authority-owned decisions with conditions, rationale and immutable history. | Recommendation, authenticated decision → decision record/event | Authority service, Audit | Atomic append; invalid/conflicting authority rejects. High-integrity consistency boundary. | Named decision authority |
| Roadmap & Handoff | Sequence approved work, propagate conditions, decompose by owner and exchange proposals. | Decisions → roadmap and intake proposal/acknowledgement | Portfolio adapter, Decision Register | Draft→validated→submitted→acknowledged/failed/reconciled. Retry only safe transport failures. Partition by target. | Roadmap owner; external target owns accepted work |
| Reporting | Create reconciled audience projections and exports. | Canonical graph/state → executive, technical, handoff views | Projection, access-control ports | Regenerable; stale or divergent views fail reconciliation. Horizontally scale stateless renderers. | Engagement reporting owner |
| Follow-up | Compare outcomes with baseline, record changed context and propose lessons. | Baseline, roadmap, later observations → outcome assessment, lesson proposal | Evidence, Knowledge governance | Planned→observed→evaluated→closed. Avoid unsupported attribution. Scale per engagement. | Engagement owner |

## Cross-cutting and delivery components

| Component | Purpose and responsibilities | Inputs → outputs | Dependencies | Lifecycle / failure / scale | Ownership |
|---|---|---|---|---|---|
| Information Governance | Classification, minimization, permitted use, transfer/AI authorization and retention obligations. | Item/context/purpose/destination → permit, deny or unresolved | Authority and policy sources | Policy versions immutable. Unknown/timeout denies sensitive transitions. Stateless evaluation may scale; decisions audited. | Security/privacy authority |
| Authority Service | Resolve authenticated actors and scoped decision rights freshly at transition time. | Actor/action/subject → authorization decision | Identity adapter, authority map | Conflicts/unavailability yield unresolved, never permit. Cache only within stated freshness. | Designated governance owner |
| Integration Gateway | Translate external contracts without leaking their models inward. | Versioned outbound/inbound messages → canonical port results | External adapters | Compatibility negotiated; malformed/unknown versions quarantined. Scale per connector. | Integration maintainer + external owner |
| AI Assistance Gateway | Supply minimized bounded context and capture model/prompt/purpose/provenance; never approve. | Authorized request → labeled proposal and metadata | Information Governance, provider adapter | Reject prohibited transfer; provider failure leaves human workflow usable. Rate-limit and isolate providers. | Product/security owner |
| Audit & Observability | Record state/decision history and safe operational telemetry with correlation. | Domain/integration events → audit trail, metrics, traces, alerts | Durable audit adapter | Append-only retention; telemetry loss signals degraded health. Partition by tenant/engagement; redact. | Operations and governance owners |
| Target Policy Adapter | Validate repository, executor, issue authority, sensitivity, mode and branch policy. | Canonical execution input + fresh source state → verified execution context | Control plane, Portfolio/source query | Received→verified/rejected. Any ambiguity fails before mutation. Stateless. | This repository |
| Publication Coordinator | Map one delivery identity to one deterministic branch/draft and result. | Verified delivery + validated change → draft URL/result | Git hosting adapter, validation suite | New→executing→published/reused/blocked. Never overwrites ambiguity. Serialized hints are not correctness. | This repository |

## Component interaction rules

1. Presentation accesses application services, never adapters directly.
2. Reporting reads canonical projections and cannot mutate domain state.
3. An AI gateway cannot call Decision Register or Authority Service as an actor.
4. Handoff does not create authoritative portfolio state until an owner acknowledgement is received.
5. Knowledge Catalog stores generalized reusable assets; engagement content never enters it through an ordinary save operation.
6. Audit data is access-controlled business evidence, while operational telemetry is minimized diagnostic data; the two are not interchangeable.
