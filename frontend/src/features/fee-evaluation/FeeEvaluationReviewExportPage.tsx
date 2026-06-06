import {
  useEffect,
  useMemo,
  useState,
  type Dispatch,
  type ReactElement,
  type SetStateAction,
} from "react";
import {
  ApiRequestError,
  exportConfirmedMatrixFeeEvaluation,
  fetchConfirmedMatrixFeeDraft,
  getLatestProjectFolder,
  getProject,
  getProjectOutputStatusSummary,
  listProjectLtrs,
  type FeeEvaluationDraft,
  type FeeEvaluationExportResponse,
  type FeeEvaluationLineItem,
  type Project,
  type ProjectOutputStatusItem,
} from "../../api/client";
import {
  FeeEvaluationReviewDetails,
  type FeeLineFilter,
} from "./FeeEvaluationReviewDetails";
import { FeeEvaluationPreviewTable } from "./FeeEvaluationPreviewTable";
import {
  buildFeeEvaluationPreviewHeader,
  buildFeeEvaluationPreviewRows,
  buildFeeEvaluationPreviewTotals,
} from "./feeEvaluationPreviewModel";

const MATRIX_BASIC_FILL_TEMPLATE_PATH =
  "D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls";

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
      projectFolderPath: string | null;
      outputStatus: ProjectOutputStatusItem | null;
    }
  | { kind: "error"; message: string };

type ExportState =
  | { kind: "idle" }
  | { kind: "running" }
  | { kind: "success"; result: FeeEvaluationExportResponse }
  | { kind: "error"; message: string; manualCleanupWarning?: string | null };

type FeeEvaluationReviewExportPageProps = {
  projectId: string;
  onBackToWorkbench: () => void;
};

export function FeeEvaluationReviewExportPage({
  projectId,
  onBackToWorkbench,
}: FeeEvaluationReviewExportPageProps): ReactElement {
  const [contextState, setContextState] = useState<FeePageContextState>({
    kind: "loading",
  });
  const [draftState, setDraftState] = useState<DraftLoadState>({ kind: "loading" });
  const [filter, setFilter] = useState<FeeLineFilter>("all");
  const [groupFilter, setGroupFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [approvedBy, setApprovedBy] = useState("");
  const [outputFileName, setOutputFileName] = useState("");
  const [exportState, setExportState] = useState<ExportState>({ kind: "idle" });

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
    void fetchConfirmedMatrixFeeDraft(projectId)
      .then((draft) => {
        if (active) {
          setDraftState({ kind: "ready", draft });
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
  const previewRows = useMemo(() => buildFeeEvaluationPreviewRows(draft), [draft]);
  const previewHeader = useMemo(
    () =>
      buildFeeEvaluationPreviewHeader({
        ltrNumber: contextState.kind === "ready" ? contextState.ltrNumber : null,
        requestor: contextState.kind === "ready" ? contextState.project.requestor : null,
      }),
    [contextState]
  );
  const previewTotals = useMemo(
    () => buildFeeEvaluationPreviewTotals(draft, approvedBy),
    [approvedBy, draft]
  );
  const groupOptions = useMemo(
    () => Array.from(new Set(lines.map((line) => line.group_label))).sort(),
    [lines]
  );
  const visibleLines = useMemo(
    () => filterLines(lines, filter, groupFilter, search),
    [filter, groupFilter, lines, search]
  );
  const projectFolderPath =
    contextState.kind === "ready" ? contextState.projectFolderPath : null;
  const exportDisabledReason = exportBlocker(draftState, contextState);

  async function handleExport(): Promise<void> {
    if (exportDisabledReason || !projectFolderPath) {
      return;
    }
    setExportState({ kind: "running" });
    try {
      const result = await exportConfirmedMatrixFeeEvaluation(projectId, {
        template_path: MATRIX_BASIC_FILL_TEMPLATE_PATH,
        output_dir: projectFolderPath,
        output_file_name: normalizeOutputFileName(outputFileName),
        overwrite: false,
        allow_review_required: true,
        fill_mode: "matrix_basic",
        approved_by: emptyToNull(approvedBy),
      });
      setExportState({ kind: "success", result });
      await refreshFeeOutputStatus(projectId, setContextState);
    } catch (error: unknown) {
      const detail =
        error instanceof ApiRequestError && isErrorDetailObject(error.detail)
          ? error.detail
          : null;
      setExportState({
        kind: "error",
        message:
          error instanceof ApiRequestError
            ? error.message
            : "Fee Evaluation export failed.",
        manualCleanupWarning: detail?.manual_cleanup_warning ?? null,
      });
    }
  }

  return (
    <section className="fee-evaluation-page" aria-label="Fee Evaluation review and export">
      <header className="fee-evaluation-topbar">
        <button
          className="fee-evaluation-back-button"
          type="button"
          onClick={onBackToWorkbench}
        >
          Back to Workbench
        </button>
        <div>
          <p className="eyebrow">Fee Evaluation</p>
          <h2>{contextTitle(contextState)}</h2>
          <p>{contextSubtitle(contextState)}</p>
        </div>
        <div className="fee-evaluation-topbar-status">
          <span>{previewTotals.confirmationLabel}</span>
          <strong>Total fee: {previewTotals.testFeeTotal}</strong>
        </div>
      </header>

      <section className="fee-evaluation-summary-strip" aria-label="Fee summary">
        <SummaryFact label="Pricing status" value={previewTotals.confirmationLabel} />
        <SummaryFact label="Total fee" value={previewTotals.testFeeTotal} />
        <SummaryFact label="Working hours" value={previewTotals.workingHours} />
        <SummaryFact
          label="Rule version"
          value={draft?.header.pricing_rule_version_id ?? "-"}
        />
        <SummaryFact
          label="Pricing effective"
          value={displayValue(draft?.header.pricing_effective_from)}
        />
        <SummaryFact
          label="Output freshness"
          value={outputFreshnessLabel(contextState)}
          detail={outputFreshnessDetail(contextState)}
        />
      </section>

      <section className="fee-evaluation-export-panel" aria-label="Matrix basic fill export">
        <div>
          <p className="eyebrow">Excel output</p>
          <h3>Generate Excel file</h3>
          <p>
            Creates the official Testing Prices workbook from the Matrix structure.
            Pricing fields remain ready for Excel-side completion.
          </p>
        </div>
        <div className="fee-evaluation-export-fields">
          <label>
            Output directory
            <input readOnly value={projectFolderPath ?? ""} placeholder="Project folder is not available" />
          </label>
          <label>
            Approved by
            <input
              value={approvedBy}
              onChange={(event) => setApprovedBy(event.currentTarget.value)}
              placeholder="Optional"
            />
          </label>
          <label>
            File name
            <input
              value={outputFileName}
              onChange={(event) => setOutputFileName(event.currentTarget.value)}
              placeholder="Optional, backend default if blank"
            />
          </label>
        </div>
        <div className="fee-evaluation-export-actions">
          <button
            type="button"
            onClick={handleExport}
            disabled={Boolean(exportDisabledReason) || exportState.kind === "running"}
          >
            {exportState.kind === "running" ? "Generating..." : "Generate Excel file"}
          </button>
          {exportDisabledReason ? (
            <p className="fee-evaluation-export-blocker">{exportDisabledReason}</p>
          ) : (
            <p>
              Review-required lines can export in this mode; the workbook still needs
              manual price confirmation.
            </p>
          )}
        </div>
        <ExportResult state={exportState} />
      </section>

      <FeeEvaluationPreviewTable
        header={previewHeader}
        rows={previewRows}
        totals={previewTotals}
      />

      <FeeEvaluationReviewDetails
        lines={lines}
        visibleLines={visibleLines}
        filter={filter}
        setFilter={setFilter}
        groupFilter={groupFilter}
        setGroupFilter={setGroupFilter}
        search={search}
        setSearch={setSearch}
        groupOptions={groupOptions}
        stateMessage={reviewStateMessage(draftState)}
      />
    </section>
  );
}

function SummaryFact({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail?: string;
}): ReactElement {
  return (
    <div>
      <span>{label}</span>
      <strong>{value}</strong>
      {detail ? <p>{detail}</p> : null}
    </div>
  );
}

function ExportResult({ state }: { state: ExportState }): ReactElement | null {
  if (state.kind === "idle" || state.kind === "running") {
    return null;
  }
  if (state.kind === "success") {
    return (
      <div className="fee-evaluation-export-result" role="status">
        <strong>Generated</strong>
        <p>{state.result.output_path}</p>
        {state.result.warnings.map((warning) => (
          <p key={warning}>{warning}</p>
        ))}
      </div>
    );
  }
  return (
    <div className="fee-evaluation-export-error" role="alert">
      <strong>Export failed</strong>
      <p>{state.message}</p>
      {state.manualCleanupWarning ? <p>{state.manualCleanupWarning}</p> : null}
    </div>
  );
}

async function loadPageContext(projectId: string): Promise<{
  project: Project;
  ltrNumber: string | null;
  projectFolderPath: string | null;
  outputStatus: ProjectOutputStatusItem | null;
}> {
  const [project, ltrs, folderResult, outputStatusResult] = await Promise.all([
    getProject(projectId),
    listProjectLtrs(projectId),
    getLatestProjectFolder(projectId).catch(() => null),
    getProjectOutputStatusSummary(projectId).catch(() => null),
  ]);
  return {
    project,
    ltrNumber: ltrs.at(-1)?.ltr_number ?? null,
    projectFolderPath: folderResult?.project_folder_path ?? null,
    outputStatus:
      outputStatusResult?.items.find(
        (item) => item.output_kind === "fee_evaluation"
      ) ?? null,
  };
}

async function refreshFeeOutputStatus(
  projectId: string,
  setContextState: Dispatch<SetStateAction<FeePageContextState>>
): Promise<void> {
  const outputStatusResult = await getProjectOutputStatusSummary(projectId).catch(() => null);
  const outputStatus =
    outputStatusResult?.items.find((item) => item.output_kind === "fee_evaluation") ?? null;
  setContextState((current) =>
    current.kind === "ready" ? { ...current, outputStatus } : current
  );
}

function flattenDraftLines(draft: FeeEvaluationDraft | null): FeeEvaluationLineItem[] {
  return draft?.groups.flatMap((group) => group.line_items) ?? [];
}

function filterLines(
  lines: FeeEvaluationLineItem[],
  filter: FeeLineFilter,
  groupFilter: string,
  search: string
): FeeEvaluationLineItem[] {
  const query = search.trim().toLowerCase();
  return lines.filter((line) => {
    if (groupFilter !== "all" && line.group_label !== groupFilter) {
      return false;
    }
    if (filter === "review_required" && !line.review_required) {
      return false;
    }
    if (filter === "calculated" && line.status !== "calculated") {
      return false;
    }
    if (filter === "no_rule_match" && line.status !== "no_rule_match") {
      return false;
    }
    if (!query) {
      return true;
    }
    return [
      line.test_item,
      line.group_label,
      line.matched_rule_name,
      line.matched_rule_id,
      line.review_reason,
      line.match_reason,
      ...line.warnings.map((warning) => warning.message),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase()
      .includes(query);
  });
}

function exportBlocker(
  draftState: DraftLoadState,
  contextState: FeePageContextState
): string | null {
  if (contextState.kind === "loading" || draftState.kind === "loading") {
    return "Waiting for project and fee draft status.";
  }
  if (contextState.kind === "error") {
    return contextState.message;
  }
  if (draftState.kind === "not_ready") {
    return "Confirm Matrix authority before generating Fee Evaluation.";
  }
  if (draftState.kind === "error") {
    return draftState.message;
  }
  if (!contextState.projectFolderPath) {
    return "Create the project folder before generating the workbook.";
  }
  return null;
}

function reviewStateMessage(draftState: DraftLoadState): ReactElement | null {
  if (draftState.kind === "loading") {
    return <p className="fee-evaluation-empty">Loading Fee Evaluation draft...</p>;
  }
  if (draftState.kind === "not_ready") {
    return (
      <p className="fee-evaluation-empty">
        No active confirmed Matrix authority yet. Confirm Matrix before fee review.
      </p>
    );
  }
  if (draftState.kind === "error") {
    return <p className="error">{draftState.message}</p>;
  }
  return null;
}

function contextTitle(state: FeePageContextState): string {
  if (state.kind !== "ready") {
    return "Project fee review";
  }
  const identity = state.ltrNumber ?? state.project.project_no ?? state.project.project_id;
  return `${identity} | ${state.project.product_name}`;
}

function contextSubtitle(state: FeePageContextState): string {
  if (state.kind === "loading") {
    return "Loading project context.";
  }
  if (state.kind === "error") {
    return state.message;
  }
  return state.projectFolderPath
    ? `Output folder: ${state.projectFolderPath}`
    : "Project folder is required before export.";
}

function outputFreshnessLabel(state: FeePageContextState): string {
  if (state.kind !== "ready" || !state.outputStatus) {
    return "Missing";
  }
  if (state.outputStatus.status === "current") {
    return "Current";
  }
  if (state.outputStatus.status === "stale") {
    return "Stale";
  }
  if (state.outputStatus.status === "failed") {
    return "Failed";
  }
  if (state.outputStatus.status === "manual") {
    return "Manual";
  }
  return "Missing";
}

function outputFreshnessDetail(state: FeePageContextState): string {
  if (state.kind !== "ready" || !state.outputStatus) {
    return "No Fee Evaluation output recorded.";
  }
  return state.outputStatus.reason;
}

function displayValue(value: string | null | undefined): string {
  const normalized = value?.trim() ?? "";
  return normalized.length > 0 ? normalized : "-";
}

function emptyToNull(value: string): string | null {
  const normalized = value.trim();
  return normalized.length > 0 ? normalized : null;
}

function normalizeOutputFileName(value: string): string | null {
  const normalized = value.trim();
  if (!normalized) {
    return null;
  }
  return /\.(xls|xlsx)$/i.test(normalized) ? normalized : `${normalized}.xls`;
}

function isErrorDetailObject(
  detail: unknown
): detail is { manual_cleanup_warning?: string | null } {
  return Boolean(detail) && typeof detail === "object";
}
