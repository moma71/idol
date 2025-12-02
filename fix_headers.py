import os
import re

# Paths
base_dir = r"c:\Users\wonders\Desktop\my-webnovel\idol"
template_path = os.path.join(base_dir, "episode1", "index.html")

# Read Template
with open(template_path, "r", encoding="utf-8") as f:
    template_content = f.read()

# Extract Template Parts
# 1. Header (up to the end of chapter-title div)
header_match = re.search(r'(.*<div class="chapter-title">.*?<div class="separator"></div>\s*</div>)', template_content, re.DOTALL)
if not header_match:
    print("Error: Could not find header in template")
    exit()
template_header = header_match.group(1)

# 2. Footer (from the closing of episode-wrapper)
# We assume the structure ends with </div></div></body></html>
# Let's find the last few tags.
footer_match = re.search(r'(</div>\s*</div>\s*</body>\s*</html>)', template_content, re.DOTALL)
if not footer_match:
    # Try a more loose match if the strict one fails
    footer_match = re.search(r'(</body>\s*</html>)', template_content, re.DOTALL)
    if not footer_match:
        print("Error: Could not find footer in template")
        exit()
    # If we only found body/html, we need to close the divs.
    # But let's look at the file structure again.
    # It ends with:
    #         </div>
    #     </div>
    # </body>
    # </html>
    pass

# Let's define the footer manually based on the known structure to be safe.
template_footer = """    </div>
    </div>
</body>

</html>"""

# Function to process an episode
def process_episode(ep_num):
    ep_dir = os.path.join(base_dir, f"episode{ep_num}")
    ep_file = os.path.join(ep_dir, "index.html")
    
    if not os.path.exists(ep_file):
        print(f"Episode {ep_num} not found")
        return

    with open(ep_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract Title and Subtitle from current file to preserve them
    title_match = re.search(r'<h1>(.*?)</h1>', content)
    subtitle_match = re.search(r'<h2>(.*?)</h2>', content)
    
    current_title = title_match.group(1) if title_match else "Dream High"
    current_subtitle = subtitle_match.group(1) if subtitle_match else f"Episode {ep_num}"

    # Extract Story Content
    # Everything after the chapter-title div and before the closing divs
    # We look for the chapter-title div end
    content_start_match = re.search(r'<div class="chapter-title">.*?<div class="separator"></div>\s*</div>', content, re.DOTALL)
    if not content_start_match:
        print(f"Error: Could not find content start in Episode {ep_num}")
        return
    
    content_start_pos = content_start_match.end()
    
    # Find the end of content. It should be before the last two closing divs.
    # We can search for the last occurrence of </div>\s*</div>\s*</body>
    content_end_match = re.search(r'\s*</div>\s*</div>\s*</body>', content)
    if not content_end_match:
         print(f"Error: Could not find content end in Episode {ep_num}")
         return
    
    content_end_pos = content_end_match.start()
    
    story_content = content[content_start_pos:content_end_pos].strip()

    # Construct New Content
    # Update Title in Template Header
    # We need to replace the <title> tag and the <h2> tag in the header
    
    # 1. Replace <title>
    new_header = re.sub(r'<title>.*?</title>', f'<title>Dream High - Episode {ep_num}</title>', template_header)
    
    # 2. Replace <h2> (Subtitle)
    # The template has "Episode 1: ..."
    # We replace it with the current subtitle
    new_header = re.sub(r'<h2>.*?</h2>', f'<h2>{current_subtitle}</h2>', new_header)

    # Combine
    new_full_content = f"{new_header}\n\n            {story_content}\n\n{template_footer}"
    
    # Write back
    with open(ep_file, "w", encoding="utf-8") as f:
        f.write(new_full_content)
    
    print(f"Processed Episode {ep_num}")

# Run for Episodes 2-10
for i in range(2, 11):
    process_episode(i)
