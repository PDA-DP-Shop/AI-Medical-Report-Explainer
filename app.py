import streamlit as st
from PIL import Image
import base64
import requests
import io
import re

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="AI Medical Report Explainer",
    page_icon="🧠",
    layout="centered"
)

OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("OpenRouter API key not found in Streamlit secrets.")
    st.stop()

# ---------------- UI ----------------
st.title("🧠 AI Medical Report Explainer")
st.write("Upload a medical report image and get an AI-generated explanation.")

language = st.selectbox(
    "Choose Explanation Language",
    ["English", "Hindi", "Gujarati"]
)

mode = st.radio(
    "Explanation Mode",
    ["Patient (Simple)", "Doctor (Technical)"]
)

uploaded_file = st.file_uploader(
    "Upload Medical Report Image (PNG / JPG)",
    type=["png", "jpg", "jpeg"]
)

# ---------------- IMAGE COMPRESSION ----------------
def compress_image(image: Image.Image, max_width=900, quality=60) -> bytes:

    if image.width > max_width:
        ratio = max_width / image.width
        image = image.resize(
            (max_width, int(image.height * ratio)),
            Image.LANCZOS
        )

    buffer = io.BytesIO()

    image.convert("RGB").save(
        buffer,
        format="JPEG",
        quality=quality,
        optimize=True
    )

    return buffer.getvalue()

# ---------------- RISK LOGIC ----------------
def detect_risk_level(text: str) -> str:

    text = text.lower()

    if any(word in text for word in ["high risk", "severe", "critical"]):
        return "High"

    if any(word in text for word in ["moderate", "average risk", "borderline"]):
        return "Average"

    if any(word in text for word in ["normal", "low risk"]):
        return "Low"

    return "Average"

def risk_badge(risk: str):

    if risk == "Low":
        st.success("🟢 Low Health Risk")

    elif risk == "Average":
        st.warning("🟡 Moderate Health Risk")

    else:
        st.error("🔴 High Health Risk")

# ---------------- ABNORMAL HIGHLIGHT ----------------
def highlight_abnormal(text: str):

    keywords = ["high", "low", "elevated", "abnormal", "above", "below"]

    for k in keywords:

        text = re.sub(
            rf"\b{k}\b",
            f"**⚠️ {k.upper()}**",
            text,
            flags=re.IGNORECASE
        )

    return text

# ---------------- FALLBACK ----------------
def fallback_explanation(language, mode):

    if language == "Hindi":
        return (
            "यह एक स्वास्थ्य रिपोर्ट है। कुछ परीक्षण परिणाम सामान्य सीमा से "
            "अधिक या कम हो सकते हैं। सटीक चिकित्सा सलाह के लिए डॉक्टर से "
            "परामर्श करें।"
        )

    if language == "Gujarati":
        return (
            "આ આરોગ્ય રિપોર્ટ છે. કેટલાક ટેસ્ટ પરિણામો સામાન્ય મર્યાદાથી "
            "ઉપર અથવા નીચે હોઈ શકે છે. ચોક્કસ સલાહ માટે ડોક્ટરને મળો."
        )

    return (
        "This appears to be a medical laboratory report. Some results may be "
        "outside the normal range. Please consult a healthcare professional "
        "for accurate diagnosis."
    )

# ---------------- PROMPT BUILDER ----------------
def build_prompt(language, mode):

    if language == "Hindi":

        if mode == "Patient (Simple)":
            return """
इस मेडिकल रिपोर्ट को सरल भाषा में समझाइए।

इन बिंदुओं को शामिल करें:

1. रिपोर्ट में कौन-कौन से टेस्ट हैं
2. कौन से परिणाम सामान्य या असामान्य हैं
3. इसका स्वास्थ्य पर क्या प्रभाव हो सकता है
4. सरल जीवनशैली सलाह दें
"""

        else:
            return """
इस मेडिकल रिपोर्ट का तकनीकी विश्लेषण करें।

प्रत्येक टेस्ट के लिए:
- टेस्ट का उद्देश्य
- परिणाम का विश्लेषण
- संभावित जोखिम
"""

    if language == "Gujarati":

        if mode == "Patient (Simple)":
            return """
આ મેડિકલ રિપોર્ટને સરળ ગુજરાતી ભાષામાં સમજાવો.

સમાવો:
1. મુખ્ય ટેસ્ટ
2. કયા પરિણામો સામાન્ય અથવા અસામાન્ય છે
3. આરોગ્ય પર તેની અસર
4. સરળ જીવનશૈલી સલાહ
"""

        else:
            return """
આ મેડિકલ રિપોર્ટનું ટેક્નિકલ વિશ્લેષણ આપો.
દરેક ટેસ્ટનું પરિણામ અને જોખમ સમજાવો.
"""

    # English

    if mode == "Patient (Simple)":
        return """
Analyze this medical report and explain it in simple language.

Include:

1. Main tests found in the report
2. Abnormal values
3. Health impact
4. Lifestyle advice
"""

    else:
        return """
Provide a clinical interpretation of this medical report.

For each test include:

- Test meaning
- Result interpretation
- Abnormal findings
- Risk implications
"""

# ---------------- OPENROUTER ----------------
def explain_with_openrouter(image: Image.Image, language, mode: str) -> str:

    compressed = compress_image(image)

    image_base64 = base64.b64encode(compressed).decode()

    prompt = build_prompt(language, mode)

    payload = {
        "model": "anthropic/claude-3-haiku",
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
        ],
        "max_tokens": 700,
        "temperature": 0.2
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            return fallback_explanation(language, mode)

        return response.json()["choices"][0]["message"]["content"]

    except Exception:
        return fallback_explanation(language, mode)

# ---------------- MAIN ----------------
if uploaded_file:

    image = Image.open(uploaded_file).convert("RGB")

    st.image(image, caption="Uploaded Medical Report", use_column_width=True)

    if st.button("Explain Report"):

        with st.spinner("Analyzing medical report..."):

            explanation = explain_with_openrouter(image, language, mode)

        risk = detect_risk_level(explanation)

        risk_badge(risk)

        st.subheader("📝 Medical Report Explanation")

        st.markdown(highlight_abnormal(explanation))

        st.subheader("📊 Health Summary")

        if risk == "High":
            st.error("High health risk detected. Please consult a doctor.")

        elif risk == "Average":
            st.warning("Moderate risk detected. Monitor lifestyle and follow-up tests.")

        else:
            st.success("Low health risk detected.")

        st.info(
            "⚠️ This AI explanation is for educational purposes only. "
            "Always consult a certified healthcare professional."
        )
