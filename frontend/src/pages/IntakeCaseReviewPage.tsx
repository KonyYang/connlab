import { type ReactElement, useEffect, useMemo, useState } from "react";

import {
  type ConfirmIntakeCase,
  type DraftPrecheckIssue,
  type IntakeCaseReview,
  type IntakeCaseReviewField,
  type IntakeCaseReviewItem,
  type IntakePrecheckLookupOptions,
  confirmIntakeCase,
  getIntakePrecheckLookupOptions,
  getIntakeCaseReview,
  updateIntakeCaseReviewFields
} from "../api/client";
import { UiIcon } from "../components/common/UiIcon";
import "../intake-case-review.css";

type IntakeCaseReviewPageProps = {
  packageId: string;
  initialCaseId?: string | null;
  onBack: () => void;
};

type FieldSpec = {
  key: string;
  label: string;
  required?: boolean;
  kind?: "input" | "select" | "date";
  lookupGroup?: keyof IntakePrecheckLookupOptions;
  options?: string[];
};

type SampleRow = Record<string, string>;

type SampleColumn = {
  key: string;
  label: string;
};

const SAMPLE_COLUMNS: SampleColumn[] = [
  { key: "product_name", label: "Product Name" },
  { key: "part_number", label: "Part Number / Revision" },
  { key: "lot_or_traceability", label: "Traceability Manufacturing Lot Info" },
  { key: "material", label: "Contact Base Material" },
  { key: "plating", label: "Contact Plating" },
  { key: "lubricant", label: "Contact Lubricant" },
  { key: "housing_material", label: "Housing Material" },
  { key: "quantity", label: "Quantity" }
];

const PROJECT_FIELDS: FieldSpec[] = [
  { key: "requester", label: "Requested By", required: true },
  { key: "phone", label: "Phone #", required: true },
  { key: "request_date", label: "Date", required: true, kind: "date" },
  { key: "email", label: "Email", required: true },
  {
    key: "business_unit",
    label: "Business Unit",
    required: true,
    kind: "select",
    lookupGroup: "business_unit"
  },
  {
    key: "manufacturing_site",
    label: "Mfg. Site",
    required: true,
    kind: "select",
    lookupGroup: "manufacturing_site"
  },
  { key: "project_no", label: "Project #", required: true },
  {
    key: "results_format",
    label: "Results Format",
    required: true,
    kind: "select",
    lookupGroup: "results_format"
  },
  { key: "requested_completion_date", label: "Requested Testing Completion Date", required: true, kind: "date" },
  {
    key: "test_type",
    label: "Test Type",
    required: true,
    kind: "select",
    lookupGroup: "test_type"
  },
  {
    key: "sample_status",
    label: "Test Sample Status",
    required: true,
    kind: "select",
    lookupGroup: "sample_status"
  },
  {
    key: "project_type",
    label: "Project Type",
    required: true,
    kind: "select",
    lookupGroup: "project_type"
  },
  {
    key: "post_testing_disposition",
    label: "Post-Testing Sample Disposition",
    required: true,
    kind: "select",
    lookupGroup: "post_testing_disposition"
  },
  { key: "send_copies_recipients", label: "Send copies of test results/reports to", required: true }
];

export function IntakeCaseReviewPage({
  packageId,
  initialCaseId,
  onBack
}: IntakeCaseReviewPageProps): ReactElement {
  const [review, setReview] = useState<IntakeCaseReview | null>(null);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [operatorConfirmed, setOperatorConfirmed] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [confirmError, setConfirmError] = useState<string | null>(null);
  const [confirmResult, setConfirmResult] = useState<ConfirmIntakeCase | null>(null);
  const [fieldValues, setFieldValues] = useState<Record<string, string>>({});
  const [sampleRows, setSampleRows] = useState<SampleRow[]>([emptySampleRow()]);
  const [lookupOptions, setLookupOptions] = useState<IntakePrecheckLookupOptions | null>(null);
  const [lookupError, setLookupError] = useState<string | null>(null);
  const [savingFields, setSavingFields] = useState(false);
  const [fieldSaveError, setFieldSaveError] = useState<string | null>(null);
  const [fieldSaveMessage, setFieldSaveMessage] = useState<string | null>(null);

  async function loadReview(): Promise<void> {
    setLoading(true);
    setLoadError(null);
    try {
      const nextReview = await getIntakeCaseReview(packageId);
      setReview(nextReview);
      setSelectedCaseId((current) => preferredCaseId(nextReview, initialCaseId, current));
    } catch (error) {
      setReview(null);
      setLoadError(error instanceof Error ? error.message : "Unable to load Precheck review.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadReview();
  }, [packageId, initialCaseId]);

  useEffect(() => {
    let active = true;
    async function loadLookupOptions(): Promise<void> {
      setLookupError(null);
      try {
        const nextOptions = await getIntakePrecheckLookupOptions();
        if (active) {
          setLookupOptions(nextOptions);
        }
      } catch (error) {
        if (active) {
          setLookupError(error instanceof Error ? error.message : "Unable to load lookup options.");
        }
      }
    }
    void loadLookupOptions();
    return () => {
      active = false;
    };
  }, []);

  const activeCase = useMemo(() => {
    if (!review) {
      return null;
    }
    return review.cases.find((item) => item.case_id === selectedCaseId) ?? review.cases[0] ?? null;
  }, [review, selectedCaseId]);

  const confirmationBlockedReason = activeCase
    ? buildConfirmationBlockedReason(activeCase, operatorConfirmed)
    : "No review case is selected.";

  const canConfirm = Boolean(activeCase?.confirm_allowed && operatorConfirmed && !confirming);
  const fieldValuesChanged = activeCase
    ? activeCase.fields.some((field) => fieldValues[field.key] !== editableValue(field.value))
    : false;
  const sampleRowsChanged = activeCase
    ? JSON.stringify(sampleRows) !== JSON.stringify(normalizedSampleRows(activeCase.sample_rows))
    : false;
  const draftChanged = fieldValuesChanged || sampleRowsChanged;
  const projectFields = useMemo(
    () => fieldsWithLookupOptions(PROJECT_FIELDS, lookupOptions),
    [lookupOptions]
  );
  const issueLevelByField = useMemo(
    () => issueLevelMap(activeCase?.precheck_issues ?? []),
    [activeCase]
  );

  useEffect(() => {
    if (!activeCase) {
      setFieldValues({});
      return;
    }
    setFieldValues(Object.fromEntries(activeCase.fields.map((field) => [field.key, editableValue(field.value)])));
    setSampleRows(normalizedSampleRows(activeCase.sample_rows));
    setFieldSaveError(null);
    setFieldSaveMessage(null);
  }, [activeCase]);

  async function handleConfirm(): Promise<void> {
    if (!activeCase || !canConfirm) {
      return;
    }
    setConfirming(true);
    setConfirmError(null);
    setConfirmResult(null);
    try {
      const result = await confirmIntakeCase(activeCase.case_id);
      setConfirmResult(result);
      setOperatorConfirmed(false);
      await loadReview();
    } catch (error) {
      setConfirmError(error instanceof Error ? error.message : "Unable to confirm this project request.");
    } finally {
      setConfirming(false);
    }
  }

  async function handleSaveFields(): Promise<void> {
    if (!activeCase || !draftChanged) {
      return;
    }
    setSavingFields(true);
    setFieldSaveError(null);
    setFieldSaveMessage(null);
    setConfirmError(null);
    setConfirmResult(null);
    try {
      await updateIntakeCaseReviewFields(activeCase.case_id, {
        fields: fieldValues,
        sample_rows: sampleRows
      });
      setFieldSaveMessage("Corrections saved. Confirmation blockers have been refreshed.");
      setOperatorConfirmed(false);
      await loadReview();
    } catch (error) {
      setFieldSaveError(error instanceof Error ? error.message : "Unable to save field corrections.");
    } finally {
      setSavingFields(false);
    }
  }

  return (
    <section className="precheck-workflow">
      <header className="precheck-header">
        <div>
          <h2>New Project</h2>
          <p>Step 2 of 4: Precheck</p>
        </div>
      </header>

      <PrecheckStepper />

      {loading ? <StatePanel title="Loading Precheck" text="Loading source context, selected case, and confirmation blockers." /> : null}
      {loadError ? <StatePanel tone="danger" title="Precheck cannot be loaded" text={loadError} /> : null}
      {lookupError ? <StatePanel tone="danger" title="Lookup options cannot be loaded" text={lookupError} /> : null}
      {!loading && review && review.cases.length === 0 ? (
        <StatePanel title="No review case exists" text="Create a review case from the package assets before Precheck." />
      ) : null}

      {!loading && review && activeCase ? (
        <>
          <SourceTemplateCheck review={review} activeCase={activeCase} />
          <PrecheckIssueSummary issues={activeCase.precheck_issues} />
          <section className="precheck-card key-information-card">
            <h3>Key Information Edit & Confirm</h3>
            <div className="precheck-form-grid">
              {projectFields.map((field) => (
                <ReviewField
                  disabled={savingFields || Boolean(activeCase.confirmed_project_id)}
                  field={field}
                  issueLevel={issueLevelByField.get(field.key)}
                  key={field.key}
                  value={fieldValues[field.key] ?? fallbackValue(field.key, activeCase.fields)}
                  onChange={(value) => {
                    if (!editableKey(field.key, activeCase.fields)) {
                      return;
                    }
                    setFieldValues((current) => ({ ...current, [field.key]: value }));
                    setFieldSaveMessage(null);
                    setFieldSaveError(null);
                  }}
                />
              ))}
            </div>
            <SampleTable
              disabled={savingFields || Boolean(activeCase.confirmed_project_id)}
              rows={sampleRows}
              onAdd={() => {
                setSampleRows((current) => [...current, emptySampleRow()]);
                setFieldSaveMessage(null);
              }}
              onChange={(rowIndex, key, value) => {
                setSampleRows((current) => updateSampleRow(current, rowIndex, key, value));
                setFieldSaveMessage(null);
                setFieldSaveError(null);
              }}
              onEdit={(rowIndex) => focusSampleRow(rowIndex)}
              onCopy={(rowIndex) => {
                setSampleRows((current) => copySampleRow(current, rowIndex));
                setFieldSaveMessage(null);
              }}
              onDelete={(rowIndex) => {
                setSampleRows((current) => deleteSampleRow(current, rowIndex));
                setFieldSaveMessage(null);
              }}
            />
            <div className="precheck-lower-grid">
              <ConsentPanel
                confidential={fieldValues.confidential ?? fallbackValue("confidential", activeCase.fields)}
                subcontract={fieldValues.subcontract ?? fallbackValue("subcontract", activeCase.fields)}
              />
              <RequestedTestingPanel value={fieldValues.requested_testing ?? fallbackValue("requested_testing", activeCase.fields)} />
              <AdditionalInfoPanel value={fieldValues.additional_information ?? fallbackValue("additional_information", activeCase.fields)} />
            </div>
          </section>

          {review.cases.length > 1 ? (
            <section className="precheck-card case-switcher">
              <h3>Review cases</h3>
              <div className="case-selector-list">
                {review.cases.map((item) => (
                  <button
                    className={item.case_id === activeCase.case_id ? "case-selector-button case-selector-button-active" : "case-selector-button"}
                    key={item.case_id}
                    type="button"
                    onClick={() => {
                      setSelectedCaseId(item.case_id);
                      setOperatorConfirmed(false);
                      setConfirmError(null);
                      setConfirmResult(null);
                    }}
                  >
                    <strong>{item.selected_asset_name ?? "Manual intake"}</strong>
                    <span>{formatStatus(item.status)}</span>
                  </button>
                ))}
              </div>
            </section>
          ) : null}

          <footer className="precheck-footer">
            <button className="secondary-button precheck-back-button" type="button" onClick={onBack}>
              <span className="button-arrow" aria-hidden="true">&lt;</span>
              Back to Intake
            </button>
            <div className="footer-source-status">
              <UiIcon name="clock" />
              <span>Source: Intake email / application form verified</span>
            </div>
            <label className="confirm-check">
              <input
                checked={operatorConfirmed}
                disabled={!activeCase.confirm_allowed || Boolean(activeCase.confirmed_project_id)}
                type="checkbox"
                onChange={(event) => setOperatorConfirmed(event.target.checked)}
              />
              <span className="sr-only">I confirm this reviewed case should create one project.</span>
            </label>
            <button
              className="secondary-button"
              disabled={!draftChanged || savingFields || Boolean(activeCase.confirmed_project_id)}
              type="button"
              onClick={() => void handleSaveFields()}
            >
              <span className="sr-only">Save corrections</span>
              {savingFields ? "Saving" : "Save Draft"}
            </button>
            <button className="primary-button precheck-confirm-button" disabled={!canConfirm} type="button" onClick={() => void handleConfirm()}>
              {confirming ? "Confirming" : "Confirm & Continue to LTR Number"}
              <span className="button-arrow" aria-hidden="true">&gt;</span>
            </button>
          </footer>

          <Messages
            activeCase={activeCase}
            confirmationBlockedReason={confirmationBlockedReason}
            confirmError={confirmError}
            confirmResult={confirmResult}
            fieldSaveError={fieldSaveError}
            fieldSaveMessage={fieldSaveMessage}
          />
        </>
      ) : null}
    </section>
  );
}

function PrecheckStepper(): ReactElement {
  const steps = ["Intake", "Precheck", "LTR Number", "Project Folder"];
  return (
    <ol className="precheck-stepper" aria-label="New project steps">
      {steps.map((step, index) => (
        <li className={index < 1 ? "precheck-step precheck-step-done" : index === 1 ? "precheck-step precheck-step-active" : "precheck-step"} key={step}>
          <span>{index === 0 ? "Done" : index + 1}</span>
          <strong>{step}</strong>
        </li>
      ))}
    </ol>
  );
}

function SourceTemplateCheck({ review, activeCase }: { review: IntakeCaseReview; activeCase: IntakeCaseReviewItem }): ReactElement {
  return (
    <section className="precheck-card source-template-check">
      <h3>Source document & template check</h3>
      <div className="template-check-grid">
        <div className="source-doc-card">
          <span className="word-file-icon">W</span>
          <div>
            <strong>{activeCase.selected_asset_name ?? review.source_original_name}</strong>
            <span>source context: {formatSourceType(review.source_type)}</span>
          </div>
          <UiIcon name="clock" />
        </div>
        <div className="metadata-card">
          <FieldBadge label="Form No." value={fallbackValue("form_no", activeCase.fields) || "E-7818"} />
          <FieldBadge label="Revision" value={fallbackValue("revision", activeCase.fields) || "H"} />
          <FieldBadge label="Reference doc." value={fallbackValue("reference_doc", activeCase.fields) || "QS-03-008"} />
        </div>
        <div className="template-warning-card">
          <div className="template-warning-copy">
            <UiIcon name="help" />
            <div>
              <strong>Template version mismatch detected</strong>
              <span>Current: In Library: E_3778_Rev-H</span>
              <span>Source: E_3778_Rev-H</span>
            </div>
          </div>
          <button className="secondary-button" disabled type="button">
            <UiIcon name="refresh" />
            Update to latest template
          </button>
        </div>
      </div>
    </section>
  );
}

function ReviewField({
  field,
  value,
  disabled,
  issueLevel,
  onChange
}: {
  field: FieldSpec;
  value: string;
  disabled: boolean;
  issueLevel?: string;
  onChange: (value: string) => void;
}): ReactElement {
  const options = normalizedOptions(field.options ?? [], value);
  const inputValue = field.kind === "date" ? dateInputValue(value) : value;
  return (
    <label className={fieldClassName(issueLevel)}>
      <span>{field.label}{field.required ? <b>*</b> : null}</span>
      {field.kind === "select" ? (
        <select disabled={disabled} value={value || options[0] || ""} onChange={(event) => onChange(event.target.value)}>
          {options.map((option) => <option key={option}>{option}</option>)}
        </select>
      ) : (
        <input
          className="draft-field-input"
          disabled={disabled}
          type={field.kind === "date" ? "date" : "text"}
          value={inputValue}
          onChange={(event) => onChange(event.target.value)}
        />
      )}
    </label>
  );
}

function SampleTable({
  disabled,
  rows,
  onAdd,
  onChange,
  onEdit,
  onCopy,
  onDelete
}: {
  disabled: boolean;
  rows: SampleRow[];
  onAdd: () => void;
  onChange: (rowIndex: number, key: string, value: string) => void;
  onEdit: (rowIndex: number) => void;
  onCopy: (rowIndex: number) => void;
  onDelete: (rowIndex: number) => void;
}): ReactElement {
  return (
    <div className="sample-table-wrap">
      <div className="sample-table-header">
        <h4>Test Sample Information</h4>
        <button className="sample-add-button" disabled={disabled} type="button" onClick={onAdd}>
          Add Sample
        </button>
      </div>
      <table className="precheck-sample-table">
        <thead>
          <tr>
            {SAMPLE_COLUMNS.map((column) => <th key={column.key}>{column.label}</th>)}
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={`sample-${rowIndex}`}>
              {SAMPLE_COLUMNS.map((column) => (
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

function ConsentPanel({
  confidential,
  subcontract
}: {
  confidential: string;
  subcontract: string;
}): ReactElement {
  return (
    <section className="precheck-subpanel">
      <RadioLine label="Confidential test or samples?" value={confidential} />
      <RadioLine label="Can testing be subcontracted?" value={subcontract} />
    </section>
  );
}

function RadioLine({
  label,
  value
}: {
  label: string;
  value: string;
}): ReactElement {
  const normalized = value.trim().toLowerCase();
  const yes = ["yes", "y", "true", "1", "是"].includes(normalized);
  const no = value ? ["no", "n", "false", "0", "否"].includes(normalized) : false;
  return <div className="radio-line"><strong>{label}<b>*</b></strong><label><input checked={yes} readOnly name={label} type="radio" />Yes</label><label><input checked={no} readOnly name={label} type="radio" />No</label></div>;
}

function RequestedTestingPanel({ value }: { value: string }): ReactElement {
  return (
    <section className="precheck-subpanel requested-testing-panel">
      <h4>Description of Requested Testing</h4>
      <table><tbody><tr><td>Qualification test</td><td>{value || "QG-03-016_Rev1"}</td></tr><tr><td>Defect/Performance test</td><td>DG-00-048_Rev2</td></tr><tr><td>Environmental test</td><td>QG-03-016E_Rev2</td></tr></tbody></table>
      <button className="secondary-button" type="button">+ Add Row</button>
    </section>
  );
}

function AdditionalInfoPanel({ value }: { value: string }): ReactElement {
  return <section className="precheck-subpanel"><h4>Additional Information</h4><textarea value={value} readOnly placeholder="No additional information extracted from the selected application form." /></section>;
}

function PrecheckIssueSummary({ issues }: { issues: DraftPrecheckIssue[] }): ReactElement {
  const errors = issues.filter((issue) => issue.level === "error");
  const warnings = issues.filter((issue) => issue.level === "warning");
  if (issues.length === 0) {
    return <div className="precheck-issue-summary precheck-issue-summary-pass"><UiIcon name="help" /><strong>SECTION 1 precheck passed.</strong><span>No Project creation blockers detected.</span></div>;
  }
  return (
    <div className="precheck-issue-summary">
      <UiIcon name="help" />
      <div>
        <strong>{errors.length} blocker{errors.length === 1 ? "" : "s"} and {warnings.length} warning{warnings.length === 1 ? "" : "s"} before Project creation</strong>
        <span>Lab Test Request Number must be blank. SECTION 2 lab fields are excluded from this pre-project check.</span>
        <ul>
          {issues.slice(0, 6).map((issue) => (
            <li className={`precheck-issue-${issue.level}`} key={`${issue.field_key}-${issue.message}`}>{issue.message}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

function Messages(props: {
  activeCase: IntakeCaseReviewItem;
  confirmationBlockedReason: string | null;
  confirmError: string | null;
  confirmResult: ConfirmIntakeCase | null;
  fieldSaveError: string | null;
  fieldSaveMessage: string | null;
}): ReactElement {
  return (
    <div className="precheck-messages">
      {props.activeCase.missing_required_fields.length > 0 ? <p>Confirmation blockers: {props.activeCase.missing_required_fields.join(", ")}. Backend confirmation rejects missing required project request fields. missing_required_fields</p> : null}
      {props.confirmationBlockedReason ? <p>{props.confirmationBlockedReason}</p> : null}
      {props.confirmError ? <p>{props.confirmError}</p> : null}
      {props.fieldSaveError ? <p>{props.fieldSaveError}</p> : null}
      {props.fieldSaveMessage ? <p>{props.fieldSaveMessage}</p> : null}
      {props.confirmResult ? <p className="confirmation-result">Project created: {props.confirmResult.project_id}. Confirm into project completed.</p> : null}
    </div>
  );
}

function FieldBadge({ label, value }: { label: string; value: string }): ReactElement {
  return <dl><dt>{label}</dt><dd>{value}</dd></dl>;
}

function StatePanel({ title, text, tone }: { title: string; text: string; tone?: "danger" }): ReactElement {
  return <div className={tone === "danger" ? "precheck-card precheck-state precheck-state-danger" : "precheck-card precheck-state"}><h3>{title}</h3><p>{text}</p></div>;
}

function buildConfirmationBlockedReason(activeCase: IntakeCaseReviewItem, operatorConfirmed: boolean): string | null {
  if (activeCase.confirmed_project_id) {
    return `Already confirmed into project ${activeCase.confirmed_project_id}.`;
  }
  if (!activeCase.confirm_allowed) {
    return "Required project request information is still missing.";
  }
  if (!operatorConfirmed) {
    return "Operator confirmation is required before project creation.";
  }
  return null;
}

function editableKey(key: string, fields: IntakeCaseReviewField[]): boolean {
  return fields.some((field) => field.key === key);
}

function normalizedOptions(options: string[], value: string): string[] {
  if (!value || options.includes(value)) {
    return options;
  }
  return [value, ...options];
}

function fieldsWithLookupOptions(
  fields: FieldSpec[],
  lookups: IntakePrecheckLookupOptions | null
): FieldSpec[] {
  return fields.map((field) => {
    if (!field.lookupGroup || !lookups) {
      return field;
    }
    return {
      ...field,
      options: lookups[field.lookupGroup].map((option) => option.value)
    };
  });
}

function issueLevelMap(issues: DraftPrecheckIssue[]): Map<string, string> {
  const levels = new Map<string, string>();
  for (const issue of issues) {
    if (!levels.has(issue.field_key) || issue.level === "error") {
      levels.set(issue.field_key, issue.level);
    }
  }
  return levels;
}

function fieldClassName(issueLevel?: string): string {
  if (issueLevel === "error") {
    return "precheck-field precheck-field-error";
  }
  if (issueLevel === "warning") {
    return "precheck-field precheck-field-warning";
  }
  return "precheck-field";
}

function dateInputValue(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) {
    return "";
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) {
    return trimmed;
  }
  const slashMatch = /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/.exec(trimmed);
  if (!slashMatch) {
    return "";
  }
  const [, month, day, year] = slashMatch;
  return `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`;
}

function cellText(value: unknown): string {
  if (value === null || value === undefined) {
    return "";
  }
  return String(value);
}

function normalizedSampleRows(rows: Record<string, unknown>[]): SampleRow[] {
  if (rows.length === 0) {
    return [emptySampleRow()];
  }
  return rows.map((row) => ({
    ...Object.fromEntries(SAMPLE_COLUMNS.map((column) => [column.key, cellText(row[column.key])])),
    part_number: mergedPartNumberRevision(row),
    lot_or_traceability: mergedTraceabilityLotInfo(row)
  }));
}

function emptySampleRow(): SampleRow {
  return Object.fromEntries(SAMPLE_COLUMNS.map((column) => [column.key, ""]));
}

function updateSampleRow(
  rows: SampleRow[],
  rowIndex: number,
  key: string,
  value: string
): SampleRow[] {
  return rows.map((row, index) => (index === rowIndex ? { ...row, [key]: value } : row));
}

function copySampleRow(rows: SampleRow[], rowIndex: number): SampleRow[] {
  const copied = { ...(rows[rowIndex] ?? emptySampleRow()) };
  return [...rows.slice(0, rowIndex + 1), copied, ...rows.slice(rowIndex + 1)];
}

function deleteSampleRow(rows: SampleRow[], rowIndex: number): SampleRow[] {
  if (rows.length <= 1) {
    return rows;
  }
  return rows.filter((_, index) => index !== rowIndex);
}

function focusSampleRow(rowIndex: number): void {
  document
    .querySelector<HTMLInputElement>(
      `[data-sample-row="${rowIndex}"][data-sample-column="product_name"]`
    )
    ?.focus();
}

function mergedPartNumberRevision(row: Record<string, unknown>): string {
  const partNumber = cellText(row.part_number);
  const revision = cellText(row.revision);
  if (!partNumber || !revision || partNumber.toLowerCase().includes(revision.toLowerCase())) {
    return partNumber;
  }
  return `${partNumber} ${revision}`;
}

function mergedTraceabilityLotInfo(row: Record<string, unknown>): string {
  const traceability = cellText(row.lot_or_traceability);
  const manufacturingLot = cellText(row.manufacturing_lot_no);
  if (!traceability || !manufacturingLot || traceability.includes(manufacturingLot)) {
    return traceability;
  }
  return `${traceability} ${manufacturingLot}`;
}


function preferredCaseId(
  review: IntakeCaseReview,
  initialCaseId?: string | null,
  currentCaseId?: string | null
): string | null {
  if (initialCaseId && review.cases.some((item) => item.case_id === initialCaseId)) {
    return initialCaseId;
  }
  if (currentCaseId && review.cases.some((item) => item.case_id === currentCaseId)) {
    return currentCaseId;
  }
  return review.cases[0]?.case_id ?? null;
}

function fallbackValue(key: string, fields: IntakeCaseReviewField[]): string {
  const match = fields.find((field) => field.key === key);
  return match ? editableValue(match.value) : "";
}

function formatStatus(status: string): string {
  return status.split("_").filter(Boolean).map((part) => part[0]?.toUpperCase() + part.slice(1)).join(" ");
}

function formatSourceType(sourceType: string): string {
  if (sourceType === "manual" || sourceType === "manual_entry") {
    return "Manual entry";
  }
  if (sourceType === "msg_import") {
    return "MSG package";
  }
  return formatStatus(sourceType);
}

function editableValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "";
  }
  return typeof value === "object" ? JSON.stringify(value) : String(value);
}
