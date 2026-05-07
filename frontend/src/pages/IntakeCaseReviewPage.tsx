import { type ReactElement, useEffect, useMemo, useRef, useState } from "react";

import {
  type ConfirmIntakeCase,
  type IntakeCaseReview,
  type IntakePrecheckLookupOptions,
  confirmIntakeCase,
  discardUnsavedProjectCreationDraft,
  getIntakeCaseReview,
  getIntakePrecheckLookupOptions,
  saveProjectCreationDraft,
  updateIntakeCaseReviewFields
} from "../api/client";
import { UiIcon } from "../components/common/UiIcon";
import { NewProjectWorkflowHeader } from "../components/workflow/NewProjectWorkflow";
import {
  emptyPrecheckSampleRow,
  emptyPrecheckRequestedTestingRow,
  PRECHECK_PROJECT_FIELDS,
  type PrecheckSampleRow,
  type PrecheckRequestedTestingRow
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
  issueLevelMap,
  normalizedSampleRows,
  normalizedRequestedTestingRows,
  preferredCaseId,
  requestedTestingText,
  updateSampleRow
} from "../features/precheck/precheckReviewSelectors";
import { PrecheckSourceCheck } from "../features/precheck/PrecheckSourceCheck";
import { PrecheckStatePanel } from "../features/precheck/PrecheckStatePanel";
import "../intake-case-review.css";

type IntakeCaseReviewPageProps = {
  packageId: string;
  initialCaseId?: string | null;
  onExit: () => void;
  onProjectConfirmed?: () => void;
};

export function IntakeCaseReviewPage({
  packageId,
  initialCaseId,
  onExit,
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
  const [requestedTestingRows, setRequestedTestingRows] = useState<PrecheckRequestedTestingRow[]>([
    emptyPrecheckRequestedTestingRow()
  ]);
  const [lookupOptions, setLookupOptions] = useState<IntakePrecheckLookupOptions | null>(null);
  const [lookupError, setLookupError] = useState<string | null>(null);
  const [savingFields, setSavingFields] = useState(false);
  const [fieldSaveError, setFieldSaveError] = useState<string | null>(null);
  const [fieldSaveMessage, setFieldSaveMessage] = useState<string | null>(null);
  const [exiting, setExiting] = useState<"save" | "discard" | null>(null);
  const [confirmDiscard, setConfirmDiscard] = useState(false);
  const fieldValuesRef = useRef<Record<string, string>>({});
  const sampleRowsRef = useRef<PrecheckSampleRow[]>([]);
  const requestedTestingRowsRef = useRef<PrecheckRequestedTestingRow[]>([]);

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
  const requestedTestingRowsChanged = activeCase
    ? JSON.stringify(requestedTestingRows) !== JSON.stringify(normalizedRequestedTestingRows(activeCase.requested_testing_rows))
    : false;
  const draftChanged = fieldValuesChanged || sampleRowsChanged || requestedTestingRowsChanged;
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
      fieldValuesRef.current = {};
      sampleRowsRef.current = [];
      requestedTestingRowsRef.current = [];
      return;
    }
    const nextFieldValues = Object.fromEntries(activeCase.fields.map((field) => [field.key, editableValue(field.value)]));
    setFieldValues(nextFieldValues);
    fieldValuesRef.current = nextFieldValues;
    const nextSampleRows = normalizedSampleRows(activeCase.sample_rows);
    setSampleRows(nextSampleRows);
    sampleRowsRef.current = nextSampleRows;
    const nextRequestedTestingRows = normalizedRequestedTestingRows(activeCase.requested_testing_rows);
    setRequestedTestingRows(nextRequestedTestingRows);
    requestedTestingRowsRef.current = nextRequestedTestingRows;
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
    const saveCaseId = activeCase.case_id;
    try {
      await updateIntakeCaseReviewFields(saveCaseId, {
        fields: {
          ...fieldValuesRef.current,
          requested_testing: requestedTestingText(requestedTestingRowsRef.current)
        },
        sample_rows: sampleRowsRef.current,
        requested_testing_rows: requestedTestingRowsRef.current
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

  async function saveFieldCorrectionsForExit(): Promise<boolean> {
    if (!activeCase || !draftChanged) {
      return true;
    }
    setFieldSaveError(null);
    setConfirmError(null);
    try {
      await updateIntakeCaseReviewFields(activeCase.case_id, {
        fields: {
          ...fieldValuesRef.current,
          requested_testing: requestedTestingText(requestedTestingRowsRef.current)
        },
        sample_rows: sampleRowsRef.current,
        requested_testing_rows: requestedTestingRowsRef.current
      });
      return true;
    } catch (error) {
      setFieldSaveError(
        error instanceof Error ? error.message : "Unable to save field corrections before exit."
      );
      return false;
    }
  }

  async function handleSaveDraftAndExit(): Promise<void> {
    if (!activeCase) {
      return;
    }
    setExiting("save");
    setFieldSaveError(null);
    const fieldsSaved = await saveFieldCorrectionsForExit();
    if (!fieldsSaved) {
      setExiting(null);
      return;
    }
    try {
      await saveProjectCreationDraft(packageId);
      onExit();
    } catch (error) {
      setFieldSaveError(
        error instanceof Error ? error.message : "Unable to save this creation draft."
      );
    } finally {
      setExiting(null);
    }
  }

  async function handleDiscardAndExit(): Promise<void> {
    if (!activeCase) {
      return;
    }
    if (!confirmDiscard) {
      setConfirmDiscard(true);
      return;
    }
    setExiting("discard");
    setFieldSaveError(null);
    try {
      await discardUnsavedProjectCreationDraft(packageId);
      onExit();
    } catch (error) {
      setFieldSaveError(
        error instanceof Error ? error.message : "Unable to discard this unsaved creation session."
      );
    } finally {
      setExiting(null);
    }
  }

  return (
    <section className="precheck-workflow">
      <NewProjectWorkflowHeader currentStep="precheck" />

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
            <h3 className="ui-panel-title">Key Information Edit & Confirm</h3>
            <PrecheckFieldGrid
              disabled={savingFields || Boolean(activeCase.confirmed_project_id)}
              fields={projectFields}
              issueLevelByField={issueLevelByField}
              sourceFields={activeCase.fields}
              values={fieldValues}
              onChange={(key, value) => {
                setFieldValues((current) => {
                  const next = { ...current, [key]: value };
                  fieldValuesRef.current = next;
                  return next;
                });
                setFieldSaveMessage(null);
                setFieldSaveError(null);
              }}
            />
            <PrecheckSampleTable
              disabled={savingFields || Boolean(activeCase.confirmed_project_id)}
              rows={sampleRows}
              onAdd={() => {
                setSampleRows((current) => {
                  const next = [...current, emptyPrecheckSampleRow()];
                  sampleRowsRef.current = next;
                  return next;
                });
                setFieldSaveMessage(null);
              }}
              onChange={(rowIndex, key, value) => {
                setSampleRows((current) => {
                  const next = updateSampleRow(current, rowIndex, key, value);
                  sampleRowsRef.current = next;
                  return next;
                });
                setFieldSaveMessage(null);
                setFieldSaveError(null);
              }}
              onCopy={(rowIndex) => {
                setSampleRows((current) => {
                  const next = copySampleRow(current, rowIndex);
                  sampleRowsRef.current = next;
                  return next;
                });
                setFieldSaveMessage(null);
              }}
              onDelete={(rowIndex) => {
                setSampleRows((current) => {
                  const next = deleteSampleRow(current, rowIndex);
                  sampleRowsRef.current = next;
                  return next;
                });
                setFieldSaveMessage(null);
              }}
            />
            <PrecheckLowerPanels
              additionalInformation={fieldValues.additional_information ?? fallbackValue("additional_information", activeCase.fields)}
              confidential={fieldValues.confidential ?? fallbackValue("confidential", activeCase.fields)}
              disabled={savingFields || Boolean(activeCase.confirmed_project_id)}
              requestedTestingRows={requestedTestingRows}
              subcontract={fieldValues.subcontract ?? fallbackValue("subcontract", activeCase.fields)}
              onAdditionalInformationChange={(value) => {
                setFieldValues((current) => {
                  const next = { ...current, additional_information: value };
                  fieldValuesRef.current = next;
                  return next;
                });
                setFieldSaveMessage(null);
                setFieldSaveError(null);
              }}
              onConfidentialChange={(value) => {
                setFieldValues((current) => {
                  const next = { ...current, confidential: value };
                  fieldValuesRef.current = next;
                  return next;
                });
                setFieldSaveMessage(null);
                setFieldSaveError(null);
              }}
              onRequestedTestingRowAdd={() => {
                setRequestedTestingRows((current) => {
                  const next = [...current, emptyPrecheckRequestedTestingRow()];
                  requestedTestingRowsRef.current = next;
                  return next;
                });
                setFieldSaveMessage(null);
              }}
              onRequestedTestingRowChange={(rowIndex, key, value) => {
                setRequestedTestingRows((current) => {
                  const next = current.map((row, index) => (index === rowIndex ? { ...row, [key]: value } : row));
                  requestedTestingRowsRef.current = next;
                  return next;
                });
                setFieldSaveMessage(null);
                setFieldSaveError(null);
              }}
              onRequestedTestingRowCopy={(rowIndex) => {
                setRequestedTestingRows((current) => {
                  const copied = { ...(current[rowIndex] ?? emptyPrecheckRequestedTestingRow()) };
                  const next = [...current.slice(0, rowIndex + 1), copied, ...current.slice(rowIndex + 1)];
                  requestedTestingRowsRef.current = next;
                  return next;
                });
                setFieldSaveMessage(null);
              }}
              onRequestedTestingRowDelete={(rowIndex) => {
                if (requestedTestingRows.length <= 1) return;
                setRequestedTestingRows((current) => {
                  const next = current.filter((_, index) => index !== rowIndex);
                  requestedTestingRowsRef.current = next;
                  return next;
                });
                setFieldSaveMessage(null);
              }}
              onSubcontractChange={(value) => {
                setFieldValues((current) => {
                  const next = { ...current, subcontract: value };
                  fieldValuesRef.current = next;
                  return next;
                });
                setFieldSaveMessage(null);
                setFieldSaveError(null);
              }}
            />
          </section>

          <footer className="precheck-footer">
            <button
              className="new-project-secondary-action ui-secondary-action"
              disabled={Boolean(exiting)}
              type="button"
              onClick={() => void handleSaveDraftAndExit()}
            >
              {exiting === "save" ? "Saving..." : "Save draft and exit"}
            </button>
            <button
              className="new-project-secondary-action ui-secondary-action"
              disabled={Boolean(exiting)}
              type="button"
              onClick={() => void handleDiscardAndExit()}
            >
              {exiting === "discard"
                ? "Discarding..."
                : confirmDiscard
                  ? "Confirm discard"
                  : "Exit without saving"}
            </button>
            <div className="footer-source-status">
              <UiIcon name="clock" />
              <span>
                {confirmDiscard
                  ? "Discard removes ConnLab imported copies for this unsaved session."
                  : "Source: Intake email / application form verified"}
              </span>
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
              className="new-project-secondary-action ui-secondary-action"
              disabled={!draftChanged || savingFields || Boolean(activeCase.confirmed_project_id)}
              type="button"
              onClick={() => void handleSaveFields()}
            >
              <span className="sr-only">Save corrections</span>
              {savingFields ? "Saving" : "Save Draft"}
            </button>
            <button className="new-project-primary-action precheck-confirm-button ui-primary-action" disabled={!canConfirm} type="button" onClick={() => void handleConfirm()}>
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
