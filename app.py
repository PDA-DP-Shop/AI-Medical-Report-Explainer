import streamlit as st
from PIL import Image
import io
import re
import pytesseract
from groq import Groq

st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="medical_symbol",
    layout="centered"
)

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("Groq API key not found. Please add GROQ_API_KEY to your Streamlit secrets.")
    st.stop()

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

def extract_text_from_image(image):
    try:
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return ""

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

def build_prompt(language, mode, report_text):
    base = "Here is the extracted text from a medical report:\n\n" + report_text + "\n\n"
    if language == "English":
        if mode == "Patient (Simple)":
            return base + "You are a medical assistant helping patients understand lab reports. Analyze the medical report carefully. Provide a detailed explanation using this structure: 1. Report Summary 2. Important Tests Detected 3. Abnormal Results 4. Health Meaning 5. Lifestyle Advice. Write clearly so a non-medical person can understand. Minimum 150 words."
        else:
            return base + "You are a clinical medical expert. Provide a technical interpretation of this medical report. Structure response as: 1. Report Type 2. Test Interpretation 3. Abnormal Findings 4. Clinical Significance 5. Risk Assessment. Minimum 200 words."
    if language == "Hindi":
        if mode == "Patient (Simple)":
            return base + "Is medical report ko saral Hindi mein samjhaiye. 1. Report ka prakar 2. Mukhy test 3. Asamanya parinam 4. Swasthya par prabhav 5. Jeevanshaili salah. Kam se kam 150 shabd."
        else:
            return base + "Is medical report ka chikitsakiy vishleshan Hindi mein karen. 1. Report prakar 2. Test vishleshan 3. Asamanya parinam 4. Swasthya jokhim. Kam se kam 200 shabd."
    if language == "Gujarati":
        if mode == "Patient (Simple)":
            return base + "A medical report ne saral Gujarati ma samjavo. 1. Report no prakar 2. Mukhy test 3. Asamanya parinam 4. Arogya par asar 5. Jeevanshaili salah. Ochama ocha 150 shabd."
        else:
            return base + "A medical report nu technical vishleshan karo. 1. Report prakar 2. Test vishleshan 3. Asamanya parinamo 4. Arogya jokhim. Ochama ocha 200 shabd."

def explain_with_groq(report_text, language, mode):
    prompt = build_prompt(language, mode, report_text)
    client = Groq(api_key=GROQ_API_KEY)
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return "AI request failed: " + str(e)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Medical Report")
    if st.button("Explain Report"):
        with st.spinner("Reading and analyzing medical report..."):
            report_text = extract_text_from_image(image)
            if not report_text or len(report_text) < 20:
                st.error("Could not read text from this image. Please upload a clearer image.")
            else:
                explanation = explain_with_groq(report_text, language, mode)
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
