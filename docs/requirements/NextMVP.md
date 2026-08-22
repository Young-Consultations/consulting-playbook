# Consulting Playbook next-MVP target-adapter profile

## Authority and scope

This profile is the normative repository-owned implementation baseline. It uses
payload contract `ai-sdlc-contract/v2` and fixture-set manifest
`TC-MVP-CI-001` from the reviewed issue #135 recovery candidate at immutable
`Young-Consultations/.github@e27b8a541afbd27b4be5606a19ffa43637ad312a`.
The 2.3.1 compatibility release and this repository's immutable 2.3.1 adapter
tag are published and live-verified. These supplied
interface facts are requirements; conformance is established only by the
exact-file pin and executable report described below.

The current MVP contribution accepts **one already admitted task**, validates it,
and in implement mode produces or reuses **one validated managed draft pull
request**, then emits **one canonical execution-result/v2**. Verify mode only
validates. This slice preserves the broader consulting-playbook vision but does
not implement the consulting content platform, publish consulting guidance, or
perform production work.

The immutable compatibility unit defines protocol and target-capability
semantics. Current target activation is separate mutable organization
control-plane state: the organization router owns and enforces it before
dispatch. This target neither consumes historical activation from the pinned
unit nor enables, disables, or otherwise administers routing. Merging or testing
the adapter does not enable live routing.

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

All organization file references use this complete SHA (never `main` or a
mutable reference):

`Young-Consultations/.github@e27b8a541afbd27b4be5606a19ffa43637ad312a`

The target evidence consumes the three schemas below and the exact executable
`TC-MVP-CI-001` manifest, scenarios, and expected results at that SHA.
`config/mvp-conformance-pin.json` binds their Git blob identities together
with this target's workflow, adapter, and harness. Its revision is calculated
non-recursively; the report and pin never predict their containing commit.
The eventual registry separately binds the adapter tag, resolved commit, and
report digest.

The adapter shall directly consume the immutable schema files:

* `contracts/task-contract.schema.json`
* `contracts/execution-input.schema.json`
* `contracts/execution-result.schema.json`

No published Python artifact has been independently confirmed. A package,
undocumented module/path, sibling checkout, or local contract fork is therefore
not an MVP dependency. A documented public validation API is a possible future
organization-owned improvement, not a current design decision.

The immutable target-capability values consumed by this target are:

| Property | Value |
| --- | --- |
| target | `Young-Consultations/consulting-playbook` |
| permitted task types | `automation`, `documentation`, `feature`, `testing` |
| contract | `ai-sdlc-contract/v2` |
| draft_pr_only | `true` |
| branch_identity | `delivery_id` |
| ownership_marker | `ai-sdlc-delivery-id` |
| terminal_reuse_status | `duplicate-reused` |

## Exact workflow interfaces

The target workflow is `.github/workflows/codex-execute.yml`, exposes only
`workflow_dispatch`, and has exactly these required routing inputs:

| Input | Meaning |
| --- | --- |
| `execution_input_json` | Complete canonical execution-input/v2 JSON string. |
| `concurrency_group` | Required routing transport concurrency value; it reduces races but is not authorization or idempotency. |

The obsolete `execution_input` name is not an interface. The target sends its
result separately; it does not return execution success directly to the router.

It shall invoke
`Young-Consultations/.github/.github/workflows/codex-result-receiver.yml@ai-sdlc-v2.3.1`
with inputs `execution_result` and `source_issue` and secret
`CODEX_RESULT_TOKEN`. That tag is published and its workflow/action bundle was
live-verified. Receiver outputs are `accepted`, `delivery_id`,
`correlation_id`, `execution_status`, `failure_category`, and
`diagnostic_summary`.

The receiver is the canonical organization-owned result transport. Consulting
Playbook shall invoke that interface and shall not build a competing receiver.
Transport acceptance and receiver outputs are acknowledgement evidence, never a
replacement for the target's canonical execution outcome or proof of execution
success. Receiver failure and result redelivery follow the pinned organization
contract and must not replay a completed target publication effect.

## Authorization and content boundaries

Router admission canonically means `approved`. A material task change requires
a new approved source revision and new `delivery_id`; the target does not
receive or reconstruct the router's source-task identifier. `queued` is only a
post-admission projection, not authorization. The target authenticates and authorizes the
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
supplied `concurrency_group`; and fail closed when caller authentication,
authorization, or routing evidence is stale or improper. It shall not read or
enforce mutable activation state: receipt from the authenticated organization
router is downstream of the router's current activation decision.

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

Verify validates request format/schema, caller, capability and repository/content
policy. It does not invoke Codex, create a branch, or create a PR. Success uses
`execution_status: verified` and the authoritative null-field requirements.

### Implement mode

Implement invokes Codex only after validation, confines changes to this
repository, runs repository and consulting-content validation, and creates or
reuses only a draft PR before emitting the canonical result. Normal CI substitutes
a fake executor and fake publisher. A draft repository change never becomes
automatically published consulting guidance.

## Required no-Codex conformance coverage

Local tests shall consume the organization-owned executable `TC-MVP-CI-001`
fixture oracle and cover: valid verify; valid fake implement; wrong target;
invalid contract version;
invalid schema or format; unauthorized caller; unsupported task type; invalid
concurrency value; stale or improperly routed request; duplicate delivery;
conflicting payload under one delivery ID; existing matching managed draft PR;
ambiguous PR ownership; create-race requery; repository-policy rejection;
consulting-content validation failure; fake executor failure; validation failure;
test failure; publication failure; timeout; valid canonical result; receiver failure
response; identical result redelivery; conflicting result redelivery; no Codex
call; no real branch; and no real pull request.

The pinned fixture oracle supplies the organization contract inputs and expected
results. Conformance tests shall consume those exact semantics without copying,
rewriting, or supplementing organization-owned expectations. Separate local
tests may cover genuinely consulting-playbook-specific repository and content
policy, but they shall not redefine schema, status, activation, delivery,
ownership, or result behavior. Ordinary conformance uses fakes and makes zero
real Codex calls, branches, or pull requests.

The checked-in `.ai-sdlc/conformance/tc-mvp-ci-001.json` executes all 29
organization scenarios; 22 reach the real repository adapter seam. Every Codex,
branch, commit, push, pull-request, merge, release, deployment, production, and
secret-output counter is zero. The `ownership-conflict` case proves an orphaned
branch is rejected before Codex, and create-race cases re-observe both branch and
pull-request state.

## Implementation readiness and operational activation

The repository-owned adapter and no-effects evidence are implemented. Acceptance
still requires review/merge, an immutable `codex-adapter-v*` tag, registry
tag/commit/report bindings, the published and live-verified 2.3.1 receiver,
credential confirmation, and organization compatibility validation. Current
operational activation remains mutable organization control-plane state and is
neither pinned nor enforced here. This repository must not enable itself, and
implementation completion alone is not a claim that live routing is active or
production-ready.
