"""Read-only ticket search, priority-sorted view, and result formatting."""

from campusflow.reports import PRIORITY_ORDER


def _matches_filter(ticket_value, wanted):
    """Return True if no filter was given, or the values match ignoring case."""
    if wanted is None:
        return True
    wanted = str(wanted).strip()
    if wanted == "":
        return True
    return str(ticket_value).strip().casefold() == wanted.casefold()


def search_tickets(tickets, text=None, category=None, status=None, priority=None):
    """Return a NEW list of tickets that match every filter that was supplied.

    - text: case-insensitive substring match on the title (uses casefold).
      Blank text (empty or only spaces) is treated as no filter.
    - category, status, priority: exact match, ignoring case.
    - Empty or None filters are skipped. All supplied filters must match (AND).
    - The tickets themselves are never modified.
    """
    # Blank text means "no text filter". Otherwise use the text exactly as typed,
    # so a search like "in " (with a space) is a true substring search.
    needle = "" if text is None or str(text).strip() == "" else str(text).casefold()

    results = []
    for ticket in tickets:
        if needle and needle not in ticket["title"].casefold():
            continue
        if not _matches_filter(ticket["category"], category):
            continue
        if not _matches_filter(ticket["status"], status):
            continue
        if not _matches_filter(ticket["priority"], priority):
            continue
        results.append(ticket)
    return results


def _numeric_id(ticket):
    """Return the number in an ID like 'T10' as an int (bad IDs sort last)."""
    try:
        return int(ticket["id"][1:])
    except (ValueError, IndexError):
        return 9999


def sort_by_priority(tickets):
    """Return a NEW list sorted by priority (critical first), then numeric ID."""
    return sorted(
        tickets,
        key=lambda t: (PRIORITY_ORDER.get(t["priority"], 99), _numeric_id(t)),
    )


def format_search_results(tickets):
    """Return a text table of results, or a friendly message if there are none."""
    if not tickets:
        return "No matching tickets found."

    rows = [
        (
            t["id"],
            t["title"],
            t["category"],
            t["priority"],
            t["status"],
            t["assigned_to"] or "Unassigned",
        )
        for t in tickets
    ]
    headers = ("ID", "Title", "Category", "Priority", "Status", "Assigned to")

    widths = [
        max(len(headers[i]), *(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]

    def line(values):
        return "  ".join(v.ljust(w) for v, w in zip(values, widths)).rstrip()

    lines = [line(headers), "  ".join("-" * w for w in widths)]
    lines.extend(line(row) for row in rows)
    lines.append(f"{len(rows)} ticket(s) found.")
    return "\n".join(lines)