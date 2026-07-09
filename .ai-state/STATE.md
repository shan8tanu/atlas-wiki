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
│       ├── link-check.yml        # Weekly link health check (Mondays 6 AM UTC)
│       └── accuracy-audit.yml    # Weekly AI accuracy audit (Mondays 7 AM UTC)
│   # NOTE (2026-07-08): CODEOWNERS listed below does NOT exist in the repo — see session log
├── data/
│   ├── transit/                  # Transit guide data
│   │   └── transit_rules.yaml   # 6 airport hubs (FRA, CDG, LHR, DXB, SIN, IST)
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
│   ├── country.md.jinja          # THE template for all 26 country pages
│   └── transit-guide.md.jinja    # Template for Transit Rules Guide page
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
├── add_country.py                # CLI: AI new-country pipeline (research→draft→validate→PR)
├── add_visa_types.py             # One-shot: bulk-added visa_types to all YAMLs
├── add_occupation_docs.py        # One-shot: bulk-added occupation_documents to all YAMLs
└── atlas_PROJECT_STATE.md              # Current-state snapshot (regenerated 2026-07-08)
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
| 19 | Transit Rules Guide (cross-destination) | Active | `data/transit/transit_rules.yaml`, `templates/transit-guide.md.jinja`, `gen_pages.py` | Mar 2026 |
| 19 | Change Log (per-country audit trail) | Active (sample) | `data/visas/*.yaml` (changelog), `templates/country.md.jinja`, `docs/stylesheets/theme.css` | Mar 2026 |
| 20 | Visa Exemptions / Indian Privilege Check | Active (sample) | `data/visas/*.yaml` (exemptions), `templates/country.md.jinja`, `docs/stylesheets/theme.css` | Mar 2026 |
| 21 | Transit Rules | Active (sample) | `data/visas/*.yaml` (transit), `templates/country.md.jinja`, `docs/stylesheets/theme.css` | Mar 2026 |
| 22 | Jurisdiction Map (state → consulate) | Active (sample) | `data/visas/*.yaml` (jurisdiction), `templates/country.md.jinja`, `docs/stylesheets/theme.css` | Mar 2026 |
| 23 | ECR / Non-ECR Passport Rules | Active (sample) | `data/visas/*.yaml` (ecr), `templates/country.md.jinja`, `docs/stylesheets/theme.css` | Mar 2026 |
| 24 | Biometrics Tracking | Active (sample) | `data/visas/*.yaml` (biometrics), `templates/country.md.jinja`, `docs/stylesheets/theme.css` | Mar 2026 |
| 25 | Group G validation (new field checks) | Active | `validate/checks.py` (check_g), `validate/schema.py` | Mar 2026 |

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

### Session: 2026-03-15 — Claude (Opus 4.6) [continued]
**Branch:** feat/country-pages-v2
**What changed:**
- Created `docs-internal/02-frontend-system.md` — Part 2 documentation (map, theme, interactive components)
- Created `docs-internal/03-data-schema-and-country-pages.md` — Part 3 documentation (detailed YAML schema, Jinja2 template anatomy, validation matrix, how-to-add-a-country guide, edge cases)
- Committed validation system, state file, CLAUDE.md to git (commit `3bfd862`)
- Added `build_log.txt` and `nul` to `.gitignore` (build artifacts)
**Files touched:**
- `docs-internal/02-frontend-system.md` — created
- `docs-internal/03-data-schema-and-country-pages.md` — created
- `docs-internal/README.md` — updated status for Parts 2 and 3
- `.gitignore` — added build_log.txt and nul exclusions

### Session: 2026-03-15 — Claude (Opus 4.6) [continued]
**Branch:** feat/country-pages-v2
**What changed:**
- Created `docs-internal/04-validation-and-safeguards.md` — Part 4 documentation (most detailed part yet: 14 sections covering defense-in-depth model, structural validation internals, AI accuracy audit, admin update tool safeguards, CI/CD pipelines, governance, security posture, failure scenarios)
**Files touched:**
- `docs-internal/04-validation-and-safeguards.md` — created
- `docs-internal/README.md` — updated status for Part 4

### Session: 2026-03-15 — Claude (Opus 4.6) [continued]
**Branch:** feat/country-pages-v2
**What changed:**
- Created `docs-internal/05-developer-workflows.md` — Part 5 (final part, maximum detail: 20 sections covering local setup, dev server, build pipeline, all 5 scripts with CLI flags/exit codes/internal flows, validate/ package internals, environment variables, contribution flow, CI/CD step-by-step, governance, .claude/ and .ai-state/ directories, legacy files, git workflow, 5 common task walkthroughs, troubleshooting guide, dependency reference)
- Expanded `docs-internal/01-architecture-and-data-flow.md` — Added deep dives: complete mkdocs.yml config (every feature flag, palette, extensions, plugins, nav), gen_pages.py internals (iso_to_flag Unicode algorithm, uppercase vs lowercase ISO, error handling table, set_edit_path trick, minified JSON), production security headers (docs/_headers), SEO (robots.txt)
- Expanded `docs-internal/02-frontend-system.md` — Added deep dives: map.js internals (constants, readyState guard, URL prefix, tooltip positioning edge cases), theme.js internals (regex class cleanup, sibling-walking algorithm, stale-data guard, initMiniMap fetch-parse-clone algorithm, initialization order), complete CSS inventory (border-radius, z-index stack, all animations with durations/easings, dark mode adaptation table, responsive breakpoints, prefers-reduced-motion, full class inventory)
- Expanded `docs-internal/03-data-schema-and-country-pages.md` — Added 3 new gotchas (#9 sibling-walking, #10 misleading function name, #11 Python YAML tags), accessibility attributes section (ARIA roles/labels on visa selector, occupation selector, mini-map), complete data-attribute inventory (all data-* attrs with who sets/reads them), template-to-CSS class mapping diagram
- All 5 parts complete — documentation finished
**Files touched:**
- `docs-internal/05-developer-workflows.md` — created
- `docs-internal/01-architecture-and-data-flow.md` — expanded with deep dives
- `docs-internal/02-frontend-system.md` — expanded with deep dives
- `docs-internal/03-data-schema-and-country-pages.md` — expanded with new sections
- `docs-internal/README.md` — marked Parts 4 and 5 as Done

### Session: 2026-03-15 — Claude (Opus 4.6) [continued]
**Branch:** feat/country-pages-v2
**What changed:**
- Built 6 new features from the product vision gap analysis, all with sample data on Japan and France:
  1. **Change Log (Section D)** — per-country changelog with date, type (Fee/Document/Process/Policy), description, and source link. Rendered as a styled table with color-coded type tags.
  2. **Visa Exemptions / Indian Privilege (Section B)** — third-party visas that unlock simplified entry. Each exemption is a card with holding, grants, conditions, and verify-source link.
  3. **Transit Rules (Section B)** — transit visa requirements with exceptions list. Simple info-box layout.
  4. **Jurisdiction Map (Section A)** — maps Indian states to consular offices. Card-per-office layout with dot-separated state lists.
  5. **ECR / Non-ECR Rules (Section B)** — conditional red-border warning when ECR rules apply. Green for no-ECR countries.
  6. **Biometrics Tracking (Section C)** — biometrics required flag, validity period (e.g. 59 months for Schengen VIS), and notes.
- All 6 features use conditional Jinja2 blocks (`{% if field %}`) for backward compatibility — 24 countries without new fields render unchanged.
- Added Group G validation checks (G1–G9) for all new YAML fields.
- Added `TLScontact` to known processors, `ALLOWED_CHANGELOG_TYPES`, `KNOWN_INDIAN_STATES` to schema.
- Added `visa_difficulty: 5` to allowed set (for future use with hardest-tier countries).
- Full validation passes: 1184 checks across 26 files, 0 errors, 4 pre-existing warnings.
- MkDocs `--strict` build succeeds for all 26 countries.
**Files touched:**
- `data/visas/japan.yaml` — added jurisdiction, transit, exemptions, ecr, biometrics, changelog sections
- `data/visas/france.yaml` — added jurisdiction, transit, exemptions, ecr, biometrics, changelog sections
- `templates/country.md.jinja` — added 6 new conditional template sections (jurisdiction, transit, exemptions, ECR, biometrics, changelog)
- `docs/stylesheets/theme.css` — added CSS for sections 16–21 (jurisdiction, transit, exemptions, ECR, biometrics, changelog) with dark mode support
- `validate/schema.py` — added ALLOWED_CHANGELOG_TYPES, KNOWN_INDIAN_STATES, TLScontact, visa_difficulty 5
- `validate/checks.py` — added check_g() with G1–G9 validation for all new fields
- `validate.py` — wired check_g into per-file validation pipeline
- `.ai-state/STATE.md` — appended this session log

### Session: 2026-03-15 — Claude (Opus 4.6) [Session 6 — Dossily scaffolding]
**Branch:** main (Atlas), first-commit-fresh (Dossily)
**What changed:**
- Set up AI agent scaffolding for sibling project Dossily (Vertical 2 — mobile app)
- Dossily repo: [shan8tanu/dossily-app](https://github.com/shan8tanu/dossily-app)
- Created in Dossily: CLAUDE.md, .ai-state/STATE.md, docs-internal/ (vision Parts 1 & 2 + prerequisites), .claude/, .github/, services/, types/, utils/ with READMEs
- Updated Dossily .gitignore and README.md
- Committed and pushed to dossily-app `first-commit-fresh` branch
**Files touched (in Atlas):**
- `.ai-state/STATE.md` — appended this session log entry

### Session: 2026-03-27 — Claude (Opus 4.6)
**Branch:** feat/transit-guide (from main)
**What changed:**
- Built Transit Rules Guide — first non-country data-driven page in Atlas
- Created `data/transit/transit_rules.yaml` with 6 airport hubs: FRA, CDG, LHR, DXB, SIN, IST
- Created `templates/transit-guide.md.jinja` — Jinja2 template rendering all hubs as a single wiki page
- Extended `gen_pages.py` to generate transit guide page (with graceful skip if YAML missing)
- Added `Guides` nav section to `mkdocs.yml` between Countries and Contribute
- Added `guide` page type marker to `overrides/main.html` (enables `body.atlas-page--guide` CSS targeting)
- Git cleanup: committed stale STATE.md/settings changes on main, deleted 2 stale local branches
- `mkdocs build --strict` passes, all 6 hubs render with atlas-card styling, edit link points to YAML source
- Source URLs are placeholders — marked for verification before production
**Files touched:**
- `data/transit/transit_rules.yaml` — created (6 hubs, ~120 lines)
- `templates/transit-guide.md.jinja` — created (transit guide template)
- `gen_pages.py` — added transit guide generation block (~20 lines after map-data.json)
- `mkdocs.yml` — added Guides nav section
- `overrides/main.html` — added guide page type elif branch
- `.ai-state/STATE.md` — updated folder structure, feature registry, appended this log

### Session: 2026-04-26 — Claude (Sonnet 4.6)
**Branch:** main (direct push)
**What changed:**
- Fixed `validate_accuracy.py` Windows crash: replaced emoji `⚠️` warning with ASCII `WARNING:` to prevent UnicodeEncodeError on cp1252 terminals
- Installed `anthropic` package (was missing from environment) and ran `validate_accuracy.py` across all 26 countries — report saved to `validation-report.md`
- CI simplification: `htmlproofer` now skipped on push to main (gated to `pull_request` events only via `if: github.event_name == 'pull_request'`). Prevents dead embassy portals from blocking unrelated tool pushes. Weekly `link-check.yml` cron unchanged.
- Added `Bash(echo $ANTHROPIC_API_KEY)` and `Bash(python validate_accuracy.py)` permissions to `.claude/settings.local.json`
- Pushed 6 pending commits to origin/main (4 theme commits from prior session + 2 from this session)
**Files touched:**
- `validate_accuracy.py` — fixed Windows encoding crash
- `.claude/settings.local.json` — added 2 Bash permissions
- `.github/workflows/ci.yml` — gated htmlproofer to PR events only
- `validation-report.md` — generated (not committed, gitignored)

### Session: 2026-07-02 — Claude (Fable 5)
**Branch:** main (direct push)
**What changed:**
- Validator hardening: F4 now ignores subdirectory nav pages (guides/), new E8 check enforces visa_type ↔ first visa_types tab agreement, KNOWN_PROCESSORS gained CVASC and Direct, claude_audit search year is now dynamic (was hardcoded 2025)
- Brazil: removed the e-Visa visa_types block entirely (audit confirmed no e-Visa for Indian citizens) — Standard Visa (Embassy) is now the default tab
- validate.py now reports 1214 checks, 0 errors, 0 warnings (previously 5 recurring warnings)
- Created `.github/workflows/accuracy-audit.yml` — weekly cron (Mondays 7 AM UTC) for validate_accuracy.py with job-summary report + 90-day artifact. **NOT yet pushed:** git token lacks `workflow` OAuth scope; file exists locally only. Also requires ANTHROPIC_API_KEY + BRAVE_SEARCH_API_KEY repo secrets before it can run.
**Files touched:**
- `validate/checks.py` — F4 fix, new E8 check
- `validate/schema.py` — KNOWN_PROCESSORS additions
- `validate/claude_audit.py` — dynamic search year
- `data/visas/brazil.yaml` — removed evisa block
- `.github/workflows/accuracy-audit.yml` — created (local only, pending workflow scope)

### Session: 2026-07-02 — Claude (Fable 5) [continued]
**Branch:** main + 4 PR branches (add/sri-lanka, add/united-kingdom, add/canada, add/maldives)
**What changed:**
- Weekly accuracy audit is fully operational: workflow scope granted, ANTHROPIC_API_KEY + BRAVE_SEARCH_API_KEY set as repo secrets via gh, accuracy-audit.yml pushed, manual test run succeeded end-to-end (run 28565064673)
- Built `add_country.py` — 4-stage AI country pipeline: Brave research → Sonnet draft (prompt-cached system block: schema contract + japan.yaml gold example) → validate.py self-check with one repair pass → mkdocs nav insert + branch + PR via gh. New provenance convention: `data/sources/<slug>.yaml` sidecar records source/confidence (web|pattern|unverified) per fact group; PR body turns pattern/unverified fields into a human verification checklist; --audit embeds an independent validate_accuracy.py second opinion
- Ran pilot on 4 new countries → PRs #10 Sri Lanka, #11 United Kingdom, #12 Canada, #13 Maldives. All passed structural validation first-try. NOT merged — awaiting founder field-by-field review. Note: #10 and #13 both touch the Asia nav section of mkdocs.yml; expect a trivial one-line conflict when merging the second one
**Files touched:**
- `add_country.py` — created (the pipeline tool)
- `.github/workflows/accuracy-audit.yml` — pushed to main
- `data/visas/{sri-lanka,united-kingdom,canada,maldives}.yaml` — created on PR branches only
- `data/sources/{sri-lanka,united-kingdom,canada,maldives}.yaml` — provenance sidecars, PR branches only
- `mkdocs.yml` — nav entries, PR branches only

### Session: 2026-03-29 — Claude (Opus 4.6)
**Branch:** feat/transit-guide
**What changed:**
- Created Weekly Data Validation & Completeness Operations Manual — comprehensive human-in-the-loop data quality process
- Created `docs-internal/weekly-validation-plan.md` — 9-section operations manual covering: API key setup, executive summary, one-time baseline audit, weekly 7-step recurring checklist, 3-tier country rotation schedule (4-week cycle), field-by-method validation matrix with source URLs, future country population workflow (24 new countries in 4 batches), anti-bot mitigation strategies, cross-session planning protocol
- Created `docs-internal/audit-log.md` — running audit log with: baseline audit tracker (26 countries), Section A-D population tracker (24 countries pending), weekly entry template with per-country results table, blocker taxonomy (6 categories: ANTI_BOT, PORTAL_DOWN, PDF_MISSING, NO_SOURCE, CONFLICTING_SOURCES, LANGUAGE_BARRIER) with mitigation and follow-up fields
- No code changes — pure documentation deliverable that works with existing validate.py, validate_accuracy.py, and admin_update.py tooling
- Key finding: AI accuracy audit (validate_accuracy.py) only covers 8 of 30+ YAML fields. Document checklists, occupation documents, jurisdiction, transit, exemptions, ECR, biometrics all require manual validation.
**Files touched:**
- `docs-internal/weekly-validation-plan.md` — created (~600 lines)
- `docs-internal/audit-log.md` — created (~150 lines)
- `.ai-state/STATE.md` — appended this session log

### Session: 2026-04-12 — Claude (Opus 4.6)
**Branch:** main
**What changed:**
- Switched Atlas to system fonts and dropped dark mode to match the editorial feel of https://fabs.pranaykotas.com/ (Pandoc+Bootstrap reference)
- `mkdocs.yml`: `font:` block replaced with `font: false` (the Material sentinel that disables the Google Fonts `<link>` loader entirely — no `fonts.googleapis.com` requests). Palette collapsed to a single `default` entry with no `toggle:` key so Material never renders the scheme switcher
- `theme.css`: system font stacks added on `body` (NOT `:root` — see note below), heading catch-all rule, `.md-typeset { line-height: 1.75 }` body-prose bump, `color-scheme: light`, full deletion of all `[data-md-color-scheme="slate"]` blocks (7 selectors), deletion of `.md-header__option` chrome rule, hardcoded Inter/JetBrains references removed, cover letter `<pre>` switched to `var(--md-code-font-family)`
- Editorial polish: card border-radius `8px → 4px` on 9 component selectors (card, checklist, health, cover-letter, jurisdiction, transit, exemption-card, ecr, biometrics) plus minimap `12px → 6px`; `--atlas-surface` `#f8f9fa → #fcfcfc`; button hover flat (no `translateY`, color-shift only); minimap shadow softened + no hover bounce; hero weight `800 → 700`, padding tightened, animation duration `600ms → 220ms`, stagger `80ms → 0ms`
- `map.css`: full slate dark-mode block deleted (tooltip, country, disabled rules)
- **IMPORTANT for future agents:** Material's compiled `main.css` sets `--md-text-font-family` on the `body` selector using `var(--md-text-font, _)` with a sentinel fallback. A `:root` override is shadowed by that more-specific body-level declaration — the font vars MUST live on `body` in `theme.css` for the cascade to win. First commit put them on `:root` and the override silently failed verification (computed font was `_, -apple-system, ...`); the fix commit moved them to `body`. Don't put font custom-property overrides on `:root` when overriding Material tokens.
- Verification: `mkdocs build --strict` passes twice, `validate.py` passes, `preview_network` shows zero Google Fonts requests, `preview_eval` confirms `getComputedStyle(document.body).fontFamily` starts with `system-ui` and `<pre>.atlas-cover-letter__text` font starts with `ui-monospace`, card border-radius computes to `4px` site-wide, `.atlas-card` background is `rgb(252, 252, 252)`, `data-md-color-scheme=default`, Japan/transit-guide/map/homepage all render correctly
- Three commits: `50d64be` font swap + dark mode removal, `def8cdc` editorial polish, `939ab47` font scope fix (`:root` → `body`)
**Files touched:**
- `mkdocs.yml` — `font: false`, palette collapsed to single light entry with no toggle
- `docs/stylesheets/theme.css` — system font vars on `body`, heading catch-all, line-height bump, all slate blocks deleted, radii flattened, animation tokens quieted, hero softened, minimap shadow softened, cover-letter pre uses code-font token
- `docs/stylesheets/map.css` — slate dark-mode block deleted
- `.ai-state/STATE.md` — appended this session log

### Session: 2026-07-02 — Claude (Fable 5) [continued 2 — Greptile review fixes]
**Branch:** main + 4 PR branches
**What changed:**
- Triaged Greptile reviews on PRs #10-#13 and applied all mechanical fixes:
  - main: .claude/settings.local.json gitignored + untracked (security hygiene — committed allowlist contained an API-key-injecting command)
  - #10 Sri Lanka: official_portal -> https://www.eta.gov.lk/ (application entry point), processing_days 2 -> 3
  - #11 UK: bg_color -> "White or light grey"; fee/processing discrepancies REMAIN OPEN pending founder check vs UKVI fee schedule (audit says ~Rs.21,399 vs stored Rs.15,726)
  - #12 Canada: processing_days 45 -> 33 working days (calendar/working-day unit conversion)
  - All 4 sidecars: corrected hallucinated _meta.generated dates (root cause already fixed in add_country.py)
- Posted resolution comments on all 4 PRs
**Files touched:**
- .gitignore — added settings.local.json exclusion (main)
- data/visas + data/sources for sri-lanka, united-kingdom, canada, maldives — on their PR branches

### Session: 2026-07-08 — Claude (Opus 4.8)
**Branch:** main
**What changed:**
- Did a full file-by-file review of the repo and drafted `atlas_PROJECT_STATE.md` — a point-in-time current-state snapshot (distinct from this append-only log). Covers build pipeline, schema contract, validation groups A–G, all 5 CLI tools + model IDs, frontend, CI/CD, and a "Known drift" section.
- Updated stale documentation to match reality:
  - `FEATURES.md` — rewrote the Community/CI section. Removed references to `.github/CODEOWNERS` and `.github/workflows/deploy.yml` (neither exists), corrected hosting from GitHub Pages to Cloudflare Pages, fixed the PR-template path (now a `PULL_REQUEST_TEMPLATE/` directory), and added validate.py + the link-check/accuracy-audit workflows.
  - `.ai_context.md` — added a header note flagging it as founding vision (not current impl) and pointing to atlas_PROJECT_STATE.md.
  - This file — added `accuracy-audit.yml`, `add_country.py`, `atlas_PROJECT_STATE.md` to the folder tree and a note that the CODEOWNERS line in the tree is inaccurate.
- **Drift findings (surfaced, not auto-fixed):**
  1. All 26 `docs/<country>.md` and `docs/map-data.json` are committed but regenerated in-memory by `gen_pages.py` every build — stale artifacts (last touched 2026-03-01). Build is unaffected (virtual wins) but they contradict CLAUDE.md's "don't exist on disk." Candidates for deletion from git — left for founder decision.
  2. `.github/CODEOWNERS` referenced by old docs does not exist anywhere in the repo.
  3. `data/sources/` exists only on PR branches, not `main`.
- Verified: `python validate.py` → 1214 checks, 0 errors, 0 warnings; `mkdocs build --strict` → exit 0.
**Files touched:**
- `atlas_PROJECT_STATE.md` — created
- `FEATURES.md` — corrected Community/CI section + added atlas_PROJECT_STATE.md pointer
- `.ai_context.md` — added header pointer note
- `.ai-state/STATE.md` — folder-tree additions + this session log entry

### Session: 2026-07-09 — Claude (Opus 4.8)
**Branch:** feat/per-claim-citations (from main)
**What changed:**
- **Item Zero — per-claim citations infrastructure + Japan reference.** Every citable fact block
  can now display source link + authority tier + access date, or an "unverified" caveat.
- **Schema**: added optional `sources` list (`url`/`tier` 1–3/`label`/`accessed`) + `unverified`
  bool to dict blocks (requirements, health, each visa_types entry, transit, ecr, biometrics) and
  parallel `jurisdiction_sources`/`_unverified` + `exemptions_sources`/`_unverified` for the list
  blocks. Single source of truth: `CITABLE_BLOCKS` registry in `validate/schema.py`.
- **Validation group H** (`validate/checks.py` `check_h`): H1–H5 validate each source entry's
  shape (fields, https URL, tier ∈ {1,2,3}, parseable date); H6 warns when a citable block lacks
  both `sources` and `unverified` — new `--strict-citations` flag upgrades H6 to an error to gate
  CI post-migration. Wired into `validate.py`; docstring updated.
- **Rendering**: `cite()` macro in `templates/country.md.jinja` renders a subtle tier-badged
  "Sources" line or an amber "Unverified / Community-Reported" caveat with a prefilled GitHub-issue
  "Report it" link; blocks with neither render nothing (un-migrated pages unchanged). Styles in
  `docs/stylesheets/theme.css` §23.
- **Japan migrated** as the reference: requirements + standard_visa docs cite the embassy (T1) and
  VFS (T2) URLs (accessed 2026-07-09, corroborated via web search — origin servers `.go.jp`/VFS
  bot-block direct fetch with 403, so access was verified through search). health, transit, ecr,
  biometrics, the e-Visa/long-stay tabs, jurisdiction, and exemptions are honestly flagged
  `unverified: true` (no openable official source). Japan passes `--strict-citations`.
- **`add_country.py`**: `_SCHEMA_CONTRACT` now instructs drafts to emit `sources` per block from
  the provenance sidecar (confidence `web`→tiered source, `pattern`/`unverified`→`unverified: true`).
- Docs: `atlas_PROJECT_STATE.md` (§4 schema, §5 group H), `FEATURES.md` (new citations section).
- **Verified**: `validate.py` → exit 0 (129 H6 warnings on the 25 un-migrated countries);
  `validate.py --strict-citations` → exit 1 (fails on those 25); `--strict-citations --file
  japan.yaml` → exit 0; malformed-source fixture confirmed H2–H5 fire; `mkdocs build --strict` →
  exit 0; live preview confirmed Japan renders T1/T2 source lines + 8 unverified caveats and
  France (non-migrated) renders zero citation markup (no regression).
- **NOT committed/pushed** — working tree on the feature branch awaiting maintainer review.
**Files touched:**
- `validate/schema.py` — ALLOWED_SOURCE_TIERS, SOURCE_REQUIRED_FIELDS, SOURCE_DATE_FORMAT, CITABLE_BLOCKS
- `validate/checks.py` — `check_h` (group H) + `_iter_present_citable_blocks`
- `validate.py` — import/wire check_h, `--strict-citations` flag, docstring
- `templates/country.md.jinja` — `cite()` macro + 10 per-block call sites
- `docs/stylesheets/theme.css` — §23 sources/unverified styles
- `data/visas/japan.yaml` — citation migration (reference country)
- `add_country.py` — citations added to `_SCHEMA_CONTRACT`
- `atlas_PROJECT_STATE.md`, `FEATURES.md`, `.ai-state/STATE.md` — docs
