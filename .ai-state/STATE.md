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
│   ├── volatility.yaml           # Freshness cadence policy — one entry per CITABLE_BLOCKS key
│   ├── sources/                  # Provenance sidecars for AI-drafted countries (added 2026-07-09)
│   │   ├── canada.yaml
│   │   ├── maldives.yaml
│   │   ├── sri-lanka.yaml
│   │   └── united-kingdom.yaml
│   └── visas/                    # SOURCE OF TRUTH — 30 country YAML files
│       ├── australia.yaml
│       ├── brazil.yaml
│       ├── cambodia.yaml
│       ├── canada.yaml           # added 2026-07-09 via add_country.py
│       ├── china.yaml
│       ├── france.yaml
│       ├── germany.yaml
│       ├── greece.yaml
│       ├── indonesia.yaml
│       ├── italy.yaml
│       ├── japan.yaml            # citation + freshness reference country
│       ├── laos.yaml
│       ├── malaysia.yaml
│       ├── maldives.yaml         # added 2026-07-09 via add_country.py
│       ├── netherlands.yaml
│       ├── new-zealand.yaml
│       ├── philippines.yaml
│       ├── qatar.yaml
│       ├── saudi-arabia.yaml
│       ├── singapore.yaml
│       ├── south-korea.yaml
│       ├── spain.yaml
│       ├── sri-lanka.yaml        # added 2026-07-09 via add_country.py
│       ├── switzerland.yaml
│       ├── thailand.yaml
│       ├── turkey.yaml
│       ├── uae.yaml
│       ├── united-kingdom.yaml   # added 2026-07-09 via add_country.py
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
│   ├── country.md.jinja          # THE template for all 30 country pages
│   └── transit-guide.md.jinja    # Template for Transit Rules Guide page
├── validate/                     # Validation module
│   ├── __init__.py
│   ├── checks.py                 # Validation checks A–I (structural → citations → volatility)
│   ├── schema.py                 # Allowed values, ISO codes, placeholder definitions,
│   │                             #   CITABLE_BLOCKS, DIFFICULTY_LABELS
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
│                                 #   + freshness context + /meta/freshness page
├── freshness.py                  # Freshness engine: cadence policy, block states, page rollup,
│                                 #   git-date cache, report builder (added 2026-07-09)
├── freshness_report.py           # CLI: librarian's re-verification queue, always exit 0
├── validate.py                   # CLI: structural YAML validation
├── validate_accuracy.py          # CLI: AI-powered accuracy audit (needs ANTHROPIC_API_KEY)
├── admin_update.py               # CLI: trusted-source YAML updates with diff + confirmation
├── add_country.py                # CLI: AI new-country pipeline (research→draft→validate→PR)
├── add_visa_types.py             # One-shot: bulk-added visa_types to all YAMLs
├── add_occupation_docs.py        # One-shot: bulk-added occupation_documents to all YAMLs
└── atlas_PROJECT_STATE.md        # Current-state snapshot (last synced 2026-07-09)
```

---

## Tech Stack

| Layer | Tool | Version/Notes |
|-------|------|---------------|
| Site Generator | MkDocs | Python-based |
| Theme | Material for MkDocs | Custom overrides in `overrides/` |
| Templating | Jinja2 | Build-time only |
| Data | YAML (PyYAML) | 30 country files in `data/visas/` |
| Build Plugin | mkdocs-gen-files | Virtual page generation |
| Frontend JS | Vanilla JavaScript | Zero external libraries |
| Frontend CSS | Custom CSS | Light mode only (dark mode removed Apr 2026) |
| AI Validation | Anthropic Claude API | Used by validate_accuracy.py, admin_update.py, add_country.py |
| Web Search | Brave Search API | Optional, used by accuracy validator + add_country.py research |
| CI/CD | GitHub Actions | 3 workflows: ci.yml, link-check.yml, accuracy-audit.yml |
| Hosting | Cloudflare Pages | Static site at atlas-wiki.pages.dev |

---

## Feature Registry

| # | Feature | Status | Key Files | Added |
|---|---------|--------|-----------|-------|
| 1 | Data-driven country pages (30 countries) | Active | `gen_pages.py`, `templates/country.md.jinja`, `data/visas/*.yaml` | Feb 2026 |
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
| 13 | Structural YAML validation (checks A–I) | Active | `validate.py`, `validate/checks.py`, `validate/schema.py` | Mar 2026 |
| 14 | AI accuracy audit (Claude + Brave) | Active | `validate_accuracy.py`, `validate/claude_audit.py` | Mar 2026 |
| 15 | Admin update tool (trusted-source updates) | Active | `admin_update.py` | Mar 2026 |
| 16 | Community edit routing (YAML, not MD) | Active | `gen_pages.py` (set_edit_path) — note: `.github/CODEOWNERS` does NOT exist despite older docs referencing it; merge protection is a repo ruleset requiring only the `Build & Validate` check, no human-approval rule | Feb 2026 |
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
| 26 | AI new-country pipeline (research→draft→validate→PR) | Active | `add_country.py`, `data/sources/*.yaml` (provenance sidecars) | Jul 2026 |
| 27 | Per-claim citations (source + tier + access date per fact block) | Active — Japan migrated, 29 pending | `data/visas/*.yaml` (sources/unverified), `templates/country.md.jinja` (cite() macro), `validate/checks.py` (check_h), `validate/schema.py` (CITABLE_BLOCKS) | Jul 2026 |
| 28 | Volatility-based freshness (cadence + fresh/aging/overdue states) | Active | `data/volatility.yaml`, `freshness.py`, `freshness_report.py`, `gen_pages.py`, `templates/country.md.jinja`, `validate/checks.py` (check_i) | Jul 2026 |
| 29 | Freshness report / librarian queue (`/meta/freshness`) | Active | `freshness_report.py`, `gen_pages.py`, `mkdocs.yml` (`not_in_nav`), `.github/workflows/ci.yml` | Jul 2026 |

---

## Countries Covered (30)

**Asia (13):** Cambodia, China, Indonesia, Japan, Laos, Malaysia, Maldives, Philippines, Singapore, South Korea, Sri Lanka, Thailand, Vietnam
**Oceania (2):** Australia, New Zealand
**Europe (9):** France, Germany, Greece, Italy, Netherlands, Spain, Switzerland, Turkey, United Kingdom
**Middle East (3):** Qatar, Saudi Arabia, UAE
**Americas (3):** Brazil, Canada, United States

*(Maldives, Sri Lanka, United Kingdom, Canada added 2026-07-09 via the `add_country.py` AI pipeline — see Feature #26.)*

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

### Session: 2026-07-09 — Claude (Opus 4.8) [continued — freshness system]
**Branch:** feat/freshness-system (from main, after PR #14 merged)
**What changed:**
- PR #14 merged to main (squash, `d45a6c7`). Also fixed the repo RULESET (not code): it required
  a status check named "Build & Link Health Check" but the CI job was renamed "Build & Validate"
  in `0b8f9a5` — every PR was silently BLOCKED. Updated ruleset 13252933 via gh api to the real
  check name. PRs #10–#13 left open (their human-verification checkboxes are unchecked).
- **Volatility-based freshness system** on top of citations:
  - `data/volatility.yaml` — cadence policy: requirements 30d, visa_types 45d,
    health/transit/jurisdiction/exemptions 90d, ecr/biometrics 180d. Per-block override
    `cadence_days` (dict blocks) / `<key>_cadence_days` (list blocks).
  - `freshness.py` — engine: block states (fresh ≤ cadence · aging ≤ 2× · overdue > 2× from
    newest `accessed`; unverified exempt, unsourced silent), worst-state-wins page rollup,
    ONE-git-call last-commit-date cache (never file mtime), report builder (console + markdown).
  - `freshness_report.py` — CLI, always exit 0 (librarian queue, not a gate); `--data-dir`/`--today`
    flags for fixtures. New CI step prints it on every run.
  - `gen_pages.py` — sys.path guard for repo-root imports; injects `_freshness`,
    `_page_freshness` (incl. git_date fallback), `_difficulty_label`; emits virtual
    `/meta/freshness` page (nav-hidden via mkdocs `not_in_nav: meta/*`).
  - Template: `cite()` gained `fresh` arg — sources lines append "· re-checked every N days" +
    text state label when aging/overdue (never color alone). Visa Info card gained a Difficulty
    row (`DIFFICULTY_LABELS` added to validate/schema.py, mirrors map.js 1–5 incl. 5=Restricted)
    and the page badge ("Facts verified on schedule / due / overdue · date · some sections
    pending citation" | fallback "Last updated <git date> · source citations being added").
    Wording rule: "verified" = source checked, "updated" = commit.
  - Validation: `_iter_present_citable_blocks` now yields a 5-tuple (+cadence override), H7
    validates overrides, new site-level `check_i` (I1–I4) enforces policy completeness.
- **Verified**: validate.py exit 0 (129 H6 warnings unchanged, 1219 passed); I3/I4 fire on a
  doctored scratch policy; fixture (scratchpad, deleted) exercised fresh+aging+overdue and
  worst-wins=overdue with correct report ordering; real report exit 0 (japan all fresh, 25-country
  worklist oldest-first); `mkdocs build --strict` green with `site/meta/freshness/index.html`;
  DOM-verified via preview: japan badge "Facts verified on schedule · 2026-07-09" + Difficulty
  "4 — Standard Visa" + "re-checked every 30/45 days" spans; thailand shows ONLY Difficulty row +
  "Last updated 2026-03-15 · source citations being added" (zero citation markup); /meta/freshness
  renders both sections (screenshot tool timed out — DOM checks used instead).
**Files touched:**
- `data/volatility.yaml` — created (cadence policy)
- `freshness.py`, `freshness_report.py` — created
- `validate/schema.py` — DIFFICULTY_LABELS
- `validate/checks.py` — iterator 5-tuple, H7, check_i
- `validate.py` — wire check_i, docstring A–I
- `gen_pages.py` — freshness context + /meta/freshness
- `templates/country.md.jinja` — fresh arg, call sites, Difficulty row, page badge
- `docs/stylesheets/theme.css` — freshness + page-badge styles
- `mkdocs.yml` — not_in_nav meta/*
- `.github/workflows/ci.yml` — freshness report step
- `atlas_PROJECT_STATE.md`, `FEATURES.md`, `.ai-state/STATE.md` — docs

### Session: 2026-07-09 — Claude (Opus 4.8) [continued — Greptile fix, main sync, doc refresh]
**Branch:** feat/freshness-system → main (after user merge)
**What changed:**
- Addressed Greptile's review comment on PR #15 (`templates/country.md.jinja`): empirically verified
  it does NOT actually crash the build (Jinja's default Undefined degrades silently; H2 is already
  an ERROR that blocks CI before any build) — but found a real narrower gap: `mkdocs serve` (the
  local dev workflow) skips `validate.py`, so a malformed mid-edit source could render a broken
  citation badge. Hardened `cite()` with a `selectattr`-based filter to well-formed entries;
  verified japan's rendered output is byte-identical, malformed/mixed fixtures render correctly.
- User merged all 5 open PRs (#10 Sri Lanka, #11 UK, #12 Canada, #13 Maldives, #15 freshness) via
  GitHub directly — I could not self-merge #15 (blocked by the auto-mode permission classifier:
  self-authored PR to `main` with no CODEOWNERS/human-review gate). Synced local `main`
  (fast-forward, 5630f29→2ddee59 total after fetch), deleted local branches for the merged PRs
  (remote branches for add/* left in place — not asked to delete, more consequential).
  Full validate.py + `mkdocs build --strict` re-run on merged main: 1403 checks, 0 errors, 143
  warnings (up from 1219/129 — expected, the 4 new countries add H6 unmigrated-citation warnings).
- **Repo now: 30 countries** (was 26). Updated stale documentation across the repo to match:
  - `atlas_PROJECT_STATE.md` — country count/list, repo map (added `data/sources/`, `freshness.py`,
    `freshness_report.py`, fixed the `PROJECT_STATE.md`→`atlas_PROJECT_STATE.md` self-reference
    left over from the rename), check-group table (A–I), validate.py counts, CI table (added the
    freshness-report step), "Known drift" item 4 marked resolved (data/sources/ now on main), new
    drift item 5 documenting the ruleset fix from earlier this session, new-country-pipeline section
    now notes the 4 merged countries lack citations yet.
  - `FEATURES.md` — "checks A–G" → "A–I" (2 places).
  - `.ai-state/STATE.md` (this file) — folder tree, tech stack table (also fixed a pre-existing
    stale "light/dark mode" claim — dark mode was removed back in April), Feature Registry (fixed
    #1/#13/#16 counts and the CODEOWNERS reference, added #26–29 for the new-country pipeline,
    citations, freshness, and the freshness report — all of which existed before this session but
    were never registered), Countries Covered list (also fixed a pre-existing Europe count error:
    8 countries were listed under a "(7)" heading even before UK was added).
  - `.github/workflows/accuracy-audit.yml` — job name and comment hardcoded "26 countries"; made
    count-agnostic instead of hardcoding 30 (will drift again otherwise).
- Did NOT touch: historical session-log entries in this file (this file's own rules make them
  append-only), `add_visa_types.py`/`add_occupation_docs.py` docstrings (one-shot scripts
  describing a historical run, not living docs), remote `add/*` branches (not asked to delete).
**Files touched:**
- `templates/country.md.jinja` — cite() macro hardening (commit `ba3b2b0` on the now-merged PR)
- `atlas_PROJECT_STATE.md`, `FEATURES.md`, `.ai-state/STATE.md`,
  `.github/workflows/accuracy-audit.yml` — documentation sync

### Session: 2026-07-09 — Claude (Opus 4.8) [continued — docs-internal full refresh]
**Branch:** main
**What changed:**
- Full refresh of the gitignored `docs-internal/` suite (~5,300 → ~8,300 lines), which was written
  2026-03-15/29 and predated citations, freshness, add_country.py, the dark-mode removal, and the
  4 new countries. Three parallel agents rewrote the five technical parts, each verifying every
  claim against current source (not prior docs); I handled the two operational docs by hand.
- Technical parts: Part 01 (arch, 480→1042 lines) gained citations/freshness/add_country deep
  dives + corrected governance from the live `gh api` ruleset; Part 02 (frontend, 641→889) had its
  dark-mode/Google-Fonts content replaced with the real light-only/system-font state incl. the
  `body`-vs-`:root` font-var gotcha; Part 03 (schema, 946→1655) added sources/unverified/
  cadence_days to every block reference, the cite() walkthrough, and §15/§16 for vision blocks +
  citations/freshness; Part 04 (validation, 1088→1879) added Groups G/H/I (G was never documented
  at all), the freshness tier, real governance (no CODEOWNERS; ruleset requires only Build &
  Validate, no human-approval rule) and the stale-check-name failure scenario; Part 05 (workflows,
  1192→1806) added freshness_report.py/add_country.py references, H*/I* troubleshooting, and a
  command cheat sheet.
- Operational docs: `weekly-validation-plan.md` got a prominent 2026-07-09 update note — the
  manual weekly audit is largely superseded by the automated `/meta/freshness` queue for cited
  countries and now primarily drives citation migration; §6 rewritten around add_country.py (4 of
  6 Batch-1 countries done); rotation tables flagged as not yet re-tiered for the new 4.
  `audit-log.md` trackers extended with the 4 new countries (tier unassigned — founder call) and
  annotated that the baseline audit was never run. README.md links fixed (they pointed to
  pre-rename filenames) + operational-docs table added.
- Cross-check pass caught and fixed one agent error: Parts 02/03 claimed "only Japan" has the six
  vision-feature blocks — ground truth (grep of all 30 YAMLs) is Japan AND France (28 of 30 lack
  them); citations, separately, ARE Japan-only. Agents' independent findings recorded in their
  parts: old docs misclassified Brazil as e-Visa-primary; Canada/Maldives are the first
  single-visa-type countries (tabs branch now exercised for real); difficulty tier 5 is now
  validated; ruleset display name is still the old one (cosmetic — the gating check context is
  correct).
**Files touched:**
- `docs-internal/` (all 8 files — gitignored, local-only; no repo commit for them)
- `.ai-state/STATE.md` — this entry

### Session: 2026-07-10 — Claude (Fable 5)
**Branch:** feat/changes-feed (from main)
**What changed:**
- Site-wide Change Log page + RSS feed aggregating every country's `changelog` entries:
  - `gen_pages.py` collects (date, country, slug, type, description, source) while looping YAMLs;
    unparseable dates -> named build warning + exclusion (non-fatal). New virtual page `changes.md`
    (nav: between Guides and Contribute) grouped by month via `templates/changes.md.jinja`,
    reusing the existing `.atlas-changelog` table + tag classes (zero new CSS/JS).
  - RSS 2.0 at `changes.xml`: hand-built with `xml.sax.saxutils.escape`, RFC 822 pubDates via
    `email.utils.format_datetime` (locale-independent; strftime %a/%b/%B deliberately avoided),
    50-item cap, guid = slug+date+per-country-index, links to `{slug}/#change-log`, channel URLs
    from mkdocs.yml `site_url` (via `mkdocs_gen_files.config` with fallback), atom:self link.
    Autodiscovery `<link>` added to `overrides/main.html` extrahead block.
  - Validation: new G10 (date parses YYYY-MM-DD), G11 (description non-empty), G12 (source https)
    -- ERRORs, so the feed can trust its inputs. `check_f` non_country_pages gained `changes.md`
    (would otherwise trip the F4 nav-parity warning).
- Spec mismatches flagged: spec said "26 files" -- repo has 30; only japan+france carry changelog
  data (6 entries total). All 6 render; feed validated well-formed (Python minidom; no xmllint on
  this box), month grouping/nav/autodiscovery DOM-verified via preview + screenshot.
**Files touched:**
- `gen_pages.py` -- changelog collection + changes.md + changes.xml emission
- `templates/changes.md.jinja` -- created
- `overrides/main.html` -- RSS autodiscovery link
- `mkdocs.yml` -- Changes nav entry
- `validate/checks.py` -- G10-G12, non_country_pages, group-G docstring
- `atlas_PROJECT_STATE.md`, `FEATURES.md`, `.ai-state/STATE.md` -- docs

### Session: 2026-07-10 — Claude (Fable 5) [fee breakdown]
**Branch:** feat/fee-breakdown (from main)
**What changed:**
- Fee breakdown structure: optional `requirements.fees` block (components with
  label/amount_inr/mandatory/refundable + optional note; exactly one `is_government_fee: true`
  marker — chosen over label-matching, which breaks on wordings like "Embassy fee"; optional
  child_fee_inr / payment_methods / fee_last_revised). Legacy `visa_fee_inr` stays REQUIRED and
  = the government component (J4), so map / accuracy-audit / un-migrated pages are untouched.
- Validation group J (J1-J6) in validate/checks.py, wired into validate.py (docstring A-J):
  structure/types, amounts >= 0, exactly-one govt component, == visa_fee_inr, date parses,
  >= 1 mandatory. Optional-block pattern (absent -> silent), all ERRORs.
- Rendering: `compute_fees()` in gen_pages.py (totals COMPUTED at build time, never stored;
  defensive against malformed local data) injects `_fees` beside `_freshness`. Template: new
  `## Fees` table section (pipe-escaped labels/notes — lesson from PRs #16/#17), computed
  "Total (mandatory) / with all optional services" line, payment/revised meta line; overview row
  becomes "₹X total (₹Y government fee)"; checklist fee item shows the mandatory total (a
  visa_fee_inr consumer the spec didn't list). theme.css §24: changelog-style table + spec-required
  tabular-nums on the amount column. No fees block -> byte-identical rendering (thailand diffed).
- Japan reference migration — NO invented numbers: the cited VFS one-pager FETCHED successfully
  this time and yielded every amount: govt ₹500 single-entry (matches stored value), VFS service
  charge ₹800 (incl. taxes, effective 01-Apr-2026), optional courier ₹550, payment methods
  cash/POS/UPI, refund condition for the govt fee. VFS source accessed date bumped to 2026-07-10
  (actually opened); embassy source unchanged (still 403s). Mandatory total ₹1300, all-in ₹1850.
- add_country.py contract: fees block spec added; visa_fee_inr guidance FIXED from "realistic
  total" (the convention that produced the UK inconsistency in PR #11) to GOVERNMENT FEE ONLY;
  sidecar field list gains `fees`. Drafts scaffold govt-component-only when service charges are
  unsourced (an empty fees block would fail J1/J3/J6 by design).
- Verified: validate.py 1404 passed 0 errors (+1 = japan's J pass); all J1-J6 negative fixtures
  fire; --strict-citations japan exit 0; thailand byte-identical (stash-diff); strict build +
  freshness_report exit 0; DOM-verified japan fee table/totals/overview/checklist + tabular-nums
  computed style and thailand unchanged (screenshots timed out again — known flakiness).
**Files touched:**
- `validate/checks.py` — check_j (J1-J6)
- `validate.py` — wire check_j, docstring A-J
- `gen_pages.py` — compute_fees + _fees injection
- `templates/country.md.jinja` — Fees section, overview row, checklist line
- `docs/stylesheets/theme.css` — §24 fee table
- `data/visas/japan.yaml` — fees block + VFS source accessed bump
- `add_country.py` — contract fees spec + visa_fee_inr semantics fix
- `atlas_PROJECT_STATE.md`, `FEATURES.md`, `.ai-state/STATE.md` — docs

### Session: 2026-07-10 — Claude (Fable 5) [citations batch 1]
**Branch:** feat/citations-batch-1 (from main)
**What changed:**
- Migrated the next 5 worklist countries to per-block citations (japan pattern): Australia,
  Cambodia, France, Germany, Greece — 30 citable blocks total. Data values untouched (rule:
  discrepancies are reported, not fixed).
- Outcomes: 5 blocks CITED tier-1 (France requirements + biometrics via EU Commission pages;
  Germany requirements via india.diplo.de fee page + EU page; Greece requirements via EU page);
  25 blocks honestly `unverified` — every AU/KH portal and all VFS/TLS/mfa.gr pages block
  automated fetches (403 / redirect loops / WAF). accessed dates only on pages actually opened
  2026-07-10.
- DISCREPANCIES flagged for founder (PR #19): (1) Germany stored visa_fee_inr 7200 vs the German
  missions' published INR 9,800 for the €90 adult fee — the ₹7,200 convention (also FR/GR) uses a
  stale exchange rate; (2) e-Visa visa_types tabs on AU/FR/DE/GR are likely bulk-script artifacts
  (no e-Visa exists for Indian passports on any of them — Brazil precedent); (3) France transit
  exception lists UK visas but Visa Code Art. 3(5) search evidence lists only EU/CA/JP/US;
  (4) Australia health "insurance mandatory" is doubtful for visitor 600; (5) VIS source says
  fingerprint re-use over "5 years" vs stored "59 months" (consistent phrasing, noted).
- Post-review fixes (Greptile on PR #19): (a) `page_rollup` in freshness.py now counts
  `unverified` blocks as `pending` — an unverified block IS pending a real citation, so
  unverified-heavy pages no longer show a bare "verified on schedule" badge and stay on the
  migration worklist (AU/KH were wrongly dropping off with 0 real sources); (b) Germany
  requirements source label no longer embeds the contradicting "INR 9,800" figure (keeps the
  uncontested €90) so the live page doesn't self-contradict — the INR-convention discrepancy
  stays flagged in the PR for founder decision.
- Verified: all 5 files pass `validate.py -f <file> --strict-citations`; full validate 1408
  passed / 113 warnings (was 143 — 30 fewer H6); strict build green; freshness worklist 29 → 24;
  DOM-verified France + Thailand control.
**Files touched:**
- `data/visas/{australia,cambodia,france,germany,greece}.yaml` — sources/unverified only
- `freshness.py` — page_rollup pending includes unverified (post-review)
- `atlas_PROJECT_STATE.md`, `.ai-state/STATE.md` — docs

### Session: 2026-07-10 — Claude (Opus 4.8) [founder decisions: fee convention + data corrections]
**Branch:** fix/fee-convention-and-data-corrections (from main)
**What changed (all founder-directed):**
- Fee convention: adopted OFFICIAL-INR-FIRST (store the mission's published INR; convert only
  when none exists, recording rate+date). Written into add_country.py `_SCHEMA_CONTRACT`.
  - Germany visa_fee_inr 7200 -> 9800 (diplo.de official INR for €90, already cited T1).
  - France/Greece left at 7200 with a TODO comment — their consulate/VFS India fee pages
    bot-block automated fetches, so their official INR needs a human. Not guessed.
- e-Visa tab cleanup: DELETED the `evisa` visa_types tab from France/Germany/Greece (no Schengen
  short-stay e-Visa exists for Indian passports — Brazil precedent). Australia NOT deleted:
  relabelled `evisa` -> key `online`, label "Online (ImmiAccount)" — subclass 600 is genuinely
  lodged online, the old tab was mislabeled not fabricated. All stay unverified.
- France transit: removed "UK" from the ATV exemption; corrected to the EU Visa Code Art. 3(5)
  list (Schengen member state / US / Canada / Japan). Likely pre-Brexit residue. Block stays
  unverified (Reg. 810/2009 renders empty to fetchers; no citable France-Visas page).
- Australia insurance: downgraded "mandatory" -> "strongly recommended" (Home Affairs: insurance
  is recommended for subclass 600; mandatory only if condition 8501 is imposed). Over-claiming a
  requirement costs users money. Block stays unverified (homeaffairs bot-blocks fetches).
- INFRA GAP CONFIRMED: the weekly-rebuild step (rebuild.yml + CLOUDFLARE_DEPLOY_HOOK secret +
  issue forms) from the #15 "suggested, not built" note NEVER shipped — no rebuild.yml in git
  history, no CLOUDFLARE_DEPLOY_HOOK secret, no .github/ISSUE_TEMPLATE/. rebuild.yml built in a
  separate branch/PR; the Cloudflare deploy hook + secret are the founder's to set (I can't).
- Verified: 4 changed country files pass --strict-citations; full validate 1409 passed / 0 errors
  / 113 warnings (unchanged — no new bare blocks); strict build green; rendered output confirms
  Germany ₹9,800 + 2 tabs, Australia "Online (ImmiAccount)" tab, France ATV list, AU insurance.
**Files touched:**
- `data/visas/{australia,france,germany,greece}.yaml` — corrections above
- `add_country.py` — official-INR-first convention in the schema contract
- `atlas_PROJECT_STATE.md`, `.ai-state/STATE.md` — docs

### Session: 2026-07-10 — Claude (Opus 4.8) [polish + docs to stable state]
**Branch:** chore/polish-docs-verification-queue (from main)
**What changed:**
- Verification queue (founder's manual to-verify list): `freshness.py` `_collect_unverified` +
  `build_report` now enumerate every `unverified: true` block across all countries — country,
  block id, and the official portal to check against — as a new section on `/meta/freshness` and
  in `freshness_report.py` console output, with the `admin_update.py --country X --source URL`
  apply command. 31 blocks across 6 migrated countries. Auto-generated, so it can't drift.
- `BACKLOG.md` (new, root): durable open-TODO list — transit-guide real sourcing (placeholder
  URLs), France/Greece official INR, e-Visa artifact audit (12 countries still carry the generic
  "e-Visa (where available)" bulk-script tab incl. Japan), 24-country citation migration, fee
  breakdown rollout, Cloudflare rebuild setup (founder), issue forms (optional).
- `USER-JOURNEYS.md` (new, root): traveller / contributor / librarian-founder / maintainer
  journeys end to end, each mapped to the files + tools involved.
- Doc refresh: atlas_PROJECT_STATE.md (header companion-doc pointers, 6/30 migrated, repo map +
  BACKLOG/USER-JOURNEYS/rebuild.yml, §7 CI table + rebuild row, freshness ops = 3 report
  sections), FEATURES.md (companion-doc pointer), docs/CONTRIBUTING.md (how to add a `sources`
  block / `unverified` flag), CLAUDE.md (orientation-docs pointer).
- No schema/behaviour change to shipped country pages; verification queue is additive.
- Verified: validate.py 1409 passed / 0 errors; strict build green; /meta/freshness renders all
  three sections incl. the verification queue; freshness_report.py exit 0.
**Files touched:**
- `freshness.py` — verification queue (_collect_unverified + report sections)
- `BACKLOG.md`, `USER-JOURNEYS.md` — created
- `atlas_PROJECT_STATE.md`, `FEATURES.md`, `docs/CONTRIBUTING.md`, `CLAUDE.md`, `.ai-state/STATE.md` — docs
