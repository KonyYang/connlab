import type {
  CurrentReport,
  LlcrImportPreview,
  LlcrResultEntry,
  ReportWorkspaceState,
} from "../../api/client";

export type ReportEntryState = {
  kind: "generate" | "publish" | "ready" | "managed" | "blocked";
  title: string;
  description: string;
  statusLabel: string;
  locationLabel: string | null;
};

export function deriveReportEntryState(
  report: CurrentReport | null
): ReportEntryState {
  if (!report || report.status === "missing") {
    return {
      kind: "generate",
      title: "Create the initial report",
      description: "Generate the first report from the approved E-3707_H template.",
      statusLabel: "No current report",
      locationLabel: null,
    };
  }
  if (report.status === "ambiguous") {
    return {
      kind: "blocked",
      title: "Resolve the report conflict",
      description: "Keep exactly one current internal report before continuing.",
      statusLabel: "Multiple reports found",
      locationLabel: "Official project folder",
    };
  }
  if (report.mode === "official") {
    return {
      kind: "ready",
      title: "Current report ready",
      description: "The official project report is ready for controlled section updates.",
      statusLabel: "Official project report",
      locationLabel: "Official project folder",
    };
  }
  if (report.can_publish_to_official) {
    return {
      kind: "publish",
      title: "Publish current report",
      description: "Publish the existing initialized draft without rebuilding or moving it.",
      statusLabel: "ConnLab managed draft",
      locationLabel: "Destination: Official project folder",
    };
  }
  return {
    kind: "managed",
    title: "Current report draft",
    description: "The initialized report remains in ConnLab until a project folder is available.",
    statusLabel: "ConnLab managed draft",
    locationLabel: "ConnLab managed storage",
  };
}

export type LlcrOutcome = "pass" | "fail" | "not_determined";

export type LlcrDecisionDraft = {
  outcome: LlcrOutcome;
  overrideReason: string;
};

export type LlcrDecisionDrafts = Record<string, LlcrDecisionDraft>;

export type ReportWorkspaceReadiness = {
  canGenerateInitialDraft: boolean;
  initialDraftBlocker: string | null;
  canUpdateLlcr: boolean;
  llcrUpdateBlocker: string | null;
};

export function deriveReportWorkspaceReadiness(
  state: ReportWorkspaceState
): ReportWorkspaceReadiness {
  let initialDraftBlocker: string | null = null;
  if (state.basic_information_status !== "confirmed") {
    initialDraftBlocker = "Confirm Basic Information before generating a report draft.";
  } else if (!state.active_confirmed_matrix_id) {
    initialDraftBlocker = "Activate a Confirmed Matrix before generating a report draft.";
  }

  const latestDataset = state.datasets.at(-1) ?? null;
  let llcrUpdateBlocker: string | null = null;
  if (!latestDataset) {
    llcrUpdateBlocker = "Confirm an LLCR Result Dataset before updating the current report.";
  } else if (
    latestDataset.confirmed_matrix_id !== state.active_confirmed_matrix_id
    || latestDataset.confirmed_matrix_revision !== state.active_confirmed_matrix_revision
  ) {
    llcrUpdateBlocker = "The latest LLCR Result Dataset is stale for the active Confirmed Matrix.";
  }

  return {
    canGenerateInitialDraft: initialDraftBlocker === null,
    initialDraftBlocker,
    canUpdateLlcr: llcrUpdateBlocker === null,
    llcrUpdateBlocker,
  };
}

export function createLlcrDecisionDrafts(preview: LlcrImportPreview): LlcrDecisionDrafts {
  return Object.fromEntries(
    preview.entries.map((entry) => [
      entry.result_id,
      { outcome: entry.provisional_outcome, overrideReason: "" },
    ])
  );
}

export function validateLlcrConfirmation(
  preview: LlcrImportPreview,
  drafts: LlcrDecisionDrafts
): string[] {
  const errors: string[] = [];
  if (!preview.can_confirm || preview.diagnostics.some((item) => item.severity === "error")) {
    errors.push("Resolve every blocking diagnostic before confirmation.");
  }
  for (const entry of preview.entries) {
    const draft = drafts[entry.result_id];
    if (!draft) {
      errors.push(`${entry.report_target} needs a final outcome.`);
      continue;
    }
    if (draft.outcome !== entry.provisional_outcome && !draft.overrideReason.trim()) {
      errors.push(`${entry.report_target} needs an override reason.`);
    }
  }
  return errors;
}

export function buildLlcrConfirmationDecisions(
  preview: LlcrImportPreview,
  drafts: LlcrDecisionDrafts
): Array<{ result_id: string; outcome: LlcrOutcome; override_reason: string | null }> {
  return preview.entries.map((entry) => {
    const draft = drafts[entry.result_id];
    return {
      result_id: entry.result_id,
      outcome: draft.outcome,
      override_reason:
        draft.outcome === entry.provisional_outcome ? null : draft.overrideReason.trim(),
    };
  });
}

export function formatLlcrSummary(entry: LlcrResultEntry): string {
  return `${formatSummaryDecimal(entry.summary_min)} / ${formatSummaryDecimal(entry.summary_max)} / ${formatSummaryDecimal(entry.summary_average)} ${entry.unit}`;
}

function formatSummaryDecimal(value: string): string {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return value;
  }
  return parsed.toLocaleString("en-US", {
    maximumSignificantDigits: 8,
    useGrouping: false,
  });
}
