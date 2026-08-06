# Part 3 — From Notebook to `app.py`: The Transition Guide 📓➡️🐍

**Prerequisites:** Part 1 (`Maternal_Health_Risk_ML_Notebook.ipynb` → saved
`maternal_risk_pipeline.joblib`) and Part 2 (`Maternal_Health_LLM_Notebook.ipynb` →
system prompt + `advise_patient()`).

**The goal:** turn our working notebook code into a real web application —
a single file called **`app.py`** — that anyone can open in a browser, type six
measurements into, and get personalised advice from. Same flow as before:

```
 patient's numbers ──▶ ML pipeline ──▶ "high risk" ──┐
        │                                            ├──▶  LLM  ──▶ friendly, personal advice
        └────────────────────────────────────────────┘
```

The only thing that changes is the *packaging*: cells become a script, and
`input()` becomes a **Gradio** web page.

---

## 0. Why convert at all? Notebook vs App

| | Notebook (`.ipynb`) | App (`app.py`) |
|---|---|---|
| Who runs it | **You**, cell by cell | A **server**, top to bottom, once |
| Who uses it | People who know Python | **Anyone with a browser** |
| Input | `input()` prompts, edited cells | Text boxes and a button |
| Secrets | You paste the key when asked | Read silently from the environment |
| Lifetime | Dies when the kernel stops | Runs continuously, serves many users |

A notebook is a **classroom**; a `.py` file is a **product**. Deployment platforms
(like Hugging Face Spaces) cannot "run cells" — they run one script from top to
bottom and keep the resulting web server alive. That single fact explains almost
every change below.

---

## 1. The big picture: what maps to what

Only four notebook sections contain *machinery* — everything else was lesson
material and stays behind.

| Part 2 notebook | Goes into `app.py`? | As what |
|---|---|---|
| §1–2 What is an LLM / getting a key | ❌ dropped | lesson text |
| §3 Setup (client, `.env`) | ✅ | **Part 1 of app.py** — client at module level |
| §4 First LLM call | ❌ dropped | practice demo |
| §5 `HEALTH_ADVISOR_SYSTEM_PROMPT` | ✅ **copied verbatim** | **Part 3 of app.py** |
| §6 Load the pipeline | ✅ | **Part 2 of app.py** — loaded once at startup |
| §7 `advise_patient()` | ✅ (lightly hardened) | **Part 4 of app.py** |
| §7.1–7.2 Demo patients | ✅ recycled | the interface's clickable **examples** |
| §8 `input()` cell | ❌ **replaced** | the **Gradio interface** (Part 5 of app.py) |
| §9 Recap & exercises | ❌ dropped | lesson text |

**Rule of thumb:** if a cell *teaches*, it stays in the notebook. If a cell
*does*, it moves to the script.

---

## 2. Step-by-step: the five changes that matter

### Step 1 — All imports at the top, all heavy things load ONCE

In a notebook you spread imports across cells and re-run whatever you like. A
script runs top-to-bottom exactly once when the server starts — so the model and
the LLM client are created at **module level**, *outside* any function:

```python
predictor = joblib.load('maternal_risk_pipeline.joblib')   # once, at startup
client    = OpenAI(base_url=BASE_URL, api_key=api_key)     # once, at startup
```

Why it matters: every button click calls `advise_patient()`. If the
`joblib.load()` lived *inside* that function, we would reload a half-megabyte
model on every single click. Load once, reuse forever.

### Step 2 — The API key: environment only, no `getpass`

The notebook had a friendly fallback: *if no `.env` is found, ask with
`getpass`*. A deployed server has **nobody at the keyboard** — `getpass` would
hang forever. So the app reads the key from the environment and **fails loudly
and clearly** if it's missing:

```python
load_dotenv()                              # reads .env locally; no-op on a server
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY not found. Locally: put it in a .env file next to app.py "
        "(GROQ_API_KEY=gsk_...). On Hugging Face Spaces: add it under "
        "Settings -> Variables and secrets."
    )
```

- **Locally:** the key lives in `.env` (same file as Part 2 — `=` sign, no quotes).
- **Deployed:** the key lives in the platform's *Secrets* and arrives as an
  environment variable — the code doesn't change at all. `load_dotenv()` simply
  finds nothing and steps aside.
- **Never** in the code, **never** uploaded, **never** on GitHub.

### Step 3 — Harden `advise_patient()` for strangers

The core function is *unchanged* from §7 — same DataFrame, same prediction, same
user message, same `temperature=0.4`. But a web app is used by strangers who
will leave boxes empty and click at the worst moments, so two guards were added:

```python
    if any(v is None for v in values):
        raise gr.Error("Please fill in all six measurements before submitting.")
    ...
    except Exception as exc:
        raise gr.Error(
            f"The LLM call failed: {exc}. "
            "(401 = bad/expired API key; 429 = free-tier rate limit - wait a minute.)"
        )
```

`gr.Error` is Gradio's polite crash: instead of a Python traceback filling the
server logs, the user sees a red toast message explaining what to do.

### Step 4 — Gradio replaces `input()`

The §8 cell asked six questions with `input()`. Gradio does the same thing with
boxes and a button. The whole interface is one call:

```python
demo = gr.Interface(
    fn=advise_patient,                       # ← the notebook function, unchanged
    inputs=[
        gr.Number(label="Age (years)", value=25),
        gr.Number(label="Systolic BP (mmHg)", value=110),
        gr.Number(label="Diastolic BP (mmHg)", value=70),
        gr.Number(label="Blood sugar (mmol/L)", value=6.5),
        gr.Number(label="Body temperature (F)", value=98),
        gr.Number(label="Heart rate (bpm)", value=72),
    ],
    outputs=[
        gr.Label(label="Risk level (ML model)"),        # ← 1st return value
        gr.Markdown(label="Personalised advice (LLM)"), # ← 2nd return value
    ],
    examples=[
        [35, 140, 95, 13.0, 98, 82],  # the Part 1/2 high-risk demo patient
        [25, 110, 70, 6.5, 98, 72],   # the low-risk demo patient
    ],
)
```

The mapping is beautifully mechanical:

- `advise_patient` takes **6 arguments** → the interface has **6 inputs**, in the
  same order.
- It returns **2 values** `(risk_level, advice)` → the interface has **2
  outputs**: a `gr.Label` for the risk, and `gr.Markdown` so the LLM's
  `**bold**` section headers render properly instead of showing as asterisks.
- The §7.1/§7.2 demo patients become `examples` — one-click buttons under the
  form, perfect for a live demo in class.

### Step 5 — The `__main__` guard

The very last lines:

```python
if __name__ == "__main__":
    demo.launch()
```

This means *"only start a local web server if the file is run directly"*
(`python app.py`). When a hosting platform **imports** the file instead, it
finds the `demo` object and serves it its own way. One file, both worlds.

---

## 3. Run it locally

```
.venv\Scripts\python.exe app.py
```

Then open the printed link — normally **http://127.0.0.1:7860** — in your
browser. Type numbers or click an example, press **Submit**, and you'll see the
ML prediction and the LLM's advice, exactly as in the notebook but wearing a
web interface. `Ctrl+C` in the terminal stops the server.

---

## 4. Deploy to Hugging Face Spaces (not Vercel!)

*(Full step-by-step walkthrough with screenshotted-in-words instructions and a
troubleshooting checklist: see `Part4_Deploy_to_HuggingFace.md`. The summary
below is the quick version.)*

**Why not Vercel?** Vercel is built for JavaScript sites and short-lived
serverless functions: it has no long-running Python server (which Gradio needs)
and its size limits can't hold scikit-learn + pandas + gradio. **Hugging Face
Spaces** is made by the same company as Gradio, has a free CPU tier, installs
`requirements.txt` automatically, and manages secrets properly.

1. Sign up at **huggingface.co** → **New Space** → SDK: **Gradio** → hardware:
   **CPU basic (free)**.
2. Upload exactly **three files** via the Space's *Files* tab:
   - `app.py`
   - `maternal_risk_pipeline.joblib`
   - `requirements.txt`

   ⚠️ **Never upload `.env`** — that file is your password.
3. Space **Settings → Variables and secrets → New secret**: name
   `GROQ_API_KEY`, value your `gsk_...` key. It reaches `app.py` as an
   environment variable — exactly where Step 2 taught the code to look.
4. The Space builds itself (~2–3 minutes) and goes live at
   `https://huggingface.co/spaces/<your-username>/<space-name>` — a public link
   you can share with anyone.

---

## 5. Gotchas checklist

- ✅ `requirements.txt` pins **`scikit-learn==1.6.0`** — the pipeline artifact
  was pickled with it. Don't upgrade sklearn on the Space, or the joblib file
  won't load.
- ✅ The feature order is sacred:
  `['Age', 'SystolicBP', 'DiastolicBP', 'BS', 'BodyTemp', 'HeartRate']`.
- ✅ Rotate your Groq key at **console.groq.com** before putting it in a public
  Space if it may ever have leaked (then update `.env` and the Space secret).
- ✅ `temperature=0.4` stays — health advice should be calm and consistent.
- ⚕️ The ethics rule travels with the system prompt: this tool supports
  education and awareness — it must **never** replace antenatal care.

**What we learned:** a web app is not new code — it's the *same* code, loaded
once, guarded against strangers, and wearing a Gradio interface instead of
`input()`.
