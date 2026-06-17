import type {
  AccountType,
  ApplicantInput,
  Application,
  AuditEntry,
  Document as KycDocument,
  LivenessResult,
  ManagerWithLoad,
  OnboardingStage,
  RiskLevel,
  SanctionsResult,
  Stats,
  Status,
} from "./types";

interface DocumentUploadResponse {
  document: KycDocument;
  ocr_extracted: Record<string, string>;
}

const BASE = "/api";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listApplications(
    params: { status?: Status; risk?: RiskLevel; stage?: OnboardingStage; q?: string } = {},
  ): Promise<Application[]> {
    const qs = new URLSearchParams();
    if (params.status) qs.set("status", params.status);
    if (params.risk) qs.set("risk", params.risk);
    if (params.stage) qs.set("stage", params.stage);
    if (params.q) qs.set("q", params.q);
    const suffix = qs.toString() ? `?${qs}` : "";
    return fetch(`${BASE}/applications${suffix}`).then(handle<Application[]>);
  },

  getApplication(id: string): Promise<Application> {
    return fetch(`${BASE}/applications/${id}`).then(handle<Application>);
  },

  createApplication(applicant: ApplicantInput): Promise<Application> {
    return fetch(`${BASE}/applications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(applicant),
    }).then(handle<Application>);
  },

  uploadDocument(id: string, file: File, docType: string): Promise<DocumentUploadResponse> {
    const fd = new FormData();
    fd.append("file", file);
    fd.append("doc_type", docType);
    return fetch(`${BASE}/applications/${id}/documents`, { method: "POST", body: fd }).then(handle<DocumentUploadResponse>);
  },

  runLiveness(id: string, file?: File): Promise<LivenessResult> {
    let body: FormData | undefined;
    if (file) {
      body = new FormData();
      body.append("file", file);
    }
    return fetch(`${BASE}/applications/${id}/liveness`, { method: "POST", body }).then(handle<LivenessResult>);
  },

  rerunSanctions(id: string): Promise<SanctionsResult> {
    return fetch(`${BASE}/applications/${id}/sanctions`, { method: "POST" }).then(handle<SanctionsResult>);
  },

  decide(id: string, payload: { outcome: "approved" | "rejected"; reviewer: string; note: string }): Promise<Application> {
    return fetch(`${BASE}/applications/${id}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then(handle<Application>);
  },

  listAudit(applicationId?: string): Promise<AuditEntry[]> {
    const qs = applicationId ? `?application_id=${applicationId}` : "";
    return fetch(`${BASE}/audit${qs}`).then(handle<AuditEntry[]>);
  },

  getStats(): Promise<Stats> {
    return fetch(`${BASE}/stats`).then(handle<Stats>);
  },

  createAccount(id: string, payload: { type: AccountType; currency: string; initial_deposit: number }): Promise<Application> {
    return fetch(`${BASE}/applications/${id}/account`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }).then(handle<Application>);
  },

  assignRelationshipManager(id: string, managerId?: string): Promise<Application> {
    return fetch(`${BASE}/applications/${id}/relationship-manager`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ manager_id: managerId ?? null }),
    }).then(handle<Application>);
  },

  listRelationshipManagers(): Promise<ManagerWithLoad[]> {
    return fetch(`${BASE}/relationship-managers`).then(handle<ManagerWithLoad[]>);
  },
};

export const stageOrder: OnboardingStage[] = [
  "kyc",
  "account_creation",
  "rm_assignment",
  "completed",
];

export const stageLabels: Record<OnboardingStage, string> = {
  kyc: "KYC verification",
  account_creation: "Account creation",
  rm_assignment: "Relationship manager",
  completed: "Completed",
};
