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
  createTemporaryProject,
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
  type NewProjectCompletionOptions,
  type CreateTemporaryProjectInput
} from "../api/client";
import { NewProjectApplicationEditor } from "../features/new-project/NewProjectApplicationEditor";
import {
  NewProjectCompletionDock,
  isValidSpecifiedLtrInput
} from "../features/new-project/NewProjectCompletionDock";
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
  onInteractionLockChange?: (reason: string | null) => void;
  onProjectCreated: (projectId: string) => void;
};

type DuplicateImportState = {
  check: DraftDuplicateCheck;
  packageId: string;
  asset?: IntakeAsset | null;
};

type DuplicateDecisionMemo = {
  caseId: string;
  assetId: string | null;
  action: DraftDuplicateAction;
};

export function IntakeInboxPage({
  session,
  onInteractionLockChange,
  onSessionChange,
  onProjectCreated
}: IntakeInboxPageProps): ReactElement {
  const msgInputRef = useRef<HTMLInputElement | null>(null);
  const wordInputRef = useRef<HTMLInputElement | null>(null);
  const [importing, setImporting] = useState(false);
  const [importError, setImportError] = useState<string | null>(null);
  const [duplicateDraft, setDuplicateDraft] = useState<DuplicateImportState | null>(null);
  const [lastDuplicateDecision, setLastDuplicateDecision] = useState<DuplicateDecisionMemo | null>(null);
  const [hasDraftEditsSinceDecision, setHasDraftEditsSinceDecision] = useState(false);
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
    testTypeInSheet: "",
    projectLeader: "",
    labPerformingTests: "Dongguan"
  });
  const [completionSetupError, setCompletionSetupError] = useState<string | null>(null);
  const [temporaryCreating, setTemporaryCreating] = useState(false);
  const [temporaryError, setTemporaryError] = useState<string | null>(null);
  const fieldValuesRef = useRef<Record<string, string>>({});
  const sampleRowsRef = useRef<PrecheckSampleRow[]>([]);
  const requestedTestingRowsRef = useRef<PrecheckRequestedTestingRow[]>([]);
  const setupValuesRef = useRef<NewProjectSetupConfirmationValues>(setupValues);
  const { packageImport, selectedAssetId, sourceMode, directWordName } = session;
  const visibleAttachmentAssets = useMemo(
    () => visibleIntakeAttachments(packageImport),
    [packageImport]
  );
  const defaultApplicationFormAsset = useMemo(
    () => visibleAttachmentAssets.find((asset) => asset.extension.toLowerCase() === ".docx") ?? null,
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
    if (
      setupValues.ltrMode === "specified" &&
      !isValidSpecifiedLtrInput(setupValues.specifiedLtrNumber)
    ) {
      missing.add("specified_ltr_number");
    }
    if (!setupValues.testItem.trim()) missing.add("test_item");
    if (!setupValues.sampleDescription.trim()) missing.add("sample_description");
    if (!setupValues.testTypeInSheet.trim()) missing.add("test_type_in_sheet");
    if (!setupValues.projectLeader.trim()) missing.add("project_leader");
    if (!setupValues.labPerformingTests.trim()) missing.add("lab_performing_tests");
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
  const ltrApplyBusy = completionLoading;
  const ltrApplyBusyReason = "Applying LTR number. Keep this page open.";
  const importPausedReason = "Applying LTR number. Import is paused.";
  const displayedCompletionError = completionError ?? completionSetupError;
  const completionDisabled =
    editorLoading
    || completionLoading
    || Boolean(activeCase?.confirmed_project_id)
    || requiredState.missingCount > 0
    || setupMissingKeys.size > 0;

  useEffect(() => {
    onInteractionLockChange?.(ltrApplyBusy ? ltrApplyBusyReason : null);
    return () => onInteractionLockChange?.(null);
  }, [ltrApplyBusy, onInteractionLockChange]);
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
  const setupChanged = activeCase
    ? stableSetupJson(projectSetupPayload(setupValues))
      !== stableSetupJson(activeCase.project_setup ?? {})
    : false;
  const draftChanged = activeCase
    ? activeCase.fields.some((field) => fieldValues[field.key] !== editableValue(field.value))
      || JSON.stringify(sampleRows) !== JSON.stringify(normalizedSampleRows(activeCase.sample_rows))
      || JSON.stringify(requestedTestingRows)
        !== JSON.stringify(normalizedRequestedTestingRows(activeCase.requested_testing_rows))
      || setupChanged
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
        setSetupValues((current) => {
          const next = {
            ...current,
            projectLeader: current.projectLeader || options.default_project_leader
          };
          setupValuesRef.current = next;
          return next;
        });
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
    if (!packageImport) {
      setReview(null);
      setSelectedCaseId(null);
      setHasDraftEditsSinceDecision(false);
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
    const defaultFormAsset = defaultApplicationFormAsset;
    const shouldSelectDefaultApplicationForm =
      packageImport.source_type === "outlook_msg"
      && defaultFormAsset
      && !session.selectedWordAssetId
      && !session.selectedPrecheckCaseId;
    if (shouldSelectDefaultApplicationForm) {
      if (!defaultFormAsset) {
        return;
      }
      const selectedDefaultFormAsset = defaultFormAsset;
      let cancelled = false;
      async function selectDefaultApplicationForm(): Promise<void> {
        setEditorLoading(true);
        setEditorError(null);
        setImportingAssetId(selectedDefaultFormAsset.asset_id);
        try {
          const selection = await selectIntakeApplicationForm(
            packageId,
            selectedDefaultFormAsset.asset_id,
            true
          );
          if (!cancelled) {
            await applySelectedDraft(selection, selectedDefaultFormAsset.original_name);
          }
        } catch (error) {
          if (!cancelled) {
            const duplicate = draftDuplicateConflictFromError(error);
            if (duplicate) {
              const reused = await tryResolveDuplicateWithMemo(
                duplicate,
                packageId,
                selectedDefaultFormAsset,
                selectedDefaultFormAsset.original_name
              );
              if (reused) {
                return;
              }
              setDuplicateDraft({
                check: duplicate,
                packageId,
                asset: selectedDefaultFormAsset
              });
              onSessionChange({
                ...session,
                selectedAssetId: selectedDefaultFormAsset.asset_id
              });
              setReview(null);
              setSelectedCaseId(null);
              setEditorError(null);
            } else {
              setReview(null);
              setSelectedCaseId(null);
              setEditorError(
                error instanceof Error ? error.message : "Unable to select the first application form."
              );
            }
          }
        } finally {
          if (!cancelled) {
            setImportingAssetId(null);
            setEditorLoading(false);
          }
        }
      }
      void selectDefaultApplicationForm();
      return () => {
        cancelled = true;
      };
    }
    if (packageImport.source_type === "outlook_msg" && defaultApplicationFormAsset) {
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
            const reused = await tryResolveDuplicateWithMemo(
              duplicate,
              packageId,
              null,
              null
            );
            if (reused) {
              return;
            }
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
    defaultApplicationFormAsset?.asset_id,
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
      const nextSetupValues = emptySetupValues(setupOptions?.default_project_leader ?? "");
      setSetupValues(nextSetupValues);
      setupValuesRef.current = nextSetupValues;
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
    const nextSetupValues = setupValuesFromProjectSetup(
      activeCase.project_setup,
      setupOptions?.default_project_leader ?? ""
    );
    fieldValuesRef.current = nextFieldValues;
    sampleRowsRef.current = nextSampleRows;
    requestedTestingRowsRef.current = nextRequestedTestingRows;
    setupValuesRef.current = nextSetupValues;
    setSetupValues(nextSetupValues);
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
        requested_testing_rows: requestedTestingRowsRef.current,
        project_setup: projectSetupPayload(setupValuesRef.current)
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
  }, [activeCase, draftChanged, fieldValues, requestedTestingRows, sampleRows, setupValues]);

  async function handleMsgFileChange(event: ChangeEvent<HTMLInputElement>): Promise<void> {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (ltrApplyBusy) return;
    if (!file) return;
    setImporting(true);
    setImportError(null);
    setDuplicateDraft(null);
    setLastDuplicateDecision(null);
    setHasDraftEditsSinceDecision(false);
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
    if (ltrApplyBusy) {
      return;
    }
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
      setLastDuplicateDecision({
        caseId: duplicateDraft.check.existing_case_id,
        assetId: duplicateDraft.asset?.asset_id ?? null,
        action,
      });
      setHasDraftEditsSinceDecision(false);
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
    const firstApplicationForm = visibleIntakeAttachments(imported)
      .find((asset) => asset.extension.toLowerCase() === ".docx");
    onSessionChange({
      packageImport: imported,
      selectedAssetId: firstApplicationForm?.asset_id ?? null,
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
    setDuplicateDraft(null);
    setHasDraftEditsSinceDecision(false);
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
    setDuplicateDraft(null);
    setHasDraftEditsSinceDecision(false);
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
    if (ltrApplyBusy) return;
    if (!file) return;
    setImporting(true);
    setImportError(null);
    setDuplicateDraft(null);
    setLastDuplicateDecision(null);
    setHasDraftEditsSinceDecision(false);
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
    if (ltrApplyBusy) {
      return;
    }
    if (!packageImport) {
      return;
    }

    // Guard only when the loaded review case is already bound to this form asset.
    // selectedAssetId alone can reflect attachment focus before the review has changed.
    if (activeCase?.selected_form_asset_id === asset.asset_id) {
      console.info("[IntakeInbox] Asset already selected, skipping redundant import", {
        assetId: asset.asset_id,
        assetName: asset.original_name
      });
      return;
    }

    setImportingAssetId(asset.asset_id);
    setImportError(null);
    setDuplicateDraft(null);
    setImportMessage(null);
    try {
      const selection = await selectIntakeApplicationForm(packageImport.package_id, asset.asset_id, true);
      await applySelectedDraft(selection, asset.original_name);
    } catch (error) {
      const duplicate = draftDuplicateConflictFromError(error);
      if (duplicate) {
        const reused = await tryResolveDuplicateWithMemo(
          duplicate,
          packageImport.package_id,
          asset,
          asset.original_name
        );
        if (reused) {
          return;
        }
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
    if (ltrApplyBusy) {
      return;
    }
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

  async function handleCreateTemporaryProject(): Promise<void> {
    if (ltrApplyBusy) {
      return;
    }
    setTemporaryCreating(true);
    setTemporaryError(null);
    try {
      const created = await createTemporaryProject(
        temporaryProjectPayload({
          packageImport,
          directWordName,
          fieldValues,
          requestedTestingRows,
          setupValues,
          visibleAttachmentAssets
        })
      );
      onSessionChange(EMPTY_INTAKE_SESSION);
      onProjectCreated(created.project_id);
    } catch (error) {
      setTemporaryError(
        error instanceof Error ? error.message : "Unable to create temporary project."
      );
    } finally {
      setTemporaryCreating(false);
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
            interactionLocked={ltrApplyBusy}
            interactionLockedReason={importPausedReason}
            msgInputRef={msgInputRef}
            packageImport={packageImport}
            sourceMode={sourceMode}
            wordInputRef={wordInputRef}
            onDirectWordChange={(event) => void handleDirectWordChange(event)}
            onMsgFileChange={(event) => void handleMsgFileChange(event)}
            onSelectSourceMode={(mode) => {
              if (!ltrApplyBusy) {
                onSessionChange({ ...session, sourceMode: mode });
              }
            }}
          />
          <AttachmentList
            attachments={attachmentViewModels}
            disabled={ltrApplyBusy}
            disabledReason={ltrApplyBusyReason}
            duplicateDraft={duplicateDraft?.check ?? null}
            importingAssetId={importingAssetId}
            packageLoaded={Boolean(packageImport)}
            resolvingDuplicateAction={resolvingDuplicateAction}
            onDuplicateAction={(action) => void handleResolveDuplicateDraft(action)}
            onImport={(attachment) => void handleImportApplicationForm(attachment.asset)}
            onOpen={(attachment) => void handleOpenAttachment(attachment)}
            onSelect={(attachment) => {
              if (ltrApplyBusy) {
                return;
              }
              setDuplicateDraft(null);
              onSessionChange({
                ...session,
                selectedAssetId: attachment.asset.asset_id
              });
            }}
          />
          <NewProjectSetupConfirmationPanel
            disabled={completionLoading || editorLoading || Boolean(activeCase?.confirmed_project_id)}
            missingKeys={setupMissingKeys}
            testTypeInSheetOptions={setupOptions?.test_type_in_sheet_options ?? []}
            values={setupValues}
              onChange={(values) => {
      setSetupValues(values);
      setupValuesRef.current = values;
      setHasDraftEditsSinceDecision(true);
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
              disabled={
                editorLoading ||
                completionLoading ||
                Boolean(activeCase.confirmed_project_id) ||
                Boolean(activeCase.base_editing_frozen)
              }
              fieldValues={fieldValues}
              importMessage={importedFormDisplayName}
              completionError={displayedCompletionError}
              completionResult={completionResult}
              lookupError={lookupError}
              projectFields={projectFields}
              requestedTestingRows={requestedTestingRows}
              requiredState={requiredState}
              sampleRows={sampleRows}
              sourceFields={activeCase.fields}
              onFieldValuesChange={(values) => {
                setFieldValues(values);
                fieldValuesRef.current = values;
                setHasDraftEditsSinceDecision(true);
              }}
              onRequestedTestingRowsChange={(rows) => {
                setRequestedTestingRows(rows);
                requestedTestingRowsRef.current = rows;
                setHasDraftEditsSinceDecision(true);
              }}
              onSampleRowsChange={(rows) => {
                setSampleRows(rows);
                sampleRowsRef.current = rows;
                setHasDraftEditsSinceDecision(true);
              }}
            />
          ) : !packageImport ? (
            <section className="new-project-editor-panel new-project-editor-empty">
              <strong>Import a request email to start</strong>
            </section>
          ) : null}
        </main>
      </div>

      {temporaryError ? <p className="intake-error">{temporaryError}</p> : null}

      {packageImport && activeCase != null ? (
        <NewProjectCompletionDock
          completionDisabled={completionDisabled}
          completionLoading={completionLoading}
          completionText={completionText}
          disabled={completionLoading || editorLoading || Boolean(activeCase.confirmed_project_id)}
          missingKeys={setupMissingKeys}
          temporaryCreating={temporaryCreating}
          values={setupValues}
          onChange={(values) => {
            setSetupValues(values);
            setupValuesRef.current = values;
            setHasDraftEditsSinceDecision(true);
            setCompletionSetupError(null);
          }}
          onComplete={() => void completeProject()}
          onCreateTemporaryProject={() => void handleCreateTemporaryProject()}
        />
      ) : (
        <div className="step-footer new-project-completion-dock new-project-completion-dock-empty">
          <span />
          <button
            className="secondary-action"
            disabled={temporaryCreating || completionLoading || editorLoading}
            type="button"
            onClick={() => void handleCreateTemporaryProject()}
          >
            {temporaryCreating ? "Creating..." : "Create Temporary Project"}
          </button>
        </div>
      )}
    </section>
  );

  async function tryResolveDuplicateWithMemo(
    duplicate: DraftDuplicateCheck,
    packageId: string,
    asset: IntakeAsset | null,
    importMessageText: string | null
  ): Promise<boolean> {
    if (!lastDuplicateDecision || hasDraftEditsSinceDecision) {
      return false;
    }
    const assetId = asset?.asset_id ?? null;
    if (
      lastDuplicateDecision.caseId !== duplicate.existing_case_id
      || lastDuplicateDecision.assetId !== assetId
      || !duplicate.allowed_actions.includes(lastDuplicateDecision.action)
    ) {
      return false;
    }
    const resolution = {
      action: lastDuplicateDecision.action,
      caseId: duplicate.existing_case_id,
    };
    try {
      if (asset && importMessageText) {
        const selection = await selectIntakeApplicationForm(
          packageId,
          asset.asset_id,
          true,
          resolution
        );
        await applySelectedDraft(selection, importMessageText);
      } else {
        const draft = await ensureNewProjectApplicationDraft(packageId, resolution);
        await applyPreparedDraft(draft);
      }
      return true;
    } catch {
      return false;
    }
  }
}

function draftDuplicateConflictFromError(error: unknown): DraftDuplicateCheck | null {
  if (
    !(error instanceof ApiRequestError) ||
    error.status !== 409 ||
    !error.detail ||
    typeof error.detail !== "object" ||
    !("classification" in error.detail)
  ) {
    return null;
  }
  return error.detail as DraftDuplicateCheck;
}

function emptySetupValues(defaultProjectLeader = ""): NewProjectSetupConfirmationValues {
  return {
    ltrMode: "auto",
    specifiedLtrNumber: "",
    testItem: "",
    sampleDescription: "",
    testTypeInSheet: "",
    projectLeader: defaultProjectLeader,
    labPerformingTests: "Dongguan"
  };
}

function setupValuesFromProjectSetup(
  projectSetup: Record<string, unknown> | undefined,
  defaultProjectLeader = ""
): NewProjectSetupConfirmationValues {
  const rawLtrMode = stringValue(projectSetup?.ltr_mode);
  return {
    ltrMode: rawLtrMode === "specified" ? "specified" : "auto",
    specifiedLtrNumber: stringValue(projectSetup?.specified_ltr_number),
    testItem: stringValue(projectSetup?.test_item),
    sampleDescription: stringValue(projectSetup?.sample_description),
    testTypeInSheet: stringValue(projectSetup?.test_type_in_sheet),
    projectLeader: stringValue(projectSetup?.project_leader) || defaultProjectLeader,
    labPerformingTests: stringValue(projectSetup?.lab_performing_tests) || "Dongguan"
  };
}

function projectSetupPayload(
  values: NewProjectSetupConfirmationValues
): Record<string, string> {
  const payload: Record<string, string> = {
    ltr_mode: values.ltrMode
  };
  if (values.ltrMode === "specified") {
    assignText(payload, "specified_ltr_number", values.specifiedLtrNumber);
  }
  assignText(payload, "test_item", values.testItem);
  assignText(payload, "sample_description", values.sampleDescription);
  assignText(payload, "test_type_in_sheet", values.testTypeInSheet);
  assignText(payload, "project_leader", values.projectLeader);
  assignText(payload, "lab_performing_tests", values.labPerformingTests);
  return payload;
}

function temporaryProjectPayload({
  packageImport,
  directWordName,
  fieldValues,
  requestedTestingRows,
  setupValues,
  visibleAttachmentAssets
}: {
  packageImport: IntakePackageImport | null;
  directWordName: string | null;
  fieldValues: Record<string, string>;
  requestedTestingRows: PrecheckRequestedTestingRow[];
  setupValues: NewProjectSetupConfirmationValues;
  visibleAttachmentAssets: IntakeAsset[];
}): CreateTemporaryProjectInput {
  const requestSummary = firstText(
    packageImport?.subject,
    packageImport?.source_original_name,
    directWordName,
    "Temporary planning project"
  );
  const requestor = firstText(
    fieldValues.requester,
    fieldValues.requestor,
    packageImport?.sender_name,
    packageImport?.sender_email
  );
  return {
    request_summary: requestSummary,
    sample_description: firstText(setupValues.sampleDescription, requestSummary),
    test_item: firstText(setupValues.testItem, requestedTestingText(requestedTestingRows)),
    requestor,
    source_asset_ids: visibleAttachmentAssets.map((asset) => asset.asset_id),
    notes: packageImport
      ? firstText(
          packageImport.source_original_name,
          packageImport.subject,
          packageImport.package_id
        )
      : directWordName
  };
}

function firstText(...values: Array<string | null | undefined>): string | null {
  for (const value of values) {
    if (typeof value !== "string") {
      continue;
    }
    const text = value.trim();
    if (text) {
      return text;
    }
  }
  return null;
}

function assignText(payload: Record<string, string>, key: string, value: string): void {
  const text = value.trim();
  if (text) {
    payload[key] = text;
  }
}

function stableSetupJson(values: Record<string, unknown>): string {
  const sorted = Object.fromEntries(
    Object.keys(values)
      .sort()
      .map((key) => [key, values[key]])
  );
  return JSON.stringify(sorted);
}

function stringValue(value: unknown): string {
  return typeof value === "string" ? value : "";
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
