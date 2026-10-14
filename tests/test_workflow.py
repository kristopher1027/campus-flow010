import unittest
from campusflow.workflow import (
    assign_ticket,
    can_transition,
    transition_status,
)

def make_ticket(tid="T001", status="open", assigned_to=None):
    return {
        "id": tid,
        "title": "Test ticket",
        "category": "Network",
        "urgency": "high",
        "affected_users": 12,
        "priority": "critical",
        "status": status,
        "assigned_to": assigned_to,
    }


class TestAssignTicket(unittest.TestCase):

    def test_assign_unknown_ticket_raises(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T999", "Alice")

    def test_assign_empty_name_raises(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "   ")

    def test_assign_success_sets_field(self):
        tickets = [make_ticket("T001")]
        result = assign_ticket(tickets, "T001", "Alice")
        self.assertEqual(result["assigned_to"], "Alice")
        self.assertEqual(tickets[0]["assigned_to"], "Alice")

    
    def test_assign_resolved_ticket_rejected_without_mutation(self):
        tickets = [make_ticket("T001", status="resolved", assigned_to="Alice")]
        snapshot = [dict(ticket) for ticket in tickets]

        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "Bob")

        self.assertEqual(tickets, snapshot)

    def test_non_string_staff_name_rejected_without_mutation(self):
        for bad_name in (None, 123, True):
            with self.subTest(bad_name=bad_name):
                tickets = [make_ticket("T001")]
                snapshot = [dict(ticket) for ticket in tickets]

                with self.assertRaises(ValueError):
                    assign_ticket(tickets, "T001", bad_name)

                self.assertEqual(tickets, snapshot)



class TestTransitionStatus(unittest.TestCase):

    
    def test_unassigned_cannot_start_progress(self):
        tickets = [make_ticket("T001", status="open", assigned_to=None)]
        snapshot = [dict(ticket) for ticket in tickets]

        with self.assertRaises(ValueError):
            transition_status(tickets, "T001", "in_progress")

        self.assertEqual(tickets, snapshot)

    def test_assigned_can_progress_to_in_progress(self):
        tickets = [make_ticket("T001", status="open", assigned_to="Alice")]
        result = transition_status(tickets, "T001", "in_progress")
        self.assertEqual(result["status"], "in_progress")

    def test_in_progress_to_resolved(self):
        tickets = [make_ticket("T001", status="in_progress", assigned_to="Alice")]
        result = transition_status(tickets, "T001", "resolved")
        self.assertEqual(result["status"], "resolved")

    def test_resolved_must_reopen_to_open(self):
        tickets = [make_ticket("T001", status="resolved", assigned_to="Alice")]
        result = transition_status(tickets, "T001", "open")
        self.assertEqual(result["status"], "open")

    def test_resolved_cannot_skip_reopen(self):
        tickets = [make_ticket("T001", status="resolved", assigned_to="Alice")]
        with self.assertRaises(ValueError):
            transition_status(tickets, "T001", "in_progress")

    def test_unknown_ticket_raises(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(ValueError):
            transition_status(tickets, "T999", "in_progress")

    def test_invalid_transition_raises(self):
        tickets = [make_ticket("T001", status="open", assigned_to="Alice")]
        with self.assertRaises(ValueError):
            transition_status(tickets, "T001", "resolved")

    
    def test_invalid_transition_leaves_entire_collection_unchanged(self):
        tickets = [
            make_ticket("T001", status="open", assigned_to="Alice"),
            make_ticket("T002", status="resolved", assigned_to="Bob"),
        ]
        snapshot = [dict(ticket) for ticket in tickets]

        with self.assertRaises(ValueError):
            transition_status(tickets, "T001", "resolved")

        self.assertEqual(tickets, snapshot)

    def test_can_transition_rules(self):
        self.assertTrue(can_transition("open", "in_progress"))
        self.assertTrue(can_transition("in_progress", "resolved"))
        self.assertTrue(can_transition("resolved", "open"))

        self.assertFalse(can_transition("open", "resolved"))
        self.assertFalse(can_transition("resolved", "in_progress"))
        self.assertFalse(can_transition("open", "open"))
        self.assertFalse(can_transition("unknown", "open"))



if __name__ == "__main__":
    unittest.main()
