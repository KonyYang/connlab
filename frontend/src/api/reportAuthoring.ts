import { requestJson, requestBlobResponse } from "./client";

export type ReportSourceRole = "original" | "layout_reference" | "specification" | "temperature" | "cr" | "mechanical" | "photo" | "evidence";
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
};
export type ReportAuthoringOutput = {
  output_id: string; file_name: string; status: string; operation: string; issues: string[];
  download_url: string; base_source_id: string;
  artifact?: { sha256: string };
  parent_output_id?: string;
  evidence?: { result_id?: string };
};
export type ReportMatrixStep = { group_id: string; row_id: string; group_label: string; test_item: string; step_token: string };
export type ReportAuthoringState = {
  project_id: string; revision: number; sources: ReportSource[]; mappings: ReportMapping[];
  base_source_id: string | null; outputs: ReportAuthoringOutput[];
  context: { dl_number: string; matrix_id: string; steps: ReportMatrixStep[] };
  results?: ReportResult[];
  customer_outputs?: CustomerReportOutput[];
  applied_result_ids?: string[];
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
  expected_revision: number; source_id: string; kind: "temperature" | "cr" | "mechanical";
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
    rows?: Record<string, string | number | Record<string, string>>[];
    summary?: { min: string; max: string; average: string; stdev: string | null };
    analysis?: { points: { source_row: number | null; current: number; rises: number[]; maximum: number; average: number }[] };
  };
};
export const getReportSourceTable = (projectId: string, sourceId: string, sheetName = "") =>
  requestJson<ReportTable>(base(projectId) + `/sources/${encodeURIComponent(sourceId)}/table?sheet_name=${encodeURIComponent(sheetName)}`);
export const previewReportResult = (projectId: string, request: ResultImportRequest) =>
  requestJson<ReportResult>(base(projectId) + "/results/preview", { method: "POST", body: JSON.stringify(request) });
export const confirmReportResult = (projectId: string, request: ResultImportRequest) =>
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
