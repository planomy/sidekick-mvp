import streamlit as st
import openai
import os
from io import BytesIO
from docx import Document
from datetime import datetime

# ----------------------- CONFIGURATION -----------------------
st.set_page_config(page_title="Student Assignment Planner", layout="wide")

# ----------------------- HELPER FUNCTIONS -----------------------
def chat_completion_request(system_msg: str, user_msg: str, max_tokens: int = 1200, temperature: float = 0.7) -> str:
    """
    Wrapper for OpenAI chat completion with Australian spelling directive.
    """
    au_system = system_msg + "\nPlease use Australian spelling and terminology."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": au_system},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"API call error: {e}")
        return ""


def display_output_block(text: str):
    html = text.replace("\n", "<br>")
    st.markdown(
        f"""
        <div style='background:#f9f9f9; padding:20px; border-radius:8px; font-family:sans-serif;'>
            {html}
        </div>
        """, unsafe_allow_html=True
    )


def export_to_word(text: str) -> BytesIO:
    buf = BytesIO()
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    doc.save(buf)
    buf.seek(0)
    return buf

# ----------------------- ASSIGNMENT PLANNER MODULE -----------------------
def assignment_input():
    st.header("📌 Assignment Details")
    subject = st.text_input("Subject (e.g. English, History)", key="subject")
    title = st.text_input("Assignment Title", key="title")
    due_date = st.date_input("Due Date", key="due_date")
    total_words = st.number_input("Total Word Count", min_value=100, step=100, key="total_words")
    assignment_type = st.selectbox(
        "Assignment Type",
        ["Essay", "Report", "Narrative", "Presentation", "Reflection"],
        key="assignment_type"
    )
    extra = st.text_area("Additional Requirements / Rubric Notes", key="extra")

    # Step 1: Generate candidate main points
    if st.button("1️⃣ Generate Main Points"):
        if not subject or not title:
            st.error("Please enter both Subject and Assignment Title.")
        else:
            prompt = (
                f"Generate six concise, distinct main points for a {assignment_type.lower()} titled '{title}' in {subject}. "
                f"The assignment is due on {due_date.strftime('%d %B %Y')} and requires {total_words} words. Return each point as a single sentence."
            )
            with st.spinner("Generating main points..."):
                response = chat_completion_request("You are a helpful student assistant.", prompt)
            points = [p.strip().lstrip('0123456789. ') for p in response.split("\n") if p.strip()]
            st.session_state['candidate_points'] = points

    # Display and select main points (no defaults)
    candidate_points = st.session_state.get('candidate_points', [])
    if candidate_points:
        st.markdown("**Select up to 3 main points for your plan:**")
        selected_points = st.multiselect(
            "Main Points",
            options=candidate_points,
            help="Select at most 3 points",
            key="selected_points"
        )
        if len(selected_points) > 3:
            st.warning("Please select no more than 3 main points.")

        # Paragraph elements selector
        element_options = [
            "Topic sentence",
            "Context",
            "Evidence/Example",
            "Analysis",
            "Transition sentence",
            "Values/Attitudes/Beliefs",
            "Literary devices",
            "Aesthetic features",
            "Historical/Cultural context",
            "Authorial intention"
        ]
        default_elements = element_options[:5]
        paragraph_elements = st.multiselect(
            "Select paragraph elements:",
            options=element_options,
            default=default_elements,
            key="paragraph_elements",
            help="Core structure plus any extras required by your rubric"
        )

        # Step 2: Generate detailed plan
        if st.button("2️⃣ Generate Detailed Plan"):
            prompt_parts = [
                f"Create a world-class plan for a {assignment_type.lower()} titled '{title}' in {subject},"
                f" due {due_date.strftime('%d %B %Y')} with a total of {total_words} words.",
                "1. Generate a concise, analytical thesis statement for this assignment.",
                "2. Provide an outline: Introduction, 3 body paragraphs, and a Conclusion.",
                "3. For each body paragraph corresponding to the selected points, include the following elements in this exact order: "
                + ", ".join(paragraph_elements) + ".",
                *[f"   {idx}. {pt}" for idx, pt in enumerate(selected_points, 1)],
                "4. Suggest a word budget: 10% for Introduction, 80% divided equally among the 3 body paragraphs, 10% for Conclusion.",
                "5. At the end, provide a 100-word summary of the key content a student must know to start this assignment."
            ]
            if extra:
                prompt_parts.append(f"Extra rubric notes: {extra}")
            full_prompt = "\n".join(prompt_parts)
            with st.spinner("Generating detailed plan..."):
                plan = chat_completion_request("You are an expert student assistant.", full_prompt, max_tokens=1500)
            plan = plan.replace("**", "")
            display_output_block(plan)
            buf = export_to_word(plan)
            st.download_button(
                "📄 Download Detailed Plan (Word)",
                data=buf,
                file_name="detailed_assignment_plan.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

# ----------------------- MAIN APPLICATION -----------------------
def main():
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        st.warning("Set the OPENAI_API_KEY in your environment or Streamlit secrets.")
        st.stop()
    assignment_input()

if __name__ == "__main__":
    main()
