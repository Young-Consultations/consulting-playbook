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
- stable approval evidence (including authority, approved revision/scope, target,
  decision time, freshness and revocation semantics), assignment, and sensitivity
  data suitable for independent target validation.

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

- The target MUST validate contract compatibility before use, then validate stable
  canonical approval evidence and repository-local authority. Routing admission
  is necessary but not sufficient target authorization.
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

The target MUST consume only the documented public API of an explicitly supported
immutable organization contract release. Package, schema, workflow interface,
registry expectations, and shared fixtures MUST be pinned and qualified as one
compatible release unit; internal paths and unverified modules MUST NOT be used.
Consumer-driven fixtures MUST demonstrate that public API before enablement.
Upgrades require reviewed compatibility evidence and rollback instructions.
Producers MUST NOT silently change field semantics within a version. Consumers
MUST reject unsupported versions. Results MUST use a version compatible with the
accepted input.

## Ownership and assurance

The control-plane owner approves shared contract changes. Consulting-playbook
maintainers approve target policy changes. Joint contract tests SHALL cover
valid input/result, unsupported versions, missing authority, sensitivity,
wrong target, retries, partial failure, and sanitized failures.

## Known assumptions, unknowns, and validation

**Implementation evidence, not an approved dependency:** repository automation
currently references a contract version/release and package paths and constructs a
result artifact. Those observations do not prove a documented public API,
compatible release unit, approval-proof semantics, or accepted return channel.

**Unknown / external confirmation required:** immutable release, documented public
package API, stable approval-proof semantics, result-return transport, shared
fixture locations, registry enablement, canonical lifecycle vocabulary, external
schema source, retention/SLA, authentication lifecycle, compatibility window,
result consumer behavior, incident ownership, and recovery authorization.

**Required validation:** control-plane owners SHALL confirm fields, state
semantics, transport, authentication, permissions, timeouts, error taxonomy,
retention, support/incident process, test fixtures, upgrade, and rollback before
a new interface version is accepted.
