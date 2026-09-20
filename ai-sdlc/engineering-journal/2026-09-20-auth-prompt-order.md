# 2026-09-20 — Stdin prompt gates the second auth read

- **Date:** 2026-09-20
- **Decision status:** candidate; protected probe pending after merge
- **Decision owner:** consulting-playbook target adapter maintainer
- **SDLC phase:** REAL target repair
- **Evidence:** [protected probe 35516136826](https://github.com/Young-Consultations/consulting-playbook/actions/runs/35516136826)

The two-read FIFO repair in PR #58 passed offline conformance but the protected
probe timed out at `stage=auth-handoff`. The pinned Codex 0.154.0 `exec -`
implementation reads stdin to EOF before starting its in-process execution
server. The adapter withheld stdin until both auth reads completed, while the
server's second auth read could not begin until stdin closed.

The candidate serves the configuration read, closes stdin with the admitted
prompt, then serves the execution-server read. Each FIFO path is retired as
soon as its reader connects. The second path is removed before auth is
delivered to the server and before that server can run model tools. Offline
checks model this startup order and require the auth path to be absent before
execution; they cannot substitute for the protected provider request. Review
also identified a blocking stdin write for large prompts if Codex stopped
reading. The prompt now uses nonblocking pipe writes under the admitted
deadline; a stalled-child check proves the timeout and cleanup path.

Keep REAL delivery blocked until a protected probe succeeds. Then publish a
new immutable adapter tag and update the control-plane pin; the terminal
delivery identity from portfolio issue #148 must not be reused.
