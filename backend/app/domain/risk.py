from __future__ import annotations

from datetime import date

from ..models import ApplicantInput, RiskAssessment, RiskFactor, RiskLevel

HIGH_RISK_COUNTRIES = {"IR", "KP", "SY", "CU", "MM", "VE"}
MEDIUM_RISK_COUNTRIES = {"RU", "BY", "PK", "NG"}


def _age(dob: date) -> int:
    today = date.today()
    years = today.year - dob.year
    if (today.month, today.day) < (dob.month, dob.day):
        years -= 1
    return years


def assess(applicant: ApplicantInput) -> RiskAssessment:
    factors: list[RiskFactor] = []

    country = applicant.address.country.upper()
    if country in HIGH_RISK_COUNTRIES:
        factors.append(
            RiskFactor(
                code="country_high",
                label=f"Residence in high-risk country ({country})",
                weight=50,
            )
        )
    elif country in MEDIUM_RISK_COUNTRIES:
        factors.append(
            RiskFactor(
                code="country_medium",
                label=f"Residence in medium-risk country ({country})",
                weight=20,
            )
        )

    nat = applicant.nationality.upper()
    if nat != country and nat in HIGH_RISK_COUNTRIES | MEDIUM_RISK_COUNTRIES:
        factors.append(
            RiskFactor(
                code="nationality_risk",
                label=f"Nationality flagged ({nat})",
                weight=15,
            )
        )

    if applicant.politically_exposed:
        factors.append(
            RiskFactor(code="pep", label="Politically exposed person", weight=40)
        )

    age = _age(applicant.date_of_birth)
    if age < 18:
        factors.append(RiskFactor(code="minor", label="Applicant under 18", weight=100))
    elif age < 21:
        factors.append(
            RiskFactor(code="young_adult", label="Applicant under 21", weight=10)
        )
    elif age > 85:
        factors.append(
            RiskFactor(code="senior", label="Applicant over 85", weight=10)
        )

    score = sum(f.weight for f in factors)
    if score >= 50:
        level = RiskLevel.HIGH
    elif score >= 20:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    return RiskAssessment(level=level, score=score, factors=factors)
