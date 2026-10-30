import argparse
import os
import sys

from app.ai import AI
from app.helpers import extract_tool_call, parse_fn_name, parse_args, extract_text_response
from app.tools import Read

def main():   
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()
    
    ai=AI(clear_cache=True)
    chat = ai.prompt(args)    
    tool_call=ai.call_tools()
    
    if tool_call is None:
        msg =extract_text_response(chat)
    else:
        fn_name=parse_fn_name(tool_call)
        arguments = parse_args(tool_call)
        if fn_name == 'Read':
            msg =Read(arguments["file_path"])
        else:
            msg="tool"
    
    print(msg)
    
    


if __name__ == "__main__":
    main()