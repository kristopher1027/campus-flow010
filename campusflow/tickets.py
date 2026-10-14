"""Ticket creation, validation and priority logic for CampusFlow."""

ALLOWED_CATEGORIES = ("Network", "Hardware", "Software", "Other")
ALLOWED_URGENCIES = ("low", "medium", "high")


def calculate_priority(urgency, affected_users):
    """Return critical/high/medium/low. Rules are checked in order; first match wins."""
    if urgency == "high" and affected_users >= 10:
        return "critical"
    if urgency == "high" or affected_users >= 10:
        return "high"
    if urgency == "medium" or affected_users >= 3:
        return "medium"
    return "low"

def validate_title(title):
    """Return the stripped title. Raise ValueError if blank or not a string."""
    if not isinstance(title, str):
        raise ValueError("Title must be text.")
    cleaned = title.strip()
    if cleaned == "":
        raise ValueError("Title cannot be blank.")
    return cleaned


def validate_category(category):
    """Return the properly capitalised category (e.g. ' network ' -> 'Network')."""
    if not isinstance(category, str):
        raise ValueError("Category must be text.")
    cleaned = category.strip().lower()
    for allowed in ALLOWED_CATEGORIES:
        if allowed.lower() == cleaned:
            return allowed
    raise ValueError(
        "Category must be one of: " + ", ".join(ALLOWED_CATEGORIES) + "."
    )


def validate_urgency(urgency):
    """Return the lowercase urgency (e.g. ' HIGH ' -> 'high')."""
    if not isinstance(urgency, str):
        raise ValueError("Urgency must be text.")
    cleaned = urgency.strip().lower()
    if cleaned not in ALLOWED_URGENCIES:
        raise ValueError(
            "Urgency must be one of: " + ", ".join(ALLOWED_URGENCIES) + "."
        )
    return cleaned



def validate_affected_users(value):
    """Accept only a strictly positive integer, excluding booleans."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("Affected users must be a positive integer.")

    if value <= 0:
        raise ValueError("Affected users must be greater than zero.")

    return value



def validate_ticket(ticket):
    """Validate a ticket's shape and values without modifying it."""
    required_fields = {
        "id",
        "title",
        "category",
        "urgency",
        "affected_users",
        "priority",
        "status",
        "assigned_to",
    }

    if not isinstance(ticket, dict):
        raise ValueError("Ticket must be a dictionary.")

    missing = required_fields - ticket.keys()
    if missing:
        raise ValueError(
            "Ticket is missing required fields: "
            + ", ".join(sorted(missing)) + "."
        )

    ticket_id = ticket["id"]
    if (
        not isinstance(ticket_id, str)
        or len(ticket_id) < 2
        or ticket_id[0] != "T"
        or not ticket_id[1:].isdigit()
        or int(ticket_id[1:]) <= 0
    ):
        raise ValueError(
            "Ticket ID must use the format T001 with a positive number."
        )

    validate_title(ticket["title"])
    validate_category(ticket["category"])
    validate_urgency(ticket["urgency"])
    validate_affected_users(ticket["affected_users"])

    allowed_statuses = ("open", "in_progress", "resolved")
    if ticket["status"] not in allowed_statuses:
        raise ValueError(
            "Status must be one of: " + ", ".join(allowed_statuses) + "."
        )

    assignee = ticket["assigned_to"]
    if assignee is not None and (
        not isinstance(assignee, str) or not assignee.strip()
    ):
        raise ValueError(
            "Assigned staff name must be non-blank text or None."
        )

    expected_priority = calculate_priority(
        ticket["urgency"], ticket["affected_users"]
    )
    if ticket["priority"] != expected_priority:
        raise ValueError(
            f"Priority must be '{expected_priority}' for this urgency "
            "and affected-user count."
        )

    return ticket



def generate_next_id(tickets):
    """Return the next ID after validating all existing ticket IDs."""
    seen_ids = set()
    highest = 0

    for ticket in tickets:
        if not isinstance(ticket, dict):
            raise ValueError("Every ticket must be a dictionary.")

        ticket_id = ticket.get("id")

        if (
            not isinstance(ticket_id, str)
            or len(ticket_id) < 2
            or ticket_id[0] != "T"
            or not ticket_id[1:].isascii()
            or not ticket_id[1:].isdigit()
            or int(ticket_id[1:]) <= 0
        ):
            raise ValueError(
                "Ticket ID must use the format T001 with a positive number."
            )

        if ticket_id in seen_ids:
            raise ValueError(f"Duplicate ticket ID '{ticket_id}'.")

        seen_ids.add(ticket_id)
        highest = max(highest, int(ticket_id[1:]))

    return f"T{highest + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate everything, then build and append a ticket. Return the ticket."""
    # Validate first, into local variables. If any call raises, the list is untouched.
    title = validate_title(title)
    category = validate_category(category)
    urgency = validate_urgency(urgency)
    affected_users = validate_affected_users(affected_users)

    priority = calculate_priority(urgency, affected_users)
    new_id = generate_next_id(tickets)

    ticket = {
        "id": new_id,
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": affected_users,
        "priority": priority,
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }

    tickets.append(ticket)   # the very last step that touches the list
    return ticket

def find_ticket(tickets, ticket_id):
    """Return the ticket with this ID. Tolerates case and whitespace.

    Raise ValueError if the ID is not text or no ticket matches.
    """
    if not isinstance(ticket_id, str):
        raise ValueError("Ticket ID must be text, for example T001.")
    wanted = ticket_id.strip().upper()
    for ticket in tickets:
        if ticket["id"] == wanted:
            return ticket
    raise ValueError(f"No ticket found with ID '{ticket_id.strip()}'.")


def format_ticket_summary(ticket):
    """Return a one-line summary: ID | title | priority | status | assignee."""
    assignee = ticket["assigned_to"] or "Unassigned"
    return (
        f"{ticket['id']} | {ticket['title']} | {ticket['priority']} | "
        f"{ticket['status']} | {assignee}"
    )


def format_ticket_details(ticket):
    """Return a multi-line text showing all 8 fields of one ticket."""
    assignee = ticket["assigned_to"] or "Unassigned"
    lines = [
        f"ID:             {ticket['id']}",
        f"Title:          {ticket['title']}",
        f"Category:       {ticket['category']}",
        f"Urgency:        {ticket['urgency']}",
        f"Affected users: {ticket['affected_users']}",
        f"Priority:       {ticket['priority']}",
        f"Status:         {ticket['status']}",
        f"Assigned to:    {assignee}",
    ]
    return "\n".join(lines)


def format_ticket_list(tickets):
    """Return one summary line per ticket, or a friendly message if empty."""
    if not tickets:
        return "No tickets yet."
    return "\n".join(format_ticket_summary(t) for t in tickets)


def next_note_id(ticket):
    """Return the next per-ticket note ID, such as N001 or N002."""
    notes = ticket.get("notes", [])

    if not isinstance(notes, list):
        raise ValueError("Ticket notes must be a list.")

    highest = 0
    seen_ids = set()

    for note in notes:
        if not isinstance(note, dict):
            raise ValueError("Every note must be a dictionary.")

        note_id = note.get("note_id")

        if (
            not isinstance(note_id, str)
            or len(note_id) < 2
            or not note_id.startswith("N")
            or not note_id[1:].isascii()
            or not note_id[1:].isdigit()
            or int(note_id[1:]) <= 0
        ):
            raise ValueError("Note ID must use the format N001.")

        if note_id in seen_ids:
            raise ValueError(f"Duplicate note ID '{note_id}'.")

        seen_ids.add(note_id)
        highest = max(highest, int(note_id[1:]))

    return f"N{highest + 1:03d}"


def add_note(tickets, ticket_id, author, message):
    """Add a validated note to an open or in-progress ticket.

    Return the new note. Raise ValueError for invalid input or ticket state.
    Rejected notes do not mutate the ticket or consume a note ID.
    """
    ticket = find_ticket(tickets, ticket_id)

    if ticket.get("status") not in ("open", "in_progress"):
        raise ValueError("Cannot add a note to a resolved ticket.")

    if not isinstance(author, str):
        raise ValueError("Note author must be non-blank text.")

    author = author.strip()
    if not author:
        raise ValueError("Note author must be non-blank text.")

    if not isinstance(message, str):
        raise ValueError("Note message must contain 5–300 characters.")

    message = message.strip()
    if not 5 <= len(message) <= 300:
        raise ValueError("Note message must contain 5–300 characters.")

    notes = ticket.get("notes")
    if not isinstance(notes, list):
        raise ValueError("Ticket notes must be a list.")

    note_id = next_note_id(ticket)
    note = {
        "note_id": note_id,
        "author": author,
        "message": message,
    }

    notes.append(note)
    return note
