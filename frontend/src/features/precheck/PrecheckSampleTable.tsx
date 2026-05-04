import type { ReactElement } from "react";

import { UiIcon } from "../../components/common/UiIcon";
import {
  PRECHECK_SAMPLE_COLUMNS,
  type PrecheckSampleRow
} from "./precheckFieldConfig";

type PrecheckSampleTableProps = {
  disabled: boolean;
  rows: PrecheckSampleRow[];
  onAdd: () => void;
  onChange: (rowIndex: number, key: string, value: string) => void;
  onEdit: (rowIndex: number) => void;
  onCopy: (rowIndex: number) => void;
  onDelete: (rowIndex: number) => void;
};

export function PrecheckSampleTable({
  disabled,
  rows,
  onAdd,
  onChange,
  onEdit,
  onCopy,
  onDelete
}: PrecheckSampleTableProps): ReactElement {
  return (
    <div className="sample-table-wrap">
      <div className="sample-table-header">
        <h4 className="ui-section-title">Test Sample Information</h4>
        <button className="sample-add-button ui-compact-action" disabled={disabled} type="button" onClick={onAdd}>
          Add Sample
        </button>
      </div>
      <table className="precheck-sample-table">
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
                <td key={column.key}>
                  <input
                    aria-label={`${column.label} row ${rowIndex + 1}`}
                    data-sample-column={column.key}
                    data-sample-row={rowIndex}
                    disabled={disabled}
                    value={row[column.key] ?? ""}
                    onChange={(event) => onChange(rowIndex, column.key, event.target.value)}
                  />
                </td>
              ))}
              <td>
                <div className="sample-row-actions">
                  <button disabled={disabled} title="Edit sample row" type="button" onClick={() => onEdit(rowIndex)}>
                    <UiIcon name="edit" />
                    <span className="sr-only">Edit sample row</span>
                  </button>
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
