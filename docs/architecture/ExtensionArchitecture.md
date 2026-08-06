# Extension Architecture

## Goals and constraints

Extensions add engagement types, assessment domains, methods, templates, renderers, validators, policy constraints or infrastructure adapters without changing core semantics. They may tighten governance for context but cannot bypass authority, classification, evidence integrity, traceability or human review.

## Extension manifest contract

Every extension declares:

| Field | Meaning |
|---|---|
| Identity/version/type | Globally stable ID, semantic version and supported extension point. |
| Owner/reviewers | Accountable maintainer, security/content reviewers and support contact. |
| Compatibility | Core/knowledge/contract versions and other dependencies/conflicts. |
| Applicability | Engagement contexts, intended decisions, exclusions and limitations. |
| Input/output contracts | Logical types, required fields, classifications and produced records/events. |
| Permissions | Minimum data/actions/external destinations; default none. |
| Lifecycle | Initialization/use/disposal, migration, deprecation and rollback. |
| Quality evidence | Scenario, contract, accessibility, security and AI evaluations as applicable. |

## Extension points

### Engagement type and method packs

Compose named lifecycle stages and knowledge assets. They declare purpose, entry/exit criteria, tailoring options, evidence burden, participants, outputs and skipped-stage rationale. They cannot introduce a second definition of core entities.

### Assessment domains

Implement `DomainAssessment`: purpose, applicability, evidence guidance, analysis questions, observable contextual anchors, outputs, limitations and specialist escalation. Candidate domains include product/vision, backlog, SDLC, architecture, quality, security, DevOps, operating model and AI readiness. A domain's presence never implies it was applied.

### Rating/prioritization policies

Supply transparent anchors/criteria, inputs, uncertainty and explanation. Results are advisory, context-specific and overridable only with visible authorized rationale. No universal maturity target or false numeric precision.

### Templates and renderers

Templates declare consumed canonical concepts; renderers produce accessible audience projections without adding facts. Reconciliation tests compare material semantics across formats. Branding/localization cannot obscure status, uncertainty, conditions or AI disclosure.

### Validators and policy packs

Add pure deterministic constraints and actionable diagnostics. Policy packs may strengthen local/client rules but cannot weaken non-tailorable baseline. Conflicts are surfaced; precedence is explicit.

### Persistence and integration adapters

Implement published ports and owner-approved conformance suites. External models remain inside adapters. Adapters declare consistency, idempotency, retry, timeout, rate, authentication, classification, retention and observability behavior.

### AI providers/assistants

Implement the assistance port only. Declare approved tasks/data classes, provider/model provenance, safety/evaluation evidence, transfer/retention behavior and resource limits. No direct domain repository or authority interface access.

## Discovery and activation

The Knowledge Catalog discovers content extensions by signed/reviewed release metadata. Runtime extensions use an allowlisted registry controlled by deployment policy; installation does not activate permissions. Activation validates compatibility and configuration, then records owner/release/digest. Dynamic executable plugins are optional and should be avoided when declarative assets/adapters suffice.

## Isolation and failure

Run untrusted executable extensions with constrained filesystem/network/resources and no ambient credentials. Apply timeouts, bulkheads and output validation. An extension failure produces a typed limitation/degraded capability; it cannot corrupt canonical records. Security or integrity violation disables/quarantines the extension and alerts owners.

## Versioning and evolution

Additive compatible releases coexist; breaking semantics require a major version and migration. Pin exact versions in an engagement for reproducibility. Deprecation publishes successor, impact, warning window and withdrawal date. Historical artifacts remain resolvable or carry a preservation rendering. Rollback never silently reinterprets records.

## Acceptance checklist

Confirm owner and need; trace requirements; review ubiquitous language; validate manifest and compatibility; threat-model permissions/data; pass unit/scenario/contract/accessibility/reconciliation tests; document support and operational signals; pilot on synthetic/de-identified data; approve rollout/deprecation/rollback.

## Future capabilities

Potential extensions include local authoring tools, controlled multi-user collaboration, additional exchange/rendering formats, analytics approved against safe measures, and new external adapters. They remain optional hypotheses until requirements resolve users, scale, storage, privacy and interface contracts.
