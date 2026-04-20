"""Static relationship manager pool + auto-matching logic.

Workshop note: this is deliberately a hardcoded list. A real bank would have an
HR directory and a matching service; here we fake both so the feature can ship
without persistence or external calls.
"""

from __future__ import annotations

from ..models import (
    AccountType,
    Application,
    RelationshipManager,
    RiskLevel,
    RMSpecialization,
)

MANAGERS: list[RelationshipManager] = [
    RelationshipManager(
        id="rm-001",
        name="Sophie Laurent",
        email="sophie.laurent@bank.example",
        specialization=RMSpecialization.WEALTH,
        languages=["fr", "en"],
    ),
    RelationshipManager(
        id="rm-002",
        name="Marcus Chen",
        email="marcus.chen@bank.example",
        specialization=RMSpecialization.INVESTMENT,
        languages=["en", "zh"],
    ),
    RelationshipManager(
        id="rm-003",
        name="Isabella Rossi",
        email="isabella.rossi@bank.example",
        specialization=RMSpecialization.INVESTMENT,
        languages=["it", "en", "fr"],
    ),
    RelationshipManager(
        id="rm-004",
        name="David Okonkwo",
        email="david.okonkwo@bank.example",
        specialization=RMSpecialization.COMPLIANCE,
        languages=["en"],
    ),
    RelationshipManager(
        id="rm-005",
        name="Priya Sharma",
        email="priya.sharma@bank.example",
        specialization=RMSpecialization.RETAIL,
        languages=["en", "hi"],
    ),
    RelationshipManager(
        id="rm-006",
        name="Thomas Müller",
        email="thomas.mueller@bank.example",
        specialization=RMSpecialization.RETAIL,
        languages=["de", "en"],
    ),
]

_BY_ID: dict[str, RelationshipManager] = {m.id: m for m in MANAGERS}


# rough mapping from ISO-2 country code to primary language.
# Incomplete on purpose — used as a *preference* in matching, not a hard gate.
_COUNTRY_LANG: dict[str, str] = {
    "FR": "fr", "BE": "fr", "LU": "fr", "CH": "fr",
    "DE": "de", "AT": "de",
    "IT": "it",
    "CN": "zh", "HK": "zh", "TW": "zh",
    "IN": "hi",
}


def all_managers() -> list[RelationshipManager]:
    return list(MANAGERS)


def get_by_id(manager_id: str) -> RelationshipManager | None:
    return _BY_ID.get(manager_id)


def match(app: Application) -> tuple[RelationshipManager, str]:
    """Return the best-matched RM for an application and a short human reason.

    Priority:
        1. High-risk profile → compliance specialist.
        2. Investment account → investment specialist.
        3. Otherwise → retail for low risk, wealth for medium.
        4. Tie-break by language preference (applicant country → RM language).
    """

    required: RMSpecialization
    reason_parts: list[str] = []

    if app.risk and app.risk.level == RiskLevel.HIGH:
        required = RMSpecialization.COMPLIANCE
        reason_parts.append("high-risk profile")
    elif app.account and app.account.type == AccountType.INVESTMENT:
        required = RMSpecialization.INVESTMENT
        reason_parts.append("investment account")
    elif app.risk and app.risk.level == RiskLevel.MEDIUM:
        required = RMSpecialization.WEALTH
        reason_parts.append("medium-risk profile")
    else:
        required = RMSpecialization.RETAIL
        reason_parts.append("retail profile")

    candidates = [m for m in MANAGERS if m.specialization == required]
    if not candidates:
        # Fallback: any manager.
        candidates = list(MANAGERS)
        reason_parts.append("no specialist available, fell back to generalist")

    preferred_lang = _COUNTRY_LANG.get(app.applicant.address.country.upper())
    if preferred_lang:
        lang_match = [m for m in candidates if preferred_lang in m.languages]
        if lang_match:
            candidates = lang_match
            reason_parts.append(f"language match ({preferred_lang})")

    chosen = candidates[0]
    reason = "; ".join(reason_parts)
    return chosen, reason
