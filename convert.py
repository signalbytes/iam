import os
import subprocess
from datetime import datetime

# 1. Convert Word to HTML Snippet using Pandoc
for file in os.listdir('drafts'):
    if file.endswith('.docx'):
        filename = file.replace('.docx', '').lower().replace(' ', '-')
        # Extracts images to a folder called 'images' automatically
        subprocess.run(['pandoc', f'drafts/{file}', '--extract-media=.', '-o', f'{filename}-snippet.html'])

        # 2. Stitch the Page
        with open('header-template.html', 'r') as h, open('footer-template.html', 'r') as f, open(f'{filename}-snippet.html', 'r') as s:
            full_page = h.read() + "<div class='container content-section'>" + s.read() + "</div>" + f.read()
        
        with open(f'{filename}.html', 'w') as out:
            out.write(full_page)

        # 3. Update Index (Add new Bento Card)
        # (This part would use a simple string replace to add a new <a> tag to your index.html)
        print(f"✅ Published: {filename}.html")
