import streamlit as st
import requests
import base64
from PIL import Image
import io

# ---------------- CONFIG ----------------
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
MODEL = "openai/gpt-4o-mini"  # vision capable

# ---------------- UI ----------------
st.set_page_config(page_title="AI Medical Report Explainer", page_icon="🧠")

st.title("🧠 AI Medical Report Explainer")
st.write("Upload a medical report (PDF or Image) and get a simple explanation.")

language = st.selectbox(
    "Choose Explanation Language",
    ["English", "Hindi", "Gujarati"]
)

mode = st.radio(
    "Explanation Mode",
    ["Patient (Simple)", "Doctor (Technical)"]
)

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=["png", "jpg", "jpeg"]
)

# ---------------- FUNCTION ----------------
def explain_image(image_bytes):
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = f"""
You are a medical assistant AI.

Task:
- Read the medical report from the image
- Explain it clearly
- Language: {language}
- Explanation style: {mode}
- Use simple words if Patient mode
- DO NOT diagnose
- Suggest consulting a doctor if needed
"""

    payload = {
        "model": MODEL,
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
        ]
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# ---------------- BUTTON ----------------
if uploaded_file and st.button("Explain Report"):
    try:
        image = Image.open(uploaded_file)
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")

        with st.spinner("Analyzing medical report..."):
            result = explain_image(img_bytes.getvalue())

        st.subheader("📝 Explanation")
        st.write(result)

    except Exception as e:
        st.error("Unable to read report. Please upload a clear image.")

# ---------------- DISCLAIMER ----------------
st.warning(
    "⚠ This explanation is for educational purposes only. "
    "Always consult a certified doctor."
)
