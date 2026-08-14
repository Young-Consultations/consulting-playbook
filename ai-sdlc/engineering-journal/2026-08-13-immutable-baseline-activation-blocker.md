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

[`.github` draft PR #46](https://github.com/Young-Consultations/.github/pull/46)
proposes ADR-015 and separates the identities:

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
evidence. PR #46 is draft, the registry evidence remains null, no adapter or
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
