# Install first:
# pip install google-generativeai streamlit streamlit-js-eval

import streamlit as st
import google.generativeai as genai
from streamlit_js_eval import streamlit_js_eval

# Configure Gemini API
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# Page settings
st.set_page_config(page_title="JobBot", page_icon="🤖")
st.title("🌟JobBot")

# --- Session state initialization ---
defaults = {
    "setup_complete": False,
    "user_message_count": 0,
    "feedback_shown": False,
    "chat_complete": False,
    "messages": [],
    "gemini_model": "gemini-1.5-flash"  # free, fast
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Helper functions
def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

# --- Setup Stage ---
if not st.session_state.setup_complete:
    st.subheader('Personal Information', divider="rainbow")

    st.session_state["name"] = st.text_input("Name", value=st.session_state.get("name", ""), placeholder="Enter your name", max_chars=40)
    st.session_state["experience"] = st.text_area("Experience", value=st.session_state.get("experience", ""), placeholder="Describe your experience", max_chars=200)
    st.session_state["skills"] = st.text_area("Skills", value=st.session_state.get("skills", ""), placeholder="List your skills", max_chars=200)

    st.subheader('Company and Position', divider="rainbow")

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["level"] = st.radio(
            "Choose level",
            options=["Junior", "Mid-level", "Senior"],
            index=["Junior", "Mid-level", "Senior"].index(st.session_state.get("level", "Junior"))
        )

    with col2:
        st.session_state["position"] = st.selectbox(
            "Choose a position",
            ("Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst"),
            index=("Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst").index(
                st.session_state.get("position", "Data Scientist")
            )
        )

    st.session_state["company"] = st.selectbox(
        "Select a Company",
        ("Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify"),
        index=("Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify").index(
            st.session_state.get("company", "Amazon")
        )
    )

    if st.button("Start Interview", on_click=complete_setup):
        st.write("Setup complete. Starting interview...")

# --- Interview Stage ---
if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:
    st.info("Start by introducing yourself.", icon="👋")

    if not st.session_state.messages:
        # Enhanced system prompt for clarity & depth
        st.session_state.messages = [{
            "role": "system",
            "content": (
                f"You are a professional HR interviewer. Your task is to conduct a structured interview "
                f"with {st.session_state['name']}, who has {st.session_state['experience']} experience "
                f"and skills in {st.session_state['skills']}. The position is {st.session_state['level']} "
                f"{st.session_state['position']} at {st.session_state['company']}.\n"
                f"- Ask one question at a time.\n"
                f"- Tailor questions based on previous answers.\n"
                f"- Be concise and clear.\n"
                f"- After each user answer, evaluate it briefly (1-2 sentences) before moving to the next question."
            )
        }]

    # Show chat so far
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Limit interview to 5 questions
    if st.session_state.user_message_count < 6:
        if prompt := st.chat_input("Your response", max_chars=1000):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 6:
                with st.chat_message("assistant"):
                    conversation = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.messages)
                    model = genai.GenerativeModel(st.session_state["gemini_model"])
                    response = model.generate_content(conversation)
                    st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

            st.session_state.user_message_count += 1

    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

# --- Feedback Stage ---
if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

if st.session_state.feedback_shown:
    st.subheader("Feedback")

    conversation_history = "\n".join(f"{m['role']}: {m['content']}" for m in st.session_state.messages)

    # Gemini feedback with question-by-question scoring
    feedback_prompt = f"""
    You are an interview evaluator. Analyze the following interview.
    For each question asked by the interviewer, give:
    - Score from 1 to 10 for the candidate's answer.
    - Short constructive feedback.
    Then, give an overall score and summary feedback.

    Interview:
    {conversation_history}
    """

    model = genai.GenerativeModel(st.session_state["gemini_model"])
    feedback = model.generate_content(feedback_prompt)

    st.markdown(feedback.text)

    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")
