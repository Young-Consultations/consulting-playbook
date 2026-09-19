# 2026-09-19 — REAL execution lost provider authentication

Portfolio issue [#148](https://github.com/Young-Consultations/portfolio-tasks/issues/148)
was admitted through `ai-sdlc-v2.4.2`, dispatched to the immutable
`codex-adapter-v2.4.2` target, and returned a receiver-validated terminal
`codex-runtime` failure. [Target run 35474192806](https://github.com/Young-Consultations/consulting-playbook/actions/runs/35474192806)
shows `codex exec` receiving repeated 401 responses with a missing bearer/basic
authentication header. Validation did not run; no branch or draft PR was made.

The existing authentication preflight keeps `auth.json` in its isolated
`CODEX_HOME` until its provider probe completes. The production adapter instead
serves `auth.json` through a one-read FIFO, unlinking it before it supplies the
task prompt. Its offline test simulates a single read. The run proves that
production execution lacked an authenticated provider request; it does not yet
prove whether Codex reloads the file after startup or another behavior loses
the credential.

The manual **Codex production auth probe** checks that specific handoff inside
the protected target environment using the pinned client and model. It reads
the target checkout for the probe script but has no publication or result
credential, uses a fixed prompt with the read-only sandbox, suppresses provider
output, and publishes only a bounded pass/fail category. Run it from `main`
after review and merge. A failure blocks another REAL task and informs a
separate adapter correction with new immutable adapter evidence and release
registration. The failed delivery identity from #148 must not be reused.
