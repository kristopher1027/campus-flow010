import unittest

from campusflow.tickets import (
    calculate_priority,
    create_ticket,
    find_ticket,
    format_ticket_details,
    format_ticket_list,
    format_ticket_summary,
    generate_next_id,
    validate_affected_users,
)


class TestCreateTicket(unittest.TestCase):

    def test_valid_ticket_has_all_fields(self):
        tickets = []
        ticket = create_ticket(tickets, "Wi-Fi down", "Network", "high", 15)
        expected_keys = {
            "id", "title", "category", "urgency",
            "affected_users", "priority", "status", "assigned_to",
        }
        self.assertEqual(set(ticket.keys()), expected_keys)
        self.assertEqual(len(tickets), 1)

    def test_new_ticket_defaults(self):
        ticket = create_ticket([], "Wi-Fi down", "Network", "high", 15)
        self.assertEqual(ticket["status"], "open")
        self.assertIsNone(ticket["assigned_to"])

    def test_title_is_stripped(self):
        ticket = create_ticket([], "  Wi-Fi down  ", "Network", "high", 15)
        self.assertEqual(ticket["title"], "Wi-Fi down")

    def test_category_is_normalized(self):
        for raw in ("network", " NETWORK ", "Network"):
            with self.subTest(raw=raw):
                ticket = create_ticket([], "x", raw, "low", 1)
                self.assertEqual(ticket["category"], "Network")

    def test_urgency_is_normalized(self):
        for raw in ("HIGH", " high ", "High"):
            with self.subTest(raw=raw):
                ticket = create_ticket([], "x", "Network", raw, 1)
                self.assertEqual(ticket["urgency"], "high")

    def test_numeric_string_affected_users_accepted(self):
        ticket = create_ticket([], "x", "Network", "low", "15")
        self.assertEqual(ticket["affected_users"], 15)
        self.assertIsInstance(ticket["affected_users"], int)

    def test_unicode_decimal_string_affected_users_normalized(self):
        ticket = create_ticket([], "x", "Network", "low", "٣")
        self.assertEqual(ticket["affected_users"], 3)
        self.assertIsInstance(ticket["affected_users"], int)
        self.assertEqual(ticket["priority"], "medium")


class TestInvalidInput(unittest.TestCase):

    def test_blank_title_rejected(self):
        for bad in ("", "   ", None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    create_ticket([], bad, "Network", "high", 5)

    def test_invalid_category_rejected(self):
        for bad in ("Plumbing", "", "   ", None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    create_ticket([], "x", bad, "high", 5)

    def test_invalid_urgency_rejected(self):
        for bad in ("urgent", "", "   ", None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    create_ticket([], "x", "Network", bad, 5)

    def test_bad_affected_users_rejected(self):
        for bad in (0, -3, 2.5, "abc", "", "2.5", "-3", True, False, None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    validate_affected_users(bad)

    def test_failed_creation_leaves_list_unchanged(self):
        tickets = []
        create_ticket(tickets, "First", "Network", "low", 1)
        snapshot = [dict(t) for t in tickets]

        with self.assertRaises(ValueError):
            create_ticket(tickets, "Second", "Network", "high", 0)
        with self.assertRaises(ValueError):
            create_ticket(tickets, "Third", "BadCategory", "high", 5)

        self.assertEqual(tickets, snapshot)


class TestIds(unittest.TestCase):

    def test_first_id_is_t001(self):
        self.assertEqual(generate_next_id([]), "T001")

    def test_next_id_after_t009_is_t010(self):
        self.assertEqual(generate_next_id([{"id": "T009"}]), "T010")

    def test_next_id_uses_highest_not_length(self):
        # Two tickets, but the highest number is 5, so the next must be T006.
        tickets = [{"id": "T002"}, {"id": "T005"}]
        self.assertEqual(generate_next_id(tickets), "T006")

    def test_created_tickets_get_sequential_ids(self):
        tickets = []
        first = create_ticket(tickets, "a", "Network", "low", 1)
        second = create_ticket(tickets, "b", "Network", "low", 1)
        self.assertEqual(first["id"], "T001")
        self.assertEqual(second["id"], "T002")


class TestPriority(unittest.TestCase):

    def test_required_acceptance_scenarios(self):
        cases = [
            ("high", 12, "critical"),
            ("high", 2, "high"),
            ("low", 4, "medium"),
            ("low", 1, "low"),
        ]
        for urgency, users, expected in cases:
            with self.subTest(urgency=urgency, users=users):
                self.assertEqual(calculate_priority(urgency, users), expected)

    def test_boundaries(self):
        cases = [
            ("high", 10, "critical"),
            ("high", 9, "high"),
            ("medium", 9, "medium"),
            ("medium", 10, "high"),
            ("low", 10, "high"),
            ("low", 3, "medium"),
            ("low", 2, "low"),
            ("medium", 1, "medium"),
        ]
        for urgency, users, expected in cases:
            with self.subTest(urgency=urgency, users=users):
                self.assertEqual(calculate_priority(urgency, users), expected)

    def test_create_ticket_calculates_priority(self):
        ticket = create_ticket([], "Wi-Fi down", "Network", "HIGH", "12")
        self.assertEqual(ticket["priority"], "critical")

def make_ticket(**overrides):
    """Build a complete ticket dict for tests; override any field."""
    ticket = {
        "id": "T001",
        "title": "Wi-Fi down",
        "category": "Network",
        "urgency": "high",
        "affected_users": 15,
        "priority": "critical",
        "status": "open",
        "assigned_to": None,
    }
    ticket.update(overrides)
    return ticket


class TestFindTicket(unittest.TestCase):

    def test_finds_existing_ticket(self):
        tickets = [make_ticket(id="T001"), make_ticket(id="T002")]
        self.assertEqual(find_ticket(tickets, "T002")["id"], "T002")

    def test_tolerates_case_and_whitespace(self):
        tickets = [make_ticket(id="T001")]
        for raw in ("t001", " T001 ", " t001"):
            with self.subTest(raw=raw):
                self.assertEqual(find_ticket(tickets, raw)["id"], "T001")

    def test_unknown_id_raises(self):
        with self.assertRaises(ValueError):
            find_ticket([make_ticket()], "T999")

    def test_blank_or_non_text_id_raises(self):
        for bad in ("", "   ", None, 1):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    find_ticket([make_ticket()], bad)

    def test_lookup_on_empty_list_raises(self):
        with self.assertRaises(ValueError):
            find_ticket([], "T001")


class TestFormatting(unittest.TestCase):

    def test_summary_contains_key_fields(self):
        text = format_ticket_summary(
            make_ticket(id="T007", title="Printer jam", priority="low",
                        status="in_progress", assigned_to="Ada")
        )
        for expected in ("T007", "Printer jam", "low", "in_progress", "Ada"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_summary_shows_unassigned_not_none(self):
        text = format_ticket_summary(make_ticket(assigned_to=None))
        self.assertIn("Unassigned", text)
        self.assertNotIn("None", text)

    def test_details_show_all_eight_fields(self):
        text = format_ticket_details(make_ticket(assigned_to="Ada"))
        for expected in ("T001", "Wi-Fi down", "Network", "high",
                         "15", "critical", "open", "Ada"):
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_details_show_unassigned_not_none(self):
        text = format_ticket_details(make_ticket(assigned_to=None))
        self.assertIn("Unassigned", text)
        self.assertNotIn("None", text)

    def test_empty_list_shows_friendly_message(self):
        self.assertEqual(format_ticket_list([]), "No tickets yet.")

    def test_list_has_one_line_per_ticket(self):
        tickets = [make_ticket(id="T001"), make_ticket(id="T002")]
        lines = format_ticket_list(tickets).splitlines()
        self.assertEqual(len(lines), 2)
        self.assertIn("T001", lines[0])
        self.assertIn("T002", lines[1])

if __name__ == "__main__":
    unittest.main()
