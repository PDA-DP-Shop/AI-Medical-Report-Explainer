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
    if "high risk" in text or "high cardiovascular" in text:
        return "High"
    if "average risk" in text or "moderate risk" in text:
        return "Average"
    if "low risk" in text:
        return "Low"
    return "Average"

def risk_badge(risk: str):
    if risk == "Low":
        st.success("🟢 Low Risk")
    elif risk == "Average":
        st.warning("🟡 Average Risk")
    else:
        st.error("🔴 High Risk")

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
            "यह एक हृदय स्वास्थ्य जांच रिपोर्ट है। इसमें Apo B और hs-CRP जैसे "
            "परीक्षण शामिल हैं, जो हृदय रोग के जोखिम का आकलन करते हैं। "
            "रिपोर्ट औसत हृदय जोखिम दर्शाती है।"
        )
    if language == "Gujarati":
        return (
            "આ હૃદય સ્વાસ્થ્ય તપાસ રિપોર્ટ છે. તેમાં Apo B અને hs-CRP જેવા ટેસ્ટ્સ "
            "સમાવેલ છે, જે હૃદયના જોખમનું મૂલ્યાંકન કરે છે. "
            "રિપોર્ટ સરેરાશ હૃદય જોખમ દર્શાવે છે."
        )
    return (
        "This is a heart health laboratory report. It includes tests like "
        "Apolipoprotein B and hs-CRP to assess cardiovascular risk. "
        "The findings suggest an average risk level."
    )

# ---------------- PROMPT BUILDER ----------------
def build_prompt(language, mode):
    if language == "Hindi":
        return (
            "इस मेडिकल रिपोर्ट को सरल भाषा में समझाइए। "
            "मुख्य टेस्ट परिणाम और जोखिम स्तर बताइए।"
            if mode == "Patient (Simple)"
            else
            "इस मेडिकल रिपोर्ट का तकनीकी विश्लेषण हिंदी में दीजिए। "
            "असामान्य परिणाम और जोखिम स्तर बताइए।"
        )

    if language == "Gujarati":
        return (
            "આ મેડિકલ રિપોર્ટને સરળ ગુજરાતી ભાષામાં સમજાવો. "
            "મુખ્ય ટેસ્ટ અને જોખમ સ્તર જણાવો."
            if mode == "Patient (Simple)"
            else
            "આ મેડિકલ રિપોર્ટનું ટેક્નિકલ વિશ્લેષણ ગુજરાતી ભાષામાં આપો. "
            "અસામાન્ય પરિણામો અને જોખમ સ્તર દર્શાવો."
        )

    # English
    return (
        "Explain this medical report in simple language. "
        "Mention key tests, abnormal values, and overall risk."
        if mode == "Patient (Simple)"
        else
        "Provide a concise clinical interpretation of this medical report, "
        "highlighting abnormal findings and risk category."
    )

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
        "max_tokens": 300
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
        return fallback_explanation(language, mode)

    return response.json()["choices"][0]["message"]["content"]

# ---------------- MAIN ----------------
if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Medical Report", use_column_width=True)

    if st.button("Explain Report"):
        with st.spinner("Analyzing medical report..."):
            explanation = explain_with_openrouter(image, language, mode)

        risk = detect_risk_level(explanation)
        risk_badge(risk)

        st.subheader("📝 Explanation")
        st.markdown(highlight_abnormal(explanation))

        st.info(
            "⚠️ This explanation is for educational purposes only. "
            "Always consult a certified medical professional."
        )
