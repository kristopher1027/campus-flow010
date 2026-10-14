import unittest
from campusflow.workflow import assign_ticket, transition_status
from campusflow.reports import (
    get_ticket,
    list_tickets,
    work_queue,
    report_summary,
    generate_report,
    format_report,
)

def make_ticket(tid, priority="high", status="open", category="Network"):
    return {
        "id": tid,
        "title": f"Ticket {tid}",
        "category": category,
        "urgency": "high",
        "affected_users": 5,
        "priority": priority,
        "status": status,
        "assigned_to": None,
    }


class TestGetTicket(unittest.TestCase):

    def test_get_existing_ticket(self):
        tickets = [make_ticket("T001"), make_ticket("T002")]
        result = get_ticket(tickets, "T001")
        self.assertEqual(result["id"], "T001")

    def test_get_unknown_ticket_raises(self):
        tickets = [make_ticket("T001")]
        with self.assertRaises(ValueError):
            get_ticket(tickets, "T999")


class TestWorkQueue(unittest.TestCase):

    def test_orders_by_priority(self):
        tickets = [
            make_ticket("T001", priority="low"),
            make_ticket("T002", priority="critical"),
            make_ticket("T003", priority="medium"),
            make_ticket("T004", priority="high"),
        ]
        queue = work_queue(tickets)
        ids = [t["id"] for t in queue]
        self.assertEqual(ids, ["T002", "T004", "T003", "T001"])

    def test_tie_broken_by_numeric_id(self):
        tickets = [
            make_ticket("T010", priority="high"),
            make_ticket("T002", priority="high"),
            make_ticket("T005", priority="high"),
        ]
        queue = work_queue(tickets)
        ids = [t["id"] for t in queue]
        self.assertEqual(ids, ["T002", "T005", "T010"])

    def test_tie_break_handles_unpadded_numeric_ids(self):
        # Numeric order must hold even when imported IDs lack zero padding.
        tickets = [
            make_ticket("T10", priority="high"),
            make_ticket("T2", priority="high"),
        ]

        queue = work_queue(tickets)

        self.assertEqual([ticket["id"] for ticket in queue], ["T2", "T10"])
        self.assertEqual([ticket["id"] for ticket in tickets], ["T10", "T2"])

    def test_includes_only_open_tickets(self):
        tickets = [
            make_ticket("T001", status="open"),
            make_ticket("T002", status="resolved"),
            make_ticket("T003", status="in_progress"),
        ]
        queue = work_queue(tickets)
        ids = [t["id"] for t in queue]
        self.assertEqual(ids, ["T001"])

    def test_empty_queue(self):
        self.assertEqual(work_queue([]), [])


class TestReportSummary(unittest.TestCase):

    def test_empty_report_returns_zeros(self):
        summary = report_summary([])
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["by_status"]["open"], 0)
        self.assertEqual(summary["by_status"]["in_progress"], 0)
        self.assertEqual(summary["by_status"]["resolved"], 0)
        self.assertEqual(summary["by_priority"]["critical"], 0)

    def test_counts_by_status_and_priority(self):
        tickets = [
            make_ticket("T001", priority="critical", status="open"),
            make_ticket("T002", priority="high", status="in_progress"),
            make_ticket("T003", priority="high", status="resolved"),
            make_ticket("T004", priority="low", status="open"),
        ]
        summary = report_summary(tickets)
        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["by_status"]["open"], 2)
        self.assertEqual(summary["by_status"]["in_progress"], 1)
        self.assertEqual(summary["by_status"]["resolved"], 1)
        self.assertEqual(summary["by_priority"]["high"], 2)
        self.assertEqual(summary["by_priority"]["critical"], 1)


class TestGenerateReport(unittest.TestCase):

    def test_empty_report_has_all_zero_counts(self):
        report = generate_report([])

        self.assertEqual(report["total"], 0)
        self.assertEqual(
            report["by_status"],
            {"open": 0, "in_progress": 0, "resolved": 0},
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 0, "high": 0, "medium": 0, "low": 0},
        )

    def test_counts_statuses_and_priorities(self):
        tickets = [
            make_ticket("T001", priority="critical", status="open"),
            make_ticket("T002", priority="high", status="in_progress"),
            make_ticket("T003", priority="high", status="resolved"),
            make_ticket("T004", priority="low", status="open"),
        ]

        report = generate_report(tickets)

        self.assertEqual(report["total"], 4)
        self.assertEqual(
            sum(report["by_status"].values()),
            report["total"],
        )
        self.assertEqual(
            sum(report["by_priority"].values()),
            report["total"],
        )
        self.assertEqual(report["by_status"]["open"], 2)
        self.assertEqual(report["by_priority"]["high"], 2)

    def test_formatter_includes_counts_in_consistent_order(self):
        report = generate_report([
            make_ticket("T001", priority="critical", status="open"),
        ])

        output = format_report(report)

        self.assertIn("Total tickets: 1", output)
        self.assertLess(output.index("open:"), output.index("in_progress:"))
        self.assertLess(output.index("critical:"), output.index("high:"))
        self.assertIn("low: 0", output)


def report_fixture():
    """Six tickets with known counts. Used by the insight tests."""
    return [
        make_ticket("T001", "critical", "open", "Network"),
        make_ticket("T002", "high", "in_progress", "Network"),
        make_ticket("T003", "high", "resolved", "Hardware"),
        make_ticket("T004", "medium", "open", "Software"),
        make_ticket("T005", "low", "resolved", "Hardware"),
        make_ticket("T006", "low", "resolved", "Network"),
    ]


class TestReportInsights(unittest.TestCase):

    def test_empty_list_does_not_crash(self):
        report = generate_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(report["resolution_percentage"], 0)
        self.assertEqual(report["unresolved"], 0)
        self.assertEqual(report["resolved"], 0)

    def test_empty_list_includes_every_group_with_zero(self):
        report = generate_report([])
        self.assertEqual(
            report["by_category"],
            {"Network": 0, "Hardware": 0, "Software": 0, "Other": 0},
        )
        self.assertEqual(
            report["by_status"],
            {"open": 0, "in_progress": 0, "resolved": 0},
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 0, "high": 0, "medium": 0, "low": 0},
        )

    def test_empty_list_report_can_be_formatted(self):
        output = format_report(generate_report([]))
        self.assertIn("Total tickets: 0", output)
        self.assertIn("Resolution rate: 0.0%", output)

    def test_known_fixture_gives_exact_counts(self):
        report = generate_report(report_fixture())
        self.assertEqual(report["total"], 6)
        self.assertEqual(
            report["by_status"],
            {"open": 2, "in_progress": 1, "resolved": 3},
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 1, "high": 2, "medium": 1, "low": 2},
        )
        self.assertEqual(
            report["by_category"],
            {"Network": 3, "Hardware": 2, "Software": 1, "Other": 0},
        )
        self.assertEqual(report["unresolved"], 3)
        self.assertEqual(report["resolved"], 3)
        self.assertEqual(report["resolution_percentage"], 50.0)

    def test_resolution_percentage_formula(self):
        tickets = [
            make_ticket("T001", status="resolved"),
            make_ticket("T002", status="open"),
            make_ticket("T003", status="open"),
            make_ticket("T004", status="open"),
        ]
        self.assertEqual(generate_report(tickets)["resolution_percentage"], 25.0)

    def test_all_resolved_is_100_percent(self):
        tickets = [make_ticket("T001", status="resolved")]
        self.assertEqual(generate_report(tickets)["resolution_percentage"], 100.0)

    def test_each_group_of_counts_sums_to_total(self):
        report = generate_report(report_fixture())
        self.assertEqual(sum(report["by_status"].values()), report["total"])
        self.assertEqual(sum(report["by_priority"].values()), report["total"])
        self.assertEqual(sum(report["by_category"].values()), report["total"])
        self.assertEqual(
            report["unresolved"] + report["resolved"], report["total"]
        )

    def test_in_progress_counts_as_unresolved(self):
        tickets = [make_ticket("T001", status="in_progress")]
        report = generate_report(tickets)
        self.assertEqual(report["unresolved"], 1)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["resolution_percentage"], 0.0)

    def test_unresolved_is_open_plus_in_progress(self):
        report = generate_report(report_fixture())
        self.assertEqual(
            report["unresolved"],
            report["by_status"]["open"] + report["by_status"]["in_progress"],
        )

    def test_counts_change_after_resolve_and_change_back_after_reopen(self):
        tickets = report_fixture()
        before = generate_report(tickets)

        assign_ticket(tickets, "T001", "Ada")
        transition_status(tickets, "T001", "in_progress")
        transition_status(tickets, "T001", "resolved")
        resolved_report = generate_report(tickets)
        self.assertEqual(resolved_report["by_status"]["open"], 1)
        self.assertEqual(resolved_report["by_status"]["resolved"], 4)
        self.assertEqual(resolved_report["resolved"], 4)
        self.assertEqual(resolved_report["unresolved"], 2)
        self.assertAlmostEqual(
            resolved_report["resolution_percentage"], 4 / 6 * 100
        )
        # Other groups do not change when only the status changes.
        self.assertEqual(resolved_report["by_priority"], before["by_priority"])
        self.assertEqual(resolved_report["by_category"], before["by_category"])

        transition_status(tickets, "T001", "open")
        reopened_report = generate_report(tickets)
        self.assertEqual(reopened_report["by_status"], {"open": 2, "in_progress": 1, "resolved": 3})
        self.assertEqual(reopened_report["resolved"], 3)
        self.assertEqual(reopened_report["resolution_percentage"], 50.0)
        self.assertEqual(sum(reopened_report["by_status"].values()), 6)

    def test_report_does_not_modify_tickets(self):
        from copy import deepcopy
        tickets = report_fixture()
        snapshot = deepcopy(tickets)
        generate_report(tickets)
        self.assertEqual(tickets, snapshot)


class TestFormatReportInsights(unittest.TestCase):

    def test_formatter_shows_new_sections(self):
        output = format_report(generate_report(report_fixture()))
        self.assertIn("By category:", output)
        self.assertIn("Network: 3", output)
        self.assertIn("Other: 0", output)
        self.assertIn("Unresolved (open + in_progress): 3", output)
        self.assertIn("Resolved: 3", output)
        self.assertIn("Resolution rate: 50.0%", output)

    def test_formatter_section_and_category_order(self):
        output = format_report(generate_report(report_fixture()))
        self.assertLess(output.index("By status:"), output.index("By priority:"))
        self.assertLess(output.index("By priority:"), output.index("By category:"))
        self.assertLess(output.index("By category:"), output.index("Unresolved"))
        self.assertLess(output.index("Network:"), output.index("Hardware:"))
        self.assertLess(output.index("Hardware:"), output.index("Software:"))
        self.assertLess(output.index("Software:"), output.index("Other:"))

    def test_formatter_rounds_to_one_decimal(self):
        tickets = [
            make_ticket("T001", status="resolved"),
            make_ticket("T002", status="open"),
            make_ticket("T003", status="open"),
        ]
        output = format_report(generate_report(tickets))
        self.assertIn("Resolution rate: 33.3%", output)

    def test_formatter_returns_text_and_does_not_print(self):
        self.assertIsInstance(format_report(generate_report([])), str)


if __name__ == "__main__":
    unittest.main()
    
