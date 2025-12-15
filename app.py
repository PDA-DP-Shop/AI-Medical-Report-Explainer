import streamlit as st
from openai import OpenAI
import pdfplumber
import base64

st.set_page_config(page_title="AI Medical Report Explainer")

st.title("🧠 AI Medical Report Explainer")
st.write("Upload a medical report (PDF or Image) and get a simple explanation.")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

uploaded_file = st.file_uploader(
    "Upload Medical Report",
    type=["pdf", "png", "jpg", "jpeg"]
)

language = st.selectbox(
    "Choose Explanation Language",
    ["English", "Hindi", "Gujarati", "Chinese"]
)

def extract_text_from_pdf(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

def explain_with_ai(content, is_image=False):
    if is_image:
        prompt = f"""
        You are a medical assistant.
        Explain this medical report image in very simple language.
        Avoid medical terms.
        Language: {language}
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": content}}
                ]}
            ]
        )
    else:
        prompt = f"""
        You are a medical assistant.
        Explain the following medical report in very simple language.
        Avoid medical terms.
        Language: {language}

        Report:
        {content}
        """
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

    return response.choices[0].message.content


if uploaded_file and st.button("Explain Report"):
    file_type = uploaded_file.type

    try:
        # ✅ Case 1: PDF
        if file_type == "application/pdf":
            text = extract_text_from_pdf(uploaded_file)

            # Text-based PDF
            if text:
                explanation = explain_with_ai(text, is_image=False)

            # Scanned PDF → treat as image
            else:
                base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode()
                image_url = f"data:application/pdf;base64,{base64_pdf}"
                explanation = explain_with_ai(image_url, is_image=True)

        # ✅ Case 2: Image
        else:
            base64_img = base64.b64encode(uploaded_file.getvalue()).decode()
            image_url = f"data:{file_type};base64,{base64_img}"
            explanation = explain_with_ai(image_url, is_image=True)

        st.subheader("📝 Easy Explanation")
        st.write(explanation)

    except Exception as e:
        st.error("Something went wrong. Please try another report.")

st.info(
    "⚠ This explanation is for educational purposes only. "
    "Always consult a certified doctor."
)
