import os

import streamlit as st

from quiz_engine import QuizError, generate_quiz

st.set_page_config(page_title="AI Quiz Generator", page_icon="📝", layout="centered")

st.markdown(
    """
<style>
.hero {padding: 1.4rem 1.6rem; border-radius: 16px; margin-bottom: 1.2rem;
       background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); color: white;}
.hero h1 {margin: 0; font-size: 2rem; color: white;}
.hero p {margin: .3rem 0 0 0; opacity: .9;}
.footer {text-align:center; opacity:.6; font-size:.85rem; margin-top:2rem;}
</style>
<div class="hero">
  <h1>📝 AI Quiz Generator</h1>
  <p>Type any topic and get an instant multiple-choice quiz powered by Google Gemini.</p>
</div>
""",
    unsafe_allow_html=True,
)

SAMPLE_TOPICS = ["Python basics", "DBMS", "Machine Learning", "Indian History", "Operating Systems"]

# ---------- state ----------
for key, default in {"quiz": None, "answers": None, "quiz_id": 0, "meta": {}, "topic": ""}.items():
    st.session_state.setdefault(key, default)


def get_api_key():
    try:
        key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        key = None
    return key or os.getenv("GEMINI_API_KEY") or st.session_state.get("typed_key")


def set_topic(t):
    st.session_state.topic = t


def build_report(quiz, answers, meta):
    lines = [f"AI Quiz Report - {meta['topic']} ({meta['difficulty']})", ""]
    score = 0
    for i, (q, a) in enumerate(zip(quiz, answers), 1):
        ok = a == q["answer"]
        score += ok
        lines += [
            f"Q{i}. {q['question']}",
            f"   Your answer   : {a or 'Not answered'}",
            f"   Correct answer: {q['answer']}  [{'Correct' if ok else 'Wrong'}]",
            f"   Explanation   : {q['explanation']}",
            "",
        ]
    lines.append(f"Final score: {score}/{len(quiz)}")
    return "\n".join(lines)


# ---------- sidebar ----------
with st.sidebar:
    st.header("⚙️ Settings")
    n = st.slider("Number of questions", 3, 10, 5)
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
    if not (os.getenv("GEMINI_API_KEY") or "GEMINI_API_KEY" in getattr(st, "secrets", {})):
        st.text_input("Gemini API key", type="password", key="typed_key",
                      help="Free key: aistudio.google.com/apikey")
    st.caption("Built with Streamlit + Google Gemini")

# ---------- topic input ----------
st.text_input("Topic", key="topic", placeholder="e.g. Python basics, Photosynthesis, World War II")
cols = st.columns(len(SAMPLE_TOPICS))
for col, t in zip(cols, SAMPLE_TOPICS):
    col.button(t, key=f"s_{t}", on_click=set_topic, args=(t,), use_container_width=True)

if st.button("✨ Generate Quiz", type="primary", use_container_width=True):
    api_key = get_api_key()
    topic = st.session_state.topic.strip()
    if not api_key:
        st.error("Please add your Gemini API key in the sidebar (or as a secret).")
    elif not topic:
        st.warning("Please enter a topic first.")
    else:
        with st.spinner("Writing your quiz..."):
            try:
                st.session_state.quiz = generate_quiz(topic, n, difficulty, api_key)
                st.session_state.answers = None
                st.session_state.quiz_id += 1
                st.session_state.meta = {"topic": topic, "difficulty": difficulty}
            except QuizError as e:
                st.error(str(e))

quiz = st.session_state.quiz
meta = st.session_state.meta

# ---------- quiz form ----------
if quiz and st.session_state.answers is None:
    st.subheader(f"{meta['topic']} · {meta['difficulty']}")
    with st.form(f"quiz_form_{st.session_state.quiz_id}"):
        picks = []
        for i, q in enumerate(quiz):
            st.markdown(f"**Q{i + 1}. {q['question']}**")
            picks.append(
                st.radio("Options", q["options"], index=None,
                         key=f"q{st.session_state.quiz_id}_{i}", label_visibility="collapsed")
            )
            st.write("")
        submitted = st.form_submit_button("Submit answers", type="primary", use_container_width=True)
    if submitted:
        st.session_state.answers = picks
        st.rerun()

# ---------- results ----------
elif quiz:
    answers = st.session_state.answers
    score = sum(a == q["answer"] for q, a in zip(quiz, answers))
    pct = round(score / len(quiz) * 100)

    st.subheader("Your Results")
    c1, c2, c3 = st.columns(3)
    c1.metric("Score", f"{score}/{len(quiz)}")
    c2.metric("Percentage", f"{pct}%")
    c3.metric("Skipped", sum(a is None for a in answers))
    st.progress(pct / 100)
    if pct >= 80:
        st.balloons()
        st.success("Excellent work! 🎉")
    elif pct >= 50:
        st.info("Good effort. Review the explanations below to improve.")
    else:
        st.warning("Keep practicing. The explanations below will help.")

    for i, (q, a) in enumerate(zip(quiz, answers), 1):
        correct = a == q["answer"]
        with st.expander(f"{'✅' if correct else '❌'}  Q{i}. {q['question']}", expanded=not correct):
            st.write(f"**Your answer:** {a or 'Not answered'}")
            st.write(f"**Correct answer:** {q['answer']}")
            st.caption(q["explanation"])

    b1, b2, b3 = st.columns(3)
    if b1.button("🔁 Retake", use_container_width=True):
        st.session_state.answers = None
        st.session_state.quiz_id += 1
        st.rerun()
    if b2.button("🆕 New quiz", use_container_width=True):
        st.session_state.quiz = None
        st.session_state.answers = None
        st.rerun()
    b3.download_button("⬇️ Report", build_report(quiz, answers, meta),
                       file_name="quiz_report.txt", use_container_width=True)

st.markdown('<div class="footer">AI Quiz Generator · Gen AI Mini Project</div>', unsafe_allow_html=True)
