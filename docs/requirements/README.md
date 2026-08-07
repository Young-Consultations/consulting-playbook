# Consulting Playbook Requirements Baseline

This directory is the authoritative product-requirements baseline for
`Young-Consultations/consulting-playbook`. It specifies the intended consulting
operating system independently of the current implementation.

## Authority and interpretation

1. [`../VISION.md`](../VISION.md) is the controlling product vision. If this
   baseline conflicts with that vision, the vision takes precedence.
2. Approved changes to this baseline govern subsequent architecture, design,
   implementation, testing, and automation work.
3. Existing code is evidence of current capabilities, not normative product
   behavior. Requirements explicitly identified as current target-execution
   obligations remain normative until retired through governance.
4. “Consulting playbook” is the product name used here. References in the task
   request to “counseling playbook,” `portfolio-tasks` as the product, or access
   only to another repository are treated as inconsistent with the inspected
   repository and its controlling vision.

## Document set

- [Next-MVP profile](NextMVP.md) — narrow release scope, acceptance boundary,
  deferrals, no-Codex conformance, and external confirmation gates.

| Document | Purpose |
| --- | --- |
| [ProjectRequirements.md](ProjectRequirements.md) | Product purpose, scope, outcomes, stakeholders, and constraints |
| [SoftwareRequirementsSpecification.md](SoftwareRequirementsSpecification.md) | Consolidated software requirements specification |
| [FunctionalRequirements.md](FunctionalRequirements.md) | Atomic capability requirements and acceptance criteria |
| [NonFunctionalRequirements.md](NonFunctionalRequirements.md) | Measurable quality requirements |
| [RepositoryContext.md](RepositoryContext.md) | Repository ownership, boundaries, and lifecycle |
| [Interface-Organization-Control-Plane.md](Interface-Organization-Control-Plane.md) | Required contract with `Young-Consultations/.github` |
| [Interface-Portfolio-Tasks.md](Interface-Portfolio-Tasks.md) | Recommendation and execution relationship with `portfolio-tasks` |
| [Interface-Slugger.md](Interface-Slugger.md) | Boundary and potential handoff contract with `slugger` |
| [UseCases.md](UseCases.md) | Actor-oriented success and failure flows |
| [UserStories.md](UserStories.md) | Prioritized user outcomes |
| [BusinessRules.md](BusinessRules.md) | Governing policies and lifecycle rules |
| [Glossary.md](Glossary.md) | Authoritative terminology |
| [Assumptions.md](Assumptions.md) | Confirmed facts, working assumptions, unknowns, and questions |
| [RequirementsTraceability.md](RequirementsTraceability.md) | Vision-to-verification traceability |

## Requirement language and status

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are used as
described by RFC 2119. `MUST` and `SHALL` are equivalent mandatory terms.

Priorities are **P0** (safety, governance, or baseline-essential), **P1** (core
product value), **P2** (important extension), and **P3** (future candidate).
Open questions do not weaken a mandatory requirement unless that requirement
explicitly names the question as a prerequisite for baselining its criterion.

## Change control

Every requirements change MUST identify affected requirement IDs, rationale,
approver, compatibility impact, and traceability updates. Silent semantic
changes are prohibited. Superseded requirements remain discoverable through
version history.
