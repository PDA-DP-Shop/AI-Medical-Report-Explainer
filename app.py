import streamlit as st
from openai import OpenAI
from PIL import Image
import io

st.set_page_config(page_title="AI Medical Report Explainer", layout="centered")

st.title("🧠 AI Medical Report Explainer")
st.write("Upload a **clear image** of your medical report and get a simple explanation.")

# 🔐 OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ✅ IMAGE ONLY
uploaded_file = st.file_uploader(
    "Upload Medical Report Image",
    type=["png", "jpg", "jpeg"]
)

language = st.selectbox(
    "Choose Explanation Language",
    ["English", "Hindi", "Gujarati", "Chinese"]
)

if uploaded_file and st.button("Explain Report"):
    try:
        image = Image.open(uploaded_file)

        prompt = f"""
        You are a medical assistant AI.

        Explain the medical report shown in the image.
        Use very simple language.
        Avoid medical jargon.
        Do NOT diagnose.
        Suggest consulting a doctor if needed.

        Language: {language}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/png;base64,"
                                + st.session_state.get("img_b64", "")
                            },
                        },
                    ],
                }
            ],
        )

        st.subheader("📝 Easy Explanation")
        st.write(response.choices[0].message.content)

    except Exception:
        st.error("❌ Unable to read the image. Please upload a clear report image.")

st.warning(
    "⚠ This explanation is for educational purposes only. "
    "Always consult a certified doctor."
)
