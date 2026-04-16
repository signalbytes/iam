import os
import subprocess
import re

DRAFTS_FOLDER = 'drafts'
OVERRIDE = {
    "The Executive’s Guide to Google Gemini's Personal Intelligence in India": "ai-guide.html"
}

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip('-')

def safe_publish():
    if not os.path.exists(DRAFTS_FOLDER):
        return

    for filename in os.listdir(DRAFTS_FOLDER):
        if filename.endswith('.docx'):
            doc_title = filename.replace('.docx', '')
            target_html = OVERRIDE.get(doc_title, f"{slugify(doc_title)}.html")

            if os.path.exists(target_html):
                # 1. Convert Word to clean HTML
                snippet_file = "temp_body.html"
                subprocess.run(['pandoc', os.path.join(DRAFTS_FOLDER, filename), '--extract-media=.', '-o', snippet_file])

                with open(snippet_file, 'r', encoding='utf-8') as s:
                    new_content = s.read()

                # 2. Read the existing page
                with open(target_html, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 3. FIX THE LOOP: Use a Non-Greedy Regex
                # This pattern ensures we find the FIRST start and LAST end 
                # and replace EVERYTHING in between.
                pattern = r".*?"
                replacement = f"\n{new_content}\n"
                
                if "" in content:
                    # re.DOTALL is critical so it sees across multiple lines
                    updated_html = re.sub(pattern, replacement, content, flags=re.DOTALL)
                    
                    with open(target_html, 'w', encoding='utf-8') as f:
                        f.write(updated_html)
                    print(f"✅ Cleaned and Updated: {target_html}")
                
                os.remove(snippet_file)

if __name__ == "__main__":
    safe_publish()
