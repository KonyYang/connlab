import type { MatrixEditorLiveXlsxExportRequest } from "../../api/client";

export type ExportGroup = {
  id: string;
  groupKey: string;
  name: string;
  isSelected: boolean;
};

export type ExportRow = {
  id: string;
  isSampleRow: boolean;
  item: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
  groups: Record<string, string>;
};

type ProjectionInput = {
  projectReference: string;
  groups: ExportGroup[];
  rows: ExportRow[];
  sampleValues: Record<string, string>;
  timeDisplays: Record<string, string>;
};

export function buildMatrixEditorXlsxExportRequest(
  input: ProjectionInput
): MatrixEditorLiveXlsxExportRequest {
  const groups = input.groups.filter((group) => group.isSelected);
  const rows = input.rows.filter(
    (row) =>
      !row.isSampleRow &&
      groups.some((group) => (row.groups[group.id] ?? "").trim().length > 0)
  );
  return {
    source: "matrix_editor_current_ui_state",
    project_reference: input.projectReference,
    groups: groups.map((group) => ({
      group_id: group.id,
      group_key: group.groupKey,
      group_label: group.name.trim() || group.groupKey,
      sample_size: input.sampleValues[group.id] ?? "",
      time_display: input.timeDisplays[group.id] ?? "0 d",
    })),
    rows: rows.map((row) => ({
      row_id: row.id,
      test_item: row.item,
      section: row.section,
      test_method: row.method,
      condition: row.condition,
      requirement: row.requirement,
      cells: groups.map((group) => ({
        group_id: group.id,
        step_text: row.groups[group.id] ?? "",
      })),
    })),
  };
}

type AvailabilityInput = {
  lifecycleMessage: string;
  busy: boolean;
  selectedGroupCount: number;
  hasStepError: boolean;
  stepErrorMessage: string;
  qualifyingRowCount: number;
};

export function getMatrixEditorXlsxExportDisabledReason(
  input: AvailabilityInput
): string {
  if (input.lifecycleMessage) return input.lifecycleMessage;
  if (input.busy) return "Matrix export is in progress.";
  if (input.selectedGroupCount === 0) return "Select at least one Group to export.";
  if (input.hasStepError) {
    return input.stepErrorMessage || "Fix Matrix step numbering before exporting.";
  }
  if (input.qualifyingRowCount === 0) {
    return "Add at least one step to a selected Group before exporting.";
  }
  return "";
}
