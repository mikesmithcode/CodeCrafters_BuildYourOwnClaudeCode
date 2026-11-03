from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"

def get_skills_msg():
    msg= crawl_skills_frontmatter()
    if not msg:
        return None
    return { 
            "role": "system", 
            "content": msg
            }

def crawl_skills_frontmatter():
    if not SKILLS_DIR.exists():
        return ""
    
    skills = []
    for root, dirs, files in os.walk(SKILLS_DIR.resolve()):
        if "SKILL.md" in files:
            skill_name, description = parse_skill_frontmatter(os.path.join(root, "SKILL.md"))
            if skill_name:
                skills.append(f"- {skill_name}: {description}")
    
    if not skills:
        return ""
    
    return "You have access to the following skills:\n\n" + "\n".join(skills)


def parse_skill_frontmatter(filepath):
    name = ""
    description = ""
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            lower_line = line.lower()
            if lower_line.startswith("name:"):
                name = line.split(":", 1)[1].strip().strip('"\'')
            elif lower_line.startswith("description:"):
                description = line.split(":", 1)[1].strip().strip('"\'')
                
    return name, description


    