# Error Handling Strategy

## Principles

Errors are typed outcomes with stable safe codes, ownership and recovery guidance. Preserve evidence, never convert uncertainty to success, and retry only when semantics and idempotency make it safe. User messages explain remediation without exposing sensitive internals; diagnostic detail is correlated and access-controlled.

## Categories

| Category | Examples | Propagation and recovery | Retry |
|---|---|---|---|
| Input validation | Missing required field, malformed reference | Return field/path and requirement; no mutation. | After correction only. |
| Business rule | Insufficient finding support, unauthorized roadmap item | Explain violated invariant and allowed next state. | No blind retry. |
| Authentication/authorization | Invalid principal, stale/revoked proof, edited approved scope, mutable-label-only claim | Deny and emit canonical safe evidence; resolve with portfolio authority. | Only after a new explicit authoritative decision. |
| Classification/privacy | Unknown class, prohibited destination | Restrict/quarantine; minimize or obtain specific authorization. | Only after policy decision. |
| Concurrency/conflict | Stale aggregate revision, external divergence | Return current revision; human/application reconciles. | Reload then deliberate resubmit. |
| Contract/compatibility | Unknown version, invalid external payload | Reject/quarantine safe metadata; notify owners. | After compatible upgrade/correction. |
| Dependency transient | Timeout, throttle, temporary unavailable | Mark degraded/indeterminate, isolate via circuit breaker. | Bounded backoff if idempotent. |
| Dependency permanent/business | External rejection, permission denied | Record authoritative rejection; owner action. | No automatic retry. |
| Integrity/audit | Digest mismatch, audit append failure, broken invariant | Stop governed mutations, alert, preserve evidence. | Manual recovery only. |
| AI quality/safety | Unsupported claim, unsafe content, prompt injection | Discard/quarantine as permitted; human workflow continues. | Re-prompt only after reviewed correction. |
| Publication ambiguity | Orphan branch, conflicting marker, prior closed PR | Block; inspect ancestry/markers; new authority/identity if replacement. | Same identity does not authorize replacement. |

## Canonical error result

The organization contract owns the error/result shape and lifecycle vocabulary;
this repository defines no envelope or field names. A failure must preserve
delivery/result correlation, target, timestamps, validation evidence, a safe
category/detail, and organization-defined retry/reconciliation guidance. Internal
causes, stack traces, secrets, prompts, and sensitive content remain diagnostic-only.
Contract, authorization, local policy, validation, execution, publication, and
interrupted/ambiguous outcomes remain distinguishable using canonical semantics.

## Propagation and fault isolation

Domain errors return explicitly to application services. Adapters translate provider errors at the boundary. One domain assessment, renderer, AI provider or external connector failure must not corrupt other engagements or the canonical model. Circuit breakers/bulkheads and workload limits isolate dependencies. Audit/integrity failure is system-wide for affected governed writes and cannot be downgraded.

## Transaction and compensation

Within one aggregate, commit state and required audit/event atomically. Across owners, record intent/attempt before effect, use idempotency, then record acknowledgement. Do not roll back an already accepted external record by pretending it never existed; issue an owner-authorized cancellation/supersession or reconcile. Projection failure is compensated by rebuild. Report delivery failure does not revert the underlying decision.

## Retry policy

Retry only transient errors, with capped exponential backoff, jitter, attempt/time budget and server-provided limits. Preserve correlation and effect identity. Validate authorization/classification freshness again when required. After timeout with possible side effect, reconcile before resubmission. Poison messages go to a protected quarantine/dead-letter path after bounded attempts. Humans are notified before an SLA or recovery threshold expires.

## User recovery experiences

- Drafts preserve valid entered data and identify exact gaps.
- Disputes offer compare/revise/supersede rather than destructive overwrite.
- Offline/degraded mode clearly indicates unavailable validation and prohibits final transitions that require it.
- Stale reports show source revision and offer regeneration.
- External rejection links to the local proposal and safe owner reason.
- Ambiguous automation gives an evidence-preserving operator checklist, never a “force” action.

## Validation and chaos scenarios

Test malformed/oversized data, unauthorized access, stale revisions, unavailable authority, expired transfer, lost acknowledgement, duplicate event, partial projection, throttling, provider outage, corrupt audit write, replay after restore and publication races. Assert no duplicate effect, no confidentiality leakage, no false success and deterministic recovery guidance.
