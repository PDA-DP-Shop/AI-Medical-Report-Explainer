import streamlit as st
import pdfplumber
from openai import OpenAI

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🧠",
    layout="centered"
)

st.title("🧠 AI Medical Report Explainer")
st.write("Upload a medical report and get an easy explanation in your preferred language.")

# ------------------ API CLIENT ------------------
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ------------------ INPUTS ------------------
uploaded_file = st.file_uploader(
    "📄 Upload Medical Report (PDF only)",
    type=["pdf"]
)

language = st.selectbox(
    "🌍 Select Explanation Language",
    ["English", "Hindi", "Gujarati", "Chinese"]
)

# ------------------ FUNCTIONS ------------------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def generate_explanation(report_text, language):
    prompt = f"""
You are a medical assistant AI.

Rules:
- Explain the medical report in very simple and easy language
- Avoid medical jargon
- Do NOT diagnose or prescribe medicine
- If values are abnormal, gently suggest consulting a doctor
- Use bullet points where helpful

Language: {language}

Medical Report:
{report_text}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# ------------------ ACTION ------------------
if uploaded_file and st.button("🧠 Explain Report"):
    with st.spinner("Analyzing report..."):
        report_text = extract_text_from_pdf(uploaded_file)

        if not report_text.strip():
            st.error("❌ Could not read text from the PDF.")
        else:
            explanation = generate_explanation(report_text, language)
            st.subheader("📝 Easy Explanation")
            st.write(explanation)

# ------------------ DISCLAIMER ------------------
st.divider()
st.info(
    "⚠ This explanation is for educational purposes only. "
    "It does not replace professional medical advice. "
    "Always consult a certified doctor."
)
