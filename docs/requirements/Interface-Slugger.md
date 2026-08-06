# Interface Requirements: Slugger

## Purpose and boundary

`Young-Consultations/slugger` owns the AI Software Factory product and controlled
generation of validated software projects. Consulting-playbook owns consulting
analysis and recommendation-to-action patterns. No direct interaction is
confirmed in the inspected repository; this document defines the minimum
contract **only if** an approved recommendation produces Slugger-targeted work.
Slugger was not inspected and no API, event, workflow, or current capability is
assumed.

## Responsibilities

Consulting-playbook SHALL frame evidence-supported outcomes and an evidence-safe,
target-specific proposal. Portfolio governance SHALL approve and initiate work.
The organization control plane SHALL own routing/shared execution contracts.
Slugger SHALL own feasibility validation, product-specific inputs, generation,
validation, outputs, safety controls, and result semantics within its boundary.

## Required inputs and outputs

An input proposal MUST contain the FR-HO-01 fields plus an explicit Slugger target,
desired software outcome, constraints, acceptance outcomes, permitted source
context, classification, dependencies, and approval reference. It MUST NOT
prescribe or assume internal Slugger mechanisms.

If Slugger accepts governed work, its versioned result is expected to identify
source/correlation/delivery, accepted/rejected status, validation outcome,
generated-project or review-artifact references where applicable, limitations,
and sanitized failures. A result is evidence for review, not proof of fitness,
merge approval, compliance, release, or production authorization.

## Required events and behavior

Potential logical events are proposal submitted, governance approved, target
accepted/rejected, generation/validation completed/failed, and result available.
No event is active until all owners approve a versioned interface. Missing
approval, incompatible version, ambiguous target, or prohibited data MUST fail
before generation. Human review and target-specific acceptance remain mandatory.

## Retry, idempotency, versioning, and failure

A future contract MUST define stable delivery identity, duplicate behavior,
partial-effect recovery, cancellation, timeout, replay, compatibility, and
sanitized error categories. Retrying MUST NOT imply a new authorization or
duplicate product. Breaking semantics require a new version, consumer/provider
tests, and rollback. Until validated, handoff remains a portfolio proposal only.

## Ownership, assumptions, and unknowns

Slugger's owner controls its input/result contract and product behavior;
consulting-playbook controls recommendation semantics; portfolio/control-plane
owners control authorization and routing.

There are no confirmed assumptions about Slugger transport, schemas, supported
project types, repositories, validation standards, identity model, or runtime.
Required future validation includes all of those items plus authentication,
permissions, sensitive-data policy, service objectives, artifact ownership and
retention, licensing, failure/recovery, audit evidence, and human review points.
