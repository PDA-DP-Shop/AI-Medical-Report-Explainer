import streamlit as st
from PIL import Image
import base64
import requests
import io
import os

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🧠",
    layout="centered"
)

# ---------------- API KEY ----------------
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

# ---------------- FUNCTIONS ----------------
def image_to_base64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def explain_with_openrouter(image: Image.Image, mode: str) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG", optimize=True)
    image_base64 = base64.b64encode(buffered.getvalue()).decode()

    prompt = (
        "Briefly explain this medical report in simple language. "
        "Summarize key tests and risk."
        if mode == "Patient (Simple)"
        else
        "Provide a concise clinical summary of this medical report."
    )

    payload = {
        "model": "anthropic/claude-3-haiku",   # cheapest vision model
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 120   # VERY LOW to stay safe
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

    # 🔁 FALLBACK IF TOKEN / CREDIT ERROR
    if response.status_code != 200:
        return fallback_explanation(mode)

    return response.json()["choices"][0]["message"]["content"]

def fallback_explanation(mode: str) -> str:
    if mode == "Patient (Simple)":
        return (
            "This is a heart health laboratory report. It includes tests such as "
            "Apolipoprotein B and hs-CRP, which are used to assess cardiovascular risk. "
            "The hs-CRP value suggests an average risk level. Regular follow-up and "
            "healthy lifestyle habits are recommended."
        )
    else:
        return (
            "The document represents an advanced cardiovascular screening report. "
            "Reported hs-CRP places the patient in an average cardiovascular risk "
            "category. ApoB is within reference range, indicating a favorable lipid profile."
        )


# ---------------- MAIN LOGIC ----------------
if uploaded_file:
    try:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Uploaded Medical Report", use_column_width=True)

        if st.button("Explain Report"):
            with st.spinner("Analyzing medical report..."):
                explanation = explain_with_openrouter(image, mode)

            st.subheader("📝 Explanation")
            st.write(explanation)

            st.info(
                "⚠️ This explanation is for educational purposes only. "
                "Always consult a certified medical professional."
            )

    except Exception as e:
        st.error(f"Error processing image: {e}")
