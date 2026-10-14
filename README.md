# CampusFlow

CampusFlow is a Python command-line helpdesk for managing campus IT support tickets. It helps a small support team record requests, calculate their priority, assign staff, track work, and review a summary of open and resolved tickets.

## Problem statement

Campus IT requests such as Wi-Fi outages, faulty laptops, and inaccessible software can arrive through informal channels. Without a shared record, requests can be missed, urgency can be inconsistent, and staff may not know who is responsible. CampusFlow provides a lightweight, local ticket list and a repeatable workflow.

## Fellows and contributions

- **Kristopher Okoh (Engineer A):** ticket creation and validation, priority calculation, ticket IDs, JSON storage, and project documentation.
- **Moses Attah(Engineer B):** ticket assignment, status transitions, prioritized work queue, and ticket reports.
- **Shared work:** integration through the CLI, tests, and review of the combined behavior.

Relevant merged pull requests:
- Engineer A — [Ticket creation and validation, PR #13](https://github.com/kristopher1027/campus-flow/pull/13) and [priority engine, PR #15](https://github.com/kristopher1027/campus-flow/pull/15).
- Engineer B — [Assignment, workflow, queue and reports, PR #12](https://github.com/kristopher1027/campus-flow/pull/12) and [ticket summary reports, PR #17](https://github.com/kristopher1027/campus-flow/pull/17).
- Shared integration — [JSON storage, PR #18](https://github.com/kristopher1027/campus-flow/pull/18) and [CLI menu, PR #19](https://github.com/kristopher1027/campus-flow/pull/19).

## Requirements

- Python 3.10 or later (project target).
- No third-party packages; the application uses Python's standard library.

## Run the application

From the repository root:

```bash
python3 --version
python3 main.py
```

The menu lets you create, list, and view tickets; assign a ticket; change its status; display the work queue; view a report; or exit. Enter the number for the action you want and follow the prompts.

## Run the tests

From the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The tests use Python's built-in `unittest` framework. The committed integration test output records **59 tests passing** on the documented `main` revision; run the command above to verify the current checkout.

## Priority rules

Priority is calculated by `calculate_priority()` in `campusflow/tickets.py`. Rules are evaluated in order; the first matching rule wins.

| Condition | Priority |
|---|---|
| Urgency is high **and** at least 10 users are affected | critical |
| Urgency is high **or** at least 10 users are affected | high |
| Urgency is medium **or** at least 3 users are affected | medium |
| None of the above | low |

A ticket must have a non-blank title, a supported category (`Network`, `Hardware`, `Software`, or `Other`), a supported urgency (`low`, `medium`, or `high`), and a positive whole number of affected users.

## Status workflow

The workflow is enforced by `transition_status()` in `campusflow/workflow.py`.

| Current status | Next status | Rule |
|---|---|---|
| `open` | `in_progress` | Allowed only after the ticket has an assignee |
| `in_progress` | `resolved` | Allowed |
| `resolved` | `open` | Allowed to explicitly reopen the ticket |
| Any other transition | — | Rejected with `ValueError` |

Resolved tickets must be reopened before they can return to work. The work queue contains only `open` and `in_progress` tickets, sorted by priority (critical first) and then by numeric ticket ID ascending.

## Where ticket data is saved

The application stores tickets as JSON in `data/tickets.json`, configured by `DEFAULT_PATH` in `campusflow/storage.py`. The `data/tickets.json` file is ignored by Git so local ticket data is not committed.

Each file contains a JSON list of ticket objects. Current records include `id`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`, `assigned_to`, and `notes`. `assigned_to` is either a staff name or JSON `null`; `notes` is a list of objects with `note_id`, `author`, and `message`. The loader validates the entire list and rejects invalid records rather than returning a partially loaded collection. Legacy v1 records that omit `notes` are supported and load with `notes: []`; files with the current notes field use the current format.

- The data directory is created when saving if it does not exist.
- On startup, if the file is missing, CampusFlow starts with an empty ticket list.
- To start fresh, **stop the application first**, then remove the file:

  ```bash
  rm -f data/tickets.json
  ```

- If the file contains invalid JSON or the wrong top-level structure, loading raises `StorageError`; the file is not silently replaced with an empty list. Fix or move the damaged file before restarting.

## Known limitations

- Tickets are stored locally in one JSON file; there is no database, authentication, or multi-user concurrency control.
- Running multiple instances at once can cause one instance to overwrite another instance's changes.
- Priority rules are fixed in code and cannot be configured through the CLI.
- Only the current ticket status is stored; there is no audit trail or status-change history.
- Keyboard interruption and end-of-file are handled at the menu prompt, but interruption during a feature's prompts is not handled by the same exit path.
- Storage errors stop startup, but the CLI does not yet provide a dedicated recovery screen; Python may display a traceback.

## Project documentation

- [Design decisions](docs/design-decisions.md)
- [AI learning log](docs/ai-learning-log.md)
