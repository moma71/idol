import os
import re
import glob

# Configuration
BASE_DIR = r"c:\Users\wonders\Desktop\my-webnovel\idol"
PHASE3_DIR = os.path.join(BASE_DIR, "production_history", "phase3")
TEMPLATE_HEADER = """<!DOCTYPE html>
<html lang="ko">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dream High - Episode {ep_num}</title>
    <link rel="stylesheet" href="../style.css">
    <link rel="stylesheet" href="../episodes-common/episode.css">
</head>

<body>
    <div id="common-header"></div>
    <script src="../episodes-common/load-header.js" defer></script>

    <div class="ep-container" style="padding-top:100px;">
        <div class="episode-wrapper">

            <div class="chapter-title">
                <h1>🎤 Dream High - K-POP 연습생 AI 성장기</h1>
                <h2>{subtitle}</h2>
                <div class="separator"></div>
            </div>
"""

TEMPLATE_FOOTER = """
            <div class="separator"></div>

            <p style="text-align: center; font-size: 0.9em; color: #777;">
                **[Episode {ep_num} 완료]**
            </p>
            {preview_html}

        </div>
    </div>
</body>

</html>
"""

def parse_markdown(md_content):
    html_lines = []
    lines = md_content.split('\n')
    
    in_ai_guide = False
    in_code_block = False
    in_checklist = False
    img_count = 1
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines if not in code block
        if not line and not in_code_block:
            i += 1
            continue
            
        # Stop at Illustrations section
        if line.startswith("## 📸 This Episode's Illustrations"):
            break
            
        # Headers
        if line.startswith("# Episode"):
            # Handled in metadata extraction, skip here
            i += 1
            continue
            
        # Separator
        if line == "---":
            if in_checklist:
                html_lines.append("</ul>")
                in_checklist = False
            if in_ai_guide:
                html_lines.append("</div>")
                in_ai_guide = False
            html_lines.append('<div class="separator"></div>')
            i += 1
            continue
            
        # AI Guide Start
        if line.startswith("## 💡 Hands-On Tutorial"):
            if in_checklist:
                html_lines.append("</ul>")
                in_checklist = False
            if in_ai_guide:
                html_lines.append("</div>")
            
            # Extract title
            title = line.replace("## ", "").strip()
            html_lines.append('<div class="ai-guide">')
            html_lines.append(f'<h2>{title}</h2>')
            in_ai_guide = True
            i += 1
            continue

        # Learning Concept Start
        if line.startswith("## 🎯 Learning Concept"):
            if in_checklist:
                html_lines.append("</ul>")
                in_checklist = False
            if in_ai_guide:
                html_lines.append("</div>")
            
            title = line.replace("## ", "").strip()
            html_lines.append('<div class="ai-guide" style="background-color: #ffe6e6; border-left: 5px solid #c00;">')
            html_lines.append(f'<h2>{title}</h2>')
            in_ai_guide = True
            i += 1
            continue

        # Images
        img_match = re.match(r'!\[(.*?)\]\(.*?\)', line)
        if img_match:
            if in_checklist:
                html_lines.append("</ul>")
                in_checklist = False
            
            alt_text = img_match.group(1)
            img_filename = f"{img_count:02d}.webp"
            html_lines.append(f'<div class="scene-media"><img class="scene-image" src="{img_filename}" alt="{alt_text}"></div>')
            img_count += 1
            
            # Check for caption in next line
            if i + 1 < len(lines):
                next_line = lines[i+1].strip()
                if next_line.startswith("*") and next_line.endswith("*"):
                    caption = next_line[1:-1].strip()
                    html_lines.append(f'<div class="caption">{caption}</div>')
                    i += 2
                    continue
                elif next_line.startswith("*"): # Sometimes it might not end with *
                     caption = next_line[1:].strip()
                     html_lines.append(f'<div class="caption">{caption}</div>')
                     i += 2
                     continue
            i += 1
            continue

        # Code Blocks
        if line.startswith("```"):
            if in_code_block:
                html_lines.append("</div>")
                in_code_block = False
            else:
                if in_checklist:
                    html_lines.append("</ul>")
                    in_checklist = False
                html_lines.append('<div class="prompt-code">')
                in_code_block = True
            i += 1
            continue
            
        if in_code_block:
            # Handle bold in code block? Usually code blocks are literal, but here they seem to be prompts.
            # The prompt example has bolding like **현재 상황:**
            # We should probably preserve markdown inside prompt-code or convert it?
            # In ep9, <div class="prompt-code"> contains HTML tags like <strong>?
            # Let's check ep9 content again.
            # 76: 너는 {분야, 예: "퍼포먼스"} 최종 점검 전문가야.
            # 78: **현재 상황:**
            # It seems it's just text in the div, maybe white-space: pre-wrap?
            # Ep9 index.html line 75: <div class="prompt-code">
            # Line 78: **현재 상황:**
            # So it renders raw markdown syntax in the browser? Or is it styled?
            # Let's assume we just dump the text.
            html_lines.append(line) # + "<br>"?
            # If prompt-code has white-space: pre-wrap, newlines are preserved.
            # Let's assume it does.
            i += 1
            continue

        # Checklists
        if line.strip().startswith("- [ ]") or line.strip().startswith("- [x]"):
            if not in_checklist:
                html_lines.append('<ul class="checklist">')
                in_checklist = True
            
            content = line.replace("- [ ]", "").replace("- [x]", "").strip()
            # Handle links in checklist
            content = re.sub(r'(https?://\S+)', r'<a href="\1" target="_blank">\1</a>', content)
            html_lines.append(f'<li><label><input type="checkbox"> {content}</label></li>')
            i += 1
            continue
        
        if in_checklist and not (line.strip().startswith("- [ ]") or line.strip().startswith("- [x]")):
            html_lines.append("</ul>")
            in_checklist = False

        # Normal Text
        # Handle bold
        line = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
        
        # Handle simple lists (bullets) that are NOT checklists
        if line.strip().startswith("- "):
            # If we are in a list... 
            # For now, treat as paragraph or simple text if not checklist
            # But wait, ep9 has lists inside prompt-code.
            # Outside prompt-code?
            # Ep9 line 24: - 월~금 ...
            # In the markdown analysis, these were just text in p tags?
            # Ep9 line 23: **12월:**
            # Ep9 line 24: - 월~금 ...
            # In HTML: <p><strong>"Week 1: ..."</strong><br>...</p>
            # It seems lists are often converted to <p> with <br> or just multiple <p>.
            # Let's wrap in <p>.
            pass

        # Handle headers inside text (e.g. ## User Review)
        # The story md has `## 💡 ...` which we handled.
        # What about `**12월:**`?
        
        # Wrap in <p>
        html_lines.append(f'<p>{line}</p>')
        i += 1

    if in_checklist:
        html_lines.append("</ul>")
    if in_ai_guide:
        html_lines.append("</div>")
        
    return "\n".join(html_lines)

def get_subtitle(md_content):
    match = re.search(r'# Episode \d+: (.*)', md_content)
    if match:
        return f"Episode {match.group(0).replace('# ', '')}" # "Episode 11: 시작의 무게"
    return "Episode"

def process_episode(ep_num):
    print(f"Processing Episode {ep_num}...")
    
    # Find story file
    pattern = os.path.join(PHASE3_DIR, f"episode_{ep_num}_story*.md")
    files = glob.glob(pattern)
    
    if not files:
        print(f"No story file found for Episode {ep_num}")
        return

    # Prefer REVISED
    story_file = next((f for f in files if "REVISED" in f), files[0])
    print(f"Using file: {os.path.basename(story_file)}")
    
    with open(story_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    # Extract Subtitle
    # The first line is usually "# Episode 11: 시작의 무게"
    first_line = md_content.split('\n')[0].strip()
    if first_line.startswith("# Episode"):
        subtitle = first_line.replace("# ", "")
    else:
        subtitle = f"Episode {ep_num}"
        
    # Parse Content
    html_content = parse_markdown(md_content)
    
    # Preview (placeholder for now, or extract if possible)
    preview_html = ""
    # Check for preview text in md?
    
    # Generate Full HTML
    full_html = TEMPLATE_HEADER.format(ep_num=ep_num, subtitle=subtitle) + \
                html_content + \
                TEMPLATE_FOOTER.format(ep_num=ep_num, preview_html=preview_html)
                
    # Create Directory
    ep_dir = os.path.join(BASE_DIR, f"episode{ep_num}")
    os.makedirs(ep_dir, exist_ok=True)
    
    # Write HTML
    output_path = os.path.join(ep_dir, "index.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)
        
    print(f"Created {output_path}")

def main():
    for i in range(11, 16):
        process_episode(i)

if __name__ == "__main__":
    main()
