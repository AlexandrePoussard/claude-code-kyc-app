from __future__ import annotations

import hashlib
import random

from ..models import LivenessResult
from ..utils import utcnow

CHALLENGES = [
    "Turn your head slowly to the left",
    "Blink twice then smile",
    "Tilt your head to the right",
    "Say the code 7-4-2 aloud",
    "Look up then back at the camera",
]


def run_check(applicant_email: str, selfie_payload: bytes | None = None) -> LivenessResult:
    """Fake liveness check. Determinism keyed on email so repeat runs are stable."""
    seed = int(hashlib.sha256(applicant_email.encode()).hexdigest(), 16)
    rng = random.Random(seed)
    confidence = round(rng.uniform(0.55, 0.99), 2)
    passed = confidence >= 0.7
    challenge = rng.choice(CHALLENGES)
    if selfie_payload is not None and len(selfie_payload) < 100:
        passed = False
        confidence = min(confidence, 0.4)
    return LivenessResult(
        checked_at=utcnow(),
        passed=passed,
        confidence=confidence,
        challenge=challenge,
    )
