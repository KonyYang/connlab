import { requestJson, requestBlobResponse, type EquipmentListOneClickResult } from "./client";
import type { ReportAssemblyPlan } from './reportAuthoringBatch';
import type { ReportDeliveryOperation } from './reportAuthoringDelivery';

export type ReportSourceRole = "original" | "layout_reference" | "specification" | "temperature" | "cr" | "mechanical" | "photo" | "evidence" | "tools_result_package";
export type ReportSource = {
  source_id: string; role: ReportSourceRole; file_name: string; sha256: string;
  size_bytes: number; created_at: string; report_dl: string; download_url: string;
};
export type ReportMapping = {
  mapping_id: string; source_id: string; kind: "specification" | "identity" | "temperature" | "cr" | "mechanical" | "photo" | "acceptance";
  label: string; source_locator: string; value: string; status: "pending" | "confirmed"; reason: string;
  group_id: string; row_id: string; step_token: string; sample_ids: string[];
  matrix_id: string; confirmed_by: string; confirmed_at: string;
  report_text?: string;
  fact_role?: 'unspecified' | 'specification_number' | 'revision' | 'revision_date' | 'authorization_date';
  report_target?: ReportFactTarget | null;
};
export type ReportFactTarget = { part: string; paragraph: number; sha256: string };
export type ReportFactLocation = { text: string; target: ReportFactTarget };
export const getReportFactTargets = (projectId: string, outputId: string, revision: number, oldText: string) =>
  requestJson<ReportFactLocation[]>(base(projectId) + `/outputs/${encodeURIComponent(outputId)}/fact-targets?expected_revision=${revision}&old_text=${encodeURIComponent(oldText)}`);
export type ReportAuthoringOutput = {
  output_id: string; file_name: string; status: string; operation: string; issues: string[];
  download_url: string; base_source_id: string;
  artifact?: { sha256: string };
  parent_output_id?: string;
  photo_plan?: { plan_id: string; output_sha256: string; matrix_id: string; confirmed_by: string; assignments: ConfirmedPhotoAssignment[] };
  visual_preview?: ReportVisualPreviewRecord;
  evidence?: { result_id?: string; statistics?: Extract<EquipmentListOneClickResult, { status: "completed" }>["statistics"] };
};
export type ReportMatrixStep = { group_id: string; row_id: string; group_label: string; test_item: string; step_token: string };
export type ReportAuthoringState = {
  project_id: string; revision: number; sources: ReportSource[]; mappings: ReportMapping[];
  base_source_id: string | null; outputs: ReportAuthoringOutput[];
  context: { dl_number: string; matrix_id: string; steps: ReportMatrixStep[] };
  results?: ReportResult[];
  customer_outputs?: CustomerReportOutput[];
  applied_result_ids?: string[];
  assembly_plan?: ReportAssemblyPlan | null;
  delivery?: ReportDeliveryOperation | null;
};
export type ReportMappingInput = Omit<ReportMapping, "mapping_id" | "matrix_id" | "confirmed_at" | "confirmed_by"> & {
  expected_revision: number; mapping_id?: string; confirmed_by?: string;
};
const base = (projectId: string) => `/api/projects/${encodeURIComponent(projectId)}/report-workspace/authoring`;
export const getReportAuthoring = (projectId: string) => requestJson<ReportAuthoringState>(base(projectId));
export function uploadReportSource(projectId: string, file: File, role: ReportSourceRole, revision: number) {
  const body = new FormData(); body.set("file", file); body.set("role", role); body.set("expected_revision", String(revision));
  return requestJson<ReportAuthoringState>(base(projectId) + "/sources", { method: "POST", body });
}
export const saveReportMapping = (projectId: string, mapping: ReportMappingInput) =>
  requestJson<ReportAuthoringState>(base(projectId) + "/mappings", { method: "POST", body: JSON.stringify(mapping) });
export const selectReportBase = (projectId: string, sourceId: string, revision: number) =>
  requestJson<ReportAuthoringState>(base(projectId) + "/base", { method: "POST", body: JSON.stringify({ source_id: sourceId, expected_revision: revision }) });
export const downloadReportArtifact = (url: string) => requestBlobResponse(url);

export type ConfirmedPhotoAssignment = { slot_id: string; source_id: string; crop_mode: 'preserve' | 'centre_crop';
  scope?: 'step' | 'sample_overview' | 'project_context';
  accept_context_change?: boolean;
  accept_slot_transform: boolean; group_id: string; row_id: string; step_token: string; sample_ids: string[];
  stage: string; reason: string; reuse_reason: string };
export type ReportDocumentReviewData = {
  output_id: string; output_sha256: string; review_sha256: string; base_role: string; complete: boolean; notice: string;
  regions: { region_id: string; kind: string; text: string; sha256: string; target: ReportFactTarget;
    status: string; reasons: string[]; has_fields: boolean }[];
  region_groups: { region_id: string; kind: string; text: string; sha256: string; status: string; reasons: string[]; paragraph_count: number; region_ids: string[] }[];
  slots: (ReportPhotoSlot & { coverage: string })[];
  figures: { figure_id: string; caption: string; numbers: number[]; slot_ids: string[]; automatic_order: boolean; reason: string }[];
  findings: { code: string; message: string; location: string }[];
  numbering: { ready: boolean; issues: { code: string; message: string; location: string }[];
    replacements: { old: string; new: string; target: ReportFactTarget }[] };
  photo_candidates: { source_id: string; source_sha256: string; file_name: string; warning: string;
    suggestions: { slot_id: string; score: number; hints: string[] }[] }[];
};
export type ReportVisualPreviewRecord = {
  output_sha256: string; artifact: { sha256: string; file_name: string }; status: string; page_count: number;
  pages: { page: number; width: number; height: number; text: string }[]; affected_pages: number[];
  affected_pages_reason: string; changed_locations?: { text: string; pages: number[] }[];
  reviewed_pages?: number[]; reviewed_by?: string;
};
export type DocumentReviewIdentity = { expected_revision: number; output_id: string; output_sha256: string };
export const getReportDocumentReview = (projectId: string, outputId: string, revision: number) =>
  requestJson<ReportDocumentReviewData>(base(projectId) + `/outputs/${encodeURIComponent(outputId)}/document-review?expected_revision=${revision}`);
export const confirmReportPhotoPlan = (projectId: string, request: DocumentReviewIdentity & {
  review_sha256: string; confirmed_by: string; assignments: ConfirmedPhotoAssignment[];
}) => requestJson<ReportAuthoringState>(base(projectId) + '/photos/plan', { method: 'POST', body: JSON.stringify(request) });
export const confirmReportRegions = (projectId: string, request: DocumentReviewIdentity & {
  review_sha256: string; confirmed_by: string;
  decisions: { region_id: string; region_sha256: string; source_id: string; locator: string; reason: string }[];
}) => requestJson<ReportAuthoringState>(base(projectId) + '/document-review/regions', { method: 'POST', body: JSON.stringify(request) });
export const createReportVisualPreview = (projectId: string, request: DocumentReviewIdentity) =>
  requestJson<ReportAuthoringState>(base(projectId) + '/visual-preview', { method: 'POST', body: JSON.stringify(request) });
export const reportVisualPreviewUrl = (projectId: string, outputId: string) => base(projectId) + `/outputs/${encodeURIComponent(outputId)}/visual-preview`;
export const confirmReportVisualPages = (projectId: string, request: DocumentReviewIdentity & {
  preview_sha256: string; pages: number[]; confirmed_by: string; notes: string;
}) => requestJson<ReportAuthoringState>(base(projectId) + '/visual-preview/review', { method: 'POST', body: JSON.stringify(request) });

export const adoptCurrentReportWorkingCopy = (projectId: string, request: {
  expected_revision: number; source_sha256: string; source_mode: string;
}) => requestJson<ReportAuthoringState>(base(projectId) + '/working-copy/adopt', { method: 'POST', body: JSON.stringify(request) });
export const updateWorkingCopyLlcr = (projectId: string, request: {
  expected_revision: number; expected_sha256: string; dataset_revision_id: string;
}) => requestJson<ReportAuthoringState>(base(projectId) + '/working-copy/llcr', { method: 'POST', body: JSON.stringify(request) });
export function updateWorkingCopyEquipment(projectId: string, request: { expected_revision: number; expected_sha256: string },
  input?: { file?: File; referencesText?: string }) {
  const body = new FormData();
  body.set('expected_revision', String(request.expected_revision)); body.set('expected_sha256', request.expected_sha256);
  if (input?.file) body.set('file', input.file);
  if (input?.referencesText) body.set('references_text', input.referencesText);
  return requestJson<ReportAuthoringState | { status: 'source_required'; project_id: string }>(base(projectId) + '/working-copy/equipment', { method: 'POST', body });
}

export type FactPreview = { output_sha256: string; preview_sha256: string; mapping_ids: string[];
  changes: { old: string; new: string; occurrences: number; parts: string[] }[] };
export const previewReportFacts = (projectId: string, outputId: string, mappingIds: string[], revision: number) =>
  requestJson<FactPreview>(base(projectId) + "/facts/preview", { method: "POST", body: JSON.stringify({
    output_id: outputId, mapping_ids: mappingIds, expected_revision: revision,
  }) });
export const applyReportFacts = (projectId: string, outputId: string, mappingIds: string[], revision: number, previewSha: string) =>
  requestJson<ReportAuthoringState>(base(projectId) + "/facts/apply", { method: "POST", body: JSON.stringify({
    output_id: outputId, mapping_ids: mappingIds, expected_revision: revision, preview_sha256: previewSha,
  }) });

export type ReportTable = { file_name: string; sheet_names: string[]; sheet_name: string; rows: (string | number | boolean | null)[][] };
export type ResultImportRequest = {
  expected_revision: number; source_id: string; kind: "temperature" | "cr" | "mechanical" | "mechanical_qualitative" | 'electrical' | 'resistance_stages' | 'external_reference' | 'linked_temperature';
  sheet_name: string; start_row: number; end_row: number; columns: Record<string, number>;
  sample_ids?: string[];
  unit: "mV" | "V" | "N"; quantity: "absolute" | "delta"; test_type: "mating" | "unmating" | "retention";
  measurement_kind: "peak" | "hold"; group_id: string; row_id: string; step_token: string;
  outcome: "pending" | "pass" | "fail" | "not_applicable"; acceptance_reason: string;
  temperature_selection?: { header_row: number; start_row: number; end_row: number; ambient_column: number;
    current_column: number; temperature_columns: number[]; thermocouples_per_sample: number; sample_count: number };
  zero_intercept: boolean; acknowledge_warnings: boolean; preview_sha256?: string;
};
export type ReportResult = {
  result_id?: string; kind: ResultImportRequest["kind"]; source_id: string; source_sha256: string;
  matrix_id: string; target: ReportMatrixStep; profile: ResultImportRequest; outcome: string; acceptance_reason: string;
  preview_sha256: string; data: { sheet_name: string; unit: string; quantity: string;
    force_field?: string; withdraw_magnitude?: boolean;
    raw_curves?: string[];
    tables?: { title: string; row_heading?: string; column_heading?: string; columns: string[];
      samples: string[]; results: string[][]; curves?: string[]; diagonal?: boolean }[];
    rows?: Record<string, string | number | boolean | null | Record<string, string>>[];
    missing?: boolean; selection_confirmed?: boolean;
    adoption?: ResultAdoption; excerpt?: string; frozen_chart_count?: number;
    summary?: { min: string; max: string; average: string; stdev: string | null };
    analysis?: { points: { source_row: number | null; current: number; rises: number[]; maximum: number; average: number }[] };
  };
};
export type ReportToolsPackage = {
  project_hint?: string;
  entries: { entry_id: string; label: string; kind: string; supported_for_report: boolean; reason: string;
    source_names: string[]; sample_count?: number | null; sample_ids?: string[] }[];
};
export type ToolsPackageImportRequest = Pick<ResultImportRequest,
  'expected_revision' | 'source_id' | 'kind' | 'group_id' | 'row_id' | 'step_token' | 'outcome' | 'acceptance_reason' | 'preview_sha256'> & {
  package_entry_id: string; sample_ids?: string[]; source_project_confirmed?: boolean;
};
export type SemanticRecord = { stage: string; cells: Record<string, string>; unit: string;
  measurement?: 'ir' | 'dwv'; quantity?: 'absolute' | 'delta' | 'delta_from_absolute';
  voltage_v?: string; duration_s?: string; condition_locator?: string };
export type SemanticResultImportRequest = Pick<ResultImportRequest,
  'expected_revision' | 'source_id' | 'kind' | 'group_id' | 'row_id' | 'step_token' | 'outcome' | 'acceptance_reason' | 'preview_sha256'> & {
  sheet_name: string; semantic_selection: { type: 'electrical' | 'resistance_stages'; records: SemanticRecord[]; selection_confirmed: boolean };
};
export type ResultAdoption = { report_identity: string; source_version: string; source_locator: string; adopted_scope: string;
  applicability_reason: string; adverse_observations: string; source_observations: string;
  confirmed: boolean; customer_reference_allowed: boolean };
export type RelatedResultImportRequest = Pick<ResultImportRequest,
  'expected_revision' | 'source_id' | 'kind' | 'group_id' | 'row_id' | 'step_token' | 'outcome' | 'acceptance_reason' | 'preview_sha256'> & {
  adoption: ResultAdoption; linked_region?: { start: number; end: number; freeze_external_charts: boolean };
};
export type ReportSourceBlock = { index: number; kind: string; text: string; tables: number; charts: number };
export const getReportSourceRegion = (projectId: string, sourceId: string) =>
  requestJson<ReportSourceBlock[]>(base(projectId) + `/sources/${encodeURIComponent(sourceId)}/region`);
export const getReportToolsPackage = (projectId: string, sourceId: string) =>
  requestJson<ReportToolsPackage>(base(projectId) + `/sources/${encodeURIComponent(sourceId)}/package`);
export const getReportSourceTable = (projectId: string, sourceId: string, sheetName = "") =>
  requestJson<ReportTable>(base(projectId) + `/sources/${encodeURIComponent(sourceId)}/table?sheet_name=${encodeURIComponent(sheetName)}`);
export const previewReportResult = (projectId: string, request: ResultImportRequest | ToolsPackageImportRequest | SemanticResultImportRequest | RelatedResultImportRequest) =>
  requestJson<ReportResult>(base(projectId) + "/results/preview", { method: "POST", body: JSON.stringify(request) });
export const confirmReportResult = (projectId: string, request: ResultImportRequest | ToolsPackageImportRequest | SemanticResultImportRequest | RelatedResultImportRequest) =>
  requestJson<ReportAuthoringState>(base(projectId) + "/results/confirm", { method: "POST", body: JSON.stringify(request) });

export type ResultTargets = { output_sha256: string; result_id: string;
  result_rows: { table_index: number; row_index: number; step: string; test_item: string }[];
  appendix_tables: { table_index: number; title: string; headers: string[] }[];
  evidence_blocks?: { block_index: number; kind: string; text: string; drawing_count: number; temperature_evidence: boolean; protected_other_step: boolean; owned_current_result: boolean }[];
  unreconciled_temperature_evidence?: boolean };
export const getReportResultTargets = (projectId: string, outputId: string, resultId: string, revision: number) =>
  requestJson<ResultTargets>(base(projectId) + `/outputs/${encodeURIComponent(outputId)}/result-targets/${encodeURIComponent(resultId)}?expected_revision=${revision}`);
export const applyReportResult = (projectId: string, request: { expected_revision: number; output_id: string; output_sha256: string;
  result_id: string; result_table: number; result_row: number; appendix_table: number | null; appendix_title: string;
  evidence_start?: number | null; evidence_end?: number | null; evidence_selection_confirmed?: boolean }) =>
  requestJson<ReportAuthoringState>(base(projectId) + '/results/apply', { method: 'POST', body: JSON.stringify(request) });

export type ReportPhotoSlot = { slot_id: string; caption: string; width_emu: number; height_emu: number;
  media_sha256: string | null; supported: boolean; reason: string | null; rotation: number; flip_horizontal: boolean; flip_vertical: boolean };
export const getReportPhotoSlots = (projectId: string, outputId: string, revision: number) =>
  requestJson<{ output_sha256: string; slots: ReportPhotoSlot[] }>(base(projectId) + `/outputs/${encodeURIComponent(outputId)}/photos?expected_revision=${revision}`);
export const getReportPhotoImage = (projectId: string, outputId: string, slotId: string) =>
  requestBlobResponse(base(projectId) + `/outputs/${encodeURIComponent(outputId)}/photos/${encodeURIComponent(slotId)}`);
export const applyReportPhotos = (projectId: string, request: { expected_revision: number; output_id: string; output_sha256: string;
  assignments: { slot_id: string; source_id: string; crop_mode: 'preserve' | 'centre_crop'; accept_slot_transform: boolean }[] }) =>
  requestJson<ReportAuthoringState>(base(projectId) + '/photos/apply', { method: 'POST', body: JSON.stringify(request) });

export type CustomerReportIssue = { code: string; location: string; message: string; sha256: string | null };
export type CustomerReportOutput = ReportAuthoringOutput & { audit?: { passed: boolean; issues: CustomerReportIssue[];
  sensitive_terms: string[]; forbidden_project_ids: string[]; reviewed_parts: Record<string, string>; disclosure_scope_confirmed: boolean; content_review_sha256?: string | null } };
export const generateCustomerReviewCopy = (projectId: string, request: { expected_revision: number; output_id: string;
  output_sha256: string; temperature_result_ids: string[] }) => requestJson<ReportAuthoringState>(base(projectId) + '/customer/generate', { method: 'POST', body: JSON.stringify(request) });
export const checkCustomerReviewCopy = (projectId: string, request: { expected_revision: number; output_id: string;
  output_sha256: string; sensitive_terms: string[]; forbidden_project_ids: string[]; reviewed_parts: Record<string, string>;
  disclosure_scope_confirmed: boolean; content_review_sha256?: string | null }) => requestJson<ReportAuthoringState>(base(projectId) + '/customer/check', { method: 'POST', body: JSON.stringify(request) });
export const downloadCustomerPart = (projectId: string, outputId: string, part: string) =>
  requestBlobResponse(base(projectId) + `/customer/${encodeURIComponent(outputId)}/part?part=${encodeURIComponent(part)}`);
