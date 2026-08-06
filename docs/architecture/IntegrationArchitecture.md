# Integration Architecture

## Integration posture

External systems are authoritative only for their owned state. Anti-corruption adapters translate their contracts into the playbook's ports. No other repository's implementation, availability, schema or eventing model is assumed.

## Integration register

| Collaborator | Known | Assumed (must validate) | Unknown / decision required |
|---|---|---|---|
| Organization `.github` control plane | Owns AI-SDLC contracts, routing, registry, compatibility and shared verification; currently dispatches v2 target work. | Canonical logical identity remains stable across retry. | Future versions, auth, transports, SLA, result retention, incident process. |
| `portfolio-tasks` | Owns intake, governance, priority, approval and initiation. | Can acknowledge deduplicated recommendation proposals and expose fresh source state. | Exact schema/events/states, cancellation, permissions, retention, synchronization. |
| `slugger` | Owns AI Software Factory product. | None; direct interaction is not confirmed. | Whether integration exists and every contract detail. |
| Client evidence systems | Own source evidence. | Can provide authorized access-safe references. | Systems, formats, jurisdictions, authentication, retention and availability. |
| Identity/authority provider | Needed only for an application runtime. | Can assert principal and scoped roles. | Provider, tenancy, federation, freshness and break-glass model. |
| AI provider | Optional bounded assistance. | Can return labeled suggestions without direct state access. | Approved providers/models, residency, training/retention, quotas and incident controls. |
| Git hosting/CI | Current executor uses GitHub concepts. | Draft PR/repository controls support required safeguards. | Whether consulting core depends on hosting at all (it should not). |

## Patterns

- **Synchronous query:** fresh authority/classification/source validation when an immediate decision is required.
- **Asynchronous command with acknowledgement:** handoff and execution result where external processing may outlive request.
- **Domain event:** local audit/projection fact. External delivery is not assumed unless a contract says so.
- **File/artifact exchange:** portable knowledge, reports and contract payloads, with schema/version/checksum/classification.
- **Manual exchange:** valid baseline for consulting artifacts; requires the same recorded authority and acknowledgement.

## Synchronization expectations

Local records store external references and last observed version/status, clearly labeled non-authoritative. Before an irreversible or privileged transition, query the authoritative boundary at required freshness. Reconciliation compares idempotency identity, external ID, revision, status and payload digest. Divergence produces an explicit conflict for an owner; last-write-wins is prohibited for governed state.

```mermaid
sequenceDiagram
  participant CP as Consulting Playbook
  participant AD as Anti-corruption Adapter
  participant EX as External Owner
  CP->>AD: submit canonical proposal + idempotency/correlation
  AD->>AD: validate mapping, version, classification
  AD->>EX: owner-defined contract
  alt accepted
    EX-->>AD: external ID + revision + status
    AD-->>CP: acknowledged mapping
  else rejected
    EX-->>AD: safe business reason
    AD-->>CP: rejected; no blind retry
  else timeout/unknown
    AD-->>CP: indeterminate
    CP->>AD: reconcile same identity
    AD->>EX: query by identity/reference
    EX-->>AD: authoritative outcome
    AD-->>CP: reconciled result
  end
```

## Messaging and event envelope expectations

Where messaging is selected, an envelope carries message ID, type, semantic version, producer, occurred/recorded times, correlation and causation IDs, tenant/engagement reference where permitted, classification, payload digest and payload. Consumers validate before acknowledgement, deduplicate by message ID/effect identity, quarantine poison/unknown-version messages, and expose backlog/dead-letter health. Event ordering is guaranteed only per documented aggregate key; consumers tolerate replay and gaps.

## Workflow boundaries

The consulting workflow ends at a validated handoff proposal and acknowledgement; portfolio governance begins at intake. Target execution begins only after control-plane routing and fresh source validation and ends at a draft/result, never merge. A Slugger workflow, if later approved, begins only at its accepted contract and remains externally owned.

## Failure policy

Authentication, authorization, classification or schema failures do not retry automatically. Throttling/temporary availability may use bounded exponential backoff with jitter and server guidance. Timeouts are indeterminate until reconciled. Circuit breakers isolate an unhealthy adapter while offline consulting remains usable. Payloads that could expose sensitive information are quarantined only in approved protected facilities; otherwise retain safe metadata and reject.

## Integration acceptance gates

Before enabling an adapter: confirm owner and decision rights; approve schemas and supported versions; threat-model the trust boundary; establish credentials and least privilege; define classification/retention; pass contract, idempotency, recovery and load tests; document SLO/incident contacts; test upgrade and rollback; and obtain external owner sign-off.
