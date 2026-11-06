import { useEffect, useMemo, useRef, useState } from 'react';
import { type FeeEvaluationDraft } from '../../api/client';
import { loadPlanningSeed, calculatePlanningFees, exportPlanningFees, inspectPlanningFeeForm } from '../../api/toolsPlanning';
import { FeeEvaluationPreviewTable, type FeeEvaluationCostPreviewValues } from '../fee-evaluation/FeeEvaluationPreviewTable';
import { FeeFormImportControl } from '../fee-evaluation/FeeFormImportControl';
import { applyFeeEvaluationPreviewEdits, buildFeeEvaluationPreviewRows, buildFeeEvaluationPreviewTotals,
  buildFeeEvaluationPreviewScopeTotal, filterFeeEvaluationPreviewRowsForScope,
  buildFeeEvaluationPreviewGrandCost, buildFeeEvaluationLabManpowerCost, buildFeeEvaluationPreviewWorkingHours,
  buildFeeEvaluationCostRisk, buildFeeEvaluationEditedExportPayload, type FeeEvaluationPreviewEditState } from '../fee-evaluation/feeEvaluationPreviewModel';

const KEY = 'connlab:tools-fees:v1';
const initialCost: FeeEvaluationCostPreviewValues = {conditionConfirmationSpendTime:'0',externalCost:'0',externalCostNote:'',labManpowerHourlyRate:'200'};
type SavedFee = {matrix: unknown; signature: string; draft: FeeEvaluationDraft; edits: FeeEvaluationPreviewEditState; cost: FeeEvaluationCostPreviewValues};

export function ToolsFeeWorkspace({onBack}: {onBack: () => void}) {
  const calculation = useRef(0);
  const [saved, setSaved] = useState<SavedFee | null>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [group, setGroup] = useState('all');
  const [matrix, setMatrix] = useState<unknown>(null);
  const signature = JSON.stringify(matrix);
  useEffect(() => {
    try {
      const seed = loadPlanningSeed();
      const current = seed.editor_draft;
      if (!current) throw new Error('Create or import a Matrix in Tools first.');
      setMatrix(current);
      const raw = sessionStorage.getItem(KEY);
      if (raw) setSaved(JSON.parse(raw) as SavedFee);
      else void calculate(current);
    } catch (failure) { setError(message(failure)); }
    return () => { calculation.current += 1; };
  }, []);
  async function calculate(current: unknown) {
    const generation = ++calculation.current;
    setBusy(true); setError('');
    try {
      const draft = await calculatePlanningFees(current);
      if (generation !== calculation.current) return;
      update({matrix:current, signature:JSON.stringify(current),draft,edits:{},cost:initialCost});
    } catch (failure) { if (generation === calculation.current) setError(message(failure)); }
    finally { if (generation === calculation.current) setBusy(false); }
  }
  function update(next: SavedFee) {
    // Keep the visible edits even if browser storage is full, and report the failure.
    setSaved(next);
    try {sessionStorage.setItem(KEY, JSON.stringify(next)); setError('');}
    catch {setError('The browser could not retain this estimate. Download the Fee Form before leaving.');}
  }
  const rows = useMemo(() => saved ? applyFeeEvaluationPreviewEdits(buildFeeEvaluationPreviewRows(saved.draft),saved.edits) : [], [saved]);
  const hours = buildFeeEvaluationPreviewWorkingHours(rows, saved?.cost.conditionConfirmationSpendTime ?? '0');
  const manpower = buildFeeEvaluationLabManpowerCost(hours,saved?.cost.labManpowerHourlyRate ?? '200');
  const grand = buildFeeEvaluationPreviewGrandCost(rows,saved?.cost.externalCost ?? '0');
  async function download() {
    if (!saved) return;
    setExporting(true); setError('');
    try {
      const result = await exportPlanningFees(saved.matrix,buildFeeEvaluationEditedExportPayload(rows,saved.cost));
      const url = URL.createObjectURL(result.blob); const a=document.createElement('a');
      a.href=url; a.download=result.fileName ?? 'Planning Fee Form.xlsx'; a.click();
      setTimeout(() => URL.revokeObjectURL(url),1000);
    } catch (failure) {setError(message(failure));}
    finally {setExporting(false);}
  }
  return <section className="fee-evaluation-page" aria-label="Tools Fee Evaluation">
    <header><h2>Fee Evaluation</h2><button onClick={onBack}>Back to Matrix</button></header>
    <p>Planning estimate only. Download the Fee Form to retain a file copy.</p>
    {error && <p role="alert">{error}</p>}
    {busy && <p role="status">Calculating fees…</p>}
    {saved && signature !== saved.signature && <div role="status">
      <p>The Matrix has changed. This estimate still contains the previous Matrix and your pricing edits.</p>
      <button disabled={busy} onClick={() => {if (window.confirm('Recalculate from the current Matrix? This replaces the current estimate and its manual pricing edits. Download it first if needed.')) void calculate(matrix);}}>Recalculate from Matrix</button>
    </div>}
    {saved && <FeeEvaluationPreviewTable
      identityLine="Tools estimate" costPreviewValues={saved.cost} costRisk={buildFeeEvaluationCostRisk({grandCost:grand,labManpowerCost:manpower})}
      confirmFeeActionState={{kind:'idle'}} labManpowerCostLabel={manpower} groupFilter={group}
      downloadState={exporting ? {kind:'running'} : {kind:'idle'}} feeFormButtonLabel="Download Draft Fee Form"
      draftPreviewNotice={null} onCostPreviewChange={(field,value) => update({...saved,cost:{...saved.cost,[field]:value}})}
      onGenerateFeeFile={() => void download()} onGroupFilterChange={setGroup}
      onRowEditChange={(id,field,value) => update({...saved,edits:{...saved.edits,[id]:{...saved.edits[id],[field]:value}}})}
      saveState={{kind:'idle',message:null}} scopeFeeLabel={buildFeeEvaluationPreviewScopeTotal(rows,group)}
      groupOptions={[...new Set(rows.filter(row=>row.groupLabel).map(row=>row.groupLabel))]}
      rows={filterFeeEvaluationPreviewRowsForScope(rows,group)}
      totals={{...buildFeeEvaluationPreviewTotals(saved.draft,''),workingHours:hours,labManpowerCost:manpower,externalCost:saved.cost.externalCost,grandCost:grand,testFeeTotal:buildFeeEvaluationPreviewScopeTotal(rows,'all')}}
      importControl={<FeeFormImportControl projectId="" planning rows={rows} disabled={busy || exporting}
        inspectFile={inspectPlanningFeeForm}
        onApply={changes => {const edits={...saved.edits}; for(const change of changes) edits[change.row.lineId]={...edits[change.row.lineId],...change.values}; update({...saved,edits});}} />}
    />}
  </section>;
}
function message(value: unknown) {return value instanceof Error ? value.message : 'Unable to prepare the estimate.';}
