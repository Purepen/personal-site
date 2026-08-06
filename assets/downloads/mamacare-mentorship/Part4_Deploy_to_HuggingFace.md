# Part 4 — Deploy Your App to Hugging Face Spaces 🚀

**Prerequisites:** your own working copy of the four files below (from Part 3), and
your own free Groq API key (from Part 2).

```
app.py                          ← the Gradio app
requirements.txt                ← exact library versions it needs
README.md                       ← tells Hugging Face how to run it
maternal_risk_pipeline.joblib   ← the trained ML model
```

**The goal:** turn the app running on *your* laptop into a public web link
anyone can open — `https://huggingface.co/spaces/<your-username>/<your-space-name>`.
Every student deploys **their own** Space, under **their own** Hugging Face
account, with **their own** Groq key.

⚠️ **Read Step 1 before you do anything else.** Hugging Face's rules about who
can host a free Space changed recently, and one of those rules depends on
*how old your account is* — something you cannot fix in the middle of class.
Check it first.

---

## 0. Why Hugging Face Spaces?

Your laptop can run `app.py` and print `http://127.0.0.1:7860` — but that link
only works *on your machine*. To get a link that works for anyone, anywhere,
the code needs to live on a server that's always on.

Hugging Face Spaces is the natural home for a Gradio app:

- It **already knows Gradio** — no server configuration.
- It reads `requirements.txt` and installs everything automatically.
- It has a proper, private place for secrets (your API key never appears in
  public code).
- It has a genuinely free hosting path for a small app like ours (details in
  Step 1 and Step 2 — it's not quite as simple as it used to be, so read
  carefully).

Think of it like this: your laptop is a rehearsal room, Hugging Face Spaces is
the stage.

---

## 1. Create your Hugging Face account — and check you actually qualify for free hosting

1. Go to **huggingface.co** → **Sign Up** (free, no card required to sign up).
2. Verify your email — you cannot create *any* Space until you do.
3. **Now the part most guides skip.** As of 2026, Hugging Face's official
   policy states:

   > "Gradio and Docker Spaces run on compute and require a paid plan to
   > create: PRO for personal accounts... Free personal accounts in good
   > standing can still host up to 2 Gradio Spaces running on **ZeroGPU**."

   And Hugging Face defines "good standing," for hosting a free ZeroGPU
   Space, as:

   > "accounts in good standing (**verified email, account older than 30
   > days**)"

   Read that again: **a brand-new account cannot host a live Gradio app for
   free — not even on the smallest free CPU tier — until it is more than 30
   days old.** This is not something you did wrong; it's a platform rule, and
   there is no workaround for it.

   **What this means for you, right now:**
   - If you already have a Hugging Face account that's over a month old →
     you're fine, skip ahead to Step 2.
   - If you just created your account today for this class → you can still
     do **everything up to deployment**: run `app.py` locally (Part 3), and
     come back to finish this step once your account passes the 30-day mark.
     Ask your instructor whether the class will demo from one older shared
     account in the meantime.
   - Either way, you're also capped at **2 free ZeroGPU Spaces per account,
     ever** (not 2 at a time — 2 total, unless you delete an old one first).
     Don't burn one of your two slots on a throwaway test name.

---

## 2. Create a new Space

1. Go to **huggingface.co/spaces** and click **Create new Space** (or:
   profile picture, top right → **New Space**).
2. Fill in the form exactly as follows:
   - **Owner** — your username (or a class organization, if your instructor
     set one up).
   - **Space name** — e.g. `mamacare-advisor`. This becomes part of your
     public URL, so keep it short and avoid spaces (use hyphens).
   - **License** — optional; MIT is a reasonable default for a class project.
   - **Short description** — optional, one line is fine (e.g. "ML + LLM
     maternal health risk advisor").
   - **Select the Space SDK** — you'll see three tiles: **Gradio**, **Docker**,
     **Static HTML**. Click **Gradio**.
   - **Space hardware** — this is the field that trips people up. You'll see
     a list starting with **CPU Basic** (shown as "Free") and going up
     through paid GPU tiers. **Do not pick CPU Basic** — for a Gradio Space
     on a free personal account, Hugging Face will reject it at creation
     time with `402 Payment Required`, because (per Step 1) CPU Basic
     hosting for a live Gradio app now requires a paid plan. Scroll the
     hardware list and select **ZeroGPU** instead — it's the one genuinely
     free option. (Step 2a explains why our CPU-only app still needs this
     GPU-flavored hardware, and what one line of code has to do with it.)
   - **Visibility** — **Public** (classmates and family can open the link),
     or **Private** (only you can access it; "Protected" is a paid-plan-only
     option, skip it).
3. Click **Create Space**.

You'll land on an almost-empty Space with its own Git repository and a
**Files** tab. That's where your four files go next (Step 3).

### 2a. Why `app.py` has a `@spaces.GPU` line

ZeroGPU Spaces are a **shared, on-demand GPU pool**: Hugging Face only
attaches a real GPU to your app for the few seconds a request actually needs
one, then releases it for someone else's Space to use. To make that possible,
**ZeroGPU refuses to even start unless at least one function in `app.py` is
decorated with `@spaces.GPU`** — that decorator is literally how the platform
knows *which* function might need a GPU.

Our app never touches a GPU — scikit-learn's `.predict()` and the Groq API
call are both plain CPU work — but the platform doesn't know that until we
tell it, so the decorator is present purely to satisfy ZeroGPU's startup
check:

```python
import spaces
...

@spaces.GPU  # no GPU work happens here; this only satisfies ZeroGPU's startup check
def advise_patient(age, systolic_bp, diastolic_bp, bs, body_temp, heart_rate):
    ...
```

This is already in the `app.py` you're uploading — you don't need to add it
yourself, just understand why it's there. `requirements.txt` also lists the
`spaces` package for the same reason. Two useful facts about it, straight
from Hugging Face's own docs:

- **It's harmless locally.** "The `@spaces.GPU` decorator is designed to be
  effect-free in non-ZeroGPU environments" — so `python app.py` on your
  laptop behaves exactly as before, decorator or not.
- **It has a time limit.** Free accounts get a **daily quota of 5 minutes**
  of actual GPU-attached run time (resets 24 hours after your first call of
  the day), and by default each `@spaces.GPU` call is capped at **60
  seconds**. Our function finishes in a few seconds (prediction is instant,
  the LLM call takes a couple of seconds), so this is not something you'll
  realistically hit in a classroom demo — just know it exists if the app
  ever seems to queue or slow down after heavy repeated testing.

If a Space ever fails to start with `RUNTIME_ERROR: "No @spaces.GPU function
detected during startup"`, it means whatever `app.py` got uploaded is missing
this decorator — re-upload the correct file from this project.

---

## 3. Upload your files

You have two ways to do this. Use the web UI unless you're already
comfortable with a terminal (the CLI method, and a git method, are in
Step 7).

### Web UI (recommended for your first deploy)

1. On your new Space's page, click the **Files** tab.
2. Click the **Add file** button (usually near the top right of the file
   list).
3. From the dropdown, choose **Upload file(s)** — *not* "Create a new file"
   (that opens a blank text editor, which is for typing code by hand, not
   for uploading something already on your computer).
4. A file picker (or drag-and-drop drop-zone) opens. Either:
   - **Drag** all four files from your project folder straight into the
     browser window, or
   - **Click to browse**, then select all four files at once — hold
     **Ctrl** (Windows/Linux) or **Cmd** (Mac) while clicking each one to
     multi-select:
     ```
     app.py
     requirements.txt
     README.md
     maternal_risk_pipeline.joblib
     ```
5. Wait for all four to show as "queued"/uploaded in the panel (the
   `.joblib` file is the largest at ~530 KB, so this is fast even on a slow
   connection).
6. Type a short commit message, e.g. `Deploy MamaCare app`.
7. Click **Commit changes to main**.

⚠️ **Do NOT upload your `.env` file.** That file holds your private API key —
uploading it would publish your password to the whole internet. (If you don't
see a `.env` file in your project folder, that's correct — it is deliberately
*not* one of the four files above.)

The Space will immediately start rebuilding — don't worry about the error
you'll see in the logs yet, that's expected (see Step 4).

### If you make a mistake

Uploaded the wrong file, or need to replace one? Repeat the same **Add
file → Upload file(s)** flow with the corrected file — uploading a file with
the same name overwrites the old version and creates a new commit. Nothing is
destroyed; every past version stays visible under the **History** link on the
Files tab if you ever need to go back.

---

## 4. Add your secret API key

Your app raises a clear error if `GROQ_API_KEY` is missing — and right now,
it is, because you (correctly) didn't upload `.env`. Give the Space its own
copy of the key, kept private:

1. On your Space, click **Settings** (top of the page).
2. Scroll to the **Variables and secrets** section.
3. You'll see two separate buttons: **New variable** and **New secret** —
   these are *not* the same thing. **Variables** are stored in plain text and
   visible to anyone who opens your Space's settings; **secrets** are
   encrypted and never shown again once saved. An API key must always be a
   **secret**, never a variable.
4. Click **New secret**.
5. **Name:** `GROQ_API_KEY` (must match exactly, capital letters included —
   this is the same name `app.py` looks for with
   `os.environ.get("GROQ_API_KEY")`).
6. **Value:** paste your `gsk_...` key from console.groq.com.
7. Click **Save**.

The Space automatically restarts and injects the secret as an environment
variable — the exact same mechanism as your local `.env` file, just hosted
instead of on your laptop. `app.py` doesn't need to change at all for this to
work; that's the whole point of reading the key from the environment instead
of hard-coding it.

---

## 5. Watch it build, then test it

1. Go back to the **App** tab. You'll see a build log — installing
   `requirements.txt` (pandas, scikit-learn, gradio, etc.) typically takes
   1–3 minutes the first time.
2. When the status badge at the top says **Running**, your app is live at:
   ```
   https://huggingface.co/spaces/<your-username>/<your-space-name>
   ```
   (Hugging Face also gives it a shorter direct URL,
   `https://<your-username>-<your-space-name>.hf.space`, which works the
   same way.)
3. Test it exactly like you did locally: click one of the example patients,
   press **Analyze & Get Advice**, and confirm you get a risk badge, a
   confidence breakdown, and personalised advice back.

That URL is now a real, shareable product. Send it to a classmate and watch
them use something you built.

**One more thing to expect:** on free hardware, an idle Space "goes to
sleep" after a period of no visits (roughly two days). This is normal, not a
bug — the first visitor after a nap just has to wait ~30–60 seconds for it to
wake back up, then it runs at normal speed for everyone after that.

---

## 6. Troubleshooting checklist

| Symptom | Cause | Fix |
|---|---|---|
| Creating the Space fails with `402 Payment Required`, mentioning a PRO subscription | You selected **CPU Basic** hardware instead of **ZeroGPU** | Go back and re-create the Space (or change hardware in Settings) choosing **ZeroGPU** — see Step 2 |
| Everything looks right but you *still* can't create/host a Space, or hosting silently isn't offered | Your account is younger than 30 days, or your email isn't verified | Re-read Step 1 — there is no technical fix, only time and email verification |
| `403`/quota-style error mentioning "2 Spaces" or a hosting limit | You've already used both of your free account's ZeroGPU Space slots | Delete an old/unused Space (Settings → delete, at the bottom) to free a slot, or reuse an existing one instead of creating a new one |
| Build fails: `ModuleNotFoundError` | A library is missing from `requirements.txt` | Check every `import` in `app.py` has a matching line in `requirements.txt` |
| Build fails / crashes loading the model | `scikit-learn` version doesn't match what the pipeline was saved with | Keep `scikit-learn==1.6.0` pinned in `requirements.txt` — don't "helpfully" upgrade it |
| Space status is `RUNTIME_ERROR`: "No @spaces.GPU function detected during startup" | The uploaded `app.py` is missing the `@spaces.GPU` decorator (see Step 2a) | Re-upload the current `app.py` from this project — it already has the fix |
| App loads but crashes on submit: `GROQ_API_KEY not found` | Secret name typo, you saved it as a **variable** instead of a **secret**, or you forgot Step 4 | Settings → Variables and secrets → confirm there's a **secret** (not variable) named exactly `GROQ_API_KEY` |
| `401` error when you click Analyze | Bad or expired API key | Get a fresh key at console.groq.com and update the Space secret |
| `429` error when you click Analyze | Groq's free-tier rate limit | Wait a minute and try again |
| Space stuck "Building" for a long time | Normal on first build (installing pandas/sklearn/gradio) | Give it 2–3 minutes before worrying |
| App is slow or unresponsive on first visit after a while | The Space was asleep (see Step 5) | Wait ~30–60 seconds and reload — it wakes up automatically |

---

## 7. (Bonus, for the CLI-curious) Deploying from a terminal

Everything above can also be done without the browser, using the `hf`
command-line tool that installs alongside `gradio` (`pip install huggingface_hub`
if it's ever missing).

```bash
# 1. Log in once (opens a prompt for a token from huggingface.co/settings/tokens
#    — generate one with "Write" access)
hf auth login

# 2. Create the Space, explicitly on ZeroGPU (the free hardware — see Step 2a),
#    and set the secret straight from your local .env in the same command
hf repo create <your-username>/<space-name> --type space --sdk gradio \
  --flavor zero-a10g --secrets-file .env

# 3. Upload just the four files the app needs
hf upload <your-username>/<space-name> . --type space \
  --include "app.py" --include "requirements.txt" --include "README.md" --include "maternal_risk_pipeline.joblib" \
  --commit-message "Deploy MamaCare app"

# 4. Check on it
hf spaces wait <your-username>/<space-name>     # blocks until it's RUNNING (or fails loudly)
hf spaces logs <your-username>/<space-name>     # see what the app printed on startup
```

A third option, standard **git**, also works because every Space *is* a git
repository under the hood: `git clone` the Space's URL, copy your four files
in, `git add . && git commit -m "..." && git push`. Files over 10 MB need
`git xet track` first (ours don't — the `.joblib` is well under that), so for
a project this size the `hf upload` command above is simpler.

This is faster once you're comfortable with a terminal, and it's how you'd
script repeat deployments — but the web UI in Steps 1–5 is the one to teach
first: it makes every step (files, secrets, build logs) visible instead of
hidden behind a command.

---

## What we learned

Deploying isn't a separate skill from coding — it's **the same four files**,
placed somewhere that's always running, with the same secret-handling pattern
(environment variables) your app was already written to expect. What's new
is entirely *platform bookkeeping*: where the files live (a Space instead of
your laptop), where the secret lives (Settings → Variables and secrets
instead of `.env`), and — the part that catches people out — that "free"
hosting today comes with real conditions attached (account age, a 2-Space
cap, and a GPU-shaped hoop to jump through even for a CPU-only app). None of
that is a reflection of your code being wrong; it's just the current shape of
the free tier, and now you know it going in.

---

*This guide reflects Hugging Face's Spaces policy as of August 2026 (see
[Spaces Overview](https://huggingface.co/docs/hub/en/spaces-overview),
[Spaces ZeroGPU](https://huggingface.co/docs/hub/en/spaces-zerogpu), and
[Getting Started with Repositories](https://huggingface.co/docs/hub/en/repositories-getting-started)).
Hosting terms and UI labels can change — if something in this guide doesn't
match what you see on huggingface.co, trust the live site and let your
instructor know so this guide can be updated.*
