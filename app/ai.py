from openai import OpenAI


from app.load_config import API_KEY, BASE_URL, DEFAULT_MODEL, CACHE_FILE
from app.tools import tool_list, extract_tool_calls, handle_tool_calls
from app.skills import get_skills
from app.utils import debug_trace, debug_agent
from app.agent_helper_funcs import process_user_prompt

class Agent:
    @debug_agent
    def __init__(self, debug=False):
        self.debug = debug  # Store the debug flag
        self.client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.current_response = None
        
        skills_msg, skills = get_skills()
        self.message_history = [skills_msg]  
        self.skills = skills      
        
    @debug_agent
    def prompt(self, args):
        # Hand off prompt parsing to our helper module
        new_messages = process_user_prompt(args.p, self.skills)
        self.message_history.extend(new_messages)
        
        # Run loop
        final_message = self._start_agent_loop()
        return final_message
    
    @debug_trace
    def _start_agent_loop(self):
        """main loop that interacts with LLM
        
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
        
            # get message and update message history.    
            msg = response.choices[0].message
            self.message_history.append(msg)

            tool_calls = extract_tool_calls(msg)
            if tool_calls is None:
                break
        
            new_msgs = handle_tool_calls(self, tool_calls)
            self.message_history.extend(new_msgs)
        
        # This is the final message
        return msg.content
    
    @debug_agent
    def prompt_subagent(self, skill_name, msg):
        """Spins up a subagent, feeds it the skill body, and returns the wrapped tool message."""
        tool_call_id = msg["tool_call_id"]
        skill_body = msg["content"]
        
        subagent = Agent(debug=self.debug)
        subagent.message_history = [{"role": "user", "content": skill_body}]
        subagent_answer = subagent._start_agent_loop()

        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": f"Skill {skill_name} ran in a separate context and returned: {subagent_answer}"
        }


    
    