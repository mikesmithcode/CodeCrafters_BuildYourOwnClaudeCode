from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT/ "app" / ".claude" / "skills"

def get_skills_msg():
    msg= crawl_skills_frontmatter()
    print(msg)
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
    with open(filepath , "r") as f:
        _ =f.readline()
        name =f.readline().split(": ")[1].strip()
        description = f.readline().split(": ")[1].strip()
    return (name, description)


    