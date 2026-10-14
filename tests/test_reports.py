import unittest
from campusflow.reports import (
    get_ticket,
    list_tickets,
    work_queue,
    report_summary,
    generate_report,
    format_report,
)

def make_ticket(tid, priority="high", status="open"):
    return {
        "id": tid,
        "title": f"Ticket {tid}",
        "category": "Network",
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

    def test_excludes_resolved(self):
        tickets = [
            make_ticket("T001", status="open"),
            make_ticket("T002", status="resolved"),
            make_ticket("T003", status="in_progress"),
        ]
        queue = work_queue(tickets)
        ids = [t["id"] for t in queue]
        self.assertEqual(sorted(ids), ["T001", "T003"])

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

if __name__ == "__main__":
    unittest.main()
