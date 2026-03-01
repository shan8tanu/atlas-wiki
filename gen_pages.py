import json
import os
import yaml
import mkdocs_gen_files
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('country.md.jinja')

data_dir = os.path.join('data', 'visas')


def iso_to_flag(iso_code: str) -> str:
    """Convert a 2-letter ISO code to a Unicode flag emoji.
    e.g. 'JP' → '🇯🇵', 'US' → '🇺🇸'"""
    return ''.join(chr(0x1F1E6 + ord(c) - ord('A')) for c in iso_code.upper())


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

        # Compute flag emoji from ISO code and inject into template context
        iso = country_data.get('iso_code', '')
        if iso:
            country_data['flag_emoji'] = iso_to_flag(iso)

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
