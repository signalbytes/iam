import os
import subprocess
import re

DRAFTS_FOLDER = 'drafts'

# --- MANUAL OVERRIDES ---
# Format: "Exact Word Filename (no .docx)": "Target HTML Filename"
OVERRIDE = {
    "The Executive’s Guide to Google Gemini's Personal Intelligence in India": "ai-guide.html"
}

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def smart_publish():
    if not os.path.exists(DRAFTS_FOLDER):
        os.makedirs(DRAFTS_FOLDER)
        return

    for filename in os.listdir(DRAFTS_FOLDER):
        if filename.endswith('.docx'):
            doc_title = filename.replace('.docx', '')
            
            # 1. Check if there is a manual override first
            if doc_title in OVERRIDE:
                target_html = OVERRIDE[doc_title]
                print(f"🎯 Override Triggered: '{filename}' -> {target_html}")
            else:
                # 2. Otherwise, use the automatic slug detection
                target_html = f"{slugify(doc_title)}.html"
                print(f"🔍 Auto-detecting: '{filename}' -> {target_html}")

            if os.path.exists(target_html):
                # 3. Convert via Pandoc
                snippet_file = "temp_body.html"
                subprocess.run(['pandoc', os.path.join(DRAFTS_FOLDER, filename), '--extract-media=.', '-o', snippet_file])

                with open(snippet_file, 'r', encoding='utf-8') as s:
                    new_content = s.read()

                # 4. Inject into the page
                with open(target_html, 'r', encoding='utf-8') as f:
                    content = f.read()

                pattern = r".*?"
                replacement = f"\n{new_content}\n"
                
                if "" in content:
                    updated_html = re.sub(pattern, replacement, content, flags=re.DOTALL)
                    with open(target_html, 'w', encoding='utf-8') as f:
                        f.write(updated_html)
                    print(f"✅ Injection Complete for {target_html}")
                else:
                    print(f"⚠️ Error: No marker found in {target_html}")

                os.remove(snippet_file)
            else:
                print(f"❌ File Not Found: I looked for {target_html} but it doesn't exist in the repo.")

if __name__ == "__main__":
    smart_publish()
