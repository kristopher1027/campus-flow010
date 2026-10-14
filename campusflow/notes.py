"""Read helpers for notes embedded on tickets."""

from campusflow.tickets import find_ticket, next_note_id


def get_notes(tickets, ticket_id):
    """Return a ticket's notes ordered by their numeric note ID."""
    ticket = find_ticket(tickets, ticket_id)
    return sorted(
        ticket.get("notes", []),
        key=lambda note: int(note["note_id"][1:]),
    )


__all__ = ["get_notes", "next_note_id"]
