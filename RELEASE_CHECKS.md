# Release Checks — 2-minute founder click-through

**Required after ANY change to `templates/country.md.jinja`, `docs/javascripts/theme.js`,
or `docs/stylesheets/theme.css`** — no matter how small, no matter what CI says.

Why this exists: the occupation selector shipped 2026-03-15 and **never worked in
production until 2026-07-11** — every build was green the whole time. CI's rendered-DOM
tests (`tests/test_rendered_pages.py`) now pin the DOM mechanism, but only a human
clicking in a real browser proves end-to-end interactivity. This is that proof.

## The click-through (use /japan/ — the reference page)

Run `mkdocs serve`, open `http://127.0.0.1:8000/japan/` in a NORMAL browser window
(not a stale tab — hard-refresh, Ctrl+Shift+R):

- [ ] **Occupation pills switch documents.** Default shows *Salaried* items only.
      Click *Self-employed* → salaried items disappear, self-employed items (GST,
      CA-certified balance sheet…) appear. Click through all 6 pills — each shows a
      visibly DIFFERENT set of financial documents.
- [ ] **Visa-type tabs switch documents.** Click *e-Visa* → the standard-visa
      document rows swap for e-visa rows. First tab is active by default.
- [ ] **Checkbox persists.** Tick *Valid passport*, reload the page → still ticked,
      and your last-selected pill/tab is restored.
- [ ] **Fees table renders** with the computed "Total (mandatory): ₹…" line, and the
      overview card shows "₹X total (₹Y government fee)".
- [ ] **At least one Sources line and one amber Unverified caveat** are visible on
      the page (citations rendering intact).
- [ ] **Map loads**: open `/map/` — countries are coloured, hovering shows a tooltip,
      clicking Japan navigates to its page.

Then spot-check one UNMIGRATED page (e.g. `/thailand/`): pills and tabs still switch,
no Sources lines, page badge shows the "Last updated … · source citations being added"
fallback.

**Any box unticked = do not merge/deploy.** File the failure and fix first.
