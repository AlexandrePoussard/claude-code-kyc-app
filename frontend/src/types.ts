export type Status = "pending" | "in_review" | "approved" | "rejected";
export type RiskLevel = "low" | "medium" | "high";
export type IdDocumentType = "passport" | "national_id" | "driver_license";
export type OnboardingStage =
  | "kyc"
  | "account_creation"
  | "rm_assignment"
  | "completed";
export type AccountType = "checking" | "savings" | "investment";
export type RMSpecialization = "retail" | "wealth" | "investment" | "compliance";

export interface Address {
  line1: string;
  line2?: string | null;
  city: string;
  postal_code: string;
  country: string;
}

export interface ApplicantInput {
  first_name: string;
  last_name: string;
  email: string;
  date_of_birth: string;
  nationality: string;
  address: Address;
  id_document_type: IdDocumentType;
  id_document_number: string;
  politically_exposed: boolean;
}

export interface RiskFactor {
  code: string;
  label: string;
  weight: number;
}

export interface RiskAssessment {
  level: RiskLevel;
  score: number;
  factors: RiskFactor[];
}

export interface SanctionsHit {
  list_name: string;
  matched_name: string;
  score: number;
  reason: string;
}

export interface SanctionsResult {
  checked_at: string;
  hits: SanctionsHit[];
  clear: boolean;
}

export interface LivenessResult {
  checked_at: string;
  passed: boolean;
  confidence: number;
  challenge: string;
}

export interface Document {
  id: string;
  type: IdDocumentType;
  filename: string;
  size_bytes: number;
  uploaded_at: string;
  ocr_extracted: Record<string, string>;
}

export interface Decision {
  outcome: "approved" | "rejected";
  reviewer: string;
  note: string;
  decided_at: string;
}

export interface BankAccount {
  account_number: string;
  type: AccountType;
  currency: string;
  opened_at: string;
  initial_deposit: number;
}

export interface RelationshipManager {
  id: string;
  name: string;
  email: string;
  specialization: RMSpecialization;
  languages: string[];
}

export interface ManagerWithLoad {
  manager: RelationshipManager;
  assigned_count: number;
}

export interface AssignedRM {
  manager: RelationshipManager;
  assigned_at: string;
  reason: string;
}

export interface Application {
  id: string;
  applicant: ApplicantInput;
  status: Status;
  stage: OnboardingStage;
  created_at: string;
  updated_at: string;
  risk: RiskAssessment | null;
  sanctions: SanctionsResult | null;
  liveness: LivenessResult | null;
  documents: Document[];
  decision: Decision | null;
  account: BankAccount | null;
  relationship_manager: AssignedRM | null;
}

export interface AuditEntry {
  id: string;
  at: string;
  actor: string;
  action: string;
  application_id: string | null;
  details: Record<string, unknown>;
}

export interface StatusCounts {
  pending: number;
  in_review: number;
  approved: number;
  rejected: number;
}

export interface RiskCounts {
  low: number;
  medium: number;
  high: number;
}

export interface DailyCount {
  date: string;
  count: number;
}

export interface FunnelSteps {
  submitted: number;
  documents_uploaded: number;
  decided: number;
  approved: number;
}

export interface FactorCount {
  code: string;
  label: string;
  count: number;
}

export interface CountryCount {
  country: string;
  count: number;
}

export interface ConfidenceBucket {
  range: string;
  count: number;
}

export interface ReviewerStatsEntry {
  reviewer: string;
  approved: number;
  rejected: number;
}

export interface StageCounts {
  kyc: number;
  account_creation: number;
  rm_assignment: number;
  completed: number;
}

export interface Stats {
  total: number;
  status_counts: StatusCounts;
  stage_counts: StageCounts;
  risk_counts: RiskCounts;
  sanctions_hits: number;
  submissions_last_30_days: DailyCount[];
  funnel: FunnelSteps;
  top_risk_factors: FactorCount[];
  top_countries: CountryCount[];
  liveness_confidence_buckets: ConfidenceBucket[];
  reviewer_stats: ReviewerStatsEntry[];
}
