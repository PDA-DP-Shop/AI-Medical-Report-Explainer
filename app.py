import streamlit as st
from PIL import Image
import base64
import io
import re
import google.generativeai as genai

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="medical_symbol",
    layout="centered"
)

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Please add GEMINI_API_KEY to your Streamlit secrets.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

st.title("AI Medical Report Explainer")
st.write("Upload a medical report image and get an AI-generated explanation.")

language = st.selectbox(
    "Choose Explanation Language",
    ["English", "Hindi", "Gujarati"]
)

mode = st.radio(
    "Explanation Mode",
    ["Patient (Simple)", "Doctor (Technical)"]
)

uploaded_file = st.file_uploader(
    "Upload Medical Report Image",
    type=["png", "jpg", "jpeg"]
)

def compress_image(image, max_width=900, quality=60):
    if image.width > max_width:
        ratio = max_width / image.width
        image = image.resize(
            (max_width, int(image.height * ratio)),
            Image.LANCZOS
        )
    buffer = io.BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=quality, optimize=True)
    return buffer.getvalue()

def detect_risk_level(text):
    text = text.lower()
    if any(w in text for w in ["high risk", "severe", "critical"]):
        return "High"
    if any(w in text for w in ["moderate", "average risk", "borderline"]):
        return "Average"
    if any(w in text for w in ["normal", "low risk"]):
        return "Low"
    return "Average"

def risk_badge(risk):
    if risk == "Low":
        st.success("Low Health Risk")
    elif risk == "Average":
        st.warning("Moderate Health Risk")
    else:
        st.error("High Health Risk")

def highlight_abnormal(text):
    keywords = ["high", "low", "elevated", "abnormal", "above", "below"]
    for k in keywords:
        text = re.sub(rf"\b{k}\b", f"**{k.upper()}**", text, flags=re.IGNORECASE)
    return text

def build_prompt(language, mode):
    if language == "English":
        if mode == "Patient (Simple)":
            return "You are a medical assistant helping patients understand lab reports. Analyze the medical report image carefully. Provide a detailed explanation using this structure: 1. Report Summary 2. Important Tests Detected 3. Abnormal Results 4. Health Meaning 5. Lifestyle Advice. Write clearly so a non-medical person can understand. Minimum 150 words."
        else:
            return "You are a clinical medical expert. Provide a technical interpretation of this medical report. Structure response as: 1. Report Type 2. Test Interpretation 3. Abnormal Findings 4. Clinical Significance 5. Risk Assessment. Minimum 200 words."
    if language == "Hindi":
        if mode == "Patient (Simple)":
            return "Is medical report ko saral Hindi mein samjhaiye. In binduon ko shamil karen: 1. Report ka prakar 2. Mukhy test 3. Asamanya parinam 4. Swasthya par prabhav 5. Jeevanshaili salah. Kam se kam 150 shabd likhen."
        else:
            return "Is medical report ka chikitsakiy vishleshan Hindi mein karen. 1. Report ka prakar 2. Test vishleshan 3. Asamanya parinam 4. Swasthya jokhim. Kam se kam 200 shabd likhen."
    if language == "Gujarati":
        if mode == "Patient (Simple)":
            return "A medical report ne saral Gujarati ma samjavo. 1. Report no prakar 2. Mukhy test 3. Asamanya parinam 4. Arogya par asar 5. Jeevanshaili salah. Ochama ocha 150 shabd lakho."
        else:
            return "A medical report nu technical vishleshan karo. 1. Report prakar 2. Test vishleshan 3. Asamanya parinamo 4. Arogya jokhim. Ochama ocha 200 shabd lakho."

def explain_with_gemini(image, language, mode):
    compressed = compress_image(image)
    prompt = build_prompt(language, mode)
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        image_part = {
            "mime_type": "image/jpeg",
            "data": compressed
        }
        response = model.generate_content([prompt, image_part])
        return response.text
    except Exception as e:
        return "AI request failed: " + str(e)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Medical Report")
    if st.button("Explain Report"):
        with st.spinner("Analyzing medical report..."):
            explanation = explain_with_gemini(image, language, mode)
        risk = detect_risk_level(explanation)
        risk_badge(risk)
        st.subheader("Medical Report Explanation")
        st.markdown(highlight_abnormal(explanation))
        st.subheader("Health Summary")
        if risk == "High":
            st.error("High health risk detected. Please consult a doctor.")
        elif risk == "Average":
            st.warning("Moderate risk detected. Follow lifestyle precautions.")
        else:
            st.success("Low health risk detected.")
        st.info("This AI explanation is for educational purposes only. Always consult a medical professional.")
