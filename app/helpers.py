from types import SimpleNamespace  # https://docs.python.org/3/library/types.html really useful allows dot notation
import json

def dict_to_namespace(d):
    """Convert a dictionary to a SimpleNamespace for dot-notation access."""
    if isinstance(d, dict):
        return SimpleNamespace(**{k: dict_to_namespace(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [dict_to_namespace(v) for v in d]
    else:
        return d


def extract_tool_call(response):
    """Extract the tool_call from the openai response"""
    try:
        message = response.choices[0].message
        if hasattr(message, "tool_calls") and message.tool_calls and len(message.tool_calls) > 0:
            return message.tool_calls[0]
        return None
    except Exception as e:
        print(f"Error extracting tool_call: {e}")
        return None

def extract_text_response(response):
   return response.choices[0].message.content
   

def parse_fn_name(tool_call):
    return tool_call.function.name


def parse_args(tool_call):
    return json.loads(tool_call.function.arguments)


def read_file(filepath):
    with open(filepath) as f:
        file_contents = f.read()
    return file_contents

def load_cache(filepath):
    with open(filepath, 'r') as f:
        chat_dict = json.load(f)
        chat = dict_to_namespace(chat_dict)
    return chat

def cache_response(response, filepath):
    # Save response to cache
    with open(filepath, 'w') as f:
        json.dump(response.model_dump(), f, indent=2)
