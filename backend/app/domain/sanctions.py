from __future__ import annotations

from ..models import ApplicantInput, SanctionsHit, SanctionsResult
from ..utils import utcnow

# Fake watchlist — names are fictional but styled after public OFAC/EU formats.
WATCHLIST: list[dict] = [
    {
        "list_name": "OFAC SDN (mock)",
        "name": "Ivan Volkov",
        "reason": "Designated under EO 14024",
    },
    {
        "list_name": "EU Consolidated (mock)",
        "name": "Maria Delacroix",
        "reason": "Council Regulation 2022/xxx",
    },
    {
        "list_name": "UN 1267 (mock)",
        "name": "Abdul Rahim",
        "reason": "Entity associated with listed group",
    },
    {
        "list_name": "UK HMT (mock)",
        "name": "Chen Wei",
        "reason": "Asset freeze target",
    },
    {
        "list_name": "Interpol Red Notice (mock)",
        "name": "Sofia Marquez",
        "reason": "Wanted for financial fraud",
    },
]


def _similarity(a: str, b: str) -> float:
    a_tokens = set(a.lower().split())
    b_tokens = set(b.lower().split())
    if not a_tokens or not b_tokens:
        return 0.0
    overlap = a_tokens & b_tokens
    return len(overlap) / max(len(a_tokens), len(b_tokens))


def screen(applicant: ApplicantInput) -> SanctionsResult:
    full_name = f"{applicant.first_name} {applicant.last_name}"
    hits: list[SanctionsHit] = []
    for entry in WATCHLIST:
        score = _similarity(full_name, entry["name"])
        if score >= 0.5:
            hits.append(
                SanctionsHit(
                    list_name=entry["list_name"],
                    matched_name=entry["name"],
                    score=round(score, 2),
                    reason=entry["reason"],
                )
            )
    return SanctionsResult(
        checked_at=utcnow(),
        hits=hits,
        clear=len(hits) == 0,
    )
