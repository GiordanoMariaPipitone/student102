"""
student102 image pipeline — NanoBanana (Puter/Google) + DuckDuckGo download.

Usage:
  python image_pipeline.py <image_config.json> <output_dir>

image_config.json schema:
{
  "lesson_n": 1,
  "lesson_name": "Backpropagation",
  "nanobanana_prompt": "...",
  "search_queries": ["...", "..."],
  "style_hint": "dark, electric blue, circuit motif"
}

Reads API tokens from:
  1. Environment variables (highest priority)
  2. ~/.claude/student102.config.json (set by installer)

Outputs a JSON manifest to stdout:
{
  "generated": [{"path": "...", "alt": "..."}],
  "downloaded": [{"path": "...", "alt": "..."}]
}
"""

import sys
import os
import json
import time
import hashlib
import pathlib
import urllib.request
import urllib.error

# ── Config loading ────────────────────────────────────────────────────────────

def load_config():
    cfg_path = pathlib.Path.home() / ".claude" / "student102.config.json"
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}

def get_token(key, cfg):
    return os.environ.get(key) or cfg.get(key, "")

# ── NanoBanana (Puter AI image) ───────────────────────────────────────────────

def nanobanana_generate(prompt: str, output_path: str, cfg: dict) -> bool:
    """
    Generate an image via Puter's AI API (NanoBanana).
    Falls back gracefully if no credentials are available.
    """
    puter_token    = get_token("PUTER_AUTH_TOKEN", cfg)
    puter_user     = get_token("PUTER_USERNAME", cfg)
    puter_pass     = get_token("PUTER_PASSWORD", cfg)
    google_api_key = get_token("GOOGLE_API_KEY", cfg) or get_token("GEMINI_API_KEY", cfg)

    # Try Puter token auth
    if puter_token:
        return _puter_generate(prompt, output_path, puter_token)

    # Try Puter username+password auto-login
    if puter_user and puter_pass:
        token = _puter_login(puter_user, puter_pass)
        if token:
            return _puter_generate(prompt, output_path, token)

    # Try Google Imagen via Gemini
    if google_api_key:
        return _google_generate(prompt, output_path, google_api_key)

    print("[image_pipeline] No NanoBanana credentials — skipping generated image.", file=sys.stderr)
    return False


def _puter_login(username: str, password: str) -> str:
    """Auto-login to puter.com and return auth token."""
    import urllib.parse
    payload = json.dumps({"username": username, "password": password}).encode()
    req = urllib.request.Request(
        "https://api.puter.com/auth/login",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
            return data.get("token", "")
    except Exception as e:
        print(f"[image_pipeline] Puter login failed: {e}", file=sys.stderr)
        return ""


def _puter_generate(prompt: str, output_path: str, token: str) -> bool:
    """Call Puter's AI image generation endpoint."""
    req = urllib.request.Request(
        "https://api.puter.com/drivers/call",
        data=json.dumps({
            "interface": "puter-image-generation",
            "method": "generate",
            "args": {"prompt": prompt, "model": "dall-e-3", "size": "1024x1024"},
        }).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            image_url = (
                data.get("result", {}).get("url")
                or data.get("url")
                or (data.get("result", [{}])[0].get("url") if isinstance(data.get("result"), list) else None)
            )
            if not image_url:
                print(f"[image_pipeline] Puter: no image URL in response", file=sys.stderr)
                return False
            return _download_binary(image_url, output_path)
    except Exception as e:
        print(f"[image_pipeline] Puter image generation failed: {e}", file=sys.stderr)
        return False


def _google_generate(prompt: str, output_path: str, api_key: str) -> bool:
    """Generate image via Google Gemini (requires billing)."""
    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]},
    }).encode()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-preview-image-generation:generateContent?key={api_key}"
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
            b64 = (
                data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("inlineData", {})
                .get("data", "")
            )
            if not b64:
                print("[image_pipeline] Google: no image data in response", file=sys.stderr)
                return False
            import base64
            pathlib.Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            pathlib.Path(output_path).write_bytes(base64.b64decode(b64))
            return True
    except Exception as e:
        print(f"[image_pipeline] Google image generation failed: {e}", file=sys.stderr)
        return False

# ── DuckDuckGo image download ─────────────────────────────────────────────────

def ddg_download(queries: list, output_dir: str, max_images: int = 2) -> list:
    """Download up to max_images from DuckDuckGo image search."""
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        print("[image_pipeline] duckduckgo_search not installed — skipping DDG.", file=sys.stderr)
        return []

    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    results = []
    count = 0

    for query in queries:
        if count >= max_images:
            break
        try:
            with DDGS() as ddgs:
                for img in ddgs.images(query, max_results=5):
                    if count >= max_images:
                        break
                    url = img.get("image", "")
                    if not url:
                        continue
                    h = hashlib.md5(url.encode()).hexdigest()[:8]
                    ext = url.split("?")[0].rsplit(".", 1)[-1][:4] or "jpg"
                    fname = f"web_{h}.{ext}"
                    fpath = os.path.join(output_dir, fname)
                    if _download_binary(url, fpath, min_bytes=1024):
                        results.append({"path": fpath, "alt": query})
                        count += 1
                    time.sleep(0.3)
        except Exception as e:
            print(f"[image_pipeline] DDG search failed for '{query}': {e}", file=sys.stderr)

    return results

# ── Binary download helper ────────────────────────────────────────────────────

def _download_binary(url: str, dest: str, min_bytes: int = 0) -> bool:
    try:
        pathlib.Path(dest).parent.mkdir(parents=True, exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        if len(data) < min_bytes:
            return False
        pathlib.Path(dest).write_bytes(data)
        return True
    except Exception as e:
        print(f"[image_pipeline] Download failed {url}: {e}", file=sys.stderr)
        return False

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 3:
        print("Usage: image_pipeline.py <image_config.json> <output_dir>", file=sys.stderr)
        sys.exit(1)

    config_path = sys.argv[1]
    output_dir  = sys.argv[2]

    with open(config_path, encoding="utf-8") as f:
        img_cfg = json.load(f)

    cfg = load_config()
    lesson_n    = img_cfg.get("lesson_n", 1)
    lesson_name = img_cfg.get("lesson_name", "Lesson")
    prompt      = img_cfg.get("nanobanana_prompt", f"Educational illustration for {lesson_name}, minimal, professional")
    queries     = img_cfg.get("search_queries", [lesson_name])
    style_hint  = img_cfg.get("style_hint", "")

    if style_hint:
        prompt = f"{prompt}, {style_hint}"

    lesson_img_dir = os.path.join(output_dir, f"lesson_{lesson_n}")
    pathlib.Path(lesson_img_dir).mkdir(parents=True, exist_ok=True)

    manifest = {"generated": [], "downloaded": []}

    # NanoBanana
    gen_path = os.path.join(lesson_img_dir, "generated_01.png")
    if nanobanana_generate(prompt, gen_path, cfg):
        manifest["generated"].append({
            "path": gen_path,
            "alt": f"AI-generated illustration for {lesson_name}",
        })

    # DuckDuckGo
    dl = ddg_download(queries, lesson_img_dir, max_images=2)
    manifest["downloaded"].extend(dl)

    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
