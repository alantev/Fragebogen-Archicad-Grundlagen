"""
build_form.py
-------------
Reads all question .md files from ../source/**/*.md,
parses them into a structured question list,
and generates ../docs/index.html — the self-contained form.

Images are referenced as:
  ./images/<filename>.png
(they must be copied to docs/images/ separately — see copy_images.py)

Run:
    python scripts/build_form.py
"""

import os
import re
import json
import yaml
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOURCE_DIR = ROOT / "source"
DOCS_DIR = ROOT / "docs"
IMAGES_OUT = DOCS_DIR / "images"
CONFIG_FILE = ROOT / "config.yaml"
TEMPLATE_FILE = ROOT / "scripts" / "form_template.html"
OUTPUT_FILE = DOCS_DIR / "index.html"

# ── helpers ──────────────────────────────────────────────────────────────────

OBSIDIAN_IMG_RE = re.compile(r'!\[\[([^\]|]+?)(?:\|[^\]]*)?\]\]')

def parse_md(path: Path) -> dict | None:
    """Parse a question .md file. Returns None if no content."""
    text = path.read_text(encoding="utf-8")

    # split frontmatter
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    fm = yaml.safe_load(parts[1]) or {}
    body = parts[2].strip()

    if not body:
        return None

    # collect items (lines starting with -)
    items = []
    current_section = None
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("#"):
            current_section = line.lstrip("#").strip()
        elif line.startswith("-"):
            content = line.lstrip("-").strip()
            if not content:
                continue
            images = OBSIDIAN_IMG_RE.findall(content)
            label = OBSIDIAN_IMG_RE.sub("", content).strip()
            if label or images:
                items.append({
                    "section": current_section,
                    "label": label,
                    "images": images,
                })

    if not items:
        return None

    return {
        "id": path.stem,                          # e.g. "031"
        "category": path.parent.name,             # e.g. "Interaktion"
        "L0": fm.get("L0", ""),
        "L1": fm.get("L1", ""),
        "L3": fm.get("L3", ""),
        "items": items,
    }


def collect_questions() -> list[dict]:
    questions = []
    for md_file in sorted(SOURCE_DIR.rglob("*.md"), key=lambda p: p.stem):
        q = parse_md(md_file)
        if q:
            questions.append(q)
    return questions


def load_config() -> dict:
    return yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))


def copy_images():
    """Copy all images from source/**/_links/ to docs/images/"""
    IMAGES_OUT.mkdir(parents=True, exist_ok=True)
    copied = 0
    for links_dir in SOURCE_DIR.rglob("_links"):
        if links_dir.is_dir():
            for img in links_dir.iterdir():
                if img.is_file():
                    dest = IMAGES_OUT / img.name
                    if not dest.exists():
                        shutil.copy2(img, dest)
                        copied += 1
    print(f"  Copied {copied} images to docs/images/")


# ── main ─────────────────────────────────────────────────────────────────────

def build():
    DOCS_DIR.mkdir(exist_ok=True)
    copy_images()

    questions = collect_questions()
    config = load_config()

    respondents = config.get("respondents", [])
    web_app_url = config.get("backend", {}).get("web_app_url", "")
    form_title = config.get("form", {}).get("title", "Fragebogen")

    template = TEMPLATE_FILE.read_text(encoding="utf-8")

    html = template.replace("__FORM_TITLE__", form_title)
    html = html.replace("__WEB_APP_URL__", web_app_url)
    html = html.replace("__QUESTIONS_JSON__", json.dumps(questions, ensure_ascii=False, indent=2))
    html = html.replace("__RESPONDENTS_JSON__", json.dumps(respondents, ensure_ascii=False, indent=2))

    OUTPUT_FILE.write_text(html, encoding="utf-8")
    print(f"  Generated {OUTPUT_FILE}")
    print(f"  {len(questions)} question groups, {sum(len(q['items']) for q in questions)} items")


if __name__ == "__main__":
    build()
