import logging
from typing import Any, Dict

import httpx

from app.config import N8N_WEBHOOK_URL

logger = logging.getLogger(__name__)

WEBHOOK_TIMEOUT_SECONDS = 5


def send_qualification_webhook(payload: Dict[str, Any]) -> bool:
    """Send the final qualification result to n8n for orchestration.

    Per PROJECT_SPEC.md Section 21/22, n8n only orchestrates based on this
    payload and never recalculates the score/status. This call must never
    crash the caller: any failure (unreachable host, timeout, non-2xx
    response) is logged and reported back as False.
    """
    try:
        response = httpx.post(N8N_WEBHOOK_URL, json=payload, timeout=WEBHOOK_TIMEOUT_SECONDS)
        response.raise_for_status()
        logger.info(
            "n8n_webhook_sent lead_id=%s qualification_status=%s",
            payload.get("lead_id"),
            payload.get("qualification_status"),
        )
        return True
    except Exception as exc:
        logger.error(
            "n8n_webhook_failed lead_id=%s error_type=%s",
            payload.get("lead_id"),
            type(exc).__name__,
        )
        return False
