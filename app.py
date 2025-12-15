import streamlit as st
import requests
from PIL import Image
from pdf2image import convert_from_bytes
import base64
import io

# ---------------- CONFIG ----------------
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
MODEL = "openai/gpt-4o-mini"

# ---------------- UI ----------------
st.set_page_config(page_title="AI Medical Report Explainer", layout="centered")

st.title("🧠 AI Medical Report Explainer")
st.write("Upload a medical report (PDF or Image) and get a simple explanation.")

language = st.selectbox(
    "Choose Explanation Language",
    ["English", "Hindi", "Gujarati"]
)

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=["png", "jpg", "jpeg", "pdf"]
)

# ---------------- FUNCTIONS ----------------
def file_to_base64_image(file):
    if file.type == "application/pdf":
        images = convert_from_bytes(file.read())
        image = images[0]  # first page
    else:
        image = Image.open(file)

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

def explain_report(image_base64, language):
    prompt = f"""
You are a medical assistant.
Explain the medical report image in VERY SIMPLE language.
Avoid medical terms.
Language: {language}

Give:
- What values mean
- Whether they are normal or not
- Simple advice
Do NOT diagnose.
"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
        },
        timeout=60,
    )

    return response.json()["choices"][0]["message"]["content"]

# ---------------- RUN ----------------
if uploaded_file and st.button("Explain Report"):
    try:
        with st.spinner("Reading report..."):
            image_base64 = file_to_base64_image(uploaded_file)
            result = explain_report(image_base64, language)

        st.success("Explanation Ready")
        st.write(result)

    except Exception as e:
        st.error("Unable to read report. Please upload a clear image or PDF.")
        st.code(str(e))

st.warning(
    "⚠️ This explanation is for educational purposes only. "
    "Always consult a certified doctor."
)
