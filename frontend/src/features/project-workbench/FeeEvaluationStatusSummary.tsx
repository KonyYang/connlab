import { useEffect, useState, type ReactElement } from "react";
import {
  ApiRequestError,
  fetchConfirmedMatrixFeeDraft,
  type FeeEvaluationDraft,
} from "../../api/client";
import type { WorkbenchDocumentStatus } from "./projectWorkbenchVersionSelectors";

type FeeEvaluationStatusState =
  | { kind: "loading" }
  | { kind: "missing" }
  | { kind: "ready"; draft: FeeEvaluationDraft }
  | { kind: "stale"; message: string };

type FeeEvaluationStatusSummaryProps = {
  projectId: string;
  outputStatus: WorkbenchDocumentStatus | null;
  canOpen: boolean;
  onOpenFeeEvaluation: () => void;
};

export function FeeEvaluationStatusSummary({
  projectId,
  outputStatus: _outputStatus,
  canOpen,
  onOpenFeeEvaluation,
}: FeeEvaluationStatusSummaryProps): ReactElement {
  const [state, setState] = useState<FeeEvaluationStatusState>({
    kind: "loading",
  });

  useEffect(() => {
    let active = true;
    setState({ kind: "loading" });
    void fetchConfirmedMatrixFeeDraft(projectId)
      .then((draft) => {
        if (active) {
          setState({ kind: "ready", draft });
        }
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }
        if (error instanceof ApiRequestError && error.status === 404) {
          setState({ kind: "missing" });
          return;
        }
        setState({
          kind: "stale",
          message:
            error instanceof ApiRequestError
              ? error.message
              : "Fee draft status is unavailable.",
        });
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  return (
    <section className="runtime-console-fee" aria-label="Fee Evaluation status">
      <header>
        <p className="eyebrow">Fee Evaluation</p>
      </header>
      <div className="runtime-console-fee-grid">
        <div>
          <p>{totalDetail(state)}</p>
        </div>
      </div>
      <button
        type="button"
        disabled={!(canOpen || state.kind === "ready")}
        onClick={onOpenFeeEvaluation}
      >
        Open Fee Evaluation
      </button>
    </section>
  );
}

function totalDetail(state: FeeEvaluationStatusState): string {
  if (state.kind === "loading") {
    return "Reading active Matrix-derived fee draft.";
  }
  if (state.kind === "missing") {
    return "Total fee: Pending Matrix confirmation.";
  }
  if (state.kind === "stale") {
    return state.message;
  }
  if (state.draft.draft_status === "needs_review") {
    return "Total fee: Pending Excel confirmation.";
  }
  if (state.draft.draft_status === "empty") {
    return "Total fee: No fee rows.";
  }
  return `Total fee: ${formatMoney(state.draft.total_fee)}`;
}

function formatMoney(value: string | null | undefined): string {
  if (!value) {
    return "Pending";
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return value;
  }
  return parsed.toFixed(2);
}
