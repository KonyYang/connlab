import { requestJson } from './client';
import type { FactPreview, ReportAuthoringState, ReportMapping, ReportMatrixStep, ReportSourceRole } from './reportAuthoring';

export type ReportInventoryItem = {
  relative_path: string; name: string; size_bytes: number | null; modified_ns: string | null;
  file_token: string | null; suggested_role: ReportSourceRole | null;
  status: 'candidate' | 'excluded' | 'unsupported' | 'blocked'; reason: string; duplicate_name?: boolean;
};
export type ReportInventory = {
  available: boolean; reason: string; root_token: string | null; items: ReportInventoryItem[]; warnings: string[];
};
export type ReportCoverageStatus = 'ready' | 'missing' | 'needs_review' | 'not_applicable';
export type ReportLlcrDataset = {
  dataset_id: string; revision: number; source_file_name: string; source_sha256: string;
  entries: { entry_id: string; group_id: string; row_id: string; group_label: string; step_token: string;
    stage: string; stage_label: string; outcome: string; summary: { min: string; max: string; average: string; unit: string } }[];
};
export type ReportCoverage = {
  matrix_id: string; has_confirmed_matrix: boolean; complete: boolean;
  rows: (ReportMatrixStep & { status: ReportCoverageStatus; reasons: string[]; result_ids: string[];
    usable_result_ids: string[]; applied_result_ids: string[] })[];
  pending_mappings: ReportMapping[]; counts: Partial<Record<ReportCoverageStatus, number>>;
  llcr_dataset?: ReportLlcrDataset | null; llcr_unavailable_reason?: string;
};
export type ReportAssemblyResult = {
  result_id: string; result_table?: number; result_row?: number; appendix_table?: number | null; appendix_title?: string;
  evidence_start?: number | null; evidence_end?: number | null; evidence_selection_confirmed?: boolean;
};
export type ReportAssemblyPhoto = {
  slot_id: string; source_id: string; crop_mode: 'preserve' | 'centre_crop'; accept_slot_transform: boolean;
};
export type ReportAssemblyRequest = {
  expected_revision: number; output_id: string; output_sha256: string;
  mapping_ids: string[]; results: ReportAssemblyResult[]; assignments: ReportAssemblyPhoto[];
  llcr_dataset_id?: string | null;
  photo_plan_id?: string;
  renumber_figures?: boolean;
};
export type ReportAssemblyLlcrPreview = {
  dataset_id: string; revision: number; source_sha256: string; dataset_sha256: string; changed: boolean;
  rows: { result_id: string; group_label: string; step_token: string; table_index: number; row_index: number;
    requirement: string; current_result: string; current_comment: string; new_result: string; new_comment: string; changed: boolean }[];
  appendix: { identifier: 'A'; action: 'create' | 'update' | 'reuse'; heading_block_index: number | null;
    table_index: number | null; summary_rows: number; sha256: string | null };
};
export type ReportAssemblyPlan = {
  plan_id: string; preview_sha256: string; status: 'prepared' | 'completed'; can_apply: boolean; prepared_revision?: number;
  base_output_id: string; output_sha256: string; applied_output_id?: string;
  request: Omit<ReportAssemblyRequest, 'expected_revision'> & { expected_revision?: number };
  changes: { kind: string; label: string; result_id?: string; slot_id?: string }[]; issues: string[]; omitted: string[];
  document_plan?: { facts: FactPreview['changes']; results: { result_id: string; target: Omit<ReportAssemblyResult, 'result_id'> | null;
    current_result?: string; current_comment?: string; new_result?: string; new_comment?: string }[];
    llcr?: ReportAssemblyLlcrPreview | null };
};
export type ReportBatchState = ReportAuthoringState;
const base = (projectId: string) => `/api/projects/${encodeURIComponent(projectId)}/report-workspace/authoring`;
export const getReportInventory = (projectId: string) => requestJson<ReportInventory>(base(projectId) + '/inventory');
export const getReportCoverage = (projectId: string) => requestJson<ReportCoverage>(base(projectId) + '/coverage');
export const retainReportInventory = (projectId: string, request: {
  expected_revision: number; root_token: string;
  items: { relative_path: string; file_token: string; role: ReportSourceRole }[];
}) => requestJson<ReportBatchState>(base(projectId) + '/inventory/retain', { method: 'POST', body: JSON.stringify(request) });
export const previewReportAssembly = (projectId: string, request: ReportAssemblyRequest) =>
  requestJson<ReportBatchState>(base(projectId) + '/assembly/preview', { method: 'POST', body: JSON.stringify(request) });
export const applyReportAssembly = (projectId: string, request: {
  expected_revision: number; plan_id: string; preview_sha256: string;
}) => requestJson<ReportBatchState>(base(projectId) + '/assembly/apply', { method: 'POST', body: JSON.stringify(request) });
