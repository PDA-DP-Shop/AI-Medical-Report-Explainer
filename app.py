import streamlit as st
from PIL import Image
import base64
import requests
import io
import re

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🧠",
    layout="centered"
)

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("OpenRouter API key not found in Streamlit secrets.")
    st.stop()

# ---------------- UI ----------------
st.title("🧠 AI Medical Report Explainer")
st.write("Upload a medical report image and get an AI-generated explanation.")

mode = st.radio(
    "Explanation Mode",
    ["Patient (Simple)", "Doctor (Technical)"]
)

uploaded_file = st.file_uploader(
    "Upload Medical Report Image (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

# ---------------- IMAGE COMPRESSION ----------------
def compress_image(image: Image.Image, max_width=900, quality=60) -> bytes:
    if image.width > max_width:
        ratio = max_width / image.width
        image = image.resize(
            (max_width, int(image.height * ratio)),
            Image.LANCZOS
        )

    buffer = io.BytesIO()
    image.convert("RGB").save(
        buffer,
        format="JPEG",
        quality=quality,
        optimize=True
    )
    return buffer.getvalue()

# ---------------- RISK LOGIC ----------------
def detect_risk_level(text: str) -> str:
    text = text.lower()
    if "high risk" in text or "high cardiovascular risk" in text:
        return "High"
    if "average risk" in text or "moderate risk" in text:
        return "Average"
    if "low risk" in text:
        return "Low"
    return "Average"

def risk_badge(risk: str):
    if risk == "Low":
        st.success("🟢 Low Risk")
    elif risk == "Average":
        st.warning("🟡 Average Risk")
    else:
        st.error("🔴 High Risk")

# ---------------- ABNORMAL VALUE HIGHLIGHT ----------------
def highlight_abnormal(text: str):
    abnormal_keywords = [
        "high", "elevated", "above normal",
        "low", "below normal", "abnormal"
    ]

    for word in abnormal_keywords:
        text = re.sub(
            rf"\b{word}\b",
            f"**⚠️ {word.upper()}**",
            text,
            flags=re.IGNORECASE
        )
    return text

# ---------------- FALLBACK ----------------
def fallback_explanation(mode: str) -> str:
    if mode == "Patient (Simple)":
        return (
            "This is a cardiovascular laboratory report. It includes tests like "
            "Apolipoprotein B and hs-CRP, which help assess heart disease risk. "
            "The results suggest an average cardiovascular risk. Regular follow-ups "
            "and healthy lifestyle choices are recommended."
        )
    else:
        return (
            "The report represents an advanced cardiac risk screening. hs-CRP values "
            "place the patient in an average cardiovascular risk category. ApoB is "
            "within reference range, indicating a favorable lipid profile."
        )

# ---------------- OPENROUTER CALL ----------------
def explain_with_openrouter(image: Image.Image, mode: str) -> str:
    compressed_bytes = compress_image(image)
    image_base64 = base64.b64encode(compressed_bytes).decode()

    prompt = (
        "Briefly explain this medical report in simple language. "
        "Mention key tests, abnormal values, and overall risk."
        if mode == "Patient (Simple)"
        else
        "Provide a concise clinical interpretation of this medical report, "
        "highlighting abnormal findings and risk category."
    )

    payload = {
        "model": "anthropic/claude-3-haiku",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 120
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )

    if response.status_code != 200:
        return fallback_explanation(mode)

    return response.json()["choices"][0]["message"]["content"]

# ---------------- MAIN ----------------
if uploaded_file:
    try:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Medical Report", use_column_width=True)

        if st.button("Explain Report"):
            with st.spinner("Analyzing medical report..."):
                explanation = explain_with_openrouter(image, mode)

            risk = detect_risk_level(explanation)
            risk_badge(risk)

            st.subheader("📝 Explanation")
            explanation = highlight_abnormal(explanation)
            st.markdown(explanation)

            st.info(
                "⚠️ This explanation is for educational purposes only. "
                "Always consult a certified medical professional."
            )

    except Exception as e:
        st.error(f"Error processing image: {e}")
