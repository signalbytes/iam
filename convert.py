import os
import subprocess
import re

DRAFTS_FOLDER = 'drafts'

def slugify(text):
    """Converts 'Gemini India Guide' to 'gemini-india-guide'"""
    text = text.lower()
    # Remove special characters and replace spaces with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def auto_detect_and_inject():
    if not os.path.exists(DRAFTS_FOLDER):
        print(f"❌ Folder '{DRAFTS_FOLDER}' not found.")
        return

    # 1. Loop through every file in the drafts folder
    for filename in os.listdir(DRAFTS_FOLDER):
        if filename.endswith('.docx'):
            doc_title = filename.replace('.docx', '')
            target_slug = slugify(doc_title)
            target_html = f"{target_slug}.html"

            # 2. Check if the matching HTML file exists in the root
            if os.path.exists(target_html):
                print(f"🚀 Found Match: '{filename}' -> {target_html}")
                
                # 3. Convert Word to HTML Snippet (Extracts images too!)
                snippet_file = "temp_body.html"
                subprocess.run([
                    'pandoc', 
                    os.path.join(DRAFTS_FOLDER, filename), 
                    '--extract-media=.', 
                    '-o', snippet_file
                ])

                with open(snippet_file, 'r', encoding='utf-8') as s:
                    new_content = s.read()

                # 4. Inject into the specific zone
                with open(target_html, 'r', encoding='utf-8') as f:
                    original_html = f.read()

                # Look for your markers
                pattern = r".*?"
                replacement = f"\n{new_content}\n"
                
                if "" in original_html:
                    updated_html = re.sub(pattern, replacement, original_html, flags=re.DOTALL)
                    
                    with open(target_html, 'w', encoding='utf-8') as f:
                        f.write(updated_html)
                    print(f"✅ Injected content into {target_html}")
                else:
                    print(f"⚠️ Warning: No injection markers found in {target_html}")

                os.remove(snippet_file)
            else:
                print(f"❓ No match found for '{filename}'. Expected '{target_html}'")

if __name__ == "__main__":
    auto_detect_and_inject()
