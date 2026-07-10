import email.utils
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from xml.sax.saxutils import escape

import yaml
import mkdocs_gen_files
from jinja2 import Environment, FileSystemLoader

# mkdocs-gen-files execs this script; make repo-root imports (freshness,
# validate.*) resolvable regardless of how mkdocs was launched.
sys.path.insert(0, os.getcwd())

from freshness import (  # noqa: E402
    block_freshness,
    build_report,
    git_last_commit_dates,
    load_volatility,
    page_rollup,
)
from validate.schema import DIFFICULTY_LABELS  # noqa: E402

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('country.md.jinja')

data_dir = os.path.join('data', 'visas')

# ── Freshness inputs, computed ONCE per build ────────────────────────────────
try:
    volatility = load_volatility()
except Exception as exc:
    # check I fails CI on a broken policy; keep local `mkdocs serve` usable.
    print(f"[gen] WARNING: volatility policy unavailable ({exc}) - freshness disabled")
    volatility = {}
git_dates = git_last_commit_dates(data_dir)  # {} when git history unavailable


def iso_to_flag(iso_code: str) -> str:
    """Convert a 2-letter ISO code to a Unicode flag emoji.
    e.g. 'JP' → '🇯🇵', 'US' → '🇺🇸'"""
    return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in iso_code.upper())


def compute_fees(country_data: dict):
    """
    Compute fee totals from requirements.fees — totals are NEVER stored in
    YAML. Returns {mandatory_total, all_in_total, govt_fee} or None when no
    usable fees block exists. Defensive by design (skips malformed
    components) so bad local data degrades on `mkdocs serve` instead of
    crashing the build — structural enforcement is check group J's job in CI.
    """
    fees = (country_data.get('requirements') or {}).get('fees')
    if not isinstance(fees, dict):
        return None
    components = fees.get('components')
    if not isinstance(components, list):
        return None

    mandatory_total = 0
    all_in_total = 0
    govt_fee = None
    usable = 0
    for comp in components:
        if not isinstance(comp, dict):
            continue
        amount = comp.get('amount_inr')
        if not isinstance(amount, int) or isinstance(amount, bool):
            continue
        usable += 1
        all_in_total += amount
        if comp.get('mandatory') is True:
            mandatory_total += amount
        if comp.get('is_government_fee') is True and govt_fee is None:
            govt_fee = amount
    if usable == 0:
        return None
    return {
        'mandatory_total': mandatory_total,
        'all_in_total': all_in_total,
        'govt_fee': govt_fee,
    }


# Collect map data while generating country pages
map_data = {}

# Collect parsed YAML per file for the /meta/freshness report
all_countries = {}

# Collect changelog entries across all countries for /changes/ + changes.xml.
# Locale-independent month names — strftime('%B') follows the OS locale.
MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December")
changelog_entries = []

for filename in os.listdir(data_dir):
    print(f"[gen] Scanning file: {filename}")

    # Catch both .yaml and .yml extensions
    if filename.endswith(('.yaml', '.yml')):
        print(f"[gen] Generating page for: {filename}")

        file_path = os.path.join(data_dir, filename)

        with open(file_path, 'r', encoding='utf-8') as f:
            country_data = yaml.safe_load(f)

        # Compute flag emoji from ISO code and inject into template context
        iso = country_data.get('iso_code', '')
        if iso:
            country_data['flag_emoji'] = iso_to_flag(iso)

        all_countries[filename] = country_data

        # ── Freshness context (per-block states + page rollup) ────
        fresh = block_freshness(country_data, volatility)
        rollup = page_rollup(fresh, country_data)
        rollup['git_date'] = git_dates.get(filename)
        country_data['_freshness'] = fresh
        country_data['_page_freshness'] = rollup
        country_data['_difficulty_label'] = DIFFICULTY_LABELS.get(
            country_data.get('visa_difficulty'))
        country_data['_fees'] = compute_fees(country_data)

        # ── Render the Jinja2 template ────────────────────────────
        rendered_markdown = template.render(country_data)

        # ── Prepend YAML front matter for Material page.meta ──────
        front_matter = (
            "---\n"
            "page_type: country\n"
            "---\n\n"
        )

        full_markdown = front_matter + rendered_markdown

        # Safely strip the extension and add .md
        base_name = os.path.splitext(filename)[0]
        md_filename = f"{base_name}.md"

        # ── Collect changelog entries for the site-wide Change Log ─
        # Structure/type/source problems are check group G's job (G1/G2,
        # G10-G12 ERROR in CI); here we only guard the build itself:
        # an unparseable date is warned about and excluded, never fatal.
        for entry_idx, entry in enumerate(country_data.get('changelog') or []):
            if not isinstance(entry, dict):
                continue
            try:
                entry_date = datetime.strptime(
                    str(entry.get('date')), '%Y-%m-%d').date()
            except (TypeError, ValueError):
                print(f"[gen] WARNING: {filename} changelog[{entry_idx}] has "
                      f"unparseable date {entry.get('date')!r} - entry excluded "
                      f"from the Change Log page and RSS feed")
                continue
            changelog_entries.append({
                'date': entry_date,
                'country': country_data.get('country', base_name.title()),
                'slug': base_name,
                'type': str(entry.get('type') or ''),
                'description': str(entry.get('description') or '').strip(),
                'source': str(entry.get('source') or ''),
            })

        with mkdocs_gen_files.open(md_filename, "w") as fd:
            fd.write(full_markdown)

        # Route the "Edit this page" button to the YAML source file,
        # not the generated .md. This is the entry point for community edits.
        mkdocs_gen_files.set_edit_path(md_filename, f"data/visas/{filename}")

        # Build map data entry using lowercase ISO code (matches SVG element IDs)
        iso = country_data.get('iso_code', '').lower()
        if iso:
            map_data[iso] = {
                'name': country_data.get('country', base_name.title()),
                'url': f"{base_name}/",
                'difficulty': country_data.get('visa_difficulty', 0),
                'visa_type': country_data.get('visa_type', ''),
            }

# Write map-data.json for the interactive world map
with mkdocs_gen_files.open("map-data.json", "w") as f:
    json.dump(map_data, f, separators=(',', ':'))


# ── Generate transit guide (if data exists) ─────────────────────
transit_yaml = os.path.join('data', 'transit', 'transit_rules.yaml')
if os.path.exists(transit_yaml):
    print("[gen] Generating transit guide")
    with open(transit_yaml, 'r', encoding='utf-8') as f:
        transit_data = yaml.safe_load(f)

    transit_template = env.get_template('transit-guide.md.jinja')
    rendered = transit_template.render(transit_data)

    front_matter = (
        "---\n"
        "page_type: guide\n"
        "---\n\n"
    )

    with mkdocs_gen_files.open("guides/transit-visa-rules.md", "w") as fd:
        fd.write(front_matter + rendered)

    mkdocs_gen_files.set_edit_path(
        "guides/transit-visa-rules.md",
        "data/transit/transit_rules.yaml"
    )


# ── Generate /meta/freshness (librarian's re-verification worklist) ─────────
# Not in nav (see not_in_nav in mkdocs.yml) — reachable by URL only.
if volatility:
    print("[gen] Generating freshness report page")
    _, report_md = build_report(all_countries, volatility, git_dates)
    with mkdocs_gen_files.open("meta/freshness.md", "w") as fd:
        fd.write("---\npage_type: meta\n---\n\n" + report_md)
    mkdocs_gen_files.set_edit_path("meta/freshness.md", "data/volatility.yaml")


# ── Generate /changes/ (site-wide Change Log) + changes.xml (RSS 2.0) ───────
print(f"[gen] Generating Change Log page + RSS feed "
      f"({len(changelog_entries)} entries)")

# site_url from mkdocs.yml (mkdocs-gen-files exposes the live config);
# fall back to the canonical URL if run outside mkdocs.
_config = getattr(mkdocs_gen_files, 'config', None)
site_url = (_config.get('site_url') if _config else None) or "https://atlas-wiki.pages.dev/"
if not site_url.endswith('/'):
    site_url += '/'
feed_url = f"{site_url}changes.xml"

# Newest first; stable country-name tie-break within a date.
changelog_entries.sort(key=lambda e: e['country'])
changelog_entries.sort(key=lambda e: e['date'], reverse=True)

# Group by calendar month for the page ("July 2026"), preserving date order.
months = []
for e in changelog_entries:
    label = f"{MONTH_NAMES[e['date'].month - 1]} {e['date'].year}"
    if not months or months[-1]['label'] != label:
        months.append({'label': label, 'entries': []})
    months[-1]['entries'].append({**e, 'date': e['date'].isoformat()})

changes_template = env.get_template('changes.md.jinja')
rendered_changes = changes_template.render(
    months=months, feed_url=feed_url, total=len(changelog_entries))
with mkdocs_gen_files.open("changes.md", "w") as fd:
    fd.write("---\npage_type: changes\n---\n\n" + rendered_changes)
# The page aggregates every country's changelog; route edits to the data dir.
mkdocs_gen_files.set_edit_path("changes.md", "data/visas")

# ── RSS 2.0 feed: 50 most recent items, hand-built with XML escaping ────────
rss_items = []
for e in changelog_entries[:50]:
    desc = e['description']
    title = f"{e['country']}: {e['type']} — " + (
        desc if len(desc) <= 80 else desc[:80].rstrip() + "…")
    link = f"{site_url}{e['slug']}/#change-log"
    pub = email.utils.format_datetime(  # RFC 822, locale-independent
        datetime(e['date'].year, e['date'].month, e['date'].day,
                 tzinfo=timezone.utc))
    # guid is a content hash (type+description), NOT the array index —
    # new entries are conventionally prepended to a country's changelog
    # (see japan.yaml), which would shift every later entry's index and
    # falsely re-deliver old items as new to RSS readers on every rebuild.
    content_hash = hashlib.sha1(
        f"{e['type']}|{e['description']}".encode('utf-8')).hexdigest()[:10]
    guid = f"{e['slug']}-{e['date'].isoformat()}-{content_hash}"
    rss_items.append(
        "    <item>\n"
        f"      <title>{escape(title)}</title>\n"
        f"      <link>{escape(link)}</link>\n"
        f"      <description>{escape(desc)}</description>\n"
        f"      <pubDate>{pub}</pubDate>\n"
        f"      <guid isPermaLink=\"false\">{escape(guid)}</guid>\n"
        "    </item>"
    )

last_build = (email.utils.format_datetime(
    datetime(changelog_entries[0]['date'].year,
             changelog_entries[0]['date'].month,
             changelog_entries[0]['date'].day, tzinfo=timezone.utc))
    if changelog_entries else email.utils.format_datetime(
        datetime.now(timezone.utc)))

rss = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
    '  <channel>\n'
    '    <title>Atlas — Change Log</title>\n'
    f'    <link>{escape(site_url)}changes/</link>\n'
    '    <description>Visa rule, fee, document, and process changes for '
    'Indian passport holders, aggregated across every country on the '
    'Atlas wiki.</description>\n'
    '    <language>en</language>\n'
    f'    <lastBuildDate>{last_build}</lastBuildDate>\n'
    f'    <atom:link href="{escape(feed_url)}" rel="self" '
    'type="application/rss+xml" />\n'
    + "\n".join(rss_items) + ("\n" if rss_items else "")
    + '  </channel>\n'
    '</rss>\n'
)
with mkdocs_gen_files.open("changes.xml", "w") as fd:
    fd.write(rss)
