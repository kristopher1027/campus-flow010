import os
import tempfile
import unittest

from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import create_ticket


class TestStorage(unittest.TestCase):

    def setUp(self):
        # A fresh temporary folder for every test; never touches the real data/ file.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.path = os.path.join(self.temp_dir.name, "tickets.json")

    def test_round_trip_preserves_tickets(self):
        tickets = []
        create_ticket(tickets, "Wi-Fi down", "Network", "high", 15)
        create_ticket(tickets, "Printer jam", "Hardware", "low", 1)
        save_tickets(tickets, self.path)
        self.assertEqual(load_tickets(self.path), tickets)

    def test_none_assigned_to_survives_round_trip(self):
        tickets = []
        create_ticket(tickets, "x", "Network", "low", 1)
        save_tickets(tickets, self.path)
        self.assertIsNone(load_tickets(self.path)[0]["assigned_to"])

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_empty_list_saves_and_loads(self):
        save_tickets([], self.path)
        self.assertEqual(load_tickets(self.path), [])

    def test_corrupt_json_raises_storage_error(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write("{ this is not valid json")
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_corrupt_file_is_not_overwritten(self):
        bad_text = "{ this is not valid json"
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(bad_text)
        with self.assertRaises(StorageError):
            load_tickets(self.path)
        with open(self.path, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), bad_text)

    def test_wrong_structure_raises_storage_error(self):
        for text in ('{"id": "T001"}', '["T001", "T002"]', '"hello"'):
            with self.subTest(text=text):
                with open(self.path, "w", encoding="utf-8") as f:
                    f.write(text)
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_duplicate_ticket_ids_are_rejected(self):
        duplicate_tickets = [
            {"id": "T001", "title": "First"},
            {"id": "T001", "title": "Second"},
        ]
        save_tickets(duplicate_tickets, self.path)

        current_memory = [{"id": "T999", "title": "Existing memory"}]
        with self.assertRaisesRegex(StorageError, "duplicate ticket ID"):
            loaded = load_tickets(self.path)
            current_memory[:] = loaded

        self.assertEqual(current_memory, [{"id": "T999", "title": "Existing memory"}])

    def test_save_creates_missing_folder(self):
        nested = os.path.join(self.temp_dir.name, "data", "sub", "tickets.json")
        save_tickets([], nested)
        self.assertTrue(os.path.exists(nested))

    def test_ids_stay_unique_after_reload(self):
        tickets = []
        create_ticket(tickets, "a", "Network", "low", 1)
        create_ticket(tickets, "b", "Network", "low", 1)
        save_tickets(tickets, self.path)

        reloaded = load_tickets(self.path)
        new_ticket = create_ticket(reloaded, "c", "Network", "low", 1)

        ids = [t["id"] for t in reloaded]
        self.assertEqual(new_ticket["id"], "T003")
        self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
