from pathlib import Path
import os
import re

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def get_skills_dir() -> Path:
    cwd_skills = Path.cwd() / ".claude" / "skills"
    if cwd_skills.exists():
        return cwd_skills
    return PROJECT_ROOT / ".claude" / "skills"

"""--------------------------------------------------------------------------------------
Access skills
-----------------------------------------------------------------------------------------"""

def get_skills():
    skills= crawl_skills()
    msg = "You have access to the following skills:\n\n"
    msg += "\n".join([value["msg"] for value in skills.values()])
    msg += "\n\nIf a skill matches the user's request, call the Skill tool with its name and follow the instructions it returns."
    
    skills_msg = { 
            "role": "system", 
            "content": msg, 
            }
    return skills_msg, skills

def get_skill_body(skill):
    """Convenience method to extract skill body"""
    skills_dir = get_skills_dir()
    skill_file = skills_dir / skill / "SKILL.md"

    if skill_file.exists():
        return parse_skill_file(skill_file, frontmatter=False)
    
    # Fallback search if folder name differs
    for root, dirs, files in os.walk(skills_dir):
        if "SKILL.md" in files:
            name, _ = parse_skill_file(os.path.join(root, "SKILL.md"), frontmatter=True)
            if name == skill:
                return parse_skill_file(os.path.join(root, "SKILL.md"), frontmatter=False)
    return ""


"""------------------------------------------------------------------------------------------------------
Processing skills requested by LLM
---------------------------------------------------------------------------------------------------------"""

def crawl_skills(): 
    """crawl skills
    
    This works its way through frontmatter of every skill folder in SKILLS_DIR
    and adds it to a dictionary:
        
    skills[skill_name] = {
        "msg": "skill_name: description",
        "context": "fork"   # fork results in skill being handled by a subagent
        }
        
        
        """   
    skills = {}
    skills_dir = get_skills_dir()
    for root, _, files in os.walk(skills_dir):
        if "SKILL.md" in files:
            skill_name, description, context = parse_skill_file(os.path.join(root, "SKILL.md"), frontmatter=True)
            if skill_name:
                skills[skill_name] = {"msg": f"- {skill_name}: {description}", "context": context}
    
    return skills

def parse_skill_request(prompt, existing_skills):
    """This is a prompt which has form /skill_name /skill_name2 arg1 arg2 etc"""
    matches = re.findall(r'/\w+', prompt)
    skill_names = [match[1:] for match in matches if match[1:] in existing_skills]
    for skill in skill_names:
        prompt = prompt.replace("/" + skill, "")
    args = prompt.split() 
    return skill_names, args


"""-----------------------------------------------------------------------------------------------------
Responding to the AI with a skill msg
---------------------------------------------------------------------------------------------------------"""

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
    context = None
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
                    break
                continue
            
            # Between the 1st and 2nd delimiter: inside frontmatter
            if seen_delimiters == 1:
                lower = stripped.lower()
                if lower.startswith("name:"):
                    name = stripped.split(":", 1)[1].strip().strip('"\'')
                elif lower.startswith("description:"):
                    description = stripped.split(":", 1)[1].strip().strip('"\'')
                elif lower.startswith("context:"):
                    context = stripped.split(":", 1)[1].strip().strip('"\'')
            
            # After the 2nd delimiter: inside body
            elif seen_delimiters >= 2:
                if not frontmatter:
                    body_lines.append(line)
                    
    if frontmatter:
        return name, description, context
        
    return "".join(body_lines).strip()


def create_skill_msg(skill, skill_body):
    folder = f".claude/skills/{skill}"
    preamble = (
        f"Skill: {skill} (located at {folder})\n"
        f"Paths in the instructions below are relative to that folder.\n\n"
    )
    # Replace relative script references so models running locally don't fail
    skill_body = skill_body.replace("scripts/", f"{folder}/scripts/")
    return {"role": "user", "content": preamble + skill_body}


def apply_arg_substitution(body, args):
    if not args:
        return body
    for i, arg in enumerate(args):
        body = body.replace(f"${i}", arg)
    body = body.replace("$ARGUMENTS", " ".join(args))
    return body
    




