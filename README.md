# student102 — Claude Code Skill

> **One interactive lesson per call.** Add polished, exam-ready lessons to an HTML study guide from any folder of learning materials.

---

## Install

```sh
npx github:Salazar394/student102
```

That single command:
1. Copies the `/student102` skill into your `~/.claude/skills/` directory
2. Clones and installs the [`design-taste-frontend`](https://github.com/Salazar394/design-taste-frontend) skill from GitHub (required dependency for layout and visual style)
3. Installs Python dependencies: `duckduckgo_search`, `requests`
4. Creates `~/.claude/student102.config.json` for your API tokens
5. Registers the skill in your `~/.claude/CLAUDE.md`

Then **restart Claude Code** to activate the skill.

---

## Usage

Inside Claude Code:

```
/student102 "path/to/lesson-folder"
```
Creates a new HTML file named after the folder, with one interactive lesson.

```
/student102 "path/to/lesson-folder" "path/to/existing-guide.html"
```
Appends one new lesson to an existing study guide, reusing its visual style.

### Hard rules

| Rule | Details |
|---|---|
| One lesson per call | Each invocation adds exactly one lesson |
| Lesson name = folder name | If the folder is `Backpropagation`, the lesson title is `Backpropagation` |
| Interactive widget required | Every lesson must have at least one real interactive element (slider, step-through, 3D plot…) |

---

## What it generates

- **Teoria tab** — structured theory from your source materials (PDFs, notebooks, markdown)
- **Esempi tab** — worked examples and code snippets
- **Approfondimenti tab** — cross-topic connections, exam-likely questions, pitfalls
- **Interactive widget** — chosen by domain (STEM: Chart.js/Plotly/Three.js sliders; Humanities: timelines/concept graphs)
- **Self-test quiz** — multiple-choice with reveal
- **AI illustration** — generated via NanoBanana (Puter or Google Gemini)
- **Reference images** — downloaded from DuckDuckGo image search
- **Framer Motion animations** — concept-specific, not just decorative fades
- **Dark/light toggle** — persisted in localStorage
- **WCAG AA contrast** — verified in both modes

---

## API tokens (optional)

Edit `~/.claude/student102.config.json` after installation:

```json
{
  "PUTER_AUTH_TOKEN": "your-token-here",
  "GOOGLE_API_KEY": ""
}
```

| Token | Source | Cost | Purpose |
|---|---|---|---|
| `PUTER_AUTH_TOKEN` | [puter.com](https://puter.com) → Dev Tools → Application → localStorage → `puter_auth_token` | **Free** | AI image generation (preferred) |
| `PUTER_USERNAME` + `PUTER_PASSWORD` | Your puter.com credentials | **Free** | Auto-login fallback if token expires |
| `GOOGLE_API_KEY` | [aistudio.google.com](https://aistudio.google.com) | Requires billing | Gemini image generation (alternative) |

If no token is set → NanoBanana is skipped silently. DuckDuckGo images still work without any token.

---

## Supported source file types

| Type | How it's read |
|---|---|
| `.pdf` | First 10 pages |
| `.ipynb` | All cells (code + markdown) |
| `.md`, `.txt` | Fully |
| Images (`.png`, `.jpg`, `.svg`) | Paths collected for gallery |
| Code files | Treated as snippet source |

---

## Required dependencies (auto-installed)

- **Claude Code** — [claude.ai/code](https://claude.ai/code)
- **Node.js ≥ 18** — for the installer
- **Python 3.8+** — for the image pipeline
- **`duckduckgo_search`** — `pip install duckduckgo_search` (auto-installed)
- **`requests`** — `pip install requests` (auto-installed)
- **`design-taste-frontend` Claude Code skill** — cloned automatically from GitHub at install time; provides the layout engine and visual style system used by every lesson

Optional:
- **Manim** — `pip install manim` — enables math animation rendering (degrades to Plotly if missing)

---

## Directory structure

```
student102/
├── bin/
│   └── install.js          # npx entry point — runs the installer
├── skill/
│   ├── SKILL.md            # Claude Code skill definition
│   └── image_pipeline.py   # NanoBanana + DuckDuckGo image pipeline
├── config.template.json    # Copied to ~/.claude/student102.config.json on install
├── package.json
└── README.md
```

---

## Example session

```
/student102 "C:\Courses\DeepLearning\Backpropagation"
```

Output:
```
✔ Backpropagation.html created
  Lesson 1 — Backpropagation (STEM)
  Motif: neural-circuit · Palette: dark graphite + electric blue
  Widget: Click-to-step backprop visualizer (Framer Motion)
  NanoBanana: 1 image generated
  Internet images: 2 downloaded
  Next: /student102 "C:\Courses\DeepLearning\Optimizers" "Backpropagation.html"
```

---

## License

MIT — use freely, fork, contribute.
