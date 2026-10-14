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
    print("8. Exit")


def main():
    tickets = load_tickets(DEFAULT_PATH)

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
            save_tickets(tickets, DEFAULT_PATH)
            print("Goodbye.")
            break
        else:
            print("Invalid choice. Enter 1-8.")


if __name__ == "__main__":
    main()