"""CampusFlow CLI — thin layer over the logic modules."""

from campusflow.tickets import (
    create_ticket,
    find_ticket,
    format_ticket_list,
    format_ticket_details,
)
from campusflow.reports import work_queue, report_summary, format_report
from campusflow.workflow import assign_ticket, transition_status
from campusflow.storage import load_tickets, save_tickets, DEFAULT_PATH
from campusflow.search import search_tickets, sort_by_priority, format_search_results
from campusflow.notes import add_note, get_notes
from campusflow.note_storage import load_notes, save_notes, NOTES_PATH



# ============================================================
# Engineer A's handlers
# ============================================================

def handle_create(tickets):
    try:
        title = input("Title: ").strip()
        category = input("Category (Network/Hardware/Software/Other): ").strip()
        urgency = input("Urgency (low/medium/high): ").strip()
        affected_str = input("Affected users: ").strip()
        affected = int(affected_str)
        ticket = create_ticket(tickets, title, category, urgency, affected)
        print(f"Created ticket {ticket['id']} with priority {ticket['priority']}.")
        save_tickets(tickets, DEFAULT_PATH)
    except ValueError as e:
        print(f"Error: {e}")


def handle_list(tickets):
    print(format_ticket_list(tickets))


def handle_view(tickets):
    try:
        ticket_id = input("Ticket ID: ").strip()
        ticket = find_ticket(tickets, ticket_id)
        print(format_ticket_details(ticket))
    except ValueError as e:
        print(f"Error: {e}")


# ============================================================
# Engineer B's handlers (yours)
# ============================================================

def handle_assign(tickets):
    try:
        ticket_id = input("Ticket ID: ").strip()
        staff_name = input("Staff name: ").strip()
        ticket = assign_ticket(tickets, ticket_id, staff_name)
        print(f"Assigned {ticket['id']} to {ticket['assigned_to']}.")
        save_tickets(tickets, DEFAULT_PATH)
    except ValueError as e:
        print(f"Error: {e}")


def handle_status(tickets):
    try:
        ticket_id = input("Ticket ID: ").strip()
        new_status = input("New status (open/in_progress/resolved): ").strip()
        ticket = transition_status(tickets, ticket_id, new_status)
        print(f"Ticket {ticket['id']} status is now {ticket['status']}.")
        save_tickets(tickets, DEFAULT_PATH)
    except ValueError as e:
        print(f"Error: {e}")


def handle_queue(tickets):
    queue = work_queue(tickets)
    if not queue:
        print("Queue is empty.")
        return
    print(f"{'ID':<6}{'Priority':<10}{'Status':<14}{'Title'}")
    print("-" * 55)
    for t in queue:
        print(f"{t['id']:<6}{t['priority']:<10}{t['status']:<14}{t['title']}")


def handle_report(tickets):
    print(format_report(report_summary(tickets)))



def handle_add_note(tickets, notes):
    try:
        ticket_id = input("Ticket ID: ").strip()
        note_text = input("Follow-up note: ").strip()

        note = add_note(notes, tickets, ticket_id, note_text)
        save_notes(notes, NOTES_PATH)

        print(
            f"Note {note['id']} added to ticket "
            f"{note['ticket_id']} successfully."
        )

    except ValueError as error:
        print(f"Error: {error}")


def handle_view_notes(tickets, notes):
    try:
        ticket_id = input("Ticket ID: ").strip()
        ticket_notes = get_notes(notes, tickets, ticket_id)

        if not ticket_notes:
            print(f"No notes found for ticket {ticket_id}.")
            return

        print(f"\nNotes for ticket {ticket_id}:")
        for note in ticket_notes:
            print(f"Note {note['id']}: {note['text']}")

    except ValueError as error:
        print(f"Error: {error}")



def prompt_filter(label, allowed_choices):
    """Ask for an optional filter and re-prompt until it is valid."""
    while True:
        value = input(
            f"{label} ({'/'.join(allowed_choices)}, or Enter to skip): "
        ).strip()

        if not value:
            return None

        for choice in allowed_choices:
            if value.casefold() == choice.casefold():
                return choice

        print(f"Invalid {label.lower()}. Choose one of: "
              f"{', '.join(allowed_choices)}.")


def get_search_results(tickets):
    """Collect search criteria and return matching tickets."""
    text = input("Search title (or press Enter to skip): ").strip()

    category = prompt_filter(
        "Category", ["Network", "Hardware", "Software", "Other"]
    )
    status = prompt_filter(
        "Status", ["open", "in_progress", "resolved"]
    )
    priority = prompt_filter(
        "Priority", ["critical", "high", "medium", "low"]
    )

    return search_tickets(
        tickets,
        text=text or None,
        category=category,
        status=status,
        priority=priority,
    )


def handle_search(tickets):
    results = get_search_results(tickets)
    print(format_search_results(results))


def handle_sorted_search(tickets):
    results = get_search_results(tickets)
    sorted_results = sort_by_priority(results)
    print(format_search_results(sorted_results))



# ============================================================
# Menu and main loop
# ============================================================

def show_menu():
    print("\n--- CampusFlow ---")
    print("1. Create ticket")
    print("2. List tickets")
    print("3. View ticket")
    print("4. Assign ticket")
    print("5. Change status")
    print("6. Work queue")
    print("7. Report")
    print("8. Add Follow-up Note")
    print("9. View Ticket Notes")
    print("10. Search Tickets")
    print("11. Sorted Search Results")
    print("12. Exit")



def main():
    tickets = load_tickets(DEFAULT_PATH)
    notes = load_notes(NOTES_PATH)

    while True:
        show_menu()
        try:
            choice = input("Choice: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting. Saving data...")
            save_tickets(tickets, DEFAULT_PATH)
            break

        if choice == "1":
            handle_create(tickets)
        elif choice == "2":
            handle_list(tickets)
        elif choice == "3":
            handle_view(tickets)
        elif choice == "4":
            handle_assign(tickets)
        elif choice == "5":
            handle_status(tickets)
        elif choice == "6":
            handle_queue(tickets)
        
        elif choice == "7":
            handle_report(tickets)
        
        elif choice == "8":
            handle_add_note(tickets, notes)
        elif choice == "9":
            handle_view_notes(tickets, notes)

        elif choice == "10":
            handle_search(tickets)
        elif choice == "11":
            handle_sorted_search(tickets)
        elif choice == "12":
            save_tickets(tickets, DEFAULT_PATH)
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Enter a number from 1-12.")



if __name__ == "__main__":
    main()