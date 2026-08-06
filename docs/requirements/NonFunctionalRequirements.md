# Nonfunctional Requirements

These requirements apply to normative knowledge assets, engagement records
created from them, and automation supplied by this repository. Where the product
is used manually, “validation” may be a documented review rather than software.

| ID | Quality | Mandatory, measurable requirement | Verification |
| --- | --- | --- | --- |
| NFR-PERF-01 | Performance | A user SHALL locate the current approved core method and any cataloged asset by domain, lifecycle stage, audience, and status within 2 minutes in a representative usability test, with at least 90% task success across 10 attempts. | Timed usability test. |
| NFR-PERF-02 | Performance | Automated validation owned by this repository SHALL complete within 10 minutes at the 95th percentile for the reference repository corpus, excluding external service latency; the full routed target workflow SHALL retain a declared timeout no greater than 45 minutes. | CI timing report over 20 runs; workflow inspection. |
| NFR-SEC-01 | Security | 100% of knowledge and handoff artifacts SHALL expose classification, permitted-use, and transfer-review status where they may contain engagement information; unknown classification SHALL fail closed as restricted. | Schema/reviewer sampling and negative tests. |
| NFR-SEC-02 | Security | Secrets, credentials, raw sensitive evidence, and unnecessary personal/client identifiers MUST NOT be committed to the repository, logged, placed in reusable examples, or included in executable prompts. | Secret scan, content review, prompt/log tests. |
| NFR-SEC-03 | Security | Mutation-capable automation SHALL use least-privilege, time-bounded credentials where the platform supports them and MUST NOT expose credential values in outputs. | Permissions and log review. |
| NFR-REL-01 | Reliability | For 100% of material records, internal trace links SHALL resolve or be reported by validation; unresolved external links SHALL be visibly flagged with last-validation date and SHALL NOT silently change meaning. | Link/trace validator. |
| NFR-REL-02 | Reliability | Reprocessing one delivery identity SHALL create no more than one completed publication effect; ambiguous remote state SHALL produce no overwrite, merge, or replacement effect. | Contract and race-condition tests. |
| NFR-MNT-01 | Maintainability | 100% of approved reusable assets SHALL have an owner, semantic version or baseline identifier, lifecycle status, applicability, last review, and next review due date. | Catalog audit. |
| NFR-MNT-02 | Maintainability | A change SHALL update all directly affected traceability entries in the same reviewed change; validation SHALL detect duplicate requirement IDs and broken internal references. | Pull-request checklist and validator. |
| NFR-MNT-03 | Maintainability | Normative content SHOULD use one concept per requirement and MUST distinguish requirements, examples, assumptions, and guidance. | Requirements quality review. |
| NFR-SCL-01 | Scalability | The catalog SHALL remain navigable and validation SHALL meet NFR-PERF-02 with at least 1,000 assets, 10,000 trace relations, 25 domains, and 20 engagement variants in a generated test corpus. | Load/corpus test. |
| NFR-OBS-01 | Observability | Every automated execution SHALL expose correlation identity, delivery identity where applicable, contract version, source, target, mode, lifecycle timestamps, terminal status, and sanitized failure category; it MUST NOT expose prompt content, tokens, secrets, or raw sensitive evidence. | Result/log contract tests. |
| NFR-OBS-02 | Observability | Validation failures SHALL identify the affected record/requirement and actionable rule while avoiding sensitive values; 100% of terminal automation paths SHALL emit or preserve a result when the external platform permits. | Fault-injection tests. |
| NFR-CFG-01 | Configuration | Engagement-specific scope, depth, domains, classifications, review cadence, and measures SHALL be declared outside the invariant meaning of the reusable method and SHALL retain their effective version. | Configuration/record review. |
| NFR-CFG-02 | Configuration | Unknown, missing, or incompatible contract/configuration versions MUST fail validation rather than silently default, except an explicitly documented non-safety presentation default. | Negative compatibility tests. |
| NFR-DEP-01 | Deployment independence | Core consulting content SHALL be readable, reviewable, and usable without executing code, accessing another repository, or calling a network service. | Offline walkthrough. |
| NFR-DEP-02 | Deployment independence | Failure or unavailability of an external integration SHALL NOT corrupt or retroactively alter consulting records; handoff may remain pending with an explicit status. | Outage scenario test. |
| NFR-AVL-01 | Availability | Published current knowledge SHALL be available whenever the repository's default branch is readable; no stricter runtime service availability is claimed. External automation availability SHALL inherit platform objectives and be reported separately. | Offline clone/read test; dependency report. |
| NFR-REC-01 | Recoverability | All approved content and requirement changes SHALL be recoverable from version history to the last accepted baseline; recovery exercises SHALL demonstrate restoration within 4 business hours at least annually. | Annual restore exercise. |
| NFR-REC-02 | Recoverability | Failed or partial cross-repository handoffs SHALL be retryable without duplicate authorization or publication; ambiguous cases SHALL require human reconciliation and preserve evidence. | Failure/retry scenarios. |
| NFR-CMP-01 | Compliance | The product SHALL record applicable client, legal, privacy, security, retention, and accessibility obligations as engagement constraints and SHALL NOT claim certification or compliance solely from playbook completion. | Engagement audit. |
| NFR-DOC-01 | Documentation | Every current method SHALL state purpose, users, prerequisites, inputs, activities/outcomes, outputs, tailoring points, evidence expectations, limitations, risks, and related assets. | Documentation lint/review. |
| NFR-DOC-02 | Documentation | Terms SHALL conform to `Glossary.md`; normative changes SHALL include release notes or change rationale understandable to consultant, engineering, and assurance readers. | Terminology and review audit. |
| NFR-TST-01 | Testability | Every mandatory functional requirement SHALL have at least one positive and one failure/negative future test reference before implementation is accepted. | Traceability audit. |
| NFR-TST-02 | Testability | Automated contract, policy, and validation tests SHALL be deterministic, isolated from production client data, and runnable without write access to external repositories. | Repeated offline CI run. |
| NFR-AUTO-01 | Automation readiness | Normative records intended for automation SHALL use stable unique IDs, explicit states, declared required fields, versioned semantics, and deterministic validation outcomes. | Schema/fixture validation. |
| NFR-AUTO-02 | Automation readiness | Automation MUST NOT infer approval, sensitivity clearance, decision authority, or target ownership from free text when the corresponding explicit field is absent. | Adversarial fixtures. |
| NFR-AI-01 | AI compatibility | AI-consumable tasks SHALL be self-contained for their target boundary, state objectives and constraints, include acceptance outcomes, identify external dependencies, and exclude unstated conversational context. | Blind-agent task review. |
| NFR-AI-02 | AI compatibility | AI-generated analysis or drafting SHALL remain distinguishable, cite available evidence, communicate uncertainty, and obtain documented professional review before becoming an approved finding, recommendation, decision, or reusable asset. | Provenance/review audit. |
| NFR-ACC-01 | Accessibility | Normative documents and templates SHALL meet WCAG 2.2 AA principles applicable to document content: semantic headings, descriptive links, text alternatives, non-color-only meaning, logical reading order, and tables with headers. | Automated checks plus manual keyboard/screen-reader review. |
| NFR-USA-01 | Usability | In representative tests, at least 80% of first-time consultant users SHALL correctly distinguish finding, implication, recommendation, decision, and task without assistance. | Scenario-based usability test with at least 5 users. |
| NFR-INT-01 | Interoperability | Cross-boundary records SHALL identify owning repository/system, contract version, stable correlation, source/target, timestamps, classification, and status; unsupported extensions SHALL be preserved or rejected according to the versioned contract, never silently reinterpreted. | Consumer/provider contract tests. |
| NFR-PORT-01 | Portability | Knowledge content SHALL use repository-portable text and relative internal references; export to a commonly readable document form SHALL preserve headings, tables, links, classifications, and requirement IDs. | Clone/export comparison on two environments. |

## Review thresholds

P0 nonfunctional requirements are release gates. A P1/P2 exception requires a
named owner, rationale, risk acceptance, expiration, and remediation plan. No
exception may waive confidentiality, human authority, or non-automatic-merge
guardrails.
