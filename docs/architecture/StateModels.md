# State Models

## State-model rules

Transitions require actor, time, rationale, prior state, expected revision and applicable authority. Invalid transitions fail without partial mutation. Supersession preserves history. “Unknown,” “disputed,” “not applicable” and blank are not lifecycle shortcuts.

## Engagement

```mermaid
stateDiagram-v2
  [*] --> Proposed
  Proposed --> Active: sponsor validates frame
  Proposed --> Cancelled: owner cancels
  Active --> Paused: authorized pause
  Paused --> Active: resume/revalidate context
  Active --> Closed: outcomes/records disposition reviewed
  Active --> Cancelled: authorized cancellation
  Closed --> [*]
  Cancelled --> [*]
```

Entry to Active requires owner/sponsor, scope, purpose and visible gaps. Closure requires final status, unresolved items and retention/handoff disposition; it does not imply recommendations completed.

## Finding

```mermaid
stateDiagram-v2
  [*] --> Proposed
  Proposed --> Validated: sufficient evidence or accepted limitation
  Proposed --> Disputed: reviewer disagreement
  Disputed --> Proposed: revised/reconsidered
  Validated --> Disputed: material contrary evidence
  Proposed --> Withdrawn: proponent withdraws
  Validated --> Superseded: replacement finding validated
  Disputed --> Superseded: replacement finding validated
  Superseded --> [*]
  Withdrawn --> [*]
```

Validated is prohibited when material support is insufficient and no proper limitation acceptance exists. Dispute preserves both positions and evidence.

## Recommendation and decision

```mermaid
stateDiagram-v2
  [*] --> Proposed
  Proposed --> Approved: scoped authority approves
  Proposed --> Rejected: scoped authority rejects
  Proposed --> Deferred: scoped authority defers
  Proposed --> Conditional: scoped authority sets conditions
  Deferred --> Proposed: reconsider with new revision
  Conditional --> Approved: conditions satisfied/decision updated
  Approved --> Completed: outcome closure criteria met
  Conditional --> Completed: defined conditional work closed
  Approved --> Superseded: new decision
  Conditional --> Superseded: new decision
  Rejected --> Superseded: new decision
  Completed --> [*]
  Superseded --> [*]
```

Recommendation content revisions and authority decisions are separate records. Entry to roadmap is allowed only from Approved or Conditional, with all conditions attached. Completion is not proof of benefit; follow-up evaluates outcome.

## Knowledge asset

```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> InReview: completeness/security checks pass
  InReview --> Draft: changes requested
  InReview --> Published: authorized content approval
  Published --> Deprecated: successor or end-of-support announced
  Published --> Withdrawn: safety/integrity issue
  Deprecated --> Withdrawn: support ends
  Deprecated --> Published: exceptional reviewed reinstatement
```

Published versions are immutable; updates produce a new version. Client-derived lessons require confidentiality/generalization review before InReview.

## Handoff

```mermaid
stateDiagram-v2
  [*] --> Prepared
  Prepared --> Validated: decision/conditions/contract/transfer valid
  Validated --> Submitted: outbound attempt recorded
  Submitted --> Acknowledged: owner accepts and returns identity
  Submitted --> Rejected: owner business rejection
  Submitted --> Indeterminate: timeout/lost response
  Indeterminate --> Acknowledged: reconciliation finds accepted record
  Indeterminate --> Rejected: reconciliation confirms rejection
  Indeterminate --> Validated: confirmed absent and authority still current
  Prepared --> Cancelled: owner cancels
  Validated --> Cancelled: authority revoked before submission
```

Retry from Indeterminate is reconciliation-first and uses the same idempotency identity. Revoked authority cannot be restored by retry.

## Target delivery/publication

```mermaid
stateDiagram-v2
  [*] --> Received
  Received --> Rejected: schema/policy/fresh authority invalid
  Received --> Verified: verify mode checks complete
  Received --> Ready: implement authorized + publication absent
  Received --> Reused: exact valid managed draft exists
  Received --> Blocked: ambiguous/orphaned/closed prior state
  Ready --> Executing
  Executing --> ValidationFailed
  Executing --> Publishing: candidate validates
  Publishing --> Published: exact managed draft confirmed
  Publishing --> Blocked: conflict cannot reconcile safely
  Verified --> [*]
  Reused --> [*]
  Published --> [*]
  Rejected --> [*]
  ValidationFailed --> [*]
  Blocked --> [*]
```

Blocked recovery is manual evidence-preserving reconciliation. A replacement requires a newly authorized logical delivery identity; the same identity cannot overwrite or reopen history.

## Evidence reference

Requested → Available → Validated or Disputed; Available/Validated may become Inaccessible or Retired. Inaccessible records retain provenance and limitation. Retired means no longer usable under policy, not that history is erased contrary to retention obligations.
