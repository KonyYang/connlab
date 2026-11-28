import type { ReactElement } from "react";

import type { NewProjectSetupConfirmationValues } from "./NewProjectSetupConfirmationPanel";
import type { RequiredAction } from "./newProjectRequiredState";

type NewProjectCompletionDockProps = {
  completionDisabled: boolean;
  completionError?: string | null;
  completionLoading: boolean;
  requiredActions: RequiredAction[];
  disabled: boolean;
  missingKeys: Set<string>;
  values: NewProjectSetupConfirmationValues;
  onChange: (values: NewProjectSetupConfirmationValues) => void;
  onComplete: () => void;
  onSaveMaterials?: () => void;
};

export function NewProjectCompletionDock({
  completionDisabled,
  completionError,
  completionLoading,
  requiredActions,
  disabled,
  missingKeys,
  values,
  onChange,
  onComplete,
  onSaveMaterials
}: NewProjectCompletionDockProps): ReactElement {
  const update = (patch: Partial<NewProjectSetupConfirmationValues>) =>
    onChange({ ...values, ...patch });
  const specifiedInputInvalid = missingKeys.has("specified_ltr_number");
  const showRequiredActions = !disabled && !completionLoading && requiredActions.length > 0;

  return (
    <footer className="step-footer new-project-completion-dock">
      <div className="new-project-dock-ltr-control">
        <div className="new-project-ltr-mode-row" role="radiogroup" aria-label="LTR number mode">
          <label>
            <input
              checked={values.ltrMode === "auto"}
              disabled={disabled}
              name="new-project-ltr-mode"
              type="radio"
              onChange={() => update({ ltrMode: "auto" })}
            />
            Auto assign next LTR number
          </label>
          <label>
            <input
              checked={values.ltrMode === "specified"}
              disabled={disabled}
              name="new-project-ltr-mode"
              type="radio"
              onChange={() => update({ ltrMode: "specified" })}
            />
            Use specified LTR number
          </label>
        </div>
        <div className="new-project-specified-ltr-field">
          <input
            id="intake-setup-specified_ltr_number"
            aria-describedby="specified-ltr-help"
            aria-invalid={specifiedInputInvalid}
            aria-label="Specified LTR number"
            className={`new-project-specified-ltr-input ${
              missingKeys.has("specified_ltr_number") ? "setup-field-missing" : ""
            }`}
            disabled={disabled || values.ltrMode !== "specified"}
            placeholder="DL-YYYY-MM-NNN or A1"
            type="text"
            value={values.specifiedLtrNumber}
            onChange={(event) => update({ specifiedLtrNumber: event.target.value })}
          />
          <details className="new-project-ltr-help" id="specified-ltr-help">
            <summary aria-label="Specified LTR number format help">?</summary>
            <div>
              <strong>Valid specified LTR input</strong>
              <span>Base: DL-2026-05-001</span>
              <span>Full with suffix: DL-2026-05-001A or DL-2026-05-001AA</span>
              <span>Suffix only: A, AA, A1, or SAMPLE2</span>
              <span>Suffixes must start with a letter. 123 and DL-2026-05-001123 are invalid.</span>
            </div>
          </details>
        </div>
      </div>

      {completionLoading ? (
        <div className="new-project-ltr-busy-notice" role="status" aria-live="polite">
          <span className="new-project-ltr-busy-spinner" aria-hidden="true" />
          <span>
            <strong>Applying LTR number</strong>
            <span>ConnLab may open and update the LTR workbook. Keep this page open.</span>
          </span>
        </div>
      ) : null}

      {completionError ? (
        <p className="new-project-dock-error" role="alert">{completionError}</p>
      ) : null}

      {showRequiredActions ? (
        <div className="new-project-dock-error">
          <div id="intake-required-heading" role="status">
            Complete {requiredActions.length} {requiredActions.length === 1 ? "field" : "fields"} to apply for an LTR number
          </div>
          <ul className="new-project-required-list" aria-labelledby="intake-required-heading">
            {requiredActions.map(({ targetId, label }) => (
              <li key={targetId}>
                <button
                  className="new-project-required-link"
                  type="button"
                  onClick={() => focusRequiredField(targetId)}
                >
                  {label}
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="new-project-dock-summary">
        {onSaveMaterials ? (
          <button
            className="secondary-action"
            disabled={completionLoading || disabled}
            type="button"
            onClick={onSaveMaterials}
          >
            Save materials
          </button>
        ) : null}

        <button
          className="new-project-primary-action ui-primary-action"
          disabled={completionDisabled}
          aria-describedby={showRequiredActions ? "intake-required-heading" : undefined}
          type="button"
          onClick={onComplete}
        >
          {completionLoading ? "Applying LTR number..." : "Apply LTR Number"}
          <span aria-hidden="true">&gt;</span>
        </button>
      </div>
    </footer>
  );
}

function focusRequiredField(targetId: string): void {
  const control = document.getElementById(targetId);
  if (control) {
    control.focus({ preventScroll: true });
    control.scrollIntoView?.({ block: "center", inline: "nearest" });
  }
}
