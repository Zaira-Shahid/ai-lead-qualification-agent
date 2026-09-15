import os

from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Groq offers an OpenAI-SDK-compatible API. If GROQ_API_KEY is set, the AI
# service points the OpenAI SDK client at Groq's base URL and uses this key
# instead of calling OpenAI directly. See README for how to switch back.
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./leads.db")

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook/lead-qualified")

NOTIFICATION_EMAIL = os.getenv("NOTIFICATION_EMAIL", "team@example.com")
