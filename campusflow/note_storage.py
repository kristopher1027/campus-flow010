
"""Save and load follow-up notes as JSON."""

import json
import os

NOTES_PATH = os.path.join("data", "notes.json")


def save_notes(notes, path=NOTES_PATH):
    """Save notes to a JSON file."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    temp_path = path + ".tmp"

    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(notes, file, indent=2)
        os.replace(temp_path, path)
    except (OSError, TypeError) as error:
        raise ValueError(
            f"Could not save notes to '{path}': {error}"
        ) from error


def load_notes(path=NOTES_PATH):
    """Load notes from a JSON file, or return an empty list."""
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            notes = json.load(file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(
            f"Could not load notes from '{path}': {error}"
        ) from error

    if not isinstance(notes, list) or not all(
        isinstance(note, dict) for note in notes
    ):
        raise ValueError(
            f"'{path}' must contain a list of notes."
        )

    return notes
