import type { ReactElement } from "react";

import { UiIcon } from "../../components/common/UiIcon";
import type { NewProjectSetupConfirmationValues } from "./NewProjectSetupConfirmationPanel";

type NewProjectCompletionDockProps = {
  completionDisabled: boolean;
  completionLoading: boolean;
  completionText: string;
  disabled: boolean;
  missingKeys: Set<string>;
  values: NewProjectSetupConfirmationValues;
  onChange: (values: NewProjectSetupConfirmationValues) => void;
  onComplete: () => void;
};

export function NewProjectCompletionDock({
  completionDisabled,
  completionLoading,
  completionText,
  disabled,
  missingKeys,
  values,
  onChange,
  onComplete
}: NewProjectCompletionDockProps): ReactElement {
  const update = (patch: Partial<NewProjectSetupConfirmationValues>) =>
    onChange({ ...values, ...patch });
  const specifiedInputInvalid =
    values.ltrMode === "specified" && !isValidSpecifiedLtrInput(values.specifiedLtrNumber);

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

      <div className="new-project-dock-summary">
        <span className="new-project-required-count">
          <UiIcon name="clock" />
          <span title="required fields remaining">{completionText}</span>
        </span>

        <button
          className="new-project-primary-action ui-primary-action"
          disabled={completionDisabled}
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

export function isValidSpecifiedLtrInput(value: string): boolean {
  const input = value.trim();
  if (!input) {
    return false;
  }
  const baseOrFull = /^DL-(\d{4})-(\d{2})-(\d{3})([A-Z][A-Z0-9]*)?$/i.exec(input);
  if (baseOrFull) {
    const year = Number(baseOrFull[1]);
    const month = Number(baseOrFull[2]);
    const sequence = Number(baseOrFull[3]);
    return year >= 2000 && month >= 1 && month <= 12 && sequence >= 1;
  }
  return /^[A-Z][A-Z0-9]*$/i.test(input);
}
