import streamlit as st
import pdfplumber
from PIL import Image
import pytesseract
from openai import OpenAI

st.set_page_config(page_title="AI Medical Report Explainer", layout="centered")

# OpenAI client (Streamlit Cloud Secret)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("🧠 AI Medical Report Explainer")
st.write("Upload a medical report (PDF or Image) and get a simple explanation.")

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=["pdf", "png", "jpg", "jpeg"]
)

language = st.selectbox(
    "Choose Explanation Language",
    ["English", "Hindi", "Gujarati", "Chinese"]
)

# ---------- FUNCTIONS ----------

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text


def extract_text_from_image(file):
    image = Image.open(file)
    text = pytesseract.image_to_string(image)
    return text


# ---------- MAIN LOGIC ----------

if uploaded_file and st.button("Explain Report"):
    with st.spinner("Analyzing report..."):
        if uploaded_file.type == "application/pdf":
            report_text = extract_text_from_pdf(uploaded_file)
        else:
            report_text = extract_text_from_image(uploaded_file)

        if report_text.strip() == "":
            st.error("❌ Unable to read the report. Please upload a clear PDF or image.")
        else:
            prompt = f"""
You are a medical assistant AI.

Task:
- Explain the medical report in very simple, easy language
- Avoid medical jargon
- Do NOT give diagnosis
- Explain like talking to a normal person
- Language: {language}

Medical Report:
{report_text}
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}]
            )

            st.subheader("📝 Simple Explanation")
            st.write(response.choices[0].message.content)

st.info(
    "⚠ This explanation is for educational purposes only. "
    "Always consult a certified doctor."
)
