from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"

def get_skills_msg():
    msg= crawl_skills_frontmatter()
    return { 
            "role": "system", 
            "content": msg
            }

def crawl_skills_frontmatter():
    msg = "You have access to the following skills:\n\n"
    
    for (root, dirs, files) in os.walk(SKILLS_DIR.resolve()):
        for filename in files:  # Changed from 'name' to 'filename' to avoid shadowing
            if filename == 'SKILL.md':
                skill_name, description = parse_skill_frontmatter(os.path.join(root, "SKILL.md"))
                msg += f"- {skill_name}: {description}\n"
                
    return msg


def parse_skill_frontmatter(filepath):
    name = ""
    description = ""
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Look for lines starting with name: or description:
            if line.startswith("name:"):
                name = line.split(":", 1)[1].strip().strip('"\'')
            elif line.startswith("description:"):
                description = line.split(":", 1)[1].strip().strip('"\'')
                
    return name, description


    