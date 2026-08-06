# Personal Site — Context & Editing Guide

A reference for editing and redeploying this site yourself, without needing to re-explain the project from scratch. Keep this file updated if the structure changes.

**Status: live.** Deployed at **https://micheal.fly.dev** (Fly app `micheal`, first deployed 2026-07-20). Scale-to-zero is active — the machine stops when idle and wakes on the next visit (a few seconds' delay for that first visitor), same as the Avatar app.

## What this is

A **plain static site** — HTML/CSS/vanilla JS. No framework, no build step, no `package.json`, no bundler. You edit the files directly and what you see is what ships.

Four core pages, all sharing the same nav and `<head>` (fonts + `css/tokens.css` + `css/site.css`), plus one detail page per project post (see "Add a project post" below):

| Page | Purpose |
|---|---|
| `index.html` | Home: hero, "story" (expandable bio), current work, CTA to Avatar |
| `about.html` | Full CV: projects, skills, certifications, career history, education, conferences, testimonials, contact |
| `posts.html` | Project/post grid + FAQ list. Each card links to its own detail page in the repo root (e.g. `ai-banking-assistant.html`), not out to an external site |
| `avatar.html` | Embeds the separate Avatar chatbot project via iframe |
| `<project-slug>.html` | One per project post (11 as of 2026-08-06) - the deep-dive write-up, screenshots/video, and download links for that project |

If you ever add a 6th *type* of page, copy the header/nav block from any existing page verbatim, and add a matching `<li><a href="newpage.html">...</a></li>` to the `nav-links` list on **all** pages (there's no shared template - it's duplicated by hand in each file).

## How this relates to the Avatar project

These are **two completely separate projects with two separate Fly.io deployments** — this repo has no code dependency on the Avatar repo:

- This site → Fly app **`micheal`** → `https://micheal.fly.dev`
- Avatar chatbot (`Case_studies/avatar`, published at `github.com/Purepen/avatar`) → Fly app **`purepen`** → `https://purepen.fly.dev`

The only link between them is one line in [avatar.html](avatar.html):

```js
var BASE = "https://purepen.fly.dev";
```

`avatar.html` itself has no chatbot logic — it's just an `<iframe>` pointed at that URL. If you ever redeploy the Avatar project under a different app name or custom domain, this is the **only** line in this repo you need to change.

**Why the browser URL doesn't change to `purepen.fly.dev` when you open the Avatar page — this is intentional, not a bug.** An iframe embeds another site's content *inside* the current page, so the address bar stays on `micheal.fly.dev/avatar.html` the whole time (same reason an embedded YouTube video doesn't change the address bar to `youtube.com`). This is deliberate: it keeps your nav/branding around the chat instead of sending visitors off to a separate URL. Confirmed with the site owner (2026-07-21) — keep it as an iframe. The alternative (a plain `<a href="https://purepen.fly.dev">` link instead of the iframe) would make the URL change, but visitors would leave this site entirely and lose the header/footer/nav.

**FAQ numbers must stay in sync across the two projects.** The FAQ list on `posts.html` (Q1–Q20) links to `avatar.html?q=N`, which passes `N` into the iframe so the twin answers that question instantly with no typing. The actual questions/answers live in the Avatar project at `knowledge/faq.jsonl`. You can freely reword the *question text shown on posts.html* without touching the Avatar repo, but if you add, remove, or renumber FAQs in `faq.jsonl`, update the `Q#` list here to match — otherwise a link like `Q13` might trigger the wrong answer.

## File map

```
index.html, about.html, posts.html, avatar.html   — the 4 pages
Dockerfile                                          — nginx:alpine, copies the repo in, serves on port 80
css/tokens.css                                      — design tokens (colors, fonts, spacing) — shared with the Avatar design system
css/site.css                                        — all layout/component styles
js/nav.js                                           — active nav-link highlighting + mobile hamburger menu
js/story.js                                         — "Read more" expand/collapse on index.html's story section
js/posts-data.js                                    — the POSTS array that drives posts.html (see below)
assets/photo.png, avatar-robot-round.png, icons.svg — site-wide images/icon sprite
assets/post-placeholder.svg                         — neutral blank thumbnail for posts with no real image; never use assets/photo.png as a post thumbnail (owner's preference — keep personal photo off the posts grid)
assets/certs/*                                      — certification thumbnails (used in about.html)
assets/journey/*                                    — conference/"on the ground" photos (used in about.html)
assets/posts/<project-slug>/*                       — hero/gallery images for each project detail page
assets/downloads/<project-slug>/*                   — original downloadable files (PDFs, notebooks, datasets, models) linked from each project detail page
posts/                                               — gitignored; raw source material (docx/pdf/notebooks) the project write-ups were drawn from, kept locally only, not deployed
scripts/deploy.sh, scripts/fly.toml                 — deploy config for this site (Fly app "micheal")
```

## Editing content

Every section below is a **copy an existing block, edit the text, paste it above/below the last one** operation — nothing needs registering anywhere else, and there's no build step. Just save and (when ready) redeploy.

### 1. Add a project post → new page + `posts.html`

Every card on `posts.html` links to its own detail page in the repo root, not out to an external
site. To add one:

1. **Write the detail page.** Copy an existing one closest in shape to your new project (e.g.
   `powerbi-car-sales.html` for a BI dashboard, `ai-banking-assistant.html` for an AI build,
   `ai-has-no-brain.html` for a short note with no downloads/stats) and edit the content. The shared
   structure, all hand-written HTML, no shared template file, is: `post-back-link` → `post-detail-hero`
   (eyebrow category + `h1` + subtitle + tag row) → optional `post-hero-media` image or `video-embed`
   → `prose` sections → optional `stat-grid` → optional `post-gallery` → a `resource-grid` of
   `resource-item` links (live demo, GitHub, dataset, downloads, contact). All of these classes are
   defined in `css/site.css` under "Post detail pages". Set `<body data-nav="posts.html">` so the
   "Posts" nav link stays highlighted while reading it.
2. **Add assets.** Drop images in `assets/posts/<project-slug>/` and any downloadable original files
   (PDFs, notebooks, datasets, models) in `assets/downloads/<project-slug>/`, then link to them with a
   `resource-item`. If a link genuinely doesn't exist yet (e.g. "ask for the .pbix"), use
   `<span class="resource-item is-placeholder">` instead of an `<a>` so it doesn't look clickable.
3. **Add the card.** Open [js/posts-data.js](js/posts-data.js) and add an object to the `POSTS` array:

```js
{
  category: "ai",   // "ai" | "bi" | "ml" | "notes" — see CATEGORY_LABEL for the display text
  title: "Your project title",
  url: "your-project-slug.html",
  date: "2026-07",  // "YYYY-MM", a bare year, a range, or any free label
  excerpt: "One or two sentences describing it.",
  thumbnail: "assets/posts/your-project-slug/hero.jpg",  // optional — falls back to assets/post-placeholder.svg (never a personal photo) if omitted
},
```

Writing style for post copy (confirmed with the site owner): no em dashes, no emojis, avoid "it's
not X, it's Y" and other LLM tells, natural flowing prose over short staccato sentences.

### 2. Add a certification → `about.html`

Find the **"Licences & certifications"** section (search for `Licences &amp; certifications`). It's split into two `<h3>` sub-groups — **"AI engineering"** and **"Data & analytics"** — each holding an `<div class="entry-list">` of entries. Copy an existing entry into the right sub-group:

```html
<div class="entry cert-entry">
  <div class="cert-entry__row">
    <div class="cert-entry__thumb"><img src="assets/certs/your-file.jpg" alt="Your Certificate name certificate" loading="lazy" /></div>
    <div>
      <a href="https://your-credential-url" target="_blank" rel="noopener" class="entry__title">Certificate title</a>
      <p class="entry__date" style="margin:2px 0 var(--space-2);">Issuer, Mon YYYY &middot; duration (optional)</p>
      <p class="entry__desc">A sentence or two on what it covered / what you built.</p>
    </div>
  </div>
</div>
```

Notes:
- Drop the thumbnail image into `assets/certs/` first — match the filename in `src`.
- The `entry__date` line and the description are both optional/flexible — several existing entries skip `entry__date` and just fold the issuer/date into `entry__desc` (e.g. `<p class="entry__desc">micro1 Recruiting, May 2026</p>`) when there's no separate certificate link.
- If there's no verifiable link, drop the `<a>` wrapper and just use a plain `<span class="entry__title">`.
- Update the **"N in total"** count just under the section heading (`<p ...>18 in total.</p>`) after adding/removing.

### 3. Add a project → `about.html` ("Projects I'm proud of")

```html
<div class="entry">
  <div class="entry__meta"><span class="entry__title">Project name</span><span class="entry__date">2026</span></div>
  <p class="entry__desc">What it does / the problem it solves.</p>
  <div class="entry__tags"><span class="tag">Tech</span><span class="tag">Stack</span></div>
  <p style="margin-top:var(--space-2);"><a href="https://..." target="_blank" rel="noopener">Repo &rarr;</a></p>
</div>
```

`entry__date` can be a year, a range (`"2024 – 2025"`), or a status like `"In progress"` or `"Live"`. The tags row and the link line are both optional.

### 4. Add work experience → `about.html` ("Career history") and/or `index.html` / `about.html` ("What I do now")

- **Past roles** go in `about.html`'s "Career history" list — same `entry` / `entry__meta` / `entry__date` / `entry__desc` pattern as projects above (no tags, no link line).
- **Current roles** (the two `.card` blocks under "What I do now") are duplicated in **both** `index.html` and `about.html` — if you start/change a current role, update it in both places:

```html
<div class="card">
  <h3>Job title, Company</h3>
  <p class="entry__date" style="margin-bottom:var(--space-2);">since Mon YYYY</p>
  <p>What you do there, in a sentence or two.</p>
</div>
```

### 5. Add/edit a skill category → `about.html` ("Skills")

```html
<div class="card">
  <h3>Category name</h3>
  <p>Comma-separated list of tools/skills.</p>
</div>
```

### 6. Add education → `about.html` ("Education")

```html
<div class="entry">
  <div class="entry__meta"><span class="entry__title">Institution, Degree</span><span class="entry__date">Mon YYYY – Mon YYYY</span></div>
</div>
```

### 7. Add a conference / "on the ground" photo → `about.html` ("Conferences & the work behind it")

Drop the photo in `assets/journey/`, then:

```html
<div class="journey-card">
  <div class="journey-card__thumb"><img src="assets/journey/your-file.jpg" alt="Description for accessibility" loading="lazy" /></div>
  <div class="journey-card__body">
    <p class="eyebrow journey-kicker">Conference</p>   <!-- or "On the ground" / "Community" -->
    <span class="journey-title">Short title</span>
    <p class="entry__desc">A sentence of context.</p>
  </div>
</div>
```

### 8. Add/edit a testimonial → `about.html` ("What people say")

```html
<blockquote class="quote">
  &ldquo;Quote text.&rdquo;
  <cite>Name, Title, Company</cite>
</blockquote>
```

### 9. Contact links / socials

These are duplicated in **three** places — update all of them together: `index.html` hero chip-row, `index.html` footer chip-row, and `about.html` "Links & contact" section. Email also appears as a `mailto:` link in both footers' CTA button context.

### 10. Edit the FAQ list → `posts.html`

Each FAQ is one line:

```html
<a class="faq-item" href="avatar.html?q=21"><span class="faq-item__q"><span class="faq-item__num">Q21</span><span class="faq-item__text">Your question text</span></span><span class="faq-item__cta">Ask the twin<svg class="icon icon--sm"><use href="assets/icons.svg#i-arrow-right"></use></svg></svg></span></a>
```

Remember: the number after `q=` must correspond to a `faq` entry in the **Avatar project's** `knowledge/faq.jsonl` — adding a `Q21` here does nothing useful unless FAQ #21 also exists there (and that project gets redeployed for the new answer to be live).

### 11. Edit hero / bio text → `index.html`

The hero (`<section class="hero">`) and the "story" section (`<section class="section story">`) are hand-written prose — just edit the text in place. The `id="storyMore"` block is the part hidden behind the "Read more" toggle (driven by `js/story.js`); anything inside `<div class="story__fade">` (before the toggle) is always visible.

## Styling / design tokens

- [css/tokens.css](css/tokens.css) — brand colors (indigo `#5156be` primary, green `#2ab57d` actions, sky `#4ba6ef` info), fonts (Newsreader for display/headings, Hanken Grotesk for body, JetBrains Mono for labels), spacing scale, and both light/dark theme variables. These tokens are shared with the Avatar project's design system, so the two sites read as one brand — avoid introducing new one-off colors.
- [css/site.css](css/site.css) — all component and layout CSS (`.post-card`, `.entry`, `.cert-entry`, `.journey-card`, `.faq-item`, `.card`, `.chip`, buttons, nav, etc.), plus a "Post detail pages" section (`.post-detail-hero`, `.stat-grid`, `.post-gallery`, `.video-embed`, `.resource-grid`, `.post-callout`) used by every project page. Reuse an existing class rather than inventing new CSS where possible.

## Deployment / redeploying

This is a static site with **no secrets, no database, no env vars, no build step** — deploying just copies the folder into an nginx image and ships it.

**Prerequisite (one-time):** install `flyctl` and run `fly auth login`. On this machine `flyctl` is installed at `C:\Users\admin\.fly\bin\flyctl.exe` but isn't on the default shell `PATH` — if `scripts/deploy.sh` reports "flyctl not found", add that folder to `PATH` for the session first (e.g. in Git Bash: `export PATH="/c/Users/admin/.fly/bin:$PATH"`) rather than reinstalling.

**Every time you want to publish changes:**

```bash
scripts/deploy.sh
```

That's it — from the repo root, it deploys to the Fly app `micheal` (creating it on first run) and prints `Deployed: https://micheal.fly.dev`. There's nothing else to stage or configure; any saved change to any `.html`/`.css`/`.js`/`assets` file will go live on the next run of that script.

**Config reference** (`scripts/fly.toml`): app `micheal`, region `lhr` (same as the Avatar app, for consistency — not a hard requirement), scale-to-zero (`min_machines_running = 0`), served by nginx on port 80.

**Previewing locally before deploying:** since there's no build step, you can just open any `.html` file directly in a browser, or run a tiny local server from the repo root (e.g. `python -m http.server 8080` or `npx serve`) and browse to it — either works because all asset paths are relative.
