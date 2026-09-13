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

## Follow-up

The repository maintainer should review and merge the repair, then start a new
controlled preflight run on main. The original provider failure remains
unresolved until that run produces useful evidence.

## Potential consulting or content value

Failure diagnostics need acceptance tests of their own. Safe suppression of raw
output is useful only when sufficient attributable evidence survives.
