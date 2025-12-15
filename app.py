import streamlit as st
import base64
from openai import OpenAI
from PIL import Image

st.set_page_config(page_title="AI Medical Report Explainer")

st.title("🧠 AI Medical Report Explainer")
st.write("Upload a medical report (PDF or Image) and get a simple explanation.")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=["png", "jpg", "jpeg", "pdf"]
)

language = st.selectbox(
    "Choose Explanation Language",
    ["English", "Hindi", "Gujarati", "Chinese"]
)

def encode_file(file):
    return base64.b64encode(file.read()).decode("utf-8")

if uploaded_file and st.button("Explain Report"):
    with st.spinner("Analyzing report..."):
        file_bytes = encode_file(uploaded_file)

        prompt = f"""
        You are a medical assistant.
        Read the uploaded medical report and explain it in VERY SIMPLE language.
        Avoid medical jargon.
        Do NOT diagnose.
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
                                "url": f"data:image/png;base64,{file_bytes}"
                            },
                        },
                    ],
                }
            ],
        )

        st.subheader("📄 Easy Explanation")
        st.write(response.choices[0].message.content)

st.info(
    "⚠ This explanation is for educational purposes only. "
    "Always consult a certified doctor."
)
