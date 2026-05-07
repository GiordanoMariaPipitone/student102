---
name: student102
description: >
  Add or create a lesson in an interactive HTML study guide, one directory = one lesson.
  Invocation: /student102 <directory> [existing_html_path].
  If only a directory is given, creates a new HTML file with one lesson named after the folder.
  If directory + html path is given, appends one new lesson (named after the folder) to the existing file.
  Uses design-taste-frontend for visual style, NanoBanana for AI images, DuckDuckGo for reference images,
  and interactive graphs (Chart.js / Plotly / Three.js / D3 / vis.js) as the core widget layer.
  HARD RULE: exactly one lesson per call; lesson name = folder name of the input directory.
---

# student102 — One-Lesson-at-a-Time Study Guide Builder

Generate or extend a self-contained interactive HTML study guide by adding **one lesson per call**. The lesson name is always derived from the **folder name** of the input directory — not from file contents or lesson numbering heuristics.

## Invocation

```
/student102 <directory> [existing_html_path]
```

| Arg | Required | Meaning |
|---|---|---|
| `directory` | Yes | Folder containing the lesson materials (PDFs, .ipynb, .md, .txt, .docx, images, code). The **folder name** becomes the lesson title. |
| `existing_html_path` | No | If provided → **append one new lesson** to this file. If omitted → **create a new HTML file** with this single lesson. |

**HARD RULES — never break these:**
1. **One lesson per call.** Each `/student102` invocation produces exactly one lesson in the output HTML, regardless of how many subfolders are in the directory.
2. **Lesson name = folder name.** If the directory is `C:\...\Backpropagation`, the lesson title is `Backpropagation`. Never rename it.
3. **At least one real interactive widget per lesson.** Static charts do not count.
4. **Everything you build MUST work AND MUST be visible as it should.** Before declaring the lesson complete you must mentally simulate (or, when possible, visually verify) that every widget renders, every interaction fires, every image loads, every code block has correct indentation/highlighting, every tab switches, every quiz reveals an answer. A widget that "exists in the DOM but is empty/broken/cut-off/overlapped/invisible" is a FAILED build. No exceptions. If anything is uncertain, fix it before finishing — never ship hidden, broken, or unreadable elements.
5. **Images must be readable — not microscopic, not page-dominating.** See the dedicated rules in *Image presentation rules* below. The image area used to be tiny; that is no longer acceptable.
6. **Format-sensitive content MUST be rendered in the correct format.** Code, JSON, YAML, math, tables, ASCII diagrams — anything whose meaning depends on whitespace, indentation, line breaks, or syntax highlighting — must be emitted preserving that format. See the dedicated rules in *Code & format-sensitive content rules* below. Code crammed onto one line, missing indentation, or with no syntax highlighting is a FAILED build.
7. **Visual quality is a first-class success criterion.** student102 is a *beautiful* study guide builder, not just a working one. The output must feel polished: balanced spacing, deliberate typography, harmonious palette, considered hierarchy, refined micro-interactions. "Eye-pleasing" is not a nice-to-have — it is part of done.

If a required argument is missing, ask the user — do not invent paths.

---

## Step 0 — Detect mode and resolve paths

```
MODE = "append" if existing_html_path is given else "create"
LESSON_NAME = Path(directory).name   # e.g. "Backpropagation", "CSS Flexbox", "Lezione 3"
```

For **append mode**: read the target HTML and count existing `<section data-lesson="N">` markers → `NEXT_N = count + 1`. The new lesson gets number `NEXT_N` and title `LESSON_NAME`.

For **create mode**: `NEXT_N = 1`. Output path = `<directory_parent>/<LESSON_NAME>.html`. Assets folder = `<directory_parent>/<LESSON_NAME>_assets/`.

---

## Step 1 — Inventory & subject detection

Recursively list `directory`. Read all source files:
- PDFs: `Read(file, pages="1-10")` (first 10 pages)
- `.ipynb`: read all cells, capture code + markdown
- `.md`, `.txt`: read fully
- Images: note paths for step 7

Extract and store a **lesson data object** (keep in context — no file write needed):

```json
{
  "lesson_n": 1,
  "lesson_name": "Backpropagation",
  "domain": "stem",
  "content_keywords": ["gradient", "chain rule", "weight update", "loss surface", "backprop"],
  "nanobanana_prompt": "Animated gradient flow through a neural network with glowing edges showing backpropagation, dark tech background, electric blue highlights",
  "search_queries": ["backpropagation neural network diagram", "gradient descent loss surface"],
  "style_hint": ""
}
```

Also detect **course subject** (one phrase) from folder name + file contents — e.g. "Deep Learning", "Greek Mythology", "Constitutional Law". This goes to Step 2.

Classify domain: **STEM** (math, code, equations, physics, datasets, circuits) vs **HUMANITIES** (dates, people, movements, philosophy, history, law).

---

## Step 2 — Design tokens + motif (invoke both skills in parallel)

In a single message, call both:

1. **`ui-ux-pro-max`** — Input: subject phrase + domain. Ask for: style direction, 4-color hex palette, font pair (display + body), spacing/radius scale.
2. **`design-taste-frontend`** — Input: same. Ask for: motif name, 3–5 inline SVG decorative primitives, palette override if anti-slop check rejects the first pick, metric rules, ban list.

Reconcile into a **JSON token blob**:

```json
{
  "subject": "Deep Learning",
  "motif": {
    "name": "neural-circuit",
    "primitives": ["node-glow.svg", "edge-arrow.svg", "gradient-bar.svg"],
    "background_texture": "circuit-trace"
  },
  "tokens": {
    "color": { "bg": "#0D0F1A", "ink": "#E8EAF6", "accent": "#3D8EF5", "muted": "#7B8FC7" },
    "font": { "display": "Outfit", "body": "Inter Tight", "mono": "JetBrains Mono" },
    "radius": { "sm": "4px", "md": "8px", "lg": "16px" },
    "spacing_unit_px": 8
  },
  "metric_rules": { "DESIGN_VARIANCE": 7, "MOTION_INTENSITY": 6, "VISUAL_DENSITY": 4 },
  "motion": {
    "easing_archetype": "electric-snap",
    "spring": { "stiffness": 120, "damping": 18 },
    "reveal_pattern": "stagger-children",
    "framer_mcp_preset_id": null
  }
}
```

**Conflict resolution:** `design-taste-frontend` wins on anti-slop (can override Inter, purple gradients, etc.); `ui-ux-pro-max` wins on layout-system numbers.

Also set `lesson_data.style_hint` from layer 2's motif and palette keywords (passed into NanoBanana prompt later).

---

## Step 3 — Shape three tab payloads

For the single lesson, produce:

1. **Teoria** — clean restructured theory from source materials.
2. **Esempi / Snippets** — worked examples, code blocks, source excerpts.
3. **Approfondimenti** — cross-topic connections, exam-likely questions, common pitfalls (clearly framed as synthesis, not source claims).

---

## Step 4 — Pick interactive widget(s)

**Every lesson must have at least one real interactive element.** Choose based on domain and content:

### STEM widgets

| Widget | Library | Use when |
|---|---|---|
| Parameter-slider chart | Chart.js / Plotly | Tunable functions (learning rate, sigmoid τ, RC constant) |
| Click-to-step algorithm | Vanilla JS + Framer Motion `AnimatePresence` | Sorting, BFS/DFS, backprop steps |
| 3D plot | Three.js r128 / Plotly 3D | Loss surfaces, vector fields, geometry |
| Manim animation | `manim -qm` → `<video controls loop>` | Temporal evolution (gradient descent path, convolution scan) |
| Live code sandbox | Pyodide / vanilla JS | Short editable cells |

**Manim rule:** generate `<assets>/manim/lesson_N/scene.py`, render via:
```bash
cd "<assets>/manim/lesson_N" && manim -qm scene.py SceneName
```
Embed resulting `.mp4`. If Manim unavailable → degrade to Plotly animation, never block the build.

### HUMANITIES widgets

| Widget | Library | Use when |
|---|---|---|
| Interactive timeline | Vanilla JS + Framer Motion stagger | Histories, movements |
| Concept network graph | vis.js / D3 force-directed | Relations between thinkers/works |
| Expandable schema | CSS `<details>` or D3 tree + Framer Motion unfurl | Taxonomies, frameworks |
| Comparative card flipper | CSS 3D + Framer Motion rotate | Two thinkers / two doctrines |
| Quote spotlight | Vanilla JS modal + Framer Motion `AnimatePresence` | Click quote → full passage |

### Universal (both domains)

- Sticky lesson selector (for multi-lesson guides in append mode).
- Tab strip: **Teoria | Esempi | Approfondimenti**.
- Self-test quiz (multiple choice + reveal answer) — required every lesson.
- Dark/light toggle persisting in `localStorage`.
- Search bar filtering content live.
- All transitions via Framer Motion with `motion.easing_archetype` from token blob.

---

## Step 5 — Render HTML

### Create mode

Produce a single self-contained `.html` file. Inline all CSS and JS. CDN-only externals:

- **Framer Motion:** `import { animate, inView, stagger } from "https://esm.sh/motion@latest"` inside `<script type="module">`.
- Chart.js, Plotly.js, Three.js r128, vis-network, D3 v7 — pinned versions.
- Google Fonts (display + body from layer 1).
- No build step, no npm.

Include in `<head>`:
```html
<meta name="student102-tokens" content="<base64-encoded JSON token blob>">
<meta name="student102-version" content="1.0">
```

### Append mode

1. `Read` the existing HTML.
2. Parse `<meta name="student102-tokens">` — reuse existing token blob (same motif, same palette, same fonts). Do NOT reinvent the style.
3. Find the last `</section>` before `</main>` (or `</body>` fallback) — insert new lesson section after it.
4. Update the sticky lesson selector to include the new lesson tab.
5. Use **`Edit`** (targeted), never `Write`, for files > 1500 lines. For smaller files, `Write` is acceptable.
6. Preserve any `<!-- USER-EDIT-KEEP -->...<!-- /USER-EDIT-KEEP -->` blocks verbatim.

### Lesson section skeleton

Every lesson section emitted by student102 must follow this skeleton exactly so append mode can find it:

```html
<section data-lesson="N" data-domain="stem|humanities" data-source-hash="<sha1-of-dir-mtime>" data-motif="<motif-name>" data-lesson-title="<LESSON_NAME>">
  <header class="lesson-header">
    <h2>Lesson N — <LESSON_NAME></h2>
  </header>
  <nav class="tabs" role="tablist">
    <button role="tab" aria-selected="true"  data-tab="teoria">Teoria</button>
    <button role="tab" aria-selected="false" data-tab="esempi">Esempi</button>
    <button role="tab" aria-selected="false" data-tab="approfondimenti">Approfondimenti</button>
  </nav>
  <div class="tab-panel" data-tab="teoria" data-anim="tab-panel">
    <!-- theory content -->
    <!-- s102-image-gallery inserted by Step 8 AFTER HTML write, only if images exist -->
  </div>
  <div class="tab-panel" data-tab="esempi"           data-anim="tab-panel" hidden>…</div>
  <div class="tab-panel" data-tab="approfondimenti"  data-anim="tab-panel" hidden>…</div>
  <div class="interactive-widget" data-widget="<widget-name>" data-anim="card">…</div>
  <div class="self-test" data-anim="card">…quiz…</div>
</section>
```

### Default Motion Baseline (MANDATORY)

Wire Framer Motion in a single `<script type="module">` at bottom of `<body>`:

```js
import { animate, inView, stagger } from "https://esm.sh/motion@latest";
const meta = document.querySelector('meta[name="student102-tokens"]');
const tokens = meta ? JSON.parse(atob(meta.content)) : {};
const spring = tokens.motion?.spring ?? { stiffness: 120, damping: 18 };

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
if (!reducedMotion) {
  inView("[data-anim='lesson']", ({ target }) => {
    animate(target, { opacity: [0, 1], y: [16, 0] }, { duration: 0.4, delay: stagger(0.06) });
  }, { once: true });
}
```

| Element | Default Framer behavior |
|---|---|
| Lesson `<section data-lesson>` | Fade + 16px Y-rise on viewport enter, staggered children 60ms |
| Tab panel switch | Cross-fade + 8px Y, `mode: "wait"` |
| Cards / quiz options | Stagger fade + 8px Y |
| Accordions | Height auto-animate + spring |
| Modals | Scale 0.96→1 + backdrop fade |
| Buttons | `whileHover` + `whileTap` micro-interaction |
| Sticky selector active | `layoutId` indicator |
| Self-test reveal | Height auto-animate + spring checkmark |

**`prefers-reduced-motion`:** early-return to instant transitions — hard requirement.

---

## Step 6 — Generate NanoBanana images (runs AFTER HTML write)

### Auth priority

| Env var | Source | Cost |
|---|---|---|
| `PUTER_AUTH_TOKEN` | puter.com → Dev Tools → Application → localStorage → `puter_auth_token` | Free |
| `PUTER_USERNAME` + `PUTER_PASSWORD` | puter.com login credentials (auto-login) | Free |
| `GOOGLE_API_KEY` / `GEMINI_API_KEY` | Google AI Studio | Requires billing for image models |

Tokens are read from `~/.claude/student102.config.json` (installed by the plugin installer). Environment variables override the config file.

If none set → skip NanoBanana silently, log, continue.

### Execution

Write config to `<assets_dir>/image_config.json`, then:

```bash
python ~/.claude/skills/student102/image_pipeline.py "<assets_dir>/image_config.json" "<assets_dir>/images"
```

Parse stdout JSON manifest. Save to context for Step 8.

---

## Step 7 — Download internet images via DuckDuckGo (runs AFTER Step 6)

The `image_pipeline.py` script handles DDG download using `search_queries` from Step 1.

**Prerequisites check:**
```bash
python -c "from duckduckgo_search import DDGS; print('ok')" 2>/dev/null || echo "MISSING"
```

Max 2 internet images per lesson. Skip < 1 KB files (broken). 0.3s delay between downloads.

---

## Step 8 — Integrate images into HTML (runs AFTER Step 7)

Insert image gallery block just before the `<div class="interactive-widget">` in the `[data-tab="teoria"]` tab panel.

```html
<div class="s102-image-gallery" data-lesson-images="N">
  <figure class="s102-figure s102-figure--generated">
    <img src="../<htmlname>_assets/images/lesson_N/generated_01.png"
         alt="<descriptive alt from manifest>" loading="lazy" class="s102-lesson-img">
    <figcaption>AI-generated illustration — <LESSON_NAME></figcaption>
  </figure>
</div>
```

**Only insert images that physically exist on disk.** Never insert broken `<img>` tags.

### Image presentation rules (HARD)

Bad reference: images so small inside a 2-column grid that text inside them is unreadable. This is forbidden.

- **Sizing target:** each image figure should occupy a meaningful portion of the reading column. On desktop (≥1024px viewport), the gallery row height target is **360–520px**, and a single figure's image area should be **at least 320px tall** and **at least 480px wide**. Never below 280px in either dimension.
- **Don't go absurdly large either:** cap a single figure at **70vh** tall and **min(900px, 90%)** of the column width. Images must never push the next section below the fold by themselves.
- **Layout:** prefer a single-column figure-per-row layout when the image contains *legible content* (diagrams with labels, screenshots of text, equations). Use a 2-up grid only for purely decorative / iconographic images where small size is fine.
- **`object-fit: contain`** for content-bearing images (diagrams, screenshots) — never `cover`, which crops labels.
- **Backgrounds:** if the image has a transparent or off-palette background, give the `<figure>` a neutral panel (e.g. `background: var(--surface-2); padding: 16px; border-radius: var(--radius-md);`) so it sits cleanly inside the dark/light theme.
- **Captions:** italic muted-ink, max 2 lines, never overlap the image.
- **Mobile (< 640px):** always single-column, image fills the column width, height auto.
- **Verify:** after Step 8, check that every emitted `<img>` has explicit width/height or aspect-ratio CSS so the layout doesn't jump and images don't render at 50×50 fallback size.

Reference CSS to inline (adapt token names to the current blob):

```css
.s102-image-gallery { display: grid; grid-template-columns: 1fr; gap: 24px; margin: 32px 0; }
@media (min-width: 1024px) {
  .s102-image-gallery:has(> :nth-child(2):last-child) { grid-template-columns: 1fr 1fr; }
}
.s102-figure {
  background: var(--surface-2, #11141f);
  border: 1px solid var(--border, rgba(255,255,255,.06));
  border-radius: var(--radius-lg, 16px);
  padding: 16px;
  display: flex; flex-direction: column; gap: 12px;
}
.s102-lesson-img {
  width: 100%;
  height: auto;
  max-height: 70vh;
  min-height: 320px;
  object-fit: contain;
  border-radius: var(--radius-md, 8px);
  display: block;
}
.s102-figure figcaption { font-style: italic; color: var(--ink-muted); font-size: 0.95rem; line-height: 1.4; }
```

---

## Code & format-sensitive content rules (HARD)

Bad reference: a Python class definition flattened onto a single wrapped line, no indentation, no highlighting. This is forbidden.

When emitting code, JSON, YAML, math, tables, ASCII trees, or any content whose meaning depends on whitespace and structure:

1. **Preserve newlines and indentation literally.** Inside `<pre><code>` you MUST keep real `\n` line breaks and the original leading spaces (4 for Python, 2 for JS/TS unless source uses 4). Never collapse a multi-line snippet into one line. Never replace tabs/spaces with a single space.
2. **HTML-escape, never reformat.** Escape `<`, `>`, `&`, `"`. Do NOT auto-format/prettify/minify the source — emit exactly what the lesson source contains.
3. **Always use `<pre><code class="language-XYZ">`** with a correct language token (`language-python`, `language-js`, `language-bash`, `language-json`, `language-css`, `language-html`, `language-yaml`, `language-sql`, etc.). Never put code inside a plain `<div>` or `<p>`.
4. **Wire syntax highlighting.** Include highlight.js (or Prism) from CDN in `<head>` and call it once on `DOMContentLoaded`:

   ```html
   <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/atom-one-dark.min.css">
   <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
   <script>document.addEventListener('DOMContentLoaded', () => hljs.highlightAll());</script>
   ```

   In light mode swap to `atom-one-light.min.css` via the theme toggle.
5. **Required `<pre>` CSS** (inline in the page):

   ```css
   pre { 
     white-space: pre;           /* NOT pre-wrap for code — preserves real layout */
     overflow-x: auto;           /* horizontal scroll for long lines, never wrap */
     tab-size: 4;
     font-family: var(--font-mono, "JetBrains Mono", ui-monospace, monospace);
     font-size: 0.92rem;
     line-height: 1.55;
     padding: 18px 20px;
     border-radius: var(--radius-md, 8px);
     background: var(--code-bg, #0b0d14);
     border: 1px solid var(--border, rgba(255,255,255,.06));
   }
   pre code { display: block; white-space: inherit; tab-size: inherit; }
   :not(pre) > code { 
     font-family: var(--font-mono); padding: 2px 6px; border-radius: 4px;
     background: var(--surface-2); font-size: 0.9em;
   }
   ```

   **Crucial:** use `white-space: pre` (NOT `pre-wrap`) inside `<pre>`. `pre-wrap` is what produced the broken one-line collapse seen in the bad reference when paired with HTML-source whitespace normalization.
6. **Source the snippet from the actual file.** When the source comes from a `.ipynb` cell or `.py` file, copy the cell/block bytes literally — do not paraphrase, do not "tidy up" the imports, do not strip comments. If the snippet is too long for the panel, show a meaningful contiguous excerpt with `# ...` ellipsis on its own line — never by joining lines.
7. **Inside JS template literals or HTML strings:** when generating the HTML, build code blocks with a list of lines joined by `\n`, or use a `<template>` element / `textContent` assignment, so the indentation is not eaten by a minifier or by editor-side formatting. Verify the rendered DOM has multi-line text nodes.
8. **Tables, JSON, YAML, math:** same rule — preserve structure. JSON inside `<pre><code class="language-json">` with real indentation; math via KaTeX (`$...$` / `$$...$$`) with the KaTeX auto-render script wired up; tables as semantic `<table>`, never as ASCII inside paragraphs.
9. **Verification before finishing:** scan the emitted HTML for `<pre><code` blocks. For each, confirm there is at least one `\n` in the inner text, that the first non-empty line's leading whitespace matches the source, and that the `class="language-..."` token is present. If any check fails, regenerate that block.

---

## Visual quality rules (HARD)

student102 outputs must look like a hand-crafted course site, not a generic template. Every lesson must satisfy:

- **Typography hierarchy:** distinct sizes/weights/tracking for h1/h2/h3/body/caption/code. Body line-height ≥ 1.6. Reading column max-width 68–76ch.
- **Spacing rhythm:** consistent 8px-grid spacing. Generous breathing room around section headers, between figures, around code blocks. No cramped walls of text.
- **Palette discipline:** use the token blob's 4 colors plus 2 surface shades; no ad-hoc hex values inside components. WCAG AA contrast in both themes — verify, don't assume.
- **Hierarchy of emphasis:** at most one accent-colored element per visible region. Callouts (notes, warnings, definitions) get their own styled card, not raw `<blockquote>`.
- **Micro-detail:** subtle borders, soft shadows on elevated surfaces, focused hover/active states on every interactive control, smooth tab indicator, polished scrollbars in dark mode.
- **Above-the-fold of every lesson** must be visually striking — a clear title block, a brief lede, and a hint of the lesson's hero visual or motif primitive.
- **No template-y giveaways:** no purple-blue gradient hero, no three identical feature cards, no Inter, no emoji bullets, no unstyled `<hr>`, no `<details>` without custom marker styling.
- **Self-review checklist before finishing** (run mentally):
  1. Are all images loading at the target size?
  2. Are all code blocks multi-line and highlighted?
  3. Do all tabs switch and all widgets respond?
  4. Is contrast OK in both themes?
  5. Is the layout balanced — no orphaned headers, no giant gaps, no horizontal scroll except inside `<pre>`?
  6. Does the page feel intentional, not assembled?

---

## Hard rules

1. **One lesson per call.** This is the defining constraint of student102.
2. **Lesson name = folder name.** Never override.
3. **At least one real interactive widget per lesson.** Static charts are not widgets.
4. **Bespoke Framer Motion animation per lesson.** Decorative fades alone = failed build.
5. **Never use `HTML_Expert` for files > 1000 lines.** Use targeted `Edit` inline.
6. **Never invent source content.** Approfondimenti = synthesis, not source claims.
7. **One file out.** Assets in `<htmlname>_assets/`.
8. **Anti-slop:** no Inter, no Roboto, no purple-on-white gradients, no emojis in markup, no three-card heroes.
9. **`prefers-reduced-motion` must be honored.**
10. **Subject-adaptive style mandatory.**
11. **Text contrast mandatory.** WCAG AA in both dark and light mode.
12. **Every button must do something real.**
13. **Images inserted AFTER HTML write** (Steps 6–8 are post-processing). No blocking.
14. **Only insert images that physically exist on disk.**
15. **NanoBanana prompts from `design-taste-frontend` style direction only.**
16. **Reuse existing token blob in append mode.** Never reinvent motif/palette.
17. **Everything must work and be visible as it should.** Verify before declaring done — see Hard Rule 4 above.
18. **Images must be readable at the right size.** See *Image presentation rules*. Min 320px tall, max 70vh, `object-fit: contain`, single column for content-bearing images.
19. **Format-sensitive content keeps its format.** See *Code & format-sensitive content rules*. `<pre><code class="language-...">`, `white-space: pre`, real newlines, real indentation, syntax highlighting wired up.
20. **Eye-pleasing is part of done.** See *Visual quality rules*. The output must look polished, not assembled.

---

## Output contract

```html
<!-- student102 lesson marker — do not remove -->
<section data-lesson="N" data-domain="stem|humanities" data-source-hash="..." data-motif="..." data-lesson-title="LESSON_NAME">
```

If a lesson with the same `data-lesson-title` already exists → warn user and ask before overwriting.

---

## Final report (every run)

1. Output path and mode (created / appended).
2. Lesson added: `Lesson N — LESSON_NAME` (domain).
3. Subject motif and primitives.
4. Interactive widget(s) implemented.
5. Degraded widgets and why.
6. Token blob summary. [Create mode only — append mode: "reused existing tokens".]
7. Image pipeline summary (NanoBanana + internet images count).
8. Next suggested command:
   ```
   /student102 "<next_lesson_dir>" "<output.html>"
   ```
