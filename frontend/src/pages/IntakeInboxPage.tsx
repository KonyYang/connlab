import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ChangeEvent,
  type ReactElement
} from "react";
import {
  ApiRequestError,
  ensureNewProjectApplicationDraft,
  getIntakeCaseReview,
  getIntakePackageDetail,
  getNewProjectCompletionOptions,
  getIntakePrecheckLookupOptions,
  importDirectWordApplicationForm,
  importMsgPackage,
  downloadIntakeAsset,
  selectIntakeApplicationForm,
  updateIntakeCaseReviewFields,
  uploadEmailPackageApplicationForm,
  type DraftDuplicateAction,
  type DraftDuplicateCheck,
  type IntakeCaseReview,
  type IntakePackageDetail,
  type IntakePackageImport,
  type IntakePrecheckLookupOptions,
  type IntakeAsset,
  type NewProjectCompletionOptions
} from "../api/client";
import { NewProjectApplicationEditor } from "../features/new-project/NewProjectApplicationEditor";
import { buildNewProjectRequiredState } from "../features/new-project/newProjectRequiredState";
import {
  NewProjectSetupConfirmationPanel,
  type NewProjectSetupConfirmationValues
} from "../features/new-project/NewProjectSetupConfirmationPanel";
import { useNewProjectCompletion } from "../features/new-project/useNewProjectCompletion";
import { AttachmentList } from "../features/intake/AttachmentList";
import { IntakeSourcePanel } from "../features/intake/IntakeSourcePanel";
import {
  EMPTY_INTAKE_SESSION,
  type IntakeSessionState
} from "../features/intake/intakeSession";
import {
  buildAttachmentViewModels,
  type IntakeAttachmentViewModel,
  visibleIntakeAttachments
} from "../features/intake/intakeSelectors";
import {
  emptyPrecheckRequestedTestingRow,
  emptyPrecheckSampleRow,
  PRECHECK_PROJECT_FIELDS,
  type PrecheckRequestedTestingRow,
  type PrecheckSampleRow
} from "../features/precheck/precheckFieldConfig";
import {
  editableValue,
  fieldsWithLookupOptions,
  normalizedRequestedTestingRows,
  normalizedSampleRows,
  preferredCaseId,
  requestedTestingText
} from "../features/precheck/precheckReviewSelectors";
import "../intake-case-review.css";
import "../intake-inbox.css";

type IntakeInboxPageProps = {
  session: IntakeSessionState;
  onSessionChange: (session: IntakeSessionState) => void;
  onExit: () => void;
  onProjectCreated: (projectId: string) => void;
};

type DuplicateImportState = {
  check: DraftDuplicateCheck;
  packageId: string;
  asset?: IntakeAsset | null;
};

export function IntakeInboxPage({
  session,
  onSessionChange,
  onProjectCreated
}: IntakeInboxPageProps): ReactElement {
  const msgInputRef = useRef<HTMLInputElement | null>(null);
  const wordInputRef = useRef<HTMLInputElement | null>(null);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [duplicateDraft, setDuplicateDraft] = useState<DuplicateImportState | null>(null);
  const [resolvingDuplicateAction, setResolvingDuplicateAction] = useState<string | null>(null);
  const [review, setReview] = useState<IntakeCaseReview | null>(null);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [editorLoading, setEditorLoading] = useState(false);
  const [editorError, setEditorError] = useState<string | null>(null);
  const [lookupOptions, setLookupOptions] = useState<IntakePrecheckLookupOptions | null>(null);
  const [lookupError, setLookupError] = useState<string | null>(null);
  const [fieldValues, setFieldValues] = useState<Record<string, string>>({});
  const [sampleRows, setSampleRows] = useState<PrecheckSampleRow[]>([emptyPrecheckSampleRow()]);
  const [requestedTestingRows, setRequestedTestingRows] = useState<PrecheckRequestedTestingRow[]>([
    emptyPrecheckRequestedTestingRow()
  ]);
  const [autoSaveError, setAutoSaveError] = useState<string | null>(null);
  const [importingAssetId, setImportingAssetId] = useState<string | null>(null);
  const [importMessage, setImportMessage] = useState<string | null>(null);
  const [importVersion, setImportVersion] = useState(0);
  const [setupOptions, setSetupOptions] = useState<NewProjectCompletionOptions | null>(null);
  const [setupValues, setSetupValues] = useState<NewProjectSetupConfirmationValues>({
    ltrMode: "auto",
    specifiedLtrNumber: "",
    testItem: "",
    sampleDescription: "",
    location: "",
    testTypeInSheet: "",
    projectLeader: ""
  });
  const [completionSetupError, setCompletionSetupError] = useState<string | null>(null);
  const fieldValuesRef = useRef<Record<string, string>>({});
  const sampleRowsRef = useRef<PrecheckSampleRow[]>([]);
  const requestedTestingRowsRef = useRef<PrecheckRequestedTestingRow[]>([]);
  const { packageImport, selectedAssetId, sourceMode, directWordName } = session;
  const visibleAttachmentAssets = useMemo(
    () => visibleIntakeAttachments(packageImport),
    [packageImport]
  );
  const hasSelectableApplicationForms = useMemo(
    () => visibleAttachmentAssets.some((asset) => asset.extension.toLowerCase() === ".docx"),
    [visibleAttachmentAssets]
  );
  const attachmentViewModels = useMemo(
    () => buildAttachmentViewModels(visibleAttachmentAssets, selectedAssetId),
    [selectedAssetId, visibleAttachmentAssets]
  );
  const activeCase = useMemo(() => {
    if (!review) {
      return null;
    }
    return review.cases.find((item) => item.case_id === selectedCaseId) ?? review.cases[0] ?? null;
  }, [review, selectedCaseId]);
  const projectFields = useMemo(
    () => fieldsWithLookupOptions(PRECHECK_PROJECT_FIELDS, lookupOptions),
    [lookupOptions]
  );
  const requiredState = useMemo(
    () =>
      buildNewProjectRequiredState(
        activeCase?.fields ?? [],
        fieldValues,
        sampleRows,
        requestedTestingRows
      ),
    [activeCase, fieldValues, requestedTestingRows, sampleRows]
  );
  const setupMissingKeys = useMemo(() => {
    const missing = new Set<string>();
    if (setupValues.ltrMode === "specified" && !setupValues.specifiedLtrNumber.trim()) {
      missing.add("specified_ltr_number");
    }
    if (!setupValues.testItem.trim()) missing.add("test_item");
    if (!setupValues.sampleDescription.trim()) missing.add("sample_description");
    if (!setupValues.location.trim()) missing.add("location");
    if (!setupValues.testTypeInSheet.trim()) missing.add("test_type_in_sheet");
    if (!setupValues.projectLeader.trim()) missing.add("project_leader");
    return missing;
  }, [setupValues]);
  const completionText = useMemo(() => {
    const missingCount = requiredState.missingCount + setupMissingKeys.size;
    return missingCount === 0
      ? "Required project information complete"
      : `${missingCount} required fields remaining`;
  }, [requiredState.missingCount, setupMissingKeys.size]);
  const {
    complete: completeProject,
    completionError,
    completionLoading,
    completionResult
  } = useNewProjectCompletion({
    activeCase,
    resetKey: `${packageImport?.package_id ?? ""}:${selectedAssetId ?? ""}`,
    setupValues,
    onCompleted: (projectId) => {
      onSessionChange(EMPTY_INTAKE_SESSION);
      onProjectCreated(projectId);
    }
  });
  const displayedCompletionError = completionError ?? completionSetupError;
  const completionDisabled =
    editorLoading
    || completionLoading
    || Boolean(activeCase?.confirmed_project_id)
    || requiredState.missingCount > 0
    || setupMissingKeys.size > 0;
  const importedFormDisplayName = useMemo(() => {
    if (!packageImport) {
      return null;
    }
    if (importMessage) {
      return importMessage;
    }
    if (!session.selectedWordAssetId) {
      return null;
    }
    const selectedFormAsset = packageImport.assets.find(
      (asset) => asset.asset_id === session.selectedWordAssetId
    );
    return selectedFormAsset?.original_name ?? null;
  }, [importMessage, packageImport, session.selectedWordAssetId]);
  const draftChanged = activeCase
    ? activeCase.fields.some((field) => fieldValues[field.key] !== editableValue(field.value))
      || JSON.stringify(sampleRows) !== JSON.stringify(normalizedSampleRows(activeCase.sample_rows))
      || JSON.stringify(requestedTestingRows)
        !== JSON.stringify(normalizedRequestedTestingRows(activeCase.requested_testing_rows))
    : false;
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

  useEffect(() => {
    let active = true;
    async function loadCompletionOptions(): Promise<void> {
      try {
        const options = await getNewProjectCompletionOptions();
        if (!active) {
          return;
        }
        setSetupOptions(options);
        setSetupValues((current) => ({
          ...current,
          projectLeader: current.projectLeader || options.default_project_leader
        }));
      } catch (error) {
        if (active) {
          setCompletionSetupError(
            error instanceof Error ? error.message : "Unable to load project setup options."
          );
        }
      }
    }
    void loadCompletionOptions();
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const manufacturingSite = fieldValues.manufacturing_site?.trim();
    if (!manufacturingSite || !setupOptions || setupValues.location) {
      return;
    }
    const matched = setupOptions.location_options.find(
      (option) => option.toLowerCase() === manufacturingSite.toLowerCase()
    );
    if (matched) {
      setSetupValues((current) => ({ ...current, location: matched }));
    }
  }, [fieldValues.manufacturing_site, setupOptions, setupValues.location]);

  useEffect(() => {
    if (!packageImport) {
      setReview(null);
      setSelectedCaseId(null);
      return;
    }
    const packageId = packageImport.package_id;
    if (session.selectedPrecheckCaseId) {
      let cancelled = false;
      async function loadSelectedReview(): Promise<void> {
        setEditorLoading(true);
        setEditorError(null);
        try {
          const nextReview = await getIntakeCaseReview(packageId);
          if (!cancelled) {
            setReview(nextReview);
            setSelectedCaseId((current) =>
              preferredCaseId(nextReview, session.selectedPrecheckCaseId, current)
            );
          }
        } catch (error) {
          if (!cancelled) {
            setReview(null);
            setEditorError(
              error instanceof Error ? error.message : "Unable to load the selected application draft."
            );
          }
        } finally {
          if (!cancelled) setEditorLoading(false);
        }
      }
      void loadSelectedReview();
      return () => {
        cancelled = true;
      };
    }
    const waitsForApplicationFormSelection =
      packageImport.source_type === "outlook_msg"
      && hasSelectableApplicationForms
      && !session.selectedWordAssetId
      && !session.selectedPrecheckCaseId;
    if (waitsForApplicationFormSelection) {
      setReview(null);
      setSelectedCaseId(null);
      setEditorLoading(false);
      setEditorError(null);
      return;
    }
    let cancelled = false;
    async function prepareEditor(): Promise<void> {
      setEditorLoading(true);
      setEditorError(null);
      try {
        const draft = await ensureNewProjectApplicationDraft(packageId);
        const nextReview = await getIntakeCaseReview(packageId);
        if (!cancelled) {
          setReview(nextReview);
          setSelectedCaseId((current) =>
            preferredCaseId(nextReview, session.selectedPrecheckCaseId ?? draft.case_id, current)
          );
          onSessionChange({
            ...session,
            selectedPrecheckCaseId: draft.case_id,
            selectedWordAssetId: draft.selected_form_asset_id ?? session.selectedWordAssetId
          });
        }
      } catch (error) {
        const duplicate = draftDuplicateConflictFromError(error);
        if (!cancelled) {
          if (duplicate) {
            setDuplicateDraft({ check: duplicate, packageId });
            setReview(null);
            setEditorError(null);
          } else {
            setReview(null);
            setEditorError(
              error instanceof Error ? error.message : "Unable to prepare the application editor."
            );
          }
        }
      } finally {
        if (!cancelled) setEditorLoading(false);
      }
    }
    void prepareEditor();
    return () => {
      cancelled = true;
    };
  }, [
    hasSelectableApplicationForms,
    packageImport?.package_id,
    packageImport?.source_type,
    session.selectedPrecheckCaseId,
    session.selectedWordAssetId
  ]);

  useEffect(() => {
    if (!activeCase) {
      setFieldValues({});
      fieldValuesRef.current = {};
      sampleRowsRef.current = [];
      requestedTestingRowsRef.current = [];
      return;
    }
    const nextFieldValues = Object.fromEntries(
      activeCase.fields.map((field) => [field.key, editableValue(field.value)])
    );
    const nextSampleRows = normalizedSampleRows(activeCase.sample_rows);
    const nextRequestedTestingRows = normalizedRequestedTestingRows(activeCase.requested_testing_rows);
    setFieldValues(nextFieldValues);
    setSampleRows(nextSampleRows);
    setRequestedTestingRows(nextRequestedTestingRows);
    fieldValuesRef.current = nextFieldValues;
    sampleRowsRef.current = nextSampleRows;
    requestedTestingRowsRef.current = nextRequestedTestingRows;
    setAutoSaveError(null);
  }, [activeCase?.case_id, importVersion]);

  useEffect(() => {
    if (!activeCase || activeCase.base_editing_frozen || !draftChanged) {
      return;
    }
    setAutoSaveError(null);
    const timeoutId = window.setTimeout(() => {
      updateIntakeCaseReviewFields(activeCase.case_id, {
        fields: {
          ...fieldValuesRef.current,
          requested_testing: requestedTestingText(requestedTestingRowsRef.current)
        },
        sample_rows: sampleRowsRef.current,
        requested_testing_rows: requestedTestingRowsRef.current
      })
        .then((updatedCase) => {
          setReview((current) =>
            current
              ? {
                  ...current,
                  cases: current.cases.map((item) =>
                    item.case_id === updatedCase.case_id ? updatedCase : item
                  )
                }
              : current
          );
        })
        .catch((error: unknown) => {
          setAutoSaveError(error instanceof Error ? error.message : "Unable to save draft edits.");
        });
    }, 700);
    return () => window.clearTimeout(timeoutId);
  }, [activeCase, draftChanged, fieldValues, requestedTestingRows, sampleRows]);

  async function handleMsgFileChange(event: ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setImporting(true);
    setImportError(null);
    setDuplicateDraft(null);
    setImportMessage(null);
    try {
      const imported = await importMsgPackage(file);
      applyImportedMsgPackage(imported);
    } catch (error) {
      onSessionChange(EMPTY_INTAKE_SESSION);
      setImportError(error instanceof Error ? error.message : "Import failed.");
    } finally {
      setImporting(false);
    }
  }

  async function handleResolveDuplicateDraft(action: DraftDuplicateAction): Promise<void> {
    if (!duplicateDraft) {
      return;
    }
    setResolvingDuplicateAction(action);
    setImportError(null);
    try {
      const resolution = { action, caseId: duplicateDraft.check.existing_case_id };
      if (duplicateDraft.asset) {
        const selection = await selectIntakeApplicationForm(
          duplicateDraft.packageId,
          duplicateDraft.asset.asset_id,
          true,
          resolution
        );
        await applySelectedDraft(selection, duplicateDraft.asset.original_name);
      } else {
        const draft = await ensureNewProjectApplicationDraft(duplicateDraft.packageId, resolution);
        await applyPreparedDraft(draft);
      }
      setDuplicateDraft(null);
    } catch (error) {
      const duplicate = draftDuplicateConflictFromError(error);
      if (duplicate) {
        setDuplicateDraft({ ...duplicateDraft, check: duplicate });
      }
      setImportError(error instanceof Error ? error.message : "Import failed.");
    } finally {
      setResolvingDuplicateAction(null);
    }
  }

  function applyImportedMsgPackage(imported: IntakePackageImport): void {
    onSessionChange({
      packageImport: imported,
      selectedAssetId: null,
      selectedWordAssetId: null,
      selectedPrecheckCaseId: null,
      sourceMode: "msg",
      directWordName: null
    });
  }

  async function applyPreparedDraft(draft: {
    package_id: string;
    case_id: string;
    selected_form_asset_id?: string | null;
  }): Promise<void> {
    const detail = await getIntakePackageDetail(draft.package_id);
    const refreshed = packageDetailToImport(detail);
    const nextReview = await getIntakeCaseReview(draft.package_id);
    setReview(nextReview);
    setSelectedCaseId(draft.case_id);
    onSessionChange({
      packageImport: refreshed,
      selectedAssetId: draft.selected_form_asset_id ?? refreshed.assets[0]?.asset_id ?? null,
      selectedWordAssetId: draft.selected_form_asset_id ?? null,
      selectedPrecheckCaseId: draft.case_id,
      sourceMode: refreshed.source_type === "outlook_msg" ? "msg" : "word",
      directWordName: null
    });
  }

  async function applySelectedDraft(
    selection: { package_id: string; case_id: string; selected_form_asset_id: string },
    importMessageText: string
  ): Promise<void> {
    const detail = await getIntakePackageDetail(selection.package_id);
    const refreshed = packageDetailToImport(detail);
    const nextReview = await getIntakeCaseReview(selection.package_id);
    setReview(nextReview);
    setSelectedCaseId(selection.case_id);
    setImportMessage(importMessageText);
    setImportVersion((current) => current + 1);
    onSessionChange({
      packageImport: refreshed,
      selectedAssetId: selection.selected_form_asset_id,
      selectedWordAssetId: selection.selected_form_asset_id,
      selectedPrecheckCaseId: selection.case_id,
      sourceMode: refreshed.source_type === "outlook_msg" ? "msg" : "word",
      directWordName: null
    });
  }

  async function handleDirectWordChange(event: ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    setImporting(true);
    setImportError(null);
    setDuplicateDraft(null);
    setImportMessage(null);
    try {
      if (packageImport?.source_type === "outlook_msg") {
        const selection = await uploadEmailPackageApplicationForm(packageImport.package_id, file);
        const detail = await getIntakePackageDetail(packageImport.package_id);
        const refreshed = packageDetailToImport(detail);
        onSessionChange({
          packageImport: refreshed,
          selectedAssetId: selection.selected_form_asset_id,
          selectedWordAssetId: null,
          selectedPrecheckCaseId: session.selectedPrecheckCaseId,
          sourceMode: "msg",
          directWordName: null
        });
      } else {
        const imported = await importDirectWordApplicationForm(file);
        onSessionChange({
          packageImport: imported,
          selectedAssetId: imported.assets[0]?.asset_id ?? null,
          selectedWordAssetId: null,
          selectedPrecheckCaseId: null,
          sourceMode: "word",
          directWordName: file.name
        });
      }
    } catch (error) {
      if (!packageImport) onSessionChange(EMPTY_INTAKE_SESSION);
      setImportError(error instanceof Error ? error.message : "Application form upload failed.");
    } finally {
      setImporting(false);
    }
  }

  async function handleImportApplicationForm(asset: IntakeAsset): Promise<void> {
    if (!packageImport) {
      return;
    }
    setImportingAssetId(asset.asset_id);
    setImportError(null);
    setImportMessage(null);
    try {
      const selection = await selectIntakeApplicationForm(packageImport.package_id, asset.asset_id, true);
      await applySelectedDraft(selection, asset.original_name);
    } catch (error) {
      const duplicate = draftDuplicateConflictFromError(error);
      if (duplicate) {
        setDuplicateDraft({ check: duplicate, packageId: packageImport.package_id, asset });
        setImportError(null);
      } else {
        setImportError(error instanceof Error ? error.message : "Application form import failed.");
      }
    } finally {
      setImportingAssetId(null);
    }
  }

  async function handleOpenAttachment(attachment: IntakeAttachmentViewModel): Promise<void> {
    try {
      const blob = await downloadIntakeAsset(attachment.asset.asset_id);
      const objectUrl = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = objectUrl;
      link.download = attachment.asset.original_name;
      link.rel = "noopener";
      link.style.display = "none";
      document.body.append(link);
      link.click();
      link.remove();
      window.setTimeout(() => window.URL.revokeObjectURL(objectUrl), 0);
    } catch (error) {
      setImportError(error instanceof Error ? error.message : "Attachment download failed.");
    }
  }

  return (
    <section className="intake-workflow new-project-single-page">
      <div className="new-project-single-grid">
        <aside className="intake-left-stack">
          <IntakeSourcePanel
            directWordName={directWordName}
            importError={importError}
            importing={importing}
            msgInputRef={msgInputRef}
            packageImport={packageImport}
            sourceMode={sourceMode}
            wordInputRef={wordInputRef}
            onDirectWordChange={(event) => void handleDirectWordChange(event)}
            onMsgFileChange={(event) => void handleMsgFileChange(event)}
            onSelectSourceMode={(mode) => onSessionChange({ ...session, sourceMode: mode })}
          />
          <AttachmentList
            attachments={attachmentViewModels}
            duplicateDraft={duplicateDraft?.check ?? null}
            importingAssetId={importingAssetId}
            packageLoaded={Boolean(packageImport)}
            resolvingDuplicateAction={resolvingDuplicateAction}
            onDuplicateAction={(action) => void handleResolveDuplicateDraft(action)}
            onImport={(attachment) => void handleImportApplicationForm(attachment.asset)}
            onOpen={(attachment) => void handleOpenAttachment(attachment)}
            onSelect={(attachment) => {
              setDuplicateDraft(null);
              onSessionChange({
                ...session,
                selectedAssetId: attachment.asset.asset_id
              });
            }}
          />
          <NewProjectSetupConfirmationPanel
            disabled={completionLoading || editorLoading || Boolean(activeCase?.confirmed_project_id)}
            locationOptions={setupOptions?.location_options ?? []}
            missingKeys={setupMissingKeys}
            testTypeInSheetOptions={setupOptions?.test_type_in_sheet_options ?? []}
            values={setupValues}
              onChange={(values) => {
                setSetupValues(values);
                setCompletionSetupError(null);
              }}
          />
        </aside>

        <main className="new-project-editor-stack">
          {editorLoading ? (
            <section className="new-project-editor-panel new-project-editor-empty">
              <strong>Preparing application editor</strong>
              <span>Creating the durable draft for this request package.</span>
            </section>
          ) : null}
          {editorError ? <p className="intake-error">{editorError}</p> : null}
          {packageImport && activeCase != null ? (
            <NewProjectApplicationEditor
              activeCase={activeCase}
              autoSaveError={autoSaveError}
              completionDisabled={completionDisabled}
              disabled={
                editorLoading ||
                Boolean(activeCase.confirmed_project_id) ||
                Boolean(activeCase.base_editing_frozen)
              }
              fieldValues={fieldValues}
              importMessage={importedFormDisplayName}
              completionError={displayedCompletionError}
              completionLoading={completionLoading}
              completionResult={completionResult}
              completionText={completionText}
              lookupError={lookupError}
              projectFields={projectFields}
              requestedTestingRows={requestedTestingRows}
              requiredState={requiredState}
              sampleRows={sampleRows}
              sourceFields={activeCase.fields}
              onComplete={() => void completeProject()}
              onFieldValuesChange={(values) => {
                setFieldValues(values);
                fieldValuesRef.current = values;
              }}
              onRequestedTestingRowsChange={(rows) => {
                setRequestedTestingRows(rows);
                requestedTestingRowsRef.current = rows;
              }}
              onSampleRowsChange={(rows) => {
                setSampleRows(rows);
                sampleRowsRef.current = rows;
              }}
            />
          ) : !packageImport ? (
            <section className="new-project-editor-panel new-project-editor-empty">
              <strong>Import a request email to start</strong>
            </section>
          ) : null}
        </main>
      </div>

      <div className="step-footer new-project-single-footer">
        <span className="step-footer-guidance">
          {packageImport
            ? "Draft changes save automatically while you edit this package."
            : "Import the request source before editing application information."}
        </span>
        <span aria-hidden="true" />
      </div>
    </section>
  );
}

function draftDuplicateConflictFromError(error: unknown): DraftDuplicateCheck | null {
  if (
    !(error instanceof ApiRequestError) ||
    error.status !== 409 ||
    !error.detail ||
    typeof error.detail !== "object" ||
    !("classification" in error.detail) ||
    !("allowed_actions" in error.detail)
  ) {
    return null;
  }
  return error.detail as DraftDuplicateCheck;
}

function packageDetailToImport(detail: IntakePackageDetail): IntakePackageImport {
  return {
    package_id: detail.package_id,
    source_type: detail.source_type,
    package_status: detail.package_status,
    source_original_name: detail.source_original_name,
    subject: detail.subject,
    sender_name: detail.sender_name,
    sender_email: detail.sender_email,
    received_at: detail.received_at,
    asset_count: detail.asset_count,
    candidate_count: detail.candidate_count,
    next_action: detail.next_action,
    assets: detail.assets
  };
}
