# Atlas — Claude Code Instructions

## First: Read the State File

Before doing anything, read `.ai-state/STATE.md`. It contains the current folder structure, feature registry, and a log of what every previous session changed. This saves you from re-exploring the codebase.

**Orientation docs:** `atlas_PROJECT_STATE.md` (current-state snapshot: schema, check groups A–J, CLI tools) · `USER-JOURNEYS.md` (who does what) · `BACKLOG.md` (open TODOs) · `/meta/freshness` page (live list of blocks needing a source). Data corrections go through the founder — surface discrepancies in the PR, don't silently "fix" data.

## After Every Session: Update the State File

At the end of your session, append a new entry to the **Session Log** section in `.ai-state/STATE.md`. Follow the format documented in that file. Never rewrite or delete existing entries.

## Core Rules

1. **Never edit generated Markdown.** Country pages like `docs/japan.md` don't exist on disk — they're generated in-memory by `gen_pages.py`. All factual changes go in `data/visas/*.yaml`. All layout changes go in `templates/country.md.jinja`.

2. **YAML is the source of truth.** The `data/visas/` folder is the database. Every country's visa data lives there.

3. **Run `python validate.py` after editing YAML.** This catches structural errors before they break the build.

4. **Use `mkdocs serve` for local preview.** The dev server config is in `.claude/launch.json` (port 8000).

5. **Don't commit `site/` or `docs-internal/`.** Both are gitignored. `site/` is auto-generated; `docs-internal/` is local documentation.

## Session close-out
Before ending any session that changed code or data:
1. Update atlas_PROJECT_STATE.md: what changed, new/changed schema fields,
   new validate.py check groups, open TODOs.
2. If the country YAML schema changed, note the change at the top of
   atlas_PROJECT_STATE.md under "## Schema changelog" with the date.
3. If the session touched `templates/country.md.jinja`, `docs/javascripts/theme.js`,
   or `docs/stylesheets/theme.css`: the founder MUST run the 2-minute
   click-through in `RELEASE_CHECKS.md` before deploy — flag this
   requirement prominently in the PR. (The occupation selector shipped
   broken for 4 months with green builds; rendered-DOM tests in CI catch
   the mechanism, only a human click-through proves the behavior.)
4. Commit and push.
