from openai import OpenAI
import os

from app.load_config import API_KEY, BASE_URL, DEFAULT_MODEL, CACHE_FILE
from app.tools import tool_list, parse_tool_call, extract_tool_calls
from app.tools import Read, Write, Bash
from app.skills import get_skills, get_skill_body, parse_skill_request, apply_arg_substitution


class Agent:
    def __init__(self):
        self.client =  OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.current_response=None
        skills_msg, skills_list = get_skills()
        self.message_history=[skills_msg]  
        self.skills = skills_list      
        
    def prompt(self, args):
        self._process_prompt(args.p)
        self._start_agent_loop()
    
    def _start_agent_loop(self):
        """_send_message
        
        Internal worker that sends current message history to LLM
        updates the current response to be processed and calls tools
        """
        
        while True:
            # Send request to LLM and receive response
            response = self.client.chat.completions.create(
                        model=DEFAULT_MODEL,
                        messages=self.message_history,
                        tools=tool_list,
                    )
                
            if not response.choices or len(response.choices) == 0:
                raise RuntimeError("no choices in response")
        
            #get message and update message history.    
            msg = self._update_message(response)
            tool_calls = extract_tool_calls(msg)
            if tool_calls is None:
                break
            else:
                for tool_call in tool_calls:
                    fn_name, tool_call_id, args=parse_tool_call(tool_call)
                    
                    if fn_name == 'Read':
                        msg =Read(tool_call_id, args["file_path"])
                    elif fn_name == 'Write':
                        msg = Write(tool_call_id, args["file_path"], args["content"])  
                    elif fn_name == 'Bash':
                        msg= Bash(tool_call_id, args["command"])   
                    else:     
                        raise("Tool not implemented")
                    
                    self.message_history.append(msg)
                
        #Print final response
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
            
            for skill in skill_cmds:
                if skill in self.skills:
                    skill_body = get_skill_body(skill)
                    skill_body = apply_arg_substitution(skill_body, args)
                    skill_msg = {"role": "user", "content": skill_body}
                    self.message_history.append(skill_msg)
        else:
            #Otherwise send unaltered user prompt
            user_prompt = {"role": "user", "content": prompt}
            self.message_history.append(user_prompt)
            
        
        
                

 
    
        
        