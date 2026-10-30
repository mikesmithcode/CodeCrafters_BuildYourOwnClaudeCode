from openai import OpenAI
import os

from app.load_config import API_KEY, BASE_URL, DEFAULT_MODEL, CACHE_FILE
from app.helpers import dict_to_namespace, extract_tool_call, parse_args, parse_fn_name, read_file, load_cache, cache_response
from app.tools import tool_list


class AI:
    def __init__(self, clear_cache=False):
        self.client =  OpenAI(api_key=API_KEY, base_url=BASE_URL)
        self.chat=None
        if os.path.exists(CACHE_FILE) and clear_cache:
            os.remove(CACHE_FILE)
        
    
    def prompt(self, args):
        if os.path.exists(CACHE_FILE):
            chat = load_cache(CACHE_FILE)
        else:     
            chat = self.client.chat.completions.create(
                        model=DEFAULT_MODEL,
                        messages=[{"role": "user", "content": args.p}],
                        tools=tool_list,
                    )
            cache_response(chat, CACHE_FILE)
        
        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")
        
        self.chat=chat
        return chat
    
    def call_tools(self):
        return extract_tool_call(self.chat)
    
        
        