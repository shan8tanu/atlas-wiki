import os
import yaml
import mkdocs_gen_files
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('country.md.jinja')

data_dir = os.path.join('data', 'visas')

for filename in os.listdir(data_dir):
    print(f"👀 Python sees file: {filename}")
    
    # Catch both .yaml and .yml extensions
    if filename.endswith(('.yaml', '.yml')):
        print(f"✅ Generating page for: {filename}")
        
        file_path = os.path.join(data_dir, filename)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            country_data = yaml.safe_load(f)
            
        rendered_markdown = template.render(country_data)
        
        # Safely strip the extension and add .md
        base_name = os.path.splitext(filename)[0]
        md_filename = f"{base_name}.md"
        
        with mkdocs_gen_files.open(md_filename, "w") as fd:
            fd.write(rendered_markdown)