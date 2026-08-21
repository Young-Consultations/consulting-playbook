# 2026-08-13 — Immutable baseline blocked target activation

- **Date:** 2026-08-13
- **Decision status:** resolved; recovery implementation remains open
- **SDLC phase:** acceptance-review

## Context

Issue [portfolio-tasks #117](https://github.com/Young-Consultations/portfolio-tasks/issues/117)
was ready to change mutable target activation only after issue #116 had proved
each target's conformance to
`Young-Consultations/.github@c6090e5bbadcc2102a1cb91875466e9decdada1e`.
A [P0 recovery epic](https://github.com/Young-Consultations/portfolio-tasks/issues/135)
now owns remediation before issue #117 may resume.
A readiness review compared that exact control-plane baseline with repository
snapshots and current GitHub issue, pull-request, tag, workflow, and Actions
evidence for `.github`, `portfolio-tasks`, `consulting-playbook`, and `slugger`.

The review was an acceptance gate. It did not enable a target, run Codex, create
a branch or pull request, alter secrets/settings, merge, release, deploy, or
perform a production operation.

## Discovery

No core target was ready for activation. The baseline and evidence chain contain
several independent blockers:

1. The immutable registry at `c6090e5` records every target workflow reference
   as `@main`, but the same baseline's router rejects an enabled target unless
   its workflow reference matches `codex-adapter-vMAJOR.MINOR.PATCH`. None of the
   four core repositories had such a tag. Enabling any target would therefore
   make baseline validation fail.
2. The router dynamically invokes a target with `gh workflow run`, while three
   target workflows expose only `workflow_call`. The control-plane verifier also
   expects `workflow_dispatch` plus obsolete artifact/run-ID inputs, which
   conflicts with the documented exact two-input interface.
3. The pinned result receiver requires `CODEX_RESULT_TOKEN` and
   `CODEX_TRUSTED_JOURNAL_AUTHORS`. Three target calls omit the latter, while the
   `.github` target pins an older receiver. More fundamentally, a caller-supplied
   trusted-author policy assigns an organization authorization decision to the
   target side of the boundary.
4. Green conformance did not prove shared compatibility. The control-plane check
   skipped every disabled target; portfolio explicitly recorded insufficient
   activation evidence; consulting exercised 26 repository-defined 2.2.0 cases
   rather than the 29-scenario 2.3.0 oracle; and Slugger used vendored input and
   result schemas whose blob identities differ from the exact baseline.
5. The three consumer target implementations contain additional canonical
   input/result discrepancies. The portfolio source-routing workflow also fails
   before any job starts; its caller permission declaration lacks the reusable
   router's requested `actions: read` permission.

The closure of issue #116 is therefore historical workflow state, not sufficient
activation evidence. Issue #117 must remain blocked with all targets disabled.

## Why it matters

This is not a routine activation/configuration defect. The approved immutable
unit is internally unable to represent an enabled conforming target, and the
verification path can report success without exercising any target. Treating a
green local or skipped test as release evidence could route paid, mutating AI
work into an adapter that cannot be invoked or cannot return a canonical result.

The finding also demonstrates why compatibility must be proven as a complete
producer/transport/consumer/receiver chain. Each repository can appear locally
reasonable while the assembled system has no executable path.

## Related defect(s)

- DEF-0012 — immutable activation baseline circularity
- DEF-0013 — router/target trigger mismatch
- DEF-0014 — receiver trust and compatibility boundary
- DEF-0015 — false conformance assurance
- DEF-0016 — portfolio target schema divergence
- DEF-0017 — consulting target and fixture divergence
- DEF-0018 — Slugger vendored schema divergence
- DEF-0019 — portfolio source-workflow permission mismatch

## Evidence

- [Issue #117 activation gate](https://github.com/Young-Consultations/portfolio-tasks/issues/117)
- [Issue #116 conformance definition](https://github.com/Young-Consultations/portfolio-tasks/issues/116)
- [`c6090e5` target registry](https://github.com/Young-Consultations/.github/blob/c6090e5bbadcc2102a1cb91875466e9decdada1e/config/codex-repositories.json)
- [`c6090e5` router implementation](https://github.com/Young-Consultations/.github/blob/c6090e5bbadcc2102a1cb91875466e9decdada1e/scripts/codex_router.py)
- [`c6090e5` result receiver](https://github.com/Young-Consultations/.github/blob/c6090e5bbadcc2102a1cb91875466e9decdada1e/.github/workflows/codex-result-receiver.yml)
- [Control-plane compatibility run that skipped disabled targets](https://github.com/Young-Consultations/.github/actions/runs/31679643235)
- [Portfolio source-routing startup failure](https://github.com/Young-Consultations/portfolio-tasks/actions/runs/31754000425)
- [Consulting target workflow startup failure](https://github.com/Young-Consultations/consulting-playbook/actions/runs/31753474069)
- Conformance work: [.github PR #42](https://github.com/Young-Consultations/.github/pull/42),
  [portfolio PR #131](https://github.com/Young-Consultations/portfolio-tasks/pull/131),
  [consulting PR #21](https://github.com/Young-Consultations/consulting-playbook/pull/21),
  and [Slugger PR #107](https://github.com/Young-Consultations/slugger/pull/107)
- Repository snapshots reviewed on 2026-08-13, including each active target
  workflow, conformance fixture/report, schema source, and local policy code

## What implementation or testing exposed

The implementation exposed a cross-layer contradiction that individual unit
tests did not surface: the documentation described a reusable target workflow,
the router implemented dynamic workflow dispatch, and verification encoded a
third interface containing retired inputs. The receiver likewise evolved without
an atomic consumer migration.

The conformance work then reproduced repository-local expectations instead of
executing the organization-owned oracle through the real adapter seam. A disabled
registry made the organization check green by omission. This is a concrete
false-positive pattern: success meant "nothing failed among zero exercised
targets," not "the targets conform."

## Requirement or architecture implications

The owner approved these recovery decisions on 2026-08-13:

1. The dynamically selected MVP target entry point is `workflow_dispatch` with
   exactly `execution_input_json` and `concurrency_group`.
2. Trusted-journal-author policy belongs to immutable `.github` control-plane
   configuration. Targets do not supply that policy; they receive only the
   narrowly scoped result-delivery credential required by the approved transport.
3. Preserve `c6090e5` as a historical baseline and publish a corrected immutable
   patch baseline after validation. Repinning is required because a genuine
   protocol/capability defect was found, not because mutable activation changed.

These decisions must be implemented and made authoritative in the owning
`.github` repository before consumer requirements, interfaces, or compatibility
pins are migrated. This journal records the discovery and decision context; it
does not replace organization-owned architecture or release artifacts.

## Lessons learned

- An immutable release should be validated with at least one representative
  enabled target before it becomes the activation prerequisite.
- A green compatibility job must distinguish `tested`, `skipped`, and
  `activation_evidence_sufficient`; zero tested targets cannot satisfy release
  acceptance.
- Shared-oracle conformance means running exact organization fixtures and schemas
  through the real adapter boundary, not recreating expected behavior locally.
- Workflow event type, input schema, permissions, secrets, tags, and receiver
  version are one cross-repository interface and should migrate atomically.
- "AI-correct/specification-wrong" is a useful classification when generated
  implementations faithfully follow conflicting authoritative interface
  descriptions; acceptance review still has to assemble the whole system.

## `AI_CONTEXT.md` impact

`AI_CONTEXT.md` and the root README need a focused correction now: the checked-in
adapter and green repository-local report are not activation evidence, the
target must remain disabled, and `c6090e5` is awaiting an organization-owned
replacement. The normative compatibility documents should not be repinned until
the corrected `.github` release exists and its exact commit is reviewed.

The other three repositories' `AI_CONTEXT.md` files also require review during
their recovery changes. This repository does not author those external context
files.

## Follow-up

1. Complete [P0 recovery epic #135](https://github.com/Young-Consultations/portfolio-tasks/issues/135),
   which is linked to issues #114 through #117.
2. Correct control-plane architecture, receiver trust ownership, dispatch
   contract, validation, and negative tests.
3. Correct each target and the portfolio source permission boundary.
4. Execute the complete shared oracle through each real adapter with explicit
   no-real-effects traps.
5. Publish immutable adapter tags and a corrected compatibility baseline.
6. Migrate consumers to the exact new commit, then activate one proven target at
   a time through issue #117.

## Potential consulting or content value

This is a strong case-study candidate for the proposition that AI-SDLC defects
often concentrate at authority, interface, and verification boundaries rather
than in code generation itself. It illustrates immutable-release circularity,
locally green but globally incompatible adapters, skipped-test false assurance,
and the value of treating cross-repository workflows as a single versioned
product interface.

## 2026-08-14 addendum — Evidence identity was self-referential

The control-plane recovery in
[`.github` PR #45](https://github.com/Young-Consultations/.github/pull/45)
was merged as
[`e27b8a5`](https://github.com/Young-Consultations/.github/commit/e27b8a541afbd27b4be5606a19ffa43637ad312a).
The first target-specific readiness pass then exposed a second-order release
defect, recorded as DEF-0020.

The merged verifier required a committed conformance report's
`adapter_revision` to equal the registry's `adapter_commit_sha`, while the
report itself had to exist at that adapter commit. This requirement cannot be
constructed: Git derives a commit SHA from its tree, the tree includes the
report, and changing the report to name the new SHA changes the tree and SHA
again. A review gate that no artifact can satisfy is fail-closed, but it is not
a usable recovery control.

[`.github` PR #46](https://github.com/Young-Consultations/.github/pull/46),
merged as
[`b3df35f`](https://github.com/Young-Consultations/.github/commit/b3df35f1d11da3bfed49f0e68b725f7f50936f10),
implements ADR-015 and separates the identities:

1. a canonical v2 conformance pin records the compatibility SHA plus exact Git
   blob identities for organization schemas/fixtures and target
   workflow/adapter/harness files;
2. the pin's `adapter_revision` is a SHA-256 over canonical pin contents with
   that revision field treated as null, so the pin does not hash itself;
3. the report records the pin revision, complete scenario results, and effect
   counters, but never predicts its containing commit;
4. after review and merge, the registry independently records the immutable
   adapter tag, the commit resolved from that tag, and the committed report
   SHA-256; and
5. live verification recomputes all three relationships and rejects pins that
   include either the pin or report in their target-file set.

The draft also corrects the `.github` target receiver call and create-race
ambiguity handling. Its deterministic candidate report runs all 29
`TC-MVP-CI-001` scenarios; 22 reach the real repository adapter seam, while the
remaining cases preserve router-only or missing-result boundaries. Codex,
branch, commit, push, pull-request, merge, release, deployment, production, and
secret-output counters are all zero. The report explicitly says the adapter tag
is unpublished and live receiver verification remains pending the reviewed
`ai-sdlc-v2.3.1` tag.

This is reviewable target evidence, not activation or production-readiness
evidence. The registry evidence remains null, no adapter or
compatibility tag has been created, the receiver allowlist remains deny-all,
and every target remains disabled.

### Prevention rule added by this discovery

- Never require an artifact to contain the digest or commit identity whose
  calculation includes that artifact.
- Separate identities by lifecycle stage: pre-commit content manifest,
  post-commit immutable object, and externally recorded adoption/evidence
  binding.
- Add a release-construction test that produces the exact evidence package in
  the documented order; schema validation alone cannot prove constructibility.
- Verify each relationship independently at the immutable ref: tag to commit,
  report bytes to report digest, report to pin revision, and pin entries to file
  blobs.
- Exclude the pin and report from their own bound file set, and make that a
  negative test.
- State pending operational gates in the evidence itself so a complete
  no-effects oracle is not mistaken for a published tag, live receiver proof,
  credential readiness, or activation approval.

The recovery sequence therefore remains unchanged at the governance level:
review and merge the constructible evidence model, correct each target, review
real-adapter zero-effect reports, publish immutable adapter tags only after
their evidence gates pass, finalize the `.github` compatibility release, and
then return to issue #117 one disabled-first target at a time.

## 2026-08-14 second addendum — The verifier inspected the wrapper while preflight missed the branch

After `.github` PR #46 and consulting-playbook PR #24 merged, the recovery moved
to the first low-blast-radius consumer target: consulting-playbook. Translating
the accepted adapter/evidence pattern into that repository exposed two more
cross-layer defects, recorded as DEF-0021 and DEF-0022.

First, `verify_target_workflows.py` searched the target workflow source for
words including `preflight`, `ownership marker`, `create-race`, and
`duplicate-reused`. The workflow is now intentionally a thin dispatch and
receiver wrapper; executable ownership behavior lives in the exact
`scripts/codex_target_adapter.py` blob already bound by the conformance pin.
The syntactic check therefore inspected the wrong layer. A correct wrapper
without explanatory comments would fail, while comments containing those words
could pass without implementing the behavior.

Second, the merged adapter preflight queried pull requests by deterministic head
branch but did not query branch existence independently. No matching PR was
treated as a new delivery. If the branch existed without a PR, Codex could run
again before the later non-force push failed. That violated the recovery
requirement that ambiguous ownership fail before paid execution.

The corrective `.github` draft PR is https://github.com/Young-Consultations/.github/pull/47. It:

1. limits static workflow verification to the exact two-input dispatch and
   receiver interface;
2. relies on the mandatory non-recursive pin and complete real-adapter oracle
   for idempotency behavior;
3. changes the adapter ownership observation to include branch existence plus
   every pull request;
4. rejects branch/PR disagreement as `ambiguous-rejected` before Codex;
5. repeats both observations after a create race; and
6. maps the shared `ownership-conflict` scenario to an orphaned branch while
   retaining unit coverage for conflicting payload digests and multiple drafts.

The consulting target adopts the same corrected behavior. Its candidate replaces
the obsolete `workflow_call` path and 26-case local oracle with exact
`workflow_dispatch`, canonical v2 schema/result handling, the planned immutable
2.3.1 receiver, a non-recursive exact-file pin, and all 29 organization
scenarios. Twenty-two scenarios invoke the real consulting adapter seam. Every
Codex, branch, commit, push, pull-request, merge, release, deployment,
production, and secret-output counter is zero.

### Prevention rules added by this discovery

- Verify each property at the layer that owns it: wrapper syntax for transport,
  executable tests for adapter behavior, and immutable identities for adoption.
- Never treat comments, names, or keyword presence as proof of a behavioral
  security or reliability property.
- Model remote ownership as the combination of branch state and pull-request
  state; neither is a safe proxy for the other.
- Exercise orphaned and contradictory state before any paid or mutating
  boundary, not only during publication cleanup.
- When implementation moves behind a new seam, review every verifier to ensure
  it follows the seam rather than the old file layout.

This evidence remains pre-activation. Both corrective changes are draft review
work; no adapter tag, compatibility tag/release, secret/setting change, Codex
call, live receiver acceptance, or target activation is part of them.

## 2026-08-14 third addendum — The target recovered, but the source could not produce or consume the contract

The corrective control-plane and first-consumer work have now merged:

- [`.github` PR #47](https://github.com/Young-Consultations/.github/pull/47)
  merged at
  [`4b0ff4f`](https://github.com/Young-Consultations/.github/commit/4b0ff4f86429412261ee2887d11a1c124c397a8b);
- [consulting-playbook PR #25](https://github.com/Young-Consultations/consulting-playbook/pull/25)
  merged at
  [`3ee195c`](https://github.com/Young-Consultations/consulting-playbook/commit/3ee195c0866b903b0f0b7ecb7bd48a8e0f697025); and
- the replacement consulting `Immutable MVP conformance` push run
  [31857176623](https://github.com/Young-Consultations/consulting-playbook/actions/runs/31857176623)
  completed successfully.

Those merges resolve DEF-0021 and DEF-0022 at the central and first-consumer
layers. Applying the same accepted adapter/evidence pattern to
`portfolio-tasks` then exposed two source-side failures that target-only
conformance could not reveal.

### DEF-0023 — The source could not construct task-contract/v2

The source lifecycle generated `task_id` as
`owner/repository#issue@digest`. The exact task schema permits only letters,
digits, dot, underscore, and hyphen, so every such identity was invalid. The
constructed payload also omitted required `risk`, `scope`, and
`created_by` fields and merged arbitrary material fields into a closed
schema. Finally, generic lower-and-replace normalization converted issue-form
choices such as `Refactor`, `Repository governance`, and `Investigation`
to values that the canonical schema does not permit.

The identity digest covered only a material mapping. Target, execution mode,
executor, dependency state, and sensitivity could therefore change without
changing the task identity or invalidating the earlier approval. The producer
had local unit coverage, but no test validated its actual output against the
exact shared task schema.

### DEF-0024 — The source result path contradicted the corrected receiver

The portfolio target directly called a source `workflow_call` and supplied a
target-held `PORTFOLIO_RESULT_TOKEN`. The corrected organization receiver
does neither: after validating the target, result schema, trusted admission
journal, and replay state, it forwards a bounded
`ai-sdlc-execution-result-v2` `repository_dispatch` to the source.

The source journal was also incompatible. It wrote the older free-form
`ai-sdlc-admission: task=...` marker, while the receiver accepts only the
canonical `ai-sdlc-admission:v2` JSON binding. Even a correct target result
therefore had no admission record the receiver could authorize. The local
projection expected fields that are not present in the corrected closed result
schema, so direct invocation did not merely bypass ownership; it implemented a
different protocol.

### Candidate correction and evidence

The portfolio recovery candidate now:

1. constructs exactly the closed task fields and validates them against the
   exact shared schema;
2. derives a schema-safe task hash from source material plus target, mode,
   executor, dependencies, and sensitivity, so every authority change requires
   fresh approval;
3. explicitly maps issue-form values to canonical task types and rejects
   obsolete or unknown categories;
4. adds the reusable router's required `actions: read` permission;
5. writes the exact v2 JSON admission binding after successful routing;
6. removes direct target-to-source invocation and the target-held source token;
7. accepts only an allowlisted receiver `repository_dispatch`, repeats exact
   schema and admission checks, treats identical delivery replay as a no-op,
   and quarantines conflicts; and
8. replaces the parallel portfolio target/conformance implementation with the
   same exact two-input adapter and non-recursive evidence pattern already
   accepted in the central and consulting repositories.

The candidate `TC-MVP-CI-001` report has SHA-256
`0d3d062e29bace8e20c745bc6639d4205d007bc8813d936f4382f5ea85f18d66`.
All 29 shared scenarios pass, 22 invoke the real portfolio adapter seam, and
all ten prohibited-effect counters are zero. Its canonical pin revision is
`sha256:de71418de78bcfdfffb1f4fc02ccf0a0da2fcc9eaf68a8d580526f4c89c4078c`.

### Prevention rules added by this discovery

- Test every producer, not only every consumer, against the exact closed schema
  it claims to emit.
- Require a content-derived identity to both satisfy its own schema and bind
  every field that can change authority, routing, or effect semantics.
- Map human-facing enumerations explicitly; generic string normalization is not
  contract validation.
- Exercise the complete receiver-to-source transport and journal marker in
  interface tests. A schema-valid target result is insufficient if the source
  cannot authenticate or project it.
- A target may deliver a result to the organization receiver, but it must not
  own receiver trust policy, hold a general source-write credential, or invoke
  source projection directly.
- When an interface owner changes forwarding semantics, search every producer,
  marker, source consumer, secret declaration, and test assertion for the old
  path before calling the compatibility unit complete.

The portfolio candidate remains review work. DEF-0023 and DEF-0024 stay open
until that change is reviewed and merged. DEF-0016 and DEF-0019 also remain
open until the same merge supplies the canonical target and proves the repaired
source workflow starts. No target, adapter tag, compatibility tag/release,
receiver identity, secret/setting, paid Codex run, live result acceptance, or
activation is created by this discovery record.

## 2026-08-20 fourth addendum — Slugger recovered the contract but exposed a publication credential boundary

The portfolio recovery described above has now merged in
[portfolio-tasks PR #136](https://github.com/Young-Consultations/portfolio-tasks/pull/136)
at
[`42f01e4`](https://github.com/Young-Consultations/portfolio-tasks/commit/42f01e40fd148c1d16aa93828921234a9cfa95da).
That merge resolves DEF-0016, DEF-0019, DEF-0023, and DEF-0024 at the
repository source and target layers. It does not publish the receiver release,
configure credentials, or activate a target.

Applying the same accepted recovery architecture to Slugger produced
[open PR #108, ready for review](https://github.com/Young-Consultations/slugger/pull/108).
Its historical `4491911b6926ef382b3385f09bc586951408ad4a` recovery snapshot
removes the obsolete nested payload and `workflow_call` contract, uses only
the exact two-input `workflow_dispatch` transport, consumes byte-identical v2
schemas and fixtures from compatibility candidate
`e27b8a541afbd27b4be5606a19ffa43637ad312a`, and calls the planned
organization-owned `ai-sdlc-v2.3.1` receiver with only `CODEX_RESULT_TOKEN`.

The complete report for that historical snapshot has SHA-256
`4e9956f55829b67619cb7ee48b56e86650dfb63cdb7df812c76fa4e696231690`. Its
non-recursive adapter revision is
`sha256:0269531b66ae43303a91d7e3f24394dd80ebd6921543602a5c3bf8a106b6c7cf`. All
29 organization scenarios pass, 22 invoke the real Slugger adapter seam, and
every Codex, branch, commit, push, pull-request, merge, release, deployment,
production, and secret-output counter is zero. This historical evidence
addresses the candidate behavior for DEF-0018 but does not resolve it until
review and merge.

### DEF-0025 — The publication token was placed in a Git process argument

The former Slugger publisher built an authenticated remote URL containing the
publication token and passed that URL to `git push`. Even when command output is
suppressed, command arguments can be observable through process inspection,
diagnostics, exception text, or future logging. The implementation also relied
on redaction that did not cover every supported GitHub token prefix. No token
value was collected, copied, or published during this review.

The historical `4491911b6926ef382b3385f09bc586951408ad4a` correction candidate
uses the normal anonymous HTTPS remote. A temporary `GIT_ASKPASS` helper
contains only logic and reads the password from its environment; it never
contains the credential. Terminal prompting is disabled, push output is
suppressed, the helper is removed in a `finally` block, and externally
reported failures use sanitized categories instead of command or exception
text. Current review of PR #108 still needs to confirm that anonymous
discovery stays separate from credentialed publication so preflight reads do
not receive the publication token.

### Prevention rules added by this discovery

- Prevent secret exposure structurally; redaction is a secondary control, not
  permission to place credentials in URLs, arguments, files, results, or logs.
- Keep anonymous discovery separate from credentialed publication so preflight
  reads do not receive publication credentials, and construct any credentialed
  environment from an explicit safe allowlist.
- Keep credential helpers secret-free. They may read an environment value at
  execution time but must not persist or echo it.
- Suppress effect-boundary output and translate failures into fixed safe
  categories before they cross repository or workflow boundaries.
- Add regression checks for token-bearing remote construction and all supported
  credential prefixes, while never using a real credential in tests.
- Review transport, execution, validation, publication, and result delivery as
  separate credential boundaries; a workflow-level least-privilege declaration
  does not prove subprocess-level secret handling.

The finding reinforces the broader issue #135 lesson: passing interface tests
is necessary but not sufficient. Recovery review must also inspect how each
effect boundary constructs commands, scopes credentials, reports failures, and
proves that sensitive values cannot enter durable or observable artifacts.

Slugger PR #108 remains open review work. Package build and `actionlint` are
GitHub CI gates. No target activation, immutable adapter tag, compatibility
release, live receiver dispatch, paid Codex execution, merge, deployment, or
production action is part of this addendum.
