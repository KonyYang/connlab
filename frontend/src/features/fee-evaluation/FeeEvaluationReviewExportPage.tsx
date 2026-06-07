import {
  useEffect,
  useMemo,
  useState,
  type ReactElement,
} from "react";
import {
  ApiRequestError,
  fetchConfirmedMatrixFeeDraft,
  generateConfirmedMatrixFeeFileDownload,
  getProject,
  listProjectLtrs,
  type FeeEvaluationDraft,
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
    void fetchConfirmedMatrixFeeDraft(projectId)
      .then((draft) => {
        if (active) {
          setDraftState({ kind: "ready", draft });
          setPreviewEdits({});
          setCostPreviewValues(EMPTY_COST_PREVIEW_VALUES);
        }
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }
        if (error instanceof ApiRequestError && error.status === 404) {
          setDraftState({ kind: "not_ready" });
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

  const draft = draftState.kind === "ready" ? draftState.draft : null;
  const lines = useMemo(() => flattenDraftLines(draft), [draft]);
  const sourcePreviewRows = useMemo(() => buildFeeEvaluationPreviewRows(draft), [draft]);
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
  const selectedPreviewTotal = useMemo(
    () => buildFeeEvaluationPreviewScopeTotal(previewRows, previewGroupFilter),
    [previewGroupFilter, previewRows]
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
  const labManpowerCostLabel = useMemo(
    () =>
      buildFeeEvaluationLabManpowerCost(
        workingHoursLabel,
        costPreviewValues.labManpowerHourlyRate
      ),
    [costPreviewValues.labManpowerHourlyRate, workingHoursLabel]
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
  const generateDisabledReason = feeFileDownloadBlocker(draftState);

  async function handleGenerateFeeFile(): Promise<void> {
    if (generateDisabledReason || downloadState.kind === "running") {
      return;
    }
    setDownloadState({ kind: "running" });
    try {
      const response = await generateConfirmedMatrixFeeFileDownload(projectId);
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

  function handleCostPreviewChange(
    field: keyof typeof costPreviewValues,
    value: string
  ): void {
    setCostPreviewValues((current) => ({ ...current, [field]: value }));
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
  }

  return (
    <section className="fee-evaluation-page" aria-label="Fee Evaluation review and export">
      <FeeEvaluationPreviewTable
        costPreviewValues={costPreviewValues}
        costRisk={costRisk}
        grandCostLabel={grandCostLabel}
        labManpowerCostLabel={labManpowerCostLabel}
        groupFilter={previewGroupFilter}
        groupOptions={groupOptions}
        header={previewHeader}
        downloadState={downloadState}
        generateDisabledReason={generateDisabledReason}
        onBackToWorkbench={onBackToWorkbench}
        onCostPreviewChange={handleCostPreviewChange}
        onGenerateFeeFile={handleGenerateFeeFile}
        onGroupFilterChange={setPreviewGroupFilter}
        onRowEditChange={handlePreviewRowEditChange}
        scopeFeeLabel={selectedPreviewTotal}
        rows={visiblePreviewRows}
        totals={previewTotals}
      />
    </section>
  );
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
