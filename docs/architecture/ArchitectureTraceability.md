# Architecture Traceability Matrix

## Trace method

Trace flows **Vision goal → business rules/objective → requirements → architectural capability/decision → component → interface → future implementation evidence**. Architecture IDs below are stable references: `AC-*` capability and `AD-*` decision (mapped to the numbered ADRs). Implementation is future and must supply the listed evidence; current code is not proof of the consulting product.

## Architecture capability index

| ID | Capability |
|---|---|
| AC-01 | Engagement context, tailoring and authority map |
| AC-02 | Evidence planning, provenance, sufficiency and baseline |
| AC-03 | Domain assessment and typed reasoning graph |
| AC-04 | Recommendation, priority and governed decision |
| AC-05 | Roadmap, handoff and external reconciliation |
| AC-06 | Reconciled reporting and follow-up |
| AC-07 | Knowledge catalog, lessons and lifecycle governance |
| AC-08 | Information/authority governance and bounded AI |
| AC-09 | Contract-first integrations and repository boundaries |
| AC-10 | Safe target execution and idempotent draft publication |
| AC-11 | Audit, observability, error/configuration/deployment controls |

## Vision-to-architecture matrix

| Vision goal | Business intent/rules | Requirements | Architecture | Components/interfaces | Future implementation evidence |
|---|---|---|---|---|---|
| VG-01 Repeatable, adaptable practice | BR-05, BR-13 | FR-ENG-01/02, FR-KM-01; NFR-MNT-01/03 | AC-01, AC-07; AD-001/002 | Engagement Context, Knowledge Catalog; command/catalog APIs | Two materially different end-to-end scenario tests; tailoring/deviation validation. |
| VG-02 Evidence-led conclusions | BR-06–12 | FR-EVD-01–04, FR-ANL-01; NFR-INT-01 | AC-02, AC-03; AD-004 | Evidence Registry, Reasoning Graph; evidence ports | Provenance/sufficiency/contrary-evidence invariant tests and reviewer scenarios. |
| VG-03 Current state/root cause/risk | BR-10–12 | FR-ASMT-01–03, FR-ANL-02 | AC-02, AC-03 | Assessment Engine, domain extension contract | Baseline time/scope tests; contextual anchors and causal-alternative tests. |
| VG-04 Prioritized practical action | BR-20/21 | FR-ANL-03, FR-REC-01, FR-ROAD-01 | AC-04, AC-05 | Recommendation, Roadmap | Transparent criteria, override rationale and dependency/readiness tests. |
| VG-05 Traceable follow-through/outcomes | BR-13, BR-15–18 | FR-HO-01, FR-FU-01 | AC-05, AC-06; AD-008 | Handoff, Follow-up, Portfolio port | Contract/dedup/lost-ack tests; baseline outcome comparison. |
| VG-06 Human authority | BR-01–04, BR-14–19 | FR-ENG-03, FR-DEC-01 | AC-01, AC-04, AC-08; AD-005 | Authority Service, Decision Register | Negative authorization/conflict/revocation tests; immutable decision audit. |
| VG-07 Modular reusable knowledge | BR-05, BR-23/26 | FR-ASMT-02, FR-KM-01/02 | AC-07; AD-001/003 | Catalog, extension manifest | Compatibility, deprecation, generalization and content-review gates. |
| VG-08 Shared executive/technical understanding | BR-22 | FR-RPT-01; NFR-USA-01, NFR-ACC-01 | AC-06; AD-009 | Reporting/projection API | Semantic reconciliation and accessibility tests for representative formats. |
| VG-09 Confidentiality and bounded AI | BR-24–27 | FR-SEC-01/02; NFR-SEC-01–03, NFR-AI-01/02 | AC-08; AD-006/010 | Governance, AI gateway | Threat model, transfer denial, secret/redaction, prompt-injection and human-review tests. |
| VG-10 Governed repository delivery | BR-28–30 | FR-EXE-01/02; NFR-AUTO-01/02, NFR-REL-01/02 | AC-09/10; AD-007/008 | Target Policy, Publication Coordinator, control-plane interface | Verify non-mutation; authorization freshness; race/ambiguity/idempotency contract tests. |

## Cross-cutting nonfunctional traceability

| Requirement group | Architectural response | Verification evidence |
|---|---|---|
| NFR-AVL-01, NFR-REL-01/02, NFR-REC-01/02 | Portable/manual degraded mode, atomic governed changes, idempotency/reconciliation, backup/restore without replay | Failure/restore/duplicate/lost-ack scenario suite and recovery exercise. |
| NFR-SEC-01–03, NFR-CMP-01 | Security trust boundaries, classification-first policy, least privilege, auditable decisions | Threat model, access matrix, isolation tests, retention/incident approval. |
| NFR-MNT-01–03, NFR-DOC-01/02 | Clean modules, stable IDs, ADRs, catalog versions, architecture/requirements trace | Lint/link/schema/trace checks; reviewed compatibility history. |
| NFR-TST-01/02, NFR-AUTO-01/02 | Pure policy tests, scenario fixtures, contract suites, bounded automated gates | CI evidence mapped to requirement IDs; safe no-op/rollback behavior. |
| NFR-OBS-01/02 | Safe logs/metrics/traces plus separate immutable audit | Redaction/cardinality/correlation/audit completeness and alert tests. |
| NFR-PERF-01/02, NFR-SCL-01 | Stateless scaling, version cache, bounded indexes/workers; targets deferred pending evidence | Pilot workload model and approved measurable performance criteria. |
| NFR-PORT-01, NFR-DEP-01/02 | Open portable artifacts, optional runtime, conceptual deployment units | Offline scenario, export round-trip and environment promotion/rollback. |
| NFR-CFG-01/02 | Typed layered configuration with secure defaults/non-waivable policies | Precedence/conflict/secret reference/rollback tests. |
| NFR-USA-01, NFR-ACC-01 | Progressive human interfaces and accessible projections | Task-based practitioner/sponsor usability and WCAG-aligned review. |

## Interface and use-case coverage

### Next-MVP architecture slice

The [repository release profile](../requirements/NextMVP.md) selects AC-08–11,
ADR-005–008/010–011, Target Policy, bounded Executor, Repository Validator,
Publication Coordinator, and the control-plane/portfolio/Git ports. It excludes
AC-01–07 consulting runtime implementation. FR-EXE-01–02 and the profile's listed
NFRs trace through UC-10 and Sequences 6–7 to deterministic fake-executor,
fake-publication, duplicate/result-replay, failure, and shared-manifest alignment
evidence. The terminal boundary is one validated draft or reuse/no-change and one
canonical correlated result; no merge or downstream lifecycle is included.

| Use cases | Primary components | Interfaces |
|---|---|---|
| UC-01 | Engagement Context, Knowledge Catalog | Human authoring, Command/Query, Catalog |
| UC-02/03 | Evidence Registry, Assessment Engine | Evidence source/reference and domain extension |
| UC-04/05 | Reasoning, Recommendation, Decision, Reporting | Review/decision and projection interfaces |
| UC-06 | Roadmap & Handoff | Portfolio intake contract |
| UC-07 | Follow-up | Evidence and reporting interfaces |
| UC-08 | Knowledge Catalog | Asset manifest/release interface |
| UC-09 | Governance, AI Gateway | AI assistance and authority/classification ports |
| UC-10 | Target Policy, Publication Coordinator | Control-plane, source authority and Git publication contracts |

## Maintenance rule

Every architecture or future implementation change cites affected Vision, BR, FR/NFR, AC, component and interface IDs. New requirements add tests before acceptance. A broken trace blocks release; an unknown external detail links to a validation owner and cannot be marked implemented. Superseded requirements/ADRs retain historical links.
