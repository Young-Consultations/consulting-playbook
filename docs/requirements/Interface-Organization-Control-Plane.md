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
`f2491872976a4dcc1633997954c03c07cbc4fced`. Schema, workflow interface, registry
expectations, and shared-fixture manifest form release `2.2.0`; internal paths,
unverified modules/packages, mutable `main`, and the unavailable release tag MUST
NOT be used. The incomplete fixture payload set prevents an executable shared-
fixture conformance claim before enablement.
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

The exact target and receiver interfaces, schemas, registry entry, and manifest
are recorded in [NextMVP.md](NextMVP.md). The registry is disabled. The result
receiver is an organization-owned fail-closed skeleton, so successful live return
is unavailable and transport acceptance cannot be reported as execution success.
The shared scenario manifest lacks complete executable input/expected-output
fixtures. Organization owners must implement the receiver, complete fixtures, and
enable the registry before live use. This repository must not fill those gaps by
inventing a package/API, competing receiver, fixture, or contract extension.
