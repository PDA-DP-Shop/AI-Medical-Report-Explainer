import streamlit as st
from PIL import Image
import pytesseract
import io
import os
from pdf2image import convert_from_bytes
import requests

# -------------------- CONFIG --------------------
st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🧠",
    layout="centered"
)

# -------------------- UI --------------------
st.title("🧠 AI Medical Report Explainer")
st.write("Upload a medical report (PDF or Image) and get a simple explanation.")

language = st.selectbox(
    "Choose Explanation Language",
    ["English"]
)

mode = st.radio(
    "Explanation Mode",
    ["Patient (Simple)", "Doctor (Technical)"]
)

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=["png", "jpg", "jpeg", "pdf"]
)

# -------------------- FUNCTIONS --------------------
def extract_text_from_image(image: Image.Image) -> str:
    try:
        text = pytesseract.image_to_string(image)
        return text
    except Exception:
        return ""

def is_low_quality(image: Image.Image) -> bool:
    return image.width < 800 or image.height < 800

def looks_like_medical_report(text: str) -> bool:
    keywords = [
        "hemoglobin", "blood", "test", "report", "urine",
        "platelet", "wbc", "rbc", "cholesterol", "mg/dl",
        "patient", "reference range"
    ]
    text = text.lower()
    return any(k in text for k in keywords)

def ai_explain(text: str, mode: str) -> str:
    """
    AI fallback explanation (works even if OCR is weak)
    """
    system_prompt = (
        "Explain this medical report in simple language for a patient."
        if mode == "Patient (Simple)"
        else "Explain this medical report in technical language for a doctor."
    )

    prompt = f"""
{system_prompt}

Medical Content:
{text if text.strip() else "The image looks like a medical document but text is unclear."}

Give a clear, structured explanation.
"""

    # 🔴 Replace with your OpenRouter / Gemini / OpenAI call
    # For demo safety, static fallback explanation:
    return (
        "This appears to be a medical-related document. "
        "Some values may represent blood or lab test results. "
        "Please consult a certified doctor for exact interpretation."
    )

# -------------------- MAIN LOGIC --------------------
if uploaded_file:

    images = []

    # ---- PDF Handling ----
    if uploaded_file.type == "application/pdf":
        try:
            images = convert_from_bytes(uploaded_file.read())
        except Exception:
            st.error("Unable to process PDF. Please upload a scanned medical report.")
            st.stop()

    # ---- Image Handling ----
    else:
        try:
            image = Image.open(uploaded_file).convert("RGB")
            images = [image]
        except Exception:
            st.error("Invalid image file.")
            st.stop()

    if st.button("Explain Report"):

        all_text = ""

        for img in images:
            if is_low_quality(img):
                st.warning("Image quality is low. Results may be inaccurate.")

            extracted = extract_text_from_image(img)
            all_text += extracted + "\n"

        # ---- Validation ----
        if not all_text.strip():
            st.warning("OCR could not read clear text from this file.")
            explanation = ai_explain("", mode)

        elif not looks_like_medical_report(all_text):
            st.warning("This does not appear to be a medical report.")
            explanation = ai_explain(all_text, mode)

        else:
            explanation = ai_explain(all_text, mode)

        # ---- Output ----
        st.subheader("📝 Explanation")
        st.write(explanation)

        st.info(
            "⚠️ This explanation is for educational purposes only. "
            "Always consult a certified doctor."
        )

