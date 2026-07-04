import type { ReactElement } from "react";

import type { IntakeCaseReviewItem, IntakeCaseReviewField } from "../../api/client";
import {
  emptyPrecheckRequestedTestingRow,
  emptyPrecheckSampleRow,
  type PrecheckFieldSpec,
  type PrecheckRequestedTestingRow,
  type PrecheckSampleRow
} from "../precheck/precheckFieldConfig";
import { PrecheckFieldGrid } from "../precheck/PrecheckFieldGrid";
import { PrecheckLowerPanels } from "../precheck/PrecheckLowerPanels";
import { PrecheckSampleTable } from "../precheck/PrecheckSampleTable";
import {
  copySampleRow,
  deleteSampleRow,
  fallbackValue,
  updateSampleRow
} from "../precheck/precheckReviewSelectors";
import type { NewProjectRequiredState } from "./newProjectRequiredState";

type NewProjectApplicationEditorProps = {
  activeCase: IntakeCaseReviewItem | null;
  autoSaveError: string | null;
  completionResult: string | null;
  disabled: boolean;
  fieldValues: Record<string, string>;
  importMessage: string | null;
  lookupError: string | null;
  projectFields: PrecheckFieldSpec[];
  requestedTestingRows: PrecheckRequestedTestingRow[];
  requiredState: NewProjectRequiredState;
  sampleRows: PrecheckSampleRow[];
  sourceFields: IntakeCaseReviewField[];
  onFieldValuesChange: (values: Record<string, string>) => void;
  onRequestedTestingRowsChange: (rows: PrecheckRequestedTestingRow[]) => void;
  onSampleRowsChange: (rows: PrecheckSampleRow[]) => void;
};

export function NewProjectApplicationEditor({
  activeCase,
  autoSaveError,
  completionResult,
  disabled,
  fieldValues,
  importMessage,
  lookupError,
  projectFields,
  requestedTestingRows,
  requiredState,
  sampleRows,
  sourceFields,
  onFieldValuesChange,
  onRequestedTestingRowsChange,
  onSampleRowsChange
}: NewProjectApplicationEditorProps): ReactElement {
  const baseEditingFrozen = Boolean(activeCase?.base_editing_frozen);
  const frozenReason =
    activeCase?.frozen_reason ?? "LTR registered. Base application fields require revise/exception handling.";
  const editingDisabled = disabled || baseEditingFrozen;
  return (
    <section className="new-project-editor-panel">
      <div className="new-project-editor-heading">
        <h3 className="ui-panel-title">Application information</h3>
        {importMessage ? <p className="new-project-imported-form-message">{importMessage}</p> : null}
      </div>

      {autoSaveError ? <p className="intake-error">{autoSaveError}</p> : null}

      {baseEditingFrozen ? (
        <p className="new-project-frozen-notice">{frozenReason}</p>
      ) : null}

      {lookupError ? <p className="intake-error">{lookupError}</p> : null}

      <PrecheckFieldGrid
        disabled={editingDisabled}
        fields={projectFields}
        issueLevelByField={new Map()}
        missingRequiredByField={requiredState.missingFieldKeys}
        sourceFields={sourceFields}
        values={fieldValues}
        onChange={(key, value) => onFieldValuesChange({ ...fieldValues, [key]: value })}
      />

      <PrecheckSampleTable
        disabled={editingDisabled}
        missingCells={requiredState.missingSampleCells}
        rows={sampleRows}
        onAdd={() => onSampleRowsChange([...sampleRows, emptyPrecheckSampleRow()])}
        onChange={(rowIndex, key, value) =>
          onSampleRowsChange(updateSampleRow(sampleRows, rowIndex, key, value))
        }
        onCopy={(rowIndex) => onSampleRowsChange(copySampleRow(sampleRows, rowIndex))}
        onDelete={(rowIndex) => onSampleRowsChange(deleteSampleRow(sampleRows, rowIndex))}
      />

      <PrecheckLowerPanels
        additionalInformation={
          fieldValues.additional_information ?? fallbackValue("additional_information", sourceFields)
        }
        confidential={fieldValues.confidential ?? fallbackValue("confidential", sourceFields)}
        disabled={editingDisabled}
        missingRequiredKeys={requiredState.missingFieldKeys}
        requestedTestingRows={requestedTestingRows}
        subcontract={fieldValues.subcontract ?? fallbackValue("subcontract", sourceFields)}
        onAdditionalInformationChange={(value) =>
          onFieldValuesChange({ ...fieldValues, additional_information: value })
        }
        onConfidentialChange={(value) =>
          onFieldValuesChange({ ...fieldValues, confidential: value })
        }
        onRequestedTestingRowAdd={() =>
          onRequestedTestingRowsChange([
            ...requestedTestingRows,
            emptyPrecheckRequestedTestingRow()
          ])
        }
        onRequestedTestingRowChange={(rowIndex, key, value) =>
          onRequestedTestingRowsChange(
            requestedTestingRows.map((row, index) =>
              index === rowIndex ? { ...row, [key]: value } : row
            )
          )
        }
        onRequestedTestingRowCopy={(rowIndex) => {
          const copied = { ...(requestedTestingRows[rowIndex] ?? emptyPrecheckRequestedTestingRow()) };
          onRequestedTestingRowsChange([
            ...requestedTestingRows.slice(0, rowIndex + 1),
            copied,
            ...requestedTestingRows.slice(rowIndex + 1)
          ]);
        }}
        onRequestedTestingRowDelete={(rowIndex) => {
          if (requestedTestingRows.length <= 1) {
            return;
          }
          onRequestedTestingRowsChange(
            requestedTestingRows.filter((_, index) => index !== rowIndex)
          );
        }}
        onSubcontractChange={(value) =>
          onFieldValuesChange({ ...fieldValues, subcontract: value })
        }
      />

      {completionResult ? <p className="new-project-completion-result">{completionResult}</p> : null}

    </section>
  );
}
