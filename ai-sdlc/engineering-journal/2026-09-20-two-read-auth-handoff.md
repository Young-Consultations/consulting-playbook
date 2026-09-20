# 2026-09-20 — Codex startup needs two auth reads

- **Date:** 2026-09-20
- **Decision status:** candidate; protected provider probe pending after merge
- **Decision owner:** consulting-playbook target adapter maintainer
- **SDLC phase:** REAL target repair
- **Evidence:** [production probe 35488284499](https://github.com/Young-Consultations/consulting-playbook/actions/runs/35488284499)

The protected probe failed with `stage=probe; category=authentication`, matching
the provider 401 in portfolio issue #148. The pinned Codex 0.154.0 source
constructs an auth manager when loading cloud configuration and another when
starting the in-process execution server. The first read consumes the former
one-shot FIFO; the latter cannot find credentials, so the model request has no
bearer header.

The candidate serves each startup read from a separate FIFO inode, rotating
the pathname as soon as each reader attaches and before its writer closes. It deletes
the authentication path before submitting any model prompt, preserving the
credential boundary for model-launched commands. The fixed read-only probe
uses the same handoff, and offline tests require both reads before prompt
submission. The helper and adapter are bound to a new conformance revision.

The exact live startup sequence still needs verification in the protected
environment. Keep REAL delivery blocked until the repaired probe completes,
then publish a new immutable adapter tag and update the control-plane pin.
Do not retry the terminal delivery identity from issue #148.
