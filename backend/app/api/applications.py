from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile

from ..models import (
    ApplicantInput,
    Application,
    DecisionInput,
    DocumentUploadResponse,
    LivenessResult,
    OnboardingStage,
    RiskLevel,
    SanctionsResult,
    Status,
)
from ..services import applications as service

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[Application])
def list_applications(
    status: Optional[Status] = None,
    risk: Optional[RiskLevel] = None,
    stage: Optional[OnboardingStage] = None,
    q: Optional[str] = None,
) -> list[Application]:
    return service.list_applications(status=status, risk=risk, stage=stage, q=q)


@router.post("", response_model=Application, status_code=201)
def create_application(applicant: ApplicantInput) -> Application:
    return service.create_application(applicant)


@router.get("/{app_id}", response_model=Application)
def get_application(app_id: str) -> Application:
    return service.get_application(app_id)


@router.post("/{app_id}/documents", response_model=DocumentUploadResponse)
async def upload_document(
    app_id: str,
    file: UploadFile = File(...),
    doc_type: str = Form(...),
) -> DocumentUploadResponse:
    content = await file.read()
    return service.upload_document(app_id, content, file.filename or "document")


@router.post("/{app_id}/liveness", response_model=LivenessResult)
async def check_liveness(
    app_id: str, file: Optional[UploadFile] = File(default=None)
) -> LivenessResult:
    payload = await file.read() if file is not None else None
    return service.check_liveness(app_id, payload)


@router.post("/{app_id}/sanctions", response_model=SanctionsResult)
def rerun_sanctions(app_id: str) -> SanctionsResult:
    return service.rerun_sanctions(app_id)


@router.post("/{app_id}/decision", response_model=Application)
def decide(app_id: str, payload: DecisionInput) -> Application:
    return service.decide(app_id, payload)
