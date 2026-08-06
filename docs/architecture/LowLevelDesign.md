# Low-Level Design

## Dependency rule and logical organization

The design names logical modules, not directories or programming constructs. Future implementation SHALL keep domain modules free of infrastructure dependencies and expose application use cases through ports.

```text
presentation -> application -> domain
                         \-> ports <- adapters
knowledge definitions ------^
```

## Modules and public interfaces

| Module | Public operations | Principal invariants |
|---|---|---|
| `engagement` | frame, reviseFrame, tailorPlan, mapAuthority, close | Sponsor/owner present; revisions retained; unresolved authority blocks final decisions. |
| `knowledge` | listApplicableAssets, resolveVersion, proposeAsset, reviewAsset, deprecateAsset | Stable ID, owner, applicability, status and compatibility required. |
| `evidence` | planRequest, registerReference, validateReference, assessSufficiency | Purpose/minimum data/classification required; evidence kinds remain distinct. |
| `assessment` | establishBaseline, applyDomainMethod, recordCapabilityJudgment | Scope/time/source/omission visible; contextual anchors required. |
| `reasoning` | proposeFinding, validateFinding, disputeFinding, addImplication, analyzeCause, compareOptions | Typed links; contrary evidence retained; causation claims justified. |
| `recommendation` | propose, prioritize, revise, supersede | Criteria declared; human overrides have rationale and authority. |
| `decision` | decide, condition, defer, supersede | Actor must hold scoped authority; previous state immutable. |
| `roadmap` | sequence, assignOwner, recordDependency, revise | Only approved/conditional items; conditions propagate. |
| `handoff` | prepare, validate, submit, reconcile | Decomposed by target; no local approval inference; idempotent identity. |
| `reporting` | projectAudienceView, reconcileViews, export | One canonical source; material truth cannot diverge. |
| `followup` | recordObservation, compareBaseline, evaluateOutcome, proposeLesson | Attribution limits and changed context explicit. |
| `governance` | classify, authorizeUse, authorizeTransfer, authorizeAI, auditTransition | Unknown is restricted; authorization is purpose/destination/time specific. |
| `execution` | verifyDispatch, preflightPublication, executeBoundedChange, publishDraft, buildResult | Fresh authority validation; deterministic publication; ambiguity blocks. |

## Command contract

Every mutating use case accepts a command envelope:

| Field | Meaning |
|---|---|
| `commandId` | Unique attempt identity. |
| `correlationId` | End-to-end workflow identity. |
| `subjectId` / `expectedRevision` | Optimistic concurrency target. |
| `actor` and `authorityContext` | Authenticated principal and asserted scope, revalidated by policy. |
| `classificationContext` | Handling and transfer constraints. |
| `occurredAt` | Claimed business time where relevant; system recording time is separate. |
| `payloadVersion` / `payload` | Explicitly versioned request. |

Results are `Accepted`, `Rejected`, `Conflict`, `Forbidden`, `Unavailable`, or `Indeterminate`; each contains a safe code, correlation ID and retry guidance. Domain validation failures are not exceptions to be blindly retried.

## Internal interfaces

```text
KnowledgeCatalogPort: resolve(assetId, version), search(applicability), history(assetId)
EngagementRepositoryPort: load(id), save(aggregate, expectedRevision)
EvidenceReferencePort: verifyLocator(ref), checkAccess(ref, actor)
AuthorityPort: authorize(actor, action, subject, freshAt)
ClassificationPort: evaluate(item, purpose, destination)
PortfolioPort: validateContract(), submit(proposal, idempotencyKey), status(externalId)
ControlPlanePort: validateExecution(input), emitResult(result)
PublicationPort: inspect(identity), createDraft(identity, change), result(identity)
AuditPort: append(events), query(subject, accessContext)
ProjectionPort: rebuild(subject), read(view, accessContext)
ClockPort / IdentityPort: now(), newId()
AIAssistancePort: propose(boundedContext, declaredPurpose), metadata()
```

Ports specify semantics and conformance tests, not transport.

## Aggregate transaction boundaries

- Engagement is the consistency boundary for frame, tailoring and authority references.
- Finding controls its validation lifecycle and evidence/limitation links.
- Recommendation controls prioritization and recommendation state; a Decision is a separate authority-owned record linked to it.
- Roadmap controls sequencing but references, rather than absorbs, recommendations.
- Knowledge Asset controls its release lifecycle and immutable versions.
- Delivery controls one logical handoff/publication identity.

Cross-aggregate orchestration uses sagas/process managers with compensating status, never distributed transactions. A failed external submission leaves a resumable local submission attempt, not a fictitious portfolio task.

## Validation order

1. Parse and structural validation.
2. Contract/version compatibility.
3. authentication and fresh authority lookup.
4. classification, purpose and destination policy.
5. aggregate revision and lifecycle guard.
6. business invariants and referential integrity.
7. commit state/audit atomically.
8. perform or enqueue external effect with idempotency identity.
9. reconcile acknowledgement and update status.

## Extension points

- New engagement types compose existing lifecycle stages.
- New assessment domains implement the domain-method contract.
- Rating schemes supply contextual anchors and validation without changing findings.
- Renderers consume access-filtered projections.
- Storage, identity, portfolio, control-plane and AI adapters implement ports.
- Policy packs may tighten but never silently weaken non-tailorable rules.

Extensions declare identifier, owner, semantic version, compatibility, applicability, required inputs, produced outputs, failure modes, security classification, tests and deprecation policy.

## Concurrency, consistency and replay

Use optimistic concurrency for governed records. State transition plus audit event is atomic within its owner boundary. Projections may be eventually consistent and expose source revision. External submissions are at-least-once attempts with idempotent effects. Replaying events/projections must never repeat an external effect or re-authorize an expired action.

## Testing seams

Pure policy rules use table-driven tests; aggregate scenarios cover state transitions; ports have provider-neutral contract suites; adapters use owner-issued fixtures; reports use reconciliation/golden semantic tests; security tests cover cross-tenant/classification denial; workflow tests cover lost acknowledgements, collisions and ambiguous publications.
