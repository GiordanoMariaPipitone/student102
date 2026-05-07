#!/usr/bin/env node
/**
 * student102 installer
 * Installs the /student102 Claude Code skill + all required dependencies.
 *
 * Run via:
 *   npx github:Salazar394/student102
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { execSync, spawnSync } = require("child_process");

// ─── Utilities ─────────────────────────────────────────────────────────────

const green  = (s) => `\x1b[32m${s}\x1b[0m`;
const yellow = (s) => `\x1b[33m${s}\x1b[0m`;
const red    = (s) => `\x1b[31m${s}\x1b[0m`;
const bold   = (s) => `\x1b[1m${s}\x1b[0m`;

function log(msg)  { console.log(`  ${msg}`); }
function ok(msg)   { console.log(`  ${green("✔")} ${msg}`); }
function warn(msg) { console.log(`  ${yellow("⚠")} ${msg}`); }
function fail(msg) { console.log(`  ${red("✖")} ${msg}`); }
function step(n, total, msg) { console.log(`\n${bold(`[${n}/${total}]`)} ${msg}`); }

// ─── Paths ──────────────────────────────────────────────────────────────────

const HOME = os.homedir();
const IS_WIN = process.platform === "win32";
const CLAUDE_DIR = path.join(HOME, ".claude");
const SKILLS_DIR = path.join(CLAUDE_DIR, "skills");
const SKILL_TARGET = path.join(SKILLS_DIR, "student102");
const SKILL_SRC = path.join(__dirname, "..", "skill");
const CONFIG_FILE = path.join(CLAUDE_DIR, "student102.config.json");
const CONFIG_TEMPLATE = path.join(__dirname, "..", "config.template.json");

// ─── Step helpers ───────────────────────────────────────────────────────────

function ensureDir(p) {
  if (!fs.existsSync(p)) fs.mkdirSync(p, { recursive: true });
}

function copyDir(src, dest) {
  ensureDir(dest);
  for (const entry of fs.readdirSync(src, { withFileTypes: true })) {
    const srcPath  = path.join(src, entry.name);
    const destPath = path.join(dest, entry.name);
    if (entry.isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

function runPip(args) {
  const pip = IS_WIN ? "pip" : "pip3";
  const result = spawnSync(pip, args, { encoding: "utf8", shell: IS_WIN });
  return result.status === 0;
}

function pipInstalled(pkg) {
  const python = IS_WIN ? "python" : "python3";
  const result = spawnSync(python, ["-c", `import ${pkg.replace(/-/g, "_")}`], {
    encoding: "utf8",
    shell: IS_WIN,
  });
  return result.status === 0;
}

// ─── Main ───────────────────────────────────────────────────────────────────

const TOTAL_STEPS = 6;

console.log(`\n${bold("student102")} — Claude Code skill installer\n`);
console.log(`  Installs /student102 (one interactive lesson per call) into your Claude Code.\n`);

// ── Step 1: Verify ~/.claude exists ─────────────────────────────────────────
step(1, TOTAL_STEPS, "Checking Claude Code installation…");
if (!fs.existsSync(CLAUDE_DIR)) {
  fail(`~/.claude not found at ${CLAUDE_DIR}`);
  fail("Please install Claude Code first: https://claude.ai/code");
  process.exit(1);
}
ok(`Found Claude Code at ${CLAUDE_DIR}`);

// ── Step 2: Copy skill files ─────────────────────────────────────────────────
step(2, TOTAL_STEPS, "Installing skill files…");
if (fs.existsSync(SKILL_TARGET)) {
  warn("student102 skill already exists — overwriting with latest version.");
}
copyDir(SKILL_SRC, SKILL_TARGET);
ok(`Skill files installed to ${SKILL_TARGET}`);

// ── Step 3: Install design-taste-frontend skill (dependency) ─────────────────
step(3, TOTAL_STEPS, "Installing required Claude Code skills…");
const dtfTarget = path.join(SKILLS_DIR, "design-taste-frontend");
const dtfSrc    = path.join(__dirname, "..", "skills", "design-taste-frontend");

if (!fs.existsSync(dtfTarget)) {
  if (fs.existsSync(dtfSrc)) {
    copyDir(dtfSrc, dtfTarget);
    ok("design-taste-frontend skill installed.");
  } else {
    warn("design-taste-frontend bundled copy not found — attempting git clone…");
    try {
      execSync(
        `git clone --depth 1 https://github.com/Salazar394/design-taste-frontend.git "${dtfTarget}"`,
        { stdio: "pipe" }
      );
      ok("design-taste-frontend cloned from GitHub.");
    } catch (_) {
      warn(
        "Could not install design-taste-frontend automatically.\n" +
        "    Run manually: git clone https://github.com/Salazar394/design-taste-frontend ~/.claude/skills/design-taste-frontend"
      );
    }
  }
} else {
  ok("design-taste-frontend already present — skipped.");
}

// ── Step 4: Install Python dependencies ──────────────────────────────────────
step(4, TOTAL_STEPS, "Checking Python dependencies…");

const pyDeps = [
  { import: "duckduckgo_search", pip: "duckduckgo_search", label: "DuckDuckGo image search" },
  { import: "requests",          pip: "requests",          label: "HTTP requests"            },
];

let pipOk = true;
for (const dep of pyDeps) {
  if (pipInstalled(dep.import)) {
    ok(`${dep.label} (${dep.pip}) — already installed`);
  } else {
    log(`Installing ${dep.label}…`);
    if (runPip(["install", dep.pip, "--quiet"])) {
      ok(`${dep.label} installed`);
    } else {
      warn(`Could not install ${dep.pip} — run manually: pip install ${dep.pip}`);
      pipOk = false;
    }
  }
}

if (!pipOk) {
  warn("Some Python packages failed. NanoBanana / DuckDuckGo image steps will be skipped at runtime.");
}

// ── Step 5: Create/update config file ────────────────────────────────────────
step(5, TOTAL_STEPS, "Setting up API token config…");

if (!fs.existsSync(CONFIG_FILE)) {
  fs.copyFileSync(CONFIG_TEMPLATE, CONFIG_FILE);
  ok(`Config created: ${CONFIG_FILE}`);
  log(`Open that file to add your API tokens (Puter + Google API key).`);
} else {
  ok(`Config already exists: ${CONFIG_FILE} — not overwritten.`);
  log(`To reset it, delete and re-run this installer.`);
}

// ── Step 6: Register skill in CLAUDE.md (global) ─────────────────────────────
step(6, TOTAL_STEPS, "Registering skill in global CLAUDE.md…");

const claudeMd = path.join(CLAUDE_DIR, "CLAUDE.md");
const skillEntry = `\n## student102 skill\n- **Invocation:** \`/student102 <directory> [existing_html_path]\`\n- **Purpose:** Adds exactly one lesson (named after the folder) to an HTML study guide.\n- **Location:** \`~/.claude/skills/student102/SKILL.md\`\n`;
const marker = "## student102 skill";

if (fs.existsSync(claudeMd)) {
  const content = fs.readFileSync(claudeMd, "utf8");
  if (!content.includes(marker)) {
    fs.appendFileSync(claudeMd, skillEntry, "utf8");
    ok("student102 registered in ~/.claude/CLAUDE.md");
  } else {
    ok("student102 already registered in CLAUDE.md — skipped.");
  }
} else {
  fs.writeFileSync(claudeMd, skillEntry, "utf8");
  ok("Created ~/.claude/CLAUDE.md with student102 registration.");
}

// ── Done ─────────────────────────────────────────────────────────────────────
console.log(`\n${green(bold("Installation complete!"))}\n`);
console.log(`  ${bold("Usage inside Claude Code:")}`);
console.log(`    /student102 "path/to/lesson-folder"`);
console.log(`    /student102 "path/to/lesson-folder" "path/to/existing.html"\n`);
console.log(`  ${bold("API tokens (optional but recommended):")}`);
console.log(`    Edit: ${CONFIG_FILE}`);
console.log(`    ┌─ PUTER_AUTH_TOKEN   — free, from https://puter.com (Dev Tools → localStorage → puter_auth_token)`);
console.log(`    ├─ PUTER_USERNAME     — puter.com login email (auto-login fallback)`);
console.log(`    ├─ PUTER_PASSWORD     — puter.com password  (auto-login fallback)`);
console.log(`    └─ GOOGLE_API_KEY     — from https://aistudio.google.com (needs Gemini billing)\n`);
console.log(`  ${bold("Note:")} Restart your Claude Code session to activate the skill.\n`);
