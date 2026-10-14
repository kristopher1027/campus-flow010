
"""Ticket lookup, work queues, and reporting for CampusFlow."""

from campusflow.tickets import ALLOWED_CATEGORIES

PRIORITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
STATUS_ORDER = ("open", "in_progress", "resolved")
REPORT_PRIORITY_ORDER = ("critical", "high", "medium", "low")
REPORT_CATEGORY_ORDER = ALLOWED_CATEGORIES
UNRESOLVED_STATUSES = ("open", "in_progress")


def get_ticket(tickets, ticket_id):
    """Return a ticket by ID, or raise ValueError."""
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket
    raise ValueError(f"Unknown ticket ID: {ticket_id}")


def list_tickets(tickets):
    """Return the full ticket list."""
    return tickets


def work_queue(tickets):
    """Return open tickets sorted by priority and numeric ID."""
    queue = [
        ticket for ticket in tickets
        if ticket["status"] == "open"
    ]

    def sort_key(ticket):
        priority_rank = PRIORITY_ORDER.get(ticket["priority"], 99)
        try:
            numeric_id = int(ticket["id"][1:])
        except (ValueError, IndexError):
            numeric_id = 9999
        return priority_rank, numeric_id

    return sorted(queue, key=sort_key)


def generate_report(tickets):
    """Return counts and resolution insights using current ticket status."""
    by_status = {status: 0 for status in STATUS_ORDER}
    by_priority = {priority: 0 for priority in REPORT_PRIORITY_ORDER}
    by_category = {category: 0 for category in REPORT_CATEGORY_ORDER}

    for ticket in tickets:
        status = ticket["status"]
        priority = ticket["priority"]
        category = ticket["category"]

        if status in by_status:
            by_status[status] += 1

        if priority in by_priority:
            by_priority[priority] += 1

        if category in by_category:
            by_category[category] += 1

    total = len(tickets)
    unresolved = sum(by_status[s] for s in UNRESOLVED_STATUSES)
    resolved = by_status["resolved"]

    resolution_percentage = resolved / total * 100 if total else 0.0

    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "by_category": by_category,
        "unresolved": unresolved,
        "resolved": resolved,
        "resolution_percentage": resolution_percentage,
    }


def report_summary(tickets):
    """Keep compatibility with existing callers."""
    return generate_report(tickets)


def format_report(report):
    """Return a readable report string without printing."""
    lines = [
        "CampusFlow Ticket Report",
        f"Total tickets: {report['total']}",
        "",
        "By status:",
    ]

    for status in STATUS_ORDER:
        lines.append(f"  {status}: {report['by_status'][status]}")

    lines.extend(["", "By priority:"])

    for priority in REPORT_PRIORITY_ORDER:
        lines.append(f"  {priority}: {report['by_priority'][priority]}")

    lines.extend(["", "By category:"])

    for category in REPORT_CATEGORY_ORDER:
        lines.append(f"  {category}: {report['by_category'][category]}")

    lines.extend([
        "",
        f"Unresolved (open + in_progress): {report['unresolved']}",
        f"Resolved: {report['resolved']}",
        f"Resolution rate: {report['resolution_percentage']:.1f}%",
    ])

    return "\n".join(lines)
