import httpx

from app.services import notification_service

SAMPLE_PAYLOAD = {
    "lead_id": 1,
    "name": "Sarah",
    "email": "sarah@example.com",
    "phone": None,
    "service": "Cosmetic Dental Consultation",
    "lead_score": 85,
    "qualification_status": "qualified",
    "requires_human_review": False,
}


class _FakeResponse:
    def __init__(self, status_code=200):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=self)


def test_send_qualification_webhook_success(monkeypatch):
    monkeypatch.setattr(
        notification_service.httpx, "post", lambda url, json, timeout: _FakeResponse(200)
    )

    result = notification_service.send_qualification_webhook(SAMPLE_PAYLOAD)

    assert result is True


def test_send_qualification_webhook_connection_failure(monkeypatch):
    def raise_connect_error(url, json, timeout):
        raise httpx.ConnectError("connection refused")

    monkeypatch.setattr(notification_service.httpx, "post", raise_connect_error)

    result = notification_service.send_qualification_webhook(SAMPLE_PAYLOAD)

    assert result is False


def test_send_qualification_webhook_timeout(monkeypatch):
    def raise_timeout(url, json, timeout):
        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr(notification_service.httpx, "post", raise_timeout)

    result = notification_service.send_qualification_webhook(SAMPLE_PAYLOAD)

    assert result is False


def test_send_qualification_webhook_http_error_status(monkeypatch):
    monkeypatch.setattr(
        notification_service.httpx, "post", lambda url, json, timeout: _FakeResponse(500)
    )

    result = notification_service.send_qualification_webhook(SAMPLE_PAYLOAD)

    assert result is False
