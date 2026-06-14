export type Project = {
  project_id: string;
  project_no?: string | null;
  product_name: string;
  sample_description?: string | null;
  test_item?: string | null;
  requestor: string;
  status: string;
  business_unit?: string | null;
  created_on?: string | null;
  temporary_source_asset_ids?: string[];
  temporary_notes?: string | null;
};

export type ProjectRegistryRow = {
  project_id: string;
  ltr_number?: string | null;
  sample_description?: string | null;
  test_item?: string | null;
  requestor: string;
  business_unit?: string | null;
  status: string;
  progress: number;
  notes?: string | null;
  display_project_id: string;
  display_project_id_kind: "registered" | "temporary";
  has_registered_ltr: boolean;
  temporary_project_id?: string | null;
  registered_ltr_number?: string | null;
  temporary_source_asset_ids?: string[];
};

export type ProjectCreateInput = {
  project_no?: string | null;
  product_name: string;
  requestor: string;
  business_unit?: string;
};

export type CreateTemporaryProjectInput = {
  request_summary?: string | null;
  sample_description?: string | null;
  test_item?: string | null;
  requestor?: string | null;
  source_asset_ids?: string[];
  notes?: string | null;
};

export type CreateTemporaryProjectResponse = {
  project_id: string;
  display_project_id: string;
  display_project_id_kind: "temporary";
  has_registered_ltr: false;
  status: string;
  next_route: string;
};

export type TemporaryProjectDeletePreview = {
  project_id: string;
  can_delete: boolean;
  blockers: string[];
  warnings: string[];
  recommended_action: "delete" | "stop";
};

export type TemporaryProjectDeleteResponse = {
  project_id: string;
  deleted: boolean;
  deleted_temporary_context: boolean;
};

export type ProjectStopRequest = {
  reason?: string | null;
  operator?: string | null;
};

export type ProjectStopResponse = {
  project_id: string;
  previous_status: string;
  status: string;
  status_label: string;
  reason: string;
  audit_recorded: boolean;
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

export type ProjectSection2SyncFieldStatus =
  | "will_change"
  | "changed"
  | "unchanged"
  | "skipped_missing_source"
  | "blocked_invalid_source";

export type ProjectSection2SyncStatus =
  | "ready"
  | "up_to_date"
  | "partial"
  | "blocked"
  | "synced";

export type ProjectSection2SyncField = {
  field_key: "received_date" | "estimated_completion_date";
  source_field_key: "sample_received_date" | "estimated_completion_date";
  source_value?: string | null;
  current_value?: string | null;
  next_value?: string | null;
  status: ProjectSection2SyncFieldStatus;
  message: string;
};

export type ProjectSection2SyncResponse = {
  project_id: string;
  application_form_id: string;
  confirmed_matrix_id: string;
  confirmed_revision: number;
  fields: ProjectSection2SyncField[];
  status: ProjectSection2SyncStatus;
  synced_at?: string | null;
  operator?: string | null;
};

export type ProjectSection2SyncRequest = {
  expected_confirmed_matrix_id: string;
  expected_confirmed_revision: number;
  operator?: string | null;
};

export type ProjectPackagePreviewStatus = "ready" | "blocked";
export type ProjectPackagePreviewItemStatus =
  | "ready"
  | "blocked"
  | "warning"
  | "deferred";

export type ProjectPackageFolderPreview = {
  status: ProjectPackagePreviewItemStatus;
  path?: string | null;
  message: string;
};

export type ProjectPackageAuthorityContext = {
  confirmed_matrix_id?: string | null;
  confirmed_revision?: number | null;
  confirmed_fee_id?: string | null;
  confirmed_fee_revision?: number | null;
  confirmed_fee_status: string;
};

export type ProjectPackagePreviewItem = {
  key: string;
  label: string;
  status: ProjectPackagePreviewItemStatus;
  target_folder?: string | null;
  target_path?: string | null;
  message: string;
};

export type ProjectPackagePreview = {
  project_id: string;
  status: ProjectPackagePreviewStatus;
  project_folder: ProjectPackageFolderPreview;
  authority_context: ProjectPackageAuthorityContext;
  required_items: ProjectPackagePreviewItem[];
  optional_items: ProjectPackagePreviewItem[];
  blockers: string[];
  warnings: string[];
};

export type OfficialWorkspacePreviewStatus =
  | "ready"
  | "completed"
  | "blocked"
  | "adoptable"
  | "exists"
  | "inconsistent";

export type OfficialWorkspacePreview = {
  project_id: string;
  dl_number?: string | null;
  local_workspace_root?: string | null;
  local_workspace_path?: string | null;
  source_book_path?: string | null;
  template_path?: string | null;
  official_project_folder_path?: string | null;
  manifest_path?: string | null;
  template_root_mode?: string | null;
  status: OfficialWorkspacePreviewStatus;
  blockers: string[];
  warnings: string[];
  planned_paths: string[];
};

export type OfficialWorkspaceCreateResponse = {
  workspace_id: string;
  project_id: string;
  dl_number: string;
  local_workspace_path: string;
  source_book_path: string;
  official_project_folder_path: string;
  manifest_path: string;
  template_source_path: string;
  created_paths: string[];
  warnings: string[];
  created_at: string;
};

export type RequestMaterialPreviewStatus =
  | "blocked"
  | "ready"
  | "collected"
  | "review_required"
  | "partial"
  | "conflict";

export type RequestMaterialItemStatus =
  | "planned"
  | "already_present"
  | "copied"
  | "missing_source"
  | "conflict"
  | "skipped"
  | "needs_review";

export type RequestMaterialPreviewItem = {
  source_asset_id: string;
  source_asset_type: string;
  source_role?: string | null;
  source_name: string;
  source_path: string;
  dedupe_key: string;
  target_area: string;
  target_path: string;
  action: string;
  status: RequestMaterialItemStatus;
  message: string;
  review_required: boolean;
  size_bytes?: number | null;
  sha256?: string | null;
};

export type RequestMaterialPreview = {
  project_id: string;
  local_workspace_path?: string | null;
  source_book_path?: string | null;
  official_project_folder_path?: string | null;
  status: RequestMaterialPreviewStatus;
  items: RequestMaterialPreviewItem[];
  blockers: string[];
  warnings: string[];
};

export type RequestMaterialCollectResponse = RequestMaterialPreview & {
  collection_id: string;
  copied_paths: string[];
  already_present_paths: string[];
  skipped_paths: string[];
  missing_source_paths: string[];
  conflict_paths: string[];
};

export type OfficialFolderCheckStatus =
  | "blocked"
  | "missing"
  | "warning"
  | "ready"
  | "conflict";

export type OfficialFolderCheckItemStatus =
  | "ready"
  | "missing"
  | "conflict"
  | "warning"
  | "not_applicable"
  | "deferred";

export type OfficialFolderCheckItem = {
  key: string;
  label: string;
  kind: string;
  status: OfficialFolderCheckItemStatus;
  path?: string | null;
  message: string;
  repairable: boolean;
};

export type OfficialFolderCheckPreview = {
  project_id: string;
  status: OfficialFolderCheckStatus;
  local_workspace_path?: string | null;
  official_project_folder_path?: string | null;
  required_folders: OfficialFolderCheckItem[];
  required_files: OfficialFolderCheckItem[];
  blockers: string[];
  warnings: string[];
  next_action: "repair_folders" | "none";
};

export type OfficialFolderRepairResponse = {
  project_id: string;
  repair_status: "completed" | "partial" | "blocked" | "conflict";
  created_paths: string[];
  unresolved_conflicts: string[];
  errors: string[];
  preview: OfficialFolderCheckPreview;
};

export type PublicDriveUploadStatus =
  | "blocked"
  | "ready"
  | "current"
  | "conflict"
  | "warning";

export type PublicDriveUploadItemAction =
  | "add"
  | "update"
  | "skip"
  | "conflict"
  | "deferred";

export type PublicDriveUploadItemStatus =
  | "ready"
  | "current"
  | "conflict"
  | "deferred"
  | "failed";

export type PublicDriveUploadItem = {
  kind: "file" | "directory";
  relative_path: string;
  local_path?: string | null;
  public_path: string;
  action: PublicDriveUploadItemAction;
  status: PublicDriveUploadItemStatus;
  message: string;
};

export type PublicDriveUploadPreview = {
  project_id: string;
  status: PublicDriveUploadStatus;
  local_official_folder_path?: string | null;
  public_project_folder_path?: string | null;
  items: PublicDriveUploadItem[];
  blockers: string[];
  warnings: string[];
  counts: Record<string, number>;
  next_action: "preview" | "upload" | "none";
};

export type PublicDriveUploadResult = {
  project_id: string;
  upload_status: "completed" | "partial" | "blocked" | "conflict";
  copied: PublicDriveUploadItem[];
  updated: PublicDriveUploadItem[];
  skipped: PublicDriveUploadItem[];
  conflicts: PublicDriveUploadItem[];
  failed: PublicDriveUploadItem[];
  errors: string[];
  preview: PublicDriveUploadPreview;
};

export type ProjectFolderRequiredFormsStatus =
  | "blocked"
  | "ready"
  | "current"
  | "conflict";

export type ProjectFolderRequiredFormKey =
  | "test_record"
  | "fee_form"
  | "customer_feedback_form";

export type ProjectFolderRequiredFormAction =
  | "generate"
  | "update"
  | "skip"
  | "conflict"
  | "blocked";

export type ProjectFolderRequiredFormPreviewItem = {
  key: ProjectFolderRequiredFormKey;
  label: string;
  target_path: string | null;
  status: "ready" | "current" | "blocked" | "conflict";
  action: ProjectFolderRequiredFormAction;
  message: string;
};

export type ProjectFolderRequiredFormsPreview = {
  project_id: string;
  status: ProjectFolderRequiredFormsStatus;
  official_project_folder_path: string | null;
  confirmed_matrix_id: string | null;
  confirmed_revision: number | null;
  confirmed_fee_id: string | null;
  confirmed_fee_revision: number | null;
  confirmed_fee_pricing_draft_edit_id: string | null;
  customer_feedback_template_path: string | null;
  items: ProjectFolderRequiredFormPreviewItem[];
  blockers: string[];
  warnings: string[];
};

export type ProjectFolderRequiredFormsGenerateTarget = {
  key: ProjectFolderRequiredFormKey;
  target_path: string;
};

export type ProjectFolderRequiredFormsGenerateRequest = {
  expected_official_project_folder_path: string;
  expected_confirmed_matrix_id: string;
  expected_confirmed_revision: number;
  expected_confirmed_fee_id: string;
  expected_confirmed_fee_revision: number;
  expected_confirmed_fee_pricing_draft_edit_id: string;
  expected_customer_feedback_template_path: string;
  expected_targets: ProjectFolderRequiredFormsGenerateTarget[];
};

export type ProjectFolderRequiredFormsGenerateItem = {
  key: ProjectFolderRequiredFormKey;
  label: string;
  target_path: string;
  status: "generated" | "updated" | "skipped" | "failed" | "conflict";
  source_path: string | null;
  output_record_id: string | null;
  message: string;
};

export type ProjectFolderRequiredFormsGenerateResponse = {
  project_id: string;
  status: "generated" | "partial" | "blocked" | "conflict";
  official_project_folder_path: string;
  items: ProjectFolderRequiredFormsGenerateItem[];
  warnings: string[];
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

export type DraftDuplicateAction = "open_existing" | "replace_existing" | "create_separate";

export type DraftDuplicateCheck = {
  classification:
    | "exact_existing_application_draft"
    | "exact_existing_no_form_draft";
  existing_package_id: string;
  existing_case_id: string;
  existing_source_original_name: string;
  incoming_source_original_name: string;
  existing_source_size_bytes: number;
  incoming_source_size_bytes: number;
  existing_application_form_name?: string | null;
  incoming_application_form_name?: string | null;
  allowed_actions: DraftDuplicateAction[];
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
  image_data_url?: string | null;
};

export type ApplicationFormEligibility = {
  eligible: boolean;
  reason_code: string;
  message: string;
  observed_header_cell?: string | null;
  observed_footer_text?: string | null;
  expected_text: string;
};

export type IntakePackageImport = {
  package_id: string;
  source_type: string;
  package_status: string;
  source_original_name: string;
  subject?: string | null;
  sender_name?: string | null;
  sender_email?: string | null;
  received_at?: string | null;
  asset_count: number;
  candidate_count: number;
  next_action: string;
  assets: IntakeAsset[];
  duplicate_check?: DraftDuplicateCheck | null;
  resolution_action?: string | null;
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

export type ProjectCreationDraftLifecycle = {
  package_id: string;
  action: string;
  package_status?: string | null;
  deleted_package: boolean;
  deleted_assets: number;
  deleted_cases: number;
  deleted_drafts: number;
  deleted_files: boolean;
  message: string;
};

export type ProjectCreationDraft = {
  package_id: string;
  source_type: string;
  source_name: string;
  subject?: string | null;
  requester?: string | null;
  product_name?: string | null;
  updated_at?: string | null;
  current_step: string;
  selected_form_asset_id?: string | null;
  active_case_id?: string | null;
};

export type NewProjectApplicationDraft = {
  package_id: string;
  case_id: string;
  draft_id: string;
  package_status: string;
  selected_form_asset_id?: string | null;
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
  base_editing_frozen?: boolean;
  frozen_field_keys?: string[];
  frozen_reason?: string | null;
  fields: IntakeCaseReviewField[];
  sample_rows: Record<string, unknown>[];
  requested_testing_rows: Record<string, unknown>[];
  project_setup?: Record<string, unknown>;
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

export type ExternalResourceType =
  | "ltr_workbook"
  | "application_form_template"
  | "project_folder_template"
  | "project_output_root"
  | "official_public_drive_root"
  | "standard_record_excel"
  | "equipment_calibration_excel";

export type ExternalResourceValidationStatus = "not_validated" | "valid" | "invalid";

export type ExternalResource = {
  resource_id: string;
  resource_type: ExternalResourceType;
  path: string;
  active: boolean;
  validation_status: ExternalResourceValidationStatus;
  last_validated_at: string | null;
  validation_failure_reason: string | null;
};

export type ExternalResourcePickResult = {
  path: string | null;
};

export type ConfirmIntakeCase = {
  case_id: string;
  project_id: string;
  application_form_id: string;
  sample_count: number;
  file_asset_count: number;
};

export type RequestedTestingRowInput = {
  test_to_be_performed: string;
  applicable_specification: string;
};

export type UpdateIntakeCaseReviewFieldsInput = {
  fields: Record<string, string | null>;
  sample_rows?: Record<string, string>[];
  requested_testing_rows?: RequestedTestingRowInput[];
  project_setup?: Record<string, string | null>;
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

export type ProjectFolderRecord = {
  folder_id: string;
  project_id: string;
  project_folder_path: string;
  created_on?: string | null;
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

export type ApprovalPackageRequest = {
  project_folder_path: string;
  completed_application_form_path: string;
  test_record_output_path: string;
  fee_evaluation_output_path?: string | null;
  evidence_source_paths: string[];
  overwrite: boolean;
};

export type ApprovalPackageItem = {
  source_path: string;
  target_relative_path: string;
  target_path: string;
  classification: string;
  status: string;
  warnings: string[];
};

export type ApprovalPackageResponse = {
  project_id: string;
  project_folder_path: string;
  mode: string;
  items: ApprovalPackageItem[];
  warnings: string[];
  blockers: string[];
};

export type ProjectTestPlanDraftStatus = "draft" | "reviewed" | "superseded";

export type ProjectTestPlanDraftStep = {
  raw_token?: string | null;
  suffix_note?: string | null;
  sequence?: number | null;
  test_item?: string | null;
  step_label?: string | null;
  condition_summary?: string | null;
  method_summary?: string | null;
  reference_standard?: string | null;
  judgement_criteria?: string | null;
  estimated_duration_hint?: string | null;
  duration_hint?: string | null;
  estimated_duration_days?: number | null;
  duration_days?: number | null;
  estimated_duration_hours?: number | null;
  source_section?: string | null;
  source_table_index?: number | null;
  source_row_index?: number | null;
  source_trace?: string | null;
  note?: string | null;
};

export type ProjectTestPlanDraftGroup = {
  group_key?: string | null;
  group_label?: string | null;
  sample_size?: number | null;
  source_table_index?: number | null;
  steps?: ProjectTestPlanDraftStep[];
};

export type ProjectTestPlanDraftPayload = {
  groups?: ProjectTestPlanDraftGroup[];
  warnings?: string[];
  blockers?: string[];
};

export type ProjectTestPlanDraft = {
  draft_id: string;
  project_id: string;
  source_document_path: string;
  source_document_name: string;
  source_format: string;
  source_asset_id?: string | null;
  source_case_id?: string | null;
  source_draft_id?: string | null;
  status: ProjectTestPlanDraftStatus;
  version: number;
  payload: ProjectTestPlanDraftPayload;
  created_at: string;
  updated_at: string;
  reviewed_at?: string | null;
};

export type ProjectMatrixDraftRecord = {
  project_matrix_draft_id: string;
  project_id: string;
  source_import_id: string | null;
  source_snapshot_id: string;
  base_confirmed_matrix_id: string | null;
  status: string;
  created_at: string;
  updated_at: string;
  pre_test_buffer_days?: string | null;
  post_test_buffer_days?: string | null;
  sample_received_date?: string | null;
  planned_test_start_date?: string | null;
  planned_test_complete_date?: string | null;
  estimated_completion_date?: string | null;
};

export type ProjectMatrixDraftGroup = {
  draft_group_id: string;
  source_group_snapshot_id?: string | null;
  group_order: number;
  group_key: string;
  group_label: string;
  is_selected: boolean;
  sample_quantity_expression?: string | null;
  sample_note?: string | null;
};

export type ProjectMatrixDraftRow = {
  draft_row_id: string;
  source_row_snapshot_id?: string | null;
  row_order: number;
  test_item: string;
  source_section?: string | null;
  method?: string | null;
  condition?: string | null;
  requirement?: string | null;
  day_expression?: string | null;
  is_sample_row: boolean;
};

export type ProjectMatrixDraftCell = {
  draft_cell_id: string;
  draft_row_id: string;
  draft_group_id: string;
  cell_value: string;
};

export type ProjectMatrixDraft = {
  record: ProjectMatrixDraftRecord;
  groups: ProjectMatrixDraftGroup[];
  rows: ProjectMatrixDraftRow[];
  cells: ProjectMatrixDraftCell[];
};

export type ProjectMatrixDraftSummary = ProjectMatrixDraftRecord;

export type ProjectMatrixDraftSaveGroupInput = {
  draft_group_id?: string | null;
  source_group_snapshot_id?: string | null;
  group_order: number;
  group_key: string;
  group_label: string;
  is_selected: boolean;
  sample_quantity_expression?: string | null;
  sample_note?: string | null;
};

export type ProjectMatrixDraftSaveRowInput = {
  draft_row_id?: string | null;
  source_row_snapshot_id?: string | null;
  row_order: number;
  test_item: string;
  source_section?: string | null;
  method?: string | null;
  condition?: string | null;
  requirement?: string | null;
  day_expression?: string | null;
  is_sample_row?: boolean;
};

export type ProjectMatrixDraftSaveCellInput = {
  draft_row_id: string;
  draft_group_id: string;
  cell_value: string;
};

export type ProjectMatrixDraftSaveRequest = {
  groups: ProjectMatrixDraftSaveGroupInput[];
  rows: ProjectMatrixDraftSaveRowInput[];
  cells: ProjectMatrixDraftSaveCellInput[];
  pre_test_buffer_days?: string | null;
  post_test_buffer_days?: string | null;
  sample_received_date?: string | null;
  planned_test_start_date?: string | null;
  planned_test_complete_date?: string | null;
  estimated_completion_date?: string | null;
};

export type MatrixEditorSessionDraftGroup = {
  draft_group_id: string;
  source_group_snapshot_id?: string | null;
  group_order: number;
  group_key: string;
  group_label: string;
  is_selected: boolean;
  sample_quantity_expression?: string | null;
  sample_note?: string | null;
};

export type MatrixEditorSessionDraftRow = {
  draft_row_id: string;
  source_row_snapshot_id?: string | null;
  row_order: number;
  test_item: string;
  source_section?: string | null;
  method?: string | null;
  condition?: string | null;
  requirement?: string | null;
  day_expression?: string | null;
  is_sample_row: boolean;
};

export type MatrixEditorSessionDraftCell = {
  draft_row_id: string;
  draft_group_id: string;
  cell_value: string;
};

export type MatrixEditorSessionDraft = {
  groups: MatrixEditorSessionDraftGroup[];
  rows: MatrixEditorSessionDraftRow[];
  cells: MatrixEditorSessionDraftCell[];
};

export type MatrixEditorSessionSeed = {
  project_id: string;
  active_confirmed_matrix_id?: string | null;
  active_confirmed_revision?: number | null;
  active_source_import_id?: string | null;
  active_source_snapshot_id?: string | null;
  editor_draft?: MatrixEditorSessionDraft | null;
  source_preview_payload?: MatrixPreviewResponse | null;
  source_status: "available" | "unavailable" | "not_required";
  source_unavailable_message?: string | null;
  pre_test_buffer_days?: string | null;
  post_test_buffer_days?: string | null;
  sample_received_date?: string | null;
  planned_test_start_date?: string | null;
  planned_test_complete_date?: string | null;
  estimated_completion_date?: string | null;
};

export type MatrixEditorSessionConfirmRequest = {
  expected_active_confirmed_matrix_id?: string | null;
  expected_active_confirmed_revision?: number | null;
  source_document_path?: string | null;
  source_document_name?: string | null;
  source_format?: string | null;
  source_import_id?: string | null;
  source_snapshot_id?: string | null;
  confirmed_by: string;
  groups: MatrixEditorSessionDraftGroup[];
  rows: MatrixEditorSessionDraftRow[];
  cells: MatrixEditorSessionDraftCell[];
  pre_test_buffer_days?: string | null;
  post_test_buffer_days?: string | null;
  sample_received_date?: string | null;
  planned_test_start_date?: string | null;
  planned_test_complete_date?: string | null;
  estimated_completion_date?: string | null;
};

export type MatrixEditorSessionConfirmResponse = {
  publish_status: "published" | "no_change";
  message: string;
  confirmed_snapshot?: ConfirmedMatrixSnapshot | null;
};

export type MatrixEditorTestRecordDraftGroupRequest = {
  group_key: string;
  group_label: string;
  sample_quantity_expression: string;
};

export type MatrixEditorTestRecordDraftRowRequest = {
  test_item: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
  is_sample_row: boolean;
  group_values: Record<string, string>;
};

export type MatrixEditorTestRecordDraftRequest = {
  source: "matrix_editor_current_ui_state";
  groups: MatrixEditorTestRecordDraftGroupRequest[];
  rows: MatrixEditorTestRecordDraftRowRequest[];
};

export type ConfirmProjectMatrixRevisionDraftInput = {
  confirmed_by: string;
  superseded_reason?: string | null;
};

export type ConfirmedMatrixVersion = {
  confirmed_matrix_id: string;
  project_id: string;
  project_matrix_draft_id: string;
  source_import_id: string;
  source_snapshot_id: string;
  confirmed_revision: number;
  is_active_authority: boolean;
  status: string;
  confirmed_by: string;
  confirmed_at: string;
  superseded_by_confirmed_matrix_id?: string | null;
  superseded_at?: string | null;
  superseded_reason?: string | null;
  pre_test_buffer_days?: string | null;
  post_test_buffer_days?: string | null;
  sample_received_date?: string | null;
  planned_test_start_date?: string | null;
  planned_test_complete_date?: string | null;
  estimated_completion_date?: string | null;
};

export type ConfirmedMatrixGroup = {
  confirmed_group_id: string;
  draft_group_id: string;
  source_group_snapshot_id?: string | null;
  group_order: number;
  group_key: string;
  group_label: string;
  sample_quantity_expression: string;
  sample_note?: string | null;
};

export type ConfirmedMatrixRow = {
  confirmed_row_id: string;
  draft_row_id: string;
  source_row_snapshot_id?: string | null;
  row_order: number;
  test_item: string;
  source_section?: string | null;
  method?: string | null;
  condition?: string | null;
  requirement?: string | null;
  day_expression?: string | null;
};

export type ConfirmedMatrixCell = {
  confirmed_cell_id: string;
  confirmed_row_id: string;
  confirmed_group_id: string;
  draft_row_id: string;
  draft_group_id: string;
  cell_value: string;
};

export type ConfirmedMatrixSnapshot = {
  version: ConfirmedMatrixVersion;
  groups: ConfirmedMatrixGroup[];
  rows: ConfirmedMatrixRow[];
  cells: ConfirmedMatrixCell[];
};

export type MatrixValidationSummary = {
  blockers: string[];
  warnings: string[];
  group_count: number;
  step_count: number;
};

export type ProjectTestPlanMatrixActionResponse = {
  draft: ProjectTestPlanDraft;
  validation: MatrixValidationSummary;
  created_new_draft: boolean;
};

export type ProjectTestPlanMatrixValidateResponse = {
  project_id: string;
  draft_id: string;
  validation: MatrixValidationSummary;
};

export type MatrixPreviewFromPathRequest = {
  source_path: string;
  project_id?: string | null;
};

export type MatrixPreviewStep = {
  sequence: number;
  raw_token: string;
  suffix_note?: string | null;
  test_item: string;
  source_section?: string | null;
  source_note?: string | null;
  source_note_origin?: string | null;
  source_item_section_note?: string | null;
  condition_summary?: string | null;
  method_summary?: string | null;
  reference_standard?: string | null;
  judgement_criteria?: string | null;
  estimated_duration_hint?: string | null;
  duration_source?: string | null;
  duration_status: string;
  source_table_index: number;
  source_row_index: number;
  warnings: string[];
};

export type MatrixPreviewGroup = {
  group_key: string;
  group_label: string;
  source_table_index: number;
  extraction_status: string;
  sample_size?: number | null;
  sample_quantity_expression?: string | null;
  sample_note?: string | null;
  steps: MatrixPreviewStep[];
};

export type MatrixPreviewResponse = {
  project_id?: string | null;
  source_document_path: string;
  source_document_name: string;
  source_format: string;
  capability_status: string;
  generated_at: string;
  selected_table_index?: number | null;
  selected_page_number?: number | null;
  selected_page_table_index?: number | null;
  candidate_tables: Array<Record<string, unknown>>;
  preview_pdf_token?: string | null;
  rows: Array<{
    source_row_index: number;
    test_item: string;
    source_section?: string | null;
    method?: string | null;
    condition?: string | null;
    requirement?: string | null;
    detail_extraction_status?: string | null;
    detail_extraction_source_section?: string | null;
    detail_extraction_notes?: string[];
    group_tokens: Record<string, string>;
    is_sample_row: boolean;
  }>;
  groups: MatrixPreviewGroup[];
  warnings: string[];
  blockers: string[];
};

export type MatrixImportCommitRequest = {
  source_document_path: string;
  source_document_name: string;
  source_format: string;
  preview_payload: MatrixPreviewResponse;
  selected_group_keys: string[];
};

export type MatrixImportCommitResponse = {
  source_import_id: string;
  source_snapshot_id: string;
  selected_group_keys_committed: string[];
  commit_status: "created" | "reused";
  project_matrix_draft: ProjectMatrixDraft;
};

export type MatrixSourceCandidate = {
  source_asset_id: string;
  original_name: string;
  extension: string;
  asset_type: string;
  candidate_kind: string;
  reason: string;
  stored_file_available: boolean;
};

export type MatrixSourceCandidatesResponse = {
  project_id: string;
  candidates: MatrixSourceCandidate[];
  warnings: string[];
};

export type ProjectTestPlanDraftCreateRequest = {
  source_document_path: string;
  source_document_name: string;
  source_format: string;
  payload: ProjectTestPlanDraftPayload;
  status?: ProjectTestPlanDraftStatus;
  source_asset_id?: string | null;
  source_case_id?: string | null;
  source_draft_id?: string | null;
};

export type ProjectOutputKind =
  | "section2_write_back"
  | "test_record_form"
  | "fee_evaluation"
  | "customer_feedback_form"
  | "approval_package";

export type ProjectOutputStatus = "missing" | "current" | "stale" | "manual" | "failed";

export type ProjectOutputSource = "system_generated" | "system_executed" | "manual";

export type ProjectOutputStatusItem = {
  output_kind: ProjectOutputKind;
  status: ProjectOutputStatus;
  output_path: string | null;
  source: ProjectOutputSource | null;
  draft_id: string | null;
  draft_version: number | null;
  reason: string;
  updated_at: string | null;
  output_sha256?: string | null;
  output_size_bytes?: number | null;
  source_context_signature?: string | null;
};

export type ProjectOutputStatusSummary = {
  project_id: string;
  active_draft_id: string | null;
  active_draft_version: number | null;
  items: ProjectOutputStatusItem[];
};

export type FolderRequest = {
  template_path: string;
  target_root: string;
  dl_number?: string;
  plan_date?: string;
};

export type CompleteNewProjectInput = {
  ltr_mode: "auto" | "specified";
  specified_ltr_number?: string | null;
  operator_confirmed?: boolean;
  plan_date?: string | null;
  test_item?: string | null;
  sample_description?: string | null;
  location?: string | null;
  test_type_in_sheet?: string | null;
  project_leader?: string | null;
  lab_performing_tests?: string | null;
};

export type CompleteNewProject = {
  project_id: string;
  project_status: string;
  ltr_number: string;
  workbook_path?: string | null;
  workbook_sheet_name?: string | null;
  workbook_row_number?: number | null;
  workbook_backup_path?: string | null;
};

export type NewProjectCompletionOptions = {
  location_options: string[];
  test_type_in_sheet_options: string[];
  default_project_leader: string;
};

export type LtrWorkbookWriteCommitInput = {
  plan_date: string;
  operator_confirmed: boolean;
  preview_acknowledged: boolean;
  number_input?: string | null;
  test_item: string;
  sample_description: string;
  location: string;
  test_type_in_sheet: string;
  project_leader: string;
  requested_by?: string | null;
  requested_date?: string | null;
  operator_note?: string | null;
};

export type LtrWorkbookWriteCommit = {
  ltr: LtrRecord;
  action: string;
  workbook_path: string;
  backup_path: string;
  sheet_name: string;
  row_number: number;
  ltr_number: string;
};

export type RuntimeProjectionValueCountItem = {
  value: string | null;
  count: number;
};

export type RuntimeProjectionAggregationSummary = {
  lifecycle_counts: RuntimeProjectionValueCountItem[];
  evidence_counts: RuntimeProjectionValueCountItem[];
  report_sync_counts: RuntimeProjectionValueCountItem[];
  stale_counts: RuntimeProjectionValueCountItem[];
  attention_counts: RuntimeProjectionValueCountItem[];
};

export type RuntimeProjectionGroupSummary = {
  group_identity: string;
  group_label: string;
  total_tokens: number;
  unique_sequences: number;
  aggregation_summary: RuntimeProjectionAggregationSummary;
};

export type RuntimeProjectionSummaryResponse = {
  total_tokens: number;
  group_count: number;
  groups: RuntimeProjectionGroupSummary[];
};

export type RuntimeProjectionMatrixToken = {
  token_reference: string;
  raw_token: string;
  sequence_number: number;
  suffix_note: string | null;
  lifecycle_projection: string | null;
  evidence_projection: string | null;
  report_sync_projection: string | null;
  stale_projection: string | null;
  attention_projection: string | null;
};

export type RuntimeProjectionMatrixGroup = {
  group_identity: string;
  group_label: string;
  total_tokens: number;
  unique_sequences: number;
  tokens: RuntimeProjectionMatrixToken[];
};

export type RuntimeProjectionMatrixOverview = {
  total_tokens: number;
  group_count: number;
  groups: RuntimeProjectionMatrixGroup[];
};

export type RuntimeProjectionSelectedToken = {
  token_reference: string;
  raw_token: string;
  sequence_number: number;
  suffix_note: string | null;
  lifecycle_projection: string | null;
  evidence_projection: string | null;
  report_sync_projection: string | null;
  stale_projection: string | null;
  attention_projection: string | null;
  test_item_label: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
};

export type RuntimeProjectionStepWorkspace = {
  selected_token_reference: string;
  found: boolean;
  group_identity: string | null;
  group_label: string | null;
  group_token_references: string[];
  previous_token_reference: string | null;
  next_token_reference: string | null;
  selected_token: RuntimeProjectionSelectedToken | null;
};

export type RuntimeProjectionSnapshotResponse = {
  project_reference: string;
  matrix_reference: string;
  parser_warnings: string[];
  runtime_projection_summary: RuntimeProjectionSummaryResponse;
  matrix_overview: RuntimeProjectionMatrixOverview;
  step_workspace: RuntimeProjectionStepWorkspace | null;
};

export type RuntimeProjectionStateInput = {
  lifecycle?: string | null;
  evidence?: string | null;
  report_sync?: string | null;
  stale?: string | null;
  attention?: string | null;
};

export type RuntimeProjectionSnapshotRowInput = {
  group_identity: string;
  group_label: string;
  row_context: {
    test_item_label: string;
    section: string;
    method: string;
    condition: string;
    requirement: string;
  };
  raw_step_token_value?: string | null;
  projection_state?: RuntimeProjectionStateInput | null;
};

export type RuntimeProjectionSnapshotRequest = {
  project_reference: string;
  matrix_reference: string;
  rows: RuntimeProjectionSnapshotRowInput[];
  selected_token_reference?: string | null;
};

export type ConfirmedMatrixTestRecordPreviewStatus = "ready" | "empty";

export type ConfirmedMatrixTestRecordPreviewStep = {
  sequence: number;
  raw_token: string;
  test_item: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
};

export type ConfirmedMatrixTestRecordPreviewGroup = {
  group_key: string;
  group_label: string;
  sample_quantity_expression: string;
  step_count: number;
  steps: ConfirmedMatrixTestRecordPreviewStep[];
};

export type ConfirmedMatrixTestRecordPreview = {
  project_id: string;
  confirmed_matrix_id: string;
  preview_status: ConfirmedMatrixTestRecordPreviewStatus;
  groups: ConfirmedMatrixTestRecordPreviewGroup[];
};

export type FeeEvaluationDraftStatus = "ready" | "empty" | "needs_review";

export type FeeEvaluationLineStatus =
  | "calculated"
  | "review_required"
  | "no_rule_match";

export type FeeEvaluationWarning = {
  code: string;
  message: string;
  scope: string;
};

export type FeeEvaluationLineItem = {
  line_id: string;
  status: FeeEvaluationLineStatus;
  review_required: boolean;
  review_reason: string | null;
  confirmed_matrix_id: string;
  confirmed_revision: number;
  group_key: string;
  group_label: string;
  confirmed_group_id: string;
  sample_quantity_expression: string;
  confirmed_row_id: string;
  source_row_id: string | null;
  row_order: number;
  test_item: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
  step_tokens: string[];
  matched_rule_id: string | null;
  matched_rule_version_id: string | null;
  matched_rule_name: string | null;
  match_reason: string;
  calculation_strategy: string | null;
  unit_label: string;
  unit_price: string | null;
  units: string | null;
  base_fee: string | null;
  discount_percent: string | null;
  testing_fee: string | null;
  warnings: FeeEvaluationWarning[];
};

export type FeeEvaluationGroup = {
  group_key: string;
  group_label: string;
  sample_quantity_expression: string;
  line_items: FeeEvaluationLineItem[];
};

export type FeeEvaluationHeader = {
  project_id: string;
  confirmed_matrix_id: string;
  confirmed_revision: number;
  pricing_rule_version_id: string;
  pricing_source_file_name: string;
  pricing_source_hash: string;
  pricing_effective_from: string | null;
  generated_at: string;
};

export type FeeEvaluationDraft = {
  header: FeeEvaluationHeader;
  draft_status: FeeEvaluationDraftStatus;
  total_fee: string | null;
  review_required_count: number;
  groups: FeeEvaluationGroup[];
  warnings: FeeEvaluationWarning[];
};

export type FeeEvaluationExportFillMode = "fee_draft" | "matrix_basic";

export type FeeEvaluationExportRequest = {
  template_path: string;
  output_dir?: string | null;
  output_file_name?: string | null;
  overwrite?: boolean;
  allow_review_required?: boolean;
  fill_mode?: FeeEvaluationExportFillMode;
  prepared_by?: string | null;
  approved_by?: string | null;
};

export type FeeEvaluationEditedRowExportInput = {
  source_line_id: string;
  confirmed_group_id: string;
  confirmed_row_id: string;
  step_token: string;
  step_index: number;
  spend_time: string;
  unit_price: string;
  unit_type: string;
  units: string;
  base_fee: string;
  discount: string;
  testing_fee: string;
  notes: string;
};

export type FeeEvaluationEditedManualRowExportInput = {
  row_kind: "report_preparation" | "sample_preparation";
  confirmed_group_id?: string;
  group_key?: string;
  group_label?: string;
  spend_time: string;
  unit_price: string;
  unit_type: string;
  units: string;
  base_fee: string;
  discount: string;
  testing_fee: string;
  notes: string;
};

export type FeeEvaluationEditedSummaryExportInput = {
  condition_confirmation_spend_time: string;
  external_cost: string;
  external_cost_note: string;
  lab_manpower_hourly_rate: string;
};

export type FeeEvaluationEditedFileExportRequest = {
  rows: FeeEvaluationEditedRowExportInput[];
  summary: FeeEvaluationEditedSummaryExportInput;
  manual_rows?: FeeEvaluationEditedManualRowExportInput[];
};

export type FeeEvaluationPricingDraftStatus = "missing" | "current" | "stale";

export type FeeEvaluationPricingDraftResponse = {
  status: FeeEvaluationPricingDraftStatus;
  current_confirmed_matrix_id: string;
  current_confirmed_revision: number;
  current_fee_rule_version_id: string;
  saved_confirmed_matrix_id?: string | null;
  saved_confirmed_revision?: number | null;
  saved_fee_rule_version_id?: string | null;
  saved_draft_edit_id?: string | null;
  saved_updated_at?: string | null;
  payload?: FeeEvaluationEditedFileExportRequest | null;
};

export type ConfirmedFeeStatus = "missing" | "current" | "stale";

export type ConfirmedFeeSummary = {
  testing_fee_total: string;
  working_hours: string;
  lab_manpower_cost: string;
  external_cost: string;
  grand_cost: string;
};

export type ConfirmedFeeVersion = {
  confirmed_fee_id: string;
  project_id: string;
  confirmed_fee_revision: number;
  confirmed_matrix_id: string;
  confirmed_revision: number;
  fee_rule_version_id: string;
  pricing_draft_edit_id: string;
  pricing_effective_from?: string | null;
  summary: ConfirmedFeeSummary;
  confirmed_by: string;
  confirmed_at: string;
  confirmation_note?: string | null;
};

export type ConfirmedFeeLatestResponse = {
  status: ConfirmedFeeStatus;
  current_confirmed_matrix_id: string;
  current_confirmed_revision: number;
  current_fee_rule_version_id: string;
  confirmed_fee?: ConfirmedFeeVersion | null;
};

export type ConfirmFeeVersionRequest = {
  confirmed_by: string;
  expected_pricing_draft_edit_id: string;
  summary: ConfirmedFeeSummary;
  confirmation_note?: string | null;
};

export type FeeEvaluationExportLineTrace = {
  line_id: string;
  group_key: string;
  group_label: string;
  confirmed_group_id: string;
  confirmed_row_id: string;
  source_row_id: string | null;
  row_order: number;
  matched_rule_id: string | null;
  matched_rule_version_id: string | null;
  step_tokens: string[];
  cell_value?: string | null;
};

export type FeeEvaluationExportResponse = {
  project_id: string;
  output_path: string;
  output_format: string;
  status: string;
  confirmed_matrix_id: string;
  confirmed_revision: number;
  pricing_rule_version_id: string;
  pricing_effective_from: string | null;
  prepared_by: string | null;
  approved_by: string | null;
  output_record_id: string | null;
  line_traceability: FeeEvaluationExportLineTrace[];
  warnings: string[];
};

export type ConfirmedMatrixAuthorityHistoryEntry = {
  confirmed_matrix_id: string;
  confirmed_revision: number;
  is_active_authority: boolean;
  status: string;
  confirmed_by: string;
  confirmed_at: string;
  superseded_at?: string | null;
  superseded_reason?: string | null;
  source_snapshot_changed: boolean;
  group_change_count: number;
  step_change_count: number;
  token_change_count: number;
  record_regeneration_recommended: boolean;
  change_summary: string;
};

export type ConfirmedMatrixAuthorityHistory = {
  project_id: string;
  entries: ConfirmedMatrixAuthorityHistoryEntry[];
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export class ApiRequestError extends Error {
  status: number;
  detail: unknown;

  constructor(message: string, status: number, detail: unknown) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.detail = detail;
  }
}

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
    const error = await responseError(response);
    throw error;
  }

  return response.json() as Promise<T>;
}

async function responseError(response: Response): Promise<ApiRequestError> {
  const raw = await response.text();
  if (!raw) {
    return new ApiRequestError(`Request failed with ${response.status}`, response.status, null);
  }
  try {
    const parsed = JSON.parse(raw) as { detail?: unknown };
    if (typeof parsed.detail === "string") {
      return new ApiRequestError(parsed.detail, response.status, parsed.detail);
    }
    if (
      parsed.detail &&
      typeof parsed.detail === "object" &&
      "message" in parsed.detail &&
      typeof parsed.detail.message === "string"
    ) {
      return new ApiRequestError(parsed.detail.message, response.status, parsed.detail);
    }
    return new ApiRequestError(
      response.status === 409 ? "Duplicate draft detected." : raw,
      response.status,
      parsed.detail ?? parsed
    );
  } catch {
    return new ApiRequestError(raw, response.status, raw);
  }
}

async function requestBlob(path: string, init?: RequestInit): Promise<Blob> {
  const response = await requestBlobResponse(path, init);
  return response.blob;
}

export type BlobDownloadResponse = {
  blob: Blob;
  fileName: string | null;
};

async function requestBlobResponse(
  path: string,
  init?: RequestInit
): Promise<BlobDownloadResponse> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      Accept: "*/*",
      ...(init?.headers ?? {})
    }
  });

  if (!response.ok) {
    const error = await responseError(response);
    throw error;
  }

  const blob = await response.blob();
  const disposition = response.headers.get("content-disposition") ?? "";
  const utf8Name = disposition.match(/filename\*=UTF-8''([^;]+)/i)?.[1];
  const asciiName = disposition.match(/filename=\"?([^\";]+)\"?/i)?.[1];
  const fileName = decodeURIComponent(utf8Name ?? asciiName ?? "").trim() || null;
  return { blob, fileName };
}

export function listProjects(): Promise<Project[]> {
  return requestJson<Project[]>("/api/projects");
}

export function listProjectRegistryRows(): Promise<ProjectRegistryRow[]> {
  return requestJson<ProjectRegistryRow[]>("/api/projects/registry");
}

export function createProject(input: ProjectCreateInput): Promise<Project> {
  return requestJson<Project>("/api/projects", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function createTemporaryProject(
  input: CreateTemporaryProjectInput
): Promise<CreateTemporaryProjectResponse> {
  return requestJson<CreateTemporaryProjectResponse>("/api/projects/temporary", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function getProject(projectId: string): Promise<Project> {
  return requestJson<Project>(`/api/projects/${encodeURIComponent(projectId)}`);
}

export function previewTemporaryProjectDelete(
  projectId: string
): Promise<TemporaryProjectDeletePreview> {
  return requestJson<TemporaryProjectDeletePreview>(
    `/api/projects/${encodeURIComponent(projectId)}/delete-preview`,
    { cache: "no-store" }
  );
}

export function deleteTemporaryProject(
  projectId: string
): Promise<TemporaryProjectDeleteResponse> {
  return requestJson<TemporaryProjectDeleteResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/temporary`,
    { method: "DELETE" }
  );
}

export function stopProject(
  projectId: string,
  input: ProjectStopRequest
): Promise<ProjectStopResponse> {
  return requestJson<ProjectStopResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/stop`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
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

export function importMsgPackage(
  file: File,
  resolution?: {
    action: "open_existing" | "replace_existing" | "create_separate";
    packageId?: string | null;
  }
): Promise<IntakePackageImport> {
  const formData = new FormData();
  formData.append("file", file);
  if (resolution) {
    formData.append("resolution_action", resolution.action);
    if (resolution.packageId) {
      formData.append("resolution_package_id", resolution.packageId);
    }
  }
  return requestJson<IntakePackageImport>("/api/intake-packages/import-msg", {
    method: "POST",
    body: formData
  });
}

export function importDirectWordApplicationForm(file: File): Promise<IntakePackageImport> {
  const formData = new FormData();
  formData.append("file", file);
  return requestJson<IntakePackageImport>("/api/intake-packages/import-docx", {
    method: "POST",
    body: formData
  });
}

export function uploadEmailPackageApplicationForm(
  packageId: string,
  file: File
): Promise<SelectedApplicationForm> {
  const formData = new FormData();
  formData.append("file", file);
  return requestJson<SelectedApplicationForm>(
    `/api/intake-packages/${encodeURIComponent(packageId)}/application-form`,
    {
      method: "POST",
      body: formData
    }
  );
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

export function validateIntakeAssetApplicationForm(
  assetId: string
): Promise<ApplicationFormEligibility> {
  return requestJson<ApplicationFormEligibility>(
    `/api/intake-assets/${encodeURIComponent(assetId)}/application-form/validate`,
    { method: "POST" }
  );
}

export function intakeAssetDownloadUrl(assetId: string): string {
  return `${API_BASE}/api/intake-assets/${encodeURIComponent(assetId)}/download`;
}

export function downloadIntakeAsset(assetId: string): Promise<Blob> {
  return requestBlob(`/api/intake-assets/${encodeURIComponent(assetId)}/download`);
}

export function selectIntakeApplicationForm(
  packageId: string,
  assetId: string,
  replaceExisting = false,
  resolution?: { action: DraftDuplicateAction; caseId?: string | null }
): Promise<SelectedApplicationForm> {
  return requestJson<SelectedApplicationForm>(
    `/api/intake-packages/${encodeURIComponent(packageId)}/select-form`,
    {
      method: "POST",
      body: JSON.stringify({
        asset_id: assetId,
        replace_existing: replaceExisting,
        resolution_action: resolution?.action ?? null,
        resolution_case_id: resolution?.caseId ?? null
      })
    }
  );
}

export function ensureNewProjectApplicationDraft(
  packageId: string,
  resolution?: { action: DraftDuplicateAction; caseId?: string | null }
): Promise<NewProjectApplicationDraft> {
  return requestJson<NewProjectApplicationDraft>(
    `/api/intake-packages/${encodeURIComponent(packageId)}/application-draft`,
    {
      method: "POST",
      body: resolution
        ? JSON.stringify({
            resolution_action: resolution.action,
            resolution_case_id: resolution.caseId ?? null
          })
        : undefined
    }
  );
}

export function createManualIntake(input: ManualIntakeInput): Promise<ManualIntake> {
  return requestJson<ManualIntake>("/api/intake-packages/manual", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function saveProjectCreationDraft(
  packageId: string
): Promise<ProjectCreationDraftLifecycle> {
  return requestJson<ProjectCreationDraftLifecycle>(
    `/api/intake-packages/${encodeURIComponent(packageId)}/draft/save`,
    { method: "POST" }
  );
}

export function discardUnsavedProjectCreationDraft(
  packageId: string
): Promise<ProjectCreationDraftLifecycle> {
  return requestJson<ProjectCreationDraftLifecycle>(
    `/api/intake-packages/${encodeURIComponent(packageId)}/draft/discard`,
    { method: "POST" }
  );
}

export function listProjectCreationDrafts(): Promise<ProjectCreationDraft[]> {
  return requestJson<ProjectCreationDraft[]>("/api/project-creation-drafts");
}

export function discardSavedProjectCreationDraft(
  packageId: string
): Promise<ProjectCreationDraftLifecycle> {
  return requestJson<ProjectCreationDraftLifecycle>(
    `/api/project-creation-drafts/${encodeURIComponent(packageId)}/discard`,
    { method: "POST" }
  );
}

export function getIntakeCaseReview(packageId: string): Promise<IntakeCaseReview> {
  return requestJson<IntakeCaseReview>(
    `/api/intake-packages/${encodeURIComponent(packageId)}/case-review`
  );
}

export function getIntakePrecheckLookupOptions(): Promise<IntakePrecheckLookupOptions> {
  return requestJson<IntakePrecheckLookupOptions>("/api/lookups/intake-precheck");
}

export function listExternalResources(): Promise<ExternalResource[]> {
  return requestJson<ExternalResource[]>("/api/external-resources");
}

export function saveExternalResource(
  resourceType: ExternalResourceType,
  input: { path: string; active: boolean }
): Promise<ExternalResource> {
  return requestJson<ExternalResource>(
    `/api/external-resources/${encodeURIComponent(resourceType)}`,
    {
      method: "PUT",
      body: JSON.stringify(input)
    }
  );
}

export function validateExternalResource(
  resourceType: ExternalResourceType
): Promise<ExternalResource> {
  return requestJson<ExternalResource>(
    `/api/external-resources/${encodeURIComponent(resourceType)}/validate`,
    { method: "POST" }
  );
}

export function pickExternalResourcePath(
  resourceType: ExternalResourceType
): Promise<ExternalResourcePickResult> {
  return requestJson<ExternalResourcePickResult>(
    `/api/external-resources/${encodeURIComponent(resourceType)}/pick`,
    { method: "POST" }
  );
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

export function completeNewProject(
  caseId: string,
  input: CompleteNewProjectInput
): Promise<CompleteNewProject> {
  return requestJson<CompleteNewProject>(
    `/api/intake-cases/${encodeURIComponent(caseId)}/complete-new-project`,
    {
      method: "POST",
      body: JSON.stringify({ operator_confirmed: true, ...input })
    }
  );
}

export function getNewProjectCompletionOptions(): Promise<NewProjectCompletionOptions> {
  return requestJson<NewProjectCompletionOptions>("/api/new-project/completion-options");
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

export function commitLtrWorkbookWrite(
  projectId: string,
  input: LtrWorkbookWriteCommitInput
): Promise<LtrWorkbookWriteCommit> {
  return requestJson<LtrWorkbookWriteCommit>(
    `/api/projects/${encodeURIComponent(projectId)}/ltr-workbook/write-commit`,
    {
      method: "POST",
      body: JSON.stringify(input)
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

export function getLatestProjectFolder(projectId: string): Promise<ProjectFolderRecord> {
  return requestJson<ProjectFolderRecord>(
    `/api/projects/${encodeURIComponent(projectId)}/folder/latest`
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

export function previewApprovalPackage(
  projectId: string,
  input: ApprovalPackageRequest
): Promise<ApprovalPackageResponse> {
  return requestJson<ApprovalPackageResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/approval-package/preview`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function executeApprovalPackage(
  projectId: string,
  input: ApprovalPackageRequest
): Promise<ApprovalPackageResponse> {
  return requestJson<ApprovalPackageResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/approval-package/execute`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function listProjectTestPlanDrafts(projectId: string): Promise<ProjectTestPlanDraft[]> {
  return requestJson<ProjectTestPlanDraft[]>(
    `/api/projects/${encodeURIComponent(projectId)}/test-plan/drafts`
  );
}

export function listProjectMatrixDrafts(
  projectId: string
): Promise<ProjectMatrixDraftSummary[]> {
  return requestJson<ProjectMatrixDraftSummary[]>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-drafts`
  );
}

export function getProjectMatrixDraft(
  projectId: string,
  projectMatrixDraftId: string
): Promise<ProjectMatrixDraft> {
  return requestJson<ProjectMatrixDraft>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-drafts/${encodeURIComponent(projectMatrixDraftId)}`
  );
}

export function saveProjectMatrixDraft(
  projectId: string,
  projectMatrixDraftId: string,
  input: ProjectMatrixDraftSaveRequest
): Promise<ProjectMatrixDraft> {
  return requestJson<ProjectMatrixDraft>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-drafts/${encodeURIComponent(projectMatrixDraftId)}`,
    {
      method: "PUT",
      body: JSON.stringify(input)
    }
  );
}

export function createMatrixRevisionDraft(projectId: string): Promise<ProjectMatrixDraft> {
  return requestJson<ProjectMatrixDraft>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-revisions`,
    {
      method: "POST"
    }
  );
}

export function confirmProjectMatrixRevisionDraft(
  projectId: string,
  projectMatrixDraftId: string,
  input: ConfirmProjectMatrixRevisionDraftInput
): Promise<ConfirmedMatrixSnapshot> {
  return requestJson<ConfirmedMatrixSnapshot>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-drafts/${encodeURIComponent(projectMatrixDraftId)}/confirm-revision`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function confirmProjectMatrixDraft(
  projectId: string,
  projectMatrixDraftId: string,
  input: ConfirmProjectMatrixRevisionDraftInput
): Promise<ConfirmedMatrixSnapshot> {
  return requestJson<ConfirmedMatrixSnapshot>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-drafts/${encodeURIComponent(projectMatrixDraftId)}/confirm`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function fetchActiveConfirmedMatrixSnapshot(
  projectId: string
): Promise<ConfirmedMatrixSnapshot> {
  return requestJson<ConfirmedMatrixSnapshot>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/active-snapshot`
  );
}

export function fetchConfirmedMatrixRuntimeProjectionSnapshot(
  projectId: string,
  selectedTokenReference?: string | null
): Promise<RuntimeProjectionSnapshotResponse> {
  const search = new URLSearchParams();
  if (selectedTokenReference) {
    search.set("selected_token_reference", selectedTokenReference);
  }
  const suffix = search.toString() ? `?${search.toString()}` : "";
  return requestJson<RuntimeProjectionSnapshotResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/runtime-projection/confirmed-matrix-snapshot${suffix}`
  );
}

export function fetchMatrixEditorSession(
  projectId: string
): Promise<MatrixEditorSessionSeed> {
  return requestJson<MatrixEditorSessionSeed>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-editor/session`
  );
}

export function confirmMatrixEditorSession(
  projectId: string,
  input: MatrixEditorSessionConfirmRequest
): Promise<MatrixEditorSessionConfirmResponse> {
  return requestJson<MatrixEditorSessionConfirmResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-editor/session/confirm`,
    {
      method: "POST",
      body: JSON.stringify(input),
    }
  );
}

export function commitMatrixImport(
  projectId: string,
  input: MatrixImportCommitRequest
): Promise<MatrixImportCommitResponse> {
  return requestJson<MatrixImportCommitResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-import/commit`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function previewProjectTestPlanMatrixFromPath(
  input: MatrixPreviewFromPathRequest
): Promise<MatrixPreviewResponse> {
  return requestJson<MatrixPreviewResponse>("/api/test-plan/matrix-preview-from-path", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function previewProjectTestPlanMatrixFromUpload(
  file: File,
  projectId?: string | null,
  locator?: {
    pageNumber?: number | null;
    pageTableIndex?: number | null;
    tableTextQuery?: string | null;
  }
): Promise<MatrixPreviewResponse> {
  const formData = new FormData();
  formData.append("file", file);
  if (projectId) {
    formData.append("project_id", projectId);
  }
  if (typeof locator?.pageNumber === "number") {
    formData.append("page_number", String(locator.pageNumber));
  }
  if (typeof locator?.pageTableIndex === "number") {
    formData.append("page_table_index", String(locator.pageTableIndex));
  }
  if ((locator?.tableTextQuery ?? "").trim().length > 0) {
    formData.append("table_text_query", (locator?.tableTextQuery ?? "").trim());
  }
  return requestJson<MatrixPreviewResponse>("/api/test-plan/matrix-preview-from-upload", {
    method: "POST",
    body: formData
  });
}

export function matrixPreviewPdfUrl(token: string): string {
  return `${API_BASE}/api/test-plan/matrix-preview-pdf/${encodeURIComponent(token)}`;
}

export function listProjectTestPlanSourceCandidates(
  projectId: string
): Promise<MatrixSourceCandidatesResponse> {
  return requestJson<MatrixSourceCandidatesResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/test-plan/source-candidates`
  );
}

export function previewProjectTestPlanMatrixFromSourceCandidate(
  projectId: string,
  sourceAssetId: string
): Promise<MatrixPreviewResponse> {
  return requestJson<MatrixPreviewResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/test-plan/source-candidates/${encodeURIComponent(sourceAssetId)}/matrix-preview`,
    {
      method: "POST"
    }
  );
}

export function createProjectTestPlanDraft(
  projectId: string,
  input: ProjectTestPlanDraftCreateRequest
): Promise<ProjectTestPlanDraft> {
  return requestJson<ProjectTestPlanDraft>(
    `/api/projects/${encodeURIComponent(projectId)}/test-plan/drafts`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function getProjectTestPlanDraft(
  projectId: string,
  draftId: string
): Promise<ProjectTestPlanDraft> {
  return requestJson<ProjectTestPlanDraft>(
    `/api/projects/${encodeURIComponent(projectId)}/test-plan/drafts/${encodeURIComponent(draftId)}`
  );
}

export function updateProjectTestPlanMatrixDraft(
  projectId: string,
  draftId: string,
  groups: ProjectTestPlanDraftGroup[]
): Promise<ProjectTestPlanMatrixActionResponse> {
  return requestJson<ProjectTestPlanMatrixActionResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/test-plan/drafts/${encodeURIComponent(draftId)}/matrix`,
    {
      method: "PUT",
      body: JSON.stringify({ groups })
    }
  );
}

export function validateProjectTestPlanMatrixDraft(
  projectId: string,
  draftId: string,
  groups?: ProjectTestPlanDraftGroup[]
): Promise<ProjectTestPlanMatrixValidateResponse> {
  return requestJson<ProjectTestPlanMatrixValidateResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/test-plan/drafts/${encodeURIComponent(draftId)}/matrix/validate`,
    {
      method: "POST",
      body: JSON.stringify(groups ? { groups } : {})
    }
  );
}

export function confirmProjectTestPlanMatrixDraft(
  projectId: string,
  draftId: string,
  groups?: ProjectTestPlanDraftGroup[]
): Promise<ProjectTestPlanMatrixActionResponse> {
  return requestJson<ProjectTestPlanMatrixActionResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/test-plan/drafts/${encodeURIComponent(draftId)}/matrix/confirm`,
    {
      method: "POST",
      body: JSON.stringify(groups ? { groups } : {})
    }
  );
}

export function getProjectOutputStatusSummary(
  projectId: string
): Promise<ProjectOutputStatusSummary> {
  return requestJson<ProjectOutputStatusSummary>(
    `/api/projects/${encodeURIComponent(projectId)}/output-records/status`
  );
}

export function fetchProjectSection2SyncPreview(
  projectId: string
): Promise<ProjectSection2SyncResponse> {
  return requestJson<ProjectSection2SyncResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/section2-sync/preview`,
    { cache: "no-store" }
  );
}

export function fetchProjectPackagePreview(projectId: string): Promise<ProjectPackagePreview> {
  return requestJson<ProjectPackagePreview>(
    `/api/projects/${encodeURIComponent(projectId)}/project-package/preview`,
    { cache: "no-store" }
  );
}

export function fetchOfficialWorkspacePreview(
  projectId: string
): Promise<OfficialWorkspacePreview> {
  return requestJson<OfficialWorkspacePreview>(
    `/api/projects/${encodeURIComponent(projectId)}/official-workspace/preview`,
    { cache: "no-store" }
  );
}

export function createOfficialWorkspace(
  projectId: string
): Promise<OfficialWorkspaceCreateResponse> {
  return requestJson<OfficialWorkspaceCreateResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/official-workspace/create`,
    { method: "POST" }
  );
}

export function fetchRequestMaterialPreview(
  projectId: string
): Promise<RequestMaterialPreview> {
  return requestJson<RequestMaterialPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/request-material/preview`,
    { cache: "no-store" }
  );
}

export function collectRequestMaterial(
  projectId: string
): Promise<RequestMaterialCollectResponse> {
  return requestJson<RequestMaterialCollectResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/request-material/collect`,
    { method: "POST" }
  );
}

export function fetchOfficialFolderCheck(
  projectId: string
): Promise<OfficialFolderCheckPreview> {
  return requestJson<OfficialFolderCheckPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/official-folder/check`,
    { cache: "no-store" }
  );
}

export function repairOfficialFolderStructure(
  projectId: string
): Promise<OfficialFolderRepairResponse> {
  return requestJson<OfficialFolderRepairResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/official-folder/repair-folders`,
    { method: "POST" }
  );
}

export function fetchPublicDriveUploadPreview(
  projectId: string
): Promise<PublicDriveUploadPreview> {
  return requestJson<PublicDriveUploadPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/public-drive/preview`,
    { cache: "no-store" }
  );
}

export function uploadPublicDriveProjectFolder(
  projectId: string
): Promise<PublicDriveUploadResult> {
  return requestJson<PublicDriveUploadResult>(
    `/api/projects/${encodeURIComponent(projectId)}/public-drive/upload`,
    { method: "POST" }
  );
}

export function fetchProjectFolderRequiredFormsPreview(
  projectId: string
): Promise<ProjectFolderRequiredFormsPreview> {
  return requestJson<ProjectFolderRequiredFormsPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/project-folder/required-forms/preview`,
    { cache: "no-store" }
  );
}

export function generateProjectFolderRequiredForms(
  projectId: string,
  input: ProjectFolderRequiredFormsGenerateRequest
): Promise<ProjectFolderRequiredFormsGenerateResponse> {
  return requestJson<ProjectFolderRequiredFormsGenerateResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/project-folder/required-forms/generate`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function syncProjectSection2FromConfirmedMatrix(
  projectId: string,
  input: ProjectSection2SyncRequest
): Promise<ProjectSection2SyncResponse> {
  return requestJson<ProjectSection2SyncResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/section2-sync`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function getRuntimeProjectionReadOnlySnapshot(
  input: RuntimeProjectionSnapshotRequest
): Promise<RuntimeProjectionSnapshotResponse> {
  return requestJson<RuntimeProjectionSnapshotResponse>(
    "/api/runtime-projection/read-only-snapshot",
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function fetchConfirmedMatrixTestRecordPreview(
  projectId: string
): Promise<ConfirmedMatrixTestRecordPreview> {
  return requestJson<ConfirmedMatrixTestRecordPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/test-record-preview`,
    { cache: "no-store" }
  );
}

export function fetchConfirmedMatrixFeeDraft(
  projectId: string
): Promise<FeeEvaluationDraft> {
  return requestJson<FeeEvaluationDraft>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/fee-draft`,
    { cache: "no-store" }
  );
}

export function exportConfirmedMatrixFeeEvaluation(
  projectId: string,
  input: FeeEvaluationExportRequest
): Promise<FeeEvaluationExportResponse> {
  return requestJson<FeeEvaluationExportResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/fee-evaluation/export`,
    {
      method: "POST",
      body: JSON.stringify(input),
    }
  );
}

export function generateConfirmedMatrixFeeFileDownload(
  projectId: string,
  input?: FeeEvaluationEditedFileExportRequest
): Promise<BlobDownloadResponse> {
  return requestBlobResponse(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/fee-evaluation/file/generate`,
    input
      ? {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(input),
        }
      : { method: "POST" }
  );
}

export function getFeeEvaluationPricingDraft(
  projectId: string
): Promise<FeeEvaluationPricingDraftResponse> {
  return requestJson<FeeEvaluationPricingDraftResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/fee-evaluation/pricing-draft`
  );
}

export function saveFeeEvaluationPricingDraft(
  projectId: string,
  input: FeeEvaluationEditedFileExportRequest
): Promise<FeeEvaluationPricingDraftResponse> {
  return requestJson<FeeEvaluationPricingDraftResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/fee-evaluation/pricing-draft`,
    {
      method: "PUT",
      body: JSON.stringify(input),
    }
  );
}

export function getConfirmedFeeLatest(
  projectId: string
): Promise<ConfirmedFeeLatestResponse> {
  return requestJson<ConfirmedFeeLatestResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-fee/latest`
  );
}

export function confirmFeeVersion(
  projectId: string,
  input: ConfirmFeeVersionRequest
): Promise<ConfirmedFeeLatestResponse> {
  return requestJson<ConfirmedFeeLatestResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-fee/versions`,
    {
      method: "POST",
      body: JSON.stringify(input),
    }
  );
}

export function generateConfirmedMatrixTestRecordDraft(
  projectId: string
): Promise<Blob> {
  return requestBlob(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/test-record-draft/generate`,
    { method: "POST" }
  );
}

export function generateConfirmedMatrixTestRecordDraftDownload(
  projectId: string
): Promise<BlobDownloadResponse> {
  return requestBlobResponse(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/test-record-draft/generate`,
    { method: "POST" }
  );
}

export function generateMatrixEditorTestRecordDraftDownload(
  projectId: string,
  input: MatrixEditorTestRecordDraftRequest
): Promise<BlobDownloadResponse> {
  return requestBlobResponse(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-editor/test-record-draft/generate`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    }
  );
}

export function fetchConfirmedMatrixAuthorityHistory(
  projectId: string
): Promise<ConfirmedMatrixAuthorityHistory> {
  return requestJson<ConfirmedMatrixAuthorityHistory>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/authority-history`
  );
}
