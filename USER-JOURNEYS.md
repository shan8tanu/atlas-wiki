# Atlas — User Journeys

Who uses Atlas and how, end to end. Four roles: the **Traveller** (the reader we exist for), the
**Contributor** (anyone who spots a mistake), the **Librarian/Founder** (keeps data honest), and
the **Maintainer** (extends the system). Each journey names the files and tools involved so the
"who does what" maps onto the architecture in [`atlas_PROJECT_STATE.md`](atlas_PROJECT_STATE.md).

---

## 1. Traveller — "Do I need a visa, what does it cost, can I trust this?"

1. **Arrives** on the site (SEO/search or the [interactive map](docs/map.md)) and opens their
   destination's country page (e.g. `/japan/`). The map colours each country by `visa_difficulty`
   so they can browse by how hard a visa is.
2. **Gets the 5-second answer** from the Visa Info card at the top: visa type, difficulty, max
   stay, **fee** (for migrated countries, "₹X total (₹Y government fee)" with the per-component
   breakdown below), processing time, and a **freshness badge** — "Facts verified on schedule /
   … some sections pending citation", or "Last updated <date> · source citations being added" for
   pages not yet migrated.
3. **Builds their document checklist**: picks their visa type (tabs) and occupation (Salaried /
   Self-employed / Business owner / Student / Homemaker / Retired). The checklist persists in
   `localStorage`, so ticks survive a refresh.
4. **Copies the cover-letter template** (one click) and reads the health, transit, ECR,
   biometrics, and where-to-apply sections where present.
5. **Verifies trust**: each fact block shows a subtle **Sources** line — a tier badge (T1 govt /
   T2 processor / T3 secondary), the linked source, and the access date — or an amber
   **"Unverified / Community-Reported"** caveat when no official source is confirmed. The promise
   is *Trust, but Verify*: every number is either cited or honestly flagged.

**Touches:** `templates/country.md.jinja` (rendering), `docs/javascripts/theme.js` (checklist,
selectors, cover-letter copy), `docs/javascripts/map.js` (map). Zero external JS.

---

## 2. Contributor — "This fee is wrong / here's the official source"

1. Spots a mistake on a country page and clicks the **"Edit this page" pencil**, which routes
   (via `gen_pages.py` `set_edit_path`) straight to the country's `data/visas/<slug>.yaml` on
   GitHub — never the generated Markdown.
2. Edits the YAML (fixes the value, or adds/updates a `sources` entry) and opens a PR. The PR
   templates (`.github/PULL_REQUEST_TEMPLATE/`) **require an official source URL** — PRs without a
   citation are closed.
3. **CI runs automatically** (`.github/workflows/ci.yml`): `validate.py` (structural checks A–J) →
   `mkdocs build --strict` → htmlproofer (dead-link check, PRs only). A malformed source, a fee
   that isn't an integer, or a broken template fails the check.
4. The maintainer reviews, merges to `main`, and Cloudflare Pages redeploys. Plain-English guide:
   [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md).

**Touches:** `data/visas/*.yaml` (the only thing a contributor edits), `validate/`, `ci.yml`.

---

## 3. Librarian / Founder — "Keep the data honest over time"

1. **Works the queue.** Opens `/meta/freshness` (URL-only, not in nav) or reads the "Freshness
   report" step in any CI run — same content. Three sections, worst-first:
   - **Blocks needing re-verification** — cited facts whose `accessed` date has aged past the
     `data/volatility.yaml` cadence (aging / overdue).
   - **Citation migration worklist** — countries with blocks still lacking citations, oldest git
     date first.
   - **Verification queue** — every block flagged `unverified`, with the official portal to check
     against.
2. **Verifies a fact**: opens the portal, confirms the number, then either edits the block's
   `sources` list by hand, or runs
   `python admin_update.py --country <slug> --source <official-url>` — which fetches the source,
   proposes a YAML diff, and writes only on confirmation.
3. **Optional second opinion**: the weekly AI accuracy audit
   (`validate_accuracy.py` / `accuracy-audit.yml`) grades 8 fields per country as
   PLAUSIBLE / SUSPECT / OUTDATED and posts a report — a prompt for where to look, not a source of
   truth.
4. **Keeps badges honest during quiet weeks**: the weekly rebuild (`rebuild.yml`) re-runs the
   build so freshness recomputes even without pushes (see [`BACKLOG.md`](BACKLOG.md) #6 — needs
   one-time Cloudflare setup).

**Touches:** `freshness.py` / `freshness_report.py` / `/meta/freshness`, `admin_update.py`,
`validate_accuracy.py`, `data/volatility.yaml`.

---

## 4. Maintainer — "Add a country / extend the schema"

1. **Add a country** with the AI pipeline:
   `python add_country.py --country "X" --iso XX --region Asia --pr --audit` — researches (Brave),
   drafts a schema-compliant YAML + a `data/sources/<slug>.yaml` provenance sidecar (Claude,
   prompt-cached against `japan.yaml`), self-checks with `validate.py`, inserts the mkdocs nav
   entry, and opens a PR whose body turns every unsourced field into a verification checklist.
   The draft follows the schema contract in `add_country.py` `_SCHEMA_CONTRACT` (the human-readable
   spec: government-fee-only `visa_fee_inr`, official-INR-first, `fees` breakdown, per-claim
   citations).
2. **Extend the schema**: add the field to `templates/country.md.jinja` (conditional block so
   un-migrated pages are unchanged), a validation check group in `validate/checks.py`, and — if
   it's a new citable block — the `CITABLE_BLOCKS` registry + `data/volatility.yaml` cadence
   (check I fails if a block has no cadence). Document it in `atlas_PROJECT_STATE.md`'s Schema
   changelog and append a `.ai-state/STATE.md` session entry (see `CLAUDE.md` close-out rules).
3. **Ship**: branch → `validate.py` + `mkdocs build --strict` → PR. Deep architecture reference:
   `docs-internal/` (local-only).

**Touches:** `add_country.py`, `templates/`, `validate/`, `data/`, the doc set.
