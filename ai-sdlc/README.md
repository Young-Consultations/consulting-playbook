# AI-SDLC Learning and Consulting Evidence

This area is the authoritative repository location for organization-wide AI-SDLC learning and reusable consulting evidence. It preserves traceability from evidence to lessons without replacing the approved requirements, architecture, or decisions of any product.

## Artifact boundaries

| Artifact | Purpose | Use when |
| --- | --- | --- |
| [Defect Ledger](defects/README.md) | Structured quantitative source of truth for evidence-backed discrepancies | Intended and actual requirements, architecture, interfaces, configuration, workflows, tests, documentation, or implementation differ |
| [Engineering Journal](engineering-journal/README.md) | Narrative discoveries, reasoning, implementation feedback, and lessons | A discovery materially changes understanding or needs context beyond a ledger row |
| [Case studies](case-studies/README.md) | Curated, evidence-backed, usually resolved consulting examples | The outcome and evidence are mature enough for reuse |
| [Content](content/README.md) | Ideas, drafts, and published consulting posts | A lesson is being shaped for an audience |

An investigation that finds no discrepancy is not a defect. Small evidence-backed discrepancies do count. Not every discovery needs a defect, journal entry, case study, and post; create only the artifacts that add useful evidence or context.

## Learning lifecycle

```text
Implementation / Testing / Review
              ↓
          Discovery
              ↓
       Defect Ledger
              ↓
    Engineering Journal
              ↓
Requirements / Architecture reconciliation
              ↓
     AI_CONTEXT impact review
              ↓
        Implementation
```

The arrows show a common path, not mandatory bureaucracy. For example, a minor resolved defect may require only a ledger row, while a non-defect process insight may require only a journal entry.

## Authority and reconciliation

Authoritative product requirements, architecture, interfaces, and decisions remain in the approved documents of their owning repositories. Evidence found during implementation must be reconciled there by the proper authority; neither this learning system nor an implementation artifact silently changes product truth.

After reconciliation, review whether concise operational guidance in an affected repository's `AI_CONTEXT.md` must change. Unresolved speculation may be recorded and clearly labeled in the Engineering Journal, but must not be promoted to resolved repository context.

Consulting evidence may be derived from ledger records, journal entries, outcomes, and metrics. Case studies and posts interpret that evidence for reuse; they are never authoritative product requirements or architecture.
