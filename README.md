# consulting-playbook

`Young-Consultations/consulting-playbook` is a target executor repository for approved consulting-playbook implementation work.

## AI-SDLC control plane

The shared AI-SDLC execution control plane is owned by `Young-Consultations/.github`. That organization repository owns the canonical schemas, the `ai_sdlc_contracts` Python package, task and execution validation, contract versioning, repository registry, routing policy, shared failure categories, and correlation behavior.

`Young-Consultations/portfolio-tasks` owns portfolio backlog issues, structured intake and governance metadata, explicit human approval, and initiating the organization router. It does not own shared execution schemas or target execution-result contracts.

This repository consumes `ai-sdlc-contract/v2` as dispatched by the organization router to `.github/workflows/codex-execute.yml`. The workflow pins the organization control-plane checkout to immutable release `ai-sdlc-v2.1.0` and installs `ai_sdlc_contracts` from that checkout instead of copying schemas or implementing shared validators locally.

Upgrades to the organization control-plane release require an explicit reviewed repository change. Rollback must pin the workflow to the previous immutable known-good organization release.

## Target execution responsibilities

The consulting-playbook target workflow owns only repository-specific behavior:

- validating that the canonical input targets `Young-Consultations/consulting-playbook`;
- requiring the executor to be Codex;
- revalidating immediately before execution that the source is an open GitHub issue, remains explicitly approved, remains assigned to Codex, and is not marked sensitive;
- enforcing draft-only publication, no automatic merge, and no direct push to `main`;
- deriving deterministic implementation branches from canonical task identity;
- running repository validation and tests before publication;
- producing and uploading a canonical execution result through the organization package.

Verify mode is non-mutating: it validates the canonical contract, routing authorization, repository policy, and safe repository checks, but it does not invoke Codex, create a branch, commit, push, or create a pull request.

Implement mode may run Codex through the controlled wrapper and may create or update one deterministic draft pull request. Target execution can never merge automatically; human review and merge are always required.
