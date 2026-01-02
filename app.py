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
    image_base64 = image_to_base64(image)

    system_prompt = (
        "You are a medical assistant. Explain the medical report clearly in simple language for a patient."
        if mode == "Patient (Simple)"
        else "You are a medical expert. Explain the medical report in technical language for a doctor."
    )

    payload = {
        "model": "openai/gpt-4o-mini",  # Vision-capable via OpenRouter
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Analyze and explain this medical report image."
                    },
                    {
                        "type": "input_image",
                        "image_base64": image_base64
                    }
                ]
            }
        ],
        "max_tokens": 500
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
        return f"❌ API Error: {response.text}"

    data = response.json()
    return data["choices"][0]["message"]["content"]

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
