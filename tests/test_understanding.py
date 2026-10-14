import unittest
from unittest.mock import patch

import main
from campusflow.understanding_check import (
    QUESTIONS,
    is_valid_choice,
    run_check,
    score_answers,
)


class TestChoiceValidation(unittest.TestCase):

    def test_accepts_a_to_d_case_insensitively(self):
        for choice in ("A", "b", "C", "d", " a "):
            with self.subTest(choice=choice):
                self.assertTrue(is_valid_choice(choice))

    def test_rejects_other_values(self):
        for choice in ("E", "", "1", None):
            with self.subTest(choice=choice):
                self.assertFalse(is_valid_choice(choice))


class TestScoreAnswers(unittest.TestCase):

    def test_all_correct_gives_six(self):
        answers = [question["answer"] for question in QUESTIONS]
        self.assertEqual(score_answers(QUESTIONS, answers), 6)

    def test_all_wrong_gives_zero(self):
        answers = ["A" if q["answer"] != "A" else "B" for q in QUESTIONS]
        self.assertEqual(score_answers(QUESTIONS, answers), 0)

    def test_mixed_answers_score_correctly(self):
        answers = [question["answer"] for question in QUESTIONS]
        answers[1] = "A"
        answers[4] = "D"
        self.assertEqual(score_answers(QUESTIONS, answers), 4)

    def test_lowercase_answer_is_scored_correctly(self):
        answers = [question["answer"].lower() for question in QUESTIONS]
        self.assertEqual(score_answers(QUESTIONS, answers), 6)


class TestRunCheck(unittest.TestCase):

    def test_invalid_answers_retry_and_two_explanations_are_shown(self):
        supplied = iter(["E", "", "1", "b"] + [q["answer"] for q in QUESTIONS[1:]] + [
            "First explanation", "Second explanation"
        ])
        displayed = []

        score = run_check(QUESTIONS, lambda _prompt: next(supplied), displayed.append)

        self.assertEqual(score, 6)
        self.assertEqual(sum("Please enter A, B, C, or D." in s for s in displayed), 3)
        self.assertTrue(any("First explanation" in s for s in displayed))
        self.assertTrue(any("Second explanation" in s for s in displayed))

    def test_feedback_is_shown_after_valid_answer_and_score_uses_submitted_answer(self):
        questions = QUESTIONS[:1]
        answers = iter(["b", "A written explanation", "Another explanation"])
        displayed = []

        score = run_check(questions, lambda _prompt: next(answers), displayed.append)

        correct_index = displayed.index("Correct.")
        self.assertGreater(correct_index, 0)
        self.assertEqual(score, 1)

    def test_incorrect_valid_answers_score_zero(self):
        answers = iter(["A"] * len(QUESTIONS) + ["Reason one", "Reason two"])
        score = run_check(QUESTIONS, lambda _prompt: next(answers), lambda _text: None)
        self.assertEqual(score, 0)

    def test_menu_has_understanding_check_option(self):
        with patch("builtins.print") as print_output:
            main.show_menu()
        menu_text = "\n".join(str(call.args[0]) for call in print_output.call_args_list)
        self.assertIn("12. Understanding Check", menu_text)


if __name__ == "__main__":
    unittest.main()
