from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"

def get_skills_msg():
    skills= crawl_skills(frontmatter=True)
    msg = "You have access to the following skills:\n\n" + "\n".join(skills.values())
    
    skills_msg = { 
            "role": "system", 
            "content": msg
            }
    skills_list = skills.keys()
    return skills_msg, skills_list

def get_skill_body(skill):
    """Convenience method to extract skill body"""    
    return parse_skill_file(SKILLS_DIR.resolve() / skill / "SKILL.md", frontmatter=False)

    

def crawl_skills(): 
    """crawl skills
    
    This works its way through every skill folder in SKILLS_DIR
    and adds it to a dictionary"""   
    skills = {}
    for root, dirs, files in os.walk(SKILLS_DIR.resolve()):
        if "SKILL.md" in files:
            skill_name, description = parse_skill_file(os.path.join(root, "SKILL.md"), frontmatter=True)
            if skill_name:
                skills[skill_name] = f"- {skill_name}: {description}"
    
    return skills


def parse_skill_file(filepath, frontmatter=True):
    """Parsing the skill file
    
    1) If frontmatter = True it
    looks between the opening --- and second --- and then 
    strips out the name and description and returns them
    2) If frontmatter = False it finds the body - everything after second ---
    and returns it.
    """
    name = ""
    description = ""
    body_lines = []
    seen_delimiters = 0
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            
            # Check for frontmatter delimiter line
            if stripped.startswith("---") and all(c == '-' for c in stripped):
                seen_delimiters += 1
                if frontmatter and seen_delimiters == 2:
                    # Finished reading frontmatter
                    return name, description
                continue
            
            # Between the 1st and 2nd delimiter: inside frontmatter
            if seen_delimiters == 1:
                lower = stripped.lower()
                if lower.startswith("name:"):
                    name = stripped.split(":", 1)[1].strip().strip('"\'')
                elif lower.startswith("description:"):
                    description = stripped.split(":", 1)[1].strip().strip('"\'')
            
            # After the 2nd delimiter: inside body
            elif seen_delimiters >= 2:
                if not frontmatter:
                    body_lines.append(line)
                    
    if frontmatter:
        return name, description
        
    return "".join(body_lines).strip()

    