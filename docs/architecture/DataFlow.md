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
  participant Store as Record Port
  participant Audit as Audit Port
  participant Ext as External Port
  User->>App: versioned command + actor + expected revision
  App->>Policy: validate authority/classification/state/invariants
  alt invalid
    Policy-->>App: typed rejection
    App-->>User: safe error + remediation
  else valid local transition
    App->>Store: atomically save revision + domain events
    Store->>Audit: append auditable transition
    opt external effect required
      App->>Ext: command + correlation + idempotency
      Ext-->>App: acknowledgement / indeterminate / rejection
      App->>Store: record integration status
    end
    App-->>User: accepted result + revision
  end
```

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
  Schema --> Fresh[Fresh source issue, approval, assignment, sensitivity check]
  Fresh --> Mode{Mode}
  Mode -- verify --> Checks[Non-mutating policy/repository checks]
  Checks --> Result[Canonical result]
  Mode -- implement --> Preflight[Inspect deterministic branch and all PR states]
  Preflight --> State{Publication state}
  State -- existing valid draft --> Reuse[Return prior PR]
  State -- ambiguity/prior closed/orphan --> Block[Fail closed; preserve evidence]
  State -- new --> Change[Bounded AI change]
  Change --> Validate[Repository validation and tests]
  Validate --> Commit[Deterministic branch publication attempt]
  Commit --> Draft[Create/requery one managed draft]
  Reuse --> Result
  Block --> Result
  Draft --> Result
```

## Transformation rules

- Normalization must not erase original values, uncertainty or provenance.
- Derived scores retain formula/policy version and inputs; they are advisory.
- Redaction creates a derivative with a link and classification, not a replacement of authoritative source.
- Report projections include source revision and “as of” time.
- External adapter translation validates both inbound and outbound structures.
- Correlation identifiers are safe metadata; prompts, secrets and confidential content are excluded from operational telemetry.

## Failure and recovery flow

Validation rejection returns to the responsible actor. Concurrency conflict reloads current revision before a deliberate retry. External timeout becomes `indeterminate`; reconciliation precedes resubmission. An unavailable evidence source becomes a limitation. A failed projection can be rebuilt. Audit write failure blocks governed mutation. Publication ambiguity requires operator review and a newly authorized logical identity when replacement is intended.
