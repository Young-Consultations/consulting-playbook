# DEF-0125 release migration

The owner approved the major adapter classification and receiver migration on
2026-10-28. The candidate adapter is `codex-adapter-v4.0.0`; its result receiver
and credential preflight both pin forthcoming `ai-sdlc-v4.0.0`.

The mandatory protected `CODEX_AUTHORIZED_CONTROL_PLANE_SHA` binding and stricter
historical-draft provenance/freshness rules change operational prerequisites and
observable reuse policy. The v2 payload schemas and existing dispatch inputs stay
unchanged. The coordinated organization release must accept its own 4.0.0
admissions and the reviewed predecessor admission releases.

This target commit requires a fresh pin/report and CI/review before immutable
tagging. Organization PR #116 must subsequently bind its exact tag, commit and
report digest, validate the matching receiver bundle with the release-aware
verifier, and complete the governed release and publication-attestation steps.
The protected environment must authorize the reviewed registry-bearing commit
and restrict execution to the registered immutable target workflow ref/SHA.

The pending receiver state in the no-cost report remains explicit until remote
compatibility and deployed preflight pass. DEF-0125 remains investigating until
separately approved fresh-identity operational acceptance. Source #167 remains
terminal and must not be replayed.
