# Interface Requirements: Organization AI-SDLC Control Plane

## Purpose and parties

This contract defines required interaction between `consulting-playbook` (target
consumer/result producer) and `Young-Consultations/.github` (organization
control-plane owner). The external repository was not inspected for these
requirements; its responsibilities are authoritative vision context and must be
validated with its owner.

## Responsibilities

The control plane SHALL own canonical schemas, supported contract versions,
routing authorization, repository registration/compatibility, shared validation,
correlation semantics, concurrency authorization, and shared failure categories.
Consulting-playbook SHALL own only target validation, repository policy,
repository checks, bounded execution, draft publication, and result production.

## Required inbound event and inputs

The required event is an explicitly routed target-execution request. Its
versioned logical contract MUST provide:

- contract version and stable task, correlation, and delivery/idempotency identity;
- source issue repository and issue identity;
- target repository and, if supplied, requested branch;
- executor, execution mode (`verify` or `implement`), authorized concurrency group;
- explicit draft-only/no-auto-merge requirements;
- sufficient task component/context or an authorized source reference; and
- canonical router-admission status, task type, assignment, and sensitivity data.
  Material changes require a new `task_id` and a new approval; the target does not
  reconstruct or recheck organization approval.

Transport may carry inline content or an immutable artifact reference. Transport
selection is owned by the control plane and MUST preserve identical validated
semantics. No undocumented field may grant authority.

## Required outbound result

For every terminal path where platform operation permits, consulting-playbook
SHALL produce or durably expose the canonical, version-compatible organization
result; it SHALL NOT define a competing local result schema. Canonical outcomes
must distinguish verify success, implement success, existing draft reuse, no
changes, contract rejection, authorization rejection, repository-policy rejection,
validation failure, execution failure, publication failure, and interrupted or
ambiguous execution.

The result MUST contain correlation and delivery identity, result/delivery identity
needed for deduplication, source and target identity, mode, lifecycle timestamps,
terminal outcome, validation evidence, safe failure category/details, and
reconciliation/retry guidance. Branch and draft-PR identity, URL, state, and reuse
disposition are required when applicable. Prompts, tokens, secrets, and raw
sensitive evidence MUST NOT be returned. Re-consuming the same result MUST NOT
cause a second lifecycle transition.

## Behavioral contract

- The target MUST authenticate and authorize the admitted caller, validate contract
  compatibility, and apply repository-local policy. Canonical router admission is
  the organization approval decision; the target MUST NOT recheck a mutable issue
  label or demand a second organization approval. Local repository authorization
  and consulting-content approval remain separate decisions.
- `verify` MUST be non-mutating and non-publishing.
- `implement` MUST remain target-bound, draft-only, non-merging, and subject to
  repository validation/tests and human review.
- Delivery identity MUST remain stable across transport/workflow retries.
- Requested branch, when supplied, MUST exactly match the target's deterministic
  branch for that delivery identity.
- Unknown version, target, executor, mode, missing identity/authority, sensitive
  status, or incompatible safety flags MUST fail closed.

## Failure, retry, and idempotency

Transient transport/platform failure MAY be retried with the same logical
delivery identity. Redelivery SHALL reuse one exactly matching managed draft.
An orphaned branch, conflicting/invalid ownership marker, multiple matches,
non-draft managed PR, or closed/merged prior PR requires manual reconciliation;
the same identity does not authorize replacement. A new identity may be issued
only by the external authority after reconciliation. Serialization is a race
reduction mechanism, not the idempotency guarantee.

## Versioning and compatibility

The target MUST directly consume the three documented schema files at
`c6090e5bbadcc2102a1cb91875466e9decdada1e`. Schemas, workflow interfaces,
immutable target-capability semantics, and the executable shared-fixture oracle
form compatibility release `2.2.0`; internal paths, unverified modules/packages,
and mutable references MUST NOT be used. Current operational activation is
separate router-owned mutable state and MUST NOT be inferred from or enforced by
the target's immutable compatibility pin.
Upgrades require reviewed compatibility evidence and rollback instructions.
Producers MUST NOT silently change field semantics within a version. Consumers
MUST reject unsupported versions. Results MUST use a version compatible with the
accepted input.

## Ownership and assurance

The control-plane owner approves shared contract changes. Consulting-playbook
maintainers approve target policy changes. Joint contract tests SHALL cover
valid input/result, unsupported versions, missing authority, sensitivity,
wrong target, retries, partial failure, and sanitized failures.

## Confirmed interface limitations

The exact target and receiver interfaces, schemas, immutable capability
semantics, and executable fixture oracle are recorded in
[NextMVP.md](NextMVP.md). The organization router owns current activation and
enforces it before dispatch. The canonical receiver owns result transport;
transport acceptance cannot be reported as execution success. This repository
must consume those interfaces without inventing a package/API, competing
receiver, fixture expectation, activation rule, or contract extension. Target
implementation does not enable live routing.
