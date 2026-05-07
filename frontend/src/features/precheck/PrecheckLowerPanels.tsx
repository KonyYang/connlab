import { useLayoutEffect, useRef, type ReactElement } from "react";
import { UiIcon } from "../../components/common/UiIcon";
import {
  PRECHECK_REQUESTED_TESTING_COLUMNS,
  type PrecheckRequestedTestingRow
} from "./precheckFieldConfig";

type PrecheckLowerPanelsProps = {
  additionalInformation: string;
  confidential: string;
  disabled?: boolean;
  missingRequiredKeys?: Set<string>;
  requestedTestingRows: PrecheckRequestedTestingRow[];
  subcontract: string;
  onAdditionalInformationChange: (value: string) => void;
  onConfidentialChange: (value: string) => void;
  onRequestedTestingRowAdd: () => void;
  onRequestedTestingRowChange: (
    rowIndex: number,
    key: keyof PrecheckRequestedTestingRow,
    value: string
  ) => void;
  onRequestedTestingRowCopy: (rowIndex: number) => void;
  onRequestedTestingRowDelete: (rowIndex: number) => void;
  onSubcontractChange: (value: string) => void;
};

export function PrecheckLowerPanels({
  additionalInformation,
  confidential,
  disabled,
  missingRequiredKeys,
  requestedTestingRows,
  subcontract,
  onAdditionalInformationChange,
  onConfidentialChange,
  onRequestedTestingRowAdd,
  onRequestedTestingRowChange,
  onRequestedTestingRowCopy,
  onRequestedTestingRowDelete,
  onSubcontractChange
}: PrecheckLowerPanelsProps): ReactElement {
  return (
    <div className="precheck-lower-grid">
      <section className="precheck-consent-row">
        <RadioLine
        disabled={disabled}
        missing={missingRequiredKeys?.has("confidential")}
        label="Confidential test or samples?"
          value={confidential}
          onChange={onConfidentialChange}
        />
        <RadioLine
        disabled={disabled}
        missing={missingRequiredKeys?.has("subcontract")}
        label="Can testing be subcontracted?"
          value={subcontract}
          onChange={onSubcontractChange}
        />
      </section>
      <RequestedTestingPanel
        disabled={disabled}
        missing={missingRequiredKeys?.has("requested_testing")}
        rows={requestedTestingRows}
        onAdd={onRequestedTestingRowAdd}
        onChange={onRequestedTestingRowChange}
        onCopy={onRequestedTestingRowCopy}
        onDelete={onRequestedTestingRowDelete}
      />
      <AdditionalInfoPanel
        additionalInformation={additionalInformation}
        disabled={disabled}
        onChange={onAdditionalInformationChange}
      />
    </div>
  );
}



function RadioLine({
  disabled,
  label,
  missing,
  value,
  onChange
}: {
  disabled?: boolean;
  label: string;
  missing?: boolean;
  value: string;
  onChange: (value: string) => void;
}): ReactElement {
  const normalized = value.trim().toLowerCase();
  const yes = ["yes", "y", "true", "1", "是"].includes(normalized);
  const no = value ? ["no", "n", "false", "0", "否"].includes(normalized) : false;
  return (
    <div className={missing ? "radio-line radio-line-required-missing" : "radio-line"}>
      <strong>
        {label}<b>*</b>
      </strong>
      <label>
        <input
          checked={yes}
          disabled={disabled}
          name={label}
          type="radio"
          onChange={() => onChange("Yes")}
        />
        Yes
      </label>
      <label>
        <input
          checked={no}
          disabled={disabled}
          name={label}
          type="radio"
          onChange={() => onChange("No")}
        />
        No
      </label>
    </div>
  );
}

function RequestedTestingPanel({
  disabled,
  missing,
  rows,
  onAdd,
  onChange,
  onCopy,
  onDelete
}: {
  disabled?: boolean;
  missing?: boolean;
  rows: PrecheckRequestedTestingRow[];
  onAdd: () => void;
  onChange: (
    rowIndex: number,
    key: keyof PrecheckRequestedTestingRow,
    value: string
  ) => void;
  onCopy: (rowIndex: number) => void;
  onDelete: (rowIndex: number) => void;
}): ReactElement {
  return (
    <section className={missing ? "requested-testing-panel requested-testing-required-missing" : "requested-testing-panel"}>
      <div className="requested-testing-header">
        <h4 className="ui-section-title">Description of Requested Testing</h4>
        <button
          className="requested-testing-add-button ui-compact-action"
          disabled={disabled}
          type="button"
          onClick={onAdd}
        >
          Add Row
        </button>
      </div>
      <table className="requested-testing-edit-table">
        <thead>
          <tr>
            {PRECHECK_REQUESTED_TESTING_COLUMNS.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex}>
              {PRECHECK_REQUESTED_TESTING_COLUMNS.map((column) => (
                <td key={column.key}>
                  <AutoGrowTextarea
                    disabled={disabled}
                    value={(row as Record<string, string>)[column.key] ?? ""}
                    onChange={(event) => onChange(rowIndex, column.key, event.target.value)}
                  />
                </td>
              ))}
              <td>
                <div className="requested-testing-row-actions">
                  <button
                    disabled={disabled}
                    title="Copy requested testing row"
                    type="button"
                    onClick={() => onCopy(rowIndex)}
                  >
                    <UiIcon name="copy" />
                    <span className="sr-only">Copy requested testing row</span>
                  </button>
                  <button
                    disabled={disabled || rows.length <= 1}
                    title="Delete requested testing row"
                    type="button"
                    onClick={() => onDelete(rowIndex)}
                  >
                    <UiIcon name="trash" />
                    <span className="sr-only">Delete requested testing row</span>
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}

function AdditionalInfoPanel({
  additionalInformation,
  disabled,
  onChange
}: {
  additionalInformation: string;
  disabled?: boolean;
  onChange: (value: string) => void;
}): ReactElement {
  return (
    <section className="precheck-additional-panel">
      <h4 className="ui-section-title">Additional Information</h4>
      <AutoGrowPanelTextarea
        className="precheck-additional-input"
        disabled={disabled}
        placeholder="No additional information extracted from the selected application form."
        value={additionalInformation}
        onChange={onChange}
      />
    </section>
  );
}

function AutoGrowPanelTextarea({
  className,
  disabled,
  placeholder,
  value,
  onChange
}: {
  className?: string;
  disabled?: boolean;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
}): ReactElement {
  const ref = useRef<HTMLTextAreaElement | null>(null);

  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) {
      return;
    }
    element.style.height = "auto";
    element.style.height = `${element.scrollHeight}px`;
  }, [value]);

  return (
    <textarea
      ref={ref}
      className={className}
      disabled={disabled}
      placeholder={placeholder}
      rows={1}
      value={value}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}

function AutoGrowTextarea({
  disabled,
  value,
  onChange
}: {
  disabled?: boolean;
  value: string;
  onChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
}): ReactElement {
  const ref = useRef<HTMLTextAreaElement | null>(null);

  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) {
      return;
    }
    element.style.height = "auto";
    element.style.height = `${element.scrollHeight}px`;
  }, [value]);

  return (
    <textarea
      ref={ref}
      className="requested-testing-cell-input"
      disabled={disabled}
      rows={1}
      value={value}
      onChange={onChange}
    />
  );
}
