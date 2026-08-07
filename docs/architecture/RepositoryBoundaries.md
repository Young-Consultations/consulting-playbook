# Repository Boundaries

## Boundary statement

`consulting-playbook` owns reusable consulting semantics and the repository-local policy for accepting approved changes. It does not become the owner of a record merely because it references, displays, exports or transports that record.

## Responsibilities owned here

| Capability | Owned responsibility |
|---|---|
| Consulting practice | Principles, engagement lifecycle, methods, evidence guidance and domain assessment guidance. |
| Reasoning semantics | Definitions and invariants for findings, implications, causes, options, recommendations and uncertainty. |
| Action preparation | Prioritization, roadmap and recommendation-to-task proposal patterns. |
| Communication | Executive/technical templates and material reconciliation rules. |
| Knowledge governance | Catalog, stable IDs, reviews, versions, compatibility, lessons generalization and deprecation. |
| Safety guidance | Classification/minimization/AI-use and transfer gates at this boundary. |
| Local quality | Documentation, architecture, validators, tests and release evidence. |
| Target execution | Exact-target policy, repository checks, deterministic draft publication effect and canonical result production. |

## Explicitly not owned

- Raw client evidence systems, legal custody, client identity or data-processing policy.
- The authoritative organization backlog, task priority, approval or lifecycle.
- Organization-wide AI-SDLC schemas, routing, registry, shared failure taxonomy or contract compatibility.
- Slugger implementation or generated-product semantics.
- Another target repository's source, architecture, build or release.
- Authentication infrastructure unless separately scoped.
- Autonomous recommendations, decisions, approvals, merge, release or production operation.
- Certification/compliance conclusions merely from a completed method or template.

## Expected collaborators and contracts

| Collaborator | Supplies | Receives | Validation required |
|---|---|---|---|
| Client sponsor/authority | Outcomes, boundaries, authority and decisions | Findings, options, recommendations, reports | Identity, scope, decision authority, handling. |
| Evidence custodian | Authorized references/source access | Purposeful minimal requests | Provenance, classification, permitted use, access. |
| Portfolio Tasks | Intake acknowledgement, approval truth and stable repository-change approval evidence | Approved/conditional action proposals | Proof authority/revision/target, classification, idempotency, revocation/freshness. |
| Organization control plane | Canonical contract, routing admission and result transport | Canonical execution result | Immutable public API/release, exact target, registry and shared fixtures. |
| Target repository/human reviewer | Repository rules and review decision | One bounded managed draft | Repository policy, tests, marker ownership; human merge. |
| Slugger (unconfirmed) | Defined result only if contracted | Authorized product proposal only | Entire contract and ownership relation remain to validate. |

## Data ownership

| Data | Authoritative owner | This repository's permissible role |
|---|---|---|
| Knowledge asset definition/version | Consulting-playbook maintainers | Store, publish and deprecate. |
| Engagement frame/analysis | Engagement's designated owner under client policy | Create/manage only in an approved location and scope. |
| Evidence content | Source/custodian | Reference by default; copy only when authorized/minimized. |
| Decision | Named human authority | Record immutable disposition and rationale. |
| Portfolio item/status | Portfolio Tasks | Propose and cache labeled observation; reconcile. |
| AI output | No inherent authority; governed recipient controls permitted record | Label provenance; require review. |
| Execution schema/routing state | Organization control plane | Consume; never locally redefine. |
| Draft branch/PR publication | Target repository under review governance | Create/reuse exactly one managed draft per identity. |

## Lifecycle ownership

This repository owns knowledge asset proposal through deprecation. The engagement owner owns engagement opening through closure and authorized disposal. Custodians own evidence retention/deletion. A decision authority owns disposition; roadmap owners own local planning until external intake. Portfolio Tasks owns task acceptance onward. The control plane owns dispatch lifecycle; this target owns only receipt-to-result behavior. Human target maintainers own review/merge and post-merge lifecycle.

## Boundary enforcement

Adapters validate incoming identities, canonical router admission, local policy and
versions, translate without importing external domain models or undocumented
package paths, and store only necessary references. Outgoing flows use the canonical result
with classification, version, correlation and idempotency. No cached value or
mutable label grants authority. Unknown capability blocks dependent acceptance.

## Change-control rule

A boundary change requires a reviewed Vision/requirements update, responsible owners on both sides, a contract and compatibility plan, security/privacy assessment, traceability update, conformance tests and rollback. Code or workflow convenience alone cannot redefine ownership.
