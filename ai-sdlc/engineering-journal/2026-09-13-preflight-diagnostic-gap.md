# 2026-09-13 — Preflight failure diagnostics need executable evidence

- **Date:** 2026-09-13
- **Decision status:** unresolved; implementation repair proposed, live provider cause unknown
- **SDLC phase:** release-production

## Context

The manual preflight separates credential readiness from governed task delivery.

## Discovery

The [first preflight run](https://github.com/Young-Consultations/consulting-playbook/actions/runs/33905749608/job/101130151840)
failed with `codex-runtime`. Login and probe shared one log and one exit-code
variable; only a generic category survived cleanup. It was impossible to tell
which command failed. This evidence does not establish that the key is invalid.

## Why it matters

An unclassified failure without stage or exit-code evidence cannot guide recovery.

## Related defect(s)

DEF-0035 tracks the diagnostic gap; DEF-0034 tracks live readiness coverage.

## Evidence

The failed run linked above and [repair PR #48](https://github.com/Young-Consultations/consulting-playbook/pull/48)
preserve the observation, proposed change and review findings.

## What implementation or testing exposed

The repair preserves stage and original exit code in the Actions summary and
adds fixed CLI/configuration, sandbox, filesystem and service hints. Login
success is labeled credential storage, not provider authentication. Raw output
is still withheld and cleaned up; no provider text is copied into annotations.

Eighteen offline cases execute the actual workflow shell with a fake Codex
binary, including failures at both stages, unknown errors, diagnostic isolation,
secret-bearing output and forged Actions commands. They verify that login
failure skips the probe, the key is absent from the probe environment, failure
codes survive, and temporary auth/log files are removed. Review added coverage
for both output streams, run identity in every report, the pinned client label,
the intermediate credential-stored report, and permission-denied code variants.

## Requirement or architecture implications

This implements existing NFR-OBS-01/02, NFR-SEC-02 and NFR-TST-02; no contract,
architecture, credential, model, client-version or activation change is made.

## Lessons learned

Static keyword checks alone were insufficient to establish diagnostic behavior.
Executable tests must cover stderr as well as stdout and assert the evidence
operators need, including correlation and the distinction between stages.

## `AI_CONTEXT.md` impact

No policy update is required; this repair implements existing observability,
secret-handling and testing requirements.

## Controlled run after PR #48

PR #48 merged at `d18eaf576a4afc96cad560b5ecfcab37b0f26b22`.
[Run 34732628071](https://github.com/Young-Consultations/consulting-playbook/actions/runs/34732628071/job/103658119611)
confirmed login exit 0 and probe exit 1, reported as `sandbox`. The classifier
matched the normal `sandbox: read-only` banner before provider errors. Offline
reproduction classified a banner followed by 401, 429 or 503 as sandbox. This
is a confirmed diagnostic defect (DEF-0036), not evidence of a sandbox root cause.
The discarded provider output prevents establishing the live underlying error.

The follow-up repair requires failure context on the same line as a sandbox
mechanism. All probe fixtures now include a representative pinned-client header;
22 executable scenarios cover provider errors, genuine sandbox failures, benign
mechanism mentions, unknown errors, secret suppression and cleanup. The new
header fixture fails against the old classifier at the authentication case.
These are offline regression results, not live credential readiness evidence.

## Follow-up

The repository maintainer should review and merge the repair, then start a new
controlled preflight run on main. The original provider failure remains
unresolved until that run produces useful evidence.

## Potential consulting or content value

Failure diagnostics need acceptance tests of their own. Safe suppression of raw
output is useful only when sufficient attributable evidence survives.

## 2026-09-14 addendum — settings eliminated, stale client/model route isolated

PR #49 merged the startup-banner classifier repair. Controlled runs
[34762039726](https://github.com/Young-Consultations/consulting-playbook/actions/runs/34762039726/job/103736460491),
[34849176824](https://github.com/Young-Consultations/consulting-playbook/actions/runs/34849176824/job/103997987244),
and [34893752679](https://github.com/Young-Consultations/consulting-playbook/actions/runs/34893752679/job/104142492405)
then consistently reported login exit 0 followed by probe exit 1 as
`authorization-or-model-access`.

Before the last run, the operator replaced the environment secret in
`consulting-playbook-codex`, removed the project model allowlist, and verified
active billing credit, a nonzero organization spend limit, unrestricted key
permissions, and no IP allowlist. The final run still failed in the same stage
and category. Those observations eliminate the visible account and GitHub
environment settings as the differentiator.

The workflow still installed Codex CLI `0.63.0` and did not select a model.
That client's representative startup metadata identifies `gpt-5-codex`; the
current OpenAI model catalog marks that model deprecated and identifies
`gpt-5.3-codex` as the default Codex model. Because raw provider output remains
intentionally withheld, the old default cannot be proven as the exact provider
message. It is nevertheless a confirmed configuration defect: production and
preflight delegated a release-critical model choice to a stale client default.

The repair pins Codex CLI `0.154.0` and `gpt-5.3-codex` in both preflight and
target execution, reports both identities in preflight evidence, updates the
target conformance binding, and regenerates the complete no-real-effects report.
DEF-0037 tracks this defect. It remains open until the change is merged and a
controlled preflight succeeds.
