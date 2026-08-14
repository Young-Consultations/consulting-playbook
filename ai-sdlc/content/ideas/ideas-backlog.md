# Canonical Consulting Content Inventory

This file is the **single canonical inventory** for consulting posts, derivatives,
and post ideas. The draft and published directories hold content files; they do
not establish status. Update status here whenever an item moves through the
lifecycle.

## Lifecycle and maintenance

`idea` → `developing` → `draft` → `ready-to-publish` → `published`

Use `retired` when an item is intentionally withdrawn. A `draft` has repository
content at `draft_path`; `ready-to-publish` additionally has completed human
content review. `published` requires independently verifiable public evidence,
a URL, date when known, and channel. Never infer publication from a draft or
planned channel. Use `—` for unknown or not-yet-applicable values.

The inventory records content development, not publication authority. Every
claim and reusable example still requires evidence, confidentiality screening,
and human review. Internal evidence links are research traceability, not consent
to reproduce their contents publicly. Slugger remains evidence owned by its
product repository; this inventory does not define Slugger architecture.

After publication, engagement measures may be added under `notes` or in a linked
research note: views, attributed subscribers, LinkedIn impressions, comments,
meaningful conversations, consulting leads, consultation calls, and client
opportunities. Record the measurement period and source; never estimate missing
historical values.

## Series

### Building an AI-Native SDLC in Public

An evidence-driven series about controls and lessons discovered while building
and auditing real AI-assisted delivery workflows. Entries must distinguish a
validated defect from a general lesson, link internal evidence where available,
and publish only generalized, non-sensitive facts. This is a series concept, not
a claim that its entries have been drafted or published.

## Inventory

### CONTENT-001 — The Code Fallacy: Why AI Tools Aren't Making Your Engineering Team Any Faster

- **status:** `published`
- **content_type:** long-form post
- **primary_channel:** Substack
- **theme:** engineering leadership; AI-SDLC; engineering productivity
- **series:** —
- **summary_or_thesis:** AI coding tools accelerate code generation without necessarily increasing engineering-system throughput. As generation becomes cheaper, constraints move into requirements, architecture, validation, integration, security, testing, decisions, and release.
- **source_or_evidence:** [Retrospective defect-ledger seed](../../engineering-journal/2026-08-12-retrospective-defect-ledger-seed.md); [PR #39 CI-hardening journal](../../engineering-journal/2026-07-28-pr39-ci-hardening.md); [Defect Ledger](../../defects/defect-ledger.csv)
- **related_project:** consulting-playbook; portfolio-tasks evidence referenced by the journal
- **published_date:** 2026-08-10
- **published_url:** https://mightyjoe909.substack.com/p/the-code-fallacy-why-ai-tools-arent?r=8w0hfw&utm_medium=ios
- **draft_path:** —
- **supporting_assets:** Planned diagram: “Traditional bottleneck → writing code” contrasted with “AI-native bottlenecks → upstream and downstream work”; no repository asset exists yet.
- **derivative_content:** `CONTENT-003`
- **notes:** Flagship consulting thought leadership and first Substack post. Publication date and public URL were provided by the author on 2026-08-13; no repository-local Markdown copy exists yet.

### CONTENT-002 — Why I'm Starting a Software Engineering Consulting Practice

- **status:** `developing`
- **content_type:** LinkedIn-oriented post
- **primary_channel:** LinkedIn (intended)
- **theme:** consulting-practice positioning; engineering leadership; AI-assisted delivery
- **series:** —
- **summary_or_thesis:** Explain the motivation for a consulting practice that improves software engineering systems, delivery effectiveness, SDLC discipline, and practical AI adoption.
- **source_or_evidence:** [Consulting operating system](../../../consulting/README.md); [Consulting Playbook Vision](../../../docs/VISION.md)
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** —
- **derivative_content:** Potential future service-positioning excerpts; none recorded.
- **notes:** Previously developed concept, but no full repository draft or verifiable publication record was found; publication status needs human verification.

### CONTENT-003 — AI Does Not Automatically Increase Throughput

- **status:** `developing`
- **content_type:** short-form derivative
- **primary_channel:** LinkedIn/social (intended)
- **theme:** AI-SDLC; engineering productivity
- **series:** —
- **summary_or_thesis:** Faster code generation does not improve throughput when the surrounding engineering system remains constrained.
- **source_or_evidence:** Parent post concept `CONTENT-001`; [PR #39 CI-hardening journal](../../engineering-journal/2026-07-28-pr39-ci-hardening.md)
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Reuse the planned bottleneck diagram from `CONTENT-001` if produced.
- **derivative_content:** Derivative of `CONTENT-001`, not a separate long-form post.
- **notes:** Keep scoped as short-form educational material to avoid duplicating The Code Fallacy.

### CONTENT-004 — What an Idea-to-App Product Should Produce

- **status:** `developing`
- **content_type:** educational concept
- **primary_channel:** —
- **theme:** AI-native software development; trustworthy software generation
- **series:** —
- **summary_or_thesis:** An idea-to-app system should produce not only code, but requirements, acceptance criteria, architecture, interfaces, tests, CI evidence, assumptions, limitations, traceability, and follow-up work needed to understand and trust the system.
- **source_or_evidence:** [Slugger internal case-study outline](../../../consulting/10-case-studies/slugger-internal-case-study-outline.md); [repository boundary policy](../../../AI_CONTEXT.md)
- **related_project:** Slugger (evidence/case-study context only)
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Slugger case-study outline; future generalized artifact map.
- **derivative_content:** Potential checklist or carousel; none recorded.
- **notes:** Consulting-playbook does not own or define Slugger product architecture. No full repository draft or publication evidence was found.

### CONTENT-005 — Five Signs Your Backlog Is Reducing Team Velocity

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** backlog health; engineering productivity
- **series:** —
- **summary_or_thesis:** Explore observable ways backlog quality can create delay, churn, and avoidable delivery work.
- **source_or_evidence:** [Backlog health checklist](../../../consulting/04-assessment-checklist/backlog-health-checklist.md)
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Backlog health checklist.
- **derivative_content:** —
- **notes:** Validate the five signs against evidence before drafting.

### CONTENT-006 — Why Adding Developers Does Not Automatically Increase Delivery

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** delivery systems; engineering leadership
- **series:** —
- **summary_or_thesis:** Examine why capacity additions do not remove systemic constraints and may increase coordination load.
- **source_or_evidence:** Deliberate proposal in the content brief; evidence research required.
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** —
- **derivative_content:** —
- **notes:** Distinct from `CONTENT-001`: focus on staffing and system constraints rather than AI code generation.

### CONTENT-007 — How to Explain Technical Debt in Customer Language

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** technical-to-customer communication; technical debt
- **series:** —
- **summary_or_thesis:** Translate technical debt into customer outcomes, risk, delay, and option value without obscuring engineering reality.
- **source_or_evidence:** [Consulting assessment scope](../../../consulting/README.md)
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** —
- **derivative_content:** —
- **notes:** Evidence research required.

### CONTENT-008 — How to Connect Sprint Priorities to Customer Outcomes

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** prioritization; customer value
- **series:** —
- **summary_or_thesis:** Show how teams can trace sprint choices to explicit customer and business outcomes.
- **source_or_evidence:** [Consulting operating principles](../../../consulting/README.md)
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** —
- **derivative_content:** —
- **notes:** Evidence research required.

### CONTENT-009 — Stop Prompting AI to Code: Use This 5-Step Engineering Pipeline Instead

- **status:** `published`
- **content_type:** long-form post
- **primary_channel:** Substack
- **theme:** AI-SDLC controls and lifecycle; engineering leadership; traceability
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** The quality of AI-assisted software is largely determined before the coding prompt. Use a five-stage pipeline—Vision → Requirements → Architecture → Context → Verification—with traceability across stages so that changes and discoveries can be reconciled through the system. AI does not make the SDLC obsolete; it makes the SDLC more important, and skipping steps more expensive.
- **source_or_evidence:** `CONTENT-001`; [immutable-baseline activation-blocker journal](../../engineering-journal/2026-08-13-immutable-baseline-activation-blocker.md); related `DEF-0012`–`DEF-0019` in the [Defect Ledger](../../defects/defect-ledger.csv)
- **related_project:** consulting-playbook; cross-repository evidence referenced by the engineering journal
- **published_date:** 2026-08-14
- **published_url:** https://mightyjoe909.substack.com/p/stop-prompting-ai-to-code-use-this?r=8w0hfw&utm_medium=ios
- **draft_path:** —
- **supporting_assets:** Five-stage sequence in the post; no repository-local visual exists yet.
- **derivative_content:** Potential five-stage checklist or diagram; none recorded.
- **notes:** Second Substack post and part of the foundational publication sequence. It evolved from the original “What an AI-Assisted SDLC Needs Beyond a Coding Agent” idea. The author provided the publication date and public URL on 2026-08-14; no repository-local Markdown copy exists yet. Defect and rework measurement is introduced only as a bridge to later evidence-driven content rather than developed as a tangent here.

### CONTENT-010 — What an AI-SDLC Readiness Assessment Should Examine

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** AI-SDLC readiness; assessment
- **series:** —
- **summary_or_thesis:** Outline evidence areas leaders should examine before treating AI-assisted delivery as a dependable capability.
- **source_or_evidence:** [AI-SDLC readiness checklist](../../../consulting/04-assessment-checklist/ai-sdlc-readiness-checklist.md)
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** AI-SDLC readiness checklist.
- **derivative_content:** Potential assessment teaser or checklist excerpt; none recorded.
- **notes:** Do not imply that checklist completion proves readiness.

### CONTENT-011 — How Engineering Leaders Should Evaluate AI-Assisted Development

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** engineering leadership; AI evaluation
- **series:** —
- **summary_or_thesis:** Frame evaluation around system outcomes, evidence, risk, and learning rather than generated-code volume.
- **source_or_evidence:** [AI-SDLC readiness checklist](../../../consulting/04-assessment-checklist/ai-sdlc-readiness-checklist.md)
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** AI-SDLC readiness checklist.
- **derivative_content:** —
- **notes:** Evidence research required.

### CONTENT-012 — Slugger: Lessons Learned / Case Study

- **status:** `idea`
- **content_type:** case-study post idea
- **primary_channel:** —
- **theme:** AI-native product experimentation; lessons learned
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** Generalize validated lessons from Slugger experiments while distinguishing completed outcomes from expected outcomes.
- **source_or_evidence:** [Slugger internal case-study outline](../../../consulting/10-case-studies/slugger-internal-case-study-outline.md)
- **related_project:** Slugger (evidence only)
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Slugger internal case-study outline.
- **derivative_content:** —
- **notes:** Requires evidence maturation, confidentiality review, and validation by the owning product repository.

### CONTENT-013 — Velocity vs. Throughput

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** engineering productivity; flow metrics
- **series:** —
- **summary_or_thesis:** Clarify what velocity and throughput measure, where each can mislead, and how to discuss them in context.
- **source_or_evidence:** [Definitions and glossary](../../../consulting/11-knowledge-base/definitions-and-glossary.md)
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Definitions and glossary.
- **derivative_content:** —
- **notes:** Conceptually related to `CONTENT-001`, but independently focused on measurement vocabulary.

### CONTENT-014 — Quality Gates in AI-Assisted Development

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** verification; AI-SDLC
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** Explain why deterministic quality gates become more important as implementation accelerates.
- **source_or_evidence:** [PR #39 CI-hardening journal](../../engineering-journal/2026-07-28-pr39-ci-hardening.md); related `DEF-0008`–`DEF-0010` in the [Defect Ledger](../../defects/defect-ledger.csv)
- **related_project:** portfolio-tasks evidence; consulting-playbook learning system
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** CI-hardening journal and defect records.
- **derivative_content:** —
- **notes:** Generalize public evidence; do not reproduce private CI or review content.

### CONTENT-015 — Prompt Assets Should Be Versioned Engineering Artifacts

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** prompt engineering; configuration management
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** Treat durable prompts and agent instructions as reviewable, versioned engineering inputs rather than transient chat text.
- **source_or_evidence:** [Reusable prompts guidance](../../../consulting/11-knowledge-base/reusable-prompts.md); [AI context policy](../../../AI_CONTEXT.md)
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Repository-local prompt and context artifacts.
- **derivative_content:** —
- **notes:** Evidence research required before making outcome claims.

### CONTENT-016 — Context Engineering as an Engineering Discipline

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** context engineering; AI-SDLC
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** Explore how authority ordering, boundaries, traceability, and maintained repository context reduce agent drift.
- **source_or_evidence:** [AI context policy](../../../AI_CONTEXT.md); [architecture traceability](../../../docs/architecture/ArchitectureTraceability.md)
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** AI_CONTEXT.md and architecture traceability.
- **derivative_content:** —
- **notes:** Broader discipline-level treatment; `CONTENT-024` is the repository-specific story.

### CONTENT-017 — What Codex/GitHub Workflows Teach Us About AI-Native Development

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** AI-native workflows; delivery governance
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** Extract general lessons about bounded automation, review, reproducibility, and evidence from controlled Codex/GitHub workflows.
- **source_or_evidence:** [Next-MVP workflow profile](../../../docs/requirements/NextMVP.md); [PR #39 CI-hardening journal](../../engineering-journal/2026-07-28-pr39-ci-hardening.md)
- **related_project:** consulting-playbook; portfolio-tasks evidence
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Workflow requirements and engineering journal.
- **derivative_content:** —
- **notes:** Avoid claims about external implementation beyond repository evidence.

### CONTENT-018 — Failures and Lessons from Building an AI-SDLC

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** AI-SDLC retrospectives
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** Synthesize validated workflow failures into process-design lessons without treating isolated incidents as universal proof.
- **source_or_evidence:** [Retrospective defect-ledger seed](../../engineering-journal/2026-08-12-retrospective-defect-ledger-seed.md); [Defect Ledger](../../defects/defect-ledger.csv)
- **related_project:** consulting-playbook; portfolio-tasks evidence
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Retrospective journal and defect records.
- **derivative_content:** Potential umbrella/series recap; none recorded.
- **notes:** Consolidates the broad failures theme; individual evidence-led angles remain separate entries below.

### CONTENT-019 — Before/After: Traditional vs. AI-Native GitHub Workflows

- **status:** `idea`
- **content_type:** comparison post idea
- **primary_channel:** —
- **theme:** AI-native workflows; process design
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** Compare workflow stages and controls before and after adding bounded AI assistance, without claiming that “AI-native” alone proves improvement.
- **source_or_evidence:** [Next-MVP workflow profile](../../../docs/requirements/NextMVP.md); evidence research required for any before/after outcome claim.
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Potential future workflow comparison diagram; no asset exists yet.
- **derivative_content:** Potential carousel or diagram; none recorded.
- **notes:** Establish a comparable baseline before drafting.

### CONTENT-020 — AI-SDLC Is Earned Through Validation

- **status:** `idea`
- **content_type:** backlog post idea
- **primary_channel:** —
- **theme:** validation; AI-SDLC maturity
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** Dependability comes from reproducible validation and reconciled evidence, not from successful code generation alone.
- **source_or_evidence:** [PR #39 CI-hardening journal](../../engineering-journal/2026-07-28-pr39-ci-hardening.md)
- **related_project:** consulting-playbook; portfolio-tasks evidence
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** CI-hardening journal.
- **derivative_content:** Potential short-form thesis; none recorded.
- **notes:** Keep distinct from `CONTENT-014`: this is a maturity argument, while that entry focuses on specific gate design.

### CONTENT-021 — AI Writes Code Faster. It Also Creates Defects Faster.

- **status:** `idea`
- **content_type:** evidence-driven backlog post idea
- **primary_channel:** —
- **theme:** implementation velocity; defect discovery; validation
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** Increased implementation speed can also accelerate defect creation, making validation, traceability, and defect capture more important.
- **source_or_evidence:** [PR #39 CI-hardening journal](../../engineering-journal/2026-07-28-pr39-ci-hardening.md); related `DEF-0008`–`DEF-0010` in the [Defect Ledger](../../defects/defect-ledger.csv)
- **related_project:** portfolio-tasks evidence; consulting-playbook learning system
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** CI failure narrative and defect records.
- **derivative_content:** Could derive a defect-amplification graphic after evidence review.
- **notes:** New idea derived from project evidence, not a previously written post. The title is a hypothesis to support carefully, not a measured defect-rate claim.

### CONTENT-022 — Your AI Coding Agent Needs an Engineering Journal

- **status:** `idea`
- **content_type:** evidence-driven backlog post idea
- **primary_channel:** —
- **theme:** engineering knowledge management; AI-SDLC
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** Durable journal entries retain decisions, surprises, defects, and implementation discoveries that would otherwise disappear with transient chat context.
- **source_or_evidence:** [Engineering Journal guidance](../../engineering-journal/README.md); [retrospective journal](../../engineering-journal/2026-08-12-retrospective-defect-ledger-seed.md)
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Engineering Journal template and example entries.
- **derivative_content:** Potential journal-entry checklist; none recorded.
- **notes:** New idea derived from project evidence, not a previously written post.

### CONTENT-023 — Why AI_CONTEXT.md Became Part of My SDLC

- **status:** `idea`
- **content_type:** evidence-driven backlog post idea
- **primary_channel:** —
- **theme:** repository-local context; AI governance
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** Repository-local context can operate as an engineering control by ordering authority, preserving boundaries, and reducing drift across AI-assisted changes.
- **source_or_evidence:** [AI context policy](../../../AI_CONTEXT.md); `DEF-0011` and the [retrospective journal](../../engineering-journal/2026-08-12-retrospective-defect-ledger-seed.md)
- **related_project:** consulting-playbook
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** AI_CONTEXT.md and its documented reconciliation example.
- **derivative_content:** —
- **notes:** New idea derived from project evidence, not a previously written post. Distinct from the broader discipline framing in `CONTENT-016`.

### CONTENT-024 — I Asked AI to Audit Its Own Software Development Process

- **status:** `idea`
- **content_type:** evidence-driven backlog post idea
- **primary_channel:** —
- **theme:** AI-SDLC audit; documentation reconciliation
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** A retrospective audit can expose missed defects, evidence gaps, and documentation drift, while still requiring human validation of every finding.
- **source_or_evidence:** [Retrospective defect-ledger seed](../../engineering-journal/2026-08-12-retrospective-defect-ledger-seed.md); [Defect Ledger process](../../defects/README.md)
- **related_project:** consulting-playbook; portfolio-tasks evidence referenced by the journal
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Retrospective journal and defect-ledger methodology.
- **derivative_content:** Potential audit checklist; none recorded.
- **notes:** New idea derived from project evidence, not a previously written post. Be explicit that AI output was untrusted and evidence-reviewed.

### CONTENT-025 — The Defects That Taught Me More Than the Successful AI Runs

- **status:** `idea`
- **content_type:** evidence-driven backlog post idea
- **primary_channel:** —
- **theme:** defect-led learning; AI-SDLC process design
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** Validated failures involving CI, duplicate execution, contract drift, ownership, and documentation can reveal controls that successful runs leave untested.
- **source_or_evidence:** [Retrospective defect-ledger seed](../../engineering-journal/2026-08-12-retrospective-defect-ledger-seed.md); [Defect Ledger](../../defects/defect-ledger.csv)
- **related_project:** consulting-playbook; portfolio-tasks evidence
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Defect records and narrative journal entries.
- **derivative_content:** Potential “failure → control” short-form sequence; none recorded.
- **notes:** New idea derived from project evidence, not a previously written post. `CONTENT-018` is the broad retrospective; this entry is the defect-led narrative angle.

### CONTENT-026 — When AI Follows the Instructions and Still Builds the Wrong Thing

- **status:** `developing`
- **content_type:** announced follow-up post
- **primary_channel:** Substack (intended)
- **theme:** requirements quality; architecture; AI-correct/specification-wrong defects
- **series:** Building an AI-Native SDLC in Public
- **summary_or_thesis:** AI can faithfully implement the supplied instructions and still build the wrong system when requirements, architecture, or interfaces are ambiguous, incorrect, or mutually inconsistent. The correction must begin in the defective upstream source rather than only in generated code.
- **source_or_evidence:** Closing bridge from `CONTENT-009`; [AI-Correct / Specification-Wrong metric](../../defects/metrics-definition.md#ai-correct--specification-wrong-defects); [immutable-baseline activation-blocker journal](../../engineering-journal/2026-08-13-immutable-baseline-activation-blocker.md); related defects in the [Defect Ledger](../../defects/defect-ledger.csv)
- **related_project:** consulting-playbook; cross-repository evidence referenced by the engineering journal
- **published_date:** —
- **published_url:** —
- **draft_path:** —
- **supporting_assets:** Potential “instruction followed → wrong system outcome → upstream correction” traceability visual; none recorded.
- **derivative_content:** Potential short-form example contrasting implementation defects with specification defects; none recorded.
- **notes:** Announced as the next topic in `CONTENT-009`. Keep distinct from `CONTENT-021`, which concerns defect amplification as implementation accelerates; this item focuses on faithful implementation of a defective or conflicting source.
