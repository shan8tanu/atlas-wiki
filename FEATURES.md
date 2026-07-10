# Project Atlas — Features & Architecture

This is a living document that tracks the features implemented in Project Atlas, how they work under the hood, and the files that power them. We will update this file after each session as new features are built.

> For a full, current file-by-file snapshot of the repository (validation, CLI tooling, CI/CD, and known drift), see [`atlas_PROJECT_STATE.md`](atlas_PROJECT_STATE.md). For how each role uses the site, see [`USER-JOURNEYS.md`](USER-JOURNEYS.md); for open TODOs, [`BACKLOG.md`](BACKLOG.md).

---

## 🏗️ Core Architecture: Data-Driven Static Generation

Project Atlas uses a strict "Content is Downstream of Data" philosophy built on top of MkDocs and Python. We do not write Markdown files for country pages; we write data, and the engine generates the pages.

### How it works
1. **The Source of Truth (`data/visas/*.yaml`)**: All factual visa data lives in structured, machine-readable YAML files.
2. **The Template (`templates/country.md.jinja`)**: The layout schema that dictates how the factual data is displayed on the page.
3. **The Engine (`gen_pages.py`)**: A Python script runs at build time. It intercepts MkDocs, loops through the YAML data, injects it into the Jinja2 template, and creates virtual Markdown pages entirely in memory using the `mkdocs-gen-files` plugin.

**Key Files:**
- `data/visas/*.yaml` — Factual data for each country.
- `templates/country.md.jinja` — View template with Schema.org JSON-LD SEO metadata.
- `gen_pages.py` — The generation engine.
- `mkdocs.yml` — The main site configuration.

---

## 🤝 Community Edit & CI/CD Pipeline

To prevent founder burnout, the platform relies on community audits ("Edit on GitHub" mechanism), guarded by a strict review pipeline so bad data never makes it to the live site.

### How it works
1. **Dynamic Edit Routing (`gen_pages.py`)**: The MkDocs pencil icon (defined in `mkdocs.yml` via `content.action.edit`) is dynamically routed directly to the `data/visas/<country>.yaml` file on GitHub via `mkdocs_gen_files.set_edit_path()`. Contributors edit raw data, not UI code.
2. **Structural Validation (`validate.py`)**: Before anything is built, `validate.py` runs check groups A–I over the YAML (required fields, types, value ranges, cross-file parity, optional feature blocks, per-claim citations, volatility policy) and fails the pipeline on any error.
3. **Citation Requirement (`.github/PULL_REQUEST_TEMPLATE/`)**: The `data_correction.md` and `core_feature.md` PR templates force contributors to provide an official source/citation URL for their change.
4. **CI Validation (`.github/workflows/ci.yml`)**: On every push and Pull Request, GitHub Actions runs `validate.py` then `mkdocs build --strict`. On Pull Requests it additionally runs `htmlproofer` (ignoring certain bot-blocking government domains) to ensure no official embassy links are dead. htmlproofer is deliberately skipped on direct pushes so a dead portal never blocks an unrelated change.
5. **Ongoing link + accuracy monitoring**: `.github/workflows/link-check.yml` (weekly) re-scans all official links, and `.github/workflows/accuracy-audit.yml` (weekly) runs the AI accuracy audit.
6. **Deploy**: The site is hosted on **Cloudflare Pages** (https://atlas-wiki.pages.dev/), which builds and publishes automatically when `main` updates. There is no in-repo deploy workflow.

> **Note:** An earlier draft of this doc described a `.github/CODEOWNERS` approval gate and a `.github/workflows/deploy.yml` GitHub Pages deploy. Neither file exists in the repository today — see the "Known drift" section of [`atlas_PROJECT_STATE.md`](atlas_PROJECT_STATE.md).

**Key Files:**
- `validate.py` + `validate/` — Structural validation (checks A–I).
- `.github/workflows/ci.yml` — Push/PR validation (validate + strict build + PR-only dead-link check).
- `.github/workflows/link-check.yml` — Weekly dead-link scan.
- `.github/workflows/accuracy-audit.yml` — Weekly AI accuracy audit.
- `.github/PULL_REQUEST_TEMPLATE/` — The citation forms for contributors.
- `docs/CONTRIBUTING.md` — The plain-English guide for non-technical users.

---

## 🗺️ Interactive SVG World Map

An inline, vanilla JavaScript-driven SVG world map located at `/map/`. It visualizes visa difficulty with zero external library dependencies and a tiny (~25 KB) payload footprint.

### How it works
1. **Data Collection (`gen_pages.py`)**: As the engine loops through the YAML files to generate the country pages, it also extracts the `iso_code`, `country` name, and `visa_difficulty` tier. This data is dumped into a `map-data.json` file during the build.
2. **The SVG Base (`docs/assets/world-map.svg`)**: A 73 KB SVG map featuring 179 countries where every `<path>` element's `id` perfectly matches the country's lowercase ISO alpha-2 code.
3. **The JS Engine (`docs/javascripts/map.js`)**: Fetches the generated `map-data.json`, matches the ISO codes to the SVG `<path>` IDs, and injects colors based on the `visa_difficulty` tier. It also powers the hover tooltips and click-to-navigate logic (falling back to a "Coming Soon" tooltip for countries without data yet).
4. **The UI (`docs/map.md` & `docs/stylesheets/map.css`)**: The full-width Map page that houses the inline SVG, the tooltip container, the 6-item color legend, responsive layout rules, hover effects, and dark mode support.

**Key Files:**
- `docs/assets/world-map.svg` — The baseline SVG file.
- `docs/map.md` — The page that displays the map and legends layout.
- `docs/javascripts/map.js` — The logic for coloring, tooltips, and click navigation.
- `docs/stylesheets/map.css` — Styling for hover effects, tooltips, and SVG sizing.
- `gen_pages.py` — Extracts data to generate `map-data.json`.
- `data/visas/*.yaml` — The source for `visa_difficulty` tracking.

---

## 🔎 Per-Claim Citations ("Trust, but Verify" on the page)

Every major fact block on a country page can display its provenance: a source link, an authority
tier, and the date it was checked — or an explicit "unverified" caveat when no official source is
confirmed. This turns the site's core promise into something a reader can see and audit.

### How it works
1. **Schema**: each citable fact block (`requirements`, `health`, every `visa_types.<key>`,
   `transit`, `ecr`, `biometrics`) carries an optional `sources` list — each entry has `url`
   (https deep link), `tier` (1 = govt/embassy, 2 = VFS/BLS/TLS, 3 = verified secondary), `label`,
   and `accessed` (YYYY-MM-DD). The list-shaped blocks use parallel keys
   (`jurisdiction_sources`, `exemptions_sources`). Any block may instead be flagged
   `unverified: true`. The block registry is `CITABLE_BLOCKS` in `validate/schema.py`.
2. **Rendering (`templates/country.md.jinja`)**: a `cite()` macro emits a compact, Wikipedia-style
   "Sources" line (tier pill + linked label + access date) under each block, or a visually
   distinct amber "Unverified / Community-Reported" caveat whose "Report it →" link opens a
   prefilled GitHub issue. Blocks with neither render nothing, so un-migrated pages are unchanged.
3. **Validation (check group H)**: `validate.py` verifies every source entry's shape and warns
   when a citable block has no citation. `python validate.py --strict-citations` upgrades that
   warning to a failure — the switch that will gate CI once all countries are migrated.

**Key Files:**
- `validate/schema.py` — `CITABLE_BLOCKS`, `ALLOWED_SOURCE_TIERS`, source-field contract.
- `validate/checks.py` — `check_h` (groups H1–H7).
- `templates/country.md.jinja` — the `cite()` macro and per-block call sites.
- `docs/stylesheets/theme.css` — §23 source-line + unverified-caveat styles.
- `data/visas/japan.yaml` — the fully-migrated reference country.
- `add_country.py` — new-country drafts now emit the `sources` structure from provenance.

---

## ⏳ Volatility-Based Freshness (re-verification system)

Cited facts age. Every citable block's `accessed` dates are compared against a site-level
cadence policy at build time, producing a per-block state — **fresh / aging / overdue** — shown
on the page and queued for the librarian.

### How it works
1. **Policy (`data/volatility.yaml`)**: one cadence (days) per citable block type — e.g.
   requirements 30, visa_types 45, health/transit/jurisdiction/exemptions 90, ecr/biometrics 180.
   Countries may override per block (`cadence_days` / `<key>_cadence_days`). Check group **I**
   fails validation if any CITABLE_BLOCKS key lacks a cadence, so the policy stays complete.
2. **Engine (`freshness.py`)**: at build time, age = today − newest `accessed`; fresh ≤ cadence,
   aging ≤ 2×, overdue > 2×. Unverified blocks are exempt; unsourced blocks silent. Page rollup
   is worst-state-wins.
3. **Rendering**: sources lines gain "· re-checked every N days" plus a text state label when
   aging/overdue (state always in text, color only reinforces). The Visa Info card gains a
   Difficulty row (1–5 labels shared with the map) and a page badge — "Facts verified on
   schedule / Some facts due / Some facts overdue · <latest date>". Unmigrated pages instead show
   "Last updated <git commit date> · source citations being added" ("verified" = source checked;
   "updated" = file committed — never mixed).
4. **Ops surface**: `freshness_report.py` prints the aging/overdue queue + a migration worklist
   (oldest-commit first) in CI on every run (informational, always exit 0); the same report is
   published at `/meta/freshness` (URL-only, hidden from nav via `not_in_nav`).

**Key Files:**
- `data/volatility.yaml` — the cadence policy.
- `freshness.py` — states, rollup, git-date cache, report builder.
- `freshness_report.py` — CLI wrapper (CI step in `ci.yml`).
- `gen_pages.py` — injects `_freshness` / `_page_freshness` / `_difficulty_label`; emits `/meta/freshness`.
- `validate/checks.py` — H7 (cadence overrides) + `check_i` (policy completeness).

---

## 📰 Site-Wide Change Log + RSS Feed

Every per-country `changelog` entry, aggregated into one reverse-chronological page at `/changes/`
(in the nav) and an RSS 2.0 feed at `/changes.xml` — so returning users and feed readers can see
what changed across the whole wiki without visiting every country page.

### How it works
1. **Collection (`gen_pages.py`)**: while looping country YAMLs it gathers each changelog entry as
   (date, country, slug, type, description, source). Unparseable dates get a named build warning
   and are excluded — never a crash.
2. **Page (`templates/changes.md.jinja`)**: entries grouped by month ("July 2026"), newest first;
   each row reuses the existing changelog tag pills and links to the country page and the official
   source. Shows all entries.
3. **Feed**: hand-built RSS 2.0 (XML-escaped, RFC 822 dates via `email.utils` — locale-proof),
   capped at the 50 newest items; item links point to each country's `#change-log` anchor,
   `guid = slug+date+index`. Channel URLs come from `site_url` in `mkdocs.yml`. Autodiscovery
   `<link rel="alternate">` on every page via `overrides/main.html`.
4. **Trustworthy inputs**: checks **G10–G12** now enforce parseable dates, non-empty descriptions,
   and https sources on changelog entries.

**Key Files:**
- `gen_pages.py` — collection + page + feed emission (bottom section).
- `templates/changes.md.jinja` — the page template.
- `overrides/main.html` — RSS autodiscovery link.
- `validate/checks.py` — G10–G12.

---

## 💰 Fee Breakdown (what it really costs)

The #1 user question — "what will this really cost, total?" — answered with a per-component fee
table instead of a single number, while every un-migrated page keeps working unchanged.

### How it works
1. **Schema**: optional `requirements.fees.components` — each component has `label`,
   `amount_inr`, `mandatory`, `refundable` (+ optional `note`). Exactly one component carries
   `is_government_fee: true` and its amount must equal the still-required legacy
   `visa_fee_inr` (which is now unambiguously the GOVERNMENT fee — the single-number fallback
   for the map, overview card, and accuracy audit). Optional `child_fee_inr`,
   `payment_methods`, `fee_last_revised`.
2. **Validation (group J)**: J1 structure/types · J2 non-negative amounts · J3 exactly one
   government component · J4 it equals `visa_fee_inr` · J5 `fee_last_revised` parses ·
   J6 at least one mandatory component.
3. **Rendering**: totals are **computed at build time** (`compute_fees` in `gen_pages.py`),
   never stored. Migrated pages get a `## Fees` table (tabular-numeral amounts,
   mandatory/optional + refundable flags, notes), a computed
   "Total (mandatory): ₹X · with all optional services: ₹Y" line, an upgraded overview row
   ("₹X total (₹govt government fee)"), and a checklist fee item showing the mandatory total.
   Countries without `fees` render byte-identically to before.
4. **Reference migration**: Japan — all three components (govt ₹500, VFS service charge ₹800,
   optional courier ₹550) verified against the VFS Global one-pager already cited in its
   `requirements.sources`.

**Key Files:**
- `validate/checks.py` — `check_j` (J1–J6).
- `gen_pages.py` — `compute_fees` + `_fees` context injection.
- `templates/country.md.jinja` — Fees section, overview row, checklist line.
- `docs/stylesheets/theme.css` — §24 fee table styles.
- `data/visas/japan.yaml` — reference migration.
- `add_country.py` — schema contract now scaffolds `fees` for new countries.
