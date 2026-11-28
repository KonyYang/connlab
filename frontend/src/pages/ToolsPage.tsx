import {useState, type ReactElement} from "react";
import {CustomerReportDownload} from "../features/report-workspace/CustomerReportDownload";
import { EquipmentListTool } from "../features/tools/EquipmentListTool";
import { MechanicalSummaryTool } from "../features/tools/MechanicalSummaryTool";
import { EncryptionTool } from "../features/tools/EncryptionTool";
import { ToolsFeedbackTarget } from "../features/tools/ToolsFeedback";
import "../tools.css";
import { MatrixEditorWorkspace } from '../features/matrix-editor/MatrixEditorWorkspace';
import { ToolsFeeWorkspace } from '../features/tools/ToolsFeeWorkspace';
import { clearPlanningSession } from '../api/toolsPlanning';

export function ToolsPage({
  onOpenTemperatureRise = () => { window.location.assign('/tools/temperature-rise'); },
}: { onOpenTemperatureRise?: () => void } = {}): ReactElement {
  const [planning, setPlanning] = useState<'matrix' | 'fee' | null>(() => new URLSearchParams(window.location.search).has('planning') ? 'matrix' : null);
  const [planningKey,setPlanningKey] = useState(0);
  const [feedbackTarget, setFeedbackTarget] = useState<HTMLDivElement | null>(null);
  if (planning === 'matrix') return <MatrixEditorWorkspace key={planningKey} standalone projectId="" onBackToWorkbench={()=>setPlanning(null)} onEvaluateFees={()=>setPlanning('fee')} onNewPlanningMatrix={() => {
    if (window.confirm('Clear this Tools Matrix and its fee estimate? Download any files you want to retain first.')) {
      clearPlanningSession(); setPlanningKey(value=>value+1);
    }
  }} />;
  if (planning === 'fee') return <ToolsFeeWorkspace onBack={()=>setPlanning('matrix')} />;
  return (
    <ToolsFeedbackTarget value={feedbackTarget}><section className="tools-page" aria-label="Tools">
      <div className="tools-grid" role="group" aria-label="Tool actions">
        <article className="tools-action-group" aria-label="Matrix and Fee planning"><button type="button" className="primary-action tools-picker-action" onClick={()=>setPlanning('matrix')}>Matrix and Fee planning</button></article>
        <EquipmentListTool />
        <MechanicalSummaryTool />
        <article className="tools-action-group" aria-label="Temperature Rise">
          <button className="primary-action tools-picker-action" type="button" title="Open the temperature rise and derating workspace." onClick={onOpenTemperatureRise}>Drawing T-rise</button>
        </article>
        <article className="tools-action-group" aria-label="Internal Report → Customer Report">
          <CustomerReportDownload tools />
        </article>
        <EncryptionTool />
      </div>
      <div className="tools-feedback-stack" ref={setFeedbackTarget} />
    </section></ToolsFeedbackTarget>
  );
}
