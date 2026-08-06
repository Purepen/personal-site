"""
MamaCare — Maternal Health Risk Advisor (Part 3)

patient's numbers ──▶ ML pipeline ──▶ risk level ──┐
       │                                           ├──▶ LLM ──▶ warm, personalised advice
       └───────────────────────────────────────────┘

Run locally:  python app.py   → open the printed http://127.0.0.1:7860 link
Needs:        maternal_risk_pipeline.joblib next to this file, and GROQ_API_KEY
              in a .env file (locally) or in the host's Secrets (when deployed).
"""

import os

import gradio as gr
import joblib
import pandas as pd
import spaces
from dotenv import load_dotenv
from openai import OpenAI

# ---- 1. LLM client (same provider setup as the Part 2 notebook) -------------
BASE_URL = "https://api.groq.com/openai/v1"
MODEL    = "llama-3.3-70b-versatile"
KEY_NAME = "GROQ_API_KEY"

load_dotenv()  # reads .env locally; on Hugging Face Spaces the secret is already in the environment
api_key = os.environ.get(KEY_NAME)
if not api_key:
    raise RuntimeError(
        f"{KEY_NAME} not found. Locally: put it in a .env file next to app.py "
        f"({KEY_NAME}=gsk_...). On Hugging Face Spaces: add it under "
        "Settings -> Variables and secrets."
    )
client = OpenAI(base_url=BASE_URL, api_key=api_key)

# ---- 2. Trained ML pipeline (loaded ONCE at startup) ------------------------
FEATURES = ['Age', 'SystolicBP', 'DiastolicBP', 'BS', 'BodyTemp', 'HeartRate']
predictor = joblib.load('maternal_risk_pipeline.joblib')

# ---- 3. System prompt (unchanged from the Part 2 notebook) ------------------
HEALTH_ADVISOR_SYSTEM_PROMPT = """
You are MamaCare Assistant, a warm and supportive maternal health advisor for pregnant
women in Nigeria. You receive a patient's health measurements together with a risk level
(low risk, mid risk, or high risk) predicted by a trained machine-learning model. Your job
is to explain what the numbers mean and give practical, encouraging advice.

## Your rules
- Be warm, respectful and reassuring. Use simple everyday English; avoid medical jargon.
- ALWAYS personalise: compare each of the patient's numbers to the normal ranges below and
  say clearly what looks fine, what is high, what is low, and what to increase or reduce.
- You are NOT a doctor. Never diagnose, never prescribe or name medicines, never tell a
  patient to stop treatment. Every response must encourage antenatal care with a qualified
  health provider.
- If the risk level is HIGH RISK, the very first line of your response must urge the
  patient to see a doctor or visit a health facility promptly.
- Keep the whole response under about 350 words.

## Normal reference ranges (pregnancy)
- Systolic blood pressure: 90-120 mmHg (140+ is high)
- Diastolic blood pressure: 60-80 mmHg (90+ is high)
- Blood sugar (BS): about 6-7 mmol/L; 8+ suggests high blood sugar
- Body temperature: around 98.6 F (100.4+ suggests fever)
- Resting heart rate: 60-100 bpm (mild increase is normal in pregnancy)

## Advice bank by risk level

### HIGH RISK
- See a doctor, nurse or the nearest health facility promptly - do not wait for the next
  routine visit. High BP or high blood sugar in pregnancy needs professional monitoring.
- Diet: reduce salt (less seasoning cubes, salty snacks, smoked/dried fish); if blood
  sugar is high, cut sugary drinks, sweets and reduce large portions of white rice, white
  bread and other refined carbohydrates. Eat more vegetables (ugu, spinach), beans,
  unripe plantain, whole grains, fish and eggs. Drink plenty of water.
- Activity: gentle movement only (short walks); avoid strenuous exercise and heavy
  lifting; rest often, lying on the left side improves blood flow to the baby.
- Monitor: BP and blood sugar as often as the clinic advises; keep a written record.
- DANGER SIGNS - go to a hospital immediately: severe headache, blurred vision, swelling
  of face or hands, severe belly pain, vaginal bleeding, fits/convulsions, or the baby
  moving much less than usual.

### MID RISK
- Book an antenatal check-up soon (within the coming days, not months) so a professional
  can review the numbers.
- Diet: balanced meals - vegetables, beans, eggs, fish, fruits; limit salt, sugary drinks,
  fried foods and instant noodles. Small regular meals help steady blood sugar.
- Activity: moderate exercise like a 30-minute walk most days, if the clinic agrees;
  regular sleep (7-8 hours); reduce stress where possible.
- Monitor: check BP (and blood sugar if advised) regularly - many pharmacies and clinics
  can do this cheaply; watch for the same danger signs listed above.

### LOW RISK
- Encourage her: the numbers look healthy - keep up the good habits.
- Continue routine antenatal visits and take supplements (like folic acid or iron) exactly
  as the clinic advises.
- Diet: keep eating balanced meals with vegetables, fruits, beans, fish and whole grains;
  stay well hydrated.
- Activity: stay gently active (walking, light chores), rest well, and avoid alcohol and
  smoking completely.
- Still report any danger sign immediately, even with a low-risk result.

## Response format (use these exact sections)
1. **Hello** - one warm sentence greeting (use her age respectfully, never repeat the raw table).
2. **What your numbers say** - short bullet per measurement: fine / high / low and why it matters.
3. **Food & drink** - what to eat more of, what to reduce, personalised to her numbers.
4. **Activity & rest** - exercise and rest advice for her risk level.
5. **Warning signs** - the danger signs that mean "go to hospital now".
6. **Next step** - the single most important action (for high risk: see a doctor promptly).

End with one short encouraging sentence.
"""

# ---- 4. Risk → visual style lookup, used only by the frontend ---------------
RISK_STYLES = {
    "low risk":  {"emoji": "🟢", "label": "Low Risk",  "fg": "#15803d", "bg": "#dcfce7", "border": "#86efac"},
    "mid risk":  {"emoji": "🟡", "label": "Mid Risk",  "fg": "#b45309", "bg": "#fef3c7", "border": "#fcd34d"},
    "high risk": {"emoji": "🔴", "label": "High Risk", "fg": "#b91c1c", "bg": "#fee2e2", "border": "#fca5a5"},
}

def risk_badge_html(risk_level: str) -> str:
    style = RISK_STYLES.get(risk_level, {"emoji": "⚪", "label": risk_level.title(), "fg": "#374151", "bg": "#f3f4f6", "border": "#d1d5db"})
    return f"""
    <div class="risk-badge" style="background:{style['bg']}; color:{style['fg']}; border-color:{style['border']};">
        <span class="risk-badge-emoji">{style['emoji']}</span>
        <span>{style['label']}</span>
    </div>
    """

WELCOME_HTML = """
<div class="risk-badge risk-badge-placeholder">
    <span class="risk-badge-emoji">🩺</span>
    <span>Awaiting patient data</span>
</div>
"""

# ---- 5. Core function: ML prediction + LLM advice ---------------------------
@spaces.GPU  # no GPU work happens here; this only satisfies HF's free ZeroGPU hardware check
def advise_patient(age, systolic_bp, diastolic_bp, bs, body_temp, heart_rate):
    """Predict the risk level with the ML pipeline, then ask the LLM for advice."""
    values = [age, systolic_bp, diastolic_bp, bs, body_temp, heart_rate]
    if any(v is None for v in values):
        raise gr.Error("Please fill in all six measurements before submitting.")

    patient = pd.DataFrame([values], columns=FEATURES)
    risk_level = predictor.predict(patient)[0]

    try:
        proba = predictor.predict_proba(patient)[0]
        confidences = dict(zip(predictor.classes_, proba))
    except AttributeError:
        confidences = {risk_level: 1.0}

    user_message = f"""Here is a patient. Please advise her.

Age: {age} years
Systolic BP: {systolic_bp} mmHg
Diastolic BP: {diastolic_bp} mmHg
Blood sugar (BS): {bs} mmol/L
Body temperature: {body_temp} F
Heart rate: {heart_rate} bpm

Risk level predicted by our screening model: {risk_level.upper()}"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": HEALTH_ADVISOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
        )
    except Exception as exc:
        raise gr.Error(
            f"The LLM call failed: {exc}. "
            "(401 = bad/expired API key; 429 = free-tier rate limit - wait a minute.)"
        )

    return risk_badge_html(risk_level), confidences, response.choices[0].message.content


def reset_form():
    return 25, 110, 70, 6.5, 98, 72, WELCOME_HTML, None, ""


# ---- 6. Look & feel -----------------------------------------------------
THEME = gr.themes.Soft(
    primary_hue="teal",
    secondary_hue="rose",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Nunito"), "ui-sans-serif", "system-ui", "sans-serif"],
)

CUSTOM_CSS = """
.gradio-container {
    max-width: 1100px !important;
    margin: auto !important;
}

.app-header {
    display: flex;
    align-items: center;
    gap: 18px;
    padding: 22px 28px;
    margin-bottom: 8px;
    border-radius: 18px;
    background: linear-gradient(120deg, #0f766e 0%, #14b8a6 55%, #fb7185 100%);
    box-shadow: 0 8px 24px rgba(15, 118, 110, 0.25);
}
.app-header-emoji { font-size: 2.6rem; line-height: 1; }
.app-header h1 { margin: 0; color: #ffffff; font-size: 1.6rem; font-weight: 800; }
.app-header p { margin: 2px 0 0; color: #f0fdfa; opacity: 0.95; font-size: 0.95rem; }

.mc-panel {
    border-radius: 18px !important;
    padding: 18px !important;
    box-shadow: 0 2px 10px rgba(15, 23, 42, 0.06);
}

.risk-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-size: 1.15rem;
    font-weight: 800;
    padding: 16px;
    border: 2px solid;
    border-radius: 14px;
    margin-bottom: 12px;
}
.risk-badge-emoji { font-size: 1.4rem; }
.risk-badge-placeholder { opacity: 0.6; border-style: dashed; }

.mc-footer {
    text-align: center;
    font-size: 0.82rem;
    color: #6b7280;
    padding: 14px 8px 4px;
}

.dark .mc-panel { background: #1f2937 !important; }
.dark .mc-footer { color: #9ca3af; }
"""

# ---- 7. Gradio interface (dashboard layout) ----------------------------------------------------
with gr.Blocks(title="MamaCare — Maternal Health Risk Advisor") as app:
    gr.HTML(
        """
        <div class="app-header">
            <div class="app-header-emoji">🤰</div>
            <div>
                <h1>MamaCare</h1>
                <p>ML-powered maternal health risk screening + AI-personalised advice</p>
            </div>
        </div>
        """
    )

    with gr.Accordion("ℹ️ How this works", open=False):
        gr.Markdown(
            "Enter the patient's six measurements and click **Analyze**. A trained "
            "machine-learning model (Gradient Boosting) predicts a risk level, then an "
            "LLM turns the numbers and the prediction into warm, practical advice.\n\n"
            "*3MTT student educational tool only — it never replaces antenatal care by a "
            "qualified health provider.*"
        )

    with gr.Row(equal_height=False):
        with gr.Column(scale=5, elem_classes="mc-panel"):
            gr.Markdown("### 📋 Patient Vitals")
            with gr.Row():
                age = gr.Number(label="Age (years)", value=25)
                heart_rate = gr.Number(label="Heart rate (bpm)", value=72)
            with gr.Row():
                systolic_bp = gr.Number(label="Systolic BP (mmHg)", value=110)
                diastolic_bp = gr.Number(label="Diastolic BP (mmHg)", value=70)
            with gr.Row():
                bs = gr.Number(label="Blood sugar (mmol/L)", value=6.5)
                body_temp = gr.Number(label="Body temperature (F)", value=98)

            with gr.Row():
                reset_btn = gr.Button("↺ Reset")
                submit_btn = gr.Button("🩺 Analyze & Get Advice", variant="primary")

            gr.Examples(
                examples=[
                    [35, 140, 95, 13.0, 98, 82],
                    [25, 110, 70, 6.5, 98, 72],
                ],
                inputs=[age, systolic_bp, diastolic_bp, bs, body_temp, heart_rate],
                label="Try a demo patient",
            )

        with gr.Column(scale=6, elem_classes="mc-panel"):
            gr.Markdown("### 🩺 Assessment")
            risk_output = gr.HTML(value=WELCOME_HTML)
            confidence_output = gr.Label(label="Model confidence", num_top_classes=3)
            advice_output = gr.Markdown(label="Personalised advice", container=True)

    gr.HTML(
        '<div class="mc-footer">Built for 3MTT · Not a diagnostic device · '
        'Always seek care from a qualified health provider.</div>'
    )

    submit_btn.click(
        fn=advise_patient,
        inputs=[age, systolic_bp, diastolic_bp, bs, body_temp, heart_rate],
        outputs=[risk_output, confidence_output, advice_output],
    )
    reset_btn.click(
        fn=reset_form,
        inputs=None,
        outputs=[age, systolic_bp, diastolic_bp, bs, body_temp, heart_rate,
                  risk_output, confidence_output, advice_output],
    )

if __name__ == "__main__":
    app.launch(theme=THEME, css=CUSTOM_CSS)
