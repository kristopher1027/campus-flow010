# CampusFlow

CampusFlow is a local Python command-line helpdesk for campus IT support. It records requests, calculates priority, assigns staff, tracks ticket status, stores follow-up notes, supports search, and reports ticket counts.

## Problem

Campus IT requests such as Wi-Fi outages, faulty laptops, and inaccessible software can arrive through informal channels. Without a shared record, requests can be missed, urgency can be inconsistent, and staff may not know who is responsible. CampusFlow provides a small, repeatable workflow backed by a local JSON file.

## Engineers and contributions

- **Christopher Okoh (Engineer A):** ticket creation and validation, priority calculation, ticket IDs, JSON storage and validation, and follow-up notes.
- **Moses Attah (Engineer B):** assignment, status transitions, the original Open Work Queue, and ticket reports.
- **Musa Ogeh (Fellow C):** read-only search and priority-sorted results, report insights, CLI interaction tests, the understanding check, and follow-up regression checks.
- **Shared:** CLI integration, integration tests, and review of combined behavior.

Repository: [kristopher1027/campus-flow010](https://github.com/kristopher1027/campus-flow010).

Key merged feature PRs:

- Engineer A — [PR #36: validation and notes](https://github.com/kristopher1027/campus-flow010/pull/36).
- Fellow C — [PR #37: search and insights](https://github.com/kristopher1027/campus-flow010/pull/37).

Earlier feature history: [ticket creation, PR #13](https://github.com/kristopher1027/campus-flow010/pull/13), [priority engine, PR #15](https://github.com/kristopher1027/campus-flow010/pull/15), [workflow and queue, PR #12](https://github.com/kristopher1027/campus-flow010/pull/12), [reports, PR #17](https://github.com/kristopher1027/campus-flow010/pull/17), [JSON storage, PR #18](https://github.com/kristopher1027/campus-flow010/pull/18), and [CLI menu, PR #19](https://github.com/kristopher1027/campus-flow010/pull/19).

## Requirements

- Python 3.10 or later.
- No third-party packages are needed; the app and tests use Python's standard library.

## Get a fresh copy

```bash
git clone https://github.com/kristopher1027/campus-flow010.git
cd campus-flow010
```

## Run the application

From the repository root (the `campus-flow010` directory after cloning):

```bash
python3 --version
python3 main.py
```

The menu actions are:

| Choice | Action |
|---|---|
| 1 | Create ticket |
| 2 | List tickets |
| 3 | View ticket details |
| 4 | Assign ticket |
| 5 | Change ticket status |
| 6 | Show the Open Work Queue |
| 7 | Show the report |
| 8 | Add a follow-up note |
| 9 | View ticket notes |
| 10 | Search tickets |
| 11 | Show search results sorted by priority |
| 12 | Take the understanding check |
| 13 | Save and exit |

## Run the tests

From the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The project uses Python's built-in `unittest` framework. See [`docs/test-output.txt`](docs/test-output.txt) for the saved integration run; rerun the command above after changing code.

## Priority rules

Rules are checked in this order:

| Condition | Priority |
|---|---|
| Urgency is `high` and at least 10 users are affected | `critical` |
| Urgency is `high` or at least 10 users are affected | `high` |
| Urgency is `medium` or at least 3 users are affected | `medium` |
| Otherwise | `low` |

Titles must be non-blank. Category must be `Network`, `Hardware`, `Software`, or `Other`; urgency must be `low`, `medium`, or `high`; affected users must be a positive whole number. Category and urgency input is normalized for case and surrounding whitespace.

## Status and work queue

| Current status | Next status | Rule |
|---|---|---|
| `open` | `in_progress` | Allowed only when the ticket is assigned |
| `in_progress` | `resolved` | Allowed |
| `resolved` | `open` | Explicitly reopens the ticket |

Other transitions are rejected. The Open Work Queue includes only `open` tickets, sorted by priority (`critical`, `high`, `medium`, `low`) and then by numeric ticket ID ascending. `in_progress` and `resolved` tickets are excluded.

## Follow-up notes

Notes can be added to `open` or `in_progress` tickets. A note has a per-ticket ID (`N001`, `N002`, …), a non-blank author, and a message from 5 through 300 characters after trimming whitespace. Notes cannot be added while a ticket is resolved. Reopening the ticket allows new notes; existing notes remain attached. Invalid note requests do not change the ticket or consume a note ID.

## Search

Search can filter by title text, category, status, and priority. Title search matches a case-insensitive substring. Category, status, and priority filters are exact matches that ignore case and surrounding whitespace. Multiple supplied filters are combined with AND; blank filters are ignored. Search returns a new result list without changing the tickets. The sorted-search menu action orders matches by priority (`critical` first) and then numeric ticket ID.

## JSON data and persistence

Ticket data is saved in `data/tickets.json`, relative to the directory from which `main.py` is run. A missing file starts the app with an empty ticket list. The data directory is created on save. The file is ignored by Git.

A current ticket record has this shape:

```json
[
  {
    "id": "T001",
    "title": "Wi-Fi down",
    "category": "Network",
    "urgency": "high",
    "affected_users": 12,
    "priority": "critical",
    "status": "open",
    "assigned_to": null,
    "notes": [
      {
        "note_id": "N001",
        "author": "Alex",
        "message": "Router restarted"
      }
    ]
  }
]
```

The top level must be a JSON list. The loader validates the full file, including ticket fields, IDs, priority consistency, and note structure. Invalid JSON or invalid ticket data raises `StorageError`; the file is left unchanged rather than silently reset. Legacy v1 ticket records that omit `notes` load with `notes: []`; other required fields must still be present.

To start fresh, stop the app and remove its data file from the repository root:

```bash
rm -f data/tickets.json
```

## Known limitations

- Data is stored locally in one JSON file; there is no database, authentication, or multi-user write coordination.
- Running multiple app instances at once can cause one instance to overwrite another's changes.
- Priority rules are fixed in code and cannot be configured through the CLI.
- Only the current status is stored; there is no status-change audit history.
- Storage errors stop normal operation; the CLI has no dedicated recovery screen.
- Keyboard interruption and end-of-file are handled at the main menu, but not uniformly during every feature prompt.

## Project documentation

- [Design decisions](docs/design-decisions.md)
- [Baseline check](docs/baseline-check.md)
- [Integration checklist](docs/integration-checklist.md)
- [Demo script](docs/demo-script.md)
- [AI learning log](docs/ai-learning-log.md)
