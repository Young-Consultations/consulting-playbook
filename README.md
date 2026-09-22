# consulting-playbook

`Young-Consultations/consulting-playbook` is the authoritative home for reusable
consulting knowledge and its product requirements. Its current next-MVP
contribution is one bounded organization-routed target adapter.

## Repository direction

The [Consulting Playbook Vision](docs/VISION.md) defines the intended direction for this repository as Young Consultations' reusable consulting operating system. The target-executor workflow described below is an enabling delivery mechanism for approved implementation work; it is not the full consulting-playbook product vision, and the envisioned consulting methods and assets still require requirements development and implementation.

## Consulting knowledge

- [AI-SDLC learning](ai-sdlc/README.md) captures organization-wide learning and consulting evidence without replacing product requirements or architecture.
- [Defect metrics](ai-sdlc/defects/metrics-definition.md) define the initial quantitative measures and their interpretation.
- [Engineering Journal](ai-sdlc/engineering-journal/README.md) preserves material discoveries and lessons that need narrative context.
- [Consulting content](ai-sdlc/content/README.md) separates ideas, drafts, and published posts.
- [Consulting operating system](consulting/README.md) contains engagement methods, assessments, reports, and client-facing templates.

## AI-SDLC control plane

The shared AI-SDLC execution control plane is owned by `Young-Consultations/.github`. That organization repository owns canonical schemas, task and execution validation, contract versioning, repository registry, routing policy, shared failure categories, and correlation behavior.

`Young-Consultations/portfolio-tasks` owns portfolio backlog issues, structured intake and governance metadata, explicit human approval, and initiating the organization router. It does not own shared execution schemas or target execution-result contracts.

The sole next-MVP target interface is
`.github/workflows/codex-execute.yml` using `workflow_dispatch` with exactly
the two required string inputs `execution_input_json` and
`concurrency_group`. No `workflow_call`, artifact/run-ID, field-by-field, or
fallback entry point is active.

The published 2.4.3 target pins the organization receiver to
`ai-sdlc-v2.4.3`, Codex CLI to `0.154.0`, model to `gpt-5.3-codex`, and the
runtime schema validator to `4.26.0`. Issue #150 reached Codex but exposed
missing GitHub runner sandbox preparation and an empty implementation reported
as `no-changes`. This candidate restores runner preparation before credential
handoff and fails an implement task with no candidate changes before repository
validation. Its regenerated zero-effect evidence is bound by
`config/mvp-conformance-pin.json`. Publish it through a new immutable patch
release and rerun deployed preflight before another REAL approval. The published
2.4.3 and 2.4.2 units are unchanged.

The recovery evidence is bound to
`Young-Consultations/.github@e27b8a541afbd27b4be5606a19ffa43637ad312a`.
`config/mvp-conformance-pin.json` records the exact Git blob identities for the
three canonical schemas, complete 2.3.0 `TC-MVP-CI-001` fixture set, and this
repository's workflow, adapter, and harness. The checked-in organization files
are byte-exact evidence copies, not a locally redefined contract. No package,
undocumented module, mutable branch, or unavailable compatibility behavior is
supported.

The immutable compatibility unit contains protocol and target-capability
semantics, not current operational activation. Mutable activation is owned and
enforced by the organization router before dispatch. This target must not reject
an authenticated, otherwise valid routed request because historical compatibility
content predates activation, and it must not enable or disable itself. The
former issue #114 workflow_call adapter and repository-defined 26-case fixture
have been removed from the active path. The replacement runs the complete
29-scenario organization oracle through `scripts/codex_target_adapter.py`; 22
scenarios reach that real adapter seam and every prohibited effect counter is
zero. The 2026-08-13
[activation-readiness review](ai-sdlc/engineering-journal/2026-08-13-immutable-baseline-activation-blocker.md)
found cross-repository trigger, payload/result, receiver, branch, fixture, and
baseline-release blockers. Those compatibility gates are now satisfied for this
repository by `codex-adapter-v2.3.1`, the published 2.3.1 receiver, and the
registry's tag/commit/report binding. The target remains disabled because
operational activation, credentials, retention, reconciliation, and the
controlled end-to-end test are separate human-governed gates.

Upgrades to the organization control-plane release require an explicit reviewed repository change. Rollback must pin the workflow to the previous immutable known-good organization release.

## Target execution responsibilities

The consulting-playbook target workflow owns only repository-specific behavior:

- validating that the canonical input targets `Young-Consultations/consulting-playbook`;
- requiring the executor to be Codex;
- authenticating the admitted caller and enforcing the canonical admitted request plus repository-local policy without a mutable source-label approval recheck;
- enforcing draft-only publication, no automatic merge, and no direct push to `main`;
- deriving deterministic implementation branches from canonical delivery identity;
- running repository validation and tests before publication;
- producing canonical execution-result/v2 and separately invoking the organization-owned canonical result-receiver interface.

Verify mode is non-mutating: it validates the canonical contract, routing authorization, repository policy, and safe repository checks, but it does not invoke Codex, create a branch, commit, push, or create a pull request.

When an admitted request is dispatched by the organization router, implement
mode may run one bounded executor and create or reuse one deterministic draft
pull request. Target execution can never merge
automatically; human review and merge are always required.

Before implementation, the production adapter confirms that the separate
publication identity has write access to this repository. It then mirrors the
controlled authentication preflight: the API key enters only `codex login
--with-api-key` over standard input, login state is stored in a fresh temporary
`CODEX_HOME`, and the runner shell is replaced before the adapter re-executes
with a secret-free process environment. Before execution, the adapter replaces
the login file with a FIFO for each of Codex's two startup auth reads, rotating
the pathname after each reader connects. Codex consumes the admitted prompt
from deadline-bounded stdin after the first auth read and before starting its second auth
manager. The adapter removes that manager's FIFO when it attaches, before
model tools can run. The raw key is therefore absent from
the executor environment, readable filesystem paths, and ancestor process
environments while model tools can run. The publication credential and trusted
caller allowlist cross the same anonymous handoff rather than remaining in the
process environment. Codex runs from this repository root
with the pinned client and model under the `workspace-write` sandbox. Draft-PR
creation remains the authoritative check of the
publication token's pull-request write permission because GitHub provides no
read-only permission probe for that scope.

The target workflow enables unprivileged user namespaces and removes the
Ubuntu AppArmor restriction for them on its ephemeral GitHub runner before
secrets are supplied to the adapter. An implement task must produce candidate
repository changes before validation. Empty output is a failed Codex runtime
result; repository checks of an unchanged checkout do not satisfy the task.
The result is still sent to the receiver, while the execute job fails for an
unsuccessful canonical outcome.

The isolated Codex home is removed after execution. Cleanup first removes
`auth.json`, then requires a bounded quiet period with no home directory to
handle delayed plugin-cache writes. Persistent cleanup failure is reported
without printing local paths or credentials.

### Codex authentication preflight

The manual `.github/workflows/codex-auth-preflight.yml` workflow checks the
runtime credential separately from task delivery. It enters the protected
`consulting-playbook-codex` environment, installs the same pinned Codex CLI as
the target workflow, uses the same explicitly pinned model, authenticates from
`OPENAI_API_KEY` over standard input, and makes one fixed, read-only provider
probe. It has no repository checkout,
GitHub permissions, publication credential, result-delivery credential, or
automatic trigger.

A passing preflight is time-specific evidence that the environment credential,
pinned client, and current provider/model route can complete a request. It is
not contract-conformance, release, activation, production-readiness, or task
execution evidence. Provider output and the credential are not published.

Each attempted stage reports its name, original exit code, client and run ID. A successful
`login` means only `credential-stored`; only a successful `probe` reports
`authenticated`. The exact failure-category allowlist is:

`missing-credential`, `authentication`, `authorization-or-model-access`, `quota`,
`rate-limit`, `transport`, `codex-runtime`, `cli-arguments`,
`client-configuration`, `sandbox`, `local-filesystem`, `client-unavailable`,
`provider-service`.

The machine-style codes `permission_denied` and `permission-denied` are treated
as authorization hints. Plain `Permission denied` without provider context
remains a local-filesystem hint; explicit HTTP 403 or model context takes precedence.
Sandbox hints require failure context on the same line as a sandbox mechanism;
normal startup headers such as `sandbox: read-only` do not classify a failure.
These are text-pattern diagnostic hints, not proof of root cause. Unknown
failures retain `codex-runtime` with the failing stage and original exit code.
The raw log is private and deleted after classification; arbitrary provider
text, credential values, and request bodies never enter the summary.

After merging a diagnostic repair, start a **new** manual run on `main` in
Actions → Codex authentication preflight. Rerunning an old run uses its old
workflow revision. Do not retry a governed implementation delivery merely
because login succeeded; first require the provider probe to pass.

## Required idempotent publication protocol

The canonical `delivery_id` is the logical publication identity. It must be
stable across dispatch retries and must not be a workflow run ID. The active
target branch convention is:

```
codex/<lowercase-delivery-id>
```

A router-supplied `requested_branch` is accepted only when it is null or
exactly the branch derived from the schema-valid delivery identity.

Every managed pull request body contains exactly one machine-readable ownership
marker. The canonical marker is embedded as:

```
<!-- ai-sdlc-delivery-id: delivery-id; payload-sha256: canonical-payload-digest -->
```

Before Codex is invoked, the target independently queries branch existence and
all open, closed, and merged pull requests with that head. A missing branch and
no pull requests is a new delivery. Exactly one existing deterministic branch
and one open draft with a valid, exactly matching marker is a completed
publication: redelivery returns that pull request URL and skips Codex, branch
creation, and PR creation. Branch/PR disagreement, including an orphaned branch
or a PR whose branch is missing, fails `ambiguous-rejected` before paid
execution. This also handles a lost terminal acknowledgement.

Create conflicts are recovered without sleeps: the losing attempt immediately
re-queries and may reuse exactly one valid managed draft. Concurrency using the
router-provided group merely serializes overlapping attempts; it is not the
idempotency mechanism and does not establish exactly-once execution.

A branch without a PR, an invalid or conflicting marker, multiple matching
drafts, a non-draft managed PR, or a closed/merged prior managed PR fails closed.
Automation never overwrites the branch, replaces a prior PR, or closes an
ambiguous/user-owned PR. An operator must inspect branch ancestry and every PR
marker, preserve evidence, and either repair the existing managed draft or ask
the control plane to authorize a **new logical delivery identity**. Retrying the
same identity is not a recovery authorization.

The publication guarantee is: for one canonical delivery identity, this target
maps to one deterministic managed branch, permits at most one open managed draft
PR, and performs at most one completed publication effect. This is an
exactly-once **publication-effect** guarantee under GitHub's branch/PR atomicity
boundaries, not a claim that Codex itself executes exactly once. A retry racing
before either attempt publishes can execute Codex more than once, but only one
valid publication can be accepted.

The canonical result retains the delivery input (including delivery and
correlation identity), source issue, target repository, deterministic branch,
PR URL, workflow URL, terminal status, and a shared-contract failure category.
Locally generated messages are fixed, sanitized descriptions; prompts, tokens,
and secrets are never included.

### Rollout and rollback

Operational activation remains separate organization control-plane state and is
not changed by this repository. The exact target inputs are
`execution_input_json` and `concurrency_group`; see the
[next-MVP profile](docs/requirements/NextMVP.md) for the complete immutable
interface, approval/content boundaries, and fake conformance requirements.
Existing run-ID branches are legacy and are not adopted automatically. Rollback
must disable dispatch first and must not redeliver identities already published
until operators reconcile their managed PRs.
