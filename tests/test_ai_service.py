import json

import httpx2
import pytest
from openai import APIConnectionError

from app.services import ai_service


class _FakeMessage:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMessage(content)


class _FakeCompletion:
    def __init__(self, content):
        self.choices = [_FakeChoice(content)]


class _FakeCompletions:
    def __init__(self, create_fn):
        self.create = create_fn


class _FakeChat:
    def __init__(self, create_fn):
        self.completions = _FakeCompletions(create_fn)


class _FakeClient:
    def __init__(self, create_fn):
        self.chat = _FakeChat(create_fn)


def _patch_client(monkeypatch, create_fn):
    monkeypatch.setattr(ai_service, "_get_client", lambda: _FakeClient(create_fn))


VALID_PAYLOAD = {
    "reply": "Hi there!",
    "intent": "dental_cosmetic_consultation",
    "lead": {
        "name": "Sarah",
        "email": None,
        "phone": None,
        "service": "Cosmetic Dental Consultation",
        "urgency": None,
        "budget": None,
        "preferred_time": None,
    },
    "missing_fields": ["email", "urgency"],
    "booking_intent": False,
    "service_matches_clinic": True,
    "budget_is_suitable": False,
    "timeline_is_suitable": False,
    "conversation_summary": "Lead wants a cosmetic dental consultation.",
    "is_emergency": False,
}


def test_get_ai_response_valid(monkeypatch):
    def fake_create(**kwargs):
        return _FakeCompletion(json.dumps(VALID_PAYLOAD))

    _patch_client(monkeypatch, fake_create)

    result = ai_service.get_ai_response([{"role": "user", "content": "hi"}])

    assert result.reply == "Hi there!"
    assert result.lead.name == "Sarah"
    assert result.service_matches_clinic is True
    assert result.is_emergency is False


def test_get_ai_response_invalid_json_retries_then_fails(monkeypatch):
    calls = {"count": 0}

    def fake_create(**kwargs):
        calls["count"] += 1
        return _FakeCompletion("this is not json")

    _patch_client(monkeypatch, fake_create)

    with pytest.raises(ai_service.AIServiceError):
        ai_service.get_ai_response([{"role": "user", "content": "hi"}])

    assert calls["count"] == ai_service.MAX_AI_ATTEMPTS


def test_get_ai_response_recovers_after_one_invalid_attempt(monkeypatch):
    calls = {"count": 0}

    def fake_create(**kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            return _FakeCompletion("not valid json")
        return _FakeCompletion(json.dumps(VALID_PAYLOAD))

    _patch_client(monkeypatch, fake_create)

    result = ai_service.get_ai_response([{"role": "user", "content": "hi"}])

    assert calls["count"] == 2
    assert result.reply == "Hi there!"


def test_get_ai_response_api_failure_raises_service_error(monkeypatch):
    request = httpx2.Request("POST", "https://api.openai.com/v1/chat/completions")

    def fake_create(**kwargs):
        raise APIConnectionError(request=request)

    _patch_client(monkeypatch, fake_create)

    with pytest.raises(ai_service.AIServiceError):
        ai_service.get_ai_response([{"role": "user", "content": "hi"}])


def test_get_ai_response_none_content_raises_service_error_not_unhandled(monkeypatch):
    # Regression test: a None message.content (e.g. from content filtering)
    # previously raised an uncaught TypeError from json.loads(None), escaping
    # the bounded-retry loop entirely instead of resulting in AIServiceError.
    def fake_create(**kwargs):
        return _FakeCompletion(None)

    _patch_client(monkeypatch, fake_create)

    with pytest.raises(ai_service.AIServiceError):
        ai_service.get_ai_response([{"role": "user", "content": "hi"}])


def test_get_ai_response_empty_choices_raises_service_error_not_unhandled(monkeypatch):
    # Regression test: an empty choices list previously raised an uncaught
    # IndexError from response.choices[0], escaping the bounded-retry loop.
    class _EmptyChoicesCompletion:
        choices = []

    def fake_create(**kwargs):
        return _EmptyChoicesCompletion()

    _patch_client(monkeypatch, fake_create)

    with pytest.raises(ai_service.AIServiceError):
        ai_service.get_ai_response([{"role": "user", "content": "hi"}])
