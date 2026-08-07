# Consulting Playbook next-MVP target-adapter profile

## Authority and scope

This profile is the normative repository-owned implementation baseline. It uses
organization compatibility release `2.2.0`, payload contract
`ai-sdlc-contract/v2`, and fixture-set manifest `TC-MVP-CI-001`, all identified
by the immutable `Young-Consultations/.github` commit
`f2491872976a4dcc1633997954c03c07cbc4fced`. These supplied interface facts are
requirements, not a claim that this repository inspected or conforms with a
sibling repository.

The current MVP contribution accepts **one already admitted task**, validates it,
and in implement mode produces or reuses **one validated managed draft pull
request**, then emits **one canonical execution-result/v2**. Verify mode only
validates. This slice preserves the broader consulting-playbook vision but does
not implement the consulting content platform, publish consulting guidance, or
perform production work.

The registry entry is deliberately disabled (`enabled: false`). Local interface
alignment and fake implementation testing may proceed; every live routed request
must fail closed until the organization owner enables the entry.

## Included and deferred requirement IDs

Included: `FR-EXE-01`, `FR-EXE-02`, `FR-SEC-01`, `FR-SEC-02`, `NFR-SEC-02`,
`NFR-SEC-03`, `NFR-REL-02`, `NFR-REC-02`, `NFR-OBS-01`, `NFR-OBS-02`,
`NFR-CFG-02`, `NFR-INT-01`, `NFR-TST-01`, `NFR-TST-02`, `NFR-AUTO-01`,
`NFR-AUTO-02`, and `NFR-AI-01`.

Deferred functional IDs: `FR-ENG-01`–`FR-ENG-03`, `FR-EVD-01`–`FR-EVD-04`,
`FR-ASMT-01`–`FR-ASMT-03`, `FR-ANL-01`–`FR-ANL-03`, `FR-REC-01`,
`FR-DEC-01`, `FR-ROAD-01`, `FR-RPT-01`, `FR-HO-01`, `FR-FU-01`, and
`FR-KM-01`–`FR-KM-02`. Nonfunctional IDs not listed as included are deferred
until their associated capability is implemented. Explicitly deferred are rich
v3 approval evidence, cross-repository modification, automatic merge,
automatic consulting-content publication, release, deployment, production
operations, and broader content-platform automation not needed by this adapter.

## Immutable compatibility unit

All organization file references use this complete SHA (never `main` or the
declared but unavailable `ai-sdlc-v2.2.0` tag):

`Young-Consultations/.github@f2491872976a4dcc1633997954c03c07cbc4fced`

The compatibility unit comprises `release/release-manifest.json`,
`docs/interfaces/mvp-v2-compatibility.md`, `docs/releases/next-mvp.md`,
`config/codex-repositories.json`, the three schemas below,
`tests/fixtures/mvp-v2/manifest.json`, `.github/workflows/codex-router.yml`, and
`.github/workflows/codex-result-receiver.yml` at that SHA.

The adapter shall directly consume the immutable schema files:

* `contracts/task-contract.schema.json`
* `contracts/execution-input.schema.json`
* `contracts/execution-result.schema.json`

No published Python artifact has been independently confirmed. A package,
undocumented module/path, sibling checkout, or local contract fork is therefore
not an MVP dependency. A documented public validation API is a possible future
organization-owned improvement, not a current design decision.

The authoritative target registry values are:

| Property | Value |
| --- | --- |
| target | `Young-Consultations/consulting-playbook` |
| enabled | `false` |
| permitted task types | `automation`, `documentation`, `feature`, `testing` |
| contract | `ai-sdlc-contract/v2` |
| draft_pr_only | `true` |
| branch_identity | `delivery_id` |
| ownership_marker | `ai-sdlc-delivery-id` |
| terminal_reuse_status | `duplicate-reused` |

## Exact workflow interfaces

The eventual reusable target workflow is `.github/workflows/codex-execute.yml`
and has exactly these required routing inputs:

| Input | Meaning |
| --- | --- |
| `execution_input_json` | Complete canonical execution-input/v2 JSON string. |
| `concurrency_group` | Required routing transport concurrency value; it reduces races but is not authorization or idempotency. |

The obsolete `execution_input` name is not an interface. The target sends its
result separately; it does not return execution success directly to the router.

It shall invoke
`Young-Consultations/.github/.github/workflows/codex-result-receiver.yml@f2491872976a4dcc1633997954c03c07cbc4fced`
with inputs `execution_result` and `source_issue` and secret
`CODEX_RESULT_TOKEN`. Receiver outputs are `accepted`, `delivery_id`,
`correlation_id`, `execution_status`, `failure_category`, and
`diagnostic_summary`.

The receiver is an approved **fail-closed interface skeleton**. Alignment may
proceed, but successful live result return is unavailable until its organization
owner implements it. Consulting Playbook shall not build a competing receiver.
Transport acceptance and receiver outputs are acknowledgement evidence, never a
replacement for the target's canonical execution outcome or proof of execution
success.

## Authorization and content boundaries

Router admission canonically means `approved`. A material task change requires a
new `task_id` and a new organization approval. `queued` is only a post-admission
projection, not authorization. The target authenticates and authorizes the
admitted caller but does not re-read a mutable source-issue label and does not
require a second organization approval record. Rich approval provenance belongs
to v3 and must not be invented here.

These independent decisions must never substitute for one another:

1. organization task approval authorizes admission of the stated task;
2. repository policy and credentials authorize a bounded repository change;
3. consulting-content review determines whether guidance is professionally fit;
4. draft-PR review determines whether the proposed repository change may merge;
5. a final human publication decision determines whether consulting guidance is
   published or used.

Approval to change repository files is not approval to publish consulting
content, and content approval is not repository-change authorization. This
target is not an organization approval authority and receives no control-plane
credentials.

## Required adapter behavior

Before any executor or publisher effect, the adapter shall authenticate and
authorize the admitted caller; format-check and validate `execution_input_json`
against the exact immutable schema; require target
`Young-Consultations/consulting-playbook`, `ai-sdlc-contract/v2`, an allowed task
type (`automation`, `documentation`, `feature`, or `testing`), local repository
and consulting-content policy, and `draft_pr_only: true`; validate and use the
supplied `concurrency_group`; and fail closed while the registry is disabled or
when routing is stale/improper.

`delivery_id` is the sole idempotency identity and stays stable across retries;
`correlation_id` is the observability identity. Processing is at least once with
idempotent visible effects. The adapter records a payload fingerprint and rejects
mutation beneath an existing delivery ID. It derives branch identity
deterministically from `delivery_id`, searches all relevant PR state for the
`ai-sdlc-delivery-id` ownership marker, and fails closed if ownership is missing,
conflicting, or ambiguous. Exactly one matching managed open draft is reused with
terminal status `duplicate-reused`. Creation races trigger an immediate requery;
at most one managed open draft PR may result for a delivery.

Every terminal path emits the exact canonical execution-result/v2, including
the schema's required null fields, and attempts the organization result receiver.
It never merges, publishes consulting guidance, releases, deploys, performs a
production operation, or reads/modifies another repository.

### Verify mode

Verify validates request format/schema, caller, registry and repository/content
policy. It does not invoke Codex, create a branch, or create a PR. Success uses
`execution_status: verified` and the authoritative null-field requirements.

### Implement mode

Implement invokes Codex only after validation, confines changes to this
repository, runs repository and consulting-content validation, and creates or
reuses only a draft PR before emitting the canonical result. Normal CI substitutes
a fake executor and fake publisher. A draft repository change never becomes
automatically published consulting guidance.

## Planned no-Codex conformance coverage

Local tests shall align with the `TC-MVP-CI-001` manifest and cover: valid verify;
valid fake implement; wrong target; disabled target; invalid contract version;
invalid schema or format; unauthorized caller; unsupported task type; invalid
concurrency value; stale or improperly routed request; duplicate delivery;
conflicting payload under one delivery ID; existing matching managed draft PR;
ambiguous PR ownership; create-race requery; repository-policy rejection;
consulting-content validation failure; fake executor failure; validation failure;
test failure; publication failure; valid canonical result; receiver fail-closed
response; identical result redelivery; conflicting result redelivery; no Codex
call; no real branch; and no real pull request.

The manifest is the authoritative shared scenario list, but release `2.2.0` does
not supply executable inputs and expected outputs for every scenario. Planned
coverage may map to the manifest; it must not invent missing fixtures or claim
executable shared-fixture conformance. Fixture completion is an external
`Young-Consultations/.github` implementation dependency.

## Readiness and external dependencies

No further repository-owned architecture decision blocks implementation: scope,
interfaces, authorization boundaries, idempotency, ownership, results, and test
intent are fixed above. Live execution remains blocked on organization-owned
registry enablement and receiver implementation. Executable shared-fixture
completion is required for the eventual shared conformance claim. The unavailable
tag must not be used; the full SHA remains authoritative. These limitations do
not block local fake adapter implementation and testing, but they do block live
routing and any claim of cross-repository conformance or successful live return.
