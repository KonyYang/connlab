import {
  useEffect,
  useMemo,
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
  listProjectLtrs,
  saveFeeEvaluationPricingDraft,
  type ConfirmedFeeLatestResponse,
  type FeeEvaluationDraft,
  type FeeEvaluationEditedFileExportRequest,
  type FeeEvaluationLineItem,
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

type ConfirmedFeeLoadState =
  | { kind: "loading" }
  | { kind: "ready"; data: ConfirmedFeeLatestResponse }
  | { kind: "error"; message: string };

type ConfirmFeeActionState =
  | { kind: "idle" }
  | { kind: "confirming" }
  | { kind: "success"; message: string }
  | { kind: "error"; message: string };

type ConfirmedFeeViewState = {
  label: string;
  detail: string | null;
  tone: "loading" | "missing" | "current" | "stale" | "dirty" | "error";
};

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
  const [confirmedBy, setConfirmedBy] = useState("Lab User");
  const [latestSavedPricingDraftId, setLatestSavedPricingDraftId] = useState<
    string | null
  >(null);
  const [pricingDraftLoadStatus, setPricingDraftLoadStatus] =
    useState<PricingDraftLoadStatus>("loading");
  const [pricingDraftDirtySinceConfirm, setPricingDraftDirtySinceConfirm] =
    useState(false);

  useEffect(() => {
    let active = true;
    setContextState({ kind: "loading" });
    setConfirmedBy("Lab User");
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
    setPricingDraftDirtySinceConfirm(false);
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
          setLatestSavedPricingDraftId(result.saved_draft_edit_id ?? null);
          setPricingDraftLoadStatus("current");
          setPricingDraftDirtySinceConfirm(false);
          if (!result.payload) {
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
          setLatestSavedPricingDraftId(null);
          setPricingDraftLoadStatus("stale");
          setPricingDraftDirtySinceConfirm(false);
          setSaveState({
            kind: "stale",
            message:
              "Saved pricing draft belongs to an older Matrix or fee rule version. Current defaults are shown.",
          });
          return;
        }
        setLatestSavedPricingDraftId(null);
        setPricingDraftLoadStatus("missing");
        setPricingDraftDirtySinceConfirm(false);
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
  const confirmedFeeViewState = useMemo(
    () =>
      buildConfirmedFeeViewState({
        confirmedFeeState,
        latestSavedPricingDraftId,
        pricingDraftLoadStatus,
        pricingDraftDirtySinceConfirm,
      }),
    [
      confirmedFeeState,
      latestSavedPricingDraftId,
      pricingDraftDirtySinceConfirm,
      pricingDraftLoadStatus,
    ]
  );
  const confirmFeeDisabledReason = confirmFeeBlocker({
    draftState,
    confirmedBy,
    confirmedFeeState,
  });
  const generateDisabledReason = feeFileDownloadBlocker(draftState);

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

  async function handleSavePricingDraft(): Promise<void> {
    if (draftState.kind !== "ready" || saveState.kind === "saving") {
      return;
    }
    setSaveState({ kind: "saving" });
    try {
      const result = await saveFeeEvaluationPricingDraft(
        projectId,
        buildEditedExportPayload(previewRows, costPreviewValues)
      );
      if (result.status === "current") {
        setLatestSavedPricingDraftId(result.saved_draft_edit_id ?? null);
        setPricingDraftLoadStatus("current");
        setPricingDraftDirtySinceConfirm(false);
        setSaveState({ kind: "saved", message: "Saved pricing draft." });
        return;
      }
      setLatestSavedPricingDraftId(null);
      setPricingDraftLoadStatus("stale");
      setSaveState({
        kind: "stale",
        message: "Saved draft is not current for this Matrix or fee rule version.",
      });
    } catch (error: unknown) {
      setSaveState({
        kind: "error",
        message:
          error instanceof ApiRequestError
            ? error.message
            : "Unable to save pricing draft.",
      });
    }
  }

  async function handleConfirmFee(): Promise<void> {
    if (
      draftState.kind !== "ready" ||
      confirmFeeActionState.kind === "confirming" ||
      confirmFeeDisabledReason
    ) {
      if (!confirmedBy.trim()) {
        setConfirmFeeActionState({
          kind: "error",
          message: "Enter confirmed by before confirming.",
        });
      }
      return;
    }
    setConfirmFeeActionState({ kind: "confirming" });
    setSaveState({ kind: "saving" });
    try {
      const saveResult = await saveFeeEvaluationPricingDraft(
        projectId,
        buildEditedExportPayload(previewRows, costPreviewValues)
      );
      if (saveResult.status !== "current") {
        setLatestSavedPricingDraftId(null);
        setPricingDraftLoadStatus("stale");
        setSaveState({
          kind: "stale",
          message: "Saved draft is not current for this Matrix or fee rule version.",
        });
        setConfirmFeeActionState({
          kind: "error",
          message: "Saved draft is not current for this Matrix or fee rule version.",
        });
        return;
      }

      const savedDraftId = saveResult.saved_draft_edit_id ?? null;
      setLatestSavedPricingDraftId(savedDraftId);
      setPricingDraftLoadStatus("current");
      setSaveState({ kind: "saved", message: "Saved pricing draft." });
      if (!savedDraftId) {
        setConfirmFeeActionState({
          kind: "error",
          message:
            "Save returned no pricing draft id. Refresh and save again before confirming.",
        });
        return;
      }

      const result = await confirmFeeVersion(projectId, {
        confirmed_by: confirmedBy.trim(),
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
      setPricingDraftDirtySinceConfirm(false);
      setConfirmFeeActionState({ kind: "success", message: "Fee confirmed." });
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
    setPricingDraftDirtySinceConfirm(true);
    setConfirmFeeActionState((current) =>
      current.kind === "confirming" ? current : { kind: "idle" }
    );
    setSaveState((current) =>
      current.kind === "loading" || current.kind === "saving"
        ? current
        : { kind: "dirty" }
    );
  }

  return (
    <section className="fee-evaluation-page" aria-label="Fee Evaluation review and export">
      <FeeEvaluationPreviewTable
        costPreviewValues={costPreviewValues}
        costRisk={costRisk}
        confirmFeeActionState={confirmFeeActionState}
        confirmFeeDisabledReason={confirmFeeDisabledReason}
        confirmedBy={confirmedBy}
        confirmedFeeViewState={confirmedFeeViewState}
        grandCostLabel={grandCostLabel}
        labManpowerCostLabel={labManpowerCostLabel}
        groupFilter={previewGroupFilter}
        groupOptions={groupOptions}
        header={previewHeader}
        downloadState={downloadState}
        generateDisabledReason={generateDisabledReason}
        onBackToWorkbench={onBackToWorkbench}
        onCostPreviewChange={handleCostPreviewChange}
        onConfirmFee={handleConfirmFee}
        onConfirmedByChange={setConfirmedBy}
        onGenerateFeeFile={handleGenerateFeeFile}
        onGroupFilterChange={setPreviewGroupFilter}
        onRowEditChange={handlePreviewRowEditChange}
        onSavePricingDraft={handleSavePricingDraft}
        saveState={saveState}
        scopeFeeLabel={selectedPreviewTotal}
        rows={visiblePreviewRows}
        totals={previewTotals}
      />
    </section>
  );
}

function buildConfirmedFeeViewState(input: {
  confirmedFeeState: ConfirmedFeeLoadState;
  latestSavedPricingDraftId: string | null;
  pricingDraftLoadStatus: PricingDraftLoadStatus;
  pricingDraftDirtySinceConfirm: boolean;
}): ConfirmedFeeViewState {
  if (input.confirmedFeeState.kind === "loading") {
    return {
      label: "Checking Confirmed Fee",
      detail: null,
      tone: "loading",
    };
  }
  if (input.confirmedFeeState.kind === "error") {
    return {
      label: "Confirmed Fee status unavailable",
      detail: input.confirmedFeeState.message,
      tone: "error",
    };
  }
  const confirmedFee = input.confirmedFeeState.data.confirmed_fee ?? null;
  if (!confirmedFee) {
    return {
      label: "Not confirmed",
      detail: "Save the current pricing draft, then confirm.",
      tone: "missing",
    };
  }
  if (input.confirmedFeeState.data.status === "stale") {
    return {
      label: "Confirmed Fee stale",
      detail: "Matrix or fee rule version changed after confirmation.",
      tone: "stale",
    };
  }
  if (input.pricingDraftDirtySinceConfirm) {
    return {
      label: "Unconfirmed local changes",
      detail: "Save and confirm again after reviewing the local pricing changes.",
      tone: "dirty",
    };
  }
  if (
    input.latestSavedPricingDraftId &&
    confirmedFee.pricing_draft_edit_id !== input.latestSavedPricingDraftId
  ) {
    return {
      label: "Unconfirmed saved changes",
      detail: "Confirm again after reviewing the latest saved pricing draft.",
      tone: "dirty",
    };
  }
  if (input.pricingDraftLoadStatus === "loading") {
    return {
      label: "Checking pricing draft",
      detail: null,
      tone: "loading",
    };
  }
  if (
    input.pricingDraftLoadStatus === "missing" ||
    input.pricingDraftLoadStatus === "stale"
  ) {
    return {
      label: "Unconfirmed pricing draft",
      detail: "Save the current pricing draft before relying on this confirmation.",
      tone: "dirty",
    };
  }
  if (input.pricingDraftLoadStatus === "error") {
    return {
      label: "Pricing draft status unavailable",
      detail: "Reload the saved pricing draft before relying on this confirmation.",
      tone: "error",
    };
  }
  return {
    label: "Confirmed",
    detail: `Confirmed by ${confirmedFee.confirmed_by}.`,
    tone: "current",
  };
}

function confirmFeeBlocker(input: {
  draftState: DraftLoadState;
  confirmedBy: string;
  confirmedFeeState: ConfirmedFeeLoadState;
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
  if (!input.confirmedBy.trim()) {
    return "Enter confirmed by before confirming.";
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
