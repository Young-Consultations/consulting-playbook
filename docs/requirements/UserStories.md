# User Stories

Acceptance criteria reference normative requirements rather than restating all
rules. Priority uses P0–P3.

## Engagement and evidence

| ID | Story | Acceptance criteria | Priority | Dependencies |
| --- | --- | --- | --- | --- |
| US-01 | As a consultant, I want to frame outcomes, boundaries, and decisions so that assessment effort addresses the real concern. | FR-ENG-01 criteria pass; sponsor validation and change history are visible. | P0 | Sponsor availability |
| US-02 | As a consulting lead, I want methods tailored with rationale so that consistency does not become rigidity. | FR-ENG-02 criteria pass for two contrasting scenarios. | P1 | US-01, catalog |
| US-03 | As a sponsor, I want authority and participation distinguished so that the right people decide and contribute. | FR-ENG-03 criteria pass; unresolved authority blocks approval. | P0 | US-01 |
| US-04 | As an evidence custodian, I want requests minimized and purpose-bound so that protected information is not collected needlessly. | FR-EVD-01 and FR-SEC-01 pass. | P0 | Handling policy |
| US-05 | As a reviewer, I want provenance, contradiction, gaps, and limitations visible so that I can challenge findings. | FR-EVD-02–04 pass for fact, assertion, observation, inference, and unavailable evidence. | P0 | Authorized sources |
| US-06 | As a participant, I want my disagreement and validation status preserved so that synthesis does not misrepresent my input. | FR-EVD-03 alternative and failure criteria pass. | P1 | Session authorization |

## Assessment, analysis, and decisions

| ID | Story | Acceptance criteria | Priority | Dependencies |
| --- | --- | --- | --- | --- |
| US-07 | As an engineering leader, I want a dated current-state model so that causes and progress are evaluated against a shared baseline. | FR-ASMT-01 passes with explicit unknown/excluded elements. | P1 | US-05 |
| US-08 | As a specialist, I want domain guidance to state limits and escalation so that generic playbook use does not replace expertise. | FR-ASMT-02 criteria pass for each current domain. | P1 | Catalog governance |
| US-09 | As a client sponsor, I want capability judgments anchored in context so that maturity scores do not create false precision. | FR-ASMT-03 positive and failure cases pass. | P0 | US-07 |
| US-10 | As a reviewer, I want findings, implications, causes, options, and recommendations distinct so that I can audit the reasoning. | FR-ANL-01–03 trace and negative criteria pass. | P0 | US-05 |
| US-11 | As a decision authority, I want transparent priorities and trade-offs so that I can choose, defer, condition, or reject advice. | FR-REC-01 and FR-DEC-01 pass, including override and changed decision. | P0 | US-10 |
| US-12 | As an executive, I want concise consequences and choices linked to technical detail so that audiences share one truth. | FR-RPT-01 reconciliation test passes. | P1 | US-11 |

## Action, follow-up, and reuse

| ID | Story | Acceptance criteria | Priority | Dependencies |
| --- | --- | --- | --- | --- |
| US-13 | As a program manager, I want approved direction sequenced by outcomes, owners, dependencies, and checkpoints so that follow-through is accountable. | FR-ROAD-01 passes; roadmap never asserts task authorization. | P1 | US-11 |
| US-14 | As a portfolio owner, I want one complete, classified proposal per target so that intake can govern work without consulting conversations. | FR-HO-01 and Interface-Portfolio-Tasks positive/negative tests pass. | P0 | US-13, external contract |
| US-15 | As a sponsor, I want follow-up compared with the original baseline so that activity is not mistaken for improvement. | FR-FU-01 passes including changed measures and incomplete evidence. | P1 | US-07, US-13 |
| US-16 | As a maintainer, I want assets owned, versioned, reviewed, and deprecated so that practice evolves without changing history. | FR-KM-01 passes and stale/missing-owner assets are flagged. | P1 | Maintainer assignment |
| US-17 | As a client, I want lessons generalized and screened so that another engagement does not expose my information. | FR-KM-02 and FR-SEC-01 pass. | P0 | Review authority |

## AI and delivery governance

| ID | Story | Acceptance criteria | Priority | Dependencies |
| --- | --- | --- | --- | --- |
| US-18 | As a consultant, I want bounded AI drafting with visible provenance so that I gain speed without treating AI as authority. | FR-SEC-02 and NFR-AI-02 pass; fabricated facts are rejected. | P0 | Classification/authorization |
| US-19 | As an AI agent, I want self-contained approved context so that I can work within one repository without inventing external behavior. | NFR-AI-01 and FR-HO-01 pass in a blind-agent review. | P1 | US-14 |
| US-20 | As a repository owner, I want live authorization checked before mutation so that stale routing cannot execute revoked or sensitive work. | FR-EXE-01 negative cases all fail without effects. | P0 | External contracts |
| US-21 | As a human reviewer, I want retries to converge on one draft and never merge so that publication remains safe and reviewable. | FR-EXE-02 race, ambiguity, reuse, and no-merge criteria pass. | P0 | US-20 |
