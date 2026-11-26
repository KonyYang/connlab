import { useState, type ReactNode } from "react";
import type { ReportAuthoringState } from "../../api/reportAuthoring";
import { runtimeLocalStorage } from "../../runtimeEnvironment";
import { ReportAuthoringPanel } from "./ReportAuthoringPanel";
import { ReportBatchPreparation } from "./ReportBatchPreparation";
import { ReportDocumentReview } from "./ReportDocumentReview";
import { ReportToolsPackageImport } from "./ReportToolsPackageImport";
import { ReportEvidenceResults } from "./ReportEvidenceResults";
import { ReportResultsImport } from "./ReportResultsImport";
import { ReportFactUpdates } from "./ReportFactUpdates";
import { ReportResultUpdate } from "./ReportResultUpdate";
import { ReportPhotoSlots } from "./ReportPhotoSlots";
import { ReportCustomerCopy } from "./ReportCustomerCopy";
import { ReportDelivery } from "./ReportDelivery";
import "./reportContentEditor.css";

const sections = {
  llcr: "LLCR results", equipment: "Equipment list", photos: "Photos", results: "Test results",
  facts: "Project information", sources: "Sources and decisions", batch: "Batch updates", review: "Document review",
};
type Section = keyof typeof sections;
function isSection(value: string | null): value is Section {
  return value !== null && Object.prototype.hasOwnProperty.call(sections, value);
}

type Props = {
  projectId: string; state: ReportAuthoringState; disabled: boolean; llcr: ReactNode; equipment: ReactNode;
  onChanged: (state: ReportAuthoringState) => void; beginOperation: () => (() => void) | null;
  fileActions: ReactNode; directCustomerAction: ReactNode;
};

export function ReportContentEditor({ projectId, state, disabled, beginOperation, onChanged, llcr, equipment, fileActions, directCustomerAction }: Props) {
  const output = state.outputs[state.outputs.length - 1];
  const originalName = state.sources.find(source => source.source_id === output.base_source_id)?.file_name;
  const storageKey = `report-section:${projectId}:${output.base_source_id}`;
  const [section, setSection] = useState<Section>(() => {
    try {
      const saved = runtimeLocalStorage.getItem(storageKey);
      return isSection(saved) ? saved : "llcr";
    } catch { return "llcr"; }
  });
  const [customer, setCustomer] = useState(false);
  function choose(value: string) {
    if (!isSection(value)) return;
    setSection(value);
    try { runtimeLocalStorage.setItem(storageKey, value); } catch { /* Browsing still works without local storage. */ }
  }
  const props = { projectId, state, disabled, beginOperation, onChanged };
  function content() {
    switch (section) {
      case "llcr": return llcr;
      case "equipment": return equipment;
      case "photos": return <ReportPhotoSlots {...props} />;
      case "facts": return <ReportFactUpdates {...props} />;
      case "sources": return <ReportAuthoringPanel projectId={projectId} sharedState={state} disabled={disabled} onOperationStart={beginOperation} onChanged={onChanged} />;
      case "batch": return <ReportBatchPreparation {...props} />;
      case "review": return <ReportDocumentReview {...props} />;
      case "results": return <>
        <ReportEvidenceResults {...props} />
        <details><summary>Import measurements</summary><ReportResultsImport {...props} /></details>
        <details><summary>Import Tools result package</summary><ReportToolsPackageImport {...props} /></details>
        <ReportResultUpdate {...props} />
      </>;
    }
  }
  return <section className="report-editor" aria-label="Selected report working copy">
    <header className="report-editor-file"><div className="report-editor-filename"><strong>{output.file_name}</strong>
      {originalName && originalName !== output.file_name && <small>From {originalName}</small>}</div>{fileActions}</header>
    {output.issues.length > 0 && <details className="report-editor-notes"><summary>Review notes ({output.issues.length})</summary>
      <ul>{output.issues.map((issue, i) => <li key={i}>{issue}</li>)}</ul></details>}
    <nav className="report-editor-tabs" aria-label="Report view">
      <button type="button" aria-pressed={!customer} disabled={disabled} onClick={() => setCustomer(false)}>Report content</button>
      <button type="button" aria-pressed={customer} disabled={disabled} onClick={() => setCustomer(true)}>Customer copy</button>
    </nav>
    {customer ? <div className="report-editor-detail"><ReportCustomerCopy {...props} />
      {directCustomerAction}
      {Boolean(state.customer_outputs?.length) && <ReportDelivery {...props} />}</div>
      : <div className="report-editor-columns">
        <nav className="report-editor-list" aria-label="Report sections">
          {Object.entries(sections).map(([id, label]) => <button key={id} type="button" disabled={disabled}
            aria-current={section === id ? "true" : undefined} onClick={() => choose(id)}>{label}</button>)}
        </nav>
        <label className="report-editor-picker">Report section<select aria-label="Report section" value={section} disabled={disabled} onChange={e => choose(e.target.value)}>
          {Object.entries(sections).map(([id, label]) => <option key={id} value={id}>{label}</option>)}
        </select></label>
        <section className="report-editor-detail" aria-label={sections[section]}>{content()}</section>
      </div>}
  </section>;
}
