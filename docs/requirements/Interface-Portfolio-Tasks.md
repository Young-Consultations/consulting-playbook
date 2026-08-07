# Interface Requirements: Portfolio Tasks

## Purpose and parties

This contract separates consulting recommendation handoff from authoritative
portfolio governance. `consulting-playbook` produces evidence-safe task
proposals/patterns and may execute work targeted back to itself.
`Young-Consultations/portfolio-tasks` is expected to own structured intake,
governance metadata, prioritization, approval, and initiation. That repository
was not inspected; all expectations require owner validation.

## Required recommendation-to-intake contract

### Inputs to portfolio intake

For each independently governable target, a handoff package SHALL provide:

- stable handoff identity and source recommendation/decision references;
- title, business/customer outcome, rationale, target repository, and owner role;
- scope, exclusions, expected outputs/outcomes, and testable acceptance criteria;
- dependencies, sequencing, risks, assumptions, constraints, and urgency rationale;
- evidence-safe context or authorized links rather than raw evidence by default;
- information classification and transfer-review disposition;
- consulting decision status/authority/date; and
- unresolved questions and specialist/reviewer needs.

Receipt MUST NOT imply portfolio acceptance, priority, approval, or execution.
Cross-repository work MUST be decomposed into one package per target ownership
boundary. Portfolio intake SHALL return or expose a stable authoritative task
reference, intake disposition, validation errors, and governance status when the
external owner accepts this contract.

## Required execution-source contract

When an approved portfolio issue initiates work in consulting-playbook, the
interface SHALL provide the canonical control-plane request defined by
[Interface-Organization-Control-Plane.md](Interface-Organization-Control-Plane.md).
Portfolio-tasks owns approval truth; the control plane owns routing admission.
The target independently validates canonical, stable approval evidence and its
own repository policy before execution. A mutable `status:approved` label is
workflow state, not sufficient proof: it may legitimately have become
`status:queued` after admission. The evidence must bind the approving authority,
approved source revision/content digest, target, scope, decision and time, and
support the canonical freshness/revocation rules. Material edits, withdrawal,
revocation, staleness, invalid authority, or target mismatch fail closed. If the
canonical contract cannot carry or reference sufficient stable proof, live
enablement is blocked pending an organization-level contract decision.

Approval of a consulting recommendation is not approval to change this repository.
Repository-change execution requires its own portfolio authority and evidence.
The target result SHALL link source, delivery, run, and draft PR when applicable
and preserve human review.

## Events and lifecycle

Required logical events are `handoff proposed`, `intake accepted/rejected/needs
clarification`, `approval changed`, `execution requested`, and `execution result
available`. Optional future status synchronization MUST be separately versioned;
consulting-playbook SHALL NOT treat cached status as authoritative.

## Failure, retry, and idempotency

Handoff submission SHALL use stable identity so retries do not create duplicate
authoritative tasks. Validation failures SHALL identify missing/invalid fields
without leaking protected evidence. Conflicting target, classification, decision
authority, or duplicate identity SHALL fail closed for human resolution. An
execution retry follows the delivery semantics in the control-plane interface.

## Versioning and ownership

Portfolio-tasks owns intake/governance schema and lifecycle state. The control
plane owns execution schemas. Consulting-playbook owns handoff content guidance
and evidence minimization. Every exchange MUST state contract version and owners;
breaking changes require compatibility plan, fixtures, and migration/rollback.

## Assumptions, unknowns, and validation required

**Assumptions:** GitHub issues may be the portfolio record and durable links may
provide traceability; neither assumption defines an API.

**Unknowns:** actual intake fields/transports, issue templates, labels/states,
authentication, duplicate handling, acknowledgements, update/cancellation
behavior, service objectives, retention, permissions, and result ingestion.

**Validate with portfolio owners:** authoritative state model and authority,
contract/schema, transport/events, classification compatibility, idempotency,
error/retry semantics, correlation, access/retention, status synchronization,
test fixtures, operational ownership, and recovery process.
