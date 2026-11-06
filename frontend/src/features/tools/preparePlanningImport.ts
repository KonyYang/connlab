import { preparePlanningImport, loadPlanningSeed, savePlanningSeed } from '../../api/toolsPlanning';
import { type MatrixPreviewResponse, type MatrixEditorSessionSeed } from '../../api/client';
import { buildSessionDraftFromProjectMatrixDraft } from '../matrix-editor/matrixEditorDraftModel';

export async function importPlanningMatrix(preview: MatrixPreviewResponse) {
  const result = await preparePlanningImport(preview);
  const draft = result.project_matrix_draft;
  savePlanningSeed({...loadPlanningSeed(), ...draft.record, project_id:'',
    editor_draft:buildSessionDraftFromProjectMatrixDraft(draft), source_preview_payload:preview,
    editor_source_import_id:result.source_import_id, editor_source_snapshot_id:result.source_snapshot_id} as MatrixEditorSessionSeed);
  return result;
}
