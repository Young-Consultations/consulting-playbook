# Observability Architecture

## Objectives

Observability must answer: Is the knowledge release valid? Can users complete governed workflows? Which state transition or integration failed? Are projections current and consistent? Are security gates denying or unexpectedly permitting action? Has a logical external effect completed? It must do so without exposing client evidence, prompts, secrets or sensitive narrative.

## Signal model

| Signal | Required content | Excluded content |
|---|---|---|
| Operational log | Timestamp, severity, component, environment, safe event/error code, correlation, operation, outcome, duration, version | Evidence/report bodies, prompts/responses, tokens, credentials, raw personal/client data. |
| Metric | Counts/rates/durations/saturation labeled by component, outcome, contract version and coarse workflow stage | Unbounded IDs, client names, narrative, sensitive classifications as high-cardinality labels. |
| Trace | Correlation/causation, component spans, safe external endpoint class, retry/reconciliation and result | Payload bodies, auth headers, confidential locators. |
| Audit record | Actor, authority/policy reference, action, subject/revision, rationale reference, prior/new state, time, correlation and outcome | Operational stack traces and unnecessary source content. |

Audit is governed business evidence; telemetry is operational diagnosis. Neither substitutes for the other and their access/retention differ.

## Health model

- **Liveness:** process/unit can make progress; must not depend on every external provider.
- **Readiness:** required local dependencies and compatible knowledge/schema versions are available.
- **Degraded:** core/manual workflow available but projection, AI or external connector unavailable.
- **Integrity health:** audit append, revision consistency, projection lag/reconciliation and contract validation are within policy.
- **Dependency health:** each adapter reports availability, auth/compatibility status, throttling and circuit state without leaking endpoint secrets.

## Metrics

Recommended conceptual metrics include command outcomes by code; lifecycle transition counts; optimistic conflicts; validation and authorization denials; evidence limitations by non-sensitive category; projection age/reconciliation failures; knowledge validation/deprecation warnings; integration requests, latency, retries, indeterminate outcomes and reconciliation age; AI requests denied/accepted and human dispositions where ethically authorized; target dispatch verify/implement/reuse/block outcomes; and audit/telemetry delivery health.

Business success cannot be reduced to activity metrics. Do not rank consultants/clients or treat checklist completion, AI acceptance, recommendation counts or maturity scores as value without an approved measurement design.

## Correlation

Use a safe end-to-end correlation ID and local command/message IDs. Preserve causation across domain events and adapter translations. Delivery identity is used only for idempotency and can be correlated but does not replace attempt/run identifiers. User-facing errors include correlation; external result contracts retain canonical correlation. Never derive sensitive meaning in IDs.

## Logging levels and events

- `INFO`: lifecycle milestone, release/version loaded, external acknowledgement, projection rebuild.
- `WARN`: recoverable conflict, deprecated version, degraded connector, approaching limits.
- `ERROR`: failed operation requiring attention, audit/contract/integrity failure, blocked publication.
- `DEBUG`: disabled or tightly controlled in production; still no payload/secrets.

Security events include repeated denied access, cross-context attempts, contract tampering, prohibited transfer, secret detection, privilege change and break-glass use. Alerts route to named operational/security owners with playbooks.

## Diagnostics and runbooks

Diagnostics provide safe version/support matrix, configuration provenance (not values), health, correlation search, aggregate revision, projection source revision, integration reconciliation state and ownership contacts. Runbooks cover contract incompatibility, audit failure, stale projections, portfolio lost acknowledgement, AI/provider outage, data exposure, credential compromise and ambiguous target publication.

## SLOs and retention

Availability, latency, projection freshness, acknowledgement and recovery targets remain unknown until usage is validated. Define indicators and error budgets before operational acceptance. Telemetry and audit retention, access, residency and deletion must follow approved classification/legal policy. Sampling may reduce traces but never required audit evidence.

## Verification

Automated tests assert structured fields, redaction, correlation propagation, bounded metric cardinality, audit completeness/atomicity, alert routing, degraded-mode health, trace continuity and inability to disclose representative secrets/client payloads.
