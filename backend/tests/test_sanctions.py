from __future__ import annotations

from app.domain.sanctions import screen


def test_clean_name_returns_clear(applicant_factory):
    result = screen(applicant_factory(first_name="Anne", last_name="Smith"))
    assert result.clear is True
    assert result.hits == []


def test_exact_watchlist_match_triggers_hit(applicant_factory):
    result = screen(applicant_factory(first_name="Ivan", last_name="Volkov"))
    assert result.clear is False
    assert len(result.hits) >= 1
    assert any("OFAC" in h.list_name for h in result.hits)


def test_partial_overlap_triggers_hit(applicant_factory):
    # "Chen Wei" is on the mock UK HMT list — 2-token exact match
    result = screen(applicant_factory(first_name="Chen", last_name="Wei"))
    assert result.clear is False


def test_hit_score_is_within_zero_one(applicant_factory):
    result = screen(applicant_factory(first_name="Ivan", last_name="Volkov"))
    for hit in result.hits:
        assert 0.0 <= hit.score <= 1.0
