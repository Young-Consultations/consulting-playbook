# Business Rules

## Authority and governance

| ID | Rule |
| --- | --- |
| BR-01 | A recommendation, roadmap, handoff proposal, AI output, or task draft is not approval or execution authority. |
| BR-02 | Only a named authority acting within documented scope may approve, reject, defer, condition, or supersede a recommendation. |
| BR-03 | Human judgment is authoritative for conclusions, priorities, recommendations, architecture, review, merge, release, and production use. |
| BR-04 | Consulting-playbook owns method semantics; external systems retain authority for their records and states. |
| BR-05 | Material method/requirement changes require rationale, reviewers, affected IDs, compatibility impact, and version history. |

## Evidence and validation

| ID | Rule |
| --- | --- |
| BR-06 | Every evidence request must have a scope-relevant purpose and collect the minimum necessary information. |
| BR-07 | Source fact, participant assertion, observation, inference, hypothesis, finding, implication, recommendation, and decision must remain distinguishable. |
| BR-08 | A material final finding must link sufficient evidence or carry an explicit limitation accepted by the appropriate reviewer/authority. |
| BR-09 | Contrary evidence, disagreement, gaps, uncertainty, confidence, and scope limits may not be silently removed. |
| BR-10 | Absence of evidence is not evidence of absence or poor capability unless the method justifies that inference. |
| BR-11 | Correlation may not be stated as causation without supporting rationale and consideration of alternatives. |
| BR-12 | Maturity/capability ratings require contextual observable anchors and may not imply universal target states or unsupported precision. |

## Lifecycle and routing

| ID | Rule |
| --- | --- |
| BR-13 | The normative reasoning order is evidence → finding → implication → option/recommendation → decision → roadmap/handoff; iteration is allowed but skipped stages require rationale. |
| BR-14 | Finding states are at minimum proposed, validated, disputed, superseded, and withdrawn; recommendation states are at minimum proposed, approved, rejected, deferred, conditional, superseded, and completed/closed where defined. |
| BR-15 | State changes require actor, time, rationale, and retained prior state. Blank, unknown, disputed, and not-applicable are distinct. |
| BR-16 | Only approved/conditional recommendations may enter a roadmap or portfolio handoff, and all conditions must travel with them. |
| BR-17 | Cross-repository action must be decomposed by target ownership; each task must be independently understandable and governable. |
| BR-18 | Target and authoritative external state must be validated at the trust boundary; cached consulting state cannot grant authorization. |
| BR-19 | Automation may route only explicit structured authority and classification; it may not infer either from narrative text. |

## Prioritization and reporting

| ID | Rule |
| --- | --- |
| BR-20 | Prioritization criteria must be declared and include value/impact, urgency, risk, effort range, dependencies, readiness, uncertainty, and consequence of inaction as applicable. |
| BR-21 | Human override of calculated or suggested priority is permitted only with visible rationale and authority. |
| BR-22 | Executive and technical views may differ in detail but not in material facts, status, priority, uncertainty, or decision. |
| BR-23 | A template, checklist, score, or completed assessment does not itself establish quality, fitness, certification, or compliance. |

## Confidentiality and automation

| ID | Rule |
| --- | --- |
| BR-24 | Unknown classification is restricted until a designated authority resolves it. |
| BR-25 | Sensitive information transfer authorization is specific to purpose, destination, minimum content, and time; authorization for one destination does not transfer to another. |
| BR-26 | Client-specific content may become reusable knowledge only after authorization, minimization/generalization, confidentiality review, applicability limits, and content approval. |
| BR-27 | AI assistance must be disclosed and professionally reviewed; AI may not invent client facts, approve records, or act as decision authority. |
| BR-28 | Verify-mode execution is non-mutating; implement-mode target publication is draft-only, validates/tests changes, never pushes directly to `main`, and never merges automatically. |
| BR-29 | One logical delivery identity permits at most one completed managed publication effect; ambiguity blocks automation and preserves evidence for manual recovery. |
| BR-30 | Retrying the same delivery does not renew revoked authority, clear sensitivity, authorize replacement, or create a new logical delivery. |

## Approval rule precedence

Where rules conflict, applicable law/client handling obligations and explicit
human safety authority take precedence, followed by the vision, approved
requirements baseline, versioned external contract, and engagement tailoring.
Tailoring cannot waive BR-01–05 or BR-24–30.
