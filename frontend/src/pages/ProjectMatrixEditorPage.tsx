import type { ReactElement } from "react";
import { LoadingState } from "../components/common/LoadingState";
import { useProjectWorkbenchModel } from "../features/project-workbench/useProjectWorkbenchModel";
import "../workbench.css";

type ProjectMatrixEditorPageProps = {
  projectId: string;
  onBackToWorkbench: () => void;
};

const GROUP_COLUMNS = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10", "G11", "G12"];
const GROUP_SECTIONS = [
  { label: "Electrical", span: 4 },
  { label: "Mechanical", span: 4 },
  { label: "Environmental", span: 4 }
];

const PLACEHOLDER_ROWS = [
  { item: "Examination of Product", section: "5.4", method: "EIA-364-18B", condition: "10x min magnification", requirement: "No detrimental condition" },
  { item: "LLCR", section: "6.1", method: "EIA-364-23E", condition: "20mV max, 100mA max", requirement: "Initial <= 0.40mO" },
  { item: "DWV", section: "6.3", method: "EIA-364-20F", condition: "3500V/AC, 1min", requirement: "No arcing or breakdown" },
  { item: "Insulation Resistance", section: "6.4", method: "EIA-364-21F", condition: "500V/DC, 2min", requirement: ">= 1000MO" },
  { item: "Durability", section: "7.2", method: "EIA-364-09D", condition: "100 cycles", requirement: "No damage" }
];

export function ProjectMatrixEditorPage({
  projectId,
  onBackToWorkbench
}: ProjectMatrixEditorPageProps): ReactElement {
  const model = useProjectWorkbenchModel(projectId);

  if (!model.project && !model.error) {
    return <LoadingState label="Loading matrix editor..." />;
  }

  return (
    <section className="workbench-page matrix-editor-shell">
      <section className="matrix-editor-header">
        <div className="matrix-editor-title-block">
          <h2>Matrix Editor</h2>
          <p>{model.project?.project_no ?? projectId} | Definition Studio (placeholder mode)</p>
        </div>
        <div className="matrix-editor-header-actions">
          <button className="matrix-editor-back-button" type="button" onClick={onBackToWorkbench}>Workbench</button>
          <button disabled type="button">Import Template</button>
          <button disabled type="button">Save Draft</button>
          <button disabled type="button">Validate</button>
          <button className="matrix-editor-primary-action" disabled type="button">Confirm Authority</button>
        </div>
      </section>

      <section className="matrix-editor-summary-strip" aria-label="Matrix summary">
        <article><span>Authority</span><strong>v{model.runtimeAuthoritySync.authorityVersion ?? "-"}</strong></article>
        <article><span>Candidate</span><strong>{model.runtimeAuthoritySync.candidateVersion ?? "-"}</strong></article>
        <article><span>Groups</span><strong>{GROUP_COLUMNS.length}</strong></article>
        <article><span>Rows</span><strong>{PLACEHOLDER_ROWS.length}</strong></article>
        <article><span>Projection Ref</span><strong>{model.runtimeAuthoritySync.projectionMatrixReference ?? "N/A"}</strong></article>
      </section>

      <nav className="matrix-editor-segment-tabs" aria-label="Matrix sections">
        <button className="is-active" type="button">Matrix Grid</button>
        <button disabled type="button">Group Setup</button>
        <button disabled type="button">Test Item Library</button>
        <button disabled type="button">Validation</button>
      </nav>

      <section className="matrix-editor-toolbar">
        <label>
          Matrix Version
          <select defaultValue="v1">
            <option value="v1">v1 (Placeholder)</option>
          </select>
        </label>
        <label>
          Group
          <select defaultValue="all">
            <option value="all">All groups</option>
          </select>
        </label>
        <label>
          Filter
          <input placeholder="Search test item..." type="text" />
        </label>
        <label>
          Section
          <select defaultValue="all">
            <option value="all">All sections</option>
          </select>
        </label>
      </section>

      <section className="matrix-editor-body">
        <div className="matrix-editor-main-table-wrap">
          <table className="matrix-editor-main-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Test Item</th>
                <th>Section</th>
                <th>Method</th>
                <th>Condition</th>
                <th>Requirement</th>
                {GROUP_SECTIONS.map((section) => (
                  <th className="matrix-editor-group-band" colSpan={section.span} key={section.label}>
                    {section.label}
                  </th>
                ))}
              </tr>
              <tr>
                <th className="matrix-editor-subhead">#</th>
                <th className="matrix-editor-subhead">Test Item</th>
                <th className="matrix-editor-subhead">Sec.</th>
                <th className="matrix-editor-subhead">Method</th>
                <th className="matrix-editor-subhead">Condition</th>
                <th className="matrix-editor-subhead">Requirement</th>
                {GROUP_COLUMNS.map((column) => (
                  <th className="matrix-editor-subhead" key={column}>{column}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {PLACEHOLDER_ROWS.map((row, rowIndex) => (
                <tr key={`${row.item}-${rowIndex}`}>
                  <td>{rowIndex + 1}</td>
                  <td>{row.item}</td>
                  <td>{row.section}</td>
                  <td>{row.method}</td>
                  <td>{row.condition}</td>
                  <td>{row.requirement}</td>
                  {GROUP_COLUMNS.map((column, groupIndex) => (
                    <td key={`${column}-${groupIndex}`}>
                      <span className="matrix-editor-cell-token">{(rowIndex + groupIndex) % 3 === 0 ? "1,3" : "-"}</span>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <aside className="matrix-editor-sidepanel">
          <section>
            <h3>Authority Status</h3>
            <p>Current authority is read-only for this placeholder screen.</p>
            <div className="matrix-editor-status-strip">
              <span>Plan</span>
              <span>Draft</span>
              <span>Review</span>
              <span>Authority</span>
            </div>
          </section>
          <section>
            <h4>Step Identity Preview</h4>
            <ul>
              <li>Project: {model.project?.project_no ?? "N/A"}</li>
              <li>Matrix Authority: {model.runtimeAuthoritySync.authorityVersion ?? "-"}</li>
              <li>Group: G3</li>
              <li>Sequence/Token: 2</li>
            </ul>
          </section>
          <section>
            <h4>Authority Sync</h4>
            <p>
              {model.runtimeAuthoritySync.hasUnconfirmedCandidate
                ? `Candidate v${model.runtimeAuthoritySync.candidateVersion ?? "-"} pending confirmation.`
                : "No pending candidate in current session."}
            </p>
            <p>Projection Ref: {model.runtimeAuthoritySync.projectionMatrixReference ?? "not loaded"}</p>
          </section>
          <section>
            <h4>Selected Definition (Placeholder)</h4>
            <p>Cell click, inline edit, and formula behavior are not implemented in this slice.</p>
          </section>
          <section>
            <h4>Runtime Mapping Notes</h4>
            <ul>
              <li>Projection consumes authority map only.</li>
              <li>UI markers do not mutate step identity.</li>
              <li>Selection state is UI projection only.</li>
            </ul>
          </section>
        </aside>
      </section>
    </section>
  );
}
