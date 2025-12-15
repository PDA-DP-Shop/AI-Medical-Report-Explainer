import streamlit as st
import pdfplumber
from openai import OpenAI
from PIL import Image

# ---------- CONFIG ----------
st.set_page_config(page_title="AI Medical Report Explainer", page_icon="🧠")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ---------- UI ----------
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
    return text.strip()

def explain_report(report_text, language):
    prompt = f"""
    You are a medical assistant AI.

    Explain the following medical report in VERY SIMPLE language.
    Avoid medical jargon.
    Do NOT give diagnosis.
    Suggest consulting a doctor if values look abnormal.

    Language: {language}

    Medical Report:
    {report_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

# ---------- ACTION ----------
if uploaded_file and st.button("Explain Report"):

    file_type = uploaded_file.type

    if file_type == "application/pdf":
        report_text = extract_text_from_pdf(uploaded_file)

        if not report_text:
            st.error("❌ This PDF has no readable text. Please upload a text-based PDF.")
        else:
            explanation = explain_report(report_text, language)
            st.subheader("📝 Easy Explanation")
            st.write(explanation)

    else:
        st.warning(
            "⚠ Image reports are not supported on Streamlit Cloud yet.\n\n"
            "Please upload a **text-based PDF** for accurate explanation."
        )

# ---------- DISCLAIMER ----------
st.info(
    "⚠ This explanation is for educational purposes only. "
    "Always consult a certified doctor."
)
