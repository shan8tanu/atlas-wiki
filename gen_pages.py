import json
import os
import sys

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


# Collect map data while generating country pages
map_data = {}

# Collect parsed YAML per file for the /meta/freshness report
all_countries = {}

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
