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
    image.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode()

    prompt = (
        "Explain this medical report in simple language for a patient. "
        "Mention key test results and overall health risk."
        if mode == "Patient (Simple)"
        else
        "Explain this medical report in technical language for a doctor. "
        "Include clinical interpretation and risk assessment."
    )

    payload = {
        "model": "anthropic/claude-3.5-sonnet",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 700
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=90
    )

    if response.status_code != 200:
        return f"API Error: {response.text}"

    return response.json()["choices"][0]["message"]["content"]


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
