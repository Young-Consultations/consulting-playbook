# 2026-11-24 - Historical defect reconciliation (A2.3)

Status: candidate dispositions only; canonical main not changed. Reuse existing PR #101. No deliveries replayed; no tags, credential or activation changes, paid implementation calls or Pi effects.

## Scope and evidence

The canonical CSV has 143 nonblank defect IDs (144 data lines including a blank record); the existing candidate adds five IDs DEF-0147 through DEF-0151. Preserve blank record and existing historical IDs. The main ledger blob is unchanged from the original PR base, so forward-integrate current main into the existing draft without force push or dropping prior evidence. No new IDs allocated for this reconciliation.

- PR #123 post-merge [CI](https://github.com/Young-Consultations/.github/actions/runs/45542615764) passed at b513b56eb1ef97ccab6781b0b22e5ee2f66a9de3 including staged release tests and Actionlint.
- [PR #96](https://github.com/Young-Consultations/consulting-playbook/pull/96) merged at 405981a9ca2ddca0020aa56e77d38e5a1d1b8daa; immutable v4 adapter 84964d3ba099630cd5c6101e598bfca5433c74c5 is a descendant. [Exact conformance job](https://github.com/Young-Consultations/consulting-playbook/actions/runs/40711877248/job/122899016426) passed all required suites: repository validator 10, content baseline 6, checkout 16, sandbox 8, isolation 4 plus auth/adapter and shared oracle. Sandbox was mandatory and no-effect checks passed. Parent [DEF-0125 live acceptance](2026-10-28-def-0125-live-acceptance.md) is not by itself proof of these individual negative paths.
- Each row below maps to a distinct regression present in the actual immutable adapter tests; verified by inspecting exact source and historical CI. No fresh tests or live negative injections performed. Historical discovery details and repair commits retained. Proposed date_resolved uses historical successful immutable CI date 2026-10-28, not the date of this reconciliation.

| Defect | Exact immutable focused regression |
| --- | --- |
| DEF-0126 | [test_task_content_checkout.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_task_content_checkout.py): test_executor_must_equal_external_release_before_content_read; test_workflow_guard_rejects_mutable_wrong_missing_and_unregistered_executors |
| DEF-0127 | [test_task_content_checkout.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_task_content_checkout.py): test_real_publisher_race_windows_and_durable_provenance; test_block_failure_preserves_partial_identity |
| DEF-0128 | [test_task_content_checkout.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_task_content_checkout.py): test_real_publisher_race_windows_and_durable_provenance |
| DEF-0129 | [test_task_content_checkout.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_task_content_checkout.py): test_workflow_guard_rejects_mutable_wrong_missing_and_unregistered_executors |
| DEF-0130 | [test_task_content_checkout.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_task_content_checkout.py): test_ambiguous_remote_create_is_rechecked_before_success |
| DEF-0131 | [test_task_content_checkout.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_task_content_checkout.py): test_baseline_shares_one_deadline_across_git_and_both_api_reads; test_api_deadline_expiry_stops_before_second_read |
| DEF-0132 | [test_task_content_checkout.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_task_content_checkout.py): test_pushed_object_survives_topic_ref_deletion_in_canonical_evidence |
| DEF-0133 | [test_task_content_checkout.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_task_content_checkout.py): test_final_attestation_and_blocking_share_one_deadline |
| DEF-0134 | [test_candidate_test_sandbox.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_candidate_test_sandbox.py): test_broken_candidate_and_deleted_tests_cannot_pass; test_adapter_does_not_claim_tests_pass_on_sandbox_failure; test_missing_tests_and_missing_sandbox_fail_closed |
| DEF-0135 | [test_task_content_checkout.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_task_content_checkout.py): test_timed_out_push_reconciles_exact_object_and_preserves_partial_result; test_expired_push_reconciliation_never_starts_another_api_call |
| DEF-0136 | [test_candidate_test_sandbox.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_candidate_test_sandbox.py): test_home_descendant_and_symlink_dependency_paths_are_not_mounted; test_untrusted_test_has_no_host_credentials_network_or_parent_process |
| DEF-0137 | [test_publication_isolation.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_publication_isolation.py): test_model_git_configuration_hooks_filters_and_url_rewrites_never_run; test_links_and_nested_metadata_cannot_enter_the_trusted_checkout |
| DEF-0138 | [test_publication_isolation.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_publication_isolation.py): test_publication_hook_rejects_even_fastforward_updates_to_existing_refs |
| DEF-0139 | [test_publication_isolation.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_publication_isolation.py): test_actual_discovery_rejects_changed_or_incomplete_bindings_before_model |
| DEF-0140 | [test_validate_repository.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_validate_repository.py): test_nested_untracked_files_are_validated_individually |
| DEF-0141 | [test_validate_repository.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_validate_repository.py): test_binary_credential_values_and_chunk_boundaries_are_rejected; test_binary_baseline_value_duplication_is_rejected_in_final_and_index |
| DEF-0142 | [test_validate_repository.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_validate_repository.py): test_non_utf8_file_names_fail_closed |
| DEF-0143 | [test_validate_repository.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_validate_repository.py): test_binary_baseline_value_duplication_is_rejected_in_final_and_index |
| DEF-0144 | [test_validate_repository.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_validate_repository.py): test_credential_values_in_names_are_rejected_without_echoing_them |
| DEF-0145 | [test_publication_isolation.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_publication_isolation.py): test_actual_discovery_rejects_changed_or_incomplete_bindings_before_model (stale and head-unreadable cases) |
| DEF-0146 | [test_task_content_checkout.py](https://github.com/Young-Consultations/consulting-playbook/blob/84964d3ba099630cd5c6101e598bfca5433c74c5/scripts/test_task_content_checkout.py): test_ambiguous_remote_create_is_rechecked_before_success (timeout cases, one create, bounded recovery) |

## Earlier open records

- DEF-0028: #32 initial final-head and main CI failed; #33 subsequent merge cb5a5bb04af7ef2223511490c3605064b1434105 passed [32774758817](https://github.com/Young-Consultations/consulting-playbook/actions/runs/32774758817) on Aug 24. Do not claim the premature merge was green. Old failing job logs expired (HTTP 410); the original failure description remains grounded in the ledger/PR, not a newly inspected log.
- DEF-0033: merged portfolio #143 passed PR CI and [33691728930](https://github.com/Young-Consultations/portfolio-tasks/actions/runs/33691728930) passed source binding/projection. [#139 source result](https://github.com/Young-Consultations/portfolio-tasks/issues/139#issuecomment-5517459200) has matching receipt/forwarding digest. This resolves the enriched admission marker defect, not the original task or all lifecycle states. #139 is closed but retained queued label; do not alter historical issue here.

## Remaining and data quality

- DEF-0105 / #82: existing MVP accepted risk remains technically unresolved; no safe rollback asserted. A2.5 handles representation.
- DEF-0147 / #172: latest observed scheduled run 45452014161 still predates repair and failed; do not close on PR/manual checks.
- DEF-0148/0149/0150 retain resolved candidate dispositions; removed unsupported DEF-0149 origin phase and distance 4. Taxonomy explicitly permits error-handling and identity-idempotency-mismatch; no ad hoc reclassification. No inferred dates, phase metrics or effort. Legacy vocabulary drift in other historical records is not silently normalized.
- DEF-0151 / #111: existing 64 focused and 20 synthetic seam cases passed; historical issue opening time is known, first sufficient discovery date and complete reproducible seam acceptance not yet established. Keep investigating; never replay #167.
- #77 remains operationally blocked pending release binding and protected no-model canary. DEF-0048 is its historical Git transport root lesson, not duplicate defect count.
- #167 source still queued despite trusted terminal failed receipt, forwarding and source projection; A2.4 separately reconciles state and captures the distinct defect. No issue labels changed here.
- Existing A1 and A2.1 journals and candidate records are preserved. Final exact-head CI/review and human merge acceptance required.

## Learning

A parent release success and green review do not replace targeted regression evidence for each child defect. Historical failures, expired logs and evidence limitations must remain visible. Close the specific corrected discrepancy, not every symptom or associated task. Verify deployed identity plus negative-path coverage before updating quantitative status.
