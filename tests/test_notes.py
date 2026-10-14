
import unittest
from copy import deepcopy

from campusflow.tickets import create_ticket, add_note, next_note_id
from campusflow.workflow import transition_status


class TestNotes(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        self.ticket = create_ticket(
            self.tickets,
            title="Network connection issue",
            category="Network",
            urgency="medium",
            affected_users=2,
        )

    def test_new_ticket_starts_with_empty_notes(self):
        self.assertEqual(self.ticket["notes"], [])

    def test_first_note_gets_n001(self):
        note = add_note(self.tickets, self.ticket["id"], " Alice ", " Check router ")
        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(note["author"], "Alice")
        self.assertEqual(note["message"], "Check router")

    def test_note_ids_increment_per_ticket(self):
        add_note(self.tickets, self.ticket["id"], "Alice", "First note")
        note = add_note(self.tickets, self.ticket["id"], "Bob", "Second note")
        self.assertEqual(note["note_id"], "N002")

        second_ticket = create_ticket(
            self.tickets,
            title="Printer issue",
            category="Hardware",
            urgency="low",
            affected_users=1,
        )
        note = add_note(self.tickets, second_ticket["id"], "Sam", "Check printer")
        self.assertEqual(note["note_id"], "N001")

    def test_next_note_id_uses_highest_existing_id(self):
        self.ticket["notes"] = [
            {"note_id": "N001", "author": "A", "message": "First note"},
            {"note_id": "N009", "author": "B", "message": "Another note"},
        ]
        self.assertEqual(next_note_id(self.ticket), "N010")

    def test_blank_author_rejected_without_mutation(self):
        before = deepcopy(self.tickets)
        with self.assertRaises(ValueError):
            add_note(self.tickets, self.ticket["id"], "   ", "Valid message")
        self.assertEqual(self.tickets, before)

    def test_message_shorter_than_five_characters_rejected(self):
        before = deepcopy(self.tickets)
        with self.assertRaises(ValueError):
            add_note(self.tickets, self.ticket["id"], "Alice", " ab ")
        self.assertEqual(self.tickets, before)

    def test_message_longer_than_300_characters_rejected(self):
        before = deepcopy(self.tickets)
        with self.assertRaises(ValueError):
            add_note(self.tickets, self.ticket["id"], "Alice", "x" * 301)
        self.assertEqual(self.tickets, before)

    def test_message_boundaries_are_accepted(self):
        short_note = add_note(self.tickets, self.ticket["id"], "Alice", "x" * 5)
        long_note = add_note(self.tickets, self.ticket["id"], "Alice", "x" * 300)
        self.assertEqual(short_note["note_id"], "N001")
        self.assertEqual(long_note["note_id"], "N002")

    def test_resolved_ticket_rejects_notes_without_mutation(self):
        self.ticket["status"] = "resolved"
        before = deepcopy(self.tickets)

        with self.assertRaises(ValueError):
            add_note(self.tickets, self.ticket["id"], "Alice", "Valid message")

        self.assertEqual(self.tickets, before)

    def test_notes_survive_resolve_and_reopen(self):
        original = add_note(
            self.tickets, self.ticket["id"], "Alice", "Initial note"
        )
        self.ticket["status"] = "in_progress"
        add_note(self.tickets, self.ticket["id"], "Bob", "Progress update")

        # Exercise the actual status workflow.
        transition_status(self.tickets, self.ticket["id"], "resolved")
        with self.assertRaises(ValueError):
            add_note(self.tickets, self.ticket["id"], "Sam", "Rejected note")

        transition_status(self.tickets, self.ticket["id"], "open")
        reopened_note = add_note(
            self.tickets, self.ticket["id"], "Sam", "After reopening"
        )

        self.assertEqual([n["note_id"] for n in self.ticket["notes"]],
                         ["N001", "N002", "N003"])
        self.assertEqual(self.ticket["notes"][0], original)
        self.assertEqual(reopened_note["note_id"], "N003")

    def test_unknown_ticket_rejected(self):
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T999", "Alice", "Valid message")


if __name__ == "__main__":
    unittest.main()
