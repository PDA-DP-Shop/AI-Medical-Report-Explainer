import streamlit as st
import base64
from openai import OpenAI
from PIL import Image
import io

st.set_page_config(page_title="AI Medical Report Explainer", layout="centered")

st.title("🧠 AI Medical Report Explainer")
st.write("Upload a medical report (PDF or Image) and get a simple explanation.")

language = st.selectbox(
    "Choose Explanation Language",
    ["English", "Hindi", "Gujarati", "Chinese"]
)

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=["png", "jpg", "jpeg", "pdf"]
)

client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

def image_to_base64(img):
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

if uploaded_file and st.button("Explain Report"):
    try:
        if uploaded_file.type == "application/pdf":
            st.error("⚠ Please upload report as IMAGE (photo or screenshot). PDF scan not supported yet.")
            st.stop()

        image = Image.open(uploaded_file).convert("RGB")
        img_base64 = image_to_base64(image)

        prompt = f"""
        You are a medical assistant AI.

        Task:
        - Read the medical report from the image
        - Explain it in very simple language
        - No medical jargon
        - No diagnosis
        - Suggest doctor consultation if needed
        - Language: {language}
        """

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )

        st.success("✅ Report Explanation")
        st.write(response.choices[0].message.content)

    except Exception as e:
        st.error("❌ Unable to read report. Please upload a clear image.")
        st.write(str(e))

st.warning(
    "⚠ This explanation is for educational purposes only. "
    "Always consult a certified doctor."
)
