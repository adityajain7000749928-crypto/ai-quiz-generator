# 📝 AI Quiz Generator

A Gen AI mini project that creates multiple-choice quizzes on any topic using **Google Gemini**, with a clean **Streamlit** interface.

**Live demo:** https://ai-quiz-generator-bymedicaps.streamlit.app

## Features
- Any topic, 3-10 questions, Easy / Medium / Hard
- Instant scoring with a per-question review and explanations
- Retake the same quiz, start a new one, or download a text report
- Validates and retries the AI output so the app does not crash on bad JSON

## Architecture
```
User input (topic, difficulty, count)
        |
   app.py (Streamlit UI)
        |
   quiz_engine.py -> builds prompt -> Gemini API -> JSON
        |
   validate_quiz() cleans and checks the questions
        |
   UI renders quiz -> scores answers -> shows review
```

| File | Purpose |
|------|---------|
| `app.py` | Streamlit user interface |
| `quiz_engine.py` | Prompt, Gemini call, retries, validation |
| `test_quiz_engine.py` | Unit tests for validation |
| `.streamlit/config.toml` | Theme settings |
| `.streamlit/secrets.toml.example` | Template for the API key |

## Run Locally
```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
export GEMINI_API_KEY="your_key"  # Windows: set GEMINI_API_KEY=your_key
streamlit run app.py
```
Get a free key at https://aistudio.google.com/apikey

## Run Tests
```bash
pip install -r requirements-dev.txt
pytest
```

## Deploy (Streamlit Community Cloud)
1. Push this repo to GitHub.
2. Go to https://share.streamlit.io, click **Create app**, choose the repo and `app.py`.
3. In **Advanced settings -> Secrets** add: `GEMINI_API_KEY = "your_key"`
4. Click **Deploy**.

## Tech Stack
Python, Streamlit, Google Gemini API (`google-genai`)
