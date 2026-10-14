# CampusFlow Demo Script

This short walkthrough demonstrates ticket creation, priority, assignment, workflow, notes, combined search, reports, and the Open Work Queue. It uses a temporary working directory so the demo does not change `data/tickets.json` in the project.

## Start with a clean demo file

From the repository root:

```bash
PROJECT_DIR="$(pwd)"
DEMO_DIR="$(mktemp -d)"
cd "$DEMO_DIR"
PYTHONPATH="$PROJECT_DIR" python3 "$PROJECT_DIR/main.py"
```

The app creates `$DEMO_DIR/data/tickets.json` as tickets are saved. To run the demo again, exit the app and use a new temporary directory.

## Walkthrough

1. Choose **1 — Create ticket**:
   - Title: `Library Wi-Fi outage`
   - Category: `Network`
   - Urgency: `high`
   - Affected users: `12`
   - Expected: `Created ticket T001 with priority critical.`
2. Choose **6 — Work Queue**. The queue should contain `T001` because its status is `open`.
3. Choose **4 — Assign ticket**, enter `T001`, and assign it to `Moses`.
4. Choose **5 — Change status**, enter `T001`, and set `in_progress`.
5. Choose **6 — Work Queue** again. The queue should be empty because it includes only `open` tickets.
6. Choose **8 — Add Follow-up Note**, enter `T001`, author `Moses`, and message `Router reboot attempted`.
7. Choose **9 — View Ticket Notes** for `T001`. Confirm note `N001` appears.
8. Choose **10 — Search Tickets** and enter:
   - Title text: `Wi-Fi`
   - Category: `Network`
   - Status: `in_progress`
   - Priority: `critical`
   - Expected: one matching ticket, `T001`.
9. Choose **7 — Report**. Expected counts include one total ticket, one `in_progress`, one `critical`, one `Network`, and a `0.0%` resolution rate.
10. Choose **5 — Change status**, move `T001` to `resolved`, then choose **13 — Save and exit**.

## Expected results

- The priority rule assigns `critical` to a high-urgency ticket affecting 12 users.
- The ticket leaves the Open Work Queue when moved to `in_progress`.
- The note is saved and displayed with ID `N001`.
- Combined search returns only tickets matching every supplied filter.
- The report reflects the ticket's current status, priority, and category.
- Exiting saves the demo data under the temporary directory.
