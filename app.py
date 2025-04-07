import streamlit as st
import openai
import random
from docx import Document
from docx.shared import Pt
from io import BytesIO
from fpdf import FPDF
import textwrap
import re

from docx import Document
from docx.shared import Pt

# Function to add bold headings with a specific size (11pt)
def add_heading(doc, text):
    heading = doc.add_paragraph()
    run = heading.add_run(text)
    run.bold = True  # Make the heading bold
    run.font.size = Pt(11)  # Set font size for the heading (11pt)

# Function to add bullet points with smaller text (10pt)
def add_bullet_points(doc, points):
    for point in points:
        para = doc.add_paragraph(style='List Bullet')
        run = para.add_run(point)
        run.font.size = Pt(10)  # Set font size for bullet points (10pt)

# Create a Document object
doc = Document()

# Example formatting for the existing sections and content
# Add formatted headings and bullet points as needed

# Unit Plan Overview heading
add_heading(doc, "Unit Plan Overview:")
# Assuming content comes from elsewhere (as you're not adding more content here)
# Add bullet points for content (no content added here, just formatting)
add_bullet_points(doc, ["<existing bullet points here>"])

# Repeat for other sections like Learning Intentions, Lesson Ideas, etc.
add_heading(doc, "Learning Intentions:")
add_bullet_points(doc, ["<existing bullet points here>"])

# Continue for other sections like Assessment, Cheat Sheets, etc.
add_heading(doc, "Assessment Ideas:")
add_bullet_points(doc, ["<existing bullet points here>"])

# Save the document after formatting
doc.save('formatted_unit_plan.docx')




# ---------- CONFIG ----------
st.set_page_config(page_title="Planomy Teacher Super Aid", layout="wide")

# ---------- API KEY INPUT ----------
st.sidebar.title("Where you're the ✨ Star ✨")
api_key = st.secrets["OPENAI_API_KEY"]
if not api_key:
    st.warning("Please enter your OpenAI API key in the sidebar to use the app.")
    st.stop()

client = openai.OpenAI(api_key=api_key)

# ---------- BOOST MESSAGE ----------
teacher_boosts = [
    "You're not just teaching—you’re shaping futures. 🎓",
    "Even when no one says it: you're doing an amazing job. 💪",
    "Teachers plant seeds that grow forever. 🌱",
    "You're someone's favourite part of the day. ✨",
    "You matter more than data ever could. 🧠❤️"
]

# ---------- TOOL SELECTION ----------
st.sidebar.title("✏️ Tools")
tool = st.sidebar.radio("Choose a tool:", ["Lesson Builder", "Feedback Assistant", "Email Assistant", "Unit Glossary Generator", "Unit Planner"])

# Reset session state when changing tools (ensure Unit Plan is cleared when switching tools)
if tool != "Unit Planner":
    if "unit_plan_text" in st.session_state:
        del st.session_state["unit_plan_text"]

# ---------- TOOL 1: LESSON BUILDER ----------
if tool == "Lesson Builder":
    st.header("📝 Lesson Builder")
    year = st.selectbox("Year Level", ["7", "8", "9", "10", "11", "12"])
    subject = st.text_input("Subject (e.g. English, Science)")
    topic = st.text_input("Lesson Topic or Focus")
    duration = st.slider("Lesson Duration (minutes)", 30, 120, 70, step=5)
    sequence = st.selectbox("How many lessons do you want?", ["1 (Single Lesson)", "2", "3", "4", "5 (Full Week)"])
    goal_focus = st.selectbox("Learning Goal Focus", ["Skills-Based", "Knowledge-Based", "Critical Thinking", "Creative Thinking"])
    include_curriculum = st.checkbox("Include V9 curriculum reference")
    device_use = st.selectbox("Device Use", ["Laptops", "iPads", "Both", "No Devices"])
    grouping = st.selectbox("Grouping Preference", ["Individual", "Pairs", "Small Groups", "Whole Class"])
    differentiation = st.multiselect("Include Differentiation for:", ["Support", "Extension", "ESL", "Neurodiverse"])
    lesson_style = st.selectbox("Lesson Style", ["Hands-On", "Discussion-Based", "Quiet/Reflective", "Creative"])
    assessment = st.selectbox("Assessment Format", ["No Assessment", "Exit Slip", "Short Response", "Group Presentation", "Quiz"])

    if st.button("Generate Lesson Plan"):
        lesson_count = sequence.split()[0]
        prompt_parts = [
            f"Create {lesson_count} lesson(s), each {duration} minutes long, for a Year {year} {subject} class on '{topic}'.",
            f"Start the lesson with a clear Learning Goal aligned to a {goal_focus.lower()} outcome.",
            f"Structure each lesson with: Hook, Learning Intentions, Warm-up, Main Task, Exit Ticket.",
            f"The lesson should use {device_use.lower()}.",
            f"Students should work in {grouping.lower()}.",
            f"Use a {lesson_style.lower()} approach."
        ]
        if differentiation:
            prompt_parts.append(f"Include differentiation strategies for: {', '.join(differentiation)}.")
        if assessment != "No Assessment":
            prompt_parts.append(f"End each lesson with a {assessment.lower()} as an assessment.")
        if include_curriculum:
            prompt_parts.append("Align the lesson with the Australian V9 curriculum.")

        full_prompt = " ".join(prompt_parts)
        with st.spinner("Planning your lesson(s)..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a practical, creative Australian teacher."},
                    {"role": "user", "content": full_prompt}
                ]
            )
            formatted = response.choices[0].message.content
            formatted = formatted.replace("* ", "• ")
            formatted = re.sub(r"^### (.+)$", r"<br><b>\1</b>", formatted, flags=re.MULTILINE)
            formatted = re.sub(r"^## (.+)$", r"<br><b>\1</b>", formatted, flags=re.MULTILINE)
            formatted = re.sub(r"^# (.+)$", r"<br><b>\1</b>", formatted, flags=re.MULTILINE)
            st.markdown(f"""
            <div style='
                background-color: #f9f9f9;
                padding: 20px;
                border-radius: 8px;
                font-family: sans-serif;
                font-size: 16px;
                color: #111;
                line-height: 1.6;
                white-space: pre-wrap;
            '>
            {formatted.replace("\n", "<br>")}
            </div>
            """, unsafe_allow_html=True)

# ---------- TOOL 2: FEEDBACK ASSISTANT ----------
if tool == "Feedback Assistant":
    st.header("🧠 Feedback Assistant")
    student_text = st.text_area("Paste student writing here:")
    tone = st.selectbox("Choose feedback tone", ["Gentle", "Firm", "Colloquial"])

    if st.button("Generate Feedback"):
        feedback_prompt = (
            f"Give feedback on the following student writing using the Star and 2 Wishes model. "
            f"Highlight spelling, grammar, cohesion, repetition, and structure issues in **bold**. "
            f"Use a {tone.lower()} tone.\n\nStudent text:\n{student_text}"
        )
        with st.spinner("Analysing writing..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a kind, helpful teacher giving writing feedback."},
                    {"role": "user", "content": feedback_prompt}
                ]
            )
            st.markdown(response.choices[0].message.content)

# ---------- TOOL 3: EMAIL ASSISTANT ----------
if tool == "Email Assistant":
    st.header("✉️ Email Assistant")
    recipient = st.selectbox("Who is the email to?", ["Parent", "Student", "Staff", "Other"])
    context = st.text_area("Briefly describe the situation or what you want to say:")
    tone = st.selectbox("Choose tone", ["Supportive", "Professional", "Friendly"])

    if st.button("Generate Email"):
        email_prompt = (
            f"Write a {tone.lower()} email to a {recipient.lower()} about the following situation:\n"
            f"{context}\n\nKeep it clear, respectful, and well-structured."
        )
        with st.spinner("Writing your email..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an experienced teacher writing professional school emails."},
                    {"role": "user", "content": email_prompt}
                ]
            )
            st.markdown(response.choices[0].message.content)

# ---------- TOOL 4: UNIT GLOSSARY GENERATOR ----------
if tool == "Unit Glossary Generator":
    st.header("📘 Unit Glossary Generator")
    subject = st.text_input("Subject (e.g. Science, HASS)")
    topic = st.text_input("Topic or Unit Focus (e.g. Body Systems, Volcanoes)")
    year = st.selectbox("Year Level", ["3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])

    if st.button("Generate Glossary"):
        glossary_prompt = (
            f"Create a 3-tier vocabulary glossary for a Year {year} {subject} unit on '{topic}'. "
            "Use this structure:\n\n"
            "Tier 1 (General): 10 basic words students must know.\n"
            "Tier 2 (Core): 7 subject-specific words they will encounter in lessons.\n"
            "Tier 3 (Stretch): 5 challenge words that extend thinking or link to deeper understanding.\n\n"
            "Use bullet points. Keep each definition under 20 words. Use student-friendly language, especially for primary year levels."
        )
        with st.spinner("Generating vocabulary list..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful and experienced curriculum-aligned teacher."},
                    {"role": "user", "content": glossary_prompt}
                ]
            )
            st.markdown(response.choices[0].message.content)

# ---------- TOOL 5: UNIT PLANNER ---------
if tool == "Unit Planner":
    st.header("📘 Unit Planner")

    # Input Fields for the Unit Planner (Only shown when Unit Planner is selected)
    year = st.selectbox("Year Level", ["3", "4", "5", "6", "7", "8", "9", "10", "11", "12"], key=f"unit_year_{tool}")
    subject = st.text_input("Subject (e.g. HASS, English, Science)", key=f"unit_subject_{tool}")
    topic = st.text_input("Unit Topic or Focus (e.g. Ancient Egypt, Persuasive Writing)", key=f"unit_topic_{tool}")
    weeks = st.slider("Estimated Duration (Weeks)", 1, 10, 5, key=f"unit_weeks_{tool}")
    include_assessment = st.checkbox("Include Assessment Suggestions?", key=f"unit_assessment_{tool}")
    include_hook = st.checkbox("Include Hook Ideas for Lesson 1?", key=f"unit_hook_{tool}")
    include_fast_finishers = st.checkbox("Include Fast Finisher Suggestions?", key=f"unit_fast_finishers_{tool}")
    include_cheat_sheet = st.checkbox("Include Quick Content Cheat Sheet (for teacher)?", key=f"unit_cheat_sheet_{tool}")

    if st.button("Generate Unit Plan", key="generate_unit_plan"):
        # Construct the prompt
        prompt_parts = [
            f"Create a unit plan overview for a Year {year} {subject} unit on '{topic}'.",
            f"The unit runs for approximately {weeks} weeks.",
            "Include the following sections:",
            "1. A short Unit Overview (what it's about).",
            "2. 3–5 clear Learning Intentions.",
            "3. A list of lesson types or activity ideas that would suit this unit."
        ]
        if include_assessment:
            prompt_parts.append("5. Include 1–2 assessment ideas (format only, keep it brief).")
        if include_hook:
            prompt_parts.append("6. Suggest 2–3 engaging Hook Ideas for Lesson 1.")
        if include_fast_finishers:
            prompt_parts.append("7. Suggest Fast Finisher or Extension Task ideas.")
        if include_cheat_sheet:
            prompt_parts.append("8. Provide a Quick Content Cheat Sheet: 10 bullet-point facts a teacher should know to teach this unit.")

        full_prompt = " ".join(prompt_parts)

        with st.spinner("Planning your unit..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a practical and experienced curriculum-aligned teacher in Australia."},
                    {"role": "user", "content": full_prompt}
                ]
            )

        unit_plan_raw = response.choices[0].message.content




# After user clicks "Generate Unit Plan" and we’ve generated the text dynamically
if "unit_plan_text" in st.session_state and st.session_state["unit_plan_text"]:
    # Create a Document object
    doc = Document()

    # Add formatted headings and bullet points

    # Example for "Unit Overview" heading and bullet points
    add_heading(doc, "Unit Plan Overview:")
    add_bullet_points(doc, [
        "• Introduction to the unit and its main themes.",
        "• Overview of the activities and assessments."
    ])

    # Example for "Learning Intentions" heading and bullet points
    add_heading(doc, "Learning Intentions:")
    add_bullet_points(doc, [
        "• Identify the key concepts of the unit.",
        "• Understand how the subject matter connects to real-world applications."
    ])

    # Continue for other sections dynamically, based on user input
    add_heading(doc, "Lesson Types/Activity Ideas:")
    add_bullet_points(doc, [
        "• Research Project: Investigate a specific aspect of the unit.",
        "• Group Activity: Discussion on key themes and topics."
    ])

    # Add more sections based on your dynamic content (e.g., Quick Cheat Sheet, Assessment Ideas, etc.)

    # Save the document
    doc.save('generated_unit_plan.docx')


    
      # ---- FORMATTING CLEANUP ----
unit_plan = re.sub(r"\*\*(.*?)\*\*", r"\1", unit_plan_raw)  # Remove markdown bold
unit_plan = re.sub(r"#+\s*", "", unit_plan)  # Remove markdown headings
unit_plan = re.sub(r"\n{2,}", "\n", unit_plan.strip())  # Collapse excessive blank lines
unit_plan = re.sub(r"(:)\n", r"\1\n\n", unit_plan)  # Add spacing AFTER colons

bullet_lines = []
for line in unit_plan.splitlines():  # This line must have the same indentation as the previous line
    stripped = line.strip()
    if re.match(r'^\d+\.\s+', stripped):  # Numbered or dash
        clean = re.sub(r'^\d+\.\s+', '', stripped)
        bullet_lines.append("• " + clean)
    elif stripped.endswith(":"):
        bullet_lines.append("")  # Add space BEFORE heading
        bullet_lines.append(stripped)
    elif stripped:
        bullet_lines.append(stripped)


        
      
        final_text = "\n".join(bullet_lines)
        st.session_state["unit_plan_text"] = final_text

    # Display Unit Plan after generation
    if "unit_plan_text" in st.session_state and st.session_state["unit_plan_text"]:
        st.markdown("### Generated Unit Plan")
    
        # Ensure unit plan is cleanly displayed
        st.markdown(
            f"""
            <div style="background-color: #ffffff; padding: 20px; border-radius: 6px; font-family: 'Segoe UI', sans-serif; font-size: 16px; line-height: 1.7; color: #222; white-space: pre-wrap; text-align: left;">
                {st.session_state['unit_plan_text']}
            </div>
            """,
            unsafe_allow_html=True
        )

        # Word export button (buffer handling)
        word_buffer = BytesIO()
        doc = Document()
        doc.add_paragraph(st.session_state["unit_plan_text"])
        doc.save(word_buffer)
        word_buffer.seek(0)



       # Word Download Button with a unique key
        st.download_button(
            "📝 Download Word", 
            word_buffer,
            file_name="unit_plan.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            key=f"download_word_{int(time.time())}"  # Use a timestamp to ensure uniqueness
        )


        # PDF export button (with custom font)
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font("DejaVu", "", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", uni=True)
        pdf.set_font("DejaVu", size=10)

        # Write unit plan text to the PDF
        for line in st.session_state["unit_plan_text"].split("\n"):
            wrapped_lines = textwrap.wrap(line, width=90)
            for wrapped_line in wrapped_lines:
                pdf.cell(0, 8, txt=wrapped_line, ln=True)

        # PDF buffer
        pdf_buffer = BytesIO()
        pdf_output = pdf.output(dest='S')
        pdf_buffer.write(pdf_output.encode('latin1'))
        pdf_buffer.seek(0)

        # PDF Download Button
        st.download_button("📎 Download PDF", data=pdf_buffer,
                           file_name="unit_plan.pdf",
                           mime="application/pdf",
                           key="download_pdf")

