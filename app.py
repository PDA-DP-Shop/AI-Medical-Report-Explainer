import streamlit as st
from PIL import Image
import base64
import anthropic
import io
import re

# –––––––– CONFIG ––––––––

st.set_page_config(
page_title=“AI Medical Report Explainer”,
page_icon=“🧠”,
layout=“centered”
)

ANTHROPIC_API_KEY = st.secrets.get(“ANTHROPIC_API_KEY”)

if not ANTHROPIC_API_KEY:
st.error(“Anthropic API key not found. Please add ANTHROPIC_API_KEY to your Streamlit secrets.”)
st.stop()

# –––––––– UI ––––––––

st.title(“🧠 AI Medical Report Explainer”)
st.write(“Upload a medical report image and get an AI-generated explanation.”)

language = st.selectbox(
“Choose Explanation Language”,
[“English”, “Hindi”, “Gujarati”]
)

mode = st.radio(
“Explanation Mode”,
[“Patient (Simple)”, “Doctor (Technical)”]
)

uploaded_file = st.file_uploader(
“Upload Medical Report Image”,
type=[“png”, “jpg”, “jpeg”]
)

# –––––––– IMAGE COMPRESSION ––––––––

def compress_image(image: Image.Image, max_width=900, quality=60):

```
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
```

# –––––––– RISK DETECTION ––––––––

def detect_risk_level(text):

```
text = text.lower()

if any(w in text for w in ["high risk", "severe", "critical"]):
    return "High"

if any(w in text for w in ["moderate", "average risk", "borderline"]):
    return "Average"

if any(w in text for w in ["normal", "low risk"]):
    return "Low"

return "Average"
```

def risk_badge(risk):

```
if risk == "Low":
    st.success("🟢 Low Health Risk")

elif risk == "Average":
    st.warning("🟡 Moderate Health Risk")

else:
    st.error("🔴 High Health Risk")
```

# –––––––– HIGHLIGHT ABNORMAL ––––––––

def highlight_abnormal(text):

```
keywords = ["high", "low", "elevated", "abnormal", "above", "below"]

for k in keywords:

    text = re.sub(
        rf"\b{k}\b",
        f"**⚠️ {k.upper()}**",
        text,
        flags=re.IGNORECASE
    )

return text
```

# –––––––– PROMPT BUILDER ––––––––

def build_prompt(language, mode):

```
if language == "English":

    if mode == "Patient (Simple)":
        return """
```

You are a medical assistant helping patients understand lab reports.

Analyze the medical report image carefully.

Provide a detailed explanation using this structure:

1. Report Summary
1. Important Tests Detected
1. Abnormal Results
1. Health Meaning
1. Lifestyle Advice

Write clearly so a non-medical person can understand.

Minimum 150 words.
“””

```
    else:
        return """
```

You are a clinical medical expert.

Provide a technical interpretation of this medical report.

Structure response as:

1. Report Type
1. Test Interpretation
1. Abnormal Findings
1. Clinical Significance
1. Risk Assessment

Minimum 200 words.
“””

```
if language == "Hindi":

    if mode == "Patient (Simple)":
        return """
```

इस मेडिकल रिपोर्ट को सरल हिंदी में समझाइए।

इन बिंदुओं को शामिल करें:

1. रिपोर्ट का प्रकार
1. मुख्य टेस्ट
1. असामान्य परिणाम
1. स्वास्थ्य पर प्रभाव
1. जीवनशैली सलाह

कम से कम 150 शब्द लिखें।
“””

```
    else:
        return """
```

इस मेडिकल रिपोर्ट का चिकित्सकीय विश्लेषण हिंदी में करें।

इन बिंदुओं को शामिल करें:

1. रिपोर्ट का प्रकार
1. टेस्ट विश्लेषण
1. असामान्य परिणाम
1. स्वास्थ्य जोखिम

कम से कम 200 शब्द लिखें।
“””

```
if language == "Gujarati":

    if mode == "Patient (Simple)":
        return """
```

આ મેડિકલ રિપોર્ટને સરળ ગુજરાતી ભાષામાં સમજાવો.

સમાવો:

1. રિપોર્ટનો પ્રકાર
1. મુખ્ય ટેસ્ટ
1. અસામાન્ય પરિણામ
1. આરોગ્ય પર અસર
1. જીવનશૈલી સલાહ

ઓછામાં ઓછા 150 શબ્દ લખો.
“””

```
    else:
        return """
```

આ મેડિકલ રિપોર્ટનું ટેક્નિકલ વિશ્લેષણ કરો.

સમાવો:

1. રિપોર્ટ પ્રકાર
1. ટેસ્ટ વિશ્લેષણ
1. અસામાન્ય પરિણામો
1. આરોગ્ય જોખમ

ઓછામાં ઓછા 200 શબ્દ લખો.
“””

# –––––––– ANTHROPIC API ––––––––

def explain_with_anthropic(image, language, mode):

```
compressed = compress_image(image)
image_base64 = base64.b64encode(compressed).decode()
prompt = build_prompt(language, mode)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

try:
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1200,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    )

    return message.content[0].text

except anthropic.APIError as e:
    return f"AI request failed: {str(e)}"

except Exception as e:
    return f"Unexpected error: {str(e)}"
```

# –––––––– MAIN ––––––––

if uploaded_file:

```
image = Image.open(uploaded_file).convert("RGB")

st.image(image, caption="Uploaded Medical Report")

if st.button("Explain Report"):

    with st.spinner("Analyzing medical report..."):

        explanation = explain_with_anthropic(image, language, mode)

    risk = detect_risk_level(explanation)

    risk_badge(risk)

    st.subheader("📝 Medical Report Explanation")

    st.markdown(highlight_abnormal(explanation))

    st.subheader("📊 Health Summary")

    if risk == "High":
        st.error("High health risk detected. Please consult a doctor.")

    elif risk == "Average":
        st.warning("Moderate risk detected. Follow lifestyle precautions.")

    else:
        st.success("Low health risk detected.")

    st.info(
        "⚠️ This AI explanation is for educational purposes only. Always consult a medical professional."
    )
```
