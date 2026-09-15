from app.services.qualification_service import (
    calculate_lead_score,
    get_missing_required_fields,
    is_valid_email,
    is_valid_phone,
    qualify_lead,
    service_matches_clinic_offering,
)


def test_is_valid_email():
    assert is_valid_email("sarah@example.com") is True
    assert is_valid_email("hello") is False
    assert is_valid_email(None) is False
    assert is_valid_email("") is False


def test_is_valid_phone():
    assert is_valid_phone("+1 234 567 8901") is True
    assert is_valid_phone("123") is False
    assert is_valid_phone(None) is False


def test_service_matches_clinic_offering():
    assert service_matches_clinic_offering("Cosmetic Dental Consultation") is True
    assert service_matches_clinic_offering("Physiotherapy") is True
    assert service_matches_clinic_offering("Astrology Reading") is False
    assert service_matches_clinic_offering(None) is False


def test_qualified_lead():
    # Matches PROJECT_SPEC.md Section 32 Test 1.
    result = qualify_lead(
        email="test@example.com",
        phone=None,
        service="Cosmetic Dental Consultation",
        urgency="within_2_weeks",
        booking_intent=True,
        budget_is_suitable=True,
        timeline_is_suitable=True,
    )
    assert result.lead_score == 100
    assert result.qualification_status == "qualified"
    assert result.requires_human_review is False
    assert result.missing_required_fields == []


def test_needs_review_lead():
    result = qualify_lead(
        email="test@example.com",
        phone=None,
        service="Dental Consultation",
        urgency="asap",
        booking_intent=True,
        budget_is_suitable=False,
        timeline_is_suitable=False,
    )
    assert result.lead_score == 70
    assert result.qualification_status == "needs_review"
    assert result.requires_human_review is True


def test_unqualified_lead():
    result = qualify_lead(
        email=None,
        phone=None,
        service="Dental Consultation",
        urgency="asap",
        booking_intent=False,
        budget_is_suitable=False,
        timeline_is_suitable=False,
    )
    # No valid contact: clear_service (20) + service_match (20) only.
    assert result.lead_score == 40
    assert result.qualification_status == "unqualified"
    assert result.requires_human_review is False


def test_missing_information_downgrades_qualified_to_needs_review():
    # Would otherwise score 100 (qualified), but urgency is missing.
    result = qualify_lead(
        email="test@example.com",
        phone=None,
        service="Cosmetic Dental Consultation",
        urgency=None,
        booking_intent=True,
        budget_is_suitable=True,
        timeline_is_suitable=True,
    )
    assert result.lead_score == 100
    assert result.qualification_status == "needs_review"
    assert result.requires_human_review is True
    assert result.missing_required_fields == ["urgency"]


def test_invalid_contact_does_not_score_valid_contact_points():
    # PROJECT_SPEC.md Section 32 Test 3 / Section 21 Rule 7.
    score_with_invalid_email = calculate_lead_score(
        email="hello",
        phone=None,
        service="Dental Consultation",
        booking_intent=False,
        budget_is_suitable=False,
        timeline_is_suitable=False,
    )
    # No valid contact, but service is clear and matches the clinic:
    # clear_service (20) + service_match (20), no valid_contact points.
    assert score_with_invalid_email == 40

    result = qualify_lead(
        email="hello",
        phone=None,
        service="Dental Consultation",
        urgency="asap",
        booking_intent=False,
        budget_is_suitable=False,
        timeline_is_suitable=False,
    )
    assert "contact" in result.missing_required_fields


def test_unsupported_service_does_not_score_service_match_points():
    # PROJECT_SPEC.md Section 32 Test 4.
    result = qualify_lead(
        email="test@example.com",
        phone=None,
        service="Astrology Reading",
        urgency="asap",
        booking_intent=False,
        budget_is_suitable=False,
        timeline_is_suitable=False,
    )
    # valid_contact (10) + clear_service (20) only; no service_match points.
    assert result.lead_score == 30
    assert result.qualification_status == "unqualified"


def test_score_never_exceeds_100():
    score = calculate_lead_score(
        email="test@example.com",
        phone="+1 234 567 8901",
        service="Dental Consultation",
        booking_intent=True,
        budget_is_suitable=True,
        timeline_is_suitable=True,
    )
    assert score == 100


def test_get_missing_required_fields():
    assert get_missing_required_fields(None, None, None, None) == [
        "service",
        "contact",
        "urgency",
    ]
    assert get_missing_required_fields("test@example.com", None, "Dental Consultation", "asap") == []
