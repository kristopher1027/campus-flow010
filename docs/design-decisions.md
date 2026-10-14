# Design Decisions — CampusFlow

This document records the data and workflow choices reflected in the current implementation on `main`.

## 1. Data structure

The application keeps tickets in a single in-memory `list[dict]` named `tickets`. Each ticket has these nine fields:

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
| `notes` | `list[dict]` | Per-ticket follow-up notes with an ID, author, and message |

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
- Current JSON files contain a list of ticket objects with `id`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`, `assigned_to`, and `notes`. Notes are objects with exactly `note_id`, `author`, and `message`; `assigned_to` may be JSON `null`.
- Legacy v1 tickets without a `notes` field remain supported and load with `notes: []`. Other missing required fields are invalid.
- Loading validates the whole collection before returning it. Invalid JSON or invalid ticket data raises `StorageError`; the failed load does not overwrite the source file or replace the caller's existing in-memory collection.
- Saving creates the parent directory if needed, writes pretty-printed JSON to a temporary `.tmp` file, and uses `os.replace` to replace the target after the write.
- The real data file is ignored by Git. Tests use temporary directories/files so they do not alter a developer's real ticket data.

**Implementation:** `campusflow/storage.py`, `.gitignore`, `tests/test_storage.py`.

## 4. ID rule

`generate_next_id(tickets)` finds the highest numeric suffix among existing ticket IDs and adds one, formatted with at least three digits (`T001`, `T002`, …, `T010`). It does not use the list length, which could create duplicate IDs if IDs are not contiguous. Existing IDs must follow the `T`-prefixed positive-number format and must be unique. Malformed or duplicate IDs raise `ValueError` before a new ticket is appended. Since the full list is loaded before new tickets are created, IDs continue after a normal save/reload cycle.

**Implementation:** `campusflow/tickets.py`; coverage includes ID boundaries and creating a ticket after reloading in `tests/test_tickets.py` and `tests/test_storage.py`.

## 5. Allowed status transitions

`transition_status` permits only the following transitions:

| From | To | Condition |
|---|---|---|
| `open` | `in_progress` | Ticket must be assigned |
| `in_progress` | `resolved` | Allowed |
| `resolved` | `open` | Explicitly reopens the ticket |
| Any other pair | — | Rejected with `ValueError` |


The explicit reopen step prevents a resolved ticket from skipping the defined workflow. Resolved tickets cannot be assigned until they are reopened. Assignment and transition functions validate all applicable rules before mutation; rejected operations raise `ValueError` and leave the ticket collection unchanged.

**Implementation:** `campusflow/workflow.py`, `tests/test_workflow.py`.

## 6. Work queue decision

`work_queue(tickets)` includes only tickets whose status is `open`; `in_progress` and `resolved` tickets are excluded. The queue sorts by priority (`critical`, `high`, `medium`, `low`) and then by numeric ticket ID ascending so older/lower-numbered tickets appear first within the same priority.

The function returns a sorted list without sorting the original ticket collection in place.

**Implementation:** `campusflow/reports.py`, `tests/test_reports.py`.

### Engineer B bug-hunter case (Issue #24)

- **Initial state:** Two same-priority tickets are in the work list, ordered as `T10`, then `T2`.
- **Input:** Call `work_queue(tickets)` with both tickets at priority `high`.
- **Expected result:** The returned queue orders them numerically as `T2`, `T10`; the original input list remains `T10`, `T2`.
- **Actual result:** `test_tie_break_handles_unpadded_numeric_ids` passes with that order, and confirms the original list is unchanged.
- **Test name:** `test_tie_break_handles_unpadded_numeric_ids` in `tests/test_reports.py`.
- **Code change:** Added this regression test; no production code change was needed because `work_queue` already sorts by the numeric ID suffix.

## 7. Normalization

- Ticket titles are stripped of leading/trailing whitespace and must not be blank.
- Category input is stripped and compared case-insensitively; stored/displayed values use canonical names such as `Network`.
- Urgency input is stripped and normalized to lowercase.
- `affected_users` must be a strictly positive Python `int`. Booleans, floats, strings, zero, and negative values are rejected by validation. The CLI is responsible for converting valid numeric text to an integer before calling the validator.
- Staff names are stripped and cannot be blank.
- Ticket lookup in `campusflow/tickets.py` accepts ID case/whitespace variations. The assignment and status functions currently compare IDs exactly, so the CLI should use the canonical ticket ID when assigning or changing status.

**Implementation:** `campusflow/tickets.py`, `campusflow/workflow.py`, `tests/test_tickets.py`, `tests/test_workflow.py`.

## Ownership summary

| Area | Contribution |
|---|---|
| Ticket creation, validation, priority engine, ID generation | Engineer A |
| Assignment, workflow, queue, reports | Engineer B |
| Storage integration and CLI entry point | Shared integration work |

## Cross-engineer edge-case check

- **Initial state:** An empty ticket list; no ticket has been created yet.
- **Input:** Create a ticket with U+00A0 non-breaking spaces around `Network issue`, category `Network`, urgency `low`, and one affected user.
- **Expected result:** Leading and trailing Unicode whitespace is stripped, leaving the stored title `Network issue`.
- **Actual result:** `create_ticket` returned a ticket with title `Network issue`.
- **Test name:** `test_unicode_whitespace_around_title_is_stripped` in `tests/test_tickets.py`.
- **Code change:** No production code change was needed; the new regression test makes Unicode whitespace normalization explicit.

This edge case supplements the standard title checks by testing non-breaking spaces rather than ordinary spaces. Share this result with Engineer A as a focused review note.

Relevant implementation history: [PR #13 — ticket creation](https://github.com/kristopher1027/campus-flow/pull/13), [PR #12 — assignment/workflow/queue/reports](https://github.com/kristopher1027/campus-flow/pull/12), [PR #18 — JSON storage](https://github.com/kristopher1027/campus-flow/pull/18), and [PR #19 — CLI menu](https://github.com/kristopher1027/campus-flow/pull/19).


## Ticket Notes (Issue #21)

### `next_note_id(ticket)`

Returns the next sequential note ID for a ticket, using the format `N001`, `N002`, and so on. IDs are generated independently for each ticket and continue from the highest existing note ID.

Raises `ValueError` if the ticket's notes collection or existing note IDs are invalid.

### `add_note(tickets, ticket_id, author, message)`

Adds a note to an existing ticket and returns the new note dictionary:

- `note_id`: sequential per-ticket ID, such as `N001`.
- `author`: author name, trimmed of surrounding whitespace.
- `message`: note content, trimmed of surrounding whitespace.

**Validation rules**

- The ticket must exist.
- The ticket status must be `open` or `in_progress`.
- The author must be a non-blank string.
- The trimmed message must contain between 5 and 300 characters, inclusive.
- The ticket's notes collection must be a list.

**Errors and mutation behavior**

Raises `ValueError` when the ticket cannot be found, the ticket status does not allow notes, or the input or existing notes data is invalid.

Validation occurs before appending a note. Rejected notes do not change the ticket's notes collection or consume a note ID.

Notes remain attached to their ticket when its status changes, including when the ticket is resolved and later reopened. A resolved ticket must be reopened before additional notes can be added.

### CLI integration contract

The CLI can call `add_note(tickets, ticket_id, author, message)`. On success, it receives the created note dictionary. It should catch `ValueError` and display a clear error message to the user.
