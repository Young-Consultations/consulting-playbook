# Young Consultations Consulting Playbook Vision

## Organization Vision

Young Consultations is building a governed AI-assisted software development operating system that turns human intent into approved, traceable, and reviewable software delivery. GitHub serves as the system of record for portfolio decisions, engineering work, execution evidence, and human approval. Specialized repositories collaborate through explicit versioned contracts so that planning, governance, AI execution, product generation, and consulting knowledge can evolve independently without sacrificing safety, accountability, or architectural coherence.

The organization combines professional software leadership, consulting methods, GitHub governance, and bounded AI execution. The system should help a software leader, consultant, or small engineering team move from business need to traceable engineering delivery. Human judgment remains authoritative for priorities, recommendations, approvals, architectural decisions, review, merge, and production use. Each repository owns a clear responsibility and collaborates through explicit contracts. In this model, consulting recommendations can become structured portfolio work rather than remaining disconnected reports, but only after an authorized human decision.

## Role in the Organization

The organization owner has supplied the following repository boundaries as authoritative context:

- `Young-Consultations/.github` owns organization AI-SDLC contracts, routing, repository registration, compatibility, and shared control-plane verification.
- `Young-Consultations/portfolio-tasks` owns structured portfolio intake, governance metadata, prioritization, approval, and initiation of authorized work.
- `Young-Consultations/slugger` owns the AI Software Factory product and controlled generation of validated software projects.
- `Young-Consultations/consulting-playbook` owns reusable consulting knowledge, assessment methods, decision frameworks, delivery playbooks, and recommendation-to-action patterns.

This repository therefore contains the methods and reusable intellectual assets of the consulting practice. It is not the portfolio backlog, the organization control plane, or the software-generation product. These descriptions do not assert direct inspection of the other repositories; they record the organization owner's cross-repository context.

## Repository Vision

Young-Consultations/consulting-playbook is the organization’s reusable consulting operating system. It turns software leadership experience and proven delivery practices into structured assessments, decision frameworks, playbooks, templates, and actionable recommendations that can be applied consistently and, when approved, translated into governed portfolio work.

### Current implemented scope

At this repository snapshot, the implemented scope is primarily an organization-routed target executor and its supporting repository policy, publication behavior, contract tests, and validation. The executor accepts approved, non-sensitive, Codex-assigned work through a versioned organization contract; supports non-mutating verification and bounded implementation; and restricts publication to deterministic draft pull requests subject to human review. The current documentation explains that operational mechanism.

No reusable consulting assessments, maturity models, engagement methods, reporting templates, recommendation frameworks, or consulting knowledge library were found in this repository snapshot. Their mention in this vision describes intended responsibilities, not existing capability. The next phase must develop requirements before those capabilities and content are implemented.

## Consulting Problem Statement

Software leaders and clients often begin with ambiguous concerns, fragmented evidence, visible delivery symptoms, and recommendations that are disconnected from accountable implementation. Without a shared method, assessments can vary unnecessarily, root causes can be confused with symptoms, technical findings can lose their business context, and useful recommendations can stop at a report.

The repository exists to codify how Young Consultations evaluates software organizations, identifies material delivery problems, recommends practical improvements, and converts recommendations into clear next actions. It should make the path from evidence to action repeatable and traceable without replacing professional judgment or client authority.

## Purpose and Value Proposition

The playbook should help clients and internal project leaders:

- understand the current state of a software product, team, portfolio, or delivery system;
- distinguish symptoms from systemic causes;
- align engineering work with customer and business priorities;
- improve backlog health and delivery governance;
- define practical improvement paths;
- identify architectural, process, quality, security, and operational risks;
- turn recommendations into sequenced, accountable work; and
- retain a traceable record of evidence, decisions, assumptions, and outcomes.

Its value is a consistent body of consulting practice that supports sound analysis, communication at executive and technical levels, explicit decisions, and governed follow-through while adapting to the scope and context of each engagement.

## Primary Users and Stakeholders

- **Independent software consultant:** applies reusable methods while tailoring analysis and advice to the engagement.
- **Software engineering lead:** connects delivery concerns, engineering constraints, and system-level improvement.
- **Software program manager:** coordinates outcomes, sequencing, dependencies, risks, and ownership across workstreams.
- **Client sponsor:** frames business outcomes, supplies authority and context, and decides whether to act on recommendations.
- **Product owner:** connects customer value, product priorities, requirements, and backlog decisions.
- **Engineering manager:** evaluates team capability, flow, quality practices, and operating-model improvements.
- **Software architect:** evaluates architectural fitness, constraints, decisions, dependencies, and technical risk.
- **Technical subject-matter expert:** contributes domain evidence and validates specialized findings or options.
- **Delivery team:** supplies practical evidence, tests the feasibility of recommendations, and performs separately authorized work.
- **Reviewer or decision authority:** challenges evidence and reasoning, records decisions, and approves or rejects proposed action within their authority.

## Desired Consulting Experience

The desired experience follows a reusable but judgment-driven progression:

**Client or project concern**
→ **engagement framing**
→ **evidence request**
→ **interviews and artifact review**
→ **current-state model**
→ **findings and risks**
→ **strategic options**
→ **prioritized recommendation**
→ **roadmap and ownership**
→ **approved actionable work**
→ **follow-up assessment**

The consultant makes assumptions, evidence, uncertainty, implications, alternatives, and decision points visible throughout. The exact depth, number of methods, evidence burden, participants, and outputs depend on engagement scope, risk, available information, and the decisions to be supported. Reuse should improve consistency, not force every engagement into the same sequence or level of detail.

## Consulting Knowledge Model

The future content model is:

**Principles**
→ **engagement types**
→ **assessment domains**
→ **methods**
→ **evidence checklists**
→ **templates**
→ **findings patterns**
→ **recommendation patterns**
→ **roadmaps**
→ **handoff artifacts**
→ **lessons learned**

Principles anchor professional conduct and reasoning; engagement types select fit-for-purpose paths; assessment domains organize subject matter; methods and evidence checklists support inquiry; templates support consistent capture and communication; reusable patterns accelerate analysis without predetermining it; roadmaps and handoff artifacts connect decisions to action; and lessons learned improve the knowledge base. This is a vision-level knowledge model, not a directory restructuring or assertion that these assets already exist.

## Repository Responsibilities

The repository should own:

- consulting principles and engagement model;
- discovery and intake methods;
- current-state assessment frameworks;
- maturity and capability assessments;
- product and project vision facilitation guidance;
- requirements-development guidance;
- backlog-health assessment;
- software delivery and SDLC assessment;
- architecture and technical-risk assessment;
- AI-assisted delivery readiness assessment;
- recommendation prioritization;
- roadmap and action-plan templates;
- executive and technical reporting templates;
- decision records and evidence guidance;
- recommendation-to-portfolio-task handoff patterns; and
- lessons learned and reusable consulting knowledge.

Over time, the modular knowledge system should provide reusable methods across strategy and vision; product and portfolio management; requirements; architecture; engineering execution; quality and testing; security; DevOps and release; organizational operating models; AI-assisted software delivery; and technical leadership and team effectiveness. These are intended knowledge responsibilities that require requirements and implementation.

## Explicit Non-Responsibilities

This repository does not own:

- the authoritative organization backlog;
- task approval state;
- organization-wide contracts or routing;
- Slugger's product implementation;
- autonomous client decisions;
- target-repository source code outside approved execution;
- automatic merging;
- production authorization; or
- claims that a consulting template alone proves compliance or engineering quality.

It also does not convert advice into authorization. Portfolio governance, target-specific implementation, review, merge, and production decisions remain with their designated owners and human authorities.

## Guiding Principles

- **Evidence before recommendation.** Establish what supports a conclusion and disclose limitations before advising action.
- **Distinguish symptoms from root causes.** Avoid treating visible incidents or delays as the whole system problem.
- **Connect technical findings to business or customer impact.** Explain why a technical condition matters and to whom.
- **Prioritize the system over isolated activity.** Optimize outcomes and flow rather than local busyness.
- **Improve the backlog and operating model, not only individual tasks.** Address the mechanisms that repeatedly shape delivery.
- **Preserve client and leadership decision authority.** Advice informs decisions; it does not replace accountable judgment.
- **Make assumptions visible.** Record what is believed, why, and what would validate or change it.
- **Separate findings, implications, recommendations, and decisions.** Preserve the reasoning chain and avoid presenting proposals as facts or approvals.
- **Produce actionable and owned next steps.** Identify ownership, sequence, dependencies, and decision points at an appropriate level.
- **Avoid one-size-fits-all prescriptions.** Tailor methods and advice to context, scope, risk, and capability.
- **Treat AI output as analysis support, not unquestioned authority.** Require professional evaluation, evidence, and human review.
- **Make approved recommendations traceable into portfolio work.** Retain the link from evidence and decision to separately governed tasks.
- **Protect confidential and sensitive information.** Minimize exposure, apply deliberate handling decisions, and keep sensitive evidence out of executable prompts unless explicitly reviewed and authorized.

## Measures of Vision Success

Vision success is demonstrated qualitatively when:

- assessments are repeatable without becoming mechanical;
- findings are supported by identifiable evidence;
- recommendations are prioritized and tied to consequences;
- executives and engineers can understand the same assessment at appropriate levels;
- action plans identify owners, sequencing, dependencies, and decision points;
- approved recommendations can be converted into complete target-specific portfolio tasks;
- follow-up engagements can evaluate progress against the original baseline;
- consulting content remains reusable and maintainable; and
- the repository's consulting role remains distinct from portfolio governance and code execution.

The repository ultimately succeeds when a consultant can use a repeatable method to move through:

**Engagement context**
→ **evidence collection**
→ **current-state assessment**
→ **findings**
→ **implications**
→ **prioritized recommendations**
→ **decision points**
→ **sequenced roadmap**
→ **approved portfolio work**
→ **measurable follow-up**

## Constraints and Guardrails

- Human judgment remains authoritative for consulting conclusions and all priority, recommendation, approval, architecture, review, merge, and production decisions.
- Consulting content must communicate the strength, source, limits, and sensitivity of evidence without claiming that use of a method or template proves quality or compliance.
- Confidential and sensitive information must be minimized and handled deliberately; it must not flow automatically from consulting evidence into AI prompts or target tasks.
- AI may assist analysis and drafting, but its outputs require evidence-based professional review and must not fabricate client facts.
- Repository boundaries and explicit versioned contracts must remain intact; this repository must not absorb portfolio approval, organization routing, or product-generation ownership.
- A recommendation is not execution authority, and a roadmap is not approval to modify a target repository.
- The current target executor remains bounded by approval, sensitivity, target, draft-only publication, and human-review controls.
- Future content must remain adaptable to engagement context and maintainable as professional knowledge evolves.

## Relationship to Governed Portfolio Work

The desired handoff is:

**Consulting recommendation**
→ **client or owner decision**
→ **approved recommendation**
→ **one or more structured portfolio tasks**
→ **target-specific execution**
→ **review and delivery**
→ **follow-up evidence**

Consulting recommendations do not authorize execution. A client or accountable owner first decides whether to approve the recommendation through the applicable governance process. Cross-repository recommendations must be decomposed into separate repository-specific tasks, and each target-specific task must contain enough context for isolated execution without relying on unstated consulting conversations or access to other repositories.

The authoritative approval state belongs outside this repository. This repository may eventually define templates and guidance for a complete, traceable handoff, but it does not become the portfolio system of record. Target-specific execution, review, delivery, and later evidence remain governed by their owning systems and authorities.

The currently implemented target-executor workflow is an enabling mechanism at the execution end of this relationship. It can receive properly approved work intended for this repository and prepare a draft change for review; it neither supplies the consulting method nor approves a recommendation.

## Evolution Strategy

Evolution should be modular and evidence-led. First, validate the assumptions and capability boundaries below; then define requirements and an information architecture; next, implement a small coherent core method with governance and maintenance guidance; and finally, add assessment domains, engagement variants, and reusable patterns as use demonstrates value. Versioning and review should let methods evolve without silently changing the meaning of prior engagement records.

The playbook should support consistent delivery while preserving professional judgment and engagement context. Lessons learned should improve shared knowledge without exposing confidential client information or turning engagement-specific conclusions into universal prescriptions. Existing execution infrastructure should continue to be treated as a delivery enabler rather than evidence that the consulting content system is complete.

## Transition to Requirements Development

The next phase should elaborate, in order:

**Consulting vision**
→ **engagement outcomes**
→ **consulting capabilities**
→ **content and workflow constraints**
→ **functional requirements**
→ **non-functional requirements**
→ **information requirements**
→ **template requirements**
→ **integration requirements**
→ **verification criteria**
→ **implementation backlog**

This vision intentionally stops before shall-statements, detailed templates, questionnaires, scoring models, user stories, acceptance criteria, and implementation issues. Requirements development should address these capability areas:

- **Engagement intake:** Define the information needed to understand the initiating concern, context, sponsorship, urgency, and engagement fit.
- **Scope and objective definition:** Frame intended outcomes, boundaries, exclusions, constraints, risks, and decisions the engagement will support.
- **Stakeholder mapping:** Identify affected, informed, consulted, and decision-making parties and their perspectives or authority.
- **Evidence collection:** Guide proportionate requests, provenance, sufficiency, limitations, storage, and handling of evidence.
- **Interview and workshop guidance:** Support consistent preparation, facilitation, capture, synthesis, and participant validation without scripting away judgment.
- **Current-state modeling:** Represent relevant products, teams, processes, systems, dependencies, decisions, and observed outcomes as a baseline.
- **Maturity assessment:** Evaluate capability development in context without turning generic levels into unsupported precision or universal targets.
- **Product and vision assessment:** Examine alignment among customer needs, business intent, product direction, outcomes, and engineering activity.
- **Backlog-health assessment:** Examine clarity, readiness, prioritization, traceability, flow, ownership, dependencies, and alignment of planned work.
- **SDLC and delivery assessment:** Evaluate how work moves from intent through development, verification, release, feedback, and governance.
- **Architecture assessment:** Examine architectural fitness, decisions, constraints, dependencies, evolvability, and material technical risk.
- **Quality and testing assessment:** Evaluate quality strategy, test coverage by risk, feedback loops, defect learning, and confidence in change.
- **Security and risk assessment:** Identify material security, privacy, compliance, resilience, and delivery risks while respecting specialist authority.
- **DevOps and release assessment:** Evaluate environments, automation, deployment, observability, release controls, operability, and recovery practices.
- **AI-readiness assessment:** Evaluate the governance, data handling, engineering discipline, review controls, and task quality needed for bounded AI assistance.
- **Findings management:** Capture findings with evidence, confidence, scope, status, related impacts, and traceable evolution.
- **Root-cause analysis:** Support disciplined movement from symptoms and contributing conditions toward testable systemic causes.
- **Options analysis:** Compare credible response paths, trade-offs, costs, risks, dependencies, reversibility, and consequences of inaction.
- **Recommendation prioritization:** Order advice using transparent value, urgency, risk, effort, dependency, and organizational-readiness considerations.
- **Roadmap development:** Turn approved direction into sequenced outcomes, ownership, dependencies, decision points, and learning checkpoints.
- **Executive reporting:** Communicate material context, consequences, choices, recommendations, and decisions at an appropriate leadership level.
- **Technical reporting:** Preserve sufficient evidence, reasoning, constraints, risks, and implementation context for engineering review.
- **Decision capture:** Record accountable decisions, alternatives, rationale, assumptions, conditions, and follow-up needs.
- **Recommendation-to-task handoff:** Translate approved recommendations into complete, separately governed, repository-specific task context with traceability.
- **Follow-up measurement:** Compare outcomes and capability changes with the original baseline, decisions, and intended measures.
- **Knowledge maintenance:** Govern ownership, review, versioning, deprecation, lessons learned, and safe reuse of consulting content.
- **Confidentiality and sensitive-data controls:** Define classification, minimization, access, retention, redaction, and deliberate transfer rules across evidence, reports, AI use, and task handoffs.

## Vision Assumptions Requiring Validation

These assumptions guide requirements exploration; they are not validated facts or predetermined requirements.

| Assumption | Why it matters | Requirements-phase validation method |
| --- | --- | --- |
| Consulting engagements need both executive and technical outputs. | The knowledge and reporting model must serve different decisions and levels of detail without creating contradictory narratives. | Map representative stakeholder decisions and review sample output expectations with executive and technical roles. |
| Evidence-based repeatability creates value without eliminating professional judgment. | The central value proposition depends on consistency and adaptability coexisting. | Walk multiple representative engagement scenarios through a candidate core method and identify where standardization helps or constrains judgment. |
| Backlog health is a major predictor of delivery effectiveness. | Backlog assessment is expected to be a prominent method and source of improvement recommendations. | Compare backlog signals with delivery outcomes in appropriately authorized case evidence and seek practitioner challenge to causal assumptions. |
| Software leads create more leverage by improving the system than by repeatedly compensating as individual contributors. | The playbook prioritizes operating-model improvement over recurring local intervention. | Interview software leads and sponsors about intervention patterns, constraints, and sustained outcomes, then test the claim against engagement evidence. |
| Clients benefit from recommendations that can become governed implementation work. | The recommendation-to-task handoff is a key connection between consulting value and delivery outcomes. | Trace representative recommendation scenarios through decision, decomposition, ownership, and follow-up with relevant authorities. |
| GitHub can serve as the traceability surface for approved actions. | Integration and information requirements may rely on durable links among decisions, tasks, execution evidence, and review. | Validate required records, access boundaries, lifecycle, reporting needs, and GitHub capabilities with governance stakeholders. |
| Sensitive client evidence must not be copied into executable task prompts without deliberate review. | Unsafe transfer could expose confidential information and undermine client trust and governance. | Conduct data-flow and threat-model workshops to define classification, redaction, approval, access, and retention controls. |
| Different engagement types can reuse a shared core method. | A modular core is necessary for maintainability and consistency without one-size-fits-all delivery. | Model several distinct engagement types, identify genuinely common stages and artifacts, and record justified variation points. |
