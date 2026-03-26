# Fragebogen Archicad Grundlagen

A **self-assessment questionnaire tool** for employees of the architecture firm **k2o Architekten**, designed to evaluate their knowledge of **Archicad fundamentals**.

---

## 🎯 Purpose

Employees rate their own proficiency on a wide range of Archicad topics. The results are collected in a **Google Sheet** for analysis.

---

## 🏗️ Architecture

The project has three main layers:

### 1. Content / Source (`source/`)

Questions are written as **Markdown files** (Obsidian-style) organized into thematic categories:

| Folder | Topic |
|---|---|
| `Interaktion/` | Navigation, Transparentpause, etc. |
| `Konfiguration/` | Settings & configuration |
| `Sichtweise/` | Views & perspectives |
| `Zeichen/` | Drawing tools |
| `Attribute/` | Attributes |
| `Variantenplanung/` | Variant planning |
| `Hotlink-Module/` | Hotlink modules |
| `externe Dateien/` | External files |

Each `.md` file has YAML frontmatter (`L0`, `L1`, `L3` = topic hierarchy levels) and a body with checklist items, some referencing embedded images (`![[image.png]]`).

### 2. Build Script (`scripts/build_form.py`)

A Python script that:
- Reads all `.md` question files
- Parses frontmatter and checklist items
- Copies images from `_links/` folders to `docs/images/`
- Injects questions + respondent list into `form_template.html`
- Outputs a **single self-contained HTML file** → `docs/index.html`

Run with:
```bash
python scripts/build_form.py
```

### 3. Backend (`backend/Code.js`)

A **Google Apps Script** web app that:
- Receives form submissions via HTTP POST from the HTML form
- Writes one row per answered item into a **Google Sheet**
- Columns: `Timestamp | Name | E-Mail | Submitted At | ID | Kategorie | L1 | L3 | Thema | Bewertung`

---

## 👥 Respondents

19 employees from k2o Architekten are listed in `config.yaml` and `Mitarbeiter.txt`. The HTML form shows a **login dropdown** where the user selects their name before filling out the questionnaire.

---

## 🌐 Deployment

- The form (`docs/index.html`) is hosted on **GitHub Pages**
- The backend runs as a **Google Apps Script Web App**
- The Web App URL is configured in `config.yaml` and injected into the HTML at build time

---

## 🔄 Workflow

```
Edit .md files → run build_form.py → push docs/index.html to GitHub Pages
                                              ↓
                                Employee opens form, selects name,
                                rates each Archicad topic
                                              ↓
                                Submits → Google Apps Script → Google Sheet
```

---

## 📁 Project Structure

```
├── config.yaml              # Form config, respondents, backend URL
├── Mitarbeiter.txt          # Employee list (salutation, name, email)
├── README.md
├── backend/
│   ├── appsscript.json      # Apps Script manifest
│   └── Code.js              # Google Apps Script web app
├── docs/
│   ├── index.html           # Generated form (output)
│   └── images/              # Copied question images (output)
├── scripts/
│   ├── build_form.py        # Build script
│   └── form_template.html   # HTML template
└── source/                  # Question content (Markdown)
    ├── Interaktion/
    ├── Konfiguration/
    ├── Sichtweise/
    ├── Zeichen/
    ├── Attribute/
    ├── Variantenplanung/
    ├── Hotlink-Module/
    └── externe Dateien/
```
