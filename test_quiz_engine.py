import pytest

from quiz_engine import QuizError, validate_quiz

GOOD = {"question": "2+2?", "options": ["1", "2", "3", "4"], "answer": "4", "explanation": "Math."}


def test_valid_question_passes():
    assert validate_quiz([GOOD])[0]["answer"] == "4"


def test_letter_answer_is_mapped():
    q = {**GOOD, "answer": "D"}
    assert validate_quiz([q])[0]["answer"] == "4"


def test_wrapped_in_dict():
    assert len(validate_quiz({"questions": [GOOD]})) == 1


def test_bad_items_are_dropped():
    bad = {"question": "x", "options": ["a", "b"], "answer": "a"}
    assert len(validate_quiz([GOOD, bad])) == 1


def test_all_bad_raises():
    with pytest.raises(QuizError):
        validate_quiz([{"question": "x"}])
