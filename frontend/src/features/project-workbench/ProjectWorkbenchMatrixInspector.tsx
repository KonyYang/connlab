import type { ReactElement } from "react";
import { useMemo, useState } from "react";
import type { ProjectTestPlanDraftGroup } from "../../api/client";
import { addStep, removeStep, updateStepField } from "./projectWorkbenchMatrixHelpers";

type ProjectWorkbenchMatrixInspectorProps = {
  editableGroups: ProjectTestPlanDraftGroup[];
  validating: boolean;
  saving: boolean;
  confirming: boolean;
  hasBlockers: boolean;
  onEditableGroupsChange: (groups: ProjectTestPlanDraftGroup[]) => void;
  onValidateDraft: () => Promise<void>;
  onSaveDraft: () => Promise<void>;
  onConfirmDraft: () => Promise<void>;
};

export function ProjectWorkbenchMatrixInspector({
  editableGroups,
  validating,
  saving,
  confirming,
  hasBlockers,
  onEditableGroupsChange,
  onValidateDraft,
  onSaveDraft,
  onConfirmDraft
}: ProjectWorkbenchMatrixInspectorProps): ReactElement {
  const [activeGroupIndex, setActiveGroupIndex] = useState(0);
  const activeGroup = editableGroups[activeGroupIndex] ?? null;
  const busy = saving || validating || confirming;

  const groupLabel = useMemo(() => {
    if (!activeGroup) {
      return null;
    }
    return activeGroup.group_label ?? `Group ${activeGroupIndex + 1}`;
  }, [activeGroup, activeGroupIndex]);

  return (
    <div className="matrix-edit-surface">
      <aside className="matrix-group-nav">
        <h5>Group detail</h5>
        <ul>
          {editableGroups.map((group, index) => (
            <li key={`${group.group_key ?? "group"}-${index}`}>
              <button
                className={index === activeGroupIndex ? "matrix-group-tab matrix-group-tab-active" : "matrix-group-tab"}
                onClick={() => setActiveGroupIndex(index)}
                type="button"
              >
                {group.group_label ?? `Group ${index + 1}`}
              </button>
            </li>
          ))}
        </ul>
      </aside>
      <div className="matrix-group-editor">
        {!activeGroup ? <p className="fine-print">No editable group is available.</p> : null}
        {activeGroup ? (
          <>
            <header>
              <h5>{groupLabel}</h5>
              <div className="action-row">
                <button disabled={busy} onClick={() => void onValidateDraft()} type="button">
                  {validating ? "Validating..." : "Validate"}
                </button>
                <button disabled={busy} onClick={() => void onSaveDraft()} type="button">
                  {saving ? "Saving..." : "Save draft"}
                </button>
                <button disabled={busy || hasBlockers} onClick={() => void onConfirmDraft()} type="button">
                  {confirming ? "Confirming..." : "Confirm Matrix"}
                </button>
              </div>
            </header>
            <div className="matrix-group-step-list">
              {(activeGroup.steps ?? []).map((step, stepIndex) => (
                <article className="matrix-step-editor" key={`${step.sequence ?? stepIndex}-${stepIndex}`}>
                  <label>
                    Step token
                    <input
                      onChange={(event) =>
                        onEditableGroupsChange(
                          updateStepField(
                            editableGroups,
                            activeGroupIndex,
                            stepIndex,
                            "raw_token",
                            event.target.value
                          )
                        )
                      }
                      type="text"
                      value={step.raw_token ?? (typeof step.sequence === "number" ? `${step.sequence}` : "")}
                    />
                  </label>
                  <label>
                    Test item
                    <input
                      onChange={(event) =>
                        onEditableGroupsChange(
                          updateStepField(
                            editableGroups,
                            activeGroupIndex,
                            stepIndex,
                            "test_item",
                            event.target.value
                          )
                        )
                      }
                      type="text"
                      value={step.test_item ?? ""}
                    />
                  </label>
                  <label>
                    Method
                    <input
                      onChange={(event) =>
                        onEditableGroupsChange(
                          updateStepField(
                            editableGroups,
                            activeGroupIndex,
                            stepIndex,
                            "method_summary",
                            event.target.value
                          )
                        )
                      }
                      type="text"
                      value={step.method_summary ?? ""}
                    />
                  </label>
                  <label>
                    Requirement
                    <input
                      onChange={(event) =>
                        onEditableGroupsChange(
                          updateStepField(
                            editableGroups,
                            activeGroupIndex,
                            stepIndex,
                            "judgement_criteria",
                            event.target.value
                          )
                        )
                      }
                      type="text"
                      value={step.judgement_criteria ?? ""}
                    />
                  </label>
                  <label>
                    Condition
                    <input
                      onChange={(event) =>
                        onEditableGroupsChange(
                          updateStepField(
                            editableGroups,
                            activeGroupIndex,
                            stepIndex,
                            "condition_summary",
                            event.target.value
                          )
                        )
                      }
                      type="text"
                      value={step.condition_summary ?? ""}
                    />
                  </label>
                  <button
                    className="secondary-button"
                    disabled={busy}
                    onClick={() => onEditableGroupsChange(removeStep(editableGroups, activeGroupIndex, stepIndex))}
                    type="button"
                  >
                    Remove step
                  </button>
                </article>
              ))}
            </div>
            <button
              className="secondary-button"
              disabled={busy}
              onClick={() => onEditableGroupsChange(addStep(editableGroups, activeGroupIndex))}
              type="button"
            >
              Add step
            </button>
          </>
        ) : null}
      </div>
    </div>
  );
}
