# V5.9 encrypted readiness handoff (proposed, not authorized to run)

Preserve the immutable v5 tags and existing repository TARGET_PUBLICATION_TOKEN.
This maintenance helper reads GitHub evidence and encrypts a v1 readiness
record to the protected environment's GitHub public key. It never writes a
GitHub secret, publishes a branch/PR, invokes a model, or exports plaintext.
The owner must accept fresh V5.8 publication evidence independently first.

## Preconditions and separation

- Merge this reviewed helper only under separate approval. Freeze the exact
  reviewed head on review/v5-readiness-handoff; never move it for a live run.
  GitHub requires the dispatch workflow to exist on default branch.
  Recompute the V5.8 base/authorization/marker after merge.
- Before canary dispatch capture owner-side GET metadata for repository
  TARGET_PUBLICATION_TOKEN: created_at, updated_at and observed_at UTC, scope,
  absence of org duplicate and environment override. Attest token value and
  permission continuity. Freeze the credential from before queueing V5.8
  through packaging, installation, and verification. After canary completion,
  repeat metadata readback; repeat again after each helper run and before
  installation. If any value changed or cannot be established, STOP.
  The runner cannot independently read administrative secret metadata; these
  snapshots are owner attestations, not cryptographic proof of same secret.
- Independently accept actual first-attempt created-draft-verified evidence
  and preserve draft/branch/main. Revoke PUBLICATION_CANARY_AUTHORIZATION.
- The existing environment is tag-only. Separately authorize adding **only**
  branch review/v5-readiness-handoff to its deployment policy, retaining the
  sole owner reviewer and no admin bypass. This permits other workflows at
  that branch to request deployment; never approve any except the exact
  helper run. Do not dispatch model probes. Freeze the branch. Restore
  tag-only policy after verification. No environment changes by this PR.
- Owner reads exact environment public key via GET
  /repos/Young-Consultations/consulting-playbook/environments/consulting-playbook-codex/secrets/public-key.
  Independently verify the key and key ID before authorizing package.
  If unavailable, stop. No privileged administrative token on runner.

## Owner inputs (future separate approvals)

Workflow dispatch must be from the frozen maintenance branch, actor and
triggering actor mightyjoe909, attempt 1, exact expected_helper_sha. Only
approve the specific waiting helper job/environment after verifying its
mode, canary run ID, immutable SHA, owner evidence and grant.
The continuity_json input is a JSON object with before and after objects,
each with exactly repository, secret_name, scope (repository), created_at,
updated_at, observed_at (UTC YYYY-MM-DDTHH:MM:SSZ), no_environment_override,
no_org_duplicate, credential_and_permissions_unchanged (all true).
Before observation <= canary queue time, after >= completed run updated_at
and <= helper queue time, within two hours of packaging. Same metadata
except observation timestamp. Never include secrets or fingerprints.
Owner must independently verify actual GitHub metadata, including absence
of fallbacks; inability to read it is a blocker.

Dispatch only after separate owner authorization, while no maintenance grant exists.
The unconditional credential-free preflight must succeed and the handoff job
must wait at the protected environment. Verify the actual helper run ID,
attempt 1, exact commit/ref, owner and input tuple before setting any grant.
Do not approve the deployment yet. Separately approve a protected environment variable
PUBLICATION_READINESS_MAINTENANCE_AUTHORIZATION equal to:
readiness-handoff:MODE:HELPER_SHA:CANARY_RUN_ID:HELPER_RUN_ID:1:CONTINUITY_SHA256:KEY_BINDING
where CONTINUITY_SHA256 is SHA256 of compact sorted JSON, KEY_BINDING is
KEY_ID:SHA256_OF_DECODED_PUBLIC_KEY for package, or no-key for verify.
No repo/org fallback for this grant; owner verifies this. Do not reuse grants
or dispatch twice. Confirmation is package-accepted-canary or
verify-accepted-canary. Verify inputs must have empty key fields. Grant does
not auto-consume; remove separately after the exact authorized attempt.
Protected approval remains separate even if grant exists. The grant is bound
to the waiting helper run ID and attempt 1, not just the canary run; a second
fresh run cannot use it. If preflight fails or the protected job is absent,
stop. Green workflow status alone is not acceptance: verify the successful
preflight and handoff jobs, exactly one successful mode step, the other
skipped, the enforcement step and mode-specific terminal PASS log.

## Owner installation and verification (not implemented as an action)

Package mode requires exactly one authenticated successful canary job log
result with fresh status; reads the live draft/commit/marker and immutable
registry using read-only credential; rechecks publisher /user and push
metadata; validates exact plaintext with immutable validator. Sealed box
uses GitHub's environment public key via system libsodium. Only ciphertext
and nonsecret bindings go in one-day artifact publication-readiness-envelope.
Inspect exact run identity, job success and artifact provenance, including
helper_run_id and helper_run_attempt=1 in the envelope, matching the grant
and actual producing run; read back
public key and ID again from exact environment and compare. Recheck
continuity, release and grant. No plaintext or fingerprint in artifacts.
Separately authorize owner-side installation via environment secret PUT
with only encrypted_value and key_id, after verifying absence of existing
readiness secret and repo/org fallback. Use current owner credential if
permitted; if not, stop for separate decision. Never place ciphertext or
token in Git or logs. Do not claim readback of secret value through API.

Verify mode independently repeats canary/evidence checks, reads actual
protected readiness secret and publisher token, runs immutable validator,
and compares draft URL and verification time against accepted canary.
Only PASS/FAIL logs; no artifact, writes or model. Separate mode grant,
dispatch and protected approval. Check exact run and final metadata,
remove grant and temporary branch policy via separate owner authorization.
No production migration until subsequent gates. If any mismatch, no retry,
no rotation, no cleanup and no new canary without explicit approval.
The existing immutable adapter still rejects absent, stale or mismatched
readiness. Verification time is canary time, never packaging time.

## Risks and limits

Owner input key must be authentic: binding the grant to its digest does not
independently prove it belongs to GitHub. Owner obtains it directly and
verifies again immediately before installation; never use a supplied third
party key. Public repository artifact contains ciphertext only. GitHub
hosted runner, immutable checkout, pinned actions, gh log access, system
libsodium and GitHub secret API availability remain live prerequisites.
No provider billing proof, no readiness claim from CI, no paid approval,
no new tags or Pi services. DEF-0105 remains accepted-risk.
