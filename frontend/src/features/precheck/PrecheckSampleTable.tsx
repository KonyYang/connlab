import { useLayoutEffect, useRef, type ReactElement } from "react";

import { UiIcon } from "../../components/common/UiIcon";
import {
  PRECHECK_SAMPLE_COLUMNS,
  type PrecheckSampleRow
} from "./precheckFieldConfig";

type PrecheckSampleTableProps = {
  disabled: boolean;
  missingCells?: Set<string>;
  rows: PrecheckSampleRow[];
  onAdd: () => void;
  onChange: (rowIndex: number, key: string, value: string) => void;
  onCopy: (rowIndex: number) => void;
  onDelete: (rowIndex: number) => void;
};

export function PrecheckSampleTable({
  disabled,
  missingCells,
  rows,
  onAdd,
  onChange,
  onCopy,
  onDelete
}: PrecheckSampleTableProps): ReactElement {
  return (
    <div className="sample-table-wrap">
      <div className="sample-table-header">
        <h4 className="ui-section-title">Test Sample Information</h4>
        <button className="sample-add-button ui-compact-action" disabled={disabled} type="button" onClick={onAdd}>
          Add Row
        </button>
      </div>
      <table className="precheck-sample-table">
        <colgroup>
          <col className="sample-col-product-name" />
          <col className="sample-col-part-number" />
          <col className="sample-col-traceability" />
          <col className="sample-col-contact-base-material" />
          <col className="sample-col-contact-plating" />
          <col className="sample-col-contact-lubricant" />
          <col className="sample-col-housing-material" />
          <col className="sample-col-quantity" />
          <col className="sample-col-actions" />
        </colgroup>
        <thead>
          <tr>
            {PRECHECK_SAMPLE_COLUMNS.map((column) => <th key={column.key}>{column.label}</th>)}
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={`sample-${rowIndex}`}>
              {PRECHECK_SAMPLE_COLUMNS.map((column) => (
                <td
                  className={missingCells?.has(`${rowIndex}:${column.key}`) ? "sample-cell-required-missing" : undefined}
                  key={column.key}
                >
                  <AutoGrowTextarea
                    ariaLabel={`${column.label} row ${rowIndex + 1}`}
                    columnKey={column.key}
                    disabled={disabled}
                    rowIndex={rowIndex}
                    value={row[column.key] ?? ""}
                    onChange={(value) => onChange(rowIndex, column.key, value)}
                  />
                </td>
              ))}
              <td>
                <div className="sample-row-actions">
                  <button disabled={disabled} title="Copy sample row" type="button" onClick={() => onCopy(rowIndex)}>
                    <UiIcon name="copy" />
                    <span className="sr-only">Copy sample row</span>
                  </button>
                  <button disabled={disabled || rows.length <= 1} title="Delete sample row" type="button" onClick={() => onDelete(rowIndex)}>
                    <UiIcon name="trash" />
                    <span className="sr-only">Delete sample row</span>
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

type AutoGrowTextareaProps = {
  ariaLabel: string;
  columnKey: string;
  disabled: boolean;
  rowIndex: number;
  value: string;
  onChange: (value: string) => void;
};

function AutoGrowTextarea({
  ariaLabel,
  columnKey,
  disabled,
  rowIndex,
  value,
  onChange,
}: AutoGrowTextareaProps): ReactElement {
  const ref = useRef<HTMLTextAreaElement | null>(null);

  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) {
      return;
    }
    element.style.height = "auto";
    // Keep a larger buffer so wrapped lines never clip with bordered capsule editors.
    element.style.height = `${element.scrollHeight + 4}px`;
  }, [value]);

  return (
    <textarea
      ref={ref}
      aria-label={ariaLabel}
      className="precheck-sample-cell-input"
      data-sample-column={columnKey}
      data-sample-row={rowIndex}
      disabled={disabled}
      rows={1}
      value={value}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}
