# Copilot Instructions — Fragebogen Archicad Grundlagen

## Project Overview

A **static self-assessment questionnaire** for k2o Architekten employees to rate their Archicad knowledge. Questions are authored in Markdown (Obsidian-style), compiled into a single HTML file by a Python build script, and hosted on GitHub Pages. Submissions are written to a Google Sheet via a Google Apps Script web app.

## Build & Run

```bash
# From project root — the only build command
python scripts/build_form.py
```

**Requirements:**
- Python **≥ 3.10** (uses `dict | None` union syntax)
- `PyYAML` — install once: `pip install pyyaml`
- No other third-party dependencies

**Output:** `docs/index.html` + images copied to `docs/images/`

**Deploy:** Commit and push `docs/` → GitHub Pages serves the form automatically.

## Architecture

```
source/**/*.md  ──build_form.py──►  docs/index.html  ──GitHub Pages──►  Browser
                                                                              │
                                                                         HTTP POST
                                                                              │
                                                               backend/Code.js (Google Apps Script)
                                                                              │
                                                                        Google Sheet
```

| Layer | Path | Role |
|---|---|---|
| Content | `source/` | Markdown question files (Obsidian vault) |
| Build | `scripts/build_form.py` | Parses MD → injects JSON into HTML template |
| Template | `scripts/form_template.html` | Vanilla-JS SPA; no external dependencies |
| Output | `docs/index.html` | Self-contained form (questions + respondents baked in) |
| Backend | `backend/Code.js` | Google Apps Script; writes one row per item to Sheet |
| Config | `config.yaml` | Single source of truth for title, backend URL, respondents |

## Question File Format (`source/**/*.md`)

```yaml
---
L0: Grundlagen        # Always "Grundlagen" — constant top-level category
L1: Interaktion       # Maps to folder name; becomes the card group header
L3: Navigation        # Sub-topic / section title (L2 is intentionally absent)
Bilder: true          # Optional; currently unused by build script
---

# Section Heading     ← visual divider inside the card

- Checklist item text
- Item with image ![[Pasted image 20260324121009.png]]
- Item with sized image ![[Pasted image 20260324121016.png|]]
```

**File naming:** Numeric prefix controls display order (`021.md`, `031.md`, `032.md`…). The hundreds digit encodes the category (03x = Interaktion, 04x = Konfiguration, 05x = Attribute, 06x = Sichtweise, 07x = Variantenplanung, 08x = Hotlink-Module, 09x = externe Dateien).

## Images

- **Source:** `source/<Category>/_links/Pasted image YYYYMMDDHHMMSS.png` (Obsidian attachment convention)
- **Output:** `docs/images/<filename>.png` (copied by build script)
- **Reference in MD:** Obsidian wiki-link syntax `![[filename.png]]` or `![[filename.png|]]`
- ⚠️ Filenames contain spaces — works on GitHub Pages but avoid case-sensitive servers

## Respondents

Defined in **`config.yaml`** under `respondents:` (name + email). This is the authoritative source read by the build script.

`Mitarbeiter.txt` is a parallel reference list (salutation, name, email) — **not read by the build script**. Keep both files in sync manually when adding/removing employees.

## Backend (`backend/Code.js`)

- **`setupConfig()`** — run once manually in Apps Script editor to store `SHEET_ID`
- **`doGet()`** — health check endpoint
- **`doPost()`** — receives `payload=<JSON>`, writes one row per rated item

**Sheet columns:** `Timestamp | Name | E-Mail | Submitted At | ID | Kategorie | L1 | L3 | Thema | Bewertung`

**Rating scale:** `3` = Sicher · `2` = Grundkenntnisse · `1` = Unsicher · `0` = Unbekannt

The form uses `fetch()` with `mode: "no-cors"` — submission success cannot be confirmed from the browser. This is a known limitation of cross-origin requests to Google Apps Script.

## Key Conventions

- **Edit description** → modify `source/Beschreibung.md`, then rebuild; its text appears as a banner at the top of the form
- **Edit questions** → modify `.md` files in `source/`, then rebuild
- **Add respondents** → update `config.yaml` respondents list AND `Mitarbeiter.txt`, then rebuild
- **Change backend URL** → update `web_app_url` in `config.yaml`, then rebuild
- **Add images** → place in the relevant `source/<Category>/_links/` folder; reference with `![[filename.png]]`
- **Question order** → controlled by the numeric filename prefix; rename files to reorder

## Common Pitfalls

| Pitfall | Detail |
|---|---|
| Missing `pyyaml` | `pip install pyyaml` before first run |
| Python < 3.10 | `dict \| None` syntax will fail — upgrade Python |
| Bare `-` lines in MD | `parse_md()` skips items with no content — safe to leave |
| Dual respondent lists | `config.yaml` and `Mitarbeiter.txt` must be kept in sync manually |
| `script_id` empty | Managed by `clasp` CLI, not used by the build script — leave as-is |
| Images not committed | `docs/images/` must be pushed to GitHub alongside `index.html` |
