import { requestJson, requestBlobResponse, type MatrixEditorSessionSeed, type MatrixEditorSessionDraftSaveRequest,
  type MatrixEditorSessionDraftSaveResponse, type MatrixPreviewResponse, type MatrixImportCommitResponse,
  type FeeEvaluationDraft, type FeeFormImportRow, type FeeEvaluationEditedFileExportRequest, type MatrixMethodVersionSuggestionResponse, type MatrixEditorLiveXlsxExportRequest, type MatrixEditorLiveXlsxPublicationPreview } from './client';
const KEY = 'connlab:tools-planning:v1';
const post = (body: unknown): RequestInit => ({method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
export function loadPlanningSeed(): MatrixEditorSessionSeed {
  const raw=sessionStorage.getItem(KEY);
  if(raw) return JSON.parse(raw) as MatrixEditorSessionSeed;
  return {project_id:'', active_confirmed_matrix_id:null, active_confirmed_revision:null,active_source_import_id:null,
    active_source_snapshot_id:null,editor_draft:null,source_preview_payload:null,source_status:'not_required',source_unavailable_message:null,
    draft_status:'missing',editor_draft_id:null,saved_payload_signature:null} as MatrixEditorSessionSeed;
}
export function savePlanningSeed(seed: MatrixEditorSessionSeed) {sessionStorage.setItem(KEY,JSON.stringify(seed));}
export async function savePlanningDraft(_id: string, value: MatrixEditorSessionDraftSaveRequest): Promise<MatrixEditorSessionDraftSaveResponse> {
  const seed=loadPlanningSeed();
  const signature=JSON.stringify(value);
  savePlanningSeed({...seed,...value,editor_draft:value,editor_draft_id:'browser-session',saved_payload_signature:signature,draft_status:'current'} as MatrixEditorSessionSeed);
  return {editor_draft_id:'browser-session',saved_payload_signature:signature,active_confirmed_matrix_id:null,active_confirmed_revision:null,
    source_import_id:value.source_import_id,source_snapshot_id:value.source_snapshot_id} as MatrixEditorSessionDraftSaveResponse;
}
export const preparePlanningImport = (preview: MatrixPreviewResponse) =>
  requestJson<MatrixImportCommitResponse>('/api/tools/matrix/prepare',post({preview_payload:preview}));
export const planningExportApis = {
  download: (_: string, value: MatrixEditorLiveXlsxExportRequest) => requestBlobResponse('/api/tools/matrix/export',post(value)),
  preview: async (): Promise<MatrixEditorLiveXlsxPublicationPreview> => ({mode:'download',status:'ready',authority_status:'unconfirmed',existing_file:false,existing_modified_at:null,blockers:[],preview_token:'browser-export'}),
  publish: async () => {throw new Error('Tools exports download files only.');},
};
export function clearPlanningSession() {sessionStorage.removeItem(KEY);sessionStorage.removeItem('connlab:tools-fees:v1');}

export const suggestPlanningMethods = (_: string, value: {rows: {row_id:string;method:string}[]}) =>
  requestJson<MatrixMethodVersionSuggestionResponse>('/api/tools/matrix/method-versions',post(value));

export const calculatePlanningFees = (matrix: unknown) => requestJson<FeeEvaluationDraft>('/api/tools/matrix/fees',post(matrix));
export const exportPlanningFees = (matrix: unknown, values: FeeEvaluationEditedFileExportRequest) =>
  requestBlobResponse('/api/tools/matrix/fees/export',post({matrix,values}));
export async function inspectPlanningFeeForm(_: string, file: File) {
  const form=new FormData(); form.append('file',file);
  return requestJson<{rows:FeeFormImportRow[]}>('/api/tools/matrix/fees/import',{method:'POST',body:form});
}
export type LegacyPlanningRecovery = {seed:MatrixEditorSessionSeed;fee_values:FeeEvaluationEditedFileExportRequest|null;
  retained_fee_values:FeeEvaluationEditedFileExportRequest|null;unmatched_fee_rows:string[]};
export const fetchLegacyPlanningRecovery = (id:string) => requestJson<LegacyPlanningRecovery>(`/api/tools/matrix/legacy/${encodeURIComponent(id)}`);
export function replacePlanningSession(seed:MatrixEditorSessionSeed, fee:unknown) {
  const matrixBefore=sessionStorage.getItem(KEY), feeBefore=sessionStorage.getItem('connlab:tools-fees:v1');
  try {
    savePlanningSeed(seed);
    if(fee) sessionStorage.setItem('connlab:tools-fees:v1',JSON.stringify(fee)); else sessionStorage.removeItem('connlab:tools-fees:v1');
  } catch(error) {
    if(matrixBefore===null) sessionStorage.removeItem(KEY); else sessionStorage.setItem(KEY,matrixBefore);
    if(feeBefore===null) sessionStorage.removeItem('connlab:tools-fees:v1'); else sessionStorage.setItem('connlab:tools-fees:v1',feeBefore);
    throw error;
  }
}
