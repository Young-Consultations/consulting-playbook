# 2026-09-21 — Probe cleanup raced with Codex plugin writes

- **Date:** 2026-09-21
- **Decision status:** candidate; protected provider result pending
- **Decision owner:** consulting-playbook target adapter maintainer
- **SDLC phase:** REAL target verification
- **Evidence:** [protected probe 35537515777](https://github.com/Young-Consultations/consulting-playbook/actions/runs/35537515777)

The probe of merged PR #59 ran for about four seconds and then raised an
unhandled `Directory not empty: 'plugins'` error while deleting its isolated
Codex home, consistent with a concurrent plugin-cache write. The traceback
masks the provider result. It neither proves nor
disproves that the API request authenticated.

Both the protected probe and production adapter now retry ephemeral-home
removal for three seconds when a concurrent writer causes `ENOTEMPTY`.
Persistent cleanup failures remain failures; the probe reports only
`stage=cleanup; category=filesystem`. The auth FIFO is removed when its
reader attaches, before model tools can run. Offline checks exercise the
cleanup race and bounded classification.

Require a protected provider-response pass before publishing a new immutable
adapter tag or repinning the control plane. Do not reuse the terminal
delivery identity from portfolio issue #148.
