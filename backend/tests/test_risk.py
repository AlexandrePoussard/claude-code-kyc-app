from __future__ import annotations

from datetime import date

from app.domain.risk import assess
from app.models import RiskLevel


def test_clean_profile_is_low_risk(applicant_factory):
    result = assess(applicant_factory())
    assert result.level == RiskLevel.LOW
    assert result.score == 0
    assert result.factors == []


def test_high_risk_country_flags_high(applicant_factory):
    from app.models import Address
    applicant = applicant_factory(
        address=Address(line1="1", city="Tehran", postal_code="1", country="IR"),
    )
    result = assess(applicant)
    assert result.level == RiskLevel.HIGH
    assert any(f.code == "country_high" for f in result.factors)


def test_medium_risk_country_flags_medium(applicant_factory):
    from app.models import Address
    applicant = applicant_factory(
        address=Address(line1="1", city="Moscow", postal_code="1", country="RU"),
        nationality="FR",
    )
    result = assess(applicant)
    assert result.level == RiskLevel.MEDIUM
    assert any(f.code == "country_medium" for f in result.factors)


def test_pep_adds_weight(applicant_factory):
    result = assess(applicant_factory(politically_exposed=True))
    assert any(f.code == "pep" and f.weight == 40 for f in result.factors)
    assert result.level == RiskLevel.MEDIUM


def test_minor_is_forced_high_risk(applicant_factory):
    # 10 years old
    result = assess(applicant_factory(date_of_birth=date.today().replace(year=date.today().year - 10)))
    assert result.level == RiskLevel.HIGH
    assert any(f.code == "minor" for f in result.factors)


def test_young_adult_adds_small_weight(applicant_factory):
    result = assess(applicant_factory(date_of_birth=date.today().replace(year=date.today().year - 20)))
    assert any(f.code == "young_adult" for f in result.factors)


def test_senior_adds_small_weight(applicant_factory):
    result = assess(applicant_factory(date_of_birth=date.today().replace(year=date.today().year - 90)))
    assert any(f.code == "senior" for f in result.factors)


def test_scores_sum_factor_weights(applicant_factory):
    from app.models import Address
    applicant = applicant_factory(
        politically_exposed=True,
        address=Address(line1="1", city="Moscow", postal_code="1", country="RU"),
    )
    result = assess(applicant)
    assert result.score == sum(f.weight for f in result.factors)
    assert result.level == RiskLevel.HIGH  # 40 (PEP) + 20 (country_medium) = 60
