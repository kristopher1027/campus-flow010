# Integration Checklist (Issue #30)

Run from `test/30-integration` after both feature PRs have merged. Starting `main` commit: `6b6bb8b058c0f272f9026ad2741b2045dd99b007`.

> Guide 6.1, as provided, lists 10 required scenarios. The task acceptance criteria separately asks for 14 case-to-test mappings, so cases 11–14 below are additional integration coverage drawn from the task description, not cases from guide 6.1.

## Automated tests

- Command: `python3 -m unittest discover -s tests -v`
- Result: **PASS — 157 tests**
- Full output: [`docs/test-output.txt`](test-output.txt)
- Run commit: `6b6bb8b058c0f272f9026ad2741b2045dd99b007`

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

## Additional integration coverage (to reach 14 mapped cases)

| # | Scenario from the integration task | Passing test(s) | Result |
|---|---|---|---|
| 11 | Note on a resolved ticket is rejected without changing ticket state | `test_resolved_ticket_rejects_notes_without_mutation` (`tests/test_notes.py`, `TestNotes`) | Pass |
| 12 | Notes remain intact through resolution and reopening; notes can be added after reopening | `test_notes_survive_resolve_and_reopen` (`tests/test_notes.py`, `TestNotes`) | Pass |
| 13 | Combined text, category, and status search applies all filters | `test_text_category_status_all_combined` (`tests/test_search.py`, `TestFilters`) | Pass |
| 14 | Empty and filled reports return the expected counts | `test_empty_list_includes_every_group_with_zero` and `test_known_fixture_gives_exact_counts` (`tests/test_reports.py`, `TestReportInsights`) | Pass |

## Manual checks

Record actual steps and observations. Do not mark a check complete until performed on this branch.

- [x] **Full lifecycle:** In the temporary working directory, created `T001` (`Damage`, Network, medium urgency, 6 users; priority `medium`), assigned it to `mr John`, moved it through `in_progress` and `resolved`, then reopened it to `open`. All valid operations reported success. An initial assignment using lowercase `t001` was rejected as unknown; retrying with `T001` succeeded.
- [ ] **Notes:** Add and view a note; resolve the ticket; attempt another note and confirm rejection; reopen it, add a note, and confirm both earlier notes remain.
- [ ] **Combined search:** Search using text plus category/status filters; confirm only tickets matching every selected filter appear.
- [ ] **Reports:** View the report with no tickets, then with representative tickets in each status/priority; record the displayed counts.
- [x] **Restart persistence:** After saving and restarting the CLI in the temporary working directory, chose **List tickets**. It displayed `T001 | Damage | medium | open | mr John`, confirming the ticket, status, and assignee persisted. Notes persistence across restart remains to be checked with the notes scenario.
- [ ] **Corrupted file:** Use a temporary copy containing invalid JSON; confirm a clear error and that the file contents are unchanged.
- [ ] **Duplicate-ID file:** Use a temporary JSON file with duplicate ticket IDs; confirm it is rejected and unchanged.
- [ ] **Original Open Work Queue:** Confirm it shows only `open` tickets (covered automatically by `test_includes_only_open_tickets` and `test_queue_excludes_in_progress_and_resolved` in `tests/test_reports.py` / `tests/test_search.py`).

## Invalid input and unchanged-state evidence

- Ticket creation: `test_failed_creation_leaves_list_unchanged` (`tests/test_tickets.py`).
- Notes: `test_resolved_ticket_rejects_notes_without_mutation` and invalid note-input tests (`tests/test_notes.py`).
- Workflow: `test_invalid_transition_leaves_entire_collection_unchanged` and `test_unassigned_cannot_start_progress` (`tests/test_workflow.py`).
- Search/report are read-only: `test_search_leaves_collection_unchanged` and `test_report_does_not_modify_tickets`.
- Invalid storage input: `test_corrupt_json_rejected_and_file_unchanged`, `test_duplicate_ticket_id_rejected`, and other `TestRejectedFiles` cases (`tests/test_storage.py`).

## Authorship and defects

- Test authorship: **Not yet verified.** Check PR/commit history and record at least five authored tests per engineer.
- Defects: **Not yet recorded.** Add each issue and its fix PR, or record `None found` after completing the checks.
- Final `main` commit SHA after all defect fixes merge: **Pending**.
