import type { ReactElement } from "react";
import type { ProjectTestPlanDraft, ProjectTestPlanDraftGroup, ProjectTestPlanDraftStep } from "../../api/client";
import { durationText } from "./projectWorkbenchMatrixHelpers";

type ProjectWorkbenchMatrixOverviewProps = {
  draft: ProjectTestPlanDraft;
};

type MatrixGroupColumn = {
  key: string;
  label: string;
};

type MatrixCrossRow = {
  key: string;
  testItem: string;
  method: string;
  condition: string;
  requirement: string;
  duration: string;
  rowGroupCellTokens: Record<string, string[]>;
};

export function ProjectWorkbenchMatrixOverview({ draft }: ProjectWorkbenchMatrixOverviewProps): ReactElement {
  const groups = draft.payload.groups ?? [];
  const groupColumns = buildGroupColumns(groups);
  const rows = buildMatrixCrossRows(groups, groupColumns);

  return (
    <section className="matrix-overview-panel">
      <header className="matrix-overview-heading">
        <h5>Matrix overview</h5>
        <span>{rows.length} test row(s)</span>
      </header>
      <div className="matrix-overview-table-wrap">
        <table className="matrix-overview-table">
          <thead>
            <tr>
              <th>Test item</th>
              <th>Method</th>
              <th>Condition</th>
              <th>Requirement</th>
              <th>Duration</th>
              {groupColumns.map((column) => (
                <th key={column.key}>{column.label}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.key}>
                <td>{row.testItem}</td>
                <td>{row.method}</td>
                <td>{row.condition}</td>
                <td>{row.requirement}</td>
                <td>{row.duration}</td>
                {groupColumns.map((column) => (
                  <td key={`${row.key}-${column.key}`}>
                    {renderRowGroupCellTokens(row.rowGroupCellTokens[column.key] ?? [])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function buildGroupColumns(groups: ProjectTestPlanDraftGroup[]): MatrixGroupColumn[] {
  return groups.map((group, index) => ({
    key: group.group_key?.trim() || `group_${index + 1}`,
    label: group.group_label?.trim() || `Group ${index + 1}`
  }));
}

function buildMatrixCrossRows(groups: ProjectTestPlanDraftGroup[], groupColumns: MatrixGroupColumn[]): MatrixCrossRow[] {
  const rowMap = new Map<string, MatrixCrossRow>();
  const groupKeyByIndex = groupColumns.map((column) => column.key);

  groups.forEach((group, groupIndex) => {
    const groupKey = groupKeyByIndex[groupIndex];
    (group.steps ?? []).forEach((step, stepIndex) => {
      const rowKey = buildRowKey(step, stepIndex);
      const existing = rowMap.get(rowKey);
      if (existing) {
        aggregateRowGroupCellTokens(existing.rowGroupCellTokens, groupKey, step);
        return;
      }
      const rowGroupCellTokens: Record<string, string[]> = {};
      aggregateRowGroupCellTokens(rowGroupCellTokens, groupKey, step);
      rowMap.set(rowKey, {
        key: rowKey,
        testItem: step.test_item ?? step.step_label ?? "Unspecified test step",
        method: step.method_summary ?? step.reference_standard ?? "Method/reference pending",
        condition: step.condition_summary ?? "Condition pending",
        requirement: step.judgement_criteria ?? "Requirement pending",
        duration: durationText(step),
        rowGroupCellTokens
      });
    });
  });

  return [...rowMap.values()];
}

export function aggregateRowGroupCellTokens(
  rowGroupCellTokens: Record<string, string[]>,
  groupKey: string,
  step: ProjectTestPlanDraftStep
): void {
  const token = normalizeStepToken(step);
  const existing = rowGroupCellTokens[groupKey] ?? [];
  if (!existing.includes(token)) {
    rowGroupCellTokens[groupKey] = [...existing, token];
  }
}

function renderRowGroupCellTokens(tokens: string[]): string {
  if (tokens.length === 0) {
    return "-";
  }
  return tokens.join(", ");
}

function normalizeStepToken(step: ProjectTestPlanDraftStep): string {
  if (step.raw_token && step.raw_token.trim()) {
    return step.raw_token.trim();
  }
  if (typeof step.sequence === "number") {
    return `${step.sequence}`;
  }
  return "-";
}

function buildRowKey(step: ProjectTestPlanDraftStep, stepIndex: number): string {
  const keyParts = [
    normalizeRowValue(step.test_item ?? step.step_label),
    normalizeRowValue(step.method_summary ?? step.reference_standard),
    normalizeRowValue(step.condition_summary),
    normalizeRowValue(step.judgement_criteria)
  ];
  const composed = keyParts.join("|");
  if (composed.replace(/\|/g, "").length > 0) {
    return composed;
  }
  return `fallback-row-${stepIndex}`;
}

function normalizeRowValue(value: string | null | undefined): string {
  if (!value) {
    return "";
  }
  return value.trim().toLowerCase();
}
