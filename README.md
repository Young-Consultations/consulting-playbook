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

The next-MVP adapter interface is `.github/workflows/codex-execute.yml`. It has
exactly the two routing inputs `execution_input_json` and `concurrency_group`.
Its approved compatibility unit is release `2.2.0` at immutable commit
`c6090e5bbadcc2102a1cb91875466e9decdada1e`. The adapter
must consume `contracts/task-contract.schema.json`,
`contracts/execution-input.schema.json`, and
`contracts/execution-result.schema.json` directly at that commit. No published
package, undocumented module, mutable branch, unavailable tag, artifact/run-ID
transport, or local contract copy is supported.

The immutable compatibility unit contains protocol and target-capability
semantics, not current operational activation. Mutable activation is owned and
enforced by the organization router before dispatch. This target must not reject
an authenticated, otherwise valid routed request because historical compatibility
content predates activation, and it must not enable or disable itself. The checked-in issue #114 adapter implements this repository's
canonical target workflow and repository-local contract checks. Its presence does not itself
activate live routing or prove the mutable organization-router state.

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

## Required idempotent publication protocol

The canonical `delivery_id` is
the logical publication identity. It must be stable across dispatch retries and
must not be a workflow run ID. The target branch convention is:

```
consulting-codex/<normalized-delivery-id, at most 40 characters>-<first 16 hex characters of SHA-256(delivery-id)>
```

The hash prevents values that normalize or truncate to the same readable slug
from colliding. A router-supplied `requested_branch` is accepted only when it is
exactly the branch this convention derives for the supplied delivery identity.

Every managed pull request body contains exactly one machine-readable ownership
marker. The canonical marker is embedded as:

```
<!-- ai-sdlc-delivery-id: delivery-id -->
```

Before Codex is invoked, the target queries the remote branch and all open,
closed, and merged pull requests with that head. A missing branch and no pull
requests is a new delivery. Exactly one open draft with a valid, exactly matching
marker and the deterministic branch is a completed publication: redelivery
returns that pull request URL and skips Codex, branch creation, and PR creation.
This also handles a lost terminal acknowledgement. A newly pushed branch is
eligible for PR creation only in the same attempt that successfully created it.

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
