from __future__ import annotations

from typing import Optional

from .. import audit, store
from ..domain import assess, run_check, screen
from ..errors import ApplicationAlreadyDecided, ApplicationNotFound
from ..utils import utcnow
from ..models import (
    ApplicantInput,
    Application,
    Decision,
    DecisionInput,
    Document,
    DocumentUploadResponse,
    LivenessResult,
    RiskLevel,
    SanctionsResult,
    Status,
)


def _require(app_id: str) -> Application:
    app_obj = store.get(app_id)
    if not app_obj:
        raise ApplicationNotFound(app_id)
    return app_obj


def list_applications(
    *,
    status: Optional[Status] = None,
    risk: Optional[RiskLevel] = None,
    q: Optional[str] = None,
) -> list[Application]:
    items = store.all_apps()
    if status:
        items = [a for a in items if a.status == status]
    if risk:
        items = [a for a in items if a.risk and a.risk.level == risk]
    if q:
        needle = q.lower()
        items = [
            a
            for a in items
            if needle in a.applicant.first_name.lower()
            or needle in a.applicant.last_name.lower()
            or needle in a.applicant.email.lower()
        ]
    return items


def get_application(app_id: str) -> Application:
    return _require(app_id)


def create_application(applicant: ApplicantInput) -> Application:
    new_app = Application(applicant=applicant)
    new_app.risk = assess(applicant)
    new_app.sanctions = screen(applicant)
    new_app.status = Status.PENDING
    store.put(new_app)
    audit.record(
        applicant.email,
        "application.created",
        new_app.id,
        risk=new_app.risk.level.value,
        sanctions_clear=new_app.sanctions.clear,
    )
    return new_app


def upload_document(
    app_id: str, content: bytes, filename: str
) -> DocumentUploadResponse:
    app_obj = _require(app_id)
    ocr = {
        "full_name": f"{app_obj.applicant.first_name} {app_obj.applicant.last_name}",
        "document_number": app_obj.applicant.id_document_number,
        "date_of_birth": app_obj.applicant.date_of_birth.isoformat(),
        "nationality": app_obj.applicant.nationality,
    }
    doc = Document(
        type=app_obj.applicant.id_document_type,
        filename=filename,
        size_bytes=len(content),
        ocr_extracted=ocr,
    )
    app_obj.documents.append(doc)
    app_obj.updated_at = utcnow()
    if app_obj.status == Status.PENDING:
        app_obj.status = Status.IN_REVIEW
    audit.record(
        app_obj.applicant.email,
        "document.uploaded",
        app_id,
        filename=doc.filename,
        size_bytes=doc.size_bytes,
    )
    return DocumentUploadResponse(document=doc, ocr_extracted=ocr)


def check_liveness(app_id: str, selfie: Optional[bytes] = None) -> LivenessResult:
    app_obj = _require(app_id)
    result = run_check(app_obj.applicant.email, selfie)
    app_obj.liveness = result
    app_obj.updated_at = utcnow()
    audit.record(
        app_obj.applicant.email,
        "liveness.checked",
        app_id,
        passed=result.passed,
        confidence=result.confidence,
    )
    return result


def rerun_sanctions(app_id: str) -> SanctionsResult:
    app_obj = _require(app_id)
    result = screen(app_obj.applicant)
    app_obj.sanctions = result
    app_obj.updated_at = utcnow()
    audit.record(
        "system",
        "sanctions.rescreened",
        app_id,
        clear=result.clear,
        hits=len(result.hits),
    )
    return result


def decide(app_id: str, payload: DecisionInput) -> Application:
    app_obj = _require(app_id)
    if app_obj.status in (Status.APPROVED, Status.REJECTED):
        raise ApplicationAlreadyDecided(app_id)
    decision = Decision(
        outcome=payload.outcome, reviewer=payload.reviewer, note=payload.note
    )
    app_obj.decision = decision
    app_obj.status = (
        Status.APPROVED if payload.outcome == "approved" else Status.REJECTED
    )
    app_obj.updated_at = utcnow()
    audit.record(
        payload.reviewer,
        f"application.{payload.outcome}",
        app_id,
        note=payload.note,
    )
    return app_obj
