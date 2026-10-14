import copy
import json
import os
import tempfile
import unittest

from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import generate_next_id


def make_ticket(**overrides):
    """A complete, valid ticket. Override any field."""
    ticket = {
        "id": "T001",
        "title": "Wi-Fi down",
        "category": "Network",
        "urgency": "high",
        "affected_users": 15,
        "priority": "critical",
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }
    ticket.update(overrides)
    return ticket


def make_note(note_id="N001", author="Mentor A", message="Router reboot attempted"):
    return {"note_id": note_id, "author": author, "message": message}


class StorageTestCase(unittest.TestCase):

    def setUp(self):
        # Fresh temporary folder per test. Never touches the real data/ file.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = os.path.join(self.temp_dir.name, "tickets.json")

    def write_raw(self, text):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(text)

    def read_raw(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return f.read()

    def assert_rejected(self, data):
        """Write data, expect StorageError, and prove the file was not changed."""
        text = data if isinstance(data, str) else json.dumps(data)
        self.write_raw(text)
        with self.assertRaises(StorageError):
            load_tickets(self.path)
        self.assertEqual(self.read_raw(), text)


class TestSaveAndLoad(StorageTestCase):

    def test_round_trip_with_notes(self):
        tickets = [
            make_ticket(
                id="T001", status="in_progress", assigned_to="Ada",
                notes=[make_note("N001"), make_note("N002", "Mentor B", "Checking switch ports")],
            ),
            make_ticket(id="T002", urgency="low", affected_users=1, priority="low"),
        ]
        save_tickets(tickets, self.path)
        self.assertEqual(load_tickets(self.path), tickets)

    def test_none_assigned_to_survives_round_trip(self):
        save_tickets([make_ticket()], self.path)
        self.assertIsNone(load_tickets(self.path)[0]["assigned_to"])

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_empty_list_saves_and_loads(self):
        save_tickets([], self.path)
        self.assertEqual(load_tickets(self.path), [])

    def test_save_creates_missing_folder(self):
        nested = os.path.join(self.temp_dir.name, "data", "sub", "tickets.json")
        save_tickets([], nested)
        self.assertTrue(os.path.exists(nested))


class TestRejectedFiles(StorageTestCase):

    def test_corrupt_json_rejected_and_file_unchanged(self):
        self.assert_rejected("{ this is not valid json")

    def test_wrong_top_level_structure_rejected(self):
        for data in ({"id": "T001"}, "hello", 42, None):
            with self.subTest(data=data):
                self.assert_rejected(data)

    def test_list_of_non_objects_rejected(self):
        self.assert_rejected(["T001", "T002"])

    def test_duplicate_ticket_id_rejected(self):
        self.assert_rejected([make_ticket(id="T001"), make_ticket(id="T001")])

    def test_missing_required_key_rejected(self):
        for key in ("id", "title", "category", "urgency", "affected_users",
                    "priority", "status", "assigned_to"):
            with self.subTest(missing=key):
                ticket = make_ticket()
                del ticket[key]
                self.assert_rejected([ticket])

    def test_invalid_field_values_rejected(self):
        bad_values = {
            "id": ["", "X001", "T1", 7, None],
            "title": ["", "   ", None],
            "category": ["Plumbing", "network", None],
            "urgency": ["urgent", "HIGH", None],
            "status": ["done", "Open", None],
            "priority": ["urgent", "CRITICAL", None],
        }
        for field, values in bad_values.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    self.assert_rejected([make_ticket(**{field: value})])

    def test_invalid_affected_users_rejected(self):
        for value in (0, -3, 2.5, "5", True, False, None):
            with self.subTest(value=value):
                self.assert_rejected([make_ticket(affected_users=value)])

    def test_priority_that_contradicts_urgency_and_users_rejected(self):
        ticket = make_ticket(urgency="low", affected_users=1, priority="critical")
        self.assert_rejected([ticket])

    def test_in_progress_without_assignee_rejected(self):
        self.assert_rejected([make_ticket(status="in_progress", assigned_to=None)])

    def test_blank_assignee_rejected(self):
        self.assert_rejected([make_ticket(assigned_to="   ")])

    def test_malformed_notes_rejected(self):
        bad_notes = [
            "not a list",
            ["not a dict"],
            [{"note_id": "N001", "author": "A"}],                      # missing message
            [{**make_note(), "extra": "x"}],                           # extra key
            [make_note(note_id="X1")],                                 # bad note ID
            [make_note(author="  ")],                                  # blank author
            [make_note(message="")],                                   # blank message
        ]
        for notes in bad_notes:
            with self.subTest(notes=notes):
                self.assert_rejected([make_ticket(notes=notes)])

    def test_duplicate_note_id_in_one_ticket_rejected(self):
        notes = [make_note("N001"), make_note("N001", message="A different message")]
        self.assert_rejected([make_ticket(notes=notes)])

    def test_same_note_id_on_different_tickets_is_allowed(self):
        tickets = [
            make_ticket(id="T001", notes=[make_note("N001")]),
            make_ticket(id="T002", notes=[make_note("N001")]),
        ]
        save_tickets(tickets, self.path)
        self.assertEqual(load_tickets(self.path), tickets)


class TestOldTicketsAndFailedLoads(StorageTestCase):

    def test_old_ticket_without_notes_loads_with_empty_notes(self):
        old = make_ticket()
        del old["notes"]
        self.write_raw(json.dumps([old]))

        loaded = load_tickets(self.path)

        self.assertEqual(len(loaded), 1)                 # not discarded
        self.assertEqual(loaded[0]["id"], "T001")
        self.assertEqual(loaded[0]["notes"], [])

    def test_failed_load_leaves_in_memory_tickets_unchanged(self):
        save_tickets([make_ticket(id="T001"), make_ticket(id="T002")], self.path)
        tickets = load_tickets(self.path)
        snapshot = copy.deepcopy(tickets)

        self.write_raw(json.dumps([make_ticket(id="T009"), make_ticket(id="T009")]))
        try:
            tickets = load_tickets(self.path)   # same pattern the CLI must use
        except StorageError:
            pass

        self.assertEqual(tickets, snapshot)

    def test_failed_load_does_not_modify_the_file(self):
        bad = json.dumps([make_ticket(status="done")])
        self.write_raw(bad)
        with self.assertRaises(StorageError):
            load_tickets(self.path)
        self.assertEqual(self.read_raw(), bad)


class TestIdContinuity(StorageTestCase):

    def test_next_ticket_id_after_reload_does_not_collide(self):
        save_tickets([make_ticket(id="T001"), make_ticket(id="T005")], self.path)
        reloaded = load_tickets(self.path)
        self.assertEqual(generate_next_id(reloaded), "T006")

    def test_next_note_id_after_reload_does_not_collide(self):
        from campusflow.notes import next_note_id    # needs the notes issue done

        ticket = make_ticket(notes=[make_note("N001"), make_note("N002")])
        save_tickets([ticket], self.path)
        reloaded = load_tickets(self.path)
        self.assertEqual(next_note_id(reloaded[0]), "N003")


if __name__ == "__main__":
    unittest.main()