# Integration Checklist (Issue #30)

Integration verification was performed against the feature code at main commit `6b6bb8b058c0f272f9026ad2741b2045dd99b007`.

Guide 6.1 lists 10 required scenarios. The task acceptance criteria asks for 14 test mappings, so the additional four below cover the integrated notes, search, and reporting features.

## Automated tests

- Command: `python3 -m unittest discover -s tests -v`
- Result: **PASS — 157 tests**
- Full output: [`docs/test-output.txt`](test-output.txt)
- Verified code commit: `6b6bb8b058c0f272f9026ad2741b2045dd99b007`

## Guide 6.1 required scenarios

| # | Scenario | Passing test(s) | Result |
|---|---|---|---|
| 1 | High urgency + 12 users gives critical priority | `test_required_acceptance_scenarios` (`tests/test_tickets.py`, `TestPriority`) | Pass |
| 2 | High urgency + 2 users gives high priority | `test_required_acceptance_scenarios` (`tests/test_tickets.py`, `TestPriority`) | Pass |
| 3 | Low urgency + 4 users gives medium priority | `test_required_acceptance_scenarios` (`tests/test_tickets.py`, `TestPriority`) | Pass |
| 4 | Low urgency + 1 user gives low priority | `test_required_acceptance_scenarios` (`tests/test_tickets.py`, `TestPriority`) | Pass |
| 5 | Zero affected users is rejected | `test_bad_affected_users_rejected` (`tests/test_tickets.py`, `TestInvalidInput`) | Pass |
| 6 | Unassigned ticket cannot move to `in_progress`; state stays unchanged | `test_unassigned_cannot_start_progress` (`tests/test_workflow.py`, `TestTransitionStatus`) | Pass |
| 7 | Assigned ticket moves `open` → `in_progress` → `resolved` | `test_assigned_can_progress_to_in_progress` and `test_in_progress_to_resolved` (`tests/test_workflow.py`) | Pass |
| 8 | Work queue sorts by priority, then numeric ID | `test_orders_by_priority` and `test_tie_broken_by_numeric_id` (`tests/test_reports.py`, `TestWorkQueue`) | Pass |
| 9 | Save/reload preserves ticket data | `test_round_trip_with_notes` (`tests/test_storage.py`, `TestSaveAndLoad`) | Pass |
| 10 | Creating after reload uses a nonduplicate ticket ID | `test_next_ticket_id_after_reload_does_not_collide` (`tests/test_storage.py`, `TestIdContinuity`) | Pass |

## Additional integration cases for the 14-case acceptance criterion

| # | Scenario | Passing test(s) | Result |
|---|---|---|---|
| 11 | Note on a resolved ticket is rejected without changing ticket state | `test_resolved_ticket_rejects_notes_without_mutation` (`tests/test_notes.py`, `TestNotes`) | Pass |
| 12 | Notes remain intact through resolution and reopening; a new note can then be added | `test_notes_survive_resolve_and_reopen` (`tests/test_notes.py`, `TestNotes`) | Pass |
| 13 | Combined text, category, and status search applies every filter | `test_text_category_status_all_combined` (`tests/test_search.py`, `TestFilters`) | Pass |
| 14 | Empty and filled reports return expected counts | `test_empty_list_includes_every_group_with_zero` and `test_known_fixture_gives_exact_counts` (`tests/test_reports.py`, `TestReportInsights`) | Pass |

## Manual checks

- [x] **Full lifecycle:** In a temporary working directory, created `T001` (`Damage`, Network, medium urgency, 6 users; priority `medium`), assigned it to `mr John`, moved it through `in_progress` and `resolved`, then reopened it to `open`. All valid operations succeeded. An initial assignment using lowercase `t001` was rejected as unknown; retrying with `T001` succeeded.
- [x] **Notes (add/view):** In a temporary working directory, added `N001` to `T001` and viewed it successfully. The resolved-ticket rejection and reopen/add/view sequence has not been confirmed manually. Automated coverage passes in `test_resolved_ticket_rejects_notes_without_mutation` and `test_notes_survive_resolve_and_reopen`.
- [x] **Combined search:** In the prepared demo, searched for title text `Wi-Fi` with category `Network`, status `in_progress`, and priority `critical`; only `T001` appeared. The title filter uses literal substring matching, so `wifi` does not match `Wi-Fi`.
- [x] **Reports:** Verified an empty report (all zero counts and `0.0%`) and a 12-ticket fixture with four tickets in each status and three in each priority. The summary showed 8 unresolved, 4 resolved, and a `33.3%` resolution rate.
- [x] **Restart persistence:** After saving and restarting the CLI in the temporary working directory, listing tickets displayed `T001 | Damage | medium | open | mr John`, confirming ticket, status, and assignee persisted. Notes persistence across restart has not been manually checked.
- [x] **Corrupted file:** A temporary file containing invalid JSON raised `StorageError` with a clear message, and its bytes were unchanged.
- [x] **Duplicate-ID file:** A temporary JSON file containing duplicate ticket IDs raised `StorageError`, and its bytes were unchanged.
- [x] **Legacy and missing files:** A legacy ticket without `notes` loaded with `notes: []`; a missing file loaded as an empty list.
- [x] **Open Work Queue:** In the demo, the queue showed `T001` while open and was empty after moving it to `in_progress`. Automated coverage passes in `test_includes_only_open_tickets` and `test_queue_excludes_in_progress_and_resolved` (`tests/test_reports.py`, `tests/test_search.py`).
- [x] **Fresh-clone run:** Cloned the repository into a new temporary directory, confirmed Python 3.12.3, and ran `python3 -m unittest discover -s tests -v`: **PASS — 157 tests**.

## Invalid input and unchanged-state evidence

- Ticket creation: `test_failed_creation_leaves_list_unchanged` (`tests/test_tickets.py`).
- Notes: `test_resolved_ticket_rejects_notes_without_mutation` and invalid note-input tests (`tests/test_notes.py`).
- Workflow: `test_invalid_transition_leaves_entire_collection_unchanged` and `test_unassigned_cannot_start_progress` (`tests/test_workflow.py`).
- Search and reports are read-only: `test_search_leaves_collection_unchanged` and `test_report_does_not_modify_tickets`.
- Invalid storage data: `test_corrupt_json_rejected_and_file_unchanged`, `test_duplicate_ticket_id_rejected`, and the other `TestRejectedFiles` cases (`tests/test_storage.py`).

## Authorship, defects, and final revision

- Test authorship: Automated test count is 157. Commit history attributes ticket, storage, and notes tests primarily to Christopher Okoh; workflow tests and initial reports/work-queue tests to Moses Attah; and search, report-insight, understanding-check, and notes/search CLI tests to Musa Ogeh. CLI integration work is shared, and `tests/test_reports.py` also contains a numeric-ID regression test from Engineer A. This is commit/file attribution, not a per-test line count.
- Defect triage: The demo caught and corrected an inaccurate search example (`wifi` versus the literal title substring `Wi-Fi`). No product defect was found in the manual checks recorded above. Any newly found product defect must have its own issue and fix PR.
- Verified main base SHA: `6b6bb8b058c0f272f9026ad2741b2045dd99b007`. Update the final submission SHA after all PRs merge.
