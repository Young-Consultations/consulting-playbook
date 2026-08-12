# Defect Taxonomy

Use one primary **origin** for where the defect entered the lifecycle and one **type** for the form the discrepancy took. These are separate concepts: an implementation-type failure may originate in an ambiguous requirement, while a documentation-type failure may originate during implementation. Record the best evidence-backed classification; explain close calls in `notes` rather than adding ad hoc labels.

## Origins and types

| Origin | Type | Definition |
| --- | --- | --- |
| `requirement` | `ambiguity` | Materially permits incompatible reasonable interpretations. |
| `requirement` | `contradiction` | Conflicts with another applicable requirement. |
| `requirement` | `omission` | Required behavior or constraint is absent. |
| `requirement` | `incorrect-requirement` | States behavior that evidence or an authorized decision shows is wrong. |
| `requirement` | `non-testable-requirement` | Cannot be objectively verified as written. |
| `requirement` | `scope-boundary-ambiguity` | Scope, ownership, or exclusion is materially unclear. |
| `architecture-design` | `responsibility-boundary-error` | Responsibility is allocated to the wrong component or repository. |
| `architecture-design` | `authority-ownership-error` | Decision or data authority is assigned incorrectly. |
| `architecture-design` | `interface-mismatch` | Designed participants or contracts do not align. |
| `architecture-design` | `dependency-problem` | A dependency is absent, cyclic, inappropriate, or incorrectly ordered. |
| `architecture-design` | `architectural-ambiguity` | Design permits materially incompatible interpretations. |
| `architecture-design` | `duplicated-competing-execution-path` | More than one active path owns the same responsibility. |
| `architecture-design` | `inappropriate-coupling` | Components share knowledge or change dependencies beyond their boundary. |
| `interface-integration` | `schema-mismatch` | Producer and consumer data shapes differ. |
| `interface-integration` | `version-mismatch` | Participants use incompatible contract or dependency versions. |
| `interface-integration` | `contract-interpretation` | Contract semantics are interpreted inconsistently. |
| `interface-integration` | `identity-idempotency-mismatch` | Identity, retry, deduplication, or effect semantics disagree. |
| `interface-integration` | `authentication-authorization-boundary` | Identity, permission, or trust-boundary behavior differs from intent. |
| `interface-integration` | `cross-repository-compatibility` | Independently owned repository behaviors are incompatible. |
| `configuration-workflow` | `github-actions` | GitHub Actions syntax, event, job, or action behavior is wrong. |
| `configuration-workflow` | `registry-configuration` | Registry or other configuration is missing, stale, or invalid. |
| `configuration-workflow` | `permissions` | Runtime or workflow permissions differ from intended least privilege. |
| `configuration-workflow` | `secrets-environment` | Secret or environment handling/configuration is incorrect. |
| `configuration-workflow` | `ci-cd-behavior` | Build, validation, publication, deployment, or release flow is wrong. |
| `implementation` | `logic` | Algorithmic or branching behavior is wrong. |
| `implementation` | `error-handling` | Failure detection, propagation, recovery, or messaging is wrong. |
| `implementation` | `state-management` | State creation, transition, persistence, or cleanup is wrong. |
| `implementation` | `race-condition` | Timing or concurrency causes incorrect behavior. |
| `implementation` | `security-implementation` | Implemented security behavior violates an applicable control. |
| `implementation` | `incorrect-code-behavior` | Code does not implement its applicable intended behavior. |
| `verification` | `missing-test` | A required verification is absent. |
| `verification` | `incorrect-expected-result` | A test asserts the wrong outcome. |
| `verification` | `inadequate-acceptance-criteria` | Criteria cannot establish the needed acceptance evidence. |
| `verification` | `missing-coverage` | Material path, boundary, or risk lacks verification. |
| `verification` | `false-positive-negative` | Verification incorrectly passes or rejects behavior. |
| `documentation-context` | `stale-authoritative-documentation` | An authoritative document was not updated after an approved change. |
| `documentation-context` | `misleading-documentation` | Documentation materially misrepresents behavior or authority. |
| `documentation-context` | `contradictory-documentation` | Applicable documents conflict. |
| `documentation-context` | `ai-context-drift` | `AI_CONTEXT.md` no longer reflects resolved operational guidance. |
| `documentation-context` | `unresolved-speculation-as-truth` | An unresolved claim is presented as authoritative fact. |

If multiple types apply, choose the type nearest the causal discrepancy and mention secondary effects in `notes`. Use `origin = unknown` temporarily only while root-cause analysis is open, then replace it when evidence resolves the origin.

## Severity

Use `critical`, `high`, `medium`, or `low`, based on demonstrated or credible impact rather than discovery effort. Document the impact rationale for critical and high severity records.
