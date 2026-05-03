export type Project = {
  project_id: string;
  project_no?: string | null;
  product_name: string;
  requestor: string;
  status: string;
  business_unit?: string | null;
  created_on?: string | null;
};

export type ProjectCreateInput = {
  project_no?: string | null;
  product_name: string;
  requestor: string;
  business_unit?: string;
};

export type ApplicationForm = {
  form_id: string;
  project_id: string;
  form_no: string;
  revision: string;
  requester: string;
  email?: string | null;
  project_number?: string | null;
  requested_testing?: string | null;
};

export type PrecheckIssue = {
  issue_id: string;
  category: string;
  level: string;
  message: string;
  field_name?: string | null;
  resolved: boolean;
};

export type PrecheckResult = {
  result_id: string;
  application_form_id: string;
  status: string;
  checked_on?: string | null;
  issues: PrecheckIssue[];
};

export type ProjectLookupRow = {
  project_id: string;
  project_no?: string | null;
  product_name: string;
  requestor: string;
  status: string;
  ltr_numbers: string[];
  sample_part_numbers: string[];
  matched_fields: string[];
};

export type SampleSummaryRow = {
  sample_id: string;
  product_name: string;
  part_number: string;
  revision?: string | null;
  lot_or_traceability?: string | null;
  material?: string | null;
  plating?: string | null;
  housing_material?: string | null;
  quantity?: number | null;
};

export type SampleSummary = {
  project_id: string;
  project_no?: string | null;
  product_name: string;
  requestor: string;
  ltr_numbers: string[];
  samples: SampleSummaryRow[];
};

export type TestingSummary = {
  project_id: string;
  project_no?: string | null;
  requested_testing?: string | null;
  test_type?: string | null;
  sample_condition?: string | null;
  requested_completion_date?: string | null;
  applicable_specifications: string[];
  lab?: string | null;
  assigned_personnel?: string | null;
};

export type ExceptionWorkflowIssue = {
  kind: string;
  message: string;
  operator_action: string;
  blocking: boolean;
  asset_id?: string | null;
  case_id?: string | null;
};

export type ExceptionWorkflowReview = {
  package_id: string;
  package_status: string;
  case_ids: string[];
  draft_ids: string[];
  issues: ExceptionWorkflowIssue[];
};

export type IntakeAsset = {
  asset_id: string;
  original_name: string;
  extension: string;
  mime_type?: string | null;
  size_bytes: number;
  asset_role: string;
  candidate_score?: number | null;
};

export type IntakeAssetPreviewMetadata = {
  asset_id: string;
  original_name: string;
  extension: string;
  mime_type?: string | null;
  size_bytes: number;
  asset_role: string;
};

export type IntakeAssetPreviewField = {
  label: string;
  value: string;
};

export type IntakeAssetPreviewTable = {
  title: string;
  headers: string[];
  rows: string[][];
};

export type IntakeAssetPreview = {
  kind: string;
  metadata: IntakeAssetPreviewMetadata;
  title: string;
  fields: IntakeAssetPreviewField[];
  tables: IntakeAssetPreviewTable[];
  warnings: string[];
  message?: string | null;
};

export type IntakePackageImport = {
  package_id: string;
  source_type: string;
  package_status: string;
  source_original_name: string;
  subject?: string | null;
  sender_name?: string | null;
  sender_email?: string | null;
  asset_count: number;
  candidate_count: number;
  next_action: string;
  assets: IntakeAsset[];
};

export type IntakeCaseSummary = {
  case_id: string;
  selected_form_asset_id?: string | null;
  status: string;
  confirmed_project_id?: string | null;
};

export type IntakePackageDetail = {
  package_id: string;
  source_type: string;
  package_status: string;
  source_original_name: string;
  source_stored: boolean;
  subject?: string | null;
  sender_name?: string | null;
  sender_email?: string | null;
  received_at?: string | null;
  asset_count: number;
  candidate_count: number;
  case_count: number;
  next_action: string;
  assets: IntakeAsset[];
  candidate_assets: IntakeAsset[];
  cases: IntakeCaseSummary[];
};

export type SelectedApplicationForm = {
  package_id: string;
  case_id: string;
  draft_id: string;
  selected_form_asset_id: string;
  package_status: string;
  next_action: string;
};

export type ManualIntakeInput = {
  product_name?: string | null;
  requester?: string | null;
  email?: string | null;
  business_unit?: string | null;
  project_no?: string | null;
  form_no?: string | null;
  revision?: string | null;
  requested_testing?: string | null;
  operator_notes?: string | null;
  sample?: {
    product_name?: string | null;
    part_number?: string | null;
    revision?: string | null;
    lot_or_traceability?: string | null;
    material?: string | null;
    plating?: string | null;
    housing_material?: string | null;
    quantity?: number | null;
  };
};

export type ManualIntake = {
  package_id: string;
  case_id: string;
  draft_id: string;
  package_status: string;
  selected_form_asset_id: string;
  missing_required_fields: string[];
  next_action: string;
};

export type IntakeCaseReviewField = {
  key: string;
  label: string;
  value?: unknown;
  required: boolean;
  missing: boolean;
};

export type DraftPrecheckIssue = {
  level: string;
  field_key: string;
  message: string;
};

export type IntakeCaseReviewItem = {
  case_id: string;
  status: string;
  selected_form_asset_id?: string | null;
  selected_asset_name?: string | null;
  confirmed_project_id?: string | null;
  operator_notes?: string | null;
  missing_required_fields: string[];
  confirm_allowed: boolean;
  fields: IntakeCaseReviewField[];
  sample_rows: Record<string, unknown>[];
  precheck_issues: DraftPrecheckIssue[];
};

export type IntakeCaseReview = {
  package_id: string;
  source_type: string;
  package_status: string;
  source_original_name: string;
  subject?: string | null;
  sender_name?: string | null;
  sender_email?: string | null;
  cases: IntakeCaseReviewItem[];
};

export type LookupOption = {
  value: string;
  label: string;
};

export type IntakePrecheckLookupOptions = {
  business_unit: LookupOption[];
  manufacturing_site: LookupOption[];
  results_format: LookupOption[];
  test_type: LookupOption[];
  sample_status: LookupOption[];
  project_type: LookupOption[];
  post_testing_disposition: LookupOption[];
};

export type ConfirmIntakeCase = {
  case_id: string;
  project_id: string;
  application_form_id: string;
  sample_count: number;
  file_asset_count: number;
};

export type UpdateIntakeCaseReviewFieldsInput = {
  fields: Record<string, string | null>;
  sample_rows?: Record<string, string>[];
};

export type LtrRecord = {
  ltr_id: string;
  project_id: string;
  ltr_number: string;
  status: string;
  registered_on?: string | null;
  requested_by?: string | null;
  requested_date?: string | null;
  notes?: string | null;
};

export type LtrReadinessField = {
  key: string;
  label: string;
  value?: string | null;
  source?: string | null;
  severity: string;
  state: string;
  operator_action: string;
  placeholder_policy?: string | null;
};

export type LtrReadiness = {
  project_id: string;
  status: string;
  fields: LtrReadinessField[];
  blockers: LtrReadinessField[];
  warnings: LtrReadinessField[];
};

export type LtrRegistrationType = "normal" | "associated";

export type LtrPreviewRequest = {
  year: number;
  month: number;
  registration_type: LtrRegistrationType;
  mode?: "local_only";
  proposed_ltr_number?: string | null;
};

export type LtrRegistrationPreview = {
  project_id: string;
  status: string;
  proposed_ltr_number?: string | null;
  registration_type: LtrRegistrationType;
  mode: string;
  target_write_year_sheet: string;
  number_preflight_required: boolean;
  number_preview_allowed: boolean;
  final_number_reserved: boolean;
  target_sheet?: string | null;
  target_row?: number | null;
  snapshot_fingerprint?: string | null;
  source_numbers: string[];
  readiness: LtrReadiness;
  conflicts: string[];
  warnings: string[];
  parsed_base_number?: string | null;
  base_year_sheet?: string | null;
  family_numbers: string[];
};

export type LtrLocalCommitRequest = LtrPreviewRequest & {
  operator_confirmed: boolean;
  requested_by?: string | null;
  requested_date?: string | null;
  operator_note?: string | null;
};

export type LtrLocalCommit = {
  ltr: LtrRecord;
  preview: LtrRegistrationPreview;
};

export type FolderPlanItem = {
  source_path: string;
  target_path: string;
  item_type: string;
  conflict: boolean;
};

export type FolderPlan = {
  project_folder_path: string;
  conflict: boolean;
  items: FolderPlanItem[];
};

export type FolderGeneration = {
  folder_id: string;
  project_folder_path: string;
  generated_paths: string[];
};

export type EvidencePlacementItem = {
  asset_id: string;
  category: string;
  source_path: string;
  target_path: string;
  missing_source: boolean;
  target_exists: boolean;
  duplicate_target: boolean;
  conflict: boolean;
};

export type EvidencePlacementPlan = {
  project_id: string;
  project_folder_path: string;
  evidence_root_path: string;
  conflict: boolean;
  items: EvidencePlacementItem[];
  conflicts: string[];
  warnings: string[];
};

export type EvidencePlacementResult = {
  plan: EvidencePlacementPlan;
  copied_paths: string[];
};

export type FolderRequest = {
  template_path: string;
  target_root: string;
  dl_number?: string;
  plan_date?: string;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...init?.headers
    }
  });

  if (!response.ok) {
    const message = await responseErrorMessage(response);
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

async function responseErrorMessage(response: Response): Promise<string> {
  const raw = await response.text();
  if (!raw) {
    return "";
  }
  try {
    const parsed = JSON.parse(raw) as { detail?: unknown };
    return typeof parsed.detail === "string" ? parsed.detail : raw;
  } catch {
    return raw;
  }
}

export function listProjects(): Promise<Project[]> {
  return requestJson<Project[]>("/api/projects");
}

export function createProject(input: ProjectCreateInput): Promise<Project> {
  return requestJson<Project>("/api/projects", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function getProject(projectId: string): Promise<Project> {
  return requestJson<Project>(`/api/projects/${encodeURIComponent(projectId)}`);
}

export function uploadApplicationForm(
  projectId: string,
  file: File
): Promise<ApplicationForm> {
  const formData = new FormData();
  formData.append("file", file);
  return requestJson<ApplicationForm>(
    `/api/projects/${encodeURIComponent(projectId)}/application-form`,
    {
      method: "POST",
      body: formData
    }
  );
}

export function runPrecheck(applicationFormId: string): Promise<PrecheckResult> {
  return requestJson<PrecheckResult>(
    `/api/application-forms/${encodeURIComponent(applicationFormId)}/precheck/run`,
    { method: "POST" }
  );
}

export function getLatestPrecheck(projectId: string): Promise<PrecheckResult> {
  return requestJson<PrecheckResult>(
    `/api/projects/${encodeURIComponent(projectId)}/prechecks/latest`
  );
}

export function resolvePrecheckIssue(issueId: string): Promise<PrecheckIssue> {
  return requestJson<PrecheckIssue>(
    `/api/precheck-issues/${encodeURIComponent(issueId)}/resolve`,
    { method: "PATCH" }
  );
}

export function lookupProjects(query: string): Promise<ProjectLookupRow[]> {
  const search = new URLSearchParams({ query });
  return requestJson<ProjectLookupRow[]>(`/api/projects/lookup?${search.toString()}`);
}

export function getSampleSummary(projectId: string): Promise<SampleSummary> {
  return requestJson<SampleSummary>(
    `/api/projects/${encodeURIComponent(projectId)}/sample-summary`
  );
}

export function getTestingSummary(projectId: string): Promise<TestingSummary> {
  return requestJson<TestingSummary>(
    `/api/projects/${encodeURIComponent(projectId)}/testing-summary`
  );
}

export function reviewIntakePackageExceptions(
  packageId: string
): Promise<ExceptionWorkflowReview> {
  return requestJson<ExceptionWorkflowReview>(
    `/api/intake-packages/${encodeURIComponent(packageId)}/exceptions/review`,
    { method: "POST" }
  );
}

export function importMsgPackage(file: File): Promise<IntakePackageImport> {
  const formData = new FormData();
  formData.append("file", file);
  return requestJson<IntakePackageImport>("/api/intake-packages/import-msg", {
    method: "POST",
    body: formData
  });
}

export function getIntakePackageDetail(packageId: string): Promise<IntakePackageDetail> {
  return requestJson<IntakePackageDetail>(
    `/api/intake-packages/${encodeURIComponent(packageId)}`
  );
}

export function getIntakeAssetPreview(assetId: string): Promise<IntakeAssetPreview> {
  return requestJson<IntakeAssetPreview>(
    `/api/intake-assets/${encodeURIComponent(assetId)}/preview`
  );
}

export function selectIntakeApplicationForm(
  packageId: string,
  assetId: string
): Promise<SelectedApplicationForm> {
  return requestJson<SelectedApplicationForm>(
    `/api/intake-packages/${encodeURIComponent(packageId)}/select-form`,
    {
      method: "POST",
      body: JSON.stringify({ asset_id: assetId })
    }
  );
}

export function createManualIntake(input: ManualIntakeInput): Promise<ManualIntake> {
  return requestJson<ManualIntake>("/api/intake-packages/manual", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function getIntakeCaseReview(packageId: string): Promise<IntakeCaseReview> {
  return requestJson<IntakeCaseReview>(
    `/api/intake-packages/${encodeURIComponent(packageId)}/case-review`
  );
}

export function getIntakePrecheckLookupOptions(): Promise<IntakePrecheckLookupOptions> {
  return requestJson<IntakePrecheckLookupOptions>("/api/lookups/intake-precheck");
}

export function confirmIntakeCase(caseId: string): Promise<ConfirmIntakeCase> {
  return requestJson<ConfirmIntakeCase>(
    `/api/intake-cases/${encodeURIComponent(caseId)}/confirm`,
    {
      method: "POST",
      body: JSON.stringify({ operator_confirmed: true })
    }
  );
}

export function updateIntakeCaseReviewFields(
  caseId: string,
  input: UpdateIntakeCaseReviewFieldsInput
): Promise<IntakeCaseReviewItem> {
  return requestJson<IntakeCaseReviewItem>(
    `/api/intake-cases/${encodeURIComponent(caseId)}/review-fields`,
    {
      method: "PATCH",
      body: JSON.stringify(input)
    }
  );
}

export function registerLtr(
  projectId: string,
  input: { ltr_number: string; requested_by?: string; notes?: string }
): Promise<LtrRecord> {
  return requestJson<LtrRecord>(`/api/projects/${encodeURIComponent(projectId)}/ltr`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function listProjectLtrs(projectId: string): Promise<LtrRecord[]> {
  return requestJson<LtrRecord[]>(`/api/projects/${encodeURIComponent(projectId)}/ltr`);
}

export function getLtrReadiness(
  projectId: string,
  proposedLtrNumber?: string | null
): Promise<LtrReadiness> {
  const search = new URLSearchParams();
  if (proposedLtrNumber) {
    search.set("proposed_ltr_number", proposedLtrNumber);
  }
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return requestJson<LtrReadiness>(
    `/api/projects/${encodeURIComponent(projectId)}/ltr/readiness${suffix}`
  );
}

export function previewLtrRegistration(
  projectId: string,
  input: LtrPreviewRequest
): Promise<LtrRegistrationPreview> {
  const search = new URLSearchParams({
    year: String(input.year),
    month: String(input.month),
    registration_type: input.registration_type,
    mode: input.mode ?? "local_only"
  });
  if (input.proposed_ltr_number) {
    search.set("proposed_ltr_number", input.proposed_ltr_number);
  }
  return requestJson<LtrRegistrationPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/ltr/preview?${search.toString()}`
  );
}

export function commitLtrLocally(
  projectId: string,
  input: LtrLocalCommitRequest
): Promise<LtrLocalCommit> {
  return requestJson<LtrLocalCommit>(
    `/api/projects/${encodeURIComponent(projectId)}/ltr/commit`,
    {
      method: "POST",
      body: JSON.stringify({ ...input, mode: input.mode ?? "local_only" })
    }
  );
}

export function previewFolder(projectId: string, input: FolderRequest): Promise<FolderPlan> {
  return requestJson<FolderPlan>(`/api/projects/${encodeURIComponent(projectId)}/folder/preview`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function generateFolder(
  projectId: string,
  input: FolderRequest
): Promise<FolderGeneration> {
  return requestJson<FolderGeneration>(
    `/api/projects/${encodeURIComponent(projectId)}/folder/generate`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function previewEvidencePlacement(projectId: string): Promise<EvidencePlacementPlan> {
  return requestJson<EvidencePlacementPlan>(
    `/api/projects/${encodeURIComponent(projectId)}/evidence/placement-preview`,
    { method: "POST" }
  );
}

export function placeEvidence(projectId: string): Promise<EvidencePlacementResult> {
  return requestJson<EvidencePlacementResult>(
    `/api/projects/${encodeURIComponent(projectId)}/evidence/place`,
    { method: "POST" }
  );
}
