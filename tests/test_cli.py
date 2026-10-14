import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main
from campusflow.note_storage import load_notes
from campusflow.tickets import create_ticket


class TestCliHandlers(unittest.TestCase):

    def setUp(self):
        self.tickets = []
        create_ticket(self.tickets, "Wi-Fi down", "Network", "high", 2)
        self.notes = []

    def test_invalid_menu_choice_is_reported_and_returns_to_menu(self):
        with patch.object(main, "load_tickets", return_value=self.tickets), \
             patch.object(main, "load_notes", return_value=self.notes), \
             patch.object(main, "save_tickets") as save_tickets, \
             patch("builtins.input", side_effect=["99", "13"]), \
             patch("builtins.print") as print_output:
            main.main()

        messages = [str(call.args[0]) for call in print_output.call_args_list]
        self.assertTrue(any("Invalid choice" in message for message in messages))
        self.assertTrue(any("Goodbye." in message for message in messages))
        save_tickets.assert_called_once()

    def test_invalid_search_filter_reprompts_then_accepts_valid_choice(self):
        with patch("builtins.input", side_effect=["Wi-Fi", "Wrong", "Network", "", ""]), \
             patch("builtins.print") as print_output:
            main.handle_search(self.tickets)

        messages = [str(call.args[0]) for call in print_output.call_args_list]
        self.assertTrue(any("Invalid category" in message for message in messages))
        self.assertTrue(any("Wi-Fi down" in message for message in messages))

    def test_rejected_note_shows_error_and_does_not_save(self):
        with patch("builtins.input", side_effect=["T999", "A note"]), \
             patch.object(main, "save_notes") as save_notes, \
             patch("builtins.print") as print_output:
            main.handle_add_note(self.tickets, self.notes)

        save_notes.assert_not_called()
        self.assertEqual(self.notes, [])
        self.assertTrue(any("No ticket found" in str(call) for call in print_output.call_args_list))

    def test_note_add_and_view_round_trip_with_simulated_input(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = str(Path(temp_dir) / "notes.json")
            with patch.object(main, "NOTES_PATH", path), \
                 patch("builtins.input", side_effect=["T001", "Check router"]), \
                 patch("builtins.print") as add_output:
                main.handle_add_note(self.tickets, self.notes)

            reloaded_notes = load_notes(path)
            self.assertEqual(reloaded_notes, [
                {"id": 1, "ticket_id": "T001", "text": "Check router"}
            ])
            self.assertTrue(any("added to ticket T001" in str(call) for call in add_output.call_args_list))

            with patch("builtins.input", return_value="T001"), \
                 patch("builtins.print") as view_output:
                main.handle_view_notes(self.tickets, reloaded_notes)

            self.assertTrue(any("Note 1: Check router" in str(call) for call in view_output.call_args_list))

    def test_view_notes_without_notes_shows_friendly_message(self):
        with patch("builtins.input", return_value="T001"), \
             patch("builtins.print") as print_output:
            main.handle_view_notes(self.tickets, [])

        self.assertTrue(any("No notes found for ticket T001" in str(call) for call in print_output.call_args_list))


if __name__ == "__main__":
    unittest.main()
