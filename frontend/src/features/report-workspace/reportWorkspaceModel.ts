import type {
  LlcrImportPreview,
  LlcrResultEntry,
  ReportWorkspaceState,
} from "../../api/client";

export type LlcrOutcome = "pass" | "fail" | "not_determined";

export type LlcrDecisionDraft = {
  outcome: LlcrOutcome;
  overrideReason: string;
};

export type LlcrDecisionDrafts = Record<string, LlcrDecisionDraft>;

export type ReportWorkspaceReadiness = {
  canGenerateInitialDraft: boolean;
  initialDraftBlocker: string | null;
  canGenerateLlcrDraft: boolean;
  llcrDraftBlocker: string | null;
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
  let llcrDraftBlocker: string | null = null;
  if (!latestDataset) {
    llcrDraftBlocker = "Confirm an LLCR Result Dataset before generating an LLCR report draft.";
  } else if (
    latestDataset.confirmed_matrix_id !== state.active_confirmed_matrix_id
    || latestDataset.confirmed_matrix_revision !== state.active_confirmed_matrix_revision
  ) {
    llcrDraftBlocker = "The latest LLCR Result Dataset is stale for the active Confirmed Matrix.";
  }

  return {
    canGenerateInitialDraft: initialDraftBlocker === null,
    initialDraftBlocker,
    canGenerateLlcrDraft: llcrDraftBlocker === null,
    llcrDraftBlocker,
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
