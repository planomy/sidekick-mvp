import streamlit as st
import openai
import os
from io import BytesIO
from docx import Document
from datetime import datetime

# ----------------------- CONFIGURATION -----------------------
st.set_page_config(page_title="Student Assignment Planner", layout="wide")

# ----------------------- HELPER FUNCTIONS -----------------------
def chat_completion_request(system_msg: str, user_msg: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
    """
    Wrapper for OpenAI chat completion with Australian spelling directive.
    """
    au_system = system_msg + "\nPlease use Australian spelling and terminology."
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": au_system},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"API call error: {e}")
        return ""


def display_output_block(text: str):
    """
    Render generated text in a styled container.
    """
    html = text.replace("\n", "<br>")
    st.markdown(
        f"""
        <div style='background:#f9f9f9; padding:20px; border-radius:8px; font-family:sans-serif;'>
            {html}
        </div>
        """, unsafe_allow_html=True
    )


def export_to_word(text: str) -> BytesIO:
    """
    Export text to a .docx and return a BytesIO buffer.
    """
    buf = BytesIO()
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    doc.save(buf)
    buf.seek(0)
    return buf

# ----------------------- FEATURE MODULES -----------------------
def assignment_input():
    st.header("📌 Assignment Details")
    subject = st.text_input("Subject (e.g. English, History)")
    title = st.text_input("Assignment Title")
    due_date = st.date_input("Due Date")
    total_words = st.number_input("Total Word Count", min_value=100, step=100)
    assignment_type = st.selectbox(
        "Assignment Type",
        ["Essay", "Report", "Narrative", "Presentation", "Reflection"]
    )
    extra = st.text_area("Additional Requirements / Rubric Notes")

    if st.button("Generate Plan"):
        # Build prompt
        prompt = (
            f"You are an expert student writing assistant. \n"
            f"Generate a comprehensive plan for a {assignment_type.lower()} titled '{title}' in {subject}. "
            f"The plan is due on {due_date.strftime('%d %B %Y')} with a total of {total_words} words. "
            f"Include: \n"
            f"1. A structured outline (Introduction, X body paragraphs, Conclusion) \n"
            f"2. A word-budget breakdown per section \n"
            f"3. A list of 5–7 main points to choose from \n"
            f"4. For each selected main point, 3 bullet-point prompts \n"
            f"5. A brief style guide (tone, point of view, tense) \n"
            f"6. Tips for meeting rubric criteria. "
            f"{f'Extra context: {extra}' if extra else ''}"
        )
        with st.spinner("Generating your assignment plan..."):
            plan = chat_completion_request(
                system_msg="You are a helpful, concise student assistant.",
                user_msg=prompt,
                max_tokens=1200
            )
        display_output_block(plan)
        # Export option
        word_buf = export_to_word(plan)
        st.download_button(
            label="📄 Download Plan (Word)",
            data=word_buf,
            file_name="assignment_plan.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

# ----------------------- MAIN APP -----------------------
def main():
    # Initialize API key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        st.warning("Set OPENAI_API_KEY in environment.")
        st.stop()

    assignment_input()

if __name__ == "__main__":
    main()
