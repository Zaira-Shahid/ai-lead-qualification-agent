import json
import logging
from pathlib import Path
from typing import Dict, List

from openai import OpenAI, OpenAIError

from app.config import GROQ_API_KEY, GROQ_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL
from app.schemas.ai_response import AIResponse

logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "prompts" / "lead_agent_prompt.txt"
SYSTEM_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8")

REQUEST_TIMEOUT_SECONDS = 15
MAX_AI_ATTEMPTS = 2

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if GROQ_API_KEY:
            _client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL, max_retries=0)
        else:
            _client = OpenAI(api_key=OPENAI_API_KEY, max_retries=0)
    return _client


class AIServiceError(Exception):
    """Raised when the AI service cannot produce a valid structured response
    after bounded retries."""


def _call_openai(messages: List[Dict[str, str]]) -> str:
    logger.info("ai_request_started")
    response = _get_client().chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    logger.info("ai_response_received")

    if not response.choices:
        raise ValueError("AI response contained no choices")

    content = response.choices[0].message.content
    if not content:
        raise ValueError("AI response content was empty")

    return content


def get_ai_response(conversation_messages: List[Dict[str, str]]) -> AIResponse:
    """Send the conversation to the AI and return a validated structured
    response.

    conversation_messages is the chat history (user/assistant turns) without
    the system prompt, which this function prepends.

    Raises AIServiceError if no valid structured response could be obtained
    within MAX_AI_ATTEMPTS bounded attempts (covers both API failures and
    invalid/unparsable JSON).
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_messages

    last_error: Exception | None = None

    for attempt in range(1, MAX_AI_ATTEMPTS + 1):
        try:
            raw_content = _call_openai(messages)
        except (OpenAIError, ValueError, IndexError, TypeError) as exc:
            logger.error("ai_request_failed attempt=%s error_type=%s", attempt, type(exc).__name__)
            last_error = exc
            continue

        try:
            parsed = json.loads(raw_content)
            return AIResponse.model_validate(parsed)
        except (json.JSONDecodeError, ValueError, TypeError) as exc:
            logger.error("ai_response_invalid attempt=%s", attempt)
            last_error = exc
            messages.append({"role": "assistant", "content": raw_content})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "Your previous response was not valid JSON matching the required "
                        "schema. Respond again with a single valid JSON object only, "
                        "matching the exact structure described in the system prompt."
                    ),
                }
            )
            continue

    raise AIServiceError("AI service failed to produce a valid response") from last_error
