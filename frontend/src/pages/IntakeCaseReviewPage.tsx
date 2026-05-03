import { type ReactElement, useEffect, useMemo, useState } from "react";

import {
  type ConfirmIntakeCase,
  type IntakeCaseReview,
  type IntakePrecheckLookupOptions,
  confirmIntakeCase,
  getIntakeCaseReview,
  getIntakePrecheckLookupOptions,
  updateIntakeCaseReviewFields
} from "../api/client";
import { UiIcon } from "../components/common/UiIcon";
import {
  emptyPrecheckSampleRow,
  PRECHECK_PROJECT_FIELDS,
  type PrecheckSampleRow
} from "../features/precheck/precheckFieldConfig";
import { PrecheckFieldGrid } from "../features/precheck/PrecheckFieldGrid";
import { PrecheckIssueSummary } from "../features/precheck/PrecheckIssueSummary";
import { PrecheckLowerPanels } from "../features/precheck/PrecheckLowerPanels";
import { PrecheckMessages } from "../features/precheck/PrecheckMessages";
import { PrecheckSampleTable } from "../features/precheck/PrecheckSampleTable";
import {
  buildConfirmationBlockedReason,
  copySampleRow,
  deleteSampleRow,
  editableValue,
  fallbackValue,
  fieldsWithLookupOptions,
  focusSampleRow,
  formatStatus,
  issueLevelMap,
  normalizedSampleRows,
  preferredCaseId,
  updateSampleRow
} from "../features/precheck/precheckReviewSelectors";
import { PrecheckSourceCheck } from "../features/precheck/PrecheckSourceCheck";
import { PrecheckStatePanel } from "../features/precheck/PrecheckStatePanel";
import { PrecheckStepper } from "../features/precheck/PrecheckStepper";
import "../intake-case-review.css";

type IntakeCaseReviewPageProps = {
  packageId: string;
  initialCaseId?: string | null;
  onBack: (snapshot?: PrecheckBackSnapshot) => void;
  onProjectConfirmed?: () => void;
};

export type PrecheckBackSnapshot = {
  caseId: string;
  selectedFormAssetId: string | null;
};

export function IntakeCaseReviewPage({
  packageId,
  initialCaseId,
  onBack,
  onProjectConfirmed
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
  const [sampleRows, setSampleRows] = useState<PrecheckSampleRow[]>([emptyPrecheckSampleRow()]);
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
    () => fieldsWithLookupOptions(PRECHECK_PROJECT_FIELDS, lookupOptions),
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
      onProjectConfirmed?.();
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

      {loading ? <PrecheckStatePanel title="Loading Precheck" text="Loading source context, selected case, and confirmation blockers." /> : null}
      {loadError ? <PrecheckStatePanel tone="danger" title="Precheck cannot be loaded" text={loadError} /> : null}
      {lookupError ? <PrecheckStatePanel tone="danger" title="Lookup options cannot be loaded" text={lookupError} /> : null}
      {!loading && review && review.cases.length === 0 ? (
        <PrecheckStatePanel title="No review case exists" text="Create a review case from the package assets before Precheck." />
      ) : null}

      {!loading && review && activeCase ? (
        <>
          <PrecheckSourceCheck review={review} activeCase={activeCase} />
          <PrecheckIssueSummary issues={activeCase.precheck_issues} />
          <section className="precheck-card key-information-card">
            <h3>Key Information Edit & Confirm</h3>
            <PrecheckFieldGrid
              disabled={savingFields || Boolean(activeCase.confirmed_project_id)}
              fields={projectFields}
              issueLevelByField={issueLevelByField}
              sourceFields={activeCase.fields}
              values={fieldValues}
              onChange={(key, value) => {
                setFieldValues((current) => ({ ...current, [key]: value }));
                setFieldSaveMessage(null);
                setFieldSaveError(null);
              }}
            />
            <PrecheckSampleTable
              disabled={savingFields || Boolean(activeCase.confirmed_project_id)}
              rows={sampleRows}
              onAdd={() => {
                setSampleRows((current) => [...current, emptyPrecheckSampleRow()]);
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
            <PrecheckLowerPanels
              additionalInformation={fieldValues.additional_information ?? fallbackValue("additional_information", activeCase.fields)}
              confidential={fieldValues.confidential ?? fallbackValue("confidential", activeCase.fields)}
              requestedTesting={fieldValues.requested_testing ?? fallbackValue("requested_testing", activeCase.fields)}
              subcontract={fieldValues.subcontract ?? fallbackValue("subcontract", activeCase.fields)}
            />
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
            <button
              className="secondary-button precheck-back-button"
              type="button"
              onClick={() => onBack({
                caseId: activeCase.case_id,
                selectedFormAssetId: activeCase.selected_form_asset_id ?? null
              })}
            >
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

          <PrecheckMessages
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
