# Interface Architecture

## Contract rules applying to every interface

All interfaces are versioned, schema-validatable, least-privilege and technology-neutral. Requests identify contract version, message/command ID, correlation ID, actor or system identity, timestamp, classification, purpose and payload where applicable. Responses identify outcome, safe error code, correlation, authoritative revision/status and retry guidance. Receivers validate structure, semantics, authority, freshness, classification, target ownership and compatibility at their trust boundary.

Breaking semantic changes require a new major version and coexistence/migration plan. Additive optional changes require consumer tolerance and a minor version. Documentation-only clarification is a patch. Unknown major versions fail closed.

## Human and presentation interfaces

| Interface | Input → output | Assumptions/validation | Failure handling / ownership |
|---|---|---|---|
| Engagement authoring | Concern, scope, roles, constraints → frame/plan revisions | Required fields, sponsor confirmation, authority conflicts | Preserve draft/gaps; engagement owner owns content. |
| Evidence registration | Reference/provenance/handling → register entry | Purpose, kind, locator uniqueness, classification, permitted use | Restrict unknown; do not copy inaccessible content. Custodian owns source. |
| Analysis/review | Evidence/baseline → findings/options/recommendations | Sufficiency, typed reasoning links, contrary evidence, specialist gates | Remain proposed/disputed; practitioner accountable. |
| Decision | Recommendation + authenticated authority → disposition | Fresh scoped authority, conditions, rationale | Conflict blocks; authority owns decision. No retry without reconfirmation. |
| Reporting/export | View request + access context → reconciled projection | Source revision, access filtering, semantic reconciliation, accessibility | Mark stale/fail rather than diverge. This repository owns transformation. |

Human interfaces must explain consequences, distinguish required/optional/not-applicable, support correction, and never use completion or scores as proof of quality.

## Internal application interfaces

| Interface | Responsibility | Idempotency/retry |
|---|---|---|
| Command API | Request one governed state transition with expected revision | Command ID deduplicates; conflicts require reload, not blind retry. |
| Query API | Return access-filtered canonical record or projection | Non-mutating; safe to retry; exposes data/source revision. |
| Knowledge Catalog API | Resolve/search exact asset versions and applicability | Immutable versions make reads repeatable. |
| Domain Event API | Publish committed facts for audit/projection/orchestration | Event ID deduplicates; consumers checkpoint and replay without external re-effects. |
| Audit API | Append/query access-controlled transition history | Append tied atomically to mutation; never drop silently. |

## Persistence ports

`EngagementRepository`, `KnowledgeRepository`, `AuditRepository` and `ProjectionRepository` expose load/query/save with expected revision, atomic state+event commit where required, access context and retention disposition. They do not expose storage-specific queries to domain policy. A retry after unknown save outcome must read/reconcile by command ID.

## External interface: Organization AI-SDLC control plane

- **Responsibility:** external owner supplies canonical execution input schemas, contract versions, routing, repository registration, shared validation/failure taxonomy and result consumption. This repository supplies only target policy and effect/result.
- **Inbound:** supported version, admitted caller, source and target, task type,
  executor/mode, canonical admission status, classification, delivery/correlation
  identities, concurrency, and publication constraints.
- **Outbound:** the canonical result only, covering every terminal outcome with
  identities, target, timestamps, validation evidence, safe failure/reconciliation
  detail, and branch/draft metadata when applicable.
- **Compatibility and activation:** the non-recursive target pin binds exact
  schema/fixture blobs at recovery candidate `e27b8a5` plus this workflow,
  adapter, and harness. The `ai-sdlc-v2.4.0` receiver remains the published
  rollback baseline. The reviewed `ai-sdlc-v2.4.1` receiver is the
  current candidate and remains pending publication and live verification.
  Current activation is separate mutable router state; the target neither
  consumes historical activation nor administers it. No package or observed
  import is a contract.
- **Validation:** exact immutable schemas first, then caller/target/type, supported
  executor/mode, sensitivity, repository policy, concurrency, and reconciliation.
- **Retries/idempotency:** router retries retain logical delivery identity;
  concurrency is optimization only. Preflight observes branch and pull-request
  state independently before Codex; disagreement is ambiguous and fail-closed.
  Results are correlated and safe to re-consume.
- **Ownership:** `Young-Consultations/.github` owns contract and routing; this repository owns local acceptance and publication policy.

## External interface: Portfolio Tasks

- **Recommendation intake input:** source engagement/recommendation/decision references, disposition and conditions, outcome/scope/exclusions, independently understandable proposed tasks by owner, acceptance outcomes, dependencies, risks, readiness, priority rationale, classification, transfer authorization, correlation and idempotency.
- **Execution-source input:** canonical issue reference plus stable structured
  repository-change approval evidence, executor assignment and classification.
- **Output expected:** accepted/rejected acknowledgement, external identity/version, authoritative status and safe reason.
- **Assumptions/unknowns:** exact schema, transport, labels/state model, deduplication, cancellation, permissions, retention and SLA are unknown until confirmed.
- **Validation:** never infer authority/classification from prose or a mutable
  label; validate evidence binding authority, approved revision/scope and target,
  and apply canonical edit/withdrawal/revocation/freshness rules. Treat cached
  state as advisory. Consulting approval remains a separate domain concept.
- **Retries:** transport failure may retry with identical idempotency identity after reconciliation; business rejection or revoked authority may not.
- **Ownership:** Portfolio Tasks owns intake, priority, approval and task state; this repository owns proposal construction and traceability.

## External interface: Slugger

No direct integration is confirmed. If authorized, the contract must define intended product outcome, approved source decision/task, minimum requirements/context, target ownership, classification/transfer, correlation/idempotency, version, validation result, generated artifact reference, limitations and human review points. Slugger owns generation semantics; this repository owns consulting method and an authorized proposal. No implementation, transport or schema is assumed.

## External interface: client evidence systems

Input is a purpose-bound query or human-provided reference; output is authorized source content or locator metadata. This repository records provenance and limitations, not source authority. Access denial, deletion, change or unavailability is recorded, not bypassed. Automated retrieval is optional and requires separate authentication, data-processing and rate-limit contracts.

## External interface: AI assistance provider

Input is minimum authorized context plus declared task, prohibited actions and output form. Output is untrusted labeled analysis plus provider/model/request metadata permitted for audit. Secrets and unknown/restricted content are excluded unless a designated authority explicitly permits the exact transfer. No automatic retries where duplication increases cost/exposure; transient retry must be bounded. Provider output is never an authoritative command.

## External interface: identity and authority source

Input is principal, action, subject and required freshness; output is authenticated identity and scoped permit/deny/unresolved with policy revision. Timeout/unresolved fails closed for governed action. Credentials/tokens never enter domain records or logs. Provider and data model are unknown.

## Compatibility and conformance

Each adapter ships consumer/provider contract tests, valid/invalid fixtures, maximum-size and classification tests, retry/lost-acknowledgement scenarios, and a support matrix. Ordinary target conformance replaces Codex and Git publication with deterministic fakes and has no external write credentials. Drift from organization-owned fixtures blocks merge. A real-Codex boundary is separately controlled and excluded from ordinary CI. Contract owners approve production compatibility. Deprecation states announcement, overlap window, migration and rollback; historical records remain readable under their original semantics.
