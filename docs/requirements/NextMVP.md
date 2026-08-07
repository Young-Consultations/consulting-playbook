# Consulting Playbook Next-MVP Profile

## Status, objective, and authority

This repository-level profile is the working interpretation of the expected
organization baseline at `Young-Consultations/.github/docs/releases/next-mvp.md`.
That external file and sibling repositories were not inspected; compatibility is
**not verified**. The organization baseline remains authoritative once confirmed.

The smallest meaningful contribution is an authorized target-adapter path from
one canonical routed request to one validated draft pull request (or its safe
reuse) and one correlated canonical result. It does not deliver the consulting
runtime or engagement roadmap and ends before review completion, merge, knowledge
publication, release, deployment, or production use.

## Included requirement IDs

The release profile includes only these existing baseline requirements:

| ID | MVP contribution |
| --- | --- |
| FR-EXE-01 | Canonical receipt; supported-version, target, stable approval evidence, routing admission, repository policy, executor, sensitivity, and mode validation; bounded verify/implement authorization. |
| FR-EXE-02 | At-least-once-safe execution; repository/content validation; no-change handling; exactly one draft or reuse; canonical correlated result and reconciliation. |
| FR-SEC-01, FR-SEC-02 | Minimum necessary, non-sensitive executable context and controlled AI transfer. |
| NFR-SEC-02, NFR-SEC-03 | Secret exclusion and least-privilege execution/publication credentials. |
| NFR-REL-02, NFR-REC-02 | Idempotent visible effects and reconciliation-first recovery. |
| NFR-OBS-01, NFR-OBS-02 | Correlated, safe, terminal result evidence. |
| NFR-CFG-02, NFR-INT-01 | Fail-closed versioning and interoperable ownership/correlation metadata. |
| NFR-TST-01, NFR-TST-02 | Traceable positive/negative coverage and deterministic no-write CI. |
| NFR-AUTO-01, NFR-AUTO-02, NFR-AI-01 | Deterministic records, explicit authority, and bounded self-contained work. |

All other functional requirement IDs are deferred: `FR-ENG-01–03`,
`FR-EVD-01–04`, `FR-ASMT-01–03`, `FR-ANL-01–03`, `FR-REC-01`,
`FR-DEC-01`, `FR-ROAD-01`, `FR-RPT-01`, `FR-HO-01`, `FR-FU-01`, and
`FR-KM-01–02`. They cover the broader consulting runtime, engagement workflow,
analytics/assessment, collaboration, hosted records, client/portfolio integration,
reporting, follow-up, and knowledge operations. Nonfunctional requirements not
listed above are likewise not release gates for this adapter slice; they remain
baseline requirements for their applicable future capabilities.

## End-to-end acceptance boundary

An eligible portfolio task is approved by an authorized human, admitted by the
organization control plane, and delivered at least once to this target. The target:

1. validates the canonical request and supported immutable release unit;
2. validates stable approval evidence and repository-local authorization;
3. in implement mode invokes a bounded Codex port only after all gates pass;
4. validates the candidate against repository and consulting-content policy;
5. creates or reuses exactly one managed draft PR for the delivery identity; and
6. returns or durably exposes one canonical correlated result through the approved
   transport. Verify mode skips Codex and publication. No-change is a terminal
   canonical outcome with no branch or PR side effect.

Material source edits, revocation, withdrawal, stale proof, invalid authority,
target mismatch, unsupported contract, policy denial, or ambiguous publication
state fail closed. Processing is at-least-once-safe: retry uses the same delivery
identity, reconciles before mutation, and has idempotent visible effects.

## Ordinary-CI conformance acceptance criteria

Ordinary CI MUST use deterministic consumer-driven fixtures and fakes. It MUST:

- prove a valid request reaches a fake executor while requiring no Codex credential,
  making no Codex network call, and creating no real branch or pull request;
- deterministically assert expected simulated consulting-document changes or
  declared no-change/execution outcomes;
- exercise repository/content validation and assert simulated draft-PR metadata;
- redeliver the same identity and prove reuse of the same simulated draft and no
  second result state transition;
- reject unsupported versions and malformed, unapproved, stale, withdrawn,
  revoked, materially changed, or wrong-target requests before execution;
- produce canonical contract, authorization, repository-policy, validation,
  execution, publication, and interrupted/ambiguous failure outcomes with safe
  evidence and reconciliation guidance; and
- validate against the organization-owned shared conformance fixtures, with fixture
  drift or incompatible public API blocking merge.

A separately authorized, credentialed real-Codex integration test MAY exist behind
manual/environment controls. It is not an ordinary-CI or MVP acceptance dependency
and may not merge, release, deploy, or publish consulting guidance automatically.

## External confirmation gates

Before enablement, organization owners MUST confirm together as one compatible,
immutable release unit: the contract/package release, its documented public API,
schema and workflow interface, approval-proof and revocation semantics, canonical
result-return transport, shared fixture location/version, registry enablement for
this target, and canonical lifecycle vocabulary. The adapter MUST NOT import
internal or merely observed package paths/modules, copy an external schema, or
guess a missing API. Until those facts are confirmed by provider documentation
and consumer-driven fixtures, registry enablement and live execution are blocked.
