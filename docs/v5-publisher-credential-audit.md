# Temporary V5.6 publisher credential diagnostic

Draft operational diagnostic under organization issue #77; review and merge do
not authorize execution. Supports FR-EXE-01/02, FR-SEC-01/02 and NFR-SEC-02/03
without changing the immutable executor or external contract. The exact v5
adapter conformance pin and workflow are unchanged. A separate temporary
offline CI workflow is intentional: editing the existing pinned conformance
workflow would invalidate its reviewed blob identity.

After separate owner approval, dispatch publisher-credential-audit.yml on
consulting-playbook main, first attempt only, with expected_main_sha equal to
the independently verified reviewed merge and confirmation
audit-publisher-read-only. The exact current owner login is mightyjoe909.
The job does not enter the protected environment or receive model/result/router
credentials. Only the final isolated Python step receives the existing
repository TARGET_PUBLICATION_TOKEN. GET requests are fixed to GitHub HTTPS;
no redirects, proxies, arbitrary destinations, retry, raw response logs,
fingerprint or artifact. Public control-plane tag read is unauthenticated;
the publisher credential is used only for /user and the consulting target.
The diagnostic is not a write-capability proof, a token-continuity proof across
later runs, readiness evidence, execution authority or a canary. The owner
must retain the credential unchanged through the later canary and provisioning.
The V5.9 readiness secret requires a separately designed and authorized
protected in-run binding; do not export the token or fingerprint.

On failure or unexpected automation, stop and inspect fixed categories;
no rotation, permission expansion, retry, model execution or operational
changes are authorized. Remove the temporary diagnostic and its CI after
the required evidence is accepted, using a separate reviewed change.
DEF-0105 remains accepted-risk. Paid approval hold continues.
