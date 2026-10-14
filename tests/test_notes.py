import unittest

from campusflow.notes import add_note


class TestAddNote(unittest.TestCase):

    def make_ticket(self, status):
        return {
            "id": "T001",
            "title": "Issue",
            "category": "Network",
            "urgency": "low",
            "affected_users": 1,
            "priority": "low",
            "status": status,
            "assigned_to": "Ada",
        }

    def test_resolved_ticket_rejects_note_without_changing_notes(self):
        tickets = [self.make_ticket("resolved")]
        notes = []

        with self.assertRaisesRegex(ValueError, "resolved ticket"):
            add_note(notes, tickets, "T001", "Follow up")

        self.assertEqual(notes, [])

    def test_reopened_ticket_accepts_note(self):
        notes = []
        note = add_note(notes, [self.make_ticket("open")], "T001", "Follow up")
        self.assertEqual(note["text"], "Follow up")
        self.assertEqual(notes, [note])


if __name__ == "__main__":
    unittest.main()
