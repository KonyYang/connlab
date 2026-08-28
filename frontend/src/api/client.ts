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

export type ProjectLifecycleState = "active" | "stopped" | "closed";

export type ProjectClosureType = "completed" | "administrative";

export type ProjectCloseReasonCategory =
  | "completed"
  | "failed"
  | "cancelled"
  | "cannot_test"
  | "duplicate"
  | "other";

export type ProjectLifecycleResponse = {
  project_id: string;
  lifecycle_state: ProjectLifecycleState;
  closure_type: ProjectClosureType | null;
  close_reason_category?: ProjectCloseReasonCategory | null;
  close_reason_label?: string | null;
  status_label: string;
  readonly: boolean;
  allowed_actions: string[];
  status: string;
  stopped_at?: string | null;
  stopped_reason?: string | null;
  closed_at?: string | null;
  closed_reason?: string | null;
  completion_summary?: Record<string, unknown> | null;
  warnings: string[];
};

export type ProjectLifecycleActionRequest = {
  reason?: string | null;
  operator?: string | null;
};

export type ProjectLifecycleCloseCompletedRequest = {
  close_note: string;
  operator?: string | null;
  manual_completion_confirmed: boolean;
  output_summary_acknowledged: boolean;
};

export type ProjectLifecycleCloseAdministrativeRequest = {
  reason: string;
  operator?: string | null;
};

export type ProjectLifecycleCloseRequest = {
  reason_category: ProjectCloseReasonCategory;
  note: string;
  operator?: string | null;
};

export type ProjectLifecycleReadonlyErrorDetail = {
  code: "project_lifecycle_readonly";
  project_id: string;
  lifecycle_state: ProjectLifecycleState;
  closure_type: ProjectClosureType | null;
  close_reason_category?: ProjectCloseReasonCategory | null;
  close_reason_label?: string | null;
  can_activate?: boolean;
  message: string;
  allowed_actions: string[];
};

export type ProjectBasicInformationStatus =
  | "unconfirmed"
  | "confirmed"
  | "needs_review";

export type ProjectBasicInformationRecord = {
  record_id: string;
  project_id: string;
  status: "draft" | "confirmed";
  version: number;
  values: Record<string, string>;
  source_signature: string;
  created_at: string;
  updated_at: string;
  confirmed_at?: string | null;
  confirmed_by?: string | null;
};

export type ProjectBasicInformationDraft = {
  values: Record<string, string>;
};

export type ProjectBasicInformationFieldSuggestion = {
  field_key: string;
  source: string;
  source_value: string;
  needs_review: boolean;
};

export type ProjectBasicInformationResponse = {
  project_id: string;
  status: ProjectBasicInformationStatus;
  draft: ProjectBasicInformationDraft;
  latest_confirmed: ProjectBasicInformationRecord | null;
  field_suggestions: Record<string, ProjectBasicInformationFieldSuggestion>;
  changed_source_fields: string[];
  missing_required_fields: string[];
  missing_required_labels: string[];
  blockers: string[];
  warnings: string[];
};

export type ProjectBasicInformationDraftRequest = {
  values: Record<string, string>;
};

export type ProjectBasicInformationConfirmRequest = {
  values: Record<string, string>;
  confirmed_by: string;
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

export type ApplicationFormWriteBackField = {
  field_key: string;
  label: string;
  old_value: string;
  new_value: string;
  location: string;
};

export type ApplicationFormWriteBackTiming = {
  label: string;
  elapsed_ms: number;
};

export type ApplicationFormWriteBackResponse = {
  project_id: string;
  target_path: string;
  status: string;
  changed_fields: ApplicationFormWriteBackField[];
  unchanged_fields: ApplicationFormWriteBackField[];
  warnings: string[];
  output_record_id?: string | null;
  timings?: ApplicationFormWriteBackTiming[];
  office_timings?: ApplicationFormWriteBackTiming[];
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
  matrix_source: "confirmed" | "draft" | "missing";
  project_matrix_draft_id?: string | null;
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
  conflict_paths?: string[];
  conflict_options?: OfficialWorkspaceConflictOption[];
};

export type OfficialWorkspaceConflictStrategy =
  | "backup_and_recreate"
  | "overwrite_rebuild";

export type OfficialWorkspaceConflictOption = {
  key: OfficialWorkspaceConflictStrategy;
  label: string;
  description: string;
};

export type OfficialWorkspaceCreateRequest = {
  conflict_strategy?: OfficialWorkspaceConflictStrategy | null;
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

export type PublicFolderWorkflowOperationType = "sync" | "submit" | "pull";

export type PublicFolderWorkflowStatus =
  | "ready"
  | "blocked"
  | "conflict"
  | "completed"
  | "failed";

export type PublicFolderWorkflowRootClass = "missing" | "open" | "closed" | "invalid";

export type PublicFolderWorkflowItem = {
  kind: string;
  relative_path: string;
  local_path: string | null;
  public_path: string | null;
  action: string;
  status: string;
  message: string | null;
};

export type PublicFolderWorkflowPreview = {
  project_id: string;
  operation_type: PublicFolderWorkflowOperationType;
  status: PublicFolderWorkflowStatus;
  local_official_folder_path: string | null;
  public_root: string | null;
  public_root_class: PublicFolderWorkflowRootClass | string | null;
  public_folder_year: number | null;
  year_source: string | null;
  year_evidence: string | null;
  public_open_path: string | null;
  public_closed_path: string | null;
  target_path: string | null;
  items: PublicFolderWorkflowItem[];
  blockers: string[];
  warnings: string[];
  conflicts: string[];
  required_confirmations: string[];
  counts: Record<string, number>;
  preview_hash: string | null;
  next_action: string | null;
  auto_sync_enabled: boolean;
  sync_locked: boolean;
};

export type PublicFolderWorkflowContext = {
  project_id: string;
  auto_sync_enabled: boolean;
  sync_locked: boolean;
  submitted_at: string | null;
  public_root: string | null;
  public_root_class: PublicFolderWorkflowRootClass | string | null;
  public_folder_year: number | null;
  year_source: string | null;
  year_evidence: string | null;
  local_official_folder_path: string | null;
  public_open_path: string | null;
  public_closed_path: string | null;
  blockers: string[];
  warnings: string[];
};

export type PublicFolderWorkflowState = {
  project_id: string;
  auto_sync_enabled: boolean;
  sync_locked: boolean;
  submitted_at: string | null;
  submit_operation_id: string | null;
  last_sync_operation_id: string | null;
  last_pull_operation_id: string | null;
  created_at: string | null;
  updated_at: string | null;
};

export type PublicFolderWorkflowExecuteInput = {
  preview_hash: string;
  confirmed: boolean;
  confirm_directory_creation?: boolean;
  operator?: string | null;
};

export type PublicFolderWorkflowResult = {
  project_id: string;
  operation_id: string;
  operation_type: PublicFolderWorkflowOperationType;
  status: PublicFolderWorkflowStatus;
  counts: Record<string, number>;
  errors: string[];
  preview: PublicFolderWorkflowPreview;
};

export type ProjectFolderOpenResponse = {
  project_id: string;
  status: "opened" | "blocked" | "unsupported";
  message: string;
  local_official_folder_path: string | null;
};

export type ProjectFolderRequiredFormsStatus =
  | "blocked"
  | "ready"
  | "current"
  | "conflict";

export type ProjectFolderRequiredFormKey =
  | "test_record"
  | "test_status"
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
  confirmed_basic_information_version: number | null;
  confirmed_basic_information_source_signature_hash: string | null;
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
  expected_confirmed_basic_information_version: number;
  expected_confirmed_basic_information_source_signature_hash: string;
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

export type ProjectFolderRequiredFormsTiming = {
  label: string;
  elapsed_ms: number;
};

export type ProjectFolderRequiredFormsGenerateResponse = {
  project_id: string;
  status: "generated" | "partial" | "blocked" | "conflict";
  official_project_folder_path: string;
  items: ProjectFolderRequiredFormsGenerateItem[];
  warnings: string[];
  timings?: ProjectFolderRequiredFormsTiming[];
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
  worksheet_name: string | null;
};

export type MatrixMethodVersionSyncRow = {
  draft_row_id: string;
  row_order: number;
  test_item: string;
  current_method: string | null;
  method_core: string | null;
  matched_standard_code: string | null;
  catalog_revision: string | null;
  catalog_year: number | null;
  source_row_number: number | null;
  proposed_method: string | null;
  status: string;
  reason: string | null;
  selectable: boolean;
};

export type MatrixMethodVersionSyncPreview = {
  project_id: string;
  project_matrix_draft_id: string;
  base_confirmed_matrix_id: string | null;
  resource_id: string;
  resource_path: string;
  worksheet_name: string;
  catalog_fingerprint: string;
  target_fingerprint: string;
  preview_fingerprint: string;
  generated_at: string;
  rows: MatrixMethodVersionSyncRow[];
};

export type MatrixMethodVersionSyncApplyResponse = {
  project_matrix_draft_id: string;
  saved_payload_signature: string;
  applied_row_ids: string[];
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

export type MatrixDurationAuthority = {
  duration_authority_id: string;
  group_id: string;
  row_id: string;
  step_sequence: number;
  step_suffix_note: string;
  duration_value: string;
  duration_unit: string;
  normalized_hours: string;
  source_kind: string;
  source_field: string;
  source_import_id?: string | null;
  source_fingerprint: string;
  lineage_fingerprint: string;
  authority_revision: string;
  status: string;
  diagnostic_code?: string | null;
  diagnostic_message?: string | null;
};

export type ProjectMatrixDraft = {
  record: ProjectMatrixDraftRecord;
  groups: ProjectMatrixDraftGroup[];
  rows: ProjectMatrixDraftRow[];
  cells: ProjectMatrixDraftCell[];
  duration_authorities?: MatrixDurationAuthority[];
};

export type LlcrCrRecordWorkbookDiagnostic = {
  code: string;
  severity: "blocked" | "review_required";
  message: string;
  confirmed_group_id: string | null;
  confirmed_row_id: string | null;
  step_sequence: number | null;
  family_id: string | null;
  normalized_prefix: string | null;
  first_family_id: string | null;
  first_family_label: string | null;
  second_family_id: string | null;
  second_family_label: string | null;
};

export type LlcrCrRecordWorkbookRow = {
  sample_index: number;
  contact_id: string;
  contact_label: string;
};

export type LlcrCrRecordType = "llcr" | "cr";

export type LlcrCrRecordWorkbookStage = {
  label: string;
  source_step: string;
  confirmed_row_id: string;
  test_item: string;
  condition: string;
  requirement: string;
  test_current_ampere: string | null;
};

export type LlcrCrRecordWorkbookSection = {
  record_type: LlcrCrRecordType;
  confirmed_group_id: string;
  confirmed_row_id: string;
  step_sequence: number;
  step_suffix_note: string;
  group_label: string;
  source_step: string;
  sample_count: number;
  readings_per_sample: number;
  rows: LlcrCrRecordWorkbookRow[];
  category_id: string | null;
  category_label: string | null;
  record_prefix: string | null;
  point_expression: string | null;
  stages: LlcrCrRecordWorkbookStage[];
};

export type LlcrCrRecordWorkbookPreviewResponse = {
  project_id: string;
  status: "ready" | "blocked" | "review_required" | "empty";
  confirmed_matrix_id: string;
  confirmed_revision: number;
  preview_fingerprint: string | null;
  row_count: number;
  sections: LlcrCrRecordWorkbookSection[];
  diagnostics: LlcrCrRecordWorkbookDiagnostic[];
  record_type: LlcrCrRecordType;
  point_profile_revision_id: string | null;
  point_profile_revision_sequence: number | null;
  delta_r_enabled: boolean;
};

export type LlcrCrRecordWorkbookGenerateRequest = {
  record_type: LlcrCrRecordType;
  preview_fingerprint: string;
};

export type LlcrCrRecordWorkbookGenerateResponse = {
  project_id: string;
  confirmed_matrix_id: string;
  confirmed_revision: number;
  artifact_id: string;
  file_name: string;
  download_url: string;
  record_type: LlcrCrRecordType;
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
  duration_authorities?: ProjectMatrixDraftDurationAuthorityInput[] | null;
  pre_test_buffer_days?: string | null;
  post_test_buffer_days?: string | null;
  sample_received_date?: string | null;
  planned_test_start_date?: string | null;
  planned_test_complete_date?: string | null;
  estimated_completion_date?: string | null;
};

export type ProjectMatrixDraftDurationAuthorityInput = {
  draft_duration_authority_id?: string | null;
  draft_group_id: string;
  draft_row_id: string;
  step_sequence: number;
  step_suffix_note?: string | null;
  duration_value: string;
  duration_unit: string;
  source_kind: string;
  source_field: string;
  source_import_id?: string | null;
  source_fingerprint: string;
  lineage_fingerprint: string;
  authority_revision: string;
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

export type MatrixEditorSessionDurationAuthority = {
  draft_duration_authority_id?: string | null;
  draft_group_id: string;
  draft_row_id: string;
  step_sequence: number;
  step_suffix_note: string;
  duration_value: string;
  duration_unit: string;
  normalized_hours: string;
  source_kind: string;
  source_field: string;
  source_import_id?: string | null;
  source_fingerprint: string;
  lineage_fingerprint: string;
  authority_revision: string;
  status: string;
};

export type MatrixEditorSessionDraft = {
  groups: MatrixEditorSessionDraftGroup[];
  rows: MatrixEditorSessionDraftRow[];
  cells: MatrixEditorSessionDraftCell[];
  duration_authorities?: MatrixEditorSessionDurationAuthority[];
};

export type MatrixEditorSessionSeed = {
  project_id: string;
  active_confirmed_matrix_id?: string | null;
  active_confirmed_revision?: number | null;
  active_source_import_id?: string | null;
  active_source_snapshot_id?: string | null;
  editor_source_import_id?: string | null;
  editor_source_snapshot_id?: string | null;
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
  editor_draft_id?: string | null;
  draft_status?: "missing" | "current" | "stale";
  loaded_source?: "authority" | "draft";
  stale_draft_present?: boolean;
  draft_updated_at?: string | null;
  saved_payload_signature?: string | null;
};

export type MatrixEditorSessionConfirmRequest = {
  expected_active_confirmed_matrix_id?: string | null;
  expected_active_confirmed_revision?: number | null;
  expected_editor_draft_id?: string | null;
  expected_saved_payload_signature?: string | null;
  source_document_path?: string | null;
  source_document_name?: string | null;
  source_format?: string | null;
  source_import_id?: string | null;
  source_snapshot_id?: string | null;
  confirmed_by: string;
  groups: MatrixEditorSessionDraftGroup[];
  rows: MatrixEditorSessionDraftRow[];
  cells: MatrixEditorSessionDraftCell[];
  duration_authorities?: MatrixEditorSessionDurationAuthority[];
  pre_test_buffer_days?: string | null;
  post_test_buffer_days?: string | null;
  sample_received_date?: string | null;
  planned_test_start_date?: string | null;
  planned_test_complete_date?: string | null;
  estimated_completion_date?: string | null;
};

export type MatrixEditorSessionDraftSaveRequest = Omit<
  MatrixEditorSessionConfirmRequest,
  "confirmed_by" | "expected_editor_draft_id" | "expected_saved_payload_signature"
>;

export type MatrixEditorSessionDraftSaveResponse = {
  editor_draft_id: string;
  draft_status: "current";
  draft_updated_at: string;
  saved_payload_signature: string;
  active_confirmed_matrix_id: string;
  active_confirmed_revision: number;
};

export type MatrixEditorSessionDraftDiscardRequest = {
  expected_editor_draft_id?: string | null;
  expected_saved_payload_signature?: string | null;
};

export type MatrixEditorSessionDraftDiscardResponse = {
  discarded: boolean;
  active_confirmed_matrix_id?: string | null;
  active_confirmed_revision?: number | null;
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
  sample_note?: string | null;
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

export type MatrixEditorLiveXlsxExportRequest = {
  source: "matrix_editor_current_ui_state";
  project_reference: string;
  groups: Array<{
    group_id: string;
    group_key: string;
    group_label: string;
    sample_size: string;
    time_display: string;
  }>;
  rows: Array<{
    row_id: string;
    test_item: string;
    section: string;
    test_method: string;
    condition: string;
    requirement: string;
    cells: Array<{ group_id: string; step_text: string }>;
  }>;
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
  duration_authorities?: MatrixDurationAuthority[];
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
  page_number?: number | null;
  page_table_index?: number | null;
  table_text_query?: string | null;
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
  standard_version_unavailable_action?: MatrixImportStandardVersionUnavailableAction;
};

export type MatrixImportStandardVersionUnavailableAction =
  | "prompt_if_unavailable"
  | "preserve_imported_methods";

export type MatrixImportStandardVersionUnavailableReason =
  | "standard_version_not_configured"
  | "standard_version_inactive"
  | "standard_version_file_missing"
  | "standard_version_file_unavailable"
  | "standard_version_runtime_unavailable";

export type MatrixImportStandardVersionActionRequiredDetail = {
  code: "matrix_import_standard_version_action_required";
  reason_code: MatrixImportStandardVersionUnavailableReason;
  message: string;
};

export type MatrixImportCommitResponse = {
  source_import_id: string;
  source_snapshot_id: string;
  selected_group_keys_committed: string[];
  commit_status: "created" | "reused";
  project_matrix_draft: ProjectMatrixDraft;
  method_authority_sync: {
    status: "synchronized" | "review_required" | "source_preserved";
    updated_count: number;
    current_count: number;
    review_count: number;
    standard_resource_id: string | null;
    effective_worksheet_name: string | null;
    catalog_fingerprint: string | null;
    context_fingerprint: string;
    rows: Array<{
      stable_source_row_key: string;
      row_order: number;
      test_item: string;
      current_method: string | null;
      status: string;
      resulting_method: string | null;
      matched_standard_code: string | null;
      source_row_number: number | null;
      reason: string | null;
      applied: boolean;
    }>;
    warning?: {
      code: "standard_version_unavailable";
      message: string;
    } | null;
  };
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

export type MatrixEditorTestRecordPublicationPreview = {
  project_id: string;
  mode: "download" | "official";
  status: "ready" | "conflict" | "blocked";
  target_path: string | null;
  existing_file: boolean;
  existing_modified_at: string | null;
  blockers: string[];
  preview_token: string;
};

export type MatrixEditorTestRecordPublicationResult = {
  project_id: string;
  target_path: string;
  archive_path: string | null;
  file_name: string;
};

export type MatrixEditorTestStatusDraftRequest = MatrixEditorTestRecordDraftRequest & {
  project_reference?: string | null;
};

export type MatrixEditorLlcrCrRecordDraftRequest = MatrixEditorTestRecordDraftRequest & {
  record_type: LlcrCrRecordType;
};

export type MatrixResolvedDirectoryCandidate = {
  candidate_id: string;
  file_name: string;
};

type MatrixSourceCandidatesResponseBase = {
  project_id: string;
  warnings: string[];
  source_title: string;
  preferred_import_directory: string | null;
  preferred_import_directory_source:
    | "submitted_material"
    | "intake_attachments"
    | "unavailable";
};

export type MatrixRegisteredSourceCandidatesResponse = MatrixSourceCandidatesResponseBase & {
  view: "registered_assets";
  candidates: MatrixSourceCandidate[];
};

export type MatrixResolvedDirectoryCandidatesResponse = MatrixSourceCandidatesResponseBase & {
  view: "resolved_directory";
  candidates: MatrixResolvedDirectoryCandidate[];
};

export type MatrixSourceCandidatesResponse =
  | MatrixRegisteredSourceCandidatesResponse
  | MatrixResolvedDirectoryCandidatesResponse;

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
  | "test_status"
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
  duplicate_resolution?: CompleteNewProjectDuplicateResolutionInput | null;
  specified_ltr_workbook_preview_ack?: SpecifiedLtrWorkbookAuthorityPreviewAck | null;
};

export type SpecifiedLtrWorkbookAuthorityPreviewInput = {
  specified_ltr_number: string;
};

export type SpecifiedLtrWorkbookAuthorityRowValue = {
  field_name: string;
  label: string;
  value: unknown | null;
  is_blank: boolean;
};

export type SpecifiedLtrWorkbookAuthorityPreviewAck = {
  acknowledged: boolean;
  ltr_number: string;
  sheet_name: string;
  row_number: number;
  preview_token: string;
  row_fingerprint: string;
};

export type SpecifiedLtrWorkbookAuthorityPreview = {
  status: "found" | "not_found" | "blocked";
  ltr_number: string;
  message: string;
  workbook_path?: string | null;
  sheet_name?: string | null;
  row_number?: number | null;
  row_values: SpecifiedLtrWorkbookAuthorityRowValue[];
  preview_ack?: SpecifiedLtrWorkbookAuthorityPreviewAck | null;
  blockers: string[];
  warnings: string[];
};

export type CompleteNewProjectDuplicateResolutionInput = {
  action: "replace_local_association";
  token: string;
  acknowledged: boolean;
  reason?: string | null;
};

export type LocalLtrDuplicateConflictDetail = {
  code: "LOCAL_LTR_DUPLICATE";
  message: string;
  ltr_number: string;
  existing: {
    ltr_id: string;
    project_id: string;
    display_project_id: string;
    project_name?: string | null;
    product_name?: string | null;
    sample_description?: string | null;
    test_item?: string | null;
    requester?: string | null;
    registered_on?: string | null;
    recent_activity_at?: string | null;
    project_status?: string | null;
    lifecycle_state?: string | null;
    has_local_folder?: boolean;
    local_folder_path?: string | null;
    has_matrix?: boolean;
    has_outputs?: boolean;
  };
  current: {
    case_id: string;
    project_id: string;
    project_name?: string | null;
    requester?: string | null;
  };
  resolution: {
    token: string;
    expires_at: string;
    allowed_actions: string[];
    requires_second_confirmation: boolean;
  };
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

export type LtrWorkbookBasicInformationSyncColumn = {
  column: string;
  field_name: string;
  value: unknown;
};

export type LtrWorkbookBasicInformationSyncComparisonValue = {
  field_name: string;
  label: string;
  current_value: unknown;
  pending_value: unknown;
  changed: boolean;
};

export type LtrWorkbookBasicInformationSyncPreview = {
  status: string;
  project_id: string;
  ltr_number: string;
  workbook_path: string | null;
  target_sheet: string | null;
  target_row: number | null;
  columns: LtrWorkbookBasicInformationSyncColumn[];
  comparison_values: LtrWorkbookBasicInformationSyncComparisonValue[];
  confirmed_basic_information_version: number | null;
  confirmed_basic_information_source_signature_hash: string | null;
  blockers: string[];
  warnings: string[];
};

export type LtrWorkbookBasicInformationSyncCommitInput = {
  operator_confirmed: boolean;
  preview_acknowledged: boolean;
  expected_confirmed_basic_information_version: number;
  expected_confirmed_basic_information_source_signature_hash: string;
};

export type LtrWorkbookBasicInformationSyncCommit = {
  project_id: string;
  ltr_number: string;
  workbook_path: string;
  backup_path: string;
  sheet_name: string;
  row_number: number;
  confirmed_basic_information_version: number;
  confirmed_basic_information_source_signature_hash: string;
};

export type LtrWorkbookBasicInformationReadonlyOpen = {
  project_id: string;
  ltr_number: string;
  workbook_path: string;
  sheet_name: string;
  row_number: number;
  column_number: number;
  selected_cell: string;
  message: string;
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

export type FeeEvaluationFieldMetadata = {
  field:
    | "spend_time"
    | "unit_price"
    | "unit_label"
    | "units"
    | "base_fee"
    | "discount_percent"
    | "testing_fee";
  state:
    | "auto_filled"
    | "suggested_review"
    | "manual_required"
    | "not_available";
  source: string | null;
  message: string | null;
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
  spend_time: string;
  unit_label: string;
  unit_price: string | null;
  units: string | null;
  base_fee: string | null;
  discount_percent: string | null;
  testing_fee: string | null;
  field_metadata?: FeeEvaluationFieldMetadata[];
  warnings: FeeEvaluationWarning[];
};

export type FeeEvaluationGroup = {
  group_key: string;
  group_label: string;
  sample_quantity_expression: string;
  manual_line_items?: FeeEvaluationLineItem[];
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
  manual_line_items?: FeeEvaluationLineItem[];
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
  pricing_draft_edit_id?: string | null;
  pricing_draft_generation?: number | null;
  pricing_draft_payload_fingerprint?: string | null;
  pricing_draft_validation_token?: string | null;
};

export type FeeEvaluationPricingDraftSaveRequest =
  FeeEvaluationEditedFileExportRequest & {
    expected_confirmed_matrix_id?: string | null;
    expected_confirmed_revision?: number | null;
    expected_fee_rule_version_id?: string | null;
    expected_pricing_draft_edit_id?: string | null;
    expected_generation?: number | null;
    expected_payload_fingerprint?: string | null;
    expected_updated_at?: string | null;
  };

export type FeeEvaluationPricingDraftStatus =
  | "missing"
  | "current_v2"
  | "rebase_required"
  | "legacy_unclassified"
  | "blocked"
  // Compatibility only for an in-flight pre-V2 server during desktop upgrades.
  | "current"
  | "stale";

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
  saved_generation?: number | null;
  saved_payload_fingerprint?: string | null;
  saved_validation_token?: string | null;
  saved_source_context_fingerprint?: string | null;
  payload?: FeeEvaluationEditedFileExportRequest | null;
};

export type FeeEvaluationPricingDraftDiscardRequest = {
  expected_pricing_draft_edit_id?: string | null;
  expected_confirmed_matrix_id?: string | null;
  expected_confirmed_revision?: number | null;
  expected_fee_rule_version_id?: string | null;
};

export type FeeEvaluationPricingDraftDiscardResponse = {
  discarded: boolean;
  current_confirmed_matrix_id: string;
  current_confirmed_revision: number;
  current_fee_rule_version_id: string;
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
  fee_review_required_count?: number;
  confirmed_fee?: ConfirmedFeeVersion | null;
};

export type ConfirmFeeVersionRequest = {
  confirmed_by: string;
  expected_pricing_draft_edit_id: string;
  summary: ConfirmedFeeSummary;
  expected_generation?: number | null;
  expected_payload_fingerprint?: string | null;
  expected_validation_token?: string | null;
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

export type ContactMeasurementPlanFamily = {
  family_id: string;
  family_ordinal: number;
  label: string;
  count_per_sample: number;
  record_label: string;
  record_prefix: string;
  included: boolean;
  is_custom: boolean;
};

export type ContactMeasurementPlanTarget = {
  stable_target_key: string;
  group_label: string;
  test_item: string;
  contact_kind: "llcr" | "cr_specified_current";
  step_sequence: number;
  step_suffix_note: string;
  sample_quantity_expression: string;
  eligible: boolean;
  included: boolean;
  exclusion_reason: string | null;
  is_override: boolean;
  coverage_state: string;
  readings_per_sample: number;
  target_review_state: string;
  target_review_reason: string | null;
  families: ContactMeasurementPlanFamily[];
};

export type ContactMeasurementPlanWorkspace = {
  status: string;
  project_id: string;
  active_confirmed_revision_id: string | null;
  editable_revision_id: string | null;
  editable_revision_state: string | null;
  editable_revision_fingerprint: string | null;
  revision: {
    revision_id: string;
    revision_sequence: number;
    state: string;
    fingerprint: string;
  } | null;
  matrix_binding: {
    base_confirmed_matrix_id: string;
    base_matrix_revision: number;
    current_confirmed_matrix_id: string | null;
    current_matrix_revision: number | null;
    matrix_binding_fingerprint: string;
  } | null;
  targets: ContactMeasurementPlanTarget[];
  impacts: Array<{
    impact_subject_key: string;
    category: string;
    severity: string;
    resolution_state: string;
    reason: string | null;
    candidate: {
      group_label: string;
      test_item: string;
      step_sequence: number;
      step_suffix_note: string;
    } | null;
  }>;
  summary: {
    included_target_count: number;
    total_target_count: number;
    needs_review_count: number;
    readings_by_kind: Record<string, number | null>;
  };
  diagnostics: string[];
  family_id_high_water_by_kind: {
    llcr: number;
    cr_specified_current: number;
  };
};

export type DraftMeasurementPlanWorkbookPreview = {
  project_id: string;
  revision_id: string | null;
  revision_sequence: number | null;
  revision_state: string | null;
  revision_fingerprint: string | null;
  matrix_id: string | null;
  matrix_revision: number | null;
  matrix_binding_fingerprint: string | null;
  status: "ready" | "review_required" | "blocked" | "empty";
  output_label: "DRAFT" | "NEEDS REVIEW" | null;
  preview_fingerprint: string | null;
  row_count: number;
  sections: Array<{ record_type: string; group_label: string; source_step: string; rows: unknown[] }>;
  diagnostics: Array<{ code: string; severity: string; message: string }>;
  generate_allowed: boolean;
};

export type DraftMeasurementPlanWorkbookArtifact = {
  project_id: string;
  revision_id: string;
  artifact_id: string;
  file_name: string;
  output_label: "DRAFT" | "NEEDS REVIEW";
  download_url: string;
  cleanup_warning: string | null;
};

export type ContactMeasurementPlanRevisionResponse = {
  status: string;
  revision_id: string;
};

export type ContactMeasurementPlanTargetPatchRequest = {
  actor: string;
  expected_revision_fingerprint: string;
  stable_target_key: string;
  included: boolean;
  exclusion_reason?: string | null;
  families?: Array<{
    family_id: string;
    label: string;
    count_per_sample: number;
    record_label: string;
    record_prefix: string;
    included: boolean;
    is_custom: boolean;
  }>;
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

const MATRIX_IMPORT_STANDARD_VERSION_UNAVAILABLE_REASONS = new Set<string>([
  "standard_version_not_configured",
  "standard_version_inactive",
  "standard_version_file_missing",
  "standard_version_file_unavailable",
  "standard_version_runtime_unavailable",
]);

export function isMatrixImportStandardVersionActionRequiredError(
  error: unknown
): error is ApiRequestError & { detail: MatrixImportStandardVersionActionRequiredDetail } {
  if (!(error instanceof ApiRequestError) || error.status !== 409) {
    return false;
  }
  const detail = error.detail;
  if (!detail || typeof detail !== "object") {
    return false;
  }
  const candidate = detail as Record<string, unknown>;
  return (
    candidate.code === "matrix_import_standard_version_action_required" &&
    typeof candidate.reason_code === "string" &&
    MATRIX_IMPORT_STANDARD_VERSION_UNAVAILABLE_REASONS.has(candidate.reason_code) &&
    typeof candidate.message === "string" &&
    candidate.message.length > 0
  );
}

export function isProjectLifecycleReadonlyErrorDetail(
  detail: unknown
): detail is ProjectLifecycleReadonlyErrorDetail {
  if (!detail || typeof detail !== "object") {
    return false;
  }
  const value = detail as Record<string, unknown>;
  return (
    value.code === "project_lifecycle_readonly" &&
    typeof value.project_id === "string" &&
    isProjectLifecycleState(value.lifecycle_state) &&
    (value.closure_type === null || isProjectClosureType(value.closure_type)) &&
    typeof value.message === "string" &&
    Array.isArray(value.allowed_actions) &&
    value.allowed_actions.every((action) => typeof action === "string")
  );
}

export function isLocalLtrDuplicateConflictDetail(
  detail: unknown
): detail is LocalLtrDuplicateConflictDetail {
  if (!detail || typeof detail !== "object") {
    return false;
  }
  const value = detail as Record<string, unknown>;
  const existing = value.existing as Record<string, unknown> | undefined;
  const current = value.current as Record<string, unknown> | undefined;
  const resolution = value.resolution as Record<string, unknown> | undefined;
  return (
    value.code === "LOCAL_LTR_DUPLICATE" &&
    typeof value.message === "string" &&
    typeof value.ltr_number === "string" &&
    !!existing &&
    typeof existing.ltr_id === "string" &&
    typeof existing.project_id === "string" &&
    typeof existing.display_project_id === "string" &&
    !!current &&
    typeof current.case_id === "string" &&
    typeof current.project_id === "string" &&
    !!resolution &&
    typeof resolution.token === "string" &&
    typeof resolution.expires_at === "string" &&
    Array.isArray(resolution.allowed_actions)
  );
}

function isProjectLifecycleState(value: unknown): value is ProjectLifecycleState {
  return value === "active" || value === "stopped" || value === "closed";
}

function isProjectClosureType(value: unknown): value is ProjectClosureType {
  return value === "completed" || value === "administrative";
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

async function requestNoContent(path: string, init?: RequestInit): Promise<void> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.headers ?? {})
    }
  });
  if (!response.ok) {
    throw await responseError(response);
  }
}

export type FrontendErrorReport = {
  kind: "window_error" | "unhandled_rejection";
  message: string;
  stack?: string | null;
  page_path?: string | null;
};

export type FeeFormPublicationPreview = {
  mode: "download" | "official";
  status: "ready" | "blocked" | "conflict";
  existing_file: boolean;
  existing_modified_at: string | null;
  blockers: string[];
  preview_token: string;
};

export type FeeFormPublicationResult = {
  file_name: string;
  archive_path: string | null;
};

export function reportFrontendError(report: FrontendErrorReport): Promise<void> {
  return requestNoContent("/api/support/frontend-errors", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(report)
  });
}

export function downloadSupportDiagnosticBundle(): Promise<BlobDownloadResponse> {
  return requestBlobResponse("/api/support/diagnostics");
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

export function fetchContactMeasurementPlanWorkspace(
  projectId: string
): Promise<ContactMeasurementPlanWorkspace> {
  return requestJson<ContactMeasurementPlanWorkspace>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-measurement-plan/workspace`
  );
}

export function previewDraftMeasurementPlanWorkbook(
  projectId: string,
  revisionId: string
): Promise<DraftMeasurementPlanWorkbookPreview> {
  return requestJson<DraftMeasurementPlanWorkbookPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-measurement-plan/revisions/${encodeURIComponent(revisionId)}/draft-workbook/preview`,
    { method: "POST" }
  );
}

export function generateDraftMeasurementPlanWorkbook(
  projectId: string,
  revisionId: string,
  previewFingerprint: string
): Promise<DraftMeasurementPlanWorkbookArtifact> {
  return requestJson<DraftMeasurementPlanWorkbookArtifact>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-measurement-plan/revisions/${encodeURIComponent(revisionId)}/draft-workbook/generate`,
    { method: "POST", body: JSON.stringify({ preview_fingerprint: previewFingerprint }) }
  );
}

export function fetchLatestDraftMeasurementPlanWorkbook(
  projectId: string
): Promise<DraftMeasurementPlanWorkbookArtifact | null> {
  return requestJson<DraftMeasurementPlanWorkbookArtifact | null>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-measurement-plan/draft-workbook/artifacts/latest`
  );
}

export function openContactMeasurementPlanRevision(
  projectId: string,
  actor: string
): Promise<ContactMeasurementPlanRevisionResponse> {
  return requestJson<ContactMeasurementPlanRevisionResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-measurement-plan/revisions`,
    { method: "POST", body: JSON.stringify({ actor }) }
  );
}

export function saveContactMeasurementPlanRevision(
  projectId: string,
  revisionId: string,
  actor: string,
  expectedRevisionFingerprint: string
): Promise<ContactMeasurementPlanRevisionResponse> {
  return requestJson<ContactMeasurementPlanRevisionResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-measurement-plan/revisions/${encodeURIComponent(revisionId)}`,
    {
      method: "PUT",
      body: JSON.stringify({ actor, expected_revision_fingerprint: expectedRevisionFingerprint }),
    }
  );
}

export function patchContactMeasurementPlanTarget(
  projectId: string,
  revisionId: string,
  request: ContactMeasurementPlanTargetPatchRequest
): Promise<ContactMeasurementPlanRevisionResponse> {
  return requestJson<ContactMeasurementPlanRevisionResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-measurement-plan/revisions/${encodeURIComponent(revisionId)}/targets`,
    { method: "PATCH", body: JSON.stringify(request) }
  );
}

export function confirmContactMeasurementPlanRevision(
  projectId: string,
  revisionId: string,
  actor: string,
  expectedRevisionFingerprint: string
): Promise<ContactMeasurementPlanRevisionResponse> {
  return requestJson<ContactMeasurementPlanRevisionResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-measurement-plan/revisions/${encodeURIComponent(revisionId)}/confirm`,
    {
      method: "POST",
      body: JSON.stringify({ actor, expected_revision_fingerprint: expectedRevisionFingerprint }),
    }
  );
}

export function refreshContactMeasurementPlanImpacts(
  projectId: string,
  revisionId: string,
  actor: string,
  expectedMatrixBindingFingerprint: string
): Promise<ContactMeasurementPlanRevisionResponse> {
  return requestJson<ContactMeasurementPlanRevisionResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-measurement-plan/revisions/${encodeURIComponent(revisionId)}/impacts/refresh`,
    {
      method: "POST",
      body: JSON.stringify({ actor, expected_matrix_binding_fingerprint: expectedMatrixBindingFingerprint }),
    }
  );
}

export function acceptCompatibleContactMeasurementPlanSuggestions(
  projectId: string,
  revisionId: string,
  actor: string,
  expectedRevisionFingerprint: string
): Promise<ContactMeasurementPlanRevisionResponse> {
  return requestJson<ContactMeasurementPlanRevisionResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-measurement-plan/revisions/${encodeURIComponent(revisionId)}/suggestions/accept-compatible`,
    {
      method: "POST",
      body: JSON.stringify({ actor, expected_revision_fingerprint: expectedRevisionFingerprint }),
    }
  );
}

export function rebindContactMeasurementPlanTarget(
  projectId: string,
  revisionId: string,
  actor: string,
  expectedRevisionFingerprint: string,
  stableTargetKey: string,
  candidateSubjectKey: string
): Promise<ContactMeasurementPlanRevisionResponse> {
  return requestJson<ContactMeasurementPlanRevisionResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-measurement-plan/revisions/${encodeURIComponent(revisionId)}/targets/rebind`,
    {
      method: "POST",
      body: JSON.stringify({
        actor,
        expected_revision_fingerprint: expectedRevisionFingerprint,
        stable_target_key: stableTargetKey,
        candidate_subject_key: candidateSubjectKey,
      }),
    }
  );
}

export function getProjectLifecycle(projectId: string): Promise<ProjectLifecycleResponse> {
  return requestJson<ProjectLifecycleResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/lifecycle`
  );
}

export function stopProjectLifecycle(
  projectId: string,
  input: ProjectLifecycleActionRequest
): Promise<ProjectLifecycleResponse> {
  return requestJson<ProjectLifecycleResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/lifecycle/stop`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function resumeProjectLifecycle(
  projectId: string,
  input: ProjectLifecycleActionRequest
): Promise<ProjectLifecycleResponse> {
  return requestJson<ProjectLifecycleResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/lifecycle/resume`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function activateProjectLifecycle(
  projectId: string,
  input: ProjectLifecycleActionRequest
): Promise<ProjectLifecycleResponse> {
  return requestJson<ProjectLifecycleResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/lifecycle/activate`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function closeProjectLifecycle(
  projectId: string,
  input: ProjectLifecycleCloseRequest
): Promise<ProjectLifecycleResponse> {
  return requestJson<ProjectLifecycleResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/lifecycle/close`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function closeProjectCompletedLifecycle(
  projectId: string,
  input: ProjectLifecycleCloseCompletedRequest
): Promise<ProjectLifecycleResponse> {
  return requestJson<ProjectLifecycleResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/lifecycle/close-completed`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function closeProjectAdministrativeLifecycle(
  projectId: string,
  input: ProjectLifecycleCloseAdministrativeRequest
): Promise<ProjectLifecycleResponse> {
  return requestJson<ProjectLifecycleResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/lifecycle/close-administrative`,
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
  input: { path: string; active: boolean; worksheet_name?: string | null }
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

export function previewMatrixMethodVersionSync(
  projectId: string,
  input: {
    project_matrix_draft_id: string;
    expected_saved_payload_signature: string;
  }
): Promise<MatrixMethodVersionSyncPreview> {
  return requestJson<MatrixMethodVersionSyncPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-method-version-sync/preview`,
    { method: "POST", body: JSON.stringify(input) }
  );
}

export function applyMatrixMethodVersionSync(
  projectId: string,
  input: {
    project_matrix_draft_id: string;
    expected_saved_payload_signature: string;
    preview_fingerprint: string;
    selected_draft_row_ids: string[];
    applied_by: string;
  }
): Promise<MatrixMethodVersionSyncApplyResponse> {
  return requestJson<MatrixMethodVersionSyncApplyResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-method-version-sync/apply`,
    { method: "POST", body: JSON.stringify(input) }
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

export function previewSpecifiedLtrWorkbookAuthority(
  caseId: string,
  input: SpecifiedLtrWorkbookAuthorityPreviewInput
): Promise<SpecifiedLtrWorkbookAuthorityPreview> {
  return requestJson<SpecifiedLtrWorkbookAuthorityPreview>(
    `/api/intake-cases/${encodeURIComponent(caseId)}/specified-ltr-workbook-authority-preview`,
    {
      method: "POST",
      body: JSON.stringify(input)
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

export function previewLtrWorkbookBasicInformationSync(
  projectId: string
): Promise<LtrWorkbookBasicInformationSyncPreview> {
  return requestJson<LtrWorkbookBasicInformationSyncPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/ltr-workbook/basic-information-sync/preview`,
    { cache: "no-store" }
  );
}

export function commitLtrWorkbookBasicInformationSync(
  projectId: string,
  input: LtrWorkbookBasicInformationSyncCommitInput
): Promise<LtrWorkbookBasicInformationSyncCommit> {
  return requestJson<LtrWorkbookBasicInformationSyncCommit>(
    `/api/projects/${encodeURIComponent(projectId)}/ltr-workbook/basic-information-sync/commit`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}

export function openLtrWorkbookBasicInformationSyncReadonly(
  projectId: string
): Promise<LtrWorkbookBasicInformationReadonlyOpen> {
  return requestJson<LtrWorkbookBasicInformationReadonlyOpen>(
    `/api/projects/${encodeURIComponent(projectId)}/ltr-workbook/basic-information-sync/open-readonly`,
    { method: "POST" }
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

export function openLocalProjectFolder(
  projectId: string
): Promise<ProjectFolderOpenResponse> {
  return requestJson<ProjectFolderOpenResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/folder/open-local`,
    { method: "POST" }
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

export function saveMatrixEditorSessionDraft(
  projectId: string,
  input: MatrixEditorSessionDraftSaveRequest,
  options: Pick<RequestInit, "signal"> = {}
): Promise<MatrixEditorSessionDraftSaveResponse> {
  return requestJson<MatrixEditorSessionDraftSaveResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-editor/session/draft`,
    {
      method: "PUT",
      body: JSON.stringify(input),
      signal: options.signal,
    }
  );
}

export function discardMatrixEditorSessionDraft(
  projectId: string,
  input: MatrixEditorSessionDraftDiscardRequest = {}
): Promise<MatrixEditorSessionDraftDiscardResponse> {
  return requestJson<MatrixEditorSessionDraftDiscardResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-editor/session/draft`,
    {
      method: "DELETE",
      body: JSON.stringify(input),
    }
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
): Promise<MatrixRegisteredSourceCandidatesResponse>;
export function listProjectTestPlanSourceCandidates(
  projectId: string,
  view: "registered_assets"
): Promise<MatrixRegisteredSourceCandidatesResponse>;
export function listProjectTestPlanSourceCandidates(
  projectId: string,
  view: "resolved_directory"
): Promise<MatrixResolvedDirectoryCandidatesResponse>;
export function listProjectTestPlanSourceCandidates(
  projectId: string,
  view: "registered_assets" | "resolved_directory" = "registered_assets"
): Promise<MatrixSourceCandidatesResponse> {
  const query = view === "registered_assets" ? "" : "?view=resolved_directory";
  return requestJson<MatrixSourceCandidatesResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/test-plan/source-candidates${query}`
  );
}

export function previewProjectTestPlanMatrixFromSourceCandidate(
  projectId: string,
  sourceAssetId: string,
  view: "registered_assets" | "resolved_directory" = "registered_assets"
): Promise<MatrixPreviewResponse> {
  const query = view === "registered_assets" ? "" : "?view=resolved_directory";
  return requestJson<MatrixPreviewResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/test-plan/source-candidates/${encodeURIComponent(sourceAssetId)}/matrix-preview${query}`,
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
  projectId: string,
  input: OfficialWorkspaceCreateRequest = {}
): Promise<OfficialWorkspaceCreateResponse> {
  return requestJson<OfficialWorkspaceCreateResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/official-workspace/create`,
    {
      method: "POST",
      body: JSON.stringify(input),
    }
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

function publicFolderWorkflowPath(
  projectId: string,
  suffix: string
): string {
  return `/api/projects/${encodeURIComponent(projectId)}/public-folder-workflow${suffix}`;
}

export function getPublicFolderWorkflowContext(
  projectId: string
): Promise<PublicFolderWorkflowContext> {
  return requestJson<PublicFolderWorkflowContext>(
    publicFolderWorkflowPath(projectId, "/context"),
    { cache: "no-store" }
  );
}

export function setPublicFolderWorkflowAutoSync(
  projectId: string,
  autoSyncEnabled: boolean
): Promise<PublicFolderWorkflowState> {
  return requestJson<PublicFolderWorkflowState>(
    publicFolderWorkflowPath(projectId, "/auto-sync"),
    {
      method: "PUT",
      body: JSON.stringify({ auto_sync_enabled: autoSyncEnabled }),
    }
  );
}

export function previewPublicFolderWorkflowSync(
  projectId: string
): Promise<PublicFolderWorkflowPreview> {
  return requestJson<PublicFolderWorkflowPreview>(
    publicFolderWorkflowPath(projectId, "/sync/preview"),
    { method: "POST" }
  );
}

export function executePublicFolderWorkflowSync(
  projectId: string,
  input: PublicFolderWorkflowExecuteInput
): Promise<PublicFolderWorkflowResult> {
  return requestJson<PublicFolderWorkflowResult>(
    publicFolderWorkflowPath(projectId, "/sync/execute"),
    {
      method: "POST",
      body: JSON.stringify(input),
    }
  );
}

export function previewPublicFolderWorkflowSubmit(
  projectId: string
): Promise<PublicFolderWorkflowPreview> {
  return requestJson<PublicFolderWorkflowPreview>(
    publicFolderWorkflowPath(projectId, "/submit/preview"),
    { method: "POST" }
  );
}

export function executePublicFolderWorkflowSubmit(
  projectId: string,
  input: PublicFolderWorkflowExecuteInput
): Promise<PublicFolderWorkflowResult> {
  return requestJson<PublicFolderWorkflowResult>(
    publicFolderWorkflowPath(projectId, "/submit/execute"),
    {
      method: "POST",
      body: JSON.stringify(input),
    }
  );
}

export function previewPublicFolderWorkflowPull(
  projectId: string
): Promise<PublicFolderWorkflowPreview> {
  return requestJson<PublicFolderWorkflowPreview>(
    publicFolderWorkflowPath(projectId, "/pull/preview"),
    { method: "POST" }
  );
}

export function executePublicFolderWorkflowPull(
  projectId: string,
  input: PublicFolderWorkflowExecuteInput
): Promise<PublicFolderWorkflowResult> {
  return requestJson<PublicFolderWorkflowResult>(
    publicFolderWorkflowPath(projectId, "/pull/execute"),
    {
      method: "POST",
      body: JSON.stringify(input),
    }
  );
}

export function getProjectBasicInformation(
  projectId: string
): Promise<ProjectBasicInformationResponse> {
  return requestJson<ProjectBasicInformationResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/basic-information`,
    { cache: "no-store" }
  );
}

export function saveProjectBasicInformationDraft(
  projectId: string,
  values: Record<string, string>
): Promise<ProjectBasicInformationResponse> {
  return requestJson<ProjectBasicInformationResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/basic-information/draft`,
    {
      method: "PUT",
      body: JSON.stringify({ values } satisfies ProjectBasicInformationDraftRequest),
    }
  );
}

export function confirmProjectBasicInformation(
  projectId: string,
  values: Record<string, string>,
  confirmedBy: string
): Promise<ProjectBasicInformationResponse> {
  return requestJson<ProjectBasicInformationResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/basic-information/confirm`,
    {
      method: "POST",
      body: JSON.stringify({
        values,
        confirmed_by: confirmedBy,
      } satisfies ProjectBasicInformationConfirmRequest),
    }
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

export function writeBackProjectApplicationForm(
  projectId: string
): Promise<ApplicationFormWriteBackResponse> {
  return requestJson<ApplicationFormWriteBackResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/project-folder/application-form/write-back`,
    { method: "POST" }
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

export function previewLlcrCrRecordWorkbook(
  projectId: string,
  recordType: LlcrCrRecordType,
): Promise<LlcrCrRecordWorkbookPreviewResponse> {
  return requestJson<LlcrCrRecordWorkbookPreviewResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/llcr-cr-record-workbook/preview?record_type=${recordType}`,
    { method: "POST" }
  );
}

export function generateLlcrCrRecordWorkbook(
  projectId: string,
  input: LlcrCrRecordWorkbookGenerateRequest
): Promise<LlcrCrRecordWorkbookGenerateResponse> {
  return requestJson<LlcrCrRecordWorkbookGenerateResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/llcr-cr-record-workbook/generate`,
    { method: "POST", body: JSON.stringify(input) }
  );
}

export function downloadLlcrCrRecordWorkbook(
  projectId: string,
  artifactId: string
): Promise<BlobDownloadResponse> {
  return requestBlobResponse(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/llcr-cr-record-workbook/files/${encodeURIComponent(artifactId)}`
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
  input: FeeEvaluationPricingDraftSaveRequest,
  options: Pick<RequestInit, "signal"> = {}
): Promise<FeeEvaluationPricingDraftResponse> {
  return requestJson<FeeEvaluationPricingDraftResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/fee-evaluation/pricing-draft`,
    {
      method: "PUT",
      body: JSON.stringify(input),
      signal: options.signal,
    }
  );
}

export function discardFeeEvaluationPricingDraft(
  projectId: string,
  input: FeeEvaluationPricingDraftDiscardRequest = {}
): Promise<FeeEvaluationPricingDraftDiscardResponse> {
  return requestJson<FeeEvaluationPricingDraftDiscardResponse>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/fee-evaluation/pricing-draft`,
    {
      method: "DELETE",
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

export function previewFeeFormPublication(
  projectId: string,
  input: FeeEvaluationEditedFileExportRequest
): Promise<FeeFormPublicationPreview> {
  return requestJson<FeeFormPublicationPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/fee-evaluation/fee-form-publication/preview`,
    { method: "POST", body: JSON.stringify(input) }
  );
}

export function publishFeeForm(
  projectId: string,
  input: FeeEvaluationEditedFileExportRequest & {
    preview_token: string;
    conflict_action: "none" | "archive" | "recycle";
  }
): Promise<FeeFormPublicationResult> {
  return requestJson<FeeFormPublicationResult>(
    `/api/projects/${encodeURIComponent(projectId)}/confirmed-matrix/fee-evaluation/fee-form-publication/publish`,
    { method: "POST", body: JSON.stringify(input) }
  );
}

export function previewMatrixEditorTestRecordPublication(
  projectId: string,
  input: MatrixEditorTestRecordDraftRequest
): Promise<MatrixEditorTestRecordPublicationPreview> {
  return requestJson<MatrixEditorTestRecordPublicationPreview>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-editor/test-record-publication/preview`,
    {
      method: "POST",
      body: JSON.stringify(input),
    }
  );
}

export function publishMatrixEditorTestRecord(
  projectId: string,
  input: MatrixEditorTestRecordDraftRequest & {
    preview_token: string;
    conflict_action: "none" | "archive" | "recycle";
  }
): Promise<MatrixEditorTestRecordPublicationResult> {
  return requestJson<MatrixEditorTestRecordPublicationResult>(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-editor/test-record-publication/publish`,
    {
      method: "POST",
      body: JSON.stringify(input),
    }
  );
}

export function generateMatrixEditorTestStatusDraftDownload(
  projectId: string,
  input: MatrixEditorTestStatusDraftRequest
): Promise<BlobDownloadResponse> {
  return requestBlobResponse(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-editor/test-status-draft/generate`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    }
  );
}

export function generateTestReportDraftDownload(
  projectId: string
): Promise<BlobDownloadResponse> {
  return requestBlobResponse(
    `/api/projects/${encodeURIComponent(projectId)}/test-report-draft/generate`,
    { method: "POST" }
  );
}

export function generateMatrixEditorLlcrCrRecordDraftDownload(
  projectId: string,
  input: MatrixEditorLlcrCrRecordDraftRequest
): Promise<BlobDownloadResponse> {
  return requestBlobResponse(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-editor/llcr-cr-record-draft/generate`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    }
  );
}

export function exportMatrixEditorLiveXlsx(
  projectId: string,
  input: MatrixEditorLiveXlsxExportRequest
): Promise<BlobDownloadResponse> {
  return requestBlobResponse(
    `/api/projects/${encodeURIComponent(projectId)}/matrix-editor/live-xlsx-export`,
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

export type ProjectPointProfileCategory = {
  category_id: string | null;
  category_ordinal: number;
  label: string;
  count_per_sample: number;
  record_prefix: string;
  included: boolean;
  point_expression?: string | null;
  expression_status?: "explicit" | "legacy_count_only";
  legacy_contiguous_suggestion?: string | null;
};

export type ProjectPointProfileCrCoverageMode = "follow_llcr" | "custom";

export type ProjectPointProfileCrCoverage = {
  mode: ProjectPointProfileCrCoverageMode;
  selected_category_ids: string[];
  points_per_sample: number;
};

export type ProjectPointProfileRevision = {
  revision_id: string;
  revision_sequence: number;
  state: string;
  fingerprint: string;
  created_at: string;
  confirmed_at: string | null;
  categories: ProjectPointProfileCategory[];
  points_per_sample: number;
  delta_r_enabled: boolean;
  cr_coverage: ProjectPointProfileCrCoverage;
};

export type ProjectPointProfileWorkspace = {
  status: string;
  project_id: string;
  editable_revision: ProjectPointProfileRevision | null;
  confirmed_revision: ProjectPointProfileRevision | null;
  has_unconfirmed_draft: boolean;
  legacy_uniform_suggestion: ProjectPointProfileCategory[] | null;
  diagnostics: string[];
};

export type ProjectPointProfileSummary = {
  status: string;
  project_id: string;
  confirmed_revision: ProjectPointProfileRevision | null;
  points_per_sample: number | null;
  has_unconfirmed_draft: boolean;
  diagnostics: string[];
};

export type ProjectPointProfileCommand = {
  actor: string;
  expected_revision_id: string | null;
  expected_revision_fingerprint: string | null;
  categories: ProjectPointProfileCategory[];
};

export type ProjectPointProfileDirectCategory = {
  category_id: string | null;
  prefix: string;
  point_expression: string;
  cr_selected: boolean;
};

export type ProjectPointProfileDirectConfirmCommand = {
  actor: string;
  expected_confirmed_revision_id: string | null;
  expected_confirmed_revision_fingerprint: string | null;
  cr_coverage_mode: ProjectPointProfileCrCoverageMode;
  delta_r_enabled: boolean;
  categories: ProjectPointProfileDirectCategory[];
};

export function fetchProjectPointProfileWorkspace(projectId: string): Promise<ProjectPointProfileWorkspace> {
  return requestJson<ProjectPointProfileWorkspace>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-point-profile/workspace`
  );
}

export function fetchProjectPointProfileSummary(projectId: string): Promise<ProjectPointProfileSummary> {
  return requestJson<ProjectPointProfileSummary>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-point-profile/summary`
  );
}

export function saveProjectPointProfileDraft(projectId: string, command: ProjectPointProfileCommand): Promise<ProjectPointProfileRevision> {
  return requestJson<ProjectPointProfileRevision>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-point-profile/draft`,
    { method: "PUT", body: JSON.stringify(command) }
  );
}

export function confirmProjectPointProfile(projectId: string, command: ProjectPointProfileDirectConfirmCommand): Promise<ProjectPointProfileRevision> {
  return requestJson<ProjectPointProfileRevision>(
    `/api/projects/${encodeURIComponent(projectId)}/contact-point-profile/confirm`,
    { method: "POST", body: JSON.stringify(command) }
  );
}
