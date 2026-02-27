import json
import os
import yaml
import mkdocs_gen_files
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('country.md.jinja')

data_dir = os.path.join('data', 'visas')

# ── Region-to-motif mapping ──────────────────────────────────────────
# Each region key maps to a CSS class suffix (atlas-motif--<motif>).
# Countries inherit their motif from their region unless they explicitly
# override it with a `motif` field in their YAML theme block.
REGION_MOTIFS = {
    "east-asia":      "cherry-blossom",
    "southeast-asia": "tropical-leaves",
    "europe":         "architecture",
    "north-america":  "city-skyline",
    "middle-east":    "islamic-geometric",
    "south-asia":     "mountain-range",
    "oceania":        "waves",
    "africa":         "tribal-pattern",
    "south-america":  "nature-flora",
    "default":        "subtle-grid",
}

# Default brand accent when a country YAML has no theme block
DEFAULT_ACCENT = "#ff3621"

# Collect map data while generating country pages
map_data = {}

for filename in os.listdir(data_dir):
    print(f"[gen] Scanning file: {filename}")

    # Catch both .yaml and .yml extensions
    if filename.endswith(('.yaml', '.yml')):
        print(f"[gen] Generating page for: {filename}")

        file_path = os.path.join(data_dir, filename)

        with open(file_path, 'r', encoding='utf-8') as f:
            country_data = yaml.safe_load(f)

        # ── Extract theme data ────────────────────────────────────
        theme_block = country_data.get('theme', {})
        accent = theme_block.get('accent', DEFAULT_ACCENT)
        region = theme_block.get('region', 'default')
        motif = theme_block.get('motif', REGION_MOTIFS.get(region, 'subtle-grid'))

        # ── Render the Jinja2 template ────────────────────────────
        rendered_markdown = template.render(country_data)

        # ── Prepend YAML front matter for Material page.meta ──────
        # MkDocs reads this front matter and exposes it as page.meta
        # in the Jinja2 template context. Our overrides/main.html
        # reads theme_accent and theme_motif to set CSS variables.
        front_matter = (
            "---\n"
            f"theme_accent: \"{accent}\"\n"
            f"theme_region: \"{region}\"\n"
            f"theme_motif: \"{motif}\"\n"
            f"page_type: country\n"
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
                'accent': accent,
            }

# Write map-data.json for the interactive world map
with mkdocs_gen_files.open("map-data.json", "w") as f:
    json.dump(map_data, f, separators=(',', ':'))
