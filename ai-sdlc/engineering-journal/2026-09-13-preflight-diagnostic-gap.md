# 2026-09-13 — Preflight failure diagnostics need executable evidence

- **Decision status:** implementation repair proposed; live provider cause unresolved
- **Related defect:** DEF-0035

The [first preflight run](https://github.com/Young-Consultations/consulting-playbook/actions/runs/33905749608/job/101130151840)
failed with `codex-runtime`. Login and probe shared one log and one exit-code
variable; only a generic category survived cleanup. It was impossible to tell
which command failed. This evidence does not establish that the key is invalid.

The repair preserves stage and original exit code in the Actions summary and
adds fixed CLI/configuration, sandbox, filesystem and service hints. Login
success is labeled credential storage, not provider authentication. Raw output
is still withheld and cleaned up; no provider text is copied into annotations.

Sixteen offline cases execute the actual workflow shell with a fake Codex
binary, including failures at both stages, unknown errors, diagnostic isolation,
secret-bearing output and forged Actions commands. They verify that login
failure skips the probe, the key is absent from the probe environment, failure
codes survive, and temporary auth/log files are removed.

This implements existing NFR-OBS-01/02, NFR-SEC-02 and NFR-TST-02; no contract,
architecture, credential, model, client-version or activation change is made.
AI_CONTEXT requires no policy update. The original provider failure remains
unresolved until a new controlled run produces useful evidence. Static keyword
checks alone were insufficient to establish diagnostic behavior.
