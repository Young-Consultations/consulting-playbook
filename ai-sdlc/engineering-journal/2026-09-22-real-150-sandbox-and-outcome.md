# 2026-09-22 — REAL #150 reached Codex but did not implement

- **Date:** 2026-09-22
- **Decision status:** resolved for target repair; live verification pending
- **SDLC phase:** integration and REAL acceptance

## Context

Portfolio issue [#150](https://github.com/Young-Consultations/portfolio-tasks/issues/150)
reached the target adapter under the published 2.4.3 path. The router, Codex
authentication, result receiver, and source projection worked. The requested
documentation edit and draft PR did not appear.

## Discovery

The [REAL execute job](https://github.com/Young-Consultations/consulting-playbook/actions/runs/35742889348/job/106796923578)
recorded `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` when
Codex attempted to inspect the checkout. Codex exited zero despite reporting
it could not run commands. The adapter validated the untouched checkout,
returned `no-changes`, and left the workflow green.

The [July 25 successful run](https://github.com/Young-Consultations/consulting-playbook/actions/runs/30136047760)
and [draft PR #2](https://github.com/Young-Consultations/consulting-playbook/pull/2)
prove that Codex could execute and change this repository. The former
`openai/codex-action` prepared Linux user namespaces and AppArmor; the
August 14 replacement with a direct CLI adapter omitted that preparation.
Earlier flows rejected execution before a repository shell command could expose
the latent regression.

## Why it matters

A successful transport and green baseline repository tests can coexist with
failure to satisfy the approved issue. A zero process exit is insufficient
evidence that the model's tools ran or that a requested change was made.

## Related defect(s)

DEF-0043 (sandbox preparation) and DEF-0044 (empty implementation outcome).

## Evidence

- [Failed target run](https://github.com/Young-Consultations/consulting-playbook/actions/runs/35742889348/job/106796923578)
- [Source issue #150](https://github.com/Young-Consultations/portfolio-tasks/issues/150)
- [Previously working draft PR #2](https://github.com/Young-Consultations/consulting-playbook/pull/2)
- [Adapter replacement commit](https://github.com/Young-Consultations/consulting-playbook/commit/17be077f5889a2630b583a78d1f5d71e5556658c)

## What implementation or testing exposed

The adapter's only diff check occurred during publication, after validation.
It assigned an empty checkout a terminal `no-changes` outcome, so no draft PR
was created even though #150 explicitly required one.

## Requirement or architecture implications

Keep `workspace-write` and prepare the runner before credential handoff.
Require candidate changes for implement mode before validation; return a
canonical failure when absent and fail the execute job after emitting outputs.
The receiver still transports the failure. Use a new immutable patch release;
no existing published tag changes as part of this repair.

## Lessons learned

When replacing a packaged action, capture its environment prerequisites and
test actual tool execution. A preflight that only authenticates does not test
repository command execution.

## `AI_CONTEXT.md` impact

The resolved runner prerequisite and implement outcome rule are recorded there.

## Follow-up

Review the repair PR and its exact conformance checks. Merge and publish a new
adapter release, compose and publish the matching control-plane patch release,
run a protected shell/file operation probe plus deployed Runtime and REAL
preflights, then use a fresh delivery identity for the next REAL issue.

## Potential consulting or content value

Concrete example of a green workflow with evidence that does not establish
the approved outcome.
