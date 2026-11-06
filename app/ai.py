from openai import OpenAI
import os

from app.load_config import API_KEY, BASE_URL, DEFAULT_MODEL, CACHE_FILE
from app.tools import tool_list, parse_tool_call, extract_tool_calls
from app.tools import Read, Write, Bash, Skill
from app.skills import get_skills, get_skill_body, parse_skill_request, apply_arg_substitution, create_skill_msg


class Agent:
    def __init__(self, debug=False):
        self.debug = debug  # Store the debug flag
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.current_response = None
        
        skills_msg, skills_list = get_skills()
        self.message_history = [skills_msg]  
        self.skills = skills_list      
        
        if self.debug:
            print(f"\n[DEBUG] Agent initialized.")
            print(f"[DEBUG] Available skills: {self.skills}")
            print(f"[DEBUG] Initial system/skills message:\n{skills_msg}\n")
        
    def prompt(self, args):
        if self.debug:
            print(f"\n[DEBUG] Processing user prompt input: {args.p}")
        self._process_prompt(args.p)
        self._start_agent_loop()
    
    def _start_agent_loop(self):
        """main loop that interacts with LLM
        
        Internal worker that sends current message history to LLM
        updates the current response to be processed and calls tools
        """
        
        iteration = 0
        while True:
            iteration += 1
            if self.debug:
                print(f"\n--- [DEBUG] Agent Loop Iteration {iteration} ---")
                print(f"[DEBUG] Sending {len(self.message_history)} messages to LLM history:")
                for idx, m in enumerate(self.message_history):
                    # Handle both dict messages and OpenAI message objects
                    role = m.get("role") if isinstance(m, dict) else getattr(m, "role", "unknown")
                    content = m.get("content") if isinstance(m, dict) else getattr(m, "content", "")
                    print(f"  [{idx}] Role: {role} | Content excerpt: {str(content)[:100]}...")

            # Send request to LLM and receive response
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=self.message_history,
                tools=tool_list,
            )
                    
            if not response.choices or len(response.choices) == 0:
                raise RuntimeError("no choices in response")
        
            # get message and update message history.    
            msg = self._update_message(response)
            
            if self.debug:
                print(f"[DEBUG] LLM Response received:")
                print(f"  - Content: {msg.content}")
                print(f"  - Tool Calls: {getattr(msg, 'tool_calls', None)}")

            tool_calls = extract_tool_calls(msg)
            if tool_calls is None:
                if self.debug:
                    print(f"[DEBUG] No tool calls detected. Breaking loop to finalize response.")
                break
            else:
                for tool_call in tool_calls:
                    fn_name, tool_call_id, args = parse_tool_call(tool_call)
                    
                    if self.debug:
                        print(f"[DEBUG] Executing Tool -> Name: {fn_name}, ID: {tool_call_id}, Args: {args}")
                    
                    if fn_name == 'Read':
                        msg = Read(tool_call_id, args["file_path"])
                    elif fn_name == 'Write':
                        msg = Write(tool_call_id, args["file_path"], args["content"])  
                    elif fn_name == 'Bash':
                        msg = Bash(tool_call_id, args["command"])  
                    elif fn_name == 'Skill':
                        msg = Skill(tool_call_id, args["name"], args.get("args", ""))
                    else:     
                        raise Exception(f"Tool not implemented: {fn_name}")
                    
                    if self.debug:
                        print(f"[DEBUG] Tool result message to append: {msg}")

                    self.message_history.append(msg)
                
        # Print final response
        if self.debug:
            print(f"\n[DEBUG] Final Agent Output:")
        print(msg.content)
    
    # Extracts message from response and adds message to history
    def _update_message(self, response):
        msg = response.choices[0].message
        self.message_history.append(msg)
        return msg
    
    def _process_prompt(self, prompt):
        if prompt.startswith("/"):
            # If skills called for
            skill_cmds, args = parse_skill_request(prompt, self.skills)
            if self.debug:
                print(f"[DEBUG] Parsed slash commands: {skill_cmds} with args: {args}")
            
            for skill in skill_cmds:
                if skill in self.skills:
                    skill_body = get_skill_body(skill)
                    skill_body = apply_arg_substitution(skill_body, args)
                    skill_msg = create_skill_msg(skill, skill_body)
                    if self.debug:
                        print(f"[DEBUG] Injecting skill message for '{skill}':\n{skill_msg}")
                    self.message_history.append(skill_msg)
        else:
            # Otherwise send unaltered user prompt
            user_prompt = {"role": "user", "content": prompt}
            if self.debug:
                print(f"[DEBUG] Injecting standard user prompt: {user_prompt}")
            self.message_history.append(user_prompt)