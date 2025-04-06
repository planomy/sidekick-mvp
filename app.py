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


teacher_facts = [
    "The average teacher makes over 1,500 educational decisions per day. 🤯",
    "Teachers influence more people in a year than most do in a lifetime.",
    "A pencil can write around 45,000 words—how many ideas did your class generate today?",
    "In Finland, teachers are trained at the same level as doctors and lawyers.",
    "One caring teacher can boost a child’s lifelong academic trajectory."
]

st.title("📚 Planomy – Teacher Super Aid")
st.info(random.choice(teacher_boosts + teacher_facts + funny_boosts))

# ---------- TOOL SELECTION ----------
st.sidebar.title("✏️ Tools")
tool = st.sidebar.radio("Choose a tool:", ["Lesson Builder", "Feedback Assistant", "Email Assistant"])

# ---------- TOOL 1: LESSON BUILDER ----------
if tool == "Lesson Builder":
    st.header("📝 Lesson Builder")
    year = st.selectbox("Year Level", ["7", "8", "9", "10", "11", "12"])
    subject = st.text_input("Subject (e.g. English, Science)")
    topic = st.text_input("Lesson Topic or Focus")
    include_curriculum = st.checkbox("Include V9 curriculum reference")

    if st.button("Generate Lesson Plan"):
        lesson_prompt = (
            f"Create a 70-minute Year {year} {subject} lesson on '{topic}'. "
            f"Structure it with: Hook, Learning Intentions, Warm-up, Main Task, Exit Ticket."
        )
        if include_curriculum:
            lesson_prompt += " Align the plan with the Australian V9 curriculum."

        with st.spinner("Planning your lesson..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a practical, creative Australian teacher."},
                    {"role": "user", "content": lesson_prompt}
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

