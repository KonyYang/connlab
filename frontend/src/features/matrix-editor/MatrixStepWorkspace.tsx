import type { ReactElement } from "react";
import { MatrixAutoGrowTextarea } from "./MatrixAutoGrowTextarea";
import type { StepPreviewRow } from "./matrixStepWorkspaceModel";

export type MatrixStepWorkspaceView = {
  groupName: string | null;
  itemSectionNotes: string[];
  rows: StepPreviewRow[];
  sampleNotes: string[];
  sampleValue: string;
  stepNotes: string[];
};

type MatrixStepWorkspaceProps = {
  onChangeSample: (value: string) => void;
  onChangeStep: (
    rowKey: string,
    field: "requirement" | "description",
    value: string,
  ) => void;
  readOnly: boolean;
  view: MatrixStepWorkspaceView;
};

export function MatrixStepWorkspace({
  onChangeSample,
  onChangeStep,
  readOnly,
  view,
}: MatrixStepWorkspaceProps): ReactElement {
  return (
    <aside className="matrix-editor-step-workspace" aria-label="Group Step Workspace">
      <header className="matrix-editor-step-header">
        <h3 className="matrix-editor-step-header-text">
          {`Group ${view.groupName ?? "-"}: ${view.rows.length} steps`}
        </h3>
      </header>
      {view.groupName === null ? (
        <div className="matrix-editor-step-empty">Select a group header to preview steps.</div>
      ) : view.rows.length === 0 ? (
        <div className="matrix-editor-step-empty">No steps in this group.</div>
      ) : (
        <>
          <table className="matrix-editor-step-output-table">
            <thead>
              <tr>
                <th>Step</th>
                <th>Requirement</th>
                <th>Step Description</th>
              </tr>
            </thead>
            <tbody>
              {view.rows.map((row) => (
                <tr key={row.key}>
                  <td>{row.stepNo}</td>
                  <td>
                    <MatrixAutoGrowTextarea
                      ariaLabel={`Step ${row.stepNo} requirement`}
                      className="matrix-editor-step-output-textarea"
                      disabled={readOnly}
                      value={row.requirementValue}
                      onChange={(value) => onChangeStep(row.key, "requirement", value)}
                    />
                  </td>
                  <td>
                    <MatrixAutoGrowTextarea
                      ariaLabel={`Step ${row.stepNo} description`}
                      className="matrix-editor-step-output-textarea"
                      disabled={readOnly}
                      value={row.descriptionValue}
                      onChange={(value) => onChangeStep(row.key, "description", value)}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {view.stepNotes.length > 0 ? (
            <section className="matrix-editor-notes-card matrix-editor-notes-card-step">
              <h4>Step Notes</h4>
              {view.stepNotes.map((note, index) => (
                <p key={`${note}-${index}`}>{note}</p>
              ))}
            </section>
          ) : null}
          {view.itemSectionNotes.length > 0 ? (
            <section className="matrix-editor-notes-card matrix-editor-notes-card-item-section">
              <h4>Item/Section Notes</h4>
              {view.itemSectionNotes.map((note, index) => (
                <p key={`${note}-${index}`}>{note}</p>
              ))}
            </section>
          ) : null}
          <section className="matrix-editor-notes-card matrix-editor-notes-card-samples">
            <div className="matrix-editor-samples-inline">
              <h4>Samples</h4>
              <input
                className="matrix-editor-inline-input matrix-editor-samples-inline-input"
                disabled={readOnly}
                value={view.sampleValue}
                onChange={(event) => onChangeSample(event.target.value)}
              />
            </div>
            {view.sampleNotes.length > 0 ? (
              <>
                <h5>Notes</h5>
                {view.sampleNotes.map((note, index) => (
                  <p key={`${note}-${index}`}>{note}</p>
                ))}
              </>
            ) : null}
          </section>
        </>
      )}
    </aside>
  );
}
