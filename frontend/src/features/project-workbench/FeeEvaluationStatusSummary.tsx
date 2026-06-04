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
};

export function FeeEvaluationStatusSummary({
  projectId,
  outputStatus,
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
        <p className="eyebrow">Derived output</p>
        <h3>Fee Evaluation</h3>
      </header>
      <div className="runtime-console-fee-grid">
        <div>
          <span>Status</span>
          <strong>{statusLabel(state, outputStatus)}</strong>
          <p>{statusDetail(state, outputStatus)}</p>
        </div>
      </div>
    </section>
  );
}

function statusLabel(
  state: FeeEvaluationStatusState,
  outputStatus: WorkbenchDocumentStatus | null
): string {
  if (outputStatus?.freshness === "stale") {
    return "Stale";
  }
  if (outputStatus?.freshness === "failed") {
    return "Unavailable";
  }
  if (state.kind === "loading") {
    return "Checking";
  }
  if (state.kind === "missing") {
    return "Missing";
  }
  if (state.kind === "stale") {
    return "Stale / unavailable";
  }
  if (state.draft.draft_status === "needs_review") {
    return "Needs review";
  }
  if (state.draft.draft_status === "empty") {
    return "No fee rows";
  }
  return "Draft ready";
}

function statusDetail(
  state: FeeEvaluationStatusState,
  outputStatus: WorkbenchDocumentStatus | null
): string {
  if (outputStatus?.freshness === "stale" || outputStatus?.freshness === "failed") {
    return outputStatus.reason;
  }
  if (state.kind === "loading") {
    return "Reading active Matrix-derived fee draft.";
  }
  if (state.kind === "missing") {
    return "Confirm Matrix authority before fee review.";
  }
  if (state.kind === "stale") {
    return state.message;
  }
  if (state.draft.draft_status === "needs_review") {
    return `${state.draft.review_required_count} line(s) require operator review.`;
  }
  if (state.draft.draft_status === "empty") {
    return "Active Matrix has no fee rows available.";
  }
  if (outputStatus?.freshness === "manual") {
    return outputStatus.reason;
  }
  return "All fee lines are calculated from the active rule version.";
}
