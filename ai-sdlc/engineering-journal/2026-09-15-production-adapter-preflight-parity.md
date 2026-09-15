# Production adapter did not reproduce the verified authentication boundary

## Observation

Controlled preflight run 34929448831 proved that Codex CLI 0.154.0 could log in
from the protected `consulting-playbook-codex` environment and complete a
read-only `gpt-5.3-codex` request. That run did not exercise repository
modification or draft-PR publication.

Review of the production adapter found that it used the same environment,
client, and model, but did not use the same authentication boundary. It passed
`OPENAI_API_KEY` into the `codex exec` environment, inherited ambient `CODEX_*`
configuration, and did not establish fresh login state. It also allowed Codex
to run before confirming that the publication identity had repository write
access.

## Decision

Production execution now authenticates with `codex login --with-api-key` over
standard input into a temporary `CODEX_HOME`. The executor receives that login
state but not the raw API key or ambient Codex configuration. Login and execution
both run from the target repository root; execution retains the required
`workspace-write` sandbox and the pinned `gpt-5.3-codex` model.

Before login, the adapter uses the separate publication credential to confirm
that its GitHub identity has write access to the target repository. This check
cannot prove pull-request write scope without performing a publication effect,
so successful draft creation remains the final evidence for that permission.

## Evidence and remaining gate

Executable tests cover the successful login/execution sequence, raw-key
exclusion, temporary-state cleanup, exact working directory, client/model and
sandbox arguments, denied repository write access, and failed login. The
canonical 29-scenario conformance report was regenerated with all prohibited
effects at zero.

This repair establishes production/preflight parity but is not live
implementation or publication evidence. Keep DEF-0038 open until a fresh
governed delivery creates a tested draft pull request and its terminal result is
accepted by the result receiver.
