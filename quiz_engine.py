"""Core logic: prompt building, calling Gemini, and validating the quiz JSON."""
import json
import os
import re

DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")


class QuizError(Exception):
    """Raised when a quiz cannot be generated or parsed."""


def build_prompt(topic: str, n: int, difficulty: str) -> str:
    return f"""You are an expert teacher. Create {n} multiple-choice questions on the topic "{topic}"
at {difficulty} difficulty.

Rules:
- Each question has exactly 4 options.
- Exactly one option is correct.
- "answer" must be copied exactly from one of the options.
- Keep explanations to 1-2 sentences.
- Do not repeat questions.

Return ONLY a JSON list in this format:
[
  {{"question": "...", "options": ["A", "B", "C", "D"], "answer": "A", "explanation": "..."}}
]"""


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def validate_quiz(data) -> list:
    """Check the model output and return a clean list of questions."""
    if isinstance(data, dict):
        data = data.get("questions", [])
    if not isinstance(data, list):
        raise QuizError("Quiz data is not a list.")

    clean = []
    for item in data:
        if not isinstance(item, dict):
            continue
        question = str(item.get("question", "")).strip()
        options = item.get("options")
        if not question or not isinstance(options, list) or len(options) != 4:
            continue
        options = [str(o).strip() for o in options]
        answer = str(item.get("answer", "")).strip()

        # Accept a letter answer such as "B" and map it to the option text
        if answer.upper() in {"A", "B", "C", "D"} and answer not in options:
            answer = options["ABCD".index(answer.upper())]
        # Accept case/whitespace differences
        match = next((o for o in options if o.lower() == answer.lower()), None)
        if match is None:
            continue

        clean.append(
            {
                "question": question,
                "options": options,
                "answer": match,
                "explanation": str(item.get("explanation", "")).strip(),
            }
        )

    if not clean:
        raise QuizError("The AI returned no usable questions.")
    return clean


def generate_quiz(topic: str, n: int, difficulty: str, api_key: str,
                  model: str = DEFAULT_MODEL, retries: int = 2) -> list:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=api_key)
    prompt = build_prompt(topic, n, difficulty)
    last_error = None

    for _ in range(retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json", temperature=0.7
                ),
            )
            return validate_quiz(json.loads(_strip_fences(response.text)))
        except (json.JSONDecodeError, QuizError) as e:
            last_error = e  # bad output, try again
        except Exception as e:
            raise QuizError(f"Gemini API error: {e}") from e

    raise QuizError(f"Could not get a valid quiz after several tries ({last_error}).")
