import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactElement,
} from "react";
import {
  ApiRequestError,
  confirmFeeVersion,
  fetchConfirmedMatrixFeeDraft,
  generateConfirmedMatrixFeeFileDownload,
  getConfirmedFeeLatest,
  getFeeEvaluationPricingDraft,
  getProject,
  getProjectLifecycle,
  isProjectLifecycleReadonlyErrorDetail,
  listProjectLtrs,
  saveFeeEvaluationPricingDraft,
  type ConfirmedFeeLatestResponse,
  type FeeEvaluationDraft,
  type FeeEvaluationEditedFileExportRequest,
  type FeeEvaluationLineItem,
  type FeeEvaluationPricingDraftResponse,
  type FeeEvaluationPricingDraftSaveRequest,
  type Project,
  type ProjectLifecycleResponse,
} from "../../api/client";
import { buildProjectIdentityLine } from "../projectIdentity";
import {
  deriveProjectLifecycleReadonlyView,
  deriveReadonlyApiErrorMessage,
} from "../project-lifecycle/projectLifecycleReadonlyModel";
import { FeeEvaluationPreviewTable } from "./FeeEvaluationPreviewTable";
import {
  buildFeeEvaluationCostRisk,
  buildFeeEvaluationLabManpowerCost,
  buildFeeEvaluationPreviewGrandCost,
  buildFeeEvaluationPreviewHeader,
  buildFeeEvaluationPreviewRows,
  buildFeeEvaluationPreviewScopeTotal,
  buildFeeEvaluationPreviewTotals,
  buildFeeEvaluationPreviewWorkingHours,
  applyFeeEvaluationPreviewEdits,
  filterFeeEvaluationPreviewRowsForScope,
  hydrateFeeEvaluationPreviewEditsFromSavedDraft,
  type FeeEvaluationEditableField,
  type FeeEvaluationPreviewEditState,
} from "./feeEvaluationPreviewModel";

type DraftLoadState =
  | { kind: "loading" }
  | { kind: "not_ready" }
  | { kind: "ready"; draft: FeeEvaluationDraft }
  | { kind: "error"; message: string };

type FeePageContextState =
  | { kind: "loading" }
  | {
      kind: "ready";
      project: Project;
      ltrNumber: string | null;
    }
  | { kind: "error"; message: string };

export type FeeFileDownloadState =
  | { kind: "idle" }
  | { kind: "running" }
  | { kind: "success"; fileName: string | null }
  | { kind: "error"; message: string; manualCleanupWarning?: string | null };

type FeePricingDraftSaveState =
  | { kind: "loading" }
  | { kind: "idle"; message: string | null }
  | { kind: "dirty" }
  | { kind: "saving" }
  | { kind: "saved"; message: string }
  | { kind: "stale"; message: string }
  | { kind: "error"; message: string };

type PricingDraftLoadStatus = "loading" | "missing" | "current" | "stale" | "error";

type PricingDraftContext = {
  confirmedMatrixId: string;
  confirmedRevision: number;
  feeRuleVersionId: string;
};

type ConfirmedFeeLoadState =
  | { kind: "loading" }
  | { kind: "ready"; data: ConfirmedFeeLatestResponse }
  | { kind: "error"; message: string };

type ConfirmFeeActionState =
  | { kind: "idle" }
  | { kind: "confirming" }
  | { kind: "success"; message: string }
  | { kind: "error"; message: string };

type FeeEvaluationReviewExportPageProps = {
  projectId: string;
  onBackToWorkbench: () => void;
};

const EMPTY_COST_PREVIEW_VALUES = {
  conditionConfirmationSpendTime: "0",
  externalCost: "0",
  externalCostNote: "",
  labManpowerHourlyRate: "200",
};
const FEE_CONFIRM_INTERNAL_ACTOR = "Lab User";

export function FeeEvaluationReviewExportPage({
  projectId,
  onBackToWorkbench,
}: FeeEvaluationReviewExportPageProps): ReactElement {
  const [contextState, setContextState] = useState<FeePageContextState>({
    kind: "loading",
  });
  const [lifecycle, setLifecycle] = useState<ProjectLifecycleResponse | null>(null);
  const [draftState, setDraftState] = useState<DraftLoadState>({ kind: "loading" });
  const [previewGroupFilter, setPreviewGroupFilter] = useState("all");
  const [previewEdits, setPreviewEdits] = useState<FeeEvaluationPreviewEditState>({});
  const [costPreviewValues, setCostPreviewValues] = useState(
    EMPTY_COST_PREVIEW_VALUES
  );
  const [downloadState, setDownloadState] = useState<FeeFileDownloadState>({
    kind: "idle",
  });
  const [saveState, setSaveState] = useState<FeePricingDraftSaveState>({
    kind: "loading",
  });
  const [confirmedFeeState, setConfirmedFeeState] = useState<ConfirmedFeeLoadState>({
    kind: "loading",
  });
  const [confirmFeeActionState, setConfirmFeeActionState] =
    useState<ConfirmFeeActionState>({ kind: "idle" });
  const [latestSavedPricingDraftId, setLatestSavedPricingDraftId] = useState<
    string | null
  >(null);
  const [pricingDraftLoadStatus, setPricingDraftLoadStatus] =
    useState<PricingDraftLoadStatus>("loading");
  const [savedLocalPricingSignature, setSavedLocalPricingSignature] = useState<
    string | null
  >(null);
  const [hasUserEditedPricingDraft, setHasUserEditedPricingDraft] = useState(false);
  const [needsInitialSeedSave, setNeedsInitialSeedSave] = useState(false);
  const [isCancellingPricingSession, setIsCancellingPricingSession] =
    useState(false);
  const baselinePricingPayloadRef =
    useRef<FeeEvaluationEditedFileExportRequest | null>(null);
  const baselinePricingContextRef = useRef<PricingDraftContext | null>(null);
  const hasSessionEditedPricingDraftRef = useRef(false);
  const autosaveTimeoutRef = useRef<number | null>(null);
  const autosaveGenerationRef = useRef(0);
  const autosaveInFlightRef =
    useRef<Promise<FeeEvaluationPricingDraftResponse | null> | null>(null);
  const cancellingRef = useRef(false);

  useEffect(() => {
    let active = true;
    setContextState({ kind: "loading" });
    void loadPageContext(projectId)
      .then((context) => {
        if (active) {
          setContextState({ kind: "ready", ...context });
        }
      })
      .catch((error: unknown) => {
        if (active) {
          setContextState({
            kind: "error",
            message:
              error instanceof Error
                ? error.message
                : "Unable to load project fee context.",
          });
        }
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  useEffect(() => {
    let active = true;
    void getProjectLifecycle(projectId)
      .then((nextLifecycle) => {
        if (active) {
          setLifecycle(nextLifecycle);
        }
      })
      .catch(() => {
        if (active) {
          setLifecycle(null);
        }
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  useEffect(() => {
    let active = true;
    setDraftState({ kind: "loading" });
    setPreviewEdits({});
    setCostPreviewValues(EMPTY_COST_PREVIEW_VALUES);
    setSaveState({ kind: "loading" });
    setLatestSavedPricingDraftId(null);
    setPricingDraftLoadStatus("loading");
    setSavedLocalPricingSignature(null);
    setHasUserEditedPricingDraft(false);
    setNeedsInitialSeedSave(false);
    baselinePricingPayloadRef.current = null;
    baselinePricingContextRef.current = null;
    hasSessionEditedPricingDraftRef.current = false;
    setConfirmFeeActionState({ kind: "idle" });
    void fetchConfirmedMatrixFeeDraft(projectId)
      .then((draft) => {
        if (active) {
          setDraftState({ kind: "ready", draft });
          setPreviewEdits({});
          setCostPreviewValues(EMPTY_COST_PREVIEW_VALUES);
          setSaveState({ kind: "idle", message: null });
        }
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }
        if (error instanceof ApiRequestError && error.status === 404) {
          setDraftState({ kind: "not_ready" });
          setSaveState({ kind: "idle", message: null });
          setLatestSavedPricingDraftId(null);
          setPricingDraftLoadStatus("missing");
          setSavedLocalPricingSignature(null);
          setHasUserEditedPricingDraft(false);
          setNeedsInitialSeedSave(false);
          return;
        }
        setDraftState({
          kind: "error",
          message:
            error instanceof ApiRequestError
              ? error.message
              : "Unable to load Fee Evaluation draft.",
        });
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  useEffect(() => {
    let active = true;
    setConfirmedFeeState({ kind: "loading" });
    void getConfirmedFeeLatest(projectId)
      .then((data) => {
        if (active) {
          setConfirmedFeeState({ kind: "ready", data });
        }
      })
      .catch((error: unknown) => {
        if (active) {
          setConfirmedFeeState({
            kind: "error",
            message:
              error instanceof ApiRequestError
                ? error.message
                : "Unable to load Confirmed Fee status.",
          });
        }
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  const draft = draftState.kind === "ready" ? draftState.draft : null;
  const lines = useMemo(() => flattenDraftLines(draft), [draft]);
  const sourcePreviewRows = useMemo(() => buildFeeEvaluationPreviewRows(draft), [draft]);

  useEffect(() => {
    if (draftState.kind !== "ready") {
      return;
    }
    let active = true;
    setSaveState({ kind: "loading" });
    setPricingDraftLoadStatus("loading");
    void getFeeEvaluationPricingDraft(projectId)
      .then((result) => {
        if (!active) {
          return;
        }
        if (result.status === "current") {
          baselinePricingContextRef.current = contextFromPricingDraftResponse(result);
          setLatestSavedPricingDraftId(result.saved_draft_edit_id ?? null);
          setPricingDraftLoadStatus("current");
          setHasUserEditedPricingDraft(false);
          setNeedsInitialSeedSave(false);
          if (!result.payload) {
            const currentSignature = pricingDraftSignature(
              buildEditedExportPayload(sourcePreviewRows, costPreviewValues)
            );
            baselinePricingPayloadRef.current = buildEditedExportPayload(
              sourcePreviewRows,
              costPreviewValues
            );
            setSavedLocalPricingSignature(
              result.saved_draft_edit_id ? currentSignature : null
            );
            setSaveState(
              result.saved_draft_edit_id
                ? { kind: "saved", message: "Loaded saved pricing draft." }
                : { kind: "idle", message: null }
            );
            return;
          }
          const hydrated = hydrateFeeEvaluationPreviewEditsFromSavedDraft(
            sourcePreviewRows,
            result.payload
          );
          setPreviewEdits(hydrated.edits);
          setCostPreviewValues(hydrated.costPreviewValues);
          const hydratedPayload = buildEditedExportPayload(
            applyFeeEvaluationPreviewEdits(sourcePreviewRows, hydrated.edits),
            hydrated.costPreviewValues
          );
          const hydratedSignature = pricingDraftSignature(hydratedPayload);
          baselinePricingPayloadRef.current = hydratedPayload;
          setSavedLocalPricingSignature(hydratedSignature);
          if (hydrated.unmatchedRowCount > 0) {
            setSaveState({
              kind: "stale",
              message:
                "Saved pricing draft had rows that no longer match this Matrix. Unmatched rows were not applied.",
            });
          } else {
            setSaveState({
              kind: "saved",
              message: "Loaded saved pricing draft.",
            });
          }
          return;
        }
        if (result.status === "stale") {
          baselinePricingContextRef.current = contextFromPricingDraftResponse(result);
          setLatestSavedPricingDraftId(null);
          setPricingDraftLoadStatus("stale");
          setSavedLocalPricingSignature(null);
          baselinePricingPayloadRef.current = buildEditedExportPayload(
            sourcePreviewRows,
            costPreviewValues
          );
          setHasUserEditedPricingDraft(false);
          setNeedsInitialSeedSave(false);
          setSaveState({
            kind: "stale",
            message:
              "Saved pricing draft belongs to an older Matrix or fee rule version. Current defaults are shown.",
          });
          return;
        }
        baselinePricingContextRef.current = contextFromPricingDraftResponse(result);
        setLatestSavedPricingDraftId(null);
        setPricingDraftLoadStatus("missing");
        setSavedLocalPricingSignature(null);
        baselinePricingPayloadRef.current = buildEditedExportPayload(
          sourcePreviewRows,
          costPreviewValues
        );
        setHasUserEditedPricingDraft(false);
        setNeedsInitialSeedSave(true);
        setSaveState({ kind: "idle", message: null });
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }
        setSaveState({
          kind: "error",
          message:
            error instanceof ApiRequestError
              ? error.message
              : "Unable to load saved pricing draft.",
        });
        setPricingDraftLoadStatus("error");
        setSavedLocalPricingSignature(null);
        setNeedsInitialSeedSave(false);
      });
    return () => {
      active = false;
    };
  }, [draftState.kind, projectId, sourcePreviewRows]);

  const previewRows = useMemo(
    () => applyFeeEvaluationPreviewEdits(sourcePreviewRows, previewEdits),
    [previewEdits, sourcePreviewRows]
  );
  const visiblePreviewRows = useMemo(
    () =>
      previewGroupFilter === "all"
        ? previewRows
        : previewRows.filter(
            (row) =>
              row.rowKind === "manual_trailing" || row.groupLabel === previewGroupFilter
          ),
    [previewGroupFilter, previewRows]
  );
  const scopedPreviewRows = useMemo(
    () => filterFeeEvaluationPreviewRowsForScope(previewRows, previewGroupFilter),
    [previewGroupFilter, previewRows]
  );
  const allPreviewRows = useMemo(
    () => filterFeeEvaluationPreviewRowsForScope(previewRows, "all"),
    [previewRows]
  );
  const selectedPreviewTotal = useMemo(
    () => buildFeeEvaluationPreviewScopeTotal(previewRows, previewGroupFilter),
    [previewGroupFilter, previewRows]
  );
  const allPreviewTotal = useMemo(
    () => buildFeeEvaluationPreviewScopeTotal(previewRows, "all"),
    [previewRows]
  );
  const previewHeader = useMemo(
    () =>
      buildFeeEvaluationPreviewHeader({
        ltrNumber: contextState.kind === "ready" ? contextState.ltrNumber : null,
        requestor: contextState.kind === "ready" ? contextState.project.requestor : null,
      }),
    [contextState]
  );
  const previewIdentityLine = useMemo(
    () => buildFeeEvaluationIdentityLine(contextState),
    [contextState]
  );
  const basePreviewTotals = useMemo(
    () => buildFeeEvaluationPreviewTotals(draft, ""),
    [draft]
  );
  const workingHoursLabel = useMemo(
    () =>
      buildFeeEvaluationPreviewWorkingHours(
        scopedPreviewRows,
        costPreviewValues.conditionConfirmationSpendTime
      ),
    [costPreviewValues.conditionConfirmationSpendTime, scopedPreviewRows]
  );
  const allWorkingHoursLabel = useMemo(
    () =>
      buildFeeEvaluationPreviewWorkingHours(
        allPreviewRows,
        costPreviewValues.conditionConfirmationSpendTime
      ),
    [allPreviewRows, costPreviewValues.conditionConfirmationSpendTime]
  );
  const labManpowerCostLabel = useMemo(
    () =>
      buildFeeEvaluationLabManpowerCost(
        workingHoursLabel,
        costPreviewValues.labManpowerHourlyRate
      ),
    [costPreviewValues.labManpowerHourlyRate, workingHoursLabel]
  );
  const allLabManpowerCostLabel = useMemo(
    () =>
      buildFeeEvaluationLabManpowerCost(
        allWorkingHoursLabel,
        costPreviewValues.labManpowerHourlyRate
      ),
    [allWorkingHoursLabel, costPreviewValues.labManpowerHourlyRate]
  );
  const previewTotals = useMemo(
    () => ({
      ...basePreviewTotals,
      workingHours: workingHoursLabel,
      labManpowerCost: labManpowerCostLabel,
      externalCost: costPreviewValues.externalCost,
    }),
    [
      basePreviewTotals,
      costPreviewValues.externalCost,
      labManpowerCostLabel,
      workingHoursLabel,
    ]
  );
  const grandCostLabel = useMemo(
    () =>
      buildFeeEvaluationPreviewGrandCost(
        scopedPreviewRows,
        costPreviewValues.externalCost,
        previewTotals.grandCost
      ),
    [costPreviewValues.externalCost, previewTotals.grandCost, scopedPreviewRows]
  );
  const allGrandCostLabel = useMemo(
    () =>
      buildFeeEvaluationPreviewGrandCost(
        allPreviewRows,
        costPreviewValues.externalCost,
        previewTotals.grandCost
      ),
    [allPreviewRows, costPreviewValues.externalCost, previewTotals.grandCost]
  );
  const currentPricingDraftPayload = useMemo(
    () => buildEditedExportPayload(previewRows, costPreviewValues),
    [costPreviewValues, previewRows]
  );
  const currentPricingDraftSignature = useMemo(
    () => pricingDraftSignature(currentPricingDraftPayload),
    [currentPricingDraftPayload]
  );
  const hasPricingDraftLocalChanges =
    hasUserEditedPricingDraft &&
    savedLocalPricingSignature !== currentPricingDraftSignature;
  const costRisk = useMemo(
    () =>
      buildFeeEvaluationCostRisk({
        grandCost: grandCostLabel,
        labManpowerCost: labManpowerCostLabel,
      }),
    [grandCostLabel, labManpowerCostLabel]
  );
  const groupOptions = useMemo(
    () => Array.from(new Set(lines.map((line) => line.group_label))).sort(),
    [lines]
  );
  const lifecycleReadonlyView = deriveProjectLifecycleReadonlyView(lifecycle);
  const isLifecycleReadonly = lifecycleReadonlyView.readonly;
  const confirmFeeDisabledReason = isLifecycleReadonly
    ? lifecycleReadonlyView.message
    : confirmFeeBlocker({
        draftState,
        confirmedFeeState,
        isCancellingPricingSession,
        latestSavedPricingDraftId,
        pricingDraftLoadStatus,
        saveState,
        savedLocalPricingSignature,
        currentPricingDraftSignature,
      });
  const generateDisabledReason = isLifecycleReadonly
    ? lifecycleReadonlyView.message
    : feeFileDownloadBlocker(draftState);

  function applySavedPricingDraftResult(
    result: FeeEvaluationPricingDraftResponse,
    signature: string
  ): void {
    if (result.status === "current") {
      const savedDraftId = result.saved_draft_edit_id ?? null;
      setLatestSavedPricingDraftId(savedDraftId);
      setPricingDraftLoadStatus("current");
      setSavedLocalPricingSignature(savedDraftId ? signature : null);
      setHasUserEditedPricingDraft(false);
      setNeedsInitialSeedSave(false);
      setSaveState(
        savedDraftId
          ? { kind: "saved", message: "Saved pricing draft." }
          : {
              kind: "error",
              message: "Save returned no pricing draft id. Retry before updating.",
            }
      );
      return;
    }
    setLatestSavedPricingDraftId(null);
    setPricingDraftLoadStatus("stale");
    setSavedLocalPricingSignature(null);
    setNeedsInitialSeedSave(false);
    setSaveState({
      kind: "stale",
      message: "Saved draft is not current for this Matrix or fee rule version.",
    });
  }

  useEffect(() => {
    if (autosaveTimeoutRef.current !== null) {
      window.clearTimeout(autosaveTimeoutRef.current);
      autosaveTimeoutRef.current = null;
    }
    if (
      draftState.kind !== "ready" ||
      (!hasPricingDraftLocalChanges && !needsInitialSeedSave) ||
      isLifecycleReadonly ||
      cancellingRef.current ||
      isCancellingPricingSession
    ) {
      return;
    }
    const generation = autosaveGenerationRef.current + 1;
    autosaveGenerationRef.current = generation;
    const payload = currentPricingDraftPayload;
    const signature = currentPricingDraftSignature;
    if (!needsInitialSeedSave) {
      setSaveState({ kind: "dirty" });
    }
    autosaveTimeoutRef.current = window.setTimeout(() => {
      if (cancellingRef.current) {
        return;
      }
      setSaveState({ kind: "saving" });
      const abortController = new AbortController();
      const saveRequest = saveFeeEvaluationPricingDraft(projectId, payload, {
        signal: abortController.signal,
      })
        .then((result) => {
          if (autosaveGenerationRef.current === generation && !cancellingRef.current) {
            applySavedPricingDraftResult(result, signature);
          }
          return result;
        })
        .catch((error: unknown) => {
          if (autosaveGenerationRef.current === generation && !cancellingRef.current) {
            if (isAbortError(error)) {
              return null;
            }
            setSaveState({
              kind: "error",
              message: readonlyAwareErrorMessage(
                error,
                "Unable to save pricing draft."
              ),
            });
          }
          return null;
        })
        .finally(() => {
          if (autosaveInFlightRef.current === saveRequest) {
            autosaveInFlightRef.current = null;
          }
        });
      autosaveInFlightRef.current = saveRequest;
    }, 800);
    return () => {
      if (autosaveTimeoutRef.current !== null) {
        window.clearTimeout(autosaveTimeoutRef.current);
        autosaveTimeoutRef.current = null;
      }
    };
  }, [
    currentPricingDraftPayload,
    currentPricingDraftSignature,
    draftState.kind,
    hasPricingDraftLocalChanges,
    isLifecycleReadonly,
    isCancellingPricingSession,
    needsInitialSeedSave,
    projectId,
  ]);

  async function handleGenerateFeeFile(): Promise<void> {
    if (isLifecycleReadonly) {
      setDownloadState({ kind: "error", message: lifecycleReadonlyView.message });
      return;
    }
    if (generateDisabledReason || downloadState.kind === "running") {
      return;
    }
    setDownloadState({ kind: "running" });
    try {
      const response = await generateConfirmedMatrixFeeFileDownload(
        projectId,
        buildEditedExportPayload(previewRows, costPreviewValues)
      );
      const downloadFileName = feeFileNameFromPageContext({
        projectId,
        contextState,
        draftState,
        responseFileName: response.fileName,
      });
      downloadBlob(response.blob, downloadFileName);
      setDownloadState({ kind: "success", fileName: downloadFileName });
    } catch (error: unknown) {
      const detail =
        error instanceof ApiRequestError && isErrorDetailObject(error.detail)
          ? error.detail
          : null;
      setDownloadState({
        kind: "error",
        message:
          error instanceof ApiRequestError
            ? businessReadableDownloadError(error)
            : "Fee file generation failed.",
        manualCleanupWarning: detail?.manual_cleanup_warning ?? null,
      });
    }
  }

  async function handleConfirmFee(): Promise<void> {
    if (isLifecycleReadonly) {
      setConfirmFeeActionState({
        kind: "error",
        message: lifecycleReadonlyView.message,
      });
      return;
    }
    if (
      draftState.kind !== "ready" ||
      confirmFeeActionState.kind === "confirming" ||
      confirmFeeDisabledReason
    ) {
      return;
    }
    setConfirmFeeActionState({ kind: "confirming" });
    try {
      const savedDraftId = latestSavedPricingDraftId;
      if (!savedDraftId) {
        setConfirmFeeActionState({
          kind: "error",
          message: "Save pricing draft before updating Fee.",
        });
        return;
      }

      const result = await confirmFeeVersion(projectId, {
        confirmed_by: FEE_CONFIRM_INTERNAL_ACTOR,
        expected_pricing_draft_edit_id: savedDraftId,
        summary: {
          testing_fee_total: allPreviewTotal,
          working_hours: allWorkingHoursLabel,
          lab_manpower_cost: allLabManpowerCostLabel,
          external_cost: costPreviewValues.externalCost,
          grand_cost: allGrandCostLabel,
        },
      });
      setConfirmedFeeState({ kind: "ready", data: result });
      setConfirmFeeActionState({ kind: "success", message: "Fee updated." });
      onBackToWorkbench();
    } catch (error: unknown) {
      const message = readonlyAwareErrorMessage(error, "Unable to update Fee.");
      setConfirmFeeActionState({ kind: "error", message });
      setSaveState({ kind: "error", message });
    }
  }

  function handleCostPreviewChange(
    field: keyof typeof costPreviewValues,
    value: string
  ): void {
    if (isLifecycleReadonly) {
      setConfirmFeeActionState({
        kind: "error",
        message: lifecycleReadonlyView.message,
      });
      return;
    }
    setCostPreviewValues((current) => ({ ...current, [field]: value }));
    markPricingDraftDirty();
  }

  function handlePreviewRowEditChange(
    lineId: string,
    field: FeeEvaluationEditableField,
    value: string
  ): void {
    if (isLifecycleReadonly) {
      setConfirmFeeActionState({
        kind: "error",
        message: lifecycleReadonlyView.message,
      });
      return;
    }
    setPreviewEdits((current) => ({
      ...current,
      [lineId]: {
        ...(current[lineId] ?? {}),
        [field]: value,
      },
    }));
    markPricingDraftDirty();
  }

  function markPricingDraftDirty(): void {
    if (isLifecycleReadonly) {
      return;
    }
    hasSessionEditedPricingDraftRef.current = true;
    setHasUserEditedPricingDraft(true);
    setNeedsInitialSeedSave(false);
    setConfirmFeeActionState((current) =>
      current.kind === "confirming" ? current : { kind: "idle" }
    );
    setSaveState((current) =>
      current.kind === "loading" || current.kind === "saving"
        ? current
        : { kind: "dirty" }
    );
  }

  async function handleBackToWorkbench(): Promise<void> {
    if (isLifecycleReadonly) {
      onBackToWorkbench();
      return;
    }
    const baselinePayload = baselinePricingPayloadRef.current;
    const baselineContext = baselinePricingContextRef.current;
    const hasSessionChanges =
      hasSessionEditedPricingDraftRef.current ||
      saveState.kind === "dirty" ||
      saveState.kind === "saving";
    if (!hasSessionChanges) {
      onBackToWorkbench();
      return;
    }
    if (
      !window.confirm(
        "Discard this Fee Evaluation page session and return to Workbench?"
      )
    ) {
      return;
    }
    if (!baselinePayload || !baselineContext) {
      setSaveState({
        kind: "error",
        message: "Reload Fee Evaluation before cancelling this page session.",
      });
      return;
    }
    cancellingRef.current = true;
    autosaveGenerationRef.current += 1;
    if (autosaveTimeoutRef.current !== null) {
      window.clearTimeout(autosaveTimeoutRef.current);
      autosaveTimeoutRef.current = null;
    }
    setIsCancellingPricingSession(true);
    const inFlightState = await waitForAutosaveSettlement(autosaveInFlightRef.current);
    if (inFlightState.status === "timeout") {
      cancellingRef.current = false;
      setIsCancellingPricingSession(false);
      setHasUserEditedPricingDraft(false);
      setSaveState({
        kind: "error",
        message: "Fee Evaluation is still saving. Wait a moment and retry Cancel.",
      });
      return;
    }
    try {
      const currentServerDraft = await getFeeEvaluationPricingDraft(projectId);
      const currentServerContext = contextFromPricingDraftResponse(currentServerDraft);
      if (!pricingContextEquals(baselineContext, currentServerContext)) {
        throw new FeeEvaluationSessionCancelError(
          "Fee Evaluation context changed. Refresh before leaving."
        );
      }
      const restoreResult = await saveFeeEvaluationPricingDraft(
        projectId,
        pricingDraftRestorePayload(baselinePayload, baselineContext)
      );
      if (!pricingContextEquals(baselineContext, contextFromPricingDraftResponse(restoreResult))) {
        throw new FeeEvaluationSessionCancelError(
          "Fee Evaluation context changed. Refresh before leaving."
        );
      }
      onBackToWorkbench();
    } catch (error: unknown) {
      cancellingRef.current = false;
      setIsCancellingPricingSession(false);
      setHasUserEditedPricingDraft(false);
      setSaveState({
        kind: "error",
        message:
          error instanceof Error
            ? error.message
            : "Unable to restore Fee Evaluation pricing before leaving.",
      });
    }
  }

  return (
    <section className="fee-evaluation-page" aria-label="Fee Evaluation review and export">
      {isLifecycleReadonly ? (
        <div className="fee-evaluation-confirm-error" role="status">
          <strong>{lifecycleReadonlyView.title}</strong>
          <span>{lifecycleReadonlyView.message}</span>
        </div>
      ) : null}
      <FeeEvaluationPreviewTable
        costPreviewValues={costPreviewValues}
        costRisk={costRisk}
        confirmFeeActionState={confirmFeeActionState}
        grandCostLabel={grandCostLabel}
        labManpowerCostLabel={labManpowerCostLabel}
        groupFilter={previewGroupFilter}
        groupOptions={groupOptions}
        header={previewHeader}
        identityLine={previewIdentityLine}
        downloadState={downloadState}
        generateDisabledReason={generateDisabledReason}
        onCostPreviewChange={handleCostPreviewChange}
        onGenerateFeeFile={handleGenerateFeeFile}
        onGroupFilterChange={setPreviewGroupFilter}
        onRowEditChange={handlePreviewRowEditChange}
        readOnly={isLifecycleReadonly}
        readOnlyReason={lifecycleReadonlyView.message}
        saveState={saveState}
        scopeFeeLabel={selectedPreviewTotal}
        rows={visiblePreviewRows}
        totals={previewTotals}
      />
      <footer
        aria-label="Fee Evaluation completion actions"
        className="fee-evaluation-completion-dock"
      >
        <span>
          {confirmFeeDisabledReason ??
            "Update Fee returns to Workbench after authority is updated."}
        </span>
        <div className="fee-evaluation-completion-actions">
          <button
            type="button"
            onClick={() => void handleBackToWorkbench()}
            disabled={
              confirmFeeActionState.kind === "confirming" ||
              isCancellingPricingSession
            }
          >
            {isCancellingPricingSession ? "Cancelling..." : "Cancel"}
          </button>
          <button
            className="fee-evaluation-primary-action"
            type="button"
            onClick={() => void handleConfirmFee()}
            disabled={
              Boolean(confirmFeeDisabledReason) ||
              confirmFeeActionState.kind === "confirming"
            }
            title={confirmFeeDisabledReason ?? undefined}
          >
            {confirmFeeActionState.kind === "confirming" ? "Updating..." : "Update Fee"}
          </button>
        </div>
      </footer>
    </section>
  );
}

function confirmFeeBlocker(input: {
  draftState: DraftLoadState;
  confirmedFeeState: ConfirmedFeeLoadState;
  isCancellingPricingSession: boolean;
  latestSavedPricingDraftId: string | null;
  pricingDraftLoadStatus: PricingDraftLoadStatus;
  saveState: FeePricingDraftSaveState;
  savedLocalPricingSignature: string | null;
  currentPricingDraftSignature: string;
}): string | null {
  if (input.draftState.kind === "loading") {
    return "Waiting for Fee Evaluation draft.";
  }
  if (input.draftState.kind === "not_ready") {
    return "Confirm Matrix authority before updating Fee.";
  }
  if (input.draftState.kind === "error") {
    return input.draftState.message;
  }
  if (input.confirmedFeeState.kind === "loading") {
    return "Waiting for Confirmed Fee status.";
  }
  if (input.isCancellingPricingSession) {
    return "Cancelling Fee Evaluation page session.";
  }
  if (input.pricingDraftLoadStatus === "loading") {
    return "Waiting for saved pricing draft.";
  }
  if (input.pricingDraftLoadStatus === "stale") {
    return "Saved pricing draft belongs to an older Matrix or fee rule version.";
  }
  if (input.pricingDraftLoadStatus === "error") {
    return "Reload saved pricing draft before updating Fee.";
  }
  if (input.saveState.kind === "dirty" || input.saveState.kind === "saving") {
    return "Saving pricing draft before update.";
  }
  if (input.saveState.kind === "error") {
    return input.saveState.message;
  }
  if (!input.latestSavedPricingDraftId) {
    return "Save pricing draft before updating Fee.";
  }
  if (input.savedLocalPricingSignature !== input.currentPricingDraftSignature) {
    return "Saving pricing draft before update.";
  }
  return null;
}

async function loadPageContext(projectId: string): Promise<{
  project: Project;
  ltrNumber: string | null;
}> {
  const [project, ltrs] = await Promise.all([
    getProject(projectId),
    listProjectLtrs(projectId),
  ]);
  return {
    project,
    ltrNumber: ltrs.at(-1)?.ltr_number ?? null,
  };
}

function flattenDraftLines(draft: FeeEvaluationDraft | null): FeeEvaluationLineItem[] {
  return draft?.groups.flatMap((group) => group.line_items) ?? [];
}

function buildFeeEvaluationIdentityLine(contextState: FeePageContextState): string {
  if (contextState.kind !== "ready") {
    return "Fee Evaluation";
  }

  return buildProjectIdentityLine({
    project: contextState.project,
    latestLtr: contextState.ltrNumber,
    projectId: contextState.project.project_id,
  });
}

function contextFromPricingDraftResponse(
  response: FeeEvaluationPricingDraftResponse
): PricingDraftContext {
  return {
    confirmedMatrixId: response.current_confirmed_matrix_id,
    confirmedRevision: response.current_confirmed_revision,
    feeRuleVersionId: response.current_fee_rule_version_id,
  };
}

function pricingContextEquals(
  left: PricingDraftContext,
  right: PricingDraftContext
): boolean {
  return (
    left.confirmedMatrixId === right.confirmedMatrixId &&
    left.confirmedRevision === right.confirmedRevision &&
    left.feeRuleVersionId === right.feeRuleVersionId
  );
}

function pricingDraftRestorePayload(
  payload: FeeEvaluationEditedFileExportRequest,
  context: PricingDraftContext
): FeeEvaluationPricingDraftSaveRequest {
  return {
    ...payload,
    expected_confirmed_matrix_id: context.confirmedMatrixId,
    expected_confirmed_revision: context.confirmedRevision,
    expected_fee_rule_version_id: context.feeRuleVersionId,
  };
}

function pricingDraftSignature(payload: FeeEvaluationEditedFileExportRequest): string {
  return JSON.stringify(payload);
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === "AbortError";
}

function readonlyAwareErrorMessage(error: unknown, fallback: string): string {
  const detail =
    error && typeof error === "object" && "detail" in error
      ? (error as { detail: unknown }).detail
      : null;
  if (
    isProjectLifecycleReadonlyErrorDetail(detail)
  ) {
    return deriveReadonlyApiErrorMessage(detail);
  }
  return error instanceof ApiRequestError ? error.message : fallback;
}

type AutosaveSettlement =
  | { status: "settled"; result: FeeEvaluationPricingDraftResponse | null }
  | { status: "timeout" };

function waitForAutosaveSettlement(
  promise: Promise<FeeEvaluationPricingDraftResponse | null> | null,
  timeoutMs = 1500
): Promise<AutosaveSettlement> {
  if (!promise) {
    return Promise.resolve({ status: "settled", result: null });
  }
  return Promise.race([
    promise
      .then((result) => ({ status: "settled" as const, result }))
      .catch(() => ({ status: "settled" as const, result: null })),
    new Promise<{ status: "timeout" }>((resolve) =>
      window.setTimeout(() => resolve({ status: "timeout" }), timeoutMs)
    ),
  ]);
}

class FeeEvaluationSessionCancelError extends Error {}

function feeFileDownloadBlocker(draftState: DraftLoadState): string | null {
  if (draftState.kind === "loading") {
    return "Waiting for Fee Evaluation draft.";
  }
  if (draftState.kind === "not_ready") {
    return "Confirm Matrix authority before generating the Fee file.";
  }
  if (draftState.kind === "error") {
    return draftState.message;
  }
  return null;
}

function buildEditedExportPayload(
  rows: ReturnType<typeof buildFeeEvaluationPreviewRows>,
  costPreviewValues: typeof EMPTY_COST_PREVIEW_VALUES
): FeeEvaluationEditedFileExportRequest {
  return {
    rows: rows
      .filter((row) => row.rowKind === "matrix_step")
      .map((row) => ({
        source_line_id: row.sourceLineId,
        confirmed_group_id: row.confirmedGroupId,
        confirmed_row_id: row.confirmedRowId,
        step_token: row.stepToken === "-" ? "" : row.stepToken,
        step_index: row.stepIndex,
        spend_time: row.spendTime,
        unit_price: row.unitPrice,
        unit_type: row.unitType,
        units: row.units,
        base_fee: row.baseFee,
        discount: row.discount,
        testing_fee: row.testingFee,
        notes: row.notes,
      })),
    summary: {
      condition_confirmation_spend_time:
        costPreviewValues.conditionConfirmationSpendTime,
      external_cost: costPreviewValues.externalCost,
      external_cost_note: costPreviewValues.externalCostNote,
      lab_manpower_hourly_rate: costPreviewValues.labManpowerHourlyRate,
    },
    manual_rows: rows
      .filter(
        (row) =>
          row.rowKind === "sample_preparation" ||
          (row.rowKind === "manual_trailing" &&
            row.lineId === "manual-report-preparation")
      )
      .map((row) => ({
        row_kind:
          row.rowKind === "sample_preparation"
            ? ("sample_preparation" as const)
            : ("report_preparation" as const),
        confirmed_group_id:
          row.rowKind === "sample_preparation" ? row.confirmedGroupId : undefined,
        group_key: row.rowKind === "sample_preparation" ? row.groupKey : undefined,
        group_label:
          row.rowKind === "sample_preparation" ? row.groupLabel : undefined,
        spend_time: row.spendTime,
        unit_price: row.unitPrice,
        unit_type: row.unitType,
        units: row.units,
        base_fee: row.baseFee,
        discount: row.discount,
        testing_fee: row.testingFee,
        notes: row.notes,
      })),
  };
}

function isErrorDetailObject(
  detail: unknown
): detail is { manual_cleanup_warning?: string | null } {
  return Boolean(detail) && typeof detail === "object";
}

function downloadBlob(blob: Blob, fileName: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = fileName;
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

function feeFileNameFromPageContext(input: {
  projectId: string;
  contextState: FeePageContextState;
  draftState: DraftLoadState;
  responseFileName: string | null;
}): string {
  if (input.contextState.kind !== "ready") {
    return input.responseFileName ?? defaultFeeFileName(input.projectId);
  }
  const identity =
    input.contextState.ltrNumber ??
    input.contextState.project.project_no ??
    input.projectId;
  return `${safeFeeFileName(identity)} Fee Evaluation Draft ${fileTimestamp()}.xls`;
}

function defaultFeeFileName(projectId: string): string {
  return `${safeFeeFileName(projectId)} Fee Evaluation Draft ${fileTimestamp()}.xls`;
}

function safeFeeFileName(value: string): string {
  const safe = value.replace(/[<>:"/\\|?*\x00-\x1f]+/g, "_").trim();
  return safe || "project";
}

function fileTimestamp(): string {
  const now = new Date();
  const pad = (value: number): string => String(value).padStart(2, "0");
  return [
    now.getFullYear(),
    pad(now.getMonth() + 1),
    pad(now.getDate()),
    pad(now.getHours()),
    pad(now.getMinutes()),
    pad(now.getSeconds()),
  ].join("");
}

function businessReadableDownloadError(error: ApiRequestError): string {
  if (error.status === 503) {
    return error.message;
  }
  if (error.status === 404) {
    if (error.message.toLowerCase().includes("active confirmed matrix")) {
      return "Confirm Matrix authority before generating the Fee file.";
    }
    if (error.message) {
      return error.message;
    }
    return "Confirm Matrix authority before generating the Fee file.";
  }
  return error.message || "Fee file generation failed.";
}
