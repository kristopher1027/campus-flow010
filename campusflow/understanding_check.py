"""Interactive knowledge check about CampusFlow behaviour."""

QUESTIONS = [
    {
        "prompt": "What happens when an unassigned open ticket is moved to in_progress?",
        "options": {
            "A": "The ticket is assigned automatically",
            "B": "The transition is rejected and ticket data is preserved",
            "C": "The ticket is resolved",
            "D": "The ticket is deleted",
        },
        "answer": "B",
    },
    {
        "prompt": "What resolution percentage does an empty ticket list produce?",
        "options": {
            "A": "100%",
            "B": "An error",
            "C": "0%",
            "D": "Undefined",
        },
        "answer": "C",
    },
    {
        "prompt": "What does a search for title wifi + Network + open return?",
        "options": {
            "A": "Every open ticket",
            "B": "Only records matching all supplied filters",
            "C": "Every Network ticket",
            "D": "A fuzzy match across all tickets",
        },
        "answer": "B",
    },
    {
        "prompt": "What happens if a resolved ticket receives an Add note request?",
        "options": {
            "A": "The note is attached and the ticket stays resolved",
            "B": "The ticket is reopened automatically",
            "C": "The request is rejected until the ticket is reopened",
            "D": "The note is attached to every ticket",
        },
        "answer": "C",
    },
    {
        "prompt": "What happens when a JSON file contains two tickets with the same ID?",
        "options": {
            "A": "The later ticket replaces the first",
            "B": "Both tickets are loaded",
            "C": "Loading is rejected without changing current memory",
            "D": "A new ID is generated automatically",
        },
        "answer": "C",
    },
    {
        "prompt": "A pull request has no tests for negative cases. What is the best review response?",
        "options": {
            "A": "Approve because happy paths are enough",
            "B": "Request focused tests and reasoning",
            "C": "Rewrite the feature without discussion",
            "D": "Ignore the missing tests",
        },
        "answer": "B",
    },
]

VALID_CHOICES = frozenset("ABCD")


def is_valid_choice(choice):
    """Return whether choice is one A/B/C/D, ignoring case and whitespace."""
    return isinstance(choice, str) and choice.strip().upper() in VALID_CHOICES


def score_answers(questions, answers):
    """Count correct answers without running the interactive menu loop."""
    return sum(
        1
        for question, answer in zip(questions, answers)
        if isinstance(answer, str)
        and answer.strip().upper() == question["answer"].upper()
    )


def run_check(questions, ask, show):
    """Ask each question, score submitted answers, and capture two explanations.

    ``ask`` receives a prompt and returns the user's text. ``show`` receives
    text to display. Explanations are displayed for mentor discussion and are
    not graded or persisted.
    """
    answers = []

    for index, question in enumerate(questions, start=1):
        show(f"\nQuestion {index}: {question['prompt']}")
        for letter, option in question["options"].items():
            show(f"  {letter}. {option}")

        while True:
            answer = ask("Your answer (A/B/C/D): ")
            if is_valid_choice(answer):
                answer = answer.strip().upper()
                answers.append(answer)
                # Record the first valid response before showing feedback.
                if answer == question["answer"].upper():
                    show("Correct.")
                else:
                    show(f"The correct answer is {question['answer']}.")
                break
            show("Please enter A, B, C, or D.")

    score = score_answers(questions, answers)
    show(f"Your score: {score} out of {len(questions)}.")

    explanations = []
    for number in range(1, 3):
        while True:
            explanation = ask(
                f"Briefly explain one answer for mentor discussion ({number}/2): "
            )
            if isinstance(explanation, str) and explanation.strip():
                explanations.append(explanation.strip())
                break
            show("Please enter a short explanation.")

    show("Your explanations for mentor discussion:")
    for number, explanation in enumerate(explanations, start=1):
        show(f"  {number}. {explanation}")
    return score
