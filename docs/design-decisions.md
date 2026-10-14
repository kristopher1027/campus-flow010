# Design Decisions — CampusFlow

This document records the data and workflow choices reflected in the current implementation on `main`.

## 1. Data structure

The application keeps tickets in a single in-memory `list[dict]` named `tickets`. Each ticket has these eight fields:

| Field | Type | Purpose |
|---|---|---|
| `id` | `str` | Sequential identifier such as `T001` |
| `title` | `str` | Non-blank description |
| `category` | `str` | `Network`, `Hardware`, `Software`, or `Other` |
| `urgency` | `str` | `low`, `medium`, or `high` |
| `affected_users` | `int` | Positive whole number |
| `priority` | `str` | Computed from urgency and affected users |
| `status` | `str` | `open`, `in_progress`, or `resolved` |
| `assigned_to` | `str` or `None` | Assigned staff member, or unassigned |

This structure is simple for a small, single-process CLI and maps directly to JSON. It does not provide database constraints or concurrent-write protection.

**Implementation:** `campusflow/tickets.py`, `campusflow/storage.py`.

## 2. Error handling

- Ticket validation, lookup, assignment, and invalid workflow transitions raise `ValueError`.
- The CLI handlers in `main.py` catch `ValueError` and print a readable message, then return to the menu.
- Storage operations use a separate `StorageError` for read/write failures, malformed JSON, and invalid top-level data structure.
- `main.py` does not catch `StorageError` at startup or around every save, so a storage failure currently stops normal CLI operation and may show a traceback. This avoids silently continuing with an empty ticket list after a damaged file, but a friendlier recovery path remains a limitation.
- Business logic is kept in modules so it can be tested without interactive input.

**Implementation:** `campusflow/tickets.py`, `campusflow/workflow.py`, `campusflow/storage.py`, `main.py`.

## 3. JSON ownership and persistence

All JSON file access belongs to `campusflow/storage.py`; other modules call `load_tickets` and `save_tickets` rather than reading or writing the file themselves.

- `DEFAULT_PATH` is `data/tickets.json`.
- If the file is missing, `load_tickets` returns an empty list to support a fresh start.
- Invalid JSON or a top-level value that is not a list of dictionaries raises `StorageError`; the failed load does not overwrite the source file.
- Saving creates the parent directory if needed, writes pretty-printed JSON to a temporary `.tmp` file, and uses `os.replace` to replace the target after the write.
- The real data file is ignored by Git. Tests use temporary directories/files so they do not alter a developer's real ticket data.

**Implementation:** `campusflow/storage.py`, `.gitignore`, `tests/test_storage.py`.

## 4. ID rule

`generate_next_id(tickets)` finds the highest numeric suffix among existing ticket IDs and adds one, formatted with at least three digits (`T001`, `T002`, …, `T010`). It does not use the list length, which could create duplicate IDs if IDs are not contiguous. Since the full list is loaded before new tickets are created, IDs continue after a normal save/reload cycle.

**Implementation:** `campusflow/tickets.py`; coverage includes ID boundaries and creating a ticket after reloading in `tests/test_tickets.py` and `tests/test_storage.py`.

## 5. Allowed status transitions

`transition_status` permits only the following transitions:

| From | To | Condition |
|---|---|---|
| `open` | `in_progress` | Ticket must be assigned |
| `in_progress` | `resolved` | Allowed |
| `resolved` | `open` | Explicitly reopens the ticket |
| Any other pair | — | Rejected with `ValueError` |

The explicit reopen step prevents a resolved ticket from skipping the defined workflow. Assignment and transition functions validate before changing the ticket.

**Implementation:** `campusflow/workflow.py`, `tests/test_workflow.py`.

## 6. Work queue decision

`work_queue(tickets)` includes only tickets whose status is `open`; `in_progress` and `resolved` tickets are excluded. The queue sorts by priority (`critical`, `high`, `medium`, `low`) and then by numeric ticket ID ascending so older/lower-numbered tickets appear first within the same priority.

The function returns a sorted list without sorting the original ticket collection in place.

**Implementation:** `campusflow/reports.py`, `tests/test_reports.py`.

## 7. Normalization

- Ticket titles are stripped of leading/trailing whitespace and must not be blank.
- Category input is stripped and compared case-insensitively; stored/displayed values use canonical names such as `Network`.
- Urgency input is stripped and normalized to lowercase.
- Affected users must be a positive whole number; booleans, floats, and non-numeric strings are rejected.
- Staff names are stripped and cannot be blank.
- Ticket lookup in `campusflow/tickets.py` accepts ID case/whitespace variations. The assignment and status functions currently compare IDs exactly, so the CLI should use the canonical ticket ID when assigning or changing status.

**Implementation:** `campusflow/tickets.py`, `campusflow/workflow.py`, `tests/test_tickets.py`, `tests/test_workflow.py`.

## Ownership summary

| Area | Contribution |
|---|---|
| Ticket creation, validation, priority engine, ID generation | Engineer A |
| Assignment, workflow, queue, reports | Engineer B |
| Storage integration and CLI entry point | Shared integration work |

Relevant implementation history: [PR #13 — ticket creation](https://github.com/kristopher1027/campus-flow/pull/13), [PR #12 — assignment/workflow/queue/reports](https://github.com/kristopher1027/campus-flow/pull/12), [PR #18 — JSON storage](https://github.com/kristopher1027/campus-flow/pull/18), and [PR #19 — CLI menu](https://github.com/kristopher1027/campus-flow/pull/19).
