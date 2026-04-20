from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal, Optional
from uuid import uuid4

from pydantic import BaseModel, EmailStr, Field

from .utils import utcnow


class Status(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class IdDocumentType(str, Enum):
    PASSPORT = "passport"
    NATIONAL_ID = "national_id"
    DRIVER_LICENSE = "driver_license"


class OnboardingStage(str, Enum):
    """Stage of the end-to-end client onboarding journey."""

    KYC = "kyc"
    ACCOUNT_CREATION = "account_creation"
    RM_ASSIGNMENT = "rm_assignment"
    COMPLETED = "completed"


class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    INVESTMENT = "investment"


class RMSpecialization(str, Enum):
    RETAIL = "retail"
    WEALTH = "wealth"
    INVESTMENT = "investment"
    COMPLIANCE = "compliance"


class Address(BaseModel):
    line1: str
    line2: Optional[str] = None
    city: str
    postal_code: str
    country: str  # ISO-2


class ApplicantInput(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    date_of_birth: date
    nationality: str  # ISO-2
    address: Address
    id_document_type: IdDocumentType
    id_document_number: str
    politically_exposed: bool = False


class RiskFactor(BaseModel):
    code: str
    label: str
    weight: int


class RiskAssessment(BaseModel):
    level: RiskLevel
    score: int
    factors: list[RiskFactor]


class SanctionsHit(BaseModel):
    list_name: str
    matched_name: str
    score: float
    reason: str


class SanctionsResult(BaseModel):
    checked_at: datetime
    hits: list[SanctionsHit] = []
    clear: bool


class LivenessResult(BaseModel):
    checked_at: datetime
    passed: bool
    confidence: float
    challenge: str


class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: IdDocumentType
    filename: str
    size_bytes: int
    uploaded_at: datetime = Field(default_factory=utcnow)
    ocr_extracted: dict = Field(default_factory=dict)


class Decision(BaseModel):
    outcome: Literal["approved", "rejected"]
    reviewer: str
    note: str
    decided_at: datetime = Field(default_factory=utcnow)


class BankAccount(BaseModel):
    account_number: str
    type: AccountType
    currency: str  # ISO-4217, e.g. "EUR"
    opened_at: datetime = Field(default_factory=utcnow)
    initial_deposit: float


class AccountInput(BaseModel):
    type: AccountType
    currency: str
    initial_deposit: float


class RelationshipManager(BaseModel):
    id: str
    name: str
    email: EmailStr
    specialization: RMSpecialization
    languages: list[str]


class AssignedRM(BaseModel):
    manager: RelationshipManager
    assigned_at: datetime = Field(default_factory=utcnow)
    reason: str


class RMAssignInput(BaseModel):
    manager_id: Optional[str] = None  # if None → auto-match


class ManagerWithLoad(BaseModel):
    manager: RelationshipManager
    assigned_count: int


class Application(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    applicant: ApplicantInput
    status: Status = Status.PENDING
    stage: OnboardingStage = OnboardingStage.KYC
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    risk: Optional[RiskAssessment] = None
    sanctions: Optional[SanctionsResult] = None
    liveness: Optional[LivenessResult] = None
    documents: list[Document] = []
    decision: Optional[Decision] = None
    account: Optional[BankAccount] = None
    relationship_manager: Optional[AssignedRM] = None


class DecisionInput(BaseModel):
    outcome: Literal["approved", "rejected"]
    reviewer: str
    note: str


class DocumentUploadResponse(BaseModel):
    document: Document
    ocr_extracted: dict


class AuditEntry(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    at: datetime = Field(default_factory=utcnow)
    actor: str
    action: str
    application_id: Optional[str] = None
    details: dict = Field(default_factory=dict)


class StatusCounts(BaseModel):
    pending: int = 0
    in_review: int = 0
    approved: int = 0
    rejected: int = 0


class StageCounts(BaseModel):
    kyc: int = 0
    account_creation: int = 0
    rm_assignment: int = 0
    completed: int = 0


class RiskCounts(BaseModel):
    low: int = 0
    medium: int = 0
    high: int = 0


class DailyCount(BaseModel):
    date: date
    count: int


class FunnelSteps(BaseModel):
    submitted: int
    documents_uploaded: int
    decided: int
    approved: int


class FactorCount(BaseModel):
    code: str
    label: str
    count: int


class CountryCount(BaseModel):
    country: str
    count: int


class ConfidenceBucket(BaseModel):
    range: str
    count: int


class ReviewerStats(BaseModel):
    reviewer: str
    approved: int
    rejected: int


class StatsResponse(BaseModel):
    total: int
    status_counts: StatusCounts
    stage_counts: StageCounts
    risk_counts: RiskCounts
    sanctions_hits: int
    submissions_last_30_days: list[DailyCount]
    funnel: FunnelSteps
    top_risk_factors: list[FactorCount]
    top_countries: list[CountryCount]
    liveness_confidence_buckets: list[ConfidenceBucket]
    reviewer_stats: list[ReviewerStats]
