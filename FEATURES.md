# Project Atlas — Features & Architecture

This is a living document that tracks the features implemented in Project Atlas, how they work under the hood, and the files that power them. We will update this file after each session as new features are built.

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
2. **Citation Requirement (`.github/PULL_REQUEST_TEMPLATE.md`)**: Contributors are forced to provide an official source/citation URL for their data correction.
3. **CI Validation (`.github/workflows/ci.yml`)**: On every Pull Request, GitHub Actions runs `mkdocs build --strict` to ensure the YAML is well-formed, and runs `htmlproofer` (ignoring certain bot-blocking government domains) to ensure no official embassy links are dead.
4. **Founder Review Gate (`.github/CODEOWNERS`)**: Requires `@shan8tanu` to personally review and approve every change to the `data/visas/` directory before GitHub allows the PR to be merged.
5. **Auto-Deploy (`.github/workflows/deploy.yml`)**: Once the founder approves and merges to `main`, this workflow automatically runs `mkdocs gh-deploy` to publish the updated site to GitHub Pages.

**Key Files:**
- `.github/workflows/ci.yml` — Pull Request validation (build + dead link checker).
- `.github/workflows/deploy.yml` — GitHub Pages deployment script.
- `.github/CODEOWNERS` — The approval gatekeeper.
- `.github/PULL_REQUEST_TEMPLATE.md` — The citation form for contributors.
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
