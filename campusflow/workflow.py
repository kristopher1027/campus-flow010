
"""Ticket assignment and lifecycle transition rules."""

ALLOWED_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": {"open"},
}


def can_transition(current, new):
    """Return whether a status transition is allowed."""
    return new in ALLOWED_TRANSITIONS.get(current, set())


def _find_ticket(tickets, ticket_id):
    """Find a ticket by ID or raise ValueError."""
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise ValueError(f"Unknown ticket ID: {ticket_id}")


def assign_ticket(tickets, ticket_id, staff_name):
    """Assign a non-resolved ticket to a staff member."""
    ticket = _find_ticket(tickets, ticket_id)

    if ticket["status"] == "resolved":
        raise ValueError(
            "Cannot assign a resolved ticket. Reopen it first."
        )

    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff name must be non-blank text.")

    ticket["assigned_to"] = staff_name.strip()
    return ticket


def transition_status(tickets, ticket_id, new_status):
    """Apply a valid ticket status transition without partial mutation."""
    ticket = _find_ticket(tickets, ticket_id)
    current = ticket["status"]

    if not can_transition(current, new_status):
        raise ValueError(f"Invalid transition: {current} -> {new_status}")

    if current == "open" and new_status == "in_progress":
        if not ticket["assigned_to"]:
            raise ValueError(
                "Cannot start an unassigned ticket. Assign it first."
            )

    ticket["status"] = new_status
    return ticket
