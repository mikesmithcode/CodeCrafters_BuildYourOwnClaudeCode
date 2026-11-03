from types import SimpleNamespace  # https://docs.python.org/3/library/types.html really useful allows dot notation


def dict_to_namespace(d):
    """Convert a dictionary to a SimpleNamespace for dot-notation access."""
    if isinstance(d, dict):
        return SimpleNamespace(**{k: dict_to_namespace(v) for k, v in d.items()})
    elif isinstance(d, list):
        return [dict_to_namespace(v) for v in d]
    else:
        return d


