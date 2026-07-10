"""
freshness.py — volatility-based freshness computation for Atlas.

Shared by gen_pages.py (per-block freshness + page rollup injected into the
country template, and the virtual /meta/freshness page) and by
freshness_report.py (console report for CI / the librarian).

Policy lives in data/volatility.yaml (validated by check group I). Per-block
state is derived from the newest `accessed` date among a block's sources:

    fresh    age <= cadence
    aging    cadence < age <= 2 * cadence
    overdue  age > 2 * cadence

Blocks flagged `unverified: true` are exempt (their caveat already communicates
status). Blocks with no sources produce no freshness output at all.

Wording rule used everywhere downstream:
  "verified" = a cited source was checked (an `accessed` date exists)
  "updated"  = the YAML file was committed (git date) — never mixed.
"""

import os
import subprocess
from datetime import date, datetime

import yaml

from validate.checks import _iter_present_citable_blocks
from validate.schema import SOURCE_DATE_FORMAT

VOLATILITY_PATH = os.path.join("data", "volatility.yaml")
DATA_DIR = os.path.join("data", "visas")

STATE_RANK = {"fresh": 0, "aging": 1, "overdue": 2}


def load_volatility(path: str = VOLATILITY_PATH) -> dict:
    """Load the cadence policy. Raises on missing/malformed file."""
    with open(path, encoding="utf-8") as fh:
        vol = yaml.safe_load(fh)
    cadences = vol.get("cadence_days") if isinstance(vol, dict) else None
    if not isinstance(cadences, dict):
        raise ValueError(f"{path} must contain a `cadence_days` dict")
    return cadences


def _parse_date(value) -> date:
    return datetime.strptime(str(value), SOURCE_DATE_FORMAT).date()


def block_freshness(data: dict, cadences: dict, today: date | None = None) -> dict:
    """
    Compute freshness for every sourced citable block in one country.
    Returns {block_id: {state, cadence, last_accessed, age, label}} keyed by the
    same block ids check_h uses (e.g. "requirements", "visa_types.evisa").
    """
    today = today or date.today()
    out = {}

    for block_id, label, sources, unverified, override in _iter_present_citable_blocks(data):
        if unverified is True:
            continue  # exempt — the unverified caveat carries the status
        if not isinstance(sources, list) or not sources:
            continue  # unmigrated block — no freshness output

        accessed_dates = []
        for src in sources:
            if isinstance(src, dict) and src.get("accessed") is not None:
                try:
                    accessed_dates.append(_parse_date(src["accessed"]))
                except ValueError:
                    pass  # malformed dates are check H5's job, not ours
        if not accessed_dates:
            continue

        base_key = block_id.split(".", 1)[0]
        if isinstance(override, int) and not isinstance(override, bool) and override > 0:
            cadence = override
        else:
            cadence = cadences.get(base_key)
        if not isinstance(cadence, int) or cadence < 1:
            continue  # policy gap — check I reports it; stay safe here

        last = max(accessed_dates)
        age = (today - last).days
        if age <= cadence:
            state = "fresh"
        elif age <= 2 * cadence:
            state = "aging"
        else:
            state = "overdue"

        out[block_id] = {
            "state": state,
            "cadence": cadence,
            "last_accessed": last.isoformat(),
            "age": age,
            "label": label,
        }

    return out


def page_rollup(freshness: dict, data: dict) -> dict:
    """
    Page-level summary: worst-state-wins across sourced blocks, the most recent
    accessed date on the page, and a `pending` flag.

    `pending` is True when any present citable block has no `sources` yet —
    whether it's bare (never triaged) OR flagged `unverified: true` (triaged but
    not yet confirmed against an official source). Both still need real-source
    work, so both keep the page badge honest ("… some sections pending citation")
    and keep the country on the migration worklist. (Treating `unverified` as
    "done" previously let an all-unverified country — e.g. one whose every portal
    bot-blocks fetches — silently drop off the worklist with zero real sources.)

    state is None when the page has no sourced blocks at all (fully unmigrated,
    or only unverified blocks): no verified dates exist, so callers fall back
    to the git "Last updated" line.
    """
    pending = any(
        not (isinstance(sources, list) and sources)
        for _, _, sources, _unverified, _ in _iter_present_citable_blocks(data)
    )
    if not freshness:
        return {"state": None, "latest_accessed": None, "pending": pending}

    worst = max((f["state"] for f in freshness.values()), key=STATE_RANK.__getitem__)
    latest = max(f["last_accessed"] for f in freshness.values())
    return {"state": worst, "latest_accessed": latest, "pending": pending}


def git_last_commit_dates(data_dir: str = DATA_DIR) -> dict:
    """
    ONE git call for the whole data dir → {basename: "YYYY-MM-DD"} of each
    file's most recent commit. Returns {} when git history is unavailable
    (callers must then omit the "Last updated" line — never use file mtime).
    """
    try:
        proc = subprocess.run(
            ["git", "log", "--pretty=format:COMMIT %cs", "--name-only", "--", data_dir],
            capture_output=True, text=True, check=True,
        )
    except Exception:
        return {}

    dates: dict = {}
    current = None
    for line in proc.stdout.splitlines():
        if line.startswith("COMMIT "):
            current = line[len("COMMIT "):].strip()
        elif line.strip() and current:
            name = os.path.basename(line.strip())
            dates.setdefault(name, current)  # log is newest-first
    return dates


# ── Report building (console + /meta/freshness page) ─────────────────────────

def _collect(countries: dict, cadences: dict, today: date | None = None):
    """
    countries: {filename: parsed_yaml}. Returns (attention_rows, worklist_rows).
    attention_rows: aging/overdue blocks, worst-first then oldest-first.
    worklist_rows: unmigrated/partial countries, oldest git-commit-date first.
    """
    attention = []
    worklist = []

    for filename in sorted(countries):
        data = countries[filename]
        name = data.get("country", filename)
        fresh = block_freshness(data, cadences, today)
        roll = page_rollup(fresh, data)

        for block_id, f in fresh.items():
            if f["state"] in ("aging", "overdue"):
                attention.append({
                    "country": name, "block": block_id, "state": f["state"],
                    "age": f["age"], "cadence": f["cadence"],
                    "last_accessed": f["last_accessed"],
                })

        if roll["pending"]:
            sourced = len(fresh)
            unverified_any = any(
                unv is True
                for _, _, _, unv, _ in _iter_present_citable_blocks(data)
            )
            # partial = at least one block already migrated (sourced or unverified);
            # unmigrated = nothing migrated at all
            worklist.append({
                "country": name, "file": filename,
                "status": "partial" if (sourced or unverified_any) else "unmigrated",
                "sourced_blocks": sourced,
            })

    attention.sort(key=lambda r: (-STATE_RANK[r["state"]], -r["age"]))
    return attention, worklist


def _collect_unverified(countries: dict):
    """
    Every block flagged `unverified: true` across all countries — the human
    verification queue. Returns rows {country, slug, block, label, portal},
    sorted by country then block. `portal` is where to check the fact.
    """
    rows = []
    for filename in sorted(countries):
        data = countries[filename]
        name = data.get("country", filename)
        slug = os.path.splitext(filename)[0]
        portal = ((data.get("authority") or {}).get("official_portal")) or "—"
        for block_id, label, _sources, unverified, _c in _iter_present_citable_blocks(data):
            if unverified is True:
                rows.append({"country": name, "slug": slug, "block": block_id,
                             "label": label, "portal": portal})
    return rows


def build_report(countries: dict, cadences: dict, git_dates: dict,
                 today: date | None = None) -> tuple[str, str]:
    """Returns (console_text, markdown_page) for the freshness report."""
    today = today or date.today()
    attention, worklist = _collect(countries, cadences, today)
    worklist.sort(key=lambda r: git_dates.get(r["file"], "0000-00-00"))
    unverified = _collect_unverified(countries)

    # ── Console (ASCII-only: must not crash cp1252 Windows terminals) ────────
    lines = [f"Atlas Freshness Report — {today.isoformat()}".replace("—", "-"),
             "-" * 72]
    if attention:
        lines.append(f"{'STATE':<8} {'AGE':>4} {'CADENCE':>8}  {'VERIFIED':<12} COUNTRY / BLOCK")
        for r in attention:
            lines.append(f"{r['state']:<8} {r['age']:>4} {r['cadence']:>7}d  "
                         f"{r['last_accessed']:<12} {r['country']} / {r['block']}")
    else:
        lines.append("No aging or overdue blocks - all cited facts are within schedule.")
    lines.append("")
    lines.append(f"Migration worklist ({len(worklist)} countries, oldest update first):")
    for r in worklist:
        gd = git_dates.get(r["file"], "unknown")
        lines.append(f"  {gd}  {r['country']:<15} {r['status']}"
                     f" ({r['sourced_blocks']} sourced block(s))")
    lines.append("")
    lines.append(f"Verification queue ({len(unverified)} blocks flagged unverified, "
                 f"need a human + official source):")
    for r in unverified:
        lines.append(f"  {r['country']:<15} {r['block']}")
    console = "\n".join(lines)

    # ── Markdown page (/meta/freshness) ───────────────────────────────────────
    md = [
        "# Data Freshness Report",
        "",
        f"Generated at build time on **{today.isoformat()}**. States derive from each cited "
        "block's newest `accessed` date vs the cadence policy in `data/volatility.yaml` "
        "(fresh ≤ cadence · aging ≤ 2× · overdue > 2×). \"Verified\" = a cited source was "
        "checked; \"updated\" = the data file was committed.",
        "",
        "## Blocks needing re-verification",
        "",
    ]
    if attention:
        md += ["| State | Country | Block | Verified | Age (days) | Cadence |",
               "|-------|---------|-------|----------|-----------:|--------:|"]
        for r in attention:
            md.append(f"| {r['state']} | {r['country']} | `{r['block']}` "
                      f"| {r['last_accessed']} | {r['age']} | {r['cadence']}d |")
    else:
        md.append("_No aging or overdue blocks — all cited facts are within schedule._")
    md += [
        "",
        "## Citation migration worklist",
        "",
        "Countries with blocks still lacking citations, oldest update first.",
        "",
        "| Last updated (commit) | Country | Status | Sourced blocks |",
        "|-----------------------|---------|--------|---------------:|",
    ]
    for r in worklist:
        gd = git_dates.get(r["file"], "—")
        md.append(f"| {gd} | {r['country']} | {r['status']} | {r['sourced_blocks']} |")

    # ── Verification queue (the founder's manual to-verify list) ─────────────
    md += [
        "",
        "## Verification queue — blocks awaiting an official source",
        "",
        f"{len(unverified)} block(s) are published with an \"Unverified / Community-Reported\" "
        "caveat because no official source could be confirmed (often the portal bot-blocks "
        "automated fetches). Each needs a human to open the portal, confirm the fact, then either "
        "add a `sources` entry to the block or correct the data.",
        "",
        "**Apply a fix:** `python admin_update.py --country <slug> --source <official-url>` "
        "(fetches the source, proposes a YAML diff, writes on confirmation) — or edit the block's "
        "`sources` list by hand.",
        "",
        "| Country | Block | Check against (official portal) |",
        "|---------|-------|--------------------------------|",
    ]
    if unverified:
        for r in unverified:
            md.append(f"| {r['country']} (`{r['slug']}`) | `{r['block']}` | {r['portal']} |")
    else:
        md.append("| _none_ | _every present block is cited_ | — |")
    md.append("")
    markdown = "\n".join(md)

    return console, markdown
