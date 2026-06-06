import type { Dispatch, ReactElement, SetStateAction } from "react";
import type { FeeEvaluationLineItem } from "../../api/client";

export type FeeLineFilter = "all" | "review_required" | "calculated" | "no_rule_match";

type FeeEvaluationReviewDetailsProps = {
  lines: FeeEvaluationLineItem[];
  visibleLines: FeeEvaluationLineItem[];
  filter: FeeLineFilter;
  setFilter: Dispatch<SetStateAction<FeeLineFilter>>;
  groupFilter: string;
  setGroupFilter: Dispatch<SetStateAction<string>>;
  search: string;
  setSearch: Dispatch<SetStateAction<string>>;
  groupOptions: string[];
  stateMessage: ReactElement | null;
};

export function FeeEvaluationReviewDetails({
  lines,
  visibleLines,
  filter,
  setFilter,
  groupFilter,
  setGroupFilter,
  search,
  setSearch,
  groupOptions,
  stateMessage,
}: FeeEvaluationReviewDetailsProps): ReactElement {
  return (
    <section className="fee-evaluation-review-surface" aria-label="Fee review details">
      <header className="fee-evaluation-review-header">
        <div>
          <p className="eyebrow">Review details</p>
          <h3>{lines.length} Matrix fee line(s)</h3>
        </div>
        <div className="fee-evaluation-review-filters">
          <FilterButton current={filter} value="all" onChange={setFilter} label="All" />
          <FilterButton
            current={filter}
            value="review_required"
            onChange={setFilter}
            label="Review required"
          />
          <FilterButton
            current={filter}
            value="calculated"
            onChange={setFilter}
            label="Calculated"
          />
          <FilterButton
            current={filter}
            value="no_rule_match"
            onChange={setFilter}
            label="No rule match"
          />
        </div>
      </header>

      <div className="fee-evaluation-review-toolbar">
        <label>
          Group
          <select
            value={groupFilter}
            onChange={(event) => setGroupFilter(event.currentTarget.value)}
          >
            <option value="all">All groups</option>
            {groupOptions.map((group) => (
              <option key={group} value={group}>
                {group}
              </option>
            ))}
          </select>
        </label>
        <label>
          Search
          <input
            value={search}
            onChange={(event) => setSearch(event.currentTarget.value)}
            placeholder="Test item, rule, reason"
          />
        </label>
      </div>

      {stateMessage ??
        (visibleLines.length === 0 ? (
          <p className="fee-evaluation-empty">No fee rows match the current filters.</p>
        ) : (
          <div className="fee-evaluation-table-wrap">
            <table className="fee-evaluation-table" aria-label="Fee Evaluation review rows">
              <thead>
                <tr>
                  <th>Group</th>
                  <th>Matrix source</th>
                  <th>Matched rule</th>
                  <th>Price basis</th>
                  <th>Calculated fee</th>
                  <th>Status / reason</th>
                </tr>
              </thead>
              <tbody>
                {visibleLines.map((line) => (
                  <FeeReviewRow key={line.line_id} line={line} />
                ))}
              </tbody>
            </table>
          </div>
        ))}
    </section>
  );
}

function FilterButton({
  current,
  value,
  label,
  onChange,
}: {
  current: FeeLineFilter;
  value: FeeLineFilter;
  label: string;
  onChange: Dispatch<SetStateAction<FeeLineFilter>>;
}): ReactElement {
  return (
    <button
      type="button"
      className={current === value ? "is-active" : undefined}
      onClick={() => onChange(value)}
    >
      {label}
    </button>
  );
}

function FeeReviewRow({ line }: { line: FeeEvaluationLineItem }): ReactElement {
  return (
    <tr className={line.review_required ? "fee-evaluation-row-review" : undefined}>
      <td>{line.group_label}</td>
      <td>
        <strong>{line.test_item}</strong>
        <span>
          Row {line.row_order} / step {line.step_tokens.join(", ") || "-"} / sample{" "}
          {line.sample_quantity_expression || "-"}
        </span>
      </td>
      <td>
        <strong>{displayValue(line.matched_rule_name)}</strong>
        <span>{displayValue(line.matched_rule_id)}</span>
        <span>{displayValue(line.matched_rule_version_id)}</span>
      </td>
      <td>
        <strong>{formatMoney(line.unit_price)}</strong>
        <span>{line.calculation_strategy ?? "manual"}</span>
        <span>{line.unit_label}</span>
      </td>
      <td>{formatMoney(line.testing_fee)}</td>
      <td>
        <span className="fee-evaluation-status-pill">{lineStatusLabel(line)}</span>
        {line.review_reason ? (
          <p>{line.review_reason}</p>
        ) : line.status === "no_rule_match" ? (
          <p>No fee rule match.</p>
        ) : null}
        {line.warnings.map((warning) => (
          <p key={`${line.line_id}:${warning.code}`}>{warning.message}</p>
        ))}
      </td>
    </tr>
  );
}

function lineStatusLabel(line: FeeEvaluationLineItem): string {
  if (line.status === "calculated") {
    return "Calculated";
  }
  if (line.status === "no_rule_match") {
    return "No rule match";
  }
  return "Review required";
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
