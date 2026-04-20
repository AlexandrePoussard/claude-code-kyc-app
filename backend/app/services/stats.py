from __future__ import annotations

from collections import Counter
from datetime import date, timedelta

from .. import store
from ..models import (
    ConfidenceBucket,
    CountryCount,
    DailyCount,
    FactorCount,
    FunnelSteps,
    ReviewerStats,
    RiskCounts,
    StageCounts,
    StatsResponse,
    Status,
    StatusCounts,
)

_CONFIDENCE_BUCKETS: list[tuple[str, float, float]] = [
    ("0.50–0.60", 0.50, 0.60),
    ("0.60–0.70", 0.60, 0.70),
    ("0.70–0.80", 0.70, 0.80),
    ("0.80–0.90", 0.80, 0.90),
    ("0.90–1.00", 0.90, 1.001),  # upper bound inclusive
]


def compute() -> StatsResponse:
    apps = store.all_apps()
    total = len(apps)

    # --- status, stage & risk counts ---
    status_counter: Counter[str] = Counter(a.status.value for a in apps)
    stage_counter: Counter[str] = Counter(a.stage.value for a in apps)
    risk_counter: Counter[str] = Counter(a.risk.level.value for a in apps if a.risk)

    status_counts = StatusCounts(
        pending=status_counter.get("pending", 0),
        in_review=status_counter.get("in_review", 0),
        approved=status_counter.get("approved", 0),
        rejected=status_counter.get("rejected", 0),
    )
    stage_counts = StageCounts(
        kyc=stage_counter.get("kyc", 0),
        account_creation=stage_counter.get("account_creation", 0),
        rm_assignment=stage_counter.get("rm_assignment", 0),
        completed=stage_counter.get("completed", 0),
    )
    risk_counts = RiskCounts(
        low=risk_counter.get("low", 0),
        medium=risk_counter.get("medium", 0),
        high=risk_counter.get("high", 0),
    )

    # --- sanctions flagged ---
    sanctions_hits = sum(
        1 for a in apps if a.sanctions and not a.sanctions.clear
    )

    # --- daily submissions over the last 30 days ---
    today = date.today()
    window_start = today - timedelta(days=29)
    buckets: dict[date, int] = {
        window_start + timedelta(days=i): 0 for i in range(30)
    }
    for a in apps:
        d = a.created_at.date()
        if d in buckets:
            buckets[d] += 1
    submissions = [DailyCount(date=d, count=c) for d, c in sorted(buckets.items())]

    # --- funnel ---
    submitted = total
    documents_uploaded = sum(1 for a in apps if a.documents)
    decided = sum(1 for a in apps if a.status in (Status.APPROVED, Status.REJECTED))
    approved = status_counts.approved
    funnel = FunnelSteps(
        submitted=submitted,
        documents_uploaded=documents_uploaded,
        decided=decided,
        approved=approved,
    )

    # --- top risk factors ---
    factor_counter: Counter[str] = Counter()
    factor_labels: dict[str, str] = {}
    for a in apps:
        if not a.risk:
            continue
        for f in a.risk.factors:
            factor_counter[f.code] += 1
            factor_labels[f.code] = f.label
    top_factors = [
        FactorCount(code=code, label=factor_labels[code], count=count)
        for code, count in factor_counter.most_common(10)
    ]

    # --- top countries of residence ---
    country_counter: Counter[str] = Counter(a.applicant.address.country for a in apps)
    top_countries = [
        CountryCount(country=c, count=n) for c, n in country_counter.most_common(10)
    ]

    # --- liveness confidence histogram ---
    liveness_buckets: list[ConfidenceBucket] = []
    for label, lo, hi in _CONFIDENCE_BUCKETS:
        count = sum(
            1
            for a in apps
            if a.liveness is not None and lo <= a.liveness.confidence < hi
        )
        liveness_buckets.append(ConfidenceBucket(range=label, count=count))

    # --- reviewer leaderboard ---
    reviewer_agg: dict[str, dict[str, int]] = {}
    for a in apps:
        if not a.decision:
            continue
        stats = reviewer_agg.setdefault(a.decision.reviewer, {"approved": 0, "rejected": 0})
        stats[a.decision.outcome] += 1
    reviewer_stats = [
        ReviewerStats(reviewer=reviewer, approved=v["approved"], rejected=v["rejected"])
        for reviewer, v in sorted(
            reviewer_agg.items(), key=lambda kv: kv[1]["approved"] + kv[1]["rejected"], reverse=True
        )
    ]

    return StatsResponse(
        total=total,
        status_counts=status_counts,
        stage_counts=stage_counts,
        risk_counts=risk_counts,
        sanctions_hits=sanctions_hits,
        submissions_last_30_days=submissions,
        funnel=funnel,
        top_risk_factors=top_factors,
        top_countries=top_countries,
        liveness_confidence_buckets=liveness_buckets,
        reviewer_stats=reviewer_stats,
    )
