import streamlit as st
import pdfplumber
from PIL import Image
import pytesseract
import io
import requests

# ---------------- CONFIG ----------------
st.set_page_config(page_title="AI Medical Report Explainer", page_icon="🩺")

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
MODEL = "openai/gpt-4o-mini"

# ---------------- FUNCTIONS ----------------
def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
            else:
                image = page.to_image(resolution=300).original
                text += pytesseract.image_to_string(image)
    return text.strip()

def extract_text_from_image(file):
    image = Image.open(file)
    return pytesseract.image_to_string(image)

def call_openrouter(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are a medical assistant AI. Explain reports simply. No diagnosis."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    return response.json()["choices"][0]["message"]["content"]

# ---------------- UI ----------------
st.title("🩺 AI Medical Report Explainer")
st.write("Upload **PDF or Image** → Get **simple explanation** in your language")

uploaded_file = st.file_uploader(
    "Upload Medical Report (PDF / Image)",
    type=["pdf", "png", "jpg", "jpeg"]
)

language = st.selectbox(
    "Select Explanation Language",
    ["English", "Hindi", "Gujarati", "Chinese"]
)

mode = st.radio(
    "Explanation Mode",
    ["Patient (Simple)", "Doctor (Technical)"]
)

if uploaded_file and st.button("Explain Report"):
    with st.spinner("Reading report..."):
        if uploaded_file.type == "application/pdf":
            report_text = extract_text_from_pdf(uploaded_file)
        else:
            report_text = extract_text_from_image(uploaded_file)

        if not report_text.strip():
            st.error("❌ Could not read this file. Please upload a clearer image or report.")
        else:
            prompt = f"""
Explain the following medical report.

Language: {language}
Mode: {mode}

Rules:
- Use simple words for Patient mode
- Use medical terms for Doctor mode
- Do NOT give diagnosis
- Suggest doctor consultation if needed

Medical Report:
{report_text}
"""
            result = call_openrouter(prompt)
            st.subheader("📝 Explanation")
            st.write(result)

st.info("⚠ This tool is for educational purposes only. Always consult a certified doctor.")
