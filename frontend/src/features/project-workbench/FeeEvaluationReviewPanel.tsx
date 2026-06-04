import { useEffect, useMemo, useState, type ReactElement } from "react";
import {
  ApiRequestError,
  fetchConfirmedMatrixFeeDraft,
  type FeeEvaluationDraft,
  type FeeEvaluationLineItem,
} from "../../api/client";

type FeeEvaluationReviewState =
  | { kind: "loading" }
  | { kind: "not_ready" }
  | { kind: "ready"; draft: FeeEvaluationDraft }
  | { kind: "error"; message: string };

type LocalFeeLineOverride = {
  reviewStatus: "pending" | "accepted" | "needs_manual_price";
  units: string;
  baseFee: string;
  discountPercent: string;
};

type FeeEvaluationReviewPanelProps = {
  projectId: string;
  ltrNumber?: string | null;
  projectDescription?: string | null;
};

export function FeeEvaluationReviewPanel({
  projectId,
  ltrNumber,
  projectDescription,
}: FeeEvaluationReviewPanelProps): ReactElement {
  const [state, setState] = useState<FeeEvaluationReviewState>({
    kind: "loading",
  });
  const [overrides, setOverrides] = useState<Record<string, LocalFeeLineOverride>>(
    {}
  );

  useEffect(() => {
    let active = true;
    setState({ kind: "loading" });
    setOverrides({});
    void fetchConfirmedMatrixFeeDraft(projectId)
      .then((draft) => {
        if (!active) {
          return;
        }
        setState({ kind: "ready", draft });
        setOverrides(buildInitialOverrides(draft));
      })
      .catch((error: unknown) => {
        if (!active) {
          return;
        }
        if (error instanceof ApiRequestError && error.status === 404) {
          setState({ kind: "not_ready" });
          return;
        }
        const message =
          error instanceof ApiRequestError
            ? error.message
            : "Unable to load Fee Evaluation draft.";
        setState({ kind: "error", message });
      });
    return () => {
      active = false;
    };
  }, [projectId]);

  const hasLocalChanges = useMemo(() => {
    if (state.kind !== "ready") {
      return false;
    }
    const initial = buildInitialOverrides(state.draft);
    return Object.entries(overrides).some(([lineId, override]) => {
      const original = initial[lineId];
      return original ? !sameOverride(original, override) : true;
    });
  }, [overrides, state]);

  if (state.kind === "loading") {
    return (
      <section className="runtime-console-fee-review" aria-label="Fee Evaluation">
        <p className="fine-print">Loading Fee Evaluation draft...</p>
      </section>
    );
  }

  if (state.kind === "not_ready") {
    return (
      <section className="runtime-console-fee-review" aria-label="Fee Evaluation">
        <header>
          <p className="eyebrow">Fee Evaluation</p>
          <h3>Fee Evaluation</h3>
        </header>
        <p className="runtime-console-matrix-projection-empty">
          No active confirmed matrix yet. Confirm Matrix authority first.
        </p>
      </section>
    );
  }

  if (state.kind === "error") {
    return (
      <section className="runtime-console-fee-review" aria-label="Fee Evaluation">
        <header>
          <p className="eyebrow">Fee Evaluation</p>
          <h3>Fee Evaluation</h3>
        </header>
        <p className="error">{state.message}</p>
      </section>
    );
  }

  const { draft } = state;
  const lineCount = draft.groups.reduce(
    (count, group) => count + group.line_items.length,
    0
  );
  const statusSummary = deriveDraftStatusSummary(draft);

  return (
    <section className="runtime-console-fee-review" aria-label="Fee Evaluation">
      <header className="runtime-console-fee-review-header">
        <div>
          <p className="eyebrow">Fee Evaluation</p>
          <h3>Fee Evaluation</h3>
        </div>
        <div className="runtime-console-fee-review-status">
          <strong>{statusSummary.label}</strong>
          <span>{statusSummary.detail}</span>
        </div>
      </header>

      <dl className="runtime-console-fee-review-meta">
        <div>
          <dt>LTR</dt>
          <dd>{displayValue(ltrNumber)}</dd>
        </div>
        <div>
          <dt>Project / sample</dt>
          <dd>{displayValue(projectDescription)}</dd>
        </div>
        <div>
          <dt>Fee rule version</dt>
          <dd>{draft.header.pricing_rule_version_id}</dd>
        </div>
        <div>
          <dt>Pricing effective from</dt>
          <dd>{displayValue(draft.header.pricing_effective_from)}</dd>
        </div>
        <div>
          <dt>Generated</dt>
          <dd>{formatDateTime(draft.header.generated_at)}</dd>
        </div>
      </dl>

      <div className="runtime-console-fee-review-total">
        <span>Total</span>
        <strong>{draft.total_fee ? formatMoney(draft.total_fee) : "Total pending review"}</strong>
      </div>

      {hasLocalChanges ? (
        <p className="runtime-console-fee-review-local-note">
          Local review edits only. Reloading discards changes.
        </p>
      ) : null}

      {draft.warnings.length > 0 ? (
        <div className="runtime-console-fee-review-warnings" role="note">
          {draft.warnings.map((warning) => (
            <p key={`${warning.scope}:${warning.code}`}>{warning.message}</p>
          ))}
        </div>
      ) : null}

      {lineCount === 0 ? (
        <p className="runtime-console-matrix-projection-empty">
          Active confirmed matrix found, but no fee rows are available.
        </p>
      ) : (
        <div className="runtime-console-fee-review-table-wrap">
          <table
            className="runtime-console-fee-review-table"
            aria-label="Fee Evaluation review rows"
          >
            <thead>
              <tr>
                <th>Group</th>
                <th>Matrix source</th>
                <th>Matched fee rule</th>
                <th>Unit price</th>
                <th>Units</th>
                <th>Base fee</th>
                <th>Discount</th>
                <th>Calculated fee</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {draft.groups.flatMap((group) =>
                group.line_items.map((line) => (
                  <FeeEvaluationReviewRow
                    key={line.line_id}
                    line={line}
                    override={overrides[line.line_id]}
                    changed={
                      Boolean(overrides[line.line_id]) &&
                      !sameOverride(
                        buildInitialOverride(line),
                        overrides[line.line_id]
                      )
                    }
                    onChange={(next) =>
                      setOverrides((current) => ({
                        ...current,
                        [line.line_id]: next,
                      }))
                    }
                  />
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function FeeEvaluationReviewRow({
  line,
  override,
  changed,
  onChange,
}: {
  line: FeeEvaluationLineItem;
  override: LocalFeeLineOverride | undefined;
  changed: boolean;
  onChange: (override: LocalFeeLineOverride) => void;
}): ReactElement {
  const current = override ?? buildInitialOverride(line);
  const statusLabel = line.status === "calculated" ? "Calculated" : "Review required";
  const rowClassName = line.review_required
    ? "runtime-console-fee-review-row-review"
    : undefined;

  return (
    <tr className={rowClassName}>
      <td>{line.group_label}</td>
      <td>
        <strong>{line.test_item}</strong>
        <span>
          Step {line.step_tokens.join(", ") || "-"} / sample {line.sample_quantity_expression || "-"}
        </span>
      </td>
      <td>
        <strong>{displayValue(line.matched_rule_name)}</strong>
        <span>{displayValue(line.matched_rule_version_id)}</span>
      </td>
      <td>{formatMoney(line.unit_price)}</td>
      <td>
        <label className="runtime-console-fee-review-input-label">
          Units
          <input
            value={current.units}
            onChange={(event) =>
              onChange({ ...current, units: event.currentTarget.value })
            }
          />
        </label>
      </td>
      <td>
        <label className="runtime-console-fee-review-input-label">
          Base fee
          <input
            value={current.baseFee}
            onChange={(event) =>
              onChange({ ...current, baseFee: event.currentTarget.value })
            }
          />
        </label>
      </td>
      <td>
        <label className="runtime-console-fee-review-input-label">
          Discount
          <input
            value={current.discountPercent}
            onChange={(event) =>
              onChange({ ...current, discountPercent: event.currentTarget.value })
            }
          />
        </label>
      </td>
      <td>{formatMoney(line.testing_fee)}</td>
      <td>
        <span className="runtime-console-fee-review-status-pill">{statusLabel}</span>
        {changed ? (
          <span className="runtime-console-fee-review-local-pill">Edited locally</span>
        ) : null}
        {line.review_reason ? (
          <p className="runtime-console-fee-review-reason">{line.review_reason}</p>
        ) : null}
        {line.status === "no_rule_match" && !line.review_reason ? (
          <p className="runtime-console-fee-review-reason">No fee rule match.</p>
        ) : null}
      </td>
    </tr>
  );
}

function buildInitialOverrides(
  draft: FeeEvaluationDraft
): Record<string, LocalFeeLineOverride> {
  return Object.fromEntries(
    draft.groups.flatMap((group) =>
      group.line_items.map((line) => [line.line_id, buildInitialOverride(line)])
    )
  );
}

function buildInitialOverride(line: FeeEvaluationLineItem): LocalFeeLineOverride {
  return {
    reviewStatus: line.review_required ? "pending" : "accepted",
    units: line.units ?? "",
    baseFee: line.base_fee ?? "",
    discountPercent: line.discount_percent ?? "",
  };
}

function sameOverride(
  left: LocalFeeLineOverride,
  right: LocalFeeLineOverride
): boolean {
  return (
    left.reviewStatus === right.reviewStatus &&
    left.units === right.units &&
    left.baseFee === right.baseFee &&
    left.discountPercent === right.discountPercent
  );
}

function deriveDraftStatusSummary(draft: FeeEvaluationDraft): {
  label: string;
  detail: string;
} {
  if (draft.draft_status === "empty") {
    return {
      label: "No fee rows",
      detail: "Active Matrix has no fee rows available.",
    };
  }
  if (draft.draft_status === "needs_review") {
    return {
      label: `${draft.review_required_count} lines require review`,
      detail: "Review required before total can be trusted.",
    };
  }
  return {
    label: "Draft ready",
    detail: "All lines are calculated from the active fee rule version.",
  };
}

function displayValue(value: string | null | undefined): string {
  const normalized = value?.trim() ?? "";
  return normalized.length > 0 ? normalized : "-";
}

function formatMoney(value: string | null | undefined): string {
  if (!value) {
    return "-";
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return value;
  }
  return parsed.toFixed(2);
}

function formatDateTime(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString("en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}
