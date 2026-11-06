from app.skills import parse_skill_request, get_skill_body, apply_arg_substitution, create_skill_msg


def process_user_prompt(prompt, skills):
    """
    Parses incoming prompts, handling slash commands and argument substitution.
    Returns a list of messages to be appended to the history.
    """
    if prompt.startswith("/"):
        skill_cmds, args = parse_skill_request(prompt, skills.keys())
        messages = []
        
        for skill in skill_cmds:
            if skill in skills:
                skill_body = get_skill_body(skill)
                skill_body = apply_arg_substitution(skill_body, args)
                skill_msg = create_skill_msg(skill, skill_body)
                messages.append(skill_msg)
        return messages
    else:
        # Standard user prompt
        return [{"role": "user", "content": prompt}]