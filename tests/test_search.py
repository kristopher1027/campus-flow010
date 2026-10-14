import unittest
from copy import deepcopy

from campusflow.reports import work_queue
from campusflow.search import (
    format_search_results,
    search_tickets,
    sort_by_priority,
)


def make_ticket(
    tid,
    title="Printer jam",
    category="Hardware",
    priority="low",
    status="open",
    assigned_to=None,
):
    return {
        "id": tid,
        "title": title,
        "category": category,
        "urgency": "low",
        "affected_users": 1,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }


def sample_tickets():
    return [
        make_ticket("T1", "Wi-Fi down in library", "Network", "critical", "open"),
        make_ticket("T2", "wifi slow in hostel", "Network", "high", "in_progress", "Ada"),
        make_ticket("T3", "Laptop will not boot", "Hardware", "medium", "open"),
        make_ticket("T4", "WIFI password reset", "Network", "low", "resolved", "Musa"),
        make_ticket("T5", "Install MATLAB", "Software", "low", "open"),
    ]


def ids(tickets):
    return [t["id"] for t in tickets]


class TestTitleSearch(unittest.TestCase):

    def test_ignores_case(self):
        tickets = [make_ticket("T1", "Wi-Fi down"), make_ticket("T2", "wi-fi slow")]
        self.assertEqual(ids(search_tickets(tickets, "WI-FI")), ["T1", "T2"])
        self.assertEqual(ids(search_tickets(tickets, "wi-fi")), ["T1", "T2"])

    def test_matches_substrings(self):
        tickets = sample_tickets()
        self.assertEqual(ids(search_tickets(tickets, "lap")), ["T3"])
        self.assertEqual(ids(search_tickets(tickets, "in ")), ["T1", "T2"])

    def test_casefold_handles_special_letters(self):
        tickets = [make_ticket("T1", "Straße network")]
        self.assertEqual(ids(search_tickets(tickets, "STRASSE")), ["T1"])

    def test_no_match_returns_empty_list(self):
        self.assertEqual(search_tickets(sample_tickets(), "printer"), [])

    def test_no_fuzzy_spelling_correction(self):
        tickets = sample_tickets()
        self.assertEqual(search_tickets(tickets, "wfi"), [])
        self.assertEqual(search_tickets(tickets, "laptpo"), [])


class TestFilters(unittest.TestCase):

    def test_category_and_status_use_and(self):
        result = search_tickets(sample_tickets(), category="Network", status="open")
        self.assertEqual(ids(result), ["T1"])

    def test_text_category_status_all_combined(self):
        result = search_tickets(
            sample_tickets(), text="wifi", category="Network", status="open"
        )
        # T2 and T4 contain "wifi" but are not open. T1 is open but says "Wi-Fi".
        self.assertEqual(result, [])

        tickets = sample_tickets() + [make_ticket("T6", "Wifi router", "Network", "high", "open")]
        result = search_tickets(tickets, text="wifi", category="Network", status="open")
        self.assertEqual(ids(result), ["T6"])

    def test_priority_filter(self):
        result = search_tickets(sample_tickets(), priority="low")
        self.assertEqual(ids(result), ["T4", "T5"])

    def test_filter_values_ignore_case_and_spaces(self):
        result = search_tickets(sample_tickets(), category=" network ", status="OPEN")
        self.assertEqual(ids(result), ["T1"])

    def test_filter_that_matches_nothing(self):
        result = search_tickets(sample_tickets(), category="Other")
        self.assertEqual(result, [])


class TestEmptyFilters(unittest.TestCase):

    def test_no_filters_returns_everything(self):
        tickets = sample_tickets()
        self.assertEqual(ids(search_tickets(tickets)), ids(tickets))

    def test_none_filters_return_everything(self):
        tickets = sample_tickets()
        result = search_tickets(tickets, None, None, None, None)
        self.assertEqual(ids(result), ids(tickets))

    def test_empty_string_filters_return_everything(self):
        tickets = sample_tickets()
        result = search_tickets(tickets, "", "", "", "")
        self.assertEqual(ids(result), ids(tickets))

    def test_whitespace_only_filters_return_everything(self):
        tickets = sample_tickets()
        result = search_tickets(tickets, "   ", " ", " ", " ")
        self.assertEqual(ids(result), ids(tickets))

    def test_empty_ticket_list(self):
        self.assertEqual(search_tickets([], "wifi", "Network"), [])

    def test_returns_a_new_list(self):
        tickets = sample_tickets()
        result = search_tickets(tickets)
        self.assertIsNot(result, tickets)


class TestSearchIsReadOnly(unittest.TestCase):

    def test_search_leaves_collection_unchanged(self):
        tickets = sample_tickets()
        snapshot = deepcopy(tickets)
        search_tickets(tickets, "wifi", "Network", "open", "high")
        search_tickets(tickets)
        sort_by_priority(search_tickets(tickets, "wifi"))
        self.assertEqual(tickets, snapshot)

    def test_sort_does_not_reorder_original_list(self):
        tickets = sample_tickets()
        original_order = ids(tickets)
        sort_by_priority(tickets)
        self.assertEqual(ids(tickets), original_order)


class TestSortByPriority(unittest.TestCase):

    def test_order_is_critical_high_medium_low(self):
        tickets = [
            make_ticket("T1", priority="low"),
            make_ticket("T2", priority="medium"),
            make_ticket("T3", priority="critical"),
            make_ticket("T4", priority="high"),
        ]
        self.assertEqual(ids(sort_by_priority(tickets)), ["T3", "T4", "T2", "T1"])

    def test_ties_use_numeric_id_t2_before_t10(self):
        tickets = [
            make_ticket("T10", priority="high"),
            make_ticket("T2", priority="high"),
            make_ticket("T1", priority="high"),
        ]
        # Plain text sorting would put "T10" before "T2". Numbers must win.
        self.assertEqual(ids(sort_by_priority(tickets)), ["T1", "T2", "T10"])

    def test_works_with_zero_padded_ids(self):
        tickets = [
            make_ticket("T010", priority="low"),
            make_ticket("T002", priority="low"),
        ]
        self.assertEqual(ids(sort_by_priority(tickets)), ["T002", "T010"])

    def test_sorts_search_results(self):
        found = search_tickets(sample_tickets(), category="Network")
        self.assertEqual(ids(sort_by_priority(found)), ["T1", "T2", "T4"])

    def test_empty_list(self):
        self.assertEqual(sort_by_priority([]), [])


class TestFormatSearchResults(unittest.TestCase):

    def test_shows_all_six_fields(self):
        ticket = make_ticket("T7", "Wi-Fi down", "Network", "critical", "open", "Ada")
        output = format_search_results([ticket])
        for expected in ("T7", "Wi-Fi down", "Network", "critical", "open", "Ada"):
            self.assertIn(expected, output)

    def test_unassigned_is_shown_clearly(self):
        output = format_search_results([make_ticket("T1")])
        self.assertIn("Unassigned", output)
        self.assertNotIn("None", output)

    def test_empty_results_message(self):
        self.assertEqual(format_search_results([]), "No matching tickets found.")

    def test_one_row_per_ticket_and_count(self):
        output = format_search_results(sample_tickets())
        self.assertIn("5 ticket(s) found.", output)
        for tid in ("T1", "T2", "T3", "T4", "T5"):
            self.assertIn(tid, output)


class TestOriginalWorkQueueUnchanged(unittest.TestCase):

    def test_queue_excludes_resolved(self):
        queue = work_queue(sample_tickets())
        self.assertNotIn("T4", ids(queue))

    def test_queue_behaviour_matches_current_main(self):
        # Pins the CURRENT behaviour on main: open + in_progress, sorted.
        # See the note in the PR about the issue's "excludes in_progress" wording.
        queue = work_queue(sample_tickets())
        self.assertEqual(ids(queue), ["T1", "T2", "T3", "T5"])

    def test_adding_search_does_not_change_queue(self):
        tickets = sample_tickets()
        before = ids(work_queue(tickets))
        search_tickets(tickets, "wifi", "Network", "open")
        self.assertEqual(ids(work_queue(tickets)), before)


if __name__ == "__main__":
    unittest.main()