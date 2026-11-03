
import json

def tool_response(tool_call_id, content):
    return {"role": "tool",
            "tool_call_id": tool_call_id,
            "content": content}

def extract_tool_calls(message):
    """Extracts the tool_calls from the openai response"""
    try:
        if hasattr(message, "tool_calls") and message.tool_calls and len(message.tool_calls) > 0:
            return message.tool_calls
        return None
    except Exception as e:
        print(f"Error extracting tool_call: {e}")
        return None
        
def parse_tool_call(tool_call):
    fn_name = tool_call.function.name
    id = tool_call.id
    args = json.loads(tool_call.function.arguments)
    return (fn_name, id, args)



"""----------------------------------------------------------------------------------------------------
Tools
----------------------------------------------------------------------------------------------------"""

def Read(tool_call_id, filepath):
    with open(filepath, 'r') as f:
        return tool_response(tool_call_id, f.read())

tool_list = [
                {
                    "type": "function",
                    "function": {
                        "name": "Read",
                        "description": "Read and return the contents of a file",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "file_path": {
                                    "type": "string",
                                    "description": "The path to the file to read",
                                }
                            },
                            "required": ["file_path"],
                        },
                    },
                }
            ]


