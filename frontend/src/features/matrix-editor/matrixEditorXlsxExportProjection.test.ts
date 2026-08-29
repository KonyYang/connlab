import { describe, expect, it } from "vitest";
import {
  buildMatrixEditorXlsxExportRequest,
  getMatrixEditorXlsxExportDisabledReason,
} from "./matrixEditorXlsxExportProjection";

const groups = [
  { id: "g1", groupKey: "G1", name: " Group One ", isSelected: true, sampleNote: "Reserve" },
  { id: "g2", groupKey: "G2", name: "", isSelected: false, sampleNote: null },
  { id: "g3", groupKey: "G3", name: "", isSelected: true, sampleNote: null },
];
const rows = [
  {
    id: "r1", isSampleRow: false, item: "Item", section: "1", method: "M",
    condition: "C", requirement: "R", groups: { g1: "1", g2: "9", g3: "" },
    dayExpression: "2.5x",
  },
  {
    id: "r2", isSampleRow: true, item: "Sample", section: "", method: "",
    condition: "", requirement: "", groups: { g1: "2", g2: "", g3: "2" },
    dayExpression: "",
  },
  {
    id: "r3", isSampleRow: false, item: "Other", section: "", method: "",
    condition: "", requirement: "", groups: { g1: "", g2: "4", g3: "" },
    dayExpression: "1",
  },
];

describe("Matrix Editor XLSX export projection", () => {
  it("keeps checked Groups and only qualifying non-sample rows", () => {
    const result = buildMatrixEditorXlsxExportRequest({
      projectReference: "TMP-ABCDEF12", groups, rows,
      sampleValues: { g1: "5", g3: "" }, timeDisplays: { g1: "2.5 d", g3: "0 d" },
      schedule: { post_test_buffer_days: "1" },
    });
    expect(result.groups.map((group) => [group.group_id, group.group_label])).toEqual([
      ["g1", "Group One"], ["g3", "G3"],
    ]);
    expect(result.rows).toEqual([{
      row_id: "r1", test_item: "Item", section: "1", test_method: "M",
      condition: "C", requirement: "R",
      day_expression: "2.5x",
      cells: [{ group_id: "g1", step_text: "1" }, { group_id: "g3", step_text: "" }],
    }]);
    expect(result.schedule).toEqual({ post_test_buffer_days: "1" });
    expect(result.groups.map((group) => [group.sample_size, group.time_display])).toEqual([
      ["5", "2.5 d"], ["", "0 d"],
    ]);
    expect(result.groups[0].sample_note).toBe("Reserve");
  });

  it("uses the frozen disabled reason priority", () => {
    expect(getMatrixEditorXlsxExportDisabledReason({
      lifecycleMessage: "Project is closed.", busy: true, selectedGroupCount: 0,
      hasStepError: true, stepErrorMessage: "Bad step", qualifyingRowCount: 0,
    })).toBe("Project is closed.");
    expect(getMatrixEditorXlsxExportDisabledReason({
      lifecycleMessage: "", busy: false, selectedGroupCount: 1,
      hasStepError: false, stepErrorMessage: "", qualifyingRowCount: 0,
    })).toBe("Add at least one step to a selected Group before exporting.");
  });
});
