# Configuration Architecture

## Configuration principles

Configuration selects behavior within approved architecture; it cannot redefine ownership, waive non-tailorable business rules, grant authority or turn advice/AI output into approval. Configuration is typed, versioned, reviewable, least-privilege and separated from secrets and engagement content.

## Configuration domains

| Domain | Examples | Owner |
|---|---|---|
| Knowledge release | Catalog version, supported assets, compatibility/deprecation | Knowledge maintainers |
| Engagement tailoring | Selected methods/domains/depth/outputs and recorded deviations | Engagement owner under method rules |
| Governance policy | Required fields, classification handling, review/escalation thresholds | Security/content/decision authorities |
| Integration | Enabled adapter, contract version, safe endpoint reference, timeouts/retry budgets | Integration/operations owner + external owner |
| Presentation | Locale, accessible renderer, approved branding/export | Product/client authority |
| Operations | Resource limits, health thresholds, telemetry routing/retention | Operations/security owner |
| Target execution | Supported canonical version pin, verify/implement constraints, deterministic branch namespace | Repository maintainers; shared schema remains external |

## Precedence

From highest to lowest: applicable law/client handling and explicit safety authority; Vision and approved requirements; architecture/non-tailorable policy; externally owned versioned contract at its boundary; environment/deployment policy; engagement tailoring; user presentation preference; documented default. A lower level cannot loosen a higher level. Conflicts fail validation and identify both sources.

## Loading and provenance

Each resolved setting records key, typed value or protected reference, source layer, configuration schema version and effective time. Load immutable defaults, approved policy, environment settings and scoped tailoring; validate each layer then validate the resolved set cross-field. Log only key/source/digest, never secret values.

## Validation

Validate schema/type/range/enumeration, unknown keys, version compatibility, required combinations, forbidden weakening, safe endpoint schemes, retry/time budgets, classification constraints and referenced asset existence. Startup fails closed for required invalid configuration; optional integrations become explicitly disabled/degraded. Changes are validated in non-production with representative scenarios.

## Defaults

Secure defaults are: external connectors and AI disabled until configured; unknown classification restricted; minimal collection; human review required; no autonomous decisions; no raw content telemetry; no automatic external retry after indeterminate effect; verify/non-mutating where mode is absent at an untrusted boundary; target publication draft-only/no merge; supported stable knowledge/contract release explicitly pinned.

## Secrets

Configuration contains secret references, never secret values in artifacts or source. The deployment adapter resolves secrets at runtime with scoped identity, rotation and audit. A missing/expired secret disables the adapter and returns safe health/error status.

## Dynamic change and rollback

Security, authority, schema compatibility and data-handling changes require reviewed rollout and must re-evaluate affected pending operations. Do not silently reinterpret historical records; they retain policy/version provenance. Rollback selects a compatible prior configuration and preserves newer records/external effects. Changes emit sanitized audit and operational events.

## Unknown configuration decisions

Priority engagement types, mandatory fields, rating vocabulary, classification/retention, specialist review thresholds, output formats, localization/branding, runtime tenancy, analytics and content approval cadence remain requirements decisions—not arbitrary configuration values. They must be validated and approved first.
