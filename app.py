import streamlit as st
import openai
import re
import textwrap
import time
from io import BytesIO
from docx import Document
from docx.shared import Pt
from fpdf import FPDF

import streamlit as st
import openai

st.write("OpenAI library version:", openai.__version__)


# --- SETUP ---
st.set_page_config(page_title="Planomy Teacher Super Aid", layout="wide")

# Load API key from secrets
openai.api_key = st.secrets.get("OPENAI_API_KEY")
if not openai.api_key:
    st.warning("Please enter your OpenAI API key in the Streamlit secrets.")
    st.stop()

# --- SIDEBAR: TOOL SELECTION ---
st.sidebar.title("PLANOMY - Where you're the ✨ Star ✨")
tool = st.sidebar.radio(
    "Choose a tool:", 
    ["Lesson Builder", "Feedback Assistant", "Email Assistant", "Unit Glossary Generator", "Unit Planner"]
)

# ========== HELPER FUNCTION ==========
def chat_completion_request(system_msg, user_msg, max_tokens=1000, temperature=0.7):
    """
    A helper to call GPT-3.5-turbo with system & user messages.
    Make sure your environment has openai>=0.27.0.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg}
        ],
        max_tokens=max_tokens,
        temperature=temperature
    )
    return response.choices[0].message.content.strip()

# ========== TOOL 1: LESSON BUILDER ==========
if tool == "Lesson Builder":
    st.header("📝 Lesson Builder")
    year = st.selectbox("Year Level", ["7", "8", "9", "10", "11", "12"])
    subject = st.text_input("Subject (e.g. English, Science)")
    topic = st.text_input("Lesson Topic or Focus")
    duration = st.slider("Lesson Duration (minutes)", 30, 120, 70, step=5)
    lesson_count = st.selectbox("How many lessons do you want?", ["1", "2", "3", "4", "5"])
    goal_focus = st.selectbox("Learning Goal Focus", ["Skills-Based", "Knowledge-Based", "Critical Thinking", "Creative Thinking"])
    include_curriculum = st.checkbox("Include V9 curriculum reference")
    device_use = st.selectbox("Device Use", ["Laptops", "iPads", "Both", "No Devices"])
    grouping = st.selectbox("Grouping Preference", ["Individual", "Pairs", "Small Groups", "Whole Class"])
    differentiation = st.multiselect("Include Differentiation for:", ["Support", "Extension", "ESL", "Neurodiverse"])
    lesson_style = st.selectbox("Lesson Style", ["Hands-On", "Discussion-Based", "Quiet/Reflective", "Creative"])
    assessment = st.selectbox("Assessment Format", ["No Assessment", "Exit Slip", "Short Response", "Group Presentation", "Quiz"])

    if st.button("Generate Lesson Plan"):
        prompt_parts = [
            f"Create {lesson_count} lesson(s), each {duration} minutes long, for a Year {year} {subject} class on '{topic}'.",
            f"Start each lesson with a clear Learning Goal aligned to a {goal_focus.lower()} outcome.",
            "Structure each lesson with: Hook, Learning Intentions, Warm-up, Main Task, Exit Ticket.",
            f"The lesson should use {device_use.lower()}. Students should work in {grouping.lower()}.",
            f"Use a {lesson_style.lower()} approach."
        ]
        if differentiation:
            prompt_parts.append("Include differentiation strategies for: " + ", ".join(differentiation) + ".")
        if assessment != "No Assessment":
            prompt_parts.append(f"End each lesson with a {assessment.lower()} as an assessment.")
        if include_curriculum:
            prompt_parts.append("Align the lesson with the Australian V9 curriculum.")

        full_prompt = " ".join(prompt_parts)

        with st.spinner("Planning your lesson(s)..."):
            lesson_plan = chat_completion_request(
                system_msg="You are a practical, creative Australian teacher.",
                user_msg=full_prompt,
                max_tokens=1200
            )
            # Simple formatting
            formatted_plan = lesson_plan.replace("* ", "• ")
            formatted_plan = re.sub(r"^#+\s*(.+)$", r"<br><b>\1</b>", formatted_plan, flags=re.MULTILINE)
            st.markdown(
                f"""
                <div style='background-color: #f9f9f9; padding: 20px; border-radius: 8px;
                            font-family: sans-serif; font-size: 16px; color: #111;
                            line-height: 1.6; white-space: pre-wrap;'>
                    {formatted_plan.replace("\n", "<br>")}
                </div>
                """,
                unsafe_allow_html=True
            )

# ========== TOOL 2: FEEDBACK ASSISTANT ==========
elif tool == "Feedback Assistant":
    st.header("🧠 Feedback Assistant")
    student_text = st.text_area("Paste student writing here:")
    tone = st.selectbox("Choose feedback tone", ["Gentle", "Firm", "Colloquial"])

    if st.button("Generate Feedback"):
        feedback_prompt = (
            f"Give feedback on the following student writing using the Star and 2 Wishes model. "
            f"Highlight errors in spelling, grammar, cohesion, repetition, and sentence structure by surrounding them with **bold**. "
            f"Use a {tone.lower()} tone.\n\n"
            f"Student text:\n{student_text}"
        )
        with st.spinner("Analysing writing..."):
            feedback = chat_completion_request(
                system_msg="You are a kind, helpful teacher giving writing feedback.",
                user_msg=feedback_prompt,
                max_tokens=800
            )
            st.markdown(feedback, unsafe_allow_html=True)

# ========== TOOL 3: EMAIL ASSISTANT ==========
elif tool == "Email Assistant":
    st.header("✉️ Email Assistant")
    recipient = st.selectbox("Who is the email to?", ["Parent", "Student", "Staff", "Other"])
    context = st.text_area("Briefly describe the situation or what you want to say:")
    tone = st.selectbox("Choose tone", ["Supportive", "Professional", "Friendly"])

    if st.button("Generate Email"):
        email_prompt = (
            f"Write a {tone.lower()} email to a {recipient.lower()} about the following situation:\n"
            f"{context}\n\n"
            f"Keep the email clear, respectful, and well-structured."
        )
        with st.spinner("Writing your email..."):
            email_content = chat_completion_request(
                system_msg="You are an experienced teacher writing professional school emails.",
                user_msg=email_prompt,
                max_tokens=800
            )
            st.markdown(email_content)

# ========== TOOL 4: UNIT GLOSSARY GENERATOR ==========
elif tool == "Unit Glossary Generator":
    st.header("📘 Unit Glossary Generator")
    subject = st.text_input("Subject (e.g. Science, HASS)")
    topic = st.text_input("Topic or Unit Focus (e.g. Body Systems, Volcanoes)")
    year = st.selectbox("Year Level", ["3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])

    if st.button("Generate Glossary"):
        glossary_prompt = (
            f"Create a 3-tier vocabulary glossary for a Year {year} {subject} unit on '{topic}'. "
            "Use this structure:\n"
            "Tier 1 (General): 10 basic words students must know.\n"
            "Tier 2 (Core): 7 subject-specific words they will encounter in lessons.\n"
            "Tier 3 (Stretch): 5 challenge words that extend thinking.\n\n"
            "Use bullet points. Keep each definition under 20 words. "
            "Use student-friendly language, especially for primary year levels."
        )
        with st.spinner("Generating vocabulary list..."):
            glossary = chat_completion_request(
                system_msg="You are a helpful and experienced curriculum-aligned teacher.",
                user_msg=glossary_prompt,
                max_tokens=700
            )
            st.markdown(glossary)

# ========== TOOL 5: UNIT PLANNER ==========
elif tool == "Unit Planner":
    st.header("📘 Unit Planner")
    unit_year = st.selectbox("Year Level", ["3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])
    unit_subject = st.text_input("Subject (e.g. HASS, English, Science)")
    unit_topic = st.text_input("Unit Topic or Focus (e.g. Ancient Egypt, Persuasive Writing)")
    unit_weeks = st.slider("Estimated Duration (Weeks)", 1, 10, 5)
    include_assessment = st.checkbox("Include Assessment Suggestions?")
    include_hook = st.checkbox("Include Hook Ideas for Lesson 1?")
    include_fast_finishers = st.checkbox("Include Fast Finisher Suggestions?")
    include_cheat_sheet = st.checkbox("Include Quick Content Cheat Sheet (for teacher)?")

    if st.button("Generate Unit Plan"):
        prompt_parts = [
            f"Create a unit plan overview for a Year {unit_year} {unit_subject} unit on '{unit_topic}'.",
            f"The unit runs for approximately {unit_weeks} weeks.",
            "Include the following sections:",
            "1. A short Unit Overview (what it's about).",
            "2. 3–5 clear Learning Intentions.",
            "3. A list of lesson types or activity ideas that would suit this unit."
        ]
        if include_assessment:
            prompt_parts.append("4. Include 1–2 assessment ideas (format only, keep it brief).")
        if include_hook:
            prompt_parts.append("5. Suggest 2–3 engaging Hook Ideas for Lesson 1.")
        if include_fast_finishers:
            prompt_parts.append("6. Suggest Fast Finisher or Extension Task ideas.")
        if include_cheat_sheet:
            prompt_parts.append("7. Provide a Quick Content Cheat Sheet: 10 bullet-point facts a teacher should know to teach this unit.")

        full_prompt = " ".join(prompt_parts)

        with st.spinner("Planning your unit..."):
            unit_plan_raw = chat_completion_request(
                system_msg="You are a practical and experienced curriculum-aligned teacher in Australia.",
                user_msg=full_prompt,
                max_tokens=1200
            )
            st.session_state["unit_plan_text"] = unit_plan_raw

    # If we have a generated plan, display it
    if "unit_plan_text" in st.session_state and st.session_state["unit_plan_text"]:
        unit_plan_raw = st.session_state["unit_plan_text"]

        # Clean up formatting (remove markdown syntax, etc.)
        unit_plan_clean = re.sub(r"\*\*(.*?)\*\*", r"\1", unit_plan_raw)
        unit_plan_clean = re.sub(r"^#+\s*", "", unit_plan_clean, flags=re.MULTILINE)
        unit_plan_clean = re.sub(r"\n{2,}", "\n", unit_plan_clean.strip())

        st.markdown("### Generated Unit Plan")
        st.markdown(
            f"""
            <div style="background-color: #ffffff; padding: 20px; border-radius: 6px;
                        font-family: 'Segoe UI', sans-serif; font-size: 16px; line-height: 1.7;
                        color: #222; white-space: pre-wrap;">
                {unit_plan_clean}
            </div>
            """, 
            unsafe_allow_html=True
        )

        # --- DOCX EXPORT ---
        word_buffer = BytesIO()
        doc = Document()
        for line in unit_plan_clean.split("\n"):
            if line.strip():
                doc.add_paragraph(line.strip())
        doc.save(word_buffer)
        word_buffer.seek(0)
        st.download_button(
            label="📝 Download Word",
            data=word_buffer,
            file_name="unit_plan.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key="download_word_btn"
        )

        # --- PDF EXPORT ---
        pdf = FPDF()
        pdf.add_page()
        try:
            pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
            pdf.set_font("DejaVu", size=10)
        except Exception:
            pdf.set_font("Arial", size=10)

        for line in unit_plan_clean.split("\n"):
            pdf.multi_cell(0, 8, line)
        pdf_buffer = BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin-1')
        pdf_buffer.write(pdf_output)
        pdf_buffer.seek(0)
        st.download_button(
            label="📎 Download PDF",
            data=pdf_buffer,
            file_name="unit_plan.pdf",
            mime="application/pdf",
            key="download_pdf_btn"
        )
