# Data Flow Design

## Data classes and boundaries

| Flow object | Source | Transformation | Destination | Authority |
|---|---|---|---|---|
| Concern/context | Sponsor/practitioner | Frame, scope and decision purpose | Engagement context | Sponsor validates |
| Evidence request | Engagement plan | Minimize and classify | Evidence custodian | Custodian controls source |
| Evidence reference | Client/source/participant | Register provenance, kind, limitation and access | Evidence register | Source remains external |
| Analysis | Practitioner + evidence | Sufficiency, baseline, finding, implication, options | Reasoning graph | Consultant accountable; reviewers validate |
| Recommendation | Reasoning graph | Prioritization and feasibility | Decision authority | Advice only |
| Decision | Named authority | Validate scope, record rationale/conditions | Decision register | Authority owns disposition |
| Action proposal | Approved decision | Decompose/minimize/version | Portfolio intake | External owner accepts/rejects |
| Report | Canonical reasoning graph | Access filtering and audience projection | Stakeholders | No new facts/state |
| Lesson proposal | Follow-up | Generalize, confidentiality/content review | Knowledge catalog | Maintainer publishes |
| Execution dispatch/result | Control plane | Repository policy/validation/publication | Draft PR + control plane result | External contract; local effect |

## Primary consulting flow

```mermaid
flowchart TD
  I[Concern and desired outcome] --> V{Frame valid?}
  V -- no --> G[Expose gaps / obtain sponsor validation]
  G --> I
  V -- yes --> T[Tailor methods and authority map]
  T --> EP[Plan purposeful evidence]
  EP --> C{Collection authorized and classified?}
  C -- no --> L[Reject, minimize or record limitation]
  C -- yes --> ER[Register access-safe reference and provenance]
  ER --> S{Sufficient for decision need?}
  S -- collect more --> EP
  S -- narrow/stop --> L
  S -- proceed --> B[Current-state baseline and assessment]
  B --> F[Propose finding + contrary evidence]
  F --> Q{Validated or limitation accepted?}
  Q -- no --> F
  Q -- yes --> O[Implications, causes, options]
  O --> R[Recommendation and declared prioritization]
  R --> D{Authority decision}
  D -- reject/defer --> RP[Reconciled reporting]
  D -- approve/conditional --> M[Roadmap; propagate conditions]
  M --> H[Target-specific handoff proposal]
  H --> X[External portfolio intake]
  D --> RP
```

## Command, event and query flow

```mermaid
sequenceDiagram
  actor User
  participant App as Application Service
  participant Policy as Domain Policy
  participant Tx as Governed Transaction Port
  participant Store as Record Port
  participant Audit as Audit Port
  participant Ext as External Port
  User->>App: versioned command + actor + expected revision
  App->>Policy: validate authority/classification/state/invariants
  alt invalid
    Policy-->>App: typed rejection
    App-->>User: safe error + remediation
  else valid local transition
    App->>Tx: commit revision + events + audit record
    Tx->>Store: stage revision + domain events
    Tx->>Audit: stage auditable transition
    alt state or audit stage fails
      Tx-->>App: roll back all staged writes
      App-->>User: safe failure; governed state unchanged
    else atomic commit succeeds
      Tx-->>App: committed revision + audit identity
      opt external effect required
        App->>Ext: command + correlation + idempotency
        Ext-->>App: acknowledgement / indeterminate / rejection
        App->>Tx: atomically record integration status + audit
      end
      App-->>User: accepted result + revision
    end
  end
```

The governed transaction boundary commits the authoritative revision, its domain events and the required audit record atomically. An implementation may instead commit the state, events and an audit outbox entry in one store transaction, but that outbox entry is part of the governed record and must be durably accepted before the mutation succeeds; a relay may subsequently deliver it idempotently to a separate audit sink. Failure to stage any required item rolls back the complete transaction, so no governed revision can become visible without durable audit intent.

Events are past-tense facts such as `FindingValidated`, `DecisionRecorded`, `HandoffAcknowledged` and `KnowledgeAssetPublished`. Event consumers may rebuild views or trigger authorized orchestration; they must not infer approval from event presence.

## Recommendation-to-portfolio flow

Inputs include traceable approved/conditional decision, conditions, business outcome, scope/exclusions, acceptance outcomes, target owner, dependencies, risks, classification, source links, correlation and idempotency identity. The local system validates completeness and destination authorization, submits to the external intake contract, records acknowledgement, and reconciles external state. It never assigns authoritative external IDs or silently retries business rejection.

## AI assistance flow

```mermaid
flowchart LR
  Need[Declared assistance purpose] --> Min[Select minimum context]
  Min --> Gate{Classification + destination + AI use authorized?}
  Gate -- no/unknown --> Deny[Human-only workflow]
  Gate -- yes --> AI[Provider adapter]
  AI --> Label[Label output + model/purpose/provenance]
  Label --> Review{Professional review}
  Review -- reject --> Archive[Record disposition as permitted]
  Review -- revise/accept --> Human[Human-authored governed command]
```

AI cannot write authoritative state directly. Provider prompts/responses are not logged by default and sensitive input cannot cross a boundary without specific authorization.

## Target execution flow

```mermaid
flowchart TD
  Dispatch[Canonical dispatch] --> Schema[Control-plane contract validation]
  Schema --> Proof[Stable portfolio approval proof + target local policy]
  Proof --> Mode{Mode}
  Mode -- verify --> Checks[Non-mutating policy/repository checks]
  Checks --> Result[Canonical result]
  Mode -- implement --> Preflight[Inspect deterministic branch and all PR states]
  Preflight --> State{Publication state}
  State -- existing valid draft --> Reuse[Return prior PR]
  State -- ambiguity/prior closed/orphan --> Block[Fail closed; preserve evidence]
  State -- new --> Change[Bounded AI change]
  Change --> Validate[Repository validation and tests]
  Validate -- no changes --> NoChange[Canonical no-change result]
  Validate --> Commit[Deterministic branch publication attempt]
  Commit --> Draft[Create/requery one managed draft]
  Reuse --> Result
  Block --> Result
  Draft --> Result
  NoChange --> Result
```

Routing admission and mutable portfolio labels are not authorization proof. The
proof binds authority, approved revision/scope and target and is checked under the
canonical freshness/revocation rules. Result delivery uses the organization-owned
transport and an idempotent result identity; a lost acknowledgement is reconciled
without repeating the visible lifecycle transition.

## Transformation rules

- Normalization must not erase original values, uncertainty or provenance.
- Derived scores retain formula/policy version and inputs; they are advisory.
- Redaction creates a derivative with a link and classification, not a replacement of authoritative source.
- Report projections include source revision and “as of” time.
- External adapter translation validates both inbound and outbound structures.
- Correlation identifiers are safe metadata; prompts, secrets and confidential content are excluded from operational telemetry.

## Failure and recovery flow

Validation rejection returns to the responsible actor. Concurrency conflict reloads current revision before a deliberate retry. External timeout becomes `indeterminate`; reconciliation precedes resubmission. An unavailable evidence source becomes a limitation. A failed projection can be rebuilt. Audit write failure blocks governed mutation. Publication ambiguity requires operator review and a newly authorized logical identity when replacement is intended.
