import streamlit as st
import openai
import random

# ---------- CONFIG ----------
st.set_page_config(page_title="Planomy Teacher Super Aid", layout="wide")

# ---------- API KEY INPUT ----------
st.sidebar.title("🔐 API Key Setup")
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
funny_boosts = [
    "You survived Monday. That’s basically wizardry. 🧙‍♂️",
    "You taught a whole class without Googling. Power move. 💻🚫",
    "Your patience today deserves an Olympic medal. 🥇 For Waiting.",
    "You’ve explained it three times. That’s officially ‘teacher cardio’. 🏃‍♀️📚",
    "They think you’re calm. Only your coffee knows the truth. ☕😅",
    "You said 'quietly now' 47 times. Still hopeful. 💬🔊",
    "Your whiteboard markers fear you. And they should. 🖊🔥",
    "If sarcasm were a subject, you'd be the Head of Department. 🎓",
    "‘I don’t get it’—they say. You smile. You die a little inside. 😐💀",
    "You’ve earned 6 gold stars today. Pity no one’s giving them out. ⭐⭐⭐⭐⭐⭐",
    "You ran a lesson, dodged 4 paper planes, and still made it to lunch. Hero. 🍽🛡",
    "They think you're powered by knowledge. It’s actually snacks and spite. 🍫😈"
]

sarcastic_boosts = [
    "Ah yes, because *that* worksheet will definitely solve all behaviour problems. 📄✨",
    "Nothing says ‘I’m valued’ like being handed a new policy at 8:59am. 🕘💼",
    "Sure, I’ll just invent an extra hour in the day. No worries. 🕐✨",
    "Of course I’ll differentiate this lesson... for 28 students... during lunch. 🍽🤡",
    "Great idea—let’s fix student motivation with another meeting. 🧠🎯",
    "Marking on a Friday night? Living the dream. 🍷📚",
    "The photocopier jammed again? Wow, how refreshing. 🖨🔥",
    "Yes, little Timmy, I do this job just for the fame and fortune. 💰😎",
    "Don't worry, I’ll just read your mind next time instead of asking for your name. 🧠🔮",
    "Another email. I was worried my inbox was getting too manageable. 📥📥📥",
    "Let me drop everything to print that thing you forgot. That's what I'm here for. 🏃‍♂️🖨",
    "Oh good, another last-minute ‘urgent’ change. Love those. 🧨"
]

teacher_facts = [
    "The average teacher makes over 1,500 educational decisions per day. 🤯",
    "Teachers influence more people in a year than most do in a lifetime.",
    "A pencil can write around 45,000 words—how many ideas did your class generate today?",
    "In Finland, teachers are trained at the same level as doctors and lawyers.",
    "One caring teacher can boost a child’s lifelong academic trajectory."
]

st.title("📚 Planomy – Teacher Super Aid")
st.info(random.choice(teacher_boosts + teacher_facts + funny_boosts + sarcastic_boosts))

# ---------- TOOL SELECTION ----------
st.sidebar.title("✏️ Tools")
tool = st.sidebar.radio("Choose a tool:", ["Lesson Builder", "Feedback Assistant", "Email Assistant", "Unit Glossary Generator", "Unit Planner"])

# ---------- TOOL 0: UNIT PLANNER ----------
if tool == "Unit Planner":
    st.header("📘 Unit Planner")

    # Inputs
    year = st.selectbox("Year Level", ["3", "4", "5", "6", "7", "8", "9", "10", "11", "12"])
    subject = st.text_input("Subject (e.g. HASS, English, Science)")
    topic = st.text_input("Unit Topic or Focus (e.g. Ancient Egypt, Persuasive Writing)")
    weeks = st.slider("Estimated Duration (Weeks)", 1, 10, 5)

    include_assessment = st.checkbox("Include Assessment Suggestions?")
    include_hook = st.checkbox("Include Hook Ideas for Lesson 1?")
    include_fast_finishers = st.checkbox("Include Fast Finisher Suggestions?")
    include_cheat_sheet = st.checkbox("Include Quick Content Cheat Sheet (for teacher)?")

    if st.button("Generate Unit Plan"):
        # Build the prompt
        prompt_parts = [
            f"Create a unit plan overview for a Year {year} {subject} unit on '{topic}'.",
            f"The unit runs for approximately {weeks} weeks.",
            "Include the following sections:",
            "1. A short Unit Overview (what it's about).",
            "2. 3–5 clear Learning Intentions.",
            "3. A suggested sequence of subtopics or concepts to explore each week.",
            "4. A list of lesson types or activity ideas that would suit this unit."
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

        if response and response.choices:
            unit_plan = response.choices[0].message.content
            st.markdown(unit_plan)
import re
from docx import Document
from fpdf import FPDF
from io import BytesIO
import textwrap

# --- CLEAN MARKDOWN SYNTAX ---
def strip_markdown(md_text):
    # Remove markdown formatting
    text = re.sub(r'#+ ', '', md_text)                     # remove headings
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)           # bold
    text = re.sub(r'\*(.*?)\*', r'\1', text)               # italics
    return text

clean_text = strip_markdown(unit_plan)

# --- EXPORT AS MARKDOWN ---
st.download_button("📋 Copy Markdown", clean_text, file_name="unit_plan.md")

# --- EXPORT AS WORD ---
doc = Document()
for line in clean_text.split('\n'):
    if line.strip().startswith("- "):
        doc.add_paragraph(line.strip()[2:], style='List Bullet')
    elif line.strip():
        doc.add_paragraph(line.strip())

word_buffer = BytesIO()
doc.save(word_buffer)
word_buffer.seek(0)

st.download_button("📝 Download Word", word_buffer,
                   file_name="unit_plan.docx",
                   mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# --- EXPORT AS PDF ---
pdf = FPDF()
pdf.add_page()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.set_font("Arial", size=11)

for line in clean_text.split("\n"):
    for wrapped in textwrap.wrap(line, width=90):
        pdf.cell(0, 8, txt=wrapped, ln=True)

pdf_bytes = pdf.output(dest='S').encode('latin1')
st.download_button("📎 Download PDF", data=pdf_bytes,
                   file_name="unit_plan.pdf",
                   mime="application/pdf")

            
            # --- EXPORT OPTIONS ---
            st.markdown("---")
            st.subheader("📄 Export Options")

            # Markdown download
            st.download_button("📋 Copy Markdown", unit_plan, file_name="unit_plan.md")

            # Word download
            from docx import Document
            from io import BytesIO
            doc = Document()
            doc.add_paragraph(unit_plan)
            word_buffer = BytesIO()
            doc.save(word_buffer)
            word_buffer.seek(0)
            st.download_button("📝 Download Word", word_buffer,
                               file_name="unit_plan.docx",
                               mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

            # PDF download
            from fpdf import FPDF
            import textwrap

            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_font("Arial", size=11)

            for line in unit_plan.split("\n"):
                for wrapped in textwrap.wrap(line, width=90):
                    pdf.cell(0, 8, txt=wrapped, ln=True)

            pdf_buffer = BytesIO()
            pdf_output = pdf.output(dest='S').encode('latin1')
            pdf_buffer.seek(0)
            st.download_button("📎 Download PDF", data=pdf_output, file_name="unit_plan.pdf", mime="application/pdf")
        else:
            st.warning("⚠️ Unit plan generation failed. Please try again.")





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
            st.markdown(response.choices[0].message.content)


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



