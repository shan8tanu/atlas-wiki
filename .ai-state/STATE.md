# Atlas Project — Living State File

> **FOR AI AGENTS (Claude, Codex, Gemini, Copilot, and others)**
> This file is the shared memory of the Atlas project. It is updated after every development session.

---

## Instructions for AI Agents

**READ this file at the start of every session.** It tells you what exists, what changed, and how everything connects — so you don't need to scan the entire codebase.

**UPDATE this file at the end of every session.** Follow these rules exactly:

### Rules

1. **NEVER delete or rewrite existing content.** Only append or update specific fields.
2. **Folder Structure** — If you added or removed files/folders, update the tree below. Add entries; don't remove entries you didn't delete.
3. **Feature Registry** — If you added or modified a feature, add or update its entry. Don't touch features you didn't change.
4. **Session Log** — ALWAYS append a new entry at the bottom. This is append-only. Never edit previous entries.
5. **Keep it concise.** This file should be scannable in 30 seconds. Link to source files instead of explaining implementation details.

### Format for Session Log Entries

```
### Session: YYYY-MM-DD — [Agent Name]
**Branch:** branch-name
**What changed:**
- Bullet points of what was added/modified/removed
**Files touched:**
- path/to/file — what changed
```

---

## Project Summary

Atlas is a **static visa requirements database for Indian passport holders**, built on MkDocs + Material theme. Visa data lives in YAML files (`data/visas/*.yaml`), rendered through a Jinja2 template (`templates/country.md.jinja`) by a build-time Python script (`gen_pages.py`). The site deploys to Cloudflare Pages at https://atlas-wiki.pages.dev/.

**Core principle:** "Content is Downstream of Data." Never edit generated Markdown — edit YAML data or the Jinja2 template.

---

## Folder Structure

```
atlas/
├── .ai-state/                    # THIS FOLDER — shared AI agent state (git-tracked)
│   └── STATE.md                  # This file
├── .claude/                      # Claude Code IDE configuration
│   └── launch.json               # Dev server: mkdocs serve on port 8000
├── .github/
│   ├── CODEOWNERS                # @shan8tanu approval gate for data/visas/
│   ├── PULL_REQUEST_TEMPLATE/    # PR templates (core_feature.md, data_correction.md)
│   └── workflows/
│       ├── ci.yml                # PR validation: validate.py → mkdocs build --strict → htmlproofer
│       └── link-check.yml        # Weekly link health check (Mondays 6 AM UTC)
├── data/
│   └── visas/                    # SOURCE OF TRUTH — 26 country YAML files
│       ├── australia.yaml
│       ├── brazil.yaml
│       ├── cambodia.yaml
│       ├── china.yaml
│       ├── france.yaml
│       ├── germany.yaml
│       ├── greece.yaml
│       ├── indonesia.yaml
│       ├── italy.yaml
│       ├── japan.yaml
│       ├── laos.yaml
│       ├── malaysia.yaml
│       ├── netherlands.yaml
│       ├── new-zealand.yaml
│       ├── philippines.yaml
│       ├── qatar.yaml
│       ├── saudi-arabia.yaml
│       ├── singapore.yaml
│       ├── south-korea.yaml
│       ├── spain.yaml
│       ├── switzerland.yaml
│       ├── thailand.yaml
│       ├── turkey.yaml
│       ├── uae.yaml
│       ├── united-states.yaml
│       └── vietnam.yaml
├── docs/                         # Hand-written pages + static assets
│   ├── index.md                  # Homepage
│   ├── map.md                    # Interactive world map page
│   ├── CONTRIBUTING.md           # Contributor guide
│   ├── robots.txt                # SEO
│   ├── _headers                  # HTTP headers
│   ├── map-data.json             # Auto-generated at build time (consumed by map.js)
│   ├── assets/
│   │   ├── images/favicon.svg
│   │   └── world-map.svg         # 179-country SVG, path IDs = ISO alpha-2 codes
│   ├── javascripts/
│   │   ├── map.js                # SVG coloring, tooltips, click-to-navigate
│   │   └── theme.js              # Checklist persistence, occupation/visa-type selectors,
│   │                             #   cover letter copy, mini-map, scroll animations
│   └── stylesheets/
│       ├── map.css               # Map hover effects, tooltips, legend, dark mode
│       └── theme.css             # Design system: color tokens, typography, cards,
│                                 #   selectors, checklist, responsive breakpoints
├── docs-internal/                # Deep documentation for the human (gitignored)
├── overrides/
│   └── main.html                 # Material theme override: hero section, mini-map widget
├── templates/
│   └── country.md.jinja          # THE template for all 26 country pages
├── validate/                     # Validation module
│   ├── __init__.py
│   ├── checks.py                 # Validation checks A–F
│   ├── schema.py                 # Allowed values, ISO codes, placeholder definitions
│   ├── report.py                 # Colored terminal output
│   └── claude_audit.py           # Web search + Claude accuracy comparison
├── site/                         # Build output (gitignored, auto-generated)
├── .ai_context.md                # Legacy project philosophy doc
├── .gitignore
├── CLAUDE.md                     # Claude Code instructions (points here)
├── FEATURES.md                   # Legacy feature tracking doc
├── mkdocs.yml                    # MkDocs config: theme, nav, plugins, CSS/JS
├── requirements.txt              # Python deps: mkdocs-material, jinja2, pyyaml, anthropic
├── gen_pages.py                  # Build engine: YAML → Jinja2 → virtual Markdown + map-data.json
├── validate.py                   # CLI: structural YAML validation
├── validate_accuracy.py          # CLI: AI-powered accuracy audit (needs ANTHROPIC_API_KEY)
├── admin_update.py               # CLI: trusted-source YAML updates with diff + confirmation
├── add_visa_types.py             # One-shot: bulk-added visa_types to all YAMLs
└── add_occupation_docs.py        # One-shot: bulk-added occupation_documents to all YAMLs
```

---

## Tech Stack

| Layer | Tool | Version/Notes |
|-------|------|---------------|
| Site Generator | MkDocs | Python-based |
| Theme | Material for MkDocs | Custom overrides in `overrides/` |
| Templating | Jinja2 | Build-time only |
| Data | YAML (PyYAML) | 26 country files in `data/visas/` |
| Build Plugin | mkdocs-gen-files | Virtual page generation |
| Frontend JS | Vanilla JavaScript | Zero external libraries |
| Frontend CSS | Custom CSS | Light/dark mode, responsive |
| AI Validation | Anthropic Claude API | Used by validate_accuracy.py and admin_update.py |
| Web Search | Brave Search API | Optional, used by accuracy validator |
| CI/CD | GitHub Actions | 2 workflows: ci.yml, link-check.yml |
| Hosting | Cloudflare Pages | Static site at atlas-wiki.pages.dev |

---

## Feature Registry

| # | Feature | Status | Key Files | Added |
|---|---------|--------|-----------|-------|
| 1 | Data-driven country pages (26 countries) | Active | `gen_pages.py`, `templates/country.md.jinja`, `data/visas/*.yaml` | Feb 2026 |
| 2 | Interactive SVG world map | Active | `docs/map.md`, `docs/assets/world-map.svg`, `docs/javascripts/map.js`, `docs/stylesheets/map.css` | Feb 2026 |
| 3 | Map data auto-generation (map-data.json) | Active | `gen_pages.py` (bottom section) | Feb 2026 |
| 4 | Document checklist with localStorage | Active | `templates/country.md.jinja`, `docs/javascripts/theme.js` | Feb 2026 |
| 5 | Occupation-type selector (6 categories) | Active | `templates/country.md.jinja`, `docs/javascripts/theme.js`, `data/visas/*.yaml` (occupation_documents) | Mar 2026 |
| 6 | Visa-type tabs (standard/e-visa/long-stay) | Active | `templates/country.md.jinja`, `docs/javascripts/theme.js`, `data/visas/*.yaml` (visa_types) | Mar 2026 |
| 7 | Cover letter template with copy button | Active | `templates/country.md.jinja`, `docs/javascripts/theme.js` | Mar 2026 |
| 8 | Schema.org JSON-LD SEO metadata | Active | `templates/country.md.jinja` (top) | Feb 2026 |
| 9 | Custom Material theme (light/dark mode) | Active | `docs/stylesheets/theme.css`, `overrides/main.html` | Feb 2026 |
| 10 | Homepage mini-map widget | Active | `overrides/main.html`, `docs/javascripts/theme.js` | Feb 2026 |
| 11 | CI/CD: PR validation pipeline | Active | `.github/workflows/ci.yml` | Feb 2026 |
| 12 | CI/CD: Weekly link health check | Active | `.github/workflows/link-check.yml` | Feb 2026 |
| 13 | Structural YAML validation (checks A–F) | Active | `validate.py`, `validate/checks.py`, `validate/schema.py` | Mar 2026 |
| 14 | AI accuracy audit (Claude + Brave) | Active | `validate_accuracy.py`, `validate/claude_audit.py` | Mar 2026 |
| 15 | Admin update tool (trusted-source updates) | Active | `admin_update.py` | Mar 2026 |
| 16 | Community edit routing (YAML, not MD) | Active | `gen_pages.py` (set_edit_path), `.github/CODEOWNERS` | Feb 2026 |
| 17 | Flag emoji generation from ISO codes | Active | `gen_pages.py` (iso_to_flag), flagcdn.com in template | Feb 2026 |
| 18 | Scroll-triggered reveal animations | Active | `docs/javascripts/theme.js` (IntersectionObserver) | Feb 2026 |

---

## Countries Covered (26)

**Asia (11):** Cambodia, China, Indonesia, Japan, Laos, Malaysia, Philippines, Singapore, South Korea, Thailand, Vietnam
**Oceania (2):** Australia, New Zealand
**Europe (7):** France, Germany, Greece, Italy, Netherlands, Spain, Switzerland, Turkey
**Middle East (3):** Qatar, Saudi Arabia, UAE
**Americas (2):** Brazil, United States

---

## Session Log

### Session: 2026-03-15 — Claude (Opus 4.6)
**Branch:** feat/country-pages-v2
**What changed:**
- Created `.ai-state/STATE.md` — this living state file for cross-agent context sharing
- Created `docs-internal/` folder with Part 1 documentation (Architecture & Data Flow)
- Created `docs-internal/README.md` — index for all 5 documentation parts
- Created `CLAUDE.md` — points Claude agents to `.ai-state/STATE.md`
- Updated `.gitignore` — added `docs-internal/` exclusion
**Files touched:**
- `.ai-state/STATE.md` — created (this file)
- `docs-internal/README.md` — created
- `docs-internal/01-architecture-and-data-flow.md` — created
- `CLAUDE.md` — created
- `.gitignore` — added docs-internal/ entry
