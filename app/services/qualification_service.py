import re
from dataclasses import dataclass, field
from typing import List, Optional

from app.config import (
    CLINIC_SERVICE_KEYWORDS,
    QUALIFIED_THRESHOLD,
    REVIEW_THRESHOLD,
    SCORING_RULES,
)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_DIGIT_RE = re.compile(r"\d")


def is_valid_email(email: Optional[str]) -> bool:
    if not email:
        return False
    return bool(_EMAIL_RE.match(email.strip()))


def is_valid_phone(phone: Optional[str]) -> bool:
    if not phone:
        return False
    digit_count = len(_DIGIT_RE.findall(phone))
    return 7 <= digit_count <= 15


def has_valid_contact(email: Optional[str], phone: Optional[str]) -> bool:
    return is_valid_email(email) or is_valid_phone(phone)


def service_matches_clinic_offering(service: Optional[str]) -> bool:
    """Independently verify the requested service against the clinic's
    offerings (PROJECT_SPEC.md Section 3), rather than trusting the AI's own
    service_matches_clinic flag, per Section 21 Rule 8."""
    if not service:
        return False
    service_lower = service.lower()
    return any(keyword in service_lower for keyword in CLINIC_SERVICE_KEYWORDS)


def get_missing_required_fields(
    email: Optional[str], phone: Optional[str], service: Optional[str], urgency: Optional[str]
) -> List[str]:
    """Required minimum information per PROJECT_SPEC.md Section 10: service,
    a valid email OR valid phone, and urgency/timeline."""
    missing = []
    if not service:
        missing.append("service")
    if not has_valid_contact(email, phone):
        missing.append("contact")
    if not urgency:
        missing.append("urgency")
    return missing


def calculate_lead_score(
    email: Optional[str],
    phone: Optional[str],
    service: Optional[str],
    booking_intent: bool,
    budget_is_suitable: bool,
    timeline_is_suitable: bool,
) -> int:
    """Deterministic scoring per PROJECT_SPEC.md Section 9/20. Contact
    validity and service match are computed independently by the backend
    (Section 21 Rules 7 and 8) rather than trusted from AI output; booking
    intent, budget suitability, and timeline suitability are taken from the
    AI's structured extraction, per Section 20's reference implementation."""
    score = 0

    if has_valid_contact(email, phone):
        score += SCORING_RULES["valid_contact"]

    if service:
        score += SCORING_RULES["clear_service"]

    if service_matches_clinic_offering(service):
        score += SCORING_RULES["service_match"]

    if booking_intent:
        score += SCORING_RULES["booking_intent"]

    if budget_is_suitable:
        score += SCORING_RULES["suitable_budget"]

    if timeline_is_suitable:
        score += SCORING_RULES["suitable_timeline"]

    return min(score, 100)


def determine_status_from_score(score: int) -> str:
    if score >= QUALIFIED_THRESHOLD:
        return "qualified"
    elif score >= REVIEW_THRESHOLD:
        return "needs_review"
    else:
        return "unqualified"


@dataclass
class QualificationResult:
    lead_score: int
    qualification_status: str
    requires_human_review: bool
    missing_required_fields: List[str] = field(default_factory=list)


def qualify_lead(
    *,
    email: Optional[str],
    phone: Optional[str],
    service: Optional[str],
    urgency: Optional[str],
    booking_intent: bool,
    budget_is_suitable: bool,
    timeline_is_suitable: bool,
) -> QualificationResult:
    """Deterministic qualification engine. Does not depend on an LLM.

    Per PROJECT_SPEC.md Section 21 Rule 6, a missing required field prevents
    a lead from being finalized as "qualified": if required information is
    missing, a score that would otherwise qualify is downgraded to
    "needs_review" rather than upgraded to "qualified".
    """
    score = calculate_lead_score(
        email, phone, service, booking_intent, budget_is_suitable, timeline_is_suitable
    )
    status = determine_status_from_score(score)
    missing_fields = get_missing_required_fields(email, phone, service, urgency)

    if missing_fields and status == "qualified":
        status = "needs_review"

    requires_human_review = status == "needs_review"

    return QualificationResult(
        lead_score=score,
        qualification_status=status,
        requires_human_review=requires_human_review,
        missing_required_fields=missing_fields,
    )
