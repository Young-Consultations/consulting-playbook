# Assumptions and Open Questions

## Confirmed assumptions (repository-local)

These are confirmed by the controlling vision or inspected snapshot, not by
inspection of external repositories.

| ID | Confirmed statement |
| --- | --- |
| CA-01 | Consulting-playbook owns reusable consulting knowledge and recommendation-to-action patterns, not portfolio governance or Slugger. |
| CA-02 | Human judgment and designated authority remain final for recommendations, approvals, architecture, review, merge, and production. |
| CA-03 | Current implemented scope is primarily a bounded organization-routed target executor; intended consulting content is not yet implemented. |
| CA-04 | Inspected implementation evidence supports verify/implement paths, approval/non-sensitive/Codex checks, and draft-only publication; it does not prove next-MVP contract or authorization conformance. |
| CA-05 | Other repositories were not inspected; cross-repository descriptions are owner-supplied context and required contracts, not implementation claims. |

## Working assumptions requiring validation

| ID | Assumption | Impact if false | Validation and owner |
| --- | --- | --- | --- |
| WA-01 | A shared lifecycle can support multiple engagement types. | Separate cores or a looser model may be needed. | Walk at least three materially different engagements; consulting lead. |
| WA-02 | Executive and technical views can derive from one reasoning chain. | Additional reconciliation semantics may be required. | Map audience decisions and prototype content views; UX/product owner. |
| WA-03 | Evidence-led repeatability creates value without suppressing judgment. | Product value proposition/tailoring must change. | Practitioner pilots and sponsor review; product manager. |
| WA-04 | Contextual backlog health is an important delivery signal. | Domain priority and causal language must change. | Authorized comparative case review; delivery specialist. |
| WA-05 | System improvement produces more durable leverage than recurring individual intervention. | Operating-model emphasis may be overstated. | Lead/sponsor interviews and outcome evidence; consulting lead. |
| WA-06 | Clients value governed recommendation-to-task handoff. | Handoff scope may be reduced or altered. | Trace representative decisions to intake; portfolio/client owners. |
| WA-07 | GitHub can be a suitable traceability surface for approved action. | Alternative systems/contracts are required. | Access, retention, lifecycle, reporting, and capability review; governance owner. |
| WA-08 | Core content can remain usable offline and implementation-neutral. | A runtime product may become a separately required scope. | Offline scenario tests; maintainer/users. |

## Unknowns

| ID | Unknown | Requirement impact |
| --- | --- | --- |
| U-01 | Priority engagement types, representative clients, scale, cadence, and commercial model. | Information architecture, pilots, and performance assumptions. |
| U-02 | Required client evidence systems, jurisdictions, retention, deletion, accessibility, and records obligations. | FR-SEC and NFR-CMP baselines. |
| U-03 | Preferred maturity vocabulary, rating policy, and specialist sign-off thresholds. | FR-ASMT-03 templates and verification. |
| U-04 | Required export/presentation formats, localization, branding, and collaboration modes. | Portability, accessibility, and reporting acceptance. |
| U-05 | Whether engagement-instance records will ever be stored here. | Data model, permissions, backup, and privacy architecture. |
| U-06 | Product analytics authorization and useful metrics beyond pilot success. | Telemetry scope and consent/retention. |
| U-07 | Formal content approvers, review cadence by risk, and version taxonomy. | FR-KM governance workflow. |

## Questions requiring clarification

1. Which two or three engagement types form the first coherent release, and
   what real decisions must each support?
2. Which fields are mandatory in every engagement versus selected by risk,
   domain, or contract?
3. Who may accept evidence limitations and approve each class of reusable asset?
4. What classification taxonomy and retention/disposal rules govern client
   information, links, reports, AI use, and reusable lessons?
5. What defines a “material” finding/risk for review and specialist escalation?
6. Which measurable outcomes demonstrate consulting value without reducing
   consultant/client performance to unsafe proxy metrics?
7. What exchange formats, if any, are required beyond human-readable artifacts?
8. When should the current target executor be retained, changed, or retired as
   the consulting product grows?

Safety, authority, and data-handling questions must be resolved before relevant
capabilities are operationally accepted. Other questions may remain explicit
pilot hypotheses.

## External repository dependencies

### `Young-Consultations/.github`

Confirm canonical field schema and versions, transports, authentication,
permissions, repository registration, concurrency semantics, failure taxonomy,
result consumption, retention, SLA, test fixtures, incident response, recovery,
upgrade, and rollback. See
[Interface-Organization-Control-Plane.md](Interface-Organization-Control-Plane.md).

Specifically unresolved for next-MVP enablement are the immutable organization
release, documented public package API, stable approval-proof semantics,
result-return transport, shared fixture location, target registry enablement, and
canonical lifecycle vocabulary. No observed module/path is treated as confirmed.

### `Young-Consultations/portfolio-tasks`

Confirm intake schema/transport, issue/state model, authority, classifications,
deduplication, acknowledgements, synchronization, cancellation, permissions,
retention, result handling, and recovery. See
[Interface-Portfolio-Tasks.md](Interface-Portfolio-Tasks.md).
Confirmation must explain material-edit, stale-proof, withdrawal and revocation
behavior when an approval label changes to queued after routing.

### `Young-Consultations/slugger`

First confirm whether any direct interaction is desired. If so, validate product
inputs/results, supported outcomes, identity, authorization/routing, validation,
data handling, artifacts, retry/recovery, review points, and versioning. See
[Interface-Slugger.md](Interface-Slugger.md).

## Assumption governance

Each working assumption/unknown SHALL have an owner before it blocks delivery.
Validation results SHALL update the relevant requirement and trace links in a
reviewed change. Failure to validate an assumption is information, not permission
to silently treat it as confirmed.
