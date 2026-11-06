import { useEffect, useState, type ReactNode } from 'react';
import { getProject } from '../../api/client';
import { calculatePlanningFees, fetchLegacyPlanningRecovery, replacePlanningSession, type LegacyPlanningRecovery } from '../../api/toolsPlanning';
import { buildFeeEvaluationPreviewRows, hydrateFeeEvaluationPreviewEditsFromSavedDraft } from '../fee-evaluation/feeEvaluationPreviewModel';

export function LegacyPlanningBoundary({projectId,children,onTools,onIntake}: {projectId:string;children:ReactNode;onTools:()=>void;onIntake:()=>void}) {
  const [legacy,setLegacy]=useState<boolean|null>(null);
  const [recovery,setRecovery]=useState<LegacyPlanningRecovery|null>(null);
  const [error,setError]=useState('');
  const [busy,setBusy]=useState(false);
  useEffect(()=>{let active=true; setLegacy(null); setError(''); setRecovery(null);
    void getProject(projectId).then(project=>{if(active) setLegacy(Boolean(project.is_legacy_temporary));},reason=>{if(active)setError(String(reason.message??reason));});
    return ()=>{active=false;};
  },[projectId]);
  useEffect(()=>{if(!legacy)return; let active=true;
    void fetchLegacyPlanningRecovery(projectId).then(value=>{if(active)setRecovery(value);},reason=>{if(active)setError(String(reason.message??reason));});
    return ()=>{active=false;};
  },[legacy,projectId]);
  async function openTools() {
    if(!recovery?.seed.editor_draft || busy) return;
    if(!window.confirm('Copy this retained Matrix and matching fee edits into Tools? This replaces the current Tools session; the original temporary data stays unchanged.'))return;
    setBusy(true);setError('');
    try {
      const seed={...recovery.seed,project_id:'',active_confirmed_matrix_id:null,active_confirmed_revision:null,
        active_source_import_id:null,active_source_snapshot_id:null,editor_draft_id:'browser-session',source_status:'not_required' as const,
        source_unavailable_message:null,draft_status:'current' as const};
      const matrix=seed.editor_draft;
      let fee = null;
      if (recovery.fee_values) {
        const draft = await calculatePlanningFees(matrix);
        const hydrated = hydrateFeeEvaluationPreviewEditsFromSavedDraft(buildFeeEvaluationPreviewRows(draft), recovery.fee_values);
        fee = {matrix, signature:JSON.stringify(matrix), draft, edits:hydrated.edits, cost:hydrated.costPreviewValues};
      }
      replacePlanningSession(seed, fee);
      onTools();
    } catch(reason) {setError(reason instanceof Error?reason.message:'Unable to copy retained data.');}
    finally {setBusy(false);}
  }
  function download() {
    const url=URL.createObjectURL(new Blob([JSON.stringify(recovery,null,2)],{type:'application/json'}));
    const link=document.createElement('a');link.href=url;link.download=`Retained planning ${projectId}.json`;link.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  if(legacy===false)return <>{children}</>;
  if(legacy===null)return error?<p role="alert">{error}</p>:<p role="status">Loading…</p>;
  return <section className="panel" aria-label="Retained temporary materials">
    <h2>Retained temporary work</h2>
    <p>Your original materials and edits are retained. Matrix and Fee planning now live in Tools. To apply an LTR number, import the original email in New Project.</p>
    {error&&<p role="alert">{error}</p>}
    {recovery?.unmatched_fee_rows.length ? <div role="alert"><p>Some fee edits cannot be copied safely. They remain in the original data and downloadable recovery copy.</p><ul>{recovery.unmatched_fee_rows.map((item,index)=><li key={index}>{item}</li>)}</ul></div>:null}
    <button disabled={!recovery?.seed.editor_draft||busy} onClick={()=>void openTools()}>{busy?'Copying…':'Copy Matrix and fees to Tools'}</button>
    <button disabled={!recovery} onClick={download}>Download retained edits</button>
    <button onClick={onIntake}>New Project</button>
  </section>;
}
