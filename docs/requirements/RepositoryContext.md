# Repository Context

## Purpose

`Young-Consultations/consulting-playbook` is the authoritative home for reusable
consulting knowledge, assessment methods, decision frameworks, delivery
playbooks, templates, recommendation-to-action patterns, and their product
requirements. Its product purpose is independent of its current target-executor
implementation.

## Responsibilities

The repository owns the semantics, quality, lifecycle, and maintenance of:

- consulting principles and the shared engagement lifecycle;
- discovery, assessment, analysis, reporting, roadmap, handoff, and follow-up methods;
- reusable templates, checklists, patterns, and safe generalized lessons;
- evidence, confidence, limitation, decision, and traceability guidance;
- consulting-content confidentiality and AI-use guardrails; and
- repository-local validation and bounded execution policy for changes targeted
  to this repository.

## Boundaries

It does **not** own portfolio backlog/intake state, approval, priority, routing,
organization-wide schemas, repository registration, Slugger's product behavior,
client evidence systems, external implementation, merge decisions, releases, or
production authorization. Advice, roadmaps, task proposals, and AI output are
not authority.

## Ownership and decision rights

Repository maintainers own acceptance, versioning, and deprecation of reusable
content. Consulting leads own professional-method quality. Client/designated
authorities own engagement decisions. Evidence custodians own access and use
permissions. External repository owners own their contracts and behavior.
Reviewers may challenge any conclusion; contribution does not confer approval.

## Internal capabilities

The required product capabilities are defined by FR-ENG through FR-KM and
FR-SEC. FR-EXE defines a current enabling capability: receipt, verification,
safe execution, validation, deterministic draft publication, and canonical
result reporting for approved changes to this repository.

## Data ownership

The repository owns reusable, non-client-specific knowledge and its metadata.
It may own references and minimal trace metadata for engagement artifacts when
authorized, but it SHALL NOT be presumed to own or store raw client evidence,
personal data, external decisions, portfolio tasks, or target delivery evidence.
Copies do not transfer authority; the authoritative system and record owner must
be stated. Reusable lessons require generalization and confidentiality review.

## External dependencies and consumers

| Party | Dependency/consumption |
| --- | --- |
| Consultants and client teams | Consume methods and artifacts; supply context and validation. |
| `Young-Consultations/.github` | Supplies canonical AI-SDLC contracts, routing, registration, and verification. |
| `Young-Consultations/portfolio-tasks` | Owns governed task intake/approval and may consume approved handoff proposals. |
| `Young-Consultations/slugger` | May consume separately approved target work; no direct interface is confirmed. |
| GitHub | May host version history, review, issues, workflow evidence, and links. |
| AI agents | Consume bounded, classified, approved task/context packages and produce review-required output. |

## Repository lifecycle responsibilities

1. **Propose:** identify purpose, user need, evidence basis, owner, applicability,
   confidentiality, and affected requirements.
2. **Review:** obtain professional, technical, editorial, accessibility, and
   security/privacy review proportionate to risk.
3. **Approve/publish:** assign a version and current status without rewriting
   prior engagement meaning.
4. **Use/measure:** gather safe feedback and outcome evidence without importing
   confidential engagement data.
5. **Revise:** document rationale, compatibility, migrations, and trace updates.
6. **Deprecate/archive:** mark status, replacement, effective date, and impact;
   retain historical discoverability.
7. **Recover:** restore approved baselines from version history and reconcile
   any external references.

## Boundary validation rule

An architecture or feature proposal that makes this repository authoritative for
external approval, routing, target execution, or client evidence conflicts with
the vision unless the vision and all affected interface contracts are explicitly
re-baselined by their owners.
