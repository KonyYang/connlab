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
  discardFeeEvaluationPricingDraft,
  fetchConfirmedMatrixFeeDraft,
  generateConfirmedMatrixFeeFileDownload,
  getConfirmedFeeLatest,
  getFeeEvaluationPricingDraft,
  getProject,
  listProjectLtrs,
  saveFeeEvaluationPricingDraft,
  type ConfirmedFeeLatestResponse,
  type FeeEvaluationDraft,
  type FeeEvaluationEditedFileExportRequest,
  type FeeEvaluationLineItem,
  type FeeEvaluationPricingDraftResponse,
  type Project,
} from "../../api/client";
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
  const [baselinePricingSignature, setBaselinePricingSignature] = useState<
    string | null
  >(null);
  const [hasUserEditedPricingDraft, setHasUserEditedPricingDraft] = useState(false);
  const [needsInitialSeedSave, setNeedsInitialSeedSave] = useState(false);
  const [isDiscardingPricingDraft, setIsDiscardingPricingDraft] = useState(false);
  const [activePricingContext, setActivePricingContext] =
    useState<PricingDraftContext | null>(null);
  const autosaveTimeoutRef = useRef<number | null>(null);
  const autosaveGenerationRef = useRef(0);
  const autosaveInFlightRef =
    useRef<Promise<FeeEvaluationPricingDraftResponse | null> | null>(null);
  const autosaveAbortControllerRef = useRef<AbortController | null>(null);
  const latestAutosaveResultRef = useRef<FeeEvaluationPricingDraftResponse | null>(
    null
  );
  const discardingRef = useRef(false);

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
    setDraftState({ kind: "loading" });
    setPreviewEdits({});
    setCostPreviewValues(EMPTY_COST_PREVIEW_VALUES);
    setSaveState({ kind: "loading" });
    setLatestSavedPricingDraftId(null);
    setPricingDraftLoadStatus("loading");
    setSavedLocalPricingSignature(null);
    setBaselinePricingSignature(null);
    setHasUserEditedPricingDraft(false);
    setNeedsInitialSeedSave(false);
    setActivePricingContext(null);
    latestAutosaveResultRef.current = null;
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
          setBaselinePricingSignature(null);
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
          setActivePricingContext(contextFromPricingDraftResponse(result));
          setLatestSavedPricingDraftId(result.saved_draft_edit_id ?? null);
          setPricingDraftLoadStatus("current");
          setHasUserEditedPricingDraft(false);
          setNeedsInitialSeedSave(false);
          if (!result.payload) {
            const currentSignature = pricingDraftSignature(
              buildEditedExportPayload(sourcePreviewRows, costPreviewValues)
            );
            setSavedLocalPricingSignature(
              result.saved_draft_edit_id ? currentSignature : null
            );
            setBaselinePricingSignature(currentSignature);
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
          setSavedLocalPricingSignature(hydratedSignature);
          setBaselinePricingSignature(hydratedSignature);
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
          setActivePricingContext(contextFromPricingDraftResponse(result));
          setLatestSavedPricingDraftId(null);
          setPricingDraftLoadStatus("stale");
          setSavedLocalPricingSignature(null);
          setBaselinePricingSignature(
            pricingDraftSignature(
              buildEditedExportPayload(sourcePreviewRows, costPreviewValues)
            )
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
        setActivePricingContext(contextFromPricingDraftResponse(result));
        setLatestSavedPricingDraftId(null);
        setPricingDraftLoadStatus("missing");
        setSavedLocalPricingSignature(null);
        setBaselinePricingSignature(
          pricingDraftSignature(
            buildEditedExportPayload(sourcePreviewRows, costPreviewValues)
          )
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
  const confirmFeeDisabledReason = confirmFeeBlocker({
    draftState,
    confirmedFeeState,
    isDiscardingPricingDraft,
    latestSavedPricingDraftId,
    pricingDraftLoadStatus,
    saveState,
    savedLocalPricingSignature,
    currentPricingDraftSignature,
  });
  const generateDisabledReason = feeFileDownloadBlocker(draftState);

  function applySavedPricingDraftResult(
    result: FeeEvaluationPricingDraftResponse,
    signature: string
  ): void {
    setActivePricingContext(contextFromPricingDraftResponse(result));
    if (result.status === "current") {
      const savedDraftId = result.saved_draft_edit_id ?? null;
      setLatestSavedPricingDraftId(savedDraftId);
      setPricingDraftLoadStatus("current");
      setSavedLocalPricingSignature(savedDraftId ? signature : null);
      setBaselinePricingSignature(signature);
      setHasUserEditedPricingDraft(false);
      setNeedsInitialSeedSave(false);
      setSaveState(
        savedDraftId
          ? { kind: "saved", message: "Saved pricing draft." }
          : {
              kind: "error",
              message: "Save returned no pricing draft id. Retry before confirming.",
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
      discardingRef.current ||
      isDiscardingPricingDraft
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
      if (discardingRef.current) {
        return;
      }
      setSaveState({ kind: "saving" });
      const abortController = new AbortController();
      autosaveAbortControllerRef.current = abortController;
      const saveRequest = saveFeeEvaluationPricingDraft(projectId, payload, {
        signal: abortController.signal,
      })
        .then((result) => {
          latestAutosaveResultRef.current = result;
          if (autosaveGenerationRef.current === generation && !discardingRef.current) {
            applySavedPricingDraftResult(result, signature);
          }
          return result;
        })
        .catch((error: unknown) => {
          if (autosaveGenerationRef.current === generation && !discardingRef.current) {
            if (isAbortError(error)) {
              return null;
            }
            setSaveState({
              kind: "error",
              message:
                error instanceof ApiRequestError
                  ? error.message
                  : "Unable to save pricing draft.",
            });
          }
          return null;
        })
        .finally(() => {
          if (autosaveInFlightRef.current === saveRequest) {
            autosaveInFlightRef.current = null;
          }
          if (autosaveAbortControllerRef.current === abortController) {
            autosaveAbortControllerRef.current = null;
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
    isDiscardingPricingDraft,
    needsInitialSeedSave,
    projectId,
  ]);

  async function handleGenerateFeeFile(): Promise<void> {
    if (generateDisabledReason || downloadState.kind === "running") {
      return;
    }
    setDownloadState({ kind: "running" });
    try {
      const response = await generateConfirmedMatrixFeeFileDownload(
        projectId,
        buildEditedExportPayload(previewRows, costPreviewValues)
      );
      downloadBlob(response.blob, response.fileName ?? defaultFeeFileName(projectId));
      setDownloadState({ kind: "success", fileName: response.fileName });
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
          message: "Save pricing draft before confirming Fee.",
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
      setConfirmFeeActionState({ kind: "success", message: "Fee confirmed." });
      onBackToWorkbench();
    } catch (error: unknown) {
      const message =
        error instanceof ApiRequestError ? error.message : "Unable to confirm Fee.";
      setConfirmFeeActionState({ kind: "error", message });
      setSaveState({ kind: "error", message });
    }
  }

  function handleCostPreviewChange(
    field: keyof typeof costPreviewValues,
    value: string
  ): void {
    setCostPreviewValues((current) => ({ ...current, [field]: value }));
    markPricingDraftDirty();
  }

  function handlePreviewRowEditChange(
    lineId: string,
    field: FeeEvaluationEditableField,
    value: string
  ): void {
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
    const latestResult = latestAutosaveResultRef.current;
    const hasDraftToDiscard =
      Boolean(latestResult?.saved_draft_edit_id ?? latestSavedPricingDraftId) ||
      hasUserEditedPricingDraft ||
      Boolean(savedLocalPricingSignature) ||
      saveState.kind === "dirty" ||
      saveState.kind === "saving" ||
      saveState.kind === "error";
    if (!hasDraftToDiscard) {
      onBackToWorkbench();
      return;
    }
    if (!window.confirm("Discard Fee Evaluation pricing edits and return to Workbench?")) {
      return;
    }
    discardingRef.current = true;
    autosaveGenerationRef.current += 1;
    if (autosaveTimeoutRef.current !== null) {
      window.clearTimeout(autosaveTimeoutRef.current);
      autosaveTimeoutRef.current = null;
    }
    autosaveAbortControllerRef.current?.abort();
    setIsDiscardingPricingDraft(true);
    const inFlightResult = await waitForAutosaveOrTimeout(autosaveInFlightRef.current);
    const savedResult = inFlightResult ?? latestAutosaveResultRef.current;
    const context = contextFromMaybeResponse(savedResult) ?? activePricingContext;
    try {
      await discardFeeEvaluationPricingDraft(projectId, {
        expected_pricing_draft_edit_id:
          savedResult?.saved_draft_edit_id ?? latestSavedPricingDraftId,
        expected_confirmed_matrix_id: context?.confirmedMatrixId ?? null,
        expected_confirmed_revision: context?.confirmedRevision ?? null,
        expected_fee_rule_version_id: context?.feeRuleVersionId ?? null,
      });
      onBackToWorkbench();
    } catch (error: unknown) {
      discardingRef.current = false;
      setIsDiscardingPricingDraft(false);
      setSaveState({
        kind: "error",
        message:
          error instanceof Error ? error.message : "Unable to discard pricing draft.",
      });
    }
  }

  return (
    <section className="fee-evaluation-page" aria-label="Fee Evaluation review and export">
      <FeeEvaluationPreviewTable
        costPreviewValues={costPreviewValues}
        costRisk={costRisk}
        confirmFeeActionState={confirmFeeActionState}
        grandCostLabel={grandCostLabel}
        labManpowerCostLabel={labManpowerCostLabel}
        groupFilter={previewGroupFilter}
        groupOptions={groupOptions}
        header={previewHeader}
        downloadState={downloadState}
        generateDisabledReason={generateDisabledReason}
        onCostPreviewChange={handleCostPreviewChange}
        onGenerateFeeFile={handleGenerateFeeFile}
        onGroupFilterChange={setPreviewGroupFilter}
        onRowEditChange={handlePreviewRowEditChange}
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
            "Confirm Fee returns to Workbench after authority is updated."}
        </span>
        <div className="fee-evaluation-completion-actions">
          <button
            type="button"
            onClick={() => void handleBackToWorkbench()}
            disabled={
              confirmFeeActionState.kind === "confirming" || isDiscardingPricingDraft
            }
          >
            {isDiscardingPricingDraft ? "Cancelling..." : "Cancel"}
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
            {confirmFeeActionState.kind === "confirming" ? "Confirming..." : "Confirm Fee"}
          </button>
        </div>
      </footer>
    </section>
  );
}

function confirmFeeBlocker(input: {
  draftState: DraftLoadState;
  confirmedFeeState: ConfirmedFeeLoadState;
  isDiscardingPricingDraft: boolean;
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
    return "Confirm Matrix authority before confirming Fee.";
  }
  if (input.draftState.kind === "error") {
    return input.draftState.message;
  }
  if (input.confirmedFeeState.kind === "loading") {
    return "Waiting for Confirmed Fee status.";
  }
  if (input.isDiscardingPricingDraft) {
    return "Discarding pricing draft.";
  }
  if (input.pricingDraftLoadStatus === "loading") {
    return "Waiting for saved pricing draft.";
  }
  if (input.pricingDraftLoadStatus === "stale") {
    return "Saved pricing draft belongs to an older Matrix or fee rule version.";
  }
  if (input.pricingDraftLoadStatus === "error") {
    return "Reload saved pricing draft before confirming Fee.";
  }
  if (input.saveState.kind === "dirty" || input.saveState.kind === "saving") {
    return "Saving pricing draft before confirm.";
  }
  if (input.saveState.kind === "error") {
    return input.saveState.message;
  }
  if (!input.latestSavedPricingDraftId) {
    return "Save pricing draft before confirming Fee.";
  }
  if (input.savedLocalPricingSignature !== input.currentPricingDraftSignature) {
    return "Saving pricing draft before confirm.";
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

function contextFromPricingDraftResponse(
  response: FeeEvaluationPricingDraftResponse
): PricingDraftContext {
  return {
    confirmedMatrixId: response.current_confirmed_matrix_id,
    confirmedRevision: response.current_confirmed_revision,
    feeRuleVersionId: response.current_fee_rule_version_id,
  };
}

function contextFromMaybeResponse(
  response: FeeEvaluationPricingDraftResponse | null
): PricingDraftContext | null {
  return response ? contextFromPricingDraftResponse(response) : null;
}

function pricingDraftSignature(payload: FeeEvaluationEditedFileExportRequest): string {
  return JSON.stringify(payload);
}

function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === "AbortError";
}

function waitForAutosaveOrTimeout(
  promise: Promise<FeeEvaluationPricingDraftResponse | null> | null,
  timeoutMs = 1500
): Promise<FeeEvaluationPricingDraftResponse | null> {
  if (!promise) {
    return Promise.resolve(null);
  }
  return Promise.race([
    promise.catch(() => null),
    new Promise<null>((resolve) => window.setTimeout(() => resolve(null), timeoutMs)),
  ]);
}

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

function defaultFeeFileName(projectId: string): string {
  return `fee-file-${projectId}.xls`;
}

function businessReadableDownloadError(error: ApiRequestError): string {
  if (error.status === 503) {
    return error.message;
  }
  if (error.status === 404) {
    return "Confirm Matrix authority before generating the Fee file.";
  }
  return error.message || "Fee file generation failed.";
}
