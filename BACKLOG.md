# Atlas — Backlog / Open TODOs

Tracked work that's deliberately deferred, newest concerns first. Each item says **why it's open**
and **what "done" looks like**. Data-accuracy items go through founder review (no silent edits).
For the live, always-current list of blocks needing a source, see **/meta/freshness** (the
Verification queue section) — this file is for the larger, non-mechanical items.

---

## Data accuracy

### 1. Transit Guide sources are placeholders
**Why:** every hub in [`data/transit/transit_rules.yaml`](data/transit/transit_rules.yaml) cites
`https://placeholder.example.com/...` — sample data from the guide's first build, never verified
against an official source. The Frankfurt/CDG airport-transit-visa lists are now *correct in
content* (UK removed post-Brexit, 2026-07-10) but still *unsourced*.
**Done when:** each of the 6 hubs (FRA, CDG, LHR, DXB, SIN, IST) has a real official source URL
(Schengen: EU Commission / national MFA; UK: gov.uk DATV; UAE: GDRFA; Singapore: ICA) and a real
`last_verified` date. CI htmlproofer already ignores `placeholder.example.com` — remove that
ignore rule once real URLs land.

### 2. France & Greece official INR fee (official-INR-first)
**Why:** both store `visa_fee_inr: 7200`, a stale €90 conversion. The official-INR-first
convention (see `add_country.py` contract) wants the consulate's own published INR (Germany's is
9,800 for the same €90), but france-visas.gouv.fr / mfa.gr / VFS bot-block automated fetches.
Marked with `TODO(official-INR-first)` comments in each YAML.
**Done when:** a human reads the French/Greek consulate (or their VFS India) fee schedule and sets
the official INR + a `sources` entry.

### 3. e-Visa artifact tabs — audit all countries
**Why:** the `add_visa_types.py` bulk script gave every original country a generic
`evisa: "e-Visa (where available)"` tab. **12 still have it** (china, italy, japan, netherlands,
new-zealand, philippines, singapore, south-korea, spain, switzerland, uae, united-states). Several
are certainly fabrications (Schengen Italy/Netherlands/Spain/Switzerland, USA, Japan have no
tourist e-Visa for Indians); a few may be real (verify China / UAE / Singapore e-Visa products).
Precedent: Brazil's fake tab was deleted (2026-07-02); FR/DE/GR deleted + Australia relabelled
(2026-07-10).
**Done when:** each of the 12 is either deleted (no such product) or relabelled to the real route,
per-country verified.

---

## Migration (mechanical, batched)

### 4. Per-claim citation migration — 24 countries remain
**Why:** 6 of 30 countries are migrated (Japan + batch 1: Australia, Cambodia, France, Germany,
Greece). The rest render the git-date "source citations being added" badge.
**Done when:** every citable block is cited or honestly `unverified`. Work in batches of ~5 by
`/meta/freshness` worklist order (oldest git date first). EU Commission pages are the reliable
citable source for the remaining Schengen countries (Italy, Spain, Netherlands, Switzerland).
Flip CI to `validate.py --strict-citations` once all 30 pass.

### 5. Fee breakdown (`requirements.fees`) rollout
**Why:** only Japan has a `fees` component breakdown (group J). The other 29 show the single
`visa_fee_inr`.
**Done when:** each country has a `fees` block sourced from its mission/VFS fee schedule (VFS
one-pagers are the richest single source). **Special case:** United Kingdom's `visa_fee_inr` is a
bundled total by the old convention — migrating UK means splitting it into government + VFS
components and resetting `visa_fee_inr` to the government fee (J4 will enforce it).

---

## Infrastructure

### 6. Cloudflare weekly-rebuild setup — FOUNDER ACTION
**Why:** [`rebuild.yml`](.github/workflows/rebuild.yml) is merged but **inert** — it needs a
Cloudflare Pages deploy hook + the `CLOUDFLARE_DEPLOY_HOOK` repo secret. Until then, freshness
badges silently go stale during push-less weeks.
**Done when:** (1) create the deploy hook in Cloudflare (Workers & Pages → atlas-wiki → Settings →
Builds & deployments → Deploy hooks, branch `main`); (2) `gh secret set CLOUDFLARE_DEPLOY_HOOK`;
(3) smoke-test via Actions → Weekly Rebuild → Run workflow.

### 7. Structured issue forms for citation reports (optional)
**Why:** the unverified-caveat "Report it →" links open a *prefilled plain issue*
(`issues/new?title=…&body=…`), which works but is unstructured. There is no
`.github/ISSUE_TEMPLATE/`.
**Done when:** (if wanted) a GitHub issue *form* (`.github/ISSUE_TEMPLATE/citation-report.yml`)
with fields for country, section, official URL, and note — and the caveat link points at it.
