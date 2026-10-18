# Consulting Playbook next-MVP target-adapter profile

## Authority and scope

This profile is the normative repository-owned implementation baseline. It uses
payload contract `ai-sdlc-contract/v2` and fixture-set manifest
`TC-MVP-CI-001` from the reviewed issue #135 recovery candidate at immutable
`Young-Consultations/.github@e27b8a541afbd27b4be5606a19ffa43637ad312a`.
The current published and attested control-plane release is
`ai-sdlc-v3.1.0` at commit
`e9d11fc99fee73d247c93699f058ed64786bd4c0`; the enabled
consulting adapter is the reviewed immutable `codex-adapter-v3.1.0` at
`4f15841efcba4883770b5e32c0582f733d73eb91`.
The deployed source migration and 3.1.0 no-cost readiness gates passed,
but issue #93's separate content-base safety defect remains open. The earlier published 2.4.5
composition remains initial-live-path evidence: REAL issue #154 produced one
managed draft PR with validation/tests and receiver/source projection
successful. REAL redelivery issue #156 later exposed the result-writer identity
mismatch that drove the 3.0.0 App-credential repair; REAL #159 then exposed
DEF-0073 at the 3.0.0 receiver. Published 3.0.2 repaired that receiver
compatibility boundary and passed deployed Runtime Preflight plus immutable
REAL preflight before source adoption. Published 3.0.3 subsequently
repaired cross-release admission reuse. The current published 3.x path uses the
dedicated GitHub App `ai-sdlc-result-writer` (App ID `5100679`), installed
only on `portfolio-tasks`, to mint a repository-bounded short-lived
installation token and run the organization-owned result credential capability
preflight before Codex. The 3.1.0 adapter conformance report remains immutable
prepublication *compatibility* evidence; the release and runtime preflights
are published, but no newly authorized 3.1.0 REAL content-base
acceptance has occurred. Published 2.4.4
remains immutable previous-generation evidence, but REAL #151 proved it is not
an execution-safe rollback for cost-bearing implementation because its
publication transport can lose successful Codex work. Any rollback that may
invoke Codex must select a separately reviewed safe release or disable REAL
execution.
The immutable `codex-adapter-v2.4.6` tag is retained as unused pre-release evidence because the receiver secret-interface change was subsequently classified as MAJOR under the organization release policy; it must not be selected by the registry or a control-plane release. These interface facts are requirements; conformance is established by the
exact-file pin and executable report described below, while live acceptance is
preserved separately in the governed workflow and source issue evidence.

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
The published registry separately binds the adapter tag, resolved commit, and
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

The currently published control-plane release is `ai-sdlc-v3.1.0`,
and its enabled target registry selects immutable
`codex-adapter-v3.1.0` at
`4f15841efcba4883770b5e32c0582f733d73eb91`.
The historical 3.0.3 release and its adapter are immutable predecessor
evidence, not the active selection.
The earlier 3.0.2 deployed Runtime Preflight 36640642872 and immutable
REAL preflight 36640734704 passed before its source-consumer adoption.
Those historical checks do not establish compatibility with 3.1.0.

REAL #159 was reconciled after its failed 3.0.0-target attempt, preserving the
original trusted 3.0.1 admission. That exposed DEF-0086: the 3.0.2 router
could not reuse the predecessor admission on an unchanged authorized retry.
Published 3.0.3 subsequently repaired that boundary.

The released `codex-adapter-v3.1.0` target for issue #111
uses only the versioned organization receiver. It shall invoke
`Young-Consultations/.github/.github/workflows/codex-result-receiver.yml@ai-sdlc-v3.1.0`
with inputs `execution_result` and `source_issue` and the
`RESULT_WRITER_PRIVATE_KEY` secret, supplied from target secret
`AI_SDLC_RESULT_WRITER_PRIVATE_KEY`. The matching receiver shall mint a
fresh short-lived installation token from GitHub App
`ai-sdlc-result-writer`, not consume a long-lived `CODEX_RESULT_TOKEN`.
The released target additionally binds the admitted execution input
to the 3.1.0 terminal-receipt preflight and rejects an absent safety
classification. Immutable release-tag publication, compatible registry
selection, source migration, deployed Runtime Preflight, deterministic
SIM and no-cost REAL-readiness have completed; **a new cost-bearing REAL
task and issue #93 current content-base acceptance have not**. Ordinary conformance checks
remain zero-effect compatibility evidence and do not replace live acceptance
evidence. Published 2.4.4 remains immutable previous-generation
evidence but is not an execution-safe rollback for cost-bearing implementation
because REAL #151 exposed its publication-transport defect. Any rollback that
may invoke Codex requires a separately reviewed safe release or REAL execution
must remain disabled. Receiver outputs are `accepted`, `delivery_id`, `correlation_id`,
`execution_status`, `failure_category`, and `diagnostic_summary`.

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

Before the adapter can receive the OpenAI credential or invoke Codex, the target
workflow shall reuse the adapter's `admit()` gate to authenticate the dispatch
caller and validate the canonical execution input, target, task type, mode,
branch policy, and transport concurrency value. Only an admitted request may
cross into result-credential probing. The workflow shall then require the
governed source to match `Young-Consultations/portfolio-tasks#<issue>`; mint
an installation token for
GitHub App `ai-sdlc-result-writer` (App ID `5100679`) scoped only to
`portfolio-tasks` with Issues write and Contents write; require the token's
reported app slug to equal `ai-sdlc-result-writer`; and invoke the
organization-owned
`codex-result-credential-preflight@ai-sdlc-v3.1.0`. That preflight shall prove
the trusted result-author identity, issue-comment create/delete access, and the
dedicated no-op repository-dispatch capability. Any failure stops the delivery
before cost-bearing execution. The installation token shall not be supplied to
the Codex adapter.

**Published terminal-receipt safety gate for issue #111 in 3.1.0:**
The immutable control-plane preflight
shall receive the *exact admitted execution input* and query the authenticated,
trusted-author source journal before any cost-bearing execution. A trusted
terminal result that is not a managed-draft effect shall prevent further Codex
execution under the same delivery identity. Unreadable, malformed, or
conflicting trusted result evidence shall fail closed. A trusted single
managed-draft receipt without a forwarding marker may proceed **only** into
verified owned-draft reconciliation, enabling receiver forwarding recovery
without rerunning Codex; an unforwarded non-managed terminal receipt remains
blocked. A prior managed-draft receipt permits only verified owned-draft
reconciliation; if its matching
branch and open draft are missing or inconsistent, reject before Codex. The
target shall consume an explicit safe preflight classification and reject an
absent, unsupported, or legacy `not-checked` classification before remote
effects. The released adapter/receiver and source consumer are version
pinned. Publication is not proof of a current task-content base; new REAL
work remains subject to approved issue #93 security, test and versioned
rollout gates. No second model call is permitted for a terminally failed
delivery.
The preflight's App installation token remains outside the Codex adapter.

Before any executor or publisher effect, the adapter shall authenticate and
authorize the admitted caller; format-check and validate `execution_input_json`
against the exact immutable schema; require target
`Young-Consultations/consulting-playbook`, `ai-sdlc-contract/v2`, an allowed task
type (`automation`, `documentation`, `feature`, or `testing`), local repository
and consulting-content policy, and `draft_pr_only: true`; validate and use the
supplied `concurrency_group`; and fail closed when caller authentication,
authorization, or routing evidence is stale or improper. Before invoking Codex,
the publication identity shall both report repository push permission and
successfully exercise the authenticated Git push transport with a non-mutating
dry-run. Failure or indeterminate transport readiness shall stop the delivery
before the cost-bearing executor is invoked. It shall not read or enforce mutable
activation state: receipt from the authenticated organization router is downstream
of the router's current activation decision.

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


## Approved issue #93: immutable trusted executor and current content baseline

**Architecture approved 2026-10-17. Implementation and REAL acceptance pending.**
The adapter SHALL preserve immutable, independently verified trusted executor
code, policy, schema and validation at the release-bound target SHA, distinct
from a clean task-content worktree pinned to the target's authenticated current
default-branch commit SHA. Before any cost-bearing Codex invocation, bind
the target repository, approved delivery/scope, trusted executor SHA and exact
content base SHA to one provenance record. Missing, malformed, mutable,
inconsistent, inaccessible or unauthorized base evidence fails closed without
a model call. The trusted terminal-journal and managed-draft reuse rules
remain binding and may never be bypassed by fetching a new base.

Codex edits only task-content files in the bounded worktree. Never execute
mutable checkout hooks, package scripts, imports or policy with privileged
credentials. Validators and policy come from the trusted executor and treat
candidate files as untrusted data; any necessary execution of candidate code
requires an independently reviewed credential-free sandbox. Preserve existing
Defect Ledger IDs, content IDs and links and validate `git diff --check`,
path/secret policy and deterministic tests.

The publisher SHALL verify that the candidate parent is exactly the attested
content base and re-read default HEAD just before a non-force topic push.
If moved by then, reject with zero remote writes. After the topic push but
before creating a draft, re-read default HEAD; if moved, do not open a PR,
quarantine any exactly owned topic branch and report a safe partial effect.
After creating a draft, re-read HEAD and mark a stale draft blocked for human
reconciliation. GitHub does not atomically lock unrelated refs: do not claim
zero transient branch effects or guarantee permanent HEAD stability.
Human review SHALL independently revalidate the latest parent and mergeability.
No auto-rebase, force push, automated merge, or second paid Codex invocation
is permitted to repair a moved base.

Fake-effect regression tests SHALL simulate movement before push, after push,
after PR, missing base, conflicting identity, untrusted worktree execution,
owned branch/PR reconciliation and ledger/content conservation. Preserve
all 29 shared contract scenarios with zero real side effects. The executor
change SHALL be published only through a newly reviewed immutable target
release and separately approved organization compatibility/registry gates.
Design approval alone does not authorize REAL execution.

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

The current published control plane is `ai-sdlc-v3.1.0` at immutable
`e9d11fc99fee73d247c93699f058ed64786bd4c0`, selecting the released
target adapter `codex-adapter-v3.1.0` at
`4f15841efcba4883770b5e32c0582f733d73eb91`. Historical published
2.4.5 remains initial-live-path evidence; published 2.4.4 is not a
cost-bearing-execution-safe rollback, as REAL #151 identified possible
loss of successful Codex work. A rollback that could invoke Codex
requires a separately reviewed safe release, or REAL dispatch must be
disabled.

The previously published 3.0.2 path passed its deployed Runtime
Preflight and immutable REAL preflight, but #159 exposed DEF-0086 at the
cross-release admission-reuse boundary; published 3.0.3 subsequently repaired
that defect. Issue #111 identifies a separate **3.0.3 production defect**:
a terminal failed delivery could reach a second cost-bearing Codex call.
The 3.1.0 target and control-plane tags, publication attestation,
source migration, deployed Runtime Preflight 39086605325, no-cost SIM
39087269988 and REAL-readiness preflight 39087311313 passed. They do not
establish separate task-content baseline correctness or new REAL acceptance;
issue #93 remains a cost-bearing implementation release blocker.
Operational activation remains mutable
organization control-plane state and is neither pinned nor administered here.
This repository must not create a second activation switch; routing remains
owned by the organization registry/router. The checked-in zero-effect
conformance report is pre-publication compatibility evidence, not live
acceptance.
