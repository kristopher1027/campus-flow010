"""Saving and loading tickets as JSON."""

import json
import os

DEFAULT_PATH = os.path.join("data", "tickets.json")


class StorageError(Exception):
    """Raised when tickets cannot be saved or loaded safely."""


def save_tickets(tickets, path=DEFAULT_PATH):
    """Write the tickets to a JSON file, creating the folder if needed.

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


def load_tickets(path=DEFAULT_PATH):
    """Return the list of tickets stored at path.

    A missing file means a fresh start, so it returns an empty list.
    A damaged or wrongly shaped file raises StorageError and is left untouched.
    """
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as error:
        raise StorageError(
            f"'{path}' is not valid JSON ({error}). "
            "The file has not been changed. Fix it or move it away to start fresh."
        ) from error
    except OSError as error:
        raise StorageError(f"Could not read '{path}': {error}") from error

    if not isinstance(data, list) or not all(isinstance(t, dict) for t in data):
        raise StorageError(
            f"'{path}' must contain a list of tickets. The file has not been changed."
        )

    seen_ids = []
    for ticket in data:
        ticket_id = ticket.get("id")
        if ticket_id is None:
            continue
        if ticket_id in seen_ids:
            raise StorageError(
                f"'{path}' contains duplicate ticket ID {ticket_id!r}. "
                "The file has not been changed."
            )
        seen_ids.append(ticket_id)

    return data
