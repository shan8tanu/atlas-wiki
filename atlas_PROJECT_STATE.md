# Atlas — Current State Snapshot

> **Point-in-time snapshot** of the whole repository, drafted 2026-07-08 after a full
> file-by-file review; last synced 2026-07-09 (citations + freshness systems merged, 4 new
> countries added). Unlike [`.ai-state/STATE.md`](.ai-state/STATE.md) (an append-only
> session log), this file is a *current* description of what exists today and is meant to be
> overwritten when it drifts. Where older docs disagree with the code, the code wins and the
> discrepancy is called out under **Known drift / cleanup candidates** at the bottom.

---

## Schema changelog

- **2026-07-09** — Freshness: new site-level `data/volatility.yaml` (`cadence_days` per citable
  block, check group I); country YAML gains optional per-block cadence override — `cadence_days`
  inside dict blocks / `visa_types.<key>`, or `<key>_cadence_days` parallel key for
  jurisdiction/exemptions (check H7).
- **2026-07-09** — Citations (PR #14): optional `sources` list (`url`/`tier` 1–3/`label`/
  `accessed`) + `unverified: true` on citable blocks; parallel `jurisdiction_sources`/
  `_unverified` + `exemptions_sources`/`_unverified` (check group H).

---

## 1. What Atlas is

A **static, citation-backed visa-requirements database for Indian passport holders** — the
"Wikipedia of Visas." Factual data lives in per-country YAML files; a build-time Python script
renders each file through a Jinja2 template into a virtual Markdown page. MkDocs + the Material
theme turn those pages into a static site.

- **Core principle:** *Content is downstream of data.* Never hand-edit country Markdown — edit
  the YAML (facts) or the Jinja template (layout).
- **Repo:** `github.com/shan8tanu/atlas-wiki` (branch `main`)
- **Deploy target:** Cloudflare Pages → https://atlas-wiki.pages.dev/
- **Coverage today:** 30 countries live on `main` (Sri Lanka, United Kingdom, Canada, and
  Maldives merged 2026-07-09 via the `add_country.py` pipeline — see §5).

---

## 2. Build pipeline (how a page is made)

```
data/visas/<country>.yaml            templates/country.md.jinja
        │                                     │
        └───────────────┐   ┌─────────────────┘
                        ▼   ▼
                     gen_pages.py         ← run by the mkdocs "gen-files" plugin at build time
                        │
       ┌────────────────┼─────────────────────────────┐
       ▼                ▼                             ▼
 virtual <country>.md   map-data.json (virtual)   guides/transit-visa-rules.md (virtual)
       │
       ▼
   mkdocs build ──► site/  (gitignored, deployed by Cloudflare)
```

- [`gen_pages.py`](gen_pages.py) loops every `data/visas/*.yaml`, computes a flag emoji from
  `iso_code` (`iso_to_flag`), renders the template, prepends `page_type: country` front matter,
  and writes the page **in memory** via `mkdocs_gen_files`. It also routes each page's
  "Edit this page" pencil to the YAML source (`set_edit_path`) and emits `map-data.json`.
- If [`data/transit/transit_rules.yaml`](data/transit/transit_rules.yaml) exists it also renders
  the Transit Visa Rules guide via [`templates/transit-guide.md.jinja`](templates/transit-guide.md.jinja).
- Config: [`mkdocs.yml`](mkdocs.yml). Local dev server: `python -m mkdocs serve` (see
  [`.claude/launch.json`](.claude/launch.json), port 8000).

---

## 3. Repository map (as of today)

```
atlas/
├── .ai-state/STATE.md            Append-only cross-agent session log
├── .ai_context.md                Founding vision / philosophy (historical)
├── .claude/launch.json           Dev server config (mkdocs serve :8000)
├── CLAUDE.md                     Claude Code project instructions
├── FEATURES.md                   Feature/architecture narrative (living doc)
├── atlas_PROJECT_STATE.md        ← THIS FILE (current-state snapshot)
├── mkdocs.yml                    Site config: theme, nav, plugins, CSS/JS
├── requirements.txt              mkdocs-material, mkdocs-gen-files, jinja2, pyyaml, anthropic
│
├── gen_pages.py                  Build engine: YAML → Jinja → virtual MD + map-data.json
│                                 + freshness context + /meta/freshness page
├── freshness.py                  Freshness engine: cadence policy, block states, page rollup,
│                                 git-date cache, report builder
├── freshness_report.py           CLI: librarian's re-verification queue (always exit 0)
├── validate.py                   CLI: structural YAML validation (checks A–I)
├── validate_accuracy.py          CLI: AI accuracy audit (needs ANTHROPIC_API_KEY)
├── admin_update.py               CLI: trusted-source YAML updates w/ diff + confirm
├── add_country.py                CLI: AI new-country pipeline (research→draft→validate→PR)
├── add_visa_types.py             One-shot migration (bulk-added visa_types)
├── add_occupation_docs.py        One-shot migration (bulk-added occupation_documents)
│
├── validate/                     Validation package
│   ├── checks.py                 Check groups A–I (structural → citations → volatility policy)
│   ├── schema.py                 Allowed values, ISO set, known processors, Indian states,
│   │                             CITABLE_BLOCKS, DIFFICULTY_LABELS
│   ├── report.py                 Colored terminal report renderer
│   └── claude_audit.py           Brave Search + Claude field-by-field comparison
│
├── data/
│   ├── visas/*.yaml              SOURCE OF TRUTH — 30 country files
│   ├── sources/*.yaml            Provenance sidecars for AI-drafted countries (4 files: canada,
│   │                             maldives, sri-lanka, united-kingdom) — not written for
│   │                             hand/legacy-authored countries
│   ├── volatility.yaml           Freshness cadence policy (validated by check I)
│   └── transit/transit_rules.yaml  6 airport hubs (FRA, CDG, LHR, DXB, SIN, IST)
│
├── templates/
│   ├── country.md.jinja          The template for all country pages
│   └── transit-guide.md.jinja    Transit guide template
│
├── docs/                         Hand-written pages + static assets
│   ├── index.md, map.md, CONTRIBUTING.md
│   ├── robots.txt, _headers      SEO + HTTP security headers (Cloudflare)
│   ├── assets/world-map.svg      179-country SVG; path ids = lowercase ISO alpha-2
│   ├── assets/images/favicon.svg
│   ├── javascripts/map.js        SVG coloring, tooltips, click-to-navigate
│   ├── javascripts/theme.js      Checklist persistence, occ/visa selectors, cover-letter copy, mini-map
│   ├── stylesheets/map.css       Map styling
│   ├── stylesheets/theme.css     Design system (light-only; dark mode removed)
│   ├── <country>.md × 26         ⚠ STALE committed build output — see §8 (the 4 countries added
│   │                             2026-07-09 never had this problem — gen-files only, no stale copy)
│   └── map-data.json             ⚠ STALE committed build output — see §8
│
├── overrides/main.html           Material override: hero + mini-map, page_type body class
│
└── .github/
    ├── PULL_REQUEST_TEMPLATE/     core_feature.md, data_correction.md
    └── workflows/
        ├── ci.yml                push: validate + strict build; PR: also htmlproofer
        ├── link-check.yml        Weekly Mon 06:00 UTC dead-link scan
        └── accuracy-audit.yml    Weekly Mon 07:00 UTC AI accuracy audit
```

---

## 4. Data schema (the YAML contract)

Enforced mechanically by `validate.py`. **Required** on every country file:

| Field | Notes |
|---|---|
| `country` | Must match filename slug when lowercased, spaces→hyphens (E7 guard) |
| `iso_code` | 2 uppercase letters, must be a real ISO 3166-1 alpha-2 code |
| `visa_difficulty` | int 1–5 (1 = easiest) |
| `visa_type` | one of `Standard Visa` \| `e-Visa` \| `Visa on Arrival` |
| `max_stay`, `region` | region ∈ Asia/Europe/Americas/Oceania/Middle East |
| `authority` | `.name`, `.processor`, `.official_portal` (HTTPS) |
| `requirements` | `.visa_fee_inr` (int≥0), `.processing_days` (int≥1), `.photo_specs.{dimensions,bg_color}`, `.financial_proof`, `.financial_documents` |
| `health` | `.vaccinations`, `.insurance`, `.notes` (each ≥20 chars) |

**Optional** blocks (rendered conditionally by the template, validated by check group G):
`entry_type`, `visa_validity`, `passport_validity_months`, `blank_pages_required`,
`visa_types` (tabbed doc lists; first tab must match `visa_type` — check E8),
`requirements.occupation_documents` (self_employed/business_owner/student/homemaker/retired),
`jurisdiction` (state→consulate), `transit`, `exemptions`, `ecr`, `biometrics`, `changelog`.

**Per-claim citations** (check group H): each "citable fact block" may carry a `sources` list
(`url` https deep-link · `tier` 1 govt / 2 processor / 3 secondary · `label` · `accessed`
YYYY-MM-DD) or an `unverified: true` flag. Citable blocks = `requirements`, `health`, each
`visa_types.<key>`, `transit`, `ecr`, `biometrics` (inline `sources`/`unverified`), plus
`jurisdiction` & `exemptions` (parallel `jurisdiction_sources`/`_unverified`,
`exemptions_sources`/`_unverified`, since a YAML list can't hold a sibling key). The registry is
`CITABLE_BLOCKS` in `validate/schema.py`, shared by validation and mirrored by the template.
Japan is the fully-migrated reference; the other 29 migrate later. Rendered as subtle tier-badged
"Sources" lines / an amber "Unverified" caveat by `templates/country.md.jinja`.

**Freshness system** (builds on citations): `data/volatility.yaml` maps each citable block to a
verification cadence (days); `freshness.py` computes per-block states at build time from the
newest `accessed` date (fresh ≤ cadence · aging ≤ 2× · overdue > 2×; unverified blocks exempt,
unsourced blocks silent). Per-block override: `cadence_days` inline (dict blocks) or
`<key>_cadence_days` (list blocks). `gen_pages.py` injects `_freshness`/`_page_freshness`/
`_difficulty_label` into the template: sources lines gain "re-checked every N days" (+ text state
label when aging/overdue), and the Visa Info card gains a Difficulty row (labels in
`DIFFICULTY_LABELS`, `validate/schema.py`) plus a worst-state-wins page badge (git-commit-date
"Last updated" fallback for unmigrated pages — never file mtime). Ops surface:
`freshness_report.py` (always exit 0, printed in CI) + virtual page `/meta/freshness`
(nav-hidden via `not_in_nav`). Wording rule: "verified" = cited source checked; "updated" = file
committed.

Full field-by-field intent lives in the `add_country.py` schema contract
([add_country.py](add_country.py) `_SCHEMA_CONTRACT`), which doubles as the human-readable spec.

---

## 5. Validation & safeguards

**Structural — [`validate.py`](validate.py) (no API keys, CI-safe).** Check groups:
- **A** parse / top-level dict · **B** required-field presence · **C** types · **D** value ranges
  & patterns (ISO set, HTTPS portal, allowed enums; unknown processor = *warning*) ·
  **E** exhaustiveness (min lengths, placeholder guard, `visa_type`↔first-tab, country↔filename) ·
  **F** cross-file (dup ISO/country, YAML↔nav parity; subdir `guides/` pages excluded) ·
  **G** optional feature blocks (changelog, jurisdiction, transit, exemptions, ecr, biometrics) ·
  **H** per-claim citations (source entry shape: fields present, https URL, tier ∈ {1,2,3},
  parseable `accessed` date; **H6** warns when a citable block has neither `sources` nor
  `unverified: true`; **H7** validates `cadence_days` overrides) ·
  **I** volatility policy (site-level, once: `data/volatility.yaml` exists, parses, covers every
  CITABLE_BLOCKS key, positive-int cadences).
- Exit 0 = pass (warnings allowed); exit 1 = errors. During the citation migration, group H emits
  H6 **warnings** for un-migrated countries (CI stays green). Pass **`--strict-citations`** to
  upgrade H6 to an error — flip CI to it once all 30 countries are migrated. Japan already passes
  strict. Current: 1403 checks, 0 errors, 143 warnings (up from 1219/129 pre-merge — the 4 new
  countries add unmigrated-citation warnings, expected during migration).
- Schema constants (allowed sets, ISO codes, `KNOWN_PROCESSORS` incl. VFS/BLS/TLScontact/CVASC/
  Direct, `KNOWN_INDIAN_STATES`, `ALLOWED_SOURCE_TIERS`, `CITABLE_BLOCKS`) live in
  [`validate/schema.py`](validate/schema.py).

**AI accuracy audit — [`validate_accuracy.py`](validate_accuracy.py).** Needs `ANTHROPIC_API_KEY`;
optional `BRAVE_SEARCH_API_KEY` (degrades to training-data-only). Fetches live web/portal context,
asks Claude (model `claude-haiku-4-5-20251001`) to grade 8 fields as PLAUSIBLE/SUSPECT/OUTDATED/
UNKNOWN, writes `validation-report.md` (gitignored). Exit 2 = attention needed. Runs weekly via
`accuracy-audit.yml`.

**Admin update — [`admin_update.py`](admin_update.py).** Fetches a trusted URL/text, asks Claude
(`claude-sonnet-4-6`) to update only affected fields, shows a colored diff, writes on confirmation.

**New-country pipeline — [`add_country.py`](add_country.py).** Brave research → Claude draft
(`claude-sonnet-4-6`, prompt-cached schema + japan.yaml gold example) → `validate.py` self-check
with one repair pass → mkdocs nav insert → optional branch/commit/push/PR via `gh`. Writes a
`data/sources/<slug>.yaml` provenance sidecar (web/pattern/unverified confidence per fact group)
and turns unverified fields into a PR verification checklist. Four countries drafted this way —
Sri Lanka, United Kingdom, Canada, Maldives — merged to `main` 2026-07-09 after PR review; their
sidecars now live in `data/sources/`. **None of the four have per-claim citations yet** (the
`sources`/`unverified` schema from §4 postdates their drafts) — they show up in the H6 warning
count and the `/meta/freshness` migration worklist alongside the other 25 legacy countries.

---

## 6. Frontend

Zero external JS libraries. Light mode only (dark mode intentionally removed 2026-04-12; fonts are
system stacks — Material's Google-Fonts loader is disabled via `font: false`).

- **Interactive map** — inline SVG in [`docs/map.md`](docs/map.md); [`map.js`](docs/javascripts/map.js)
  fetches `map-data.json`, colors `<path>` elements by `visa_difficulty`, does tooltips + click-nav.
- **Country page interactivity** — [`theme.js`](docs/javascripts/theme.js): localStorage checklist
  persistence, occupation + visa-type selectors, cover-letter copy button, homepage mini-map,
  IntersectionObserver reveal animations.
- **Theme/design system** — [`theme.css`](docs/stylesheets/theme.css) (tokens, cards, selectors,
  checklist, and the optional section styles) + [`map.css`](docs/stylesheets/map.css).
- **Hero + mini-map** — [`overrides/main.html`](overrides/main.html), which also sets a
  `page_type` body class for per-page-type CSS.

---

## 7. CI/CD & governance

| Workflow | Trigger | Does |
|---|---|---|
| [`ci.yml`](.github/workflows/ci.yml) | push to `main` + PRs | `validate.py` → `freshness_report.py` (informational, always exit 0) → `mkdocs build --strict`; **htmlproofer only on PRs** (a dead embassy link never blocks a push) |
| [`link-check.yml`](.github/workflows/link-check.yml) | Mon 06:00 UTC + manual | build + htmlproofer dead-link scan |
| [`accuracy-audit.yml`](.github/workflows/accuracy-audit.yml) | Mon 07:00 UTC + manual | `validate_accuracy.py` → report to job summary + 90-day artifact. Needs `ANTHROPIC_API_KEY` (+ `BRAVE_SEARCH_API_KEY`) repo secrets |

htmlproofer ignores a curated set of bot-blocking government/processor domains (kept in sync
between `ci.yml` and `link-check.yml`). Contribution flow: edit YAML on GitHub via the page pencil →
PR with a citation (templates in `.github/PULL_REQUEST_TEMPLATE/`) → maintainer review → merge →
Cloudflare redeploys. Contributor guide: [`docs/CONTRIBUTING.md`](docs/CONTRIBUTING.md).

**Branch protection** is a repo ruleset (not `.github/CODEOWNERS` — see §8), requiring the
`Build & Validate` status check to pass before merge. No required human-approval rule exists
today — any push-capable collaborator (including an authenticated agent) can merge once CI is
green. The `/meta/freshness` report page is the librarian's weekly re-verification queue (see
§4's freshness system); it's URL-only, excluded from nav via `not_in_nav` in `mkdocs.yml`.

---

## 8. Known drift / cleanup candidates

These are real mismatches found during this review — surfaced, not silently changed:

1. **Stale committed build output.** All 26 `docs/<country>.md` files and `docs/map-data.json` are
   committed (last touched 2026-03-01) but are **regenerated in memory** by `gen_pages.py` on every
   build. The virtual versions win, so the build is unaffected — but the on-disk copies are dead
   weight and contradict CLAUDE.md's "these files don't exist on disk." **Recommendation:** delete
   the 26 country `.md` files and `docs/map-data.json` from git (they're pure artifacts). Left in
   place for now because deletion is a founder call.
2. **`.github/CODEOWNERS` does not exist.** Both `FEATURES.md` and the old `.ai-state/STATE.md`
   folder tree describe it as the `data/visas/` approval gate. There is no such file in the repo
   today — merge protection is not enforced via CODEOWNERS. (Fixed the FEATURES.md reference in
   this session; STATE.md is append-only so it's noted in its session log instead.)
3. **`FEATURES.md` referenced a `deploy.yml` / GitHub Pages.** There is no deploy workflow —
   hosting is Cloudflare Pages, which builds on push. Corrected in this session.
4. ~~`data/sources/` is PR-branch-only~~ — **resolved 2026-07-09.** The 4 AI-drafted countries
   (Sri Lanka, UK, Canada, Maldives) merged to `main`, so their provenance sidecars now live in
   `data/sources/` on `main` too. Still true that hand/legacy-authored countries have no sidecar.
5. **Repo ruleset had a stale required-check name** (fixed 2026-07-09): it required a status check
   literally named "Build & Link Health Check", but that CI job was renamed to "Build & Validate"
   back in commit `0b8f9a5` and the ruleset was never updated — every PR was silently `BLOCKED`
   regardless of content. Updated the ruleset (`gh api` on ruleset id `13252933`) to require the
   real check name.

---

## 9. Quick command reference

```bash
python validate.py                       # structural checks (all countries)
python validate.py --file data/visas/japan.yaml
python -m mkdocs serve                    # local preview at :8000
python -m mkdocs build --strict           # full build into site/
python validate_accuracy.py --country japan          # AI audit (needs ANTHROPIC_API_KEY)
python admin_update.py --country japan --source "https://..."
python add_country.py --country "X" --iso XX --region Asia --pr --audit
```
