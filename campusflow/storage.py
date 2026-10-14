"""Saving and loading tickets as JSON, with full validation on load."""

import json
import os
import re

from campusflow.tickets import (
    ALLOWED_CATEGORIES,
    ALLOWED_URGENCIES,
    calculate_priority,
)

DEFAULT_PATH = os.path.join("data", "tickets.json")

REQUIRED_KEYS = (
    "id", "title", "category", "urgency", "affected_users",
    "priority", "status", "assigned_to", "notes",
)
NOTE_KEYS = {"note_id", "author", "message"}
VALID_STATUSES = ("open", "in_progress", "resolved")
VALID_PRIORITIES = ("critical", "high", "medium", "low")
TICKET_ID_PATTERN = re.compile(r"T\d{3,}")
NOTE_ID_PATTERN = re.compile(r"N\d{3,}")


class StorageError(Exception):
    """Raised when tickets cannot be saved or loaded safely."""


def save_tickets(tickets, path=DEFAULT_PATH):
    """Write every ticket field (including notes) to a JSON file.

    Writes to a temporary file first, then replaces the real file, so a
    crash halfway through cannot leave a half-written tickets file.
    """
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    temp_path = path + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(tickets, f, indent=2)
        os.replace(temp_path, path)
    except (OSError, TypeError) as error:
        raise StorageError(f"Could not save tickets to '{path}': {error}") from error


def _check_notes(ticket):
    """Raise StorageError if the notes of this ticket are invalid."""
    ticket_id = ticket["id"]
    notes = ticket["notes"]
    if not isinstance(notes, list):
        raise StorageError(f"{ticket_id}: notes must be a list.")

    seen = set()
    for note in notes:
        if not isinstance(note, dict) or set(note) != NOTE_KEYS:
            raise StorageError(
                f"{ticket_id}: each note must have exactly note_id, author and message."
            )
        note_id = note["note_id"]
        if not isinstance(note_id, str) or not NOTE_ID_PATTERN.fullmatch(note_id):
            raise StorageError(f"{ticket_id}: invalid note ID {note_id!r}.")
        if note_id in seen:
            raise StorageError(f"{ticket_id}: duplicate note ID {note_id}.")
        seen.add(note_id)
        for field in ("author", "message"):
            if not isinstance(note[field], str) or note[field].strip() == "":
                raise StorageError(f"{ticket_id}: note {note_id} has a blank {field}.")


def _check_ticket(ticket, position):
    """Raise StorageError if this one ticket is invalid."""
    where = f"Ticket #{position + 1}"
    if not isinstance(ticket, dict):
        raise StorageError(f"{where} is not an object.")

    # Old v1 tickets had no notes field. Give them an empty list.
    ticket.setdefault("notes", [])

    missing = [key for key in REQUIRED_KEYS if key not in ticket]
    if missing:
        raise StorageError(f"{where} is missing: {', '.join(missing)}.")

    ticket_id = ticket["id"]
    if not isinstance(ticket_id, str) or not TICKET_ID_PATTERN.fullmatch(ticket_id):
        raise StorageError(f"{where} has an invalid ID {ticket_id!r}.")

    if not isinstance(ticket["title"], str) or ticket["title"].strip() == "":
        raise StorageError(f"{ticket_id}: title is blank.")
    if ticket["category"] not in ALLOWED_CATEGORIES:
        raise StorageError(f"{ticket_id}: invalid category {ticket['category']!r}.")
    if ticket["urgency"] not in ALLOWED_URGENCIES:
        raise StorageError(f"{ticket_id}: invalid urgency {ticket['urgency']!r}.")
    if ticket["status"] not in VALID_STATUSES:
        raise StorageError(f"{ticket_id}: invalid status {ticket['status']!r}.")
    if ticket["priority"] not in VALID_PRIORITIES:
        raise StorageError(f"{ticket_id}: invalid priority {ticket['priority']!r}.")

    users = ticket["affected_users"]
    if isinstance(users, bool) or not isinstance(users, int) or users <= 0:
        raise StorageError(f"{ticket_id}: affected_users must be a positive whole number.")

    expected = calculate_priority(ticket["urgency"], users)
    if ticket["priority"] != expected:
        raise StorageError(
            f"{ticket_id}: priority is '{ticket['priority']}' but urgency and "
            f"affected users give '{expected}'."
        )

    assignee = ticket["assigned_to"]
    if assignee is not None and (not isinstance(assignee, str) or assignee.strip() == ""):
        raise StorageError(f"{ticket_id}: assigned_to must be a name or null.")
    if ticket["status"] == "in_progress" and assignee is None:
        raise StorageError(f"{ticket_id}: an in_progress ticket must have an assignee.")

    _check_notes(ticket)


def validate_collection(data):
    """Check the whole collection. Return it, or raise StorageError."""
    if not isinstance(data, list):
        raise StorageError("The file must contain a list of tickets.")

    seen_ids = set()
    for position, ticket in enumerate(data):
        _check_ticket(ticket, position)
        if ticket["id"] in seen_ids:
            raise StorageError(f"Duplicate ticket ID {ticket['id']}.")
        seen_ids.add(ticket["id"])
    return data


def load_tickets(path=DEFAULT_PATH):
    """Return the validated list of tickets stored at path.

    A missing file means a fresh start, so it returns an empty list.
    A damaged or invalid file raises StorageError and is never modified.
    """
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except ValueError as error:   # JSONDecodeError and UnicodeDecodeError
        raise StorageError(
            f"'{path}' is not valid JSON ({error}). "
            "The file has not been changed. Fix it or move it away to start fresh."
        ) from error
    except OSError as error:
        raise StorageError(f"Could not read '{path}': {error}") from error

    try:
        return validate_collection(data)
    except StorageError as error:
        raise StorageError(f"{error} The file has not been changed.") from error