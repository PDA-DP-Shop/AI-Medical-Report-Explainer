import streamlit as st
import base64
import requests
from PIL import Image
import io

st.set_page_config(page_title="AI Medical Report Explainer", layout="centered")

st.title("🧠 AI Medical Report Explainer")
st.write("Upload a medical report (PDF or Image) and get a simple explanation.")

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=["png", "jpg", "jpeg", "pdf"]
)

language = st.selectbox(
    "Choose Explanation Language",
    ["English", "Hindi", "Gujarati", "Chinese"]
)

def call_openrouter(image_bytes, language):
    image_base64 = base64.b64encode(image_bytes).decode()

    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
Explain this medical report in VERY SIMPLE language.
Avoid medical jargon.
Do not diagnose.
Language: {language}
"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    return response.json()["choices"][0]["message"]["content"]

if uploaded_file and st.button("Explain Report"):
    try:
        if uploaded_file.type == "application/pdf":
            st.error("📌 PDF detected. Please upload a clear IMAGE of the report.")
            st.stop()

        image = Image.open(uploaded_file).convert("RGB")
        buf = io.BytesIO()
        image.save(buf, format="PNG")

        with st.spinner("Analyzing report..."):
            explanation = call_openrouter(buf.getvalue(), language)

        st.subheader("📝 Simple Explanation")
        st.write(explanation)

    except Exception as e:
        st.error("Unable to read report. Please upload a clear image.")

st.info(
    "⚠ This explanation is for educational purposes only. "
    "Always consult a certified doctor."
)
