import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# Check for OpenRouter first, then fallback to OpenAI API key
API_KEY = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")

# Only use BASE_URL if explicitly set in the environment (e.g. OpenRouter).
# If None, the OpenAI client defaults to OpenAI's official servers.
BASE_URL = os.getenv("OPENROUTER_BASE_URL")

# Automatically choose model: use OpenAI model for OpenAI keys, otherwise CodeCrafters default
if API_KEY and API_KEY.startswith("sk-proj-"):
    DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
else:
    DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "anthropic/claude-haiku-4.5")

CACHE_FILE = 'temp_call.json'