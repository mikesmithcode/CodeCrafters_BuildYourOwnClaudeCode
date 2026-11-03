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
