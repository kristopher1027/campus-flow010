
"""Create, validate, and retrieve ticket follow-up notes."""

from campusflow.tickets import find_ticket


def add_note(notes, tickets, ticket_id, text):
    """Add a note to an existing ticket."""
    ticket = find_ticket(tickets, ticket_id)

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Note cannot be empty.")

    next_id = max(
        (note["id"] for note in notes),
        default=0,
    ) + 1

    note = {
        "id": next_id,
        "ticket_id": ticket["id"],
        "text": text.strip(),
    }

    notes.append(note)
    return note


def get_notes(notes, tickets, ticket_id):
    """Return notes for an existing ticket in ID order."""
    ticket = find_ticket(tickets, ticket_id)

    return sorted(
        [
            note for note in notes
            if note["ticket_id"] == ticket["id"]
        ],
        key=lambda note: note["id"],
    )
    