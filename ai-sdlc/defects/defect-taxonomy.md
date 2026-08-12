# Defect Taxonomy

Use one primary **origin** for the artifact or responsibility in which the defect was introduced, one **origin phase** for when it entered the lifecycle, and one **type** for the form of discrepancy. These are independent dimensions: code with incorrect behavior can originate in an ambiguous requirement, and misleading documentation can originate during implementation. Record the best evidence-backed classification; explain close calls in `notes` rather than adding ad hoc labels.

## Origins

`origin` is one of `requirement`, `architecture-design`, `interface-integration`, `configuration-workflow`, `implementation`, `verification`, `documentation-context`, or temporarily `unknown`. `origin_phase` separately uses the ordered SDLC phases in the [metrics definition](metrics-definition.md).

## Types by family

The family headings organize the vocabulary; they do not constrain `origin` to the same family.

| Family | Allowed types |
| --- | --- |
| Requirement | `ambiguity`, `contradiction`, `omission`, `incorrect-requirement`, `non-testable-requirement`, `scope-boundary-ambiguity` |
| Architecture/design | `responsibility-boundary-error`, `authority-ownership-error`, `interface-mismatch`, `dependency-problem`, `architectural-ambiguity`, `duplicated-competing-execution-path`, `inappropriate-coupling` |
| Interface/integration | `schema-mismatch`, `version-mismatch`, `contract-interpretation`, `identity-idempotency-mismatch`, `authentication-authorization-boundary`, `cross-repository-compatibility` |
| Configuration/workflow | `github-actions`, `registry-configuration`, `permissions`, `secrets-environment`, `ci-cd-behavior` |
| Implementation | `logic`, `error-handling`, `state-management`, `race-condition`, `security-implementation`, `incorrect-code-behavior` |
| Verification | `missing-test`, `incorrect-expected-result`, `inadequate-acceptance-criteria`, `missing-coverage`, `false-positive-negative` |
| Documentation/context | `stale-authoritative-documentation`, `misleading-documentation`, `contradictory-documentation`, `ai-context-drift`, `unresolved-speculation-as-truth` |

Classify the causal discrepancy rather than a downstream symptom.

### Type definitions

| Type | Definition |
| --- | --- |
| `ambiguity` | Materially permits incompatible reasonable interpretations. |
| `contradiction` | Conflicts with another applicable requirement. |
| `omission` | Required behavior or constraint is absent. |
| `incorrect-requirement` | States behavior that evidence or an authorized decision shows is wrong. |
| `non-testable-requirement` | Cannot be objectively verified as written. |
| `scope-boundary-ambiguity` | Scope, ownership, or exclusion is materially unclear. |
| `responsibility-boundary-error` | Responsibility is allocated to the wrong component or repository. |
| `authority-ownership-error` | Decision or data authority is assigned incorrectly. |
| `interface-mismatch` | Designed participants or contracts do not align. |
| `dependency-problem` | A dependency is absent, cyclic, inappropriate, or incorrectly ordered. |
| `architectural-ambiguity` | Design permits materially incompatible interpretations. |
| `duplicated-competing-execution-path` | More than one active path owns the same responsibility. |
| `inappropriate-coupling` | Components share knowledge or change dependencies beyond their boundary. |
| `schema-mismatch` | Producer and consumer data shapes differ. |
| `version-mismatch` | Participants use incompatible contract or dependency versions. |
| `contract-interpretation` | Contract semantics are interpreted inconsistently. |
| `identity-idempotency-mismatch` | Identity, retry, deduplication, or effect semantics disagree. |
| `authentication-authorization-boundary` | Identity, permission, or trust-boundary behavior differs from intent. |
| `cross-repository-compatibility` | Independently owned repository behaviors are incompatible. |
| `github-actions` | GitHub Actions syntax, event, job, or action behavior is wrong. |
| `registry-configuration` | Registry or other configuration is missing, stale, or invalid. |
| `permissions` | Runtime or workflow permissions differ from intended least privilege. |
| `secrets-environment` | Secret or environment handling/configuration is incorrect. |
| `ci-cd-behavior` | Build, validation, publication, deployment, or release flow is wrong. |
| `logic` | Algorithmic or branching behavior is wrong. |
| `error-handling` | Failure detection, propagation, recovery, or messaging is wrong. |
| `state-management` | State creation, transition, persistence, or cleanup is wrong. |
| `race-condition` | Timing or concurrency causes incorrect behavior. |
| `security-implementation` | Implemented security behavior violates an applicable control. |
| `incorrect-code-behavior` | Code does not implement its applicable intended behavior. |
| `missing-test` | A required verification is absent. |
| `incorrect-expected-result` | A test asserts the wrong outcome. |
| `inadequate-acceptance-criteria` | Criteria cannot establish the needed acceptance evidence. |
| `missing-coverage` | Material path, boundary, or risk lacks verification. |
| `false-positive-negative` | Verification incorrectly passes or rejects behavior. |
| `stale-authoritative-documentation` | An authoritative document was not updated after an approved change. |
| `misleading-documentation` | Documentation materially misrepresents behavior or authority. |
| `contradictory-documentation` | Applicable documents conflict. |
| `ai-context-drift` | `AI_CONTEXT.md` no longer reflects resolved operational guidance. |
| `unresolved-speculation-as-truth` | An unresolved claim is presented as authoritative fact. |

If multiple types apply, choose the type nearest the causal discrepancy and mention secondary effects in `notes`. Use `origin = unknown` temporarily only while root-cause analysis is open, then replace it when evidence resolves the origin. Keep `origin_phase` blank until it can be supported; do not infer it solely from the origin category.

## Severity

Use `critical`, `high`, `medium`, or `low`, based on demonstrated or credible impact rather than discovery effort. Document the impact rationale for critical and high severity records.
