# Active pilot asset catalog

This catalog governs the reusable assets used by the active Software Delivery
Assessment commercial-validation pilot. The assets remain experimental delivery
IP; catalog status does not establish market demand, willingness-to-pay, or
repeatable economics.

## Shared governance metadata

| Field | Value |
| --- | --- |
| Owner | Consulting lead |
| Lifecycle status | Current experimental pilot assets |
| Version | 0.1.0 |
| Baseline identifier | `software-delivery-pilot-2026-10` |
| Last review | 2026-10-14 |
| Next review due | 2026-10-21 |
| Review rule | Review weekly while the experiment is active and before changing fee, scope, timing, evidence-handling controls, or client-facing terms. |

Client-specific engagement records created from these assets must record the
governing version and baseline identifier so a later reviewer can identify which
offer revision controlled the engagement.

## Catalog

| Asset | Purpose | Applicability | Dependencies | Variation points | Usage guidance |
| --- | --- | --- | --- | --- | --- |
| [Canonical pilot](01-service-offer/active-software-delivery-assessment-pilot.md) | Define the active commercial experiment and its boundaries. | One delayed feature, integration handoff, or release decision that passes pilot qualification. | Portfolio task #166; discovery issue #86; qualification, assessment, report, SOW, scoreboard. | Buyer/channel hypothesis and decision-specific context may vary; fee, caps, timing, exclusions, and handling controls require reviewed baseline change. | Use as the controlling pilot definition; do not present hypotheses as validated demand. |
| [Commercial-validation scoreboard](01-service-offer/commercial-validation-scoreboard.md) | Record aggregate experiment activity, outcomes, and learning. | Active pilot commercial validation only; aggregate sanitized observations. | Canonical pilot; issue #86 experimental targets. | Effective week, actual results, learning, and next experiment. | Record actuals separately from targets and preserve denominators; never store client identities or private analytics here. |
| [Client qualification checklist](02-client-intake/client-qualification-checklist.md) | Decide whether a prospect fits the bounded pilot before booking. | Active-pilot qualification section for task #166; generic larger-engagement section remains separately reusable. | Canonical pilot; information-handling requirements. | Buyer-specific sanitized rationale, conditions, and disposition. | Complete only in an authorized engagement workspace and apply record-level handling controls before sharing. |
| [Pilot assessment checklist](04-assessment-checklist/pilot-assessment-checklist.md) | Guide bounded evidence review and analysis. | Qualified active-pilot engagements. | Qualification record; canonical pilot; authorized evidence register. | Decision-specific evidence and analysis within caps. | Apply fail-closed evidence handling and preserve observation/inference separation. |
| [Pilot report](07-report-template/pilot-assessment-report.md) | Communicate the delivery map, findings, and two-week actions. | Qualified active-pilot engagements after sufficient evidence review. | Canonical pilot; assessment checklist; authorized evidence register. | Buyer-specific evidence references, findings, actions, and limitations. | Complete outside the public repository; expose handling status before transfer. |
| [Pilot proposal/SOW](09-proposals-and-sow/pilot-proposal-sow.md) | Establish bounded client-facing commercial and delivery terms. | Prospects that pass qualification and proceed toward booking. | Canonical pilot; qualification record; governing agreement where applicable. | Parties, dates, authorized destinations, signatures, and agreed commercial terms. | Record the governing pilot version/baseline and complete handling review before transfer or signature. |

A change that makes an asset no longer suitable or current must update this
catalog in the same reviewed change. Superseded baselines remain recoverable
from repository history.
