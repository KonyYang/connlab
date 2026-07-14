import { describe, expect, it } from "vitest";
import {
  addProjectPointProfileTemplate,
  emptyProjectPointProfileCategory,
  moveProjectPointProfileCategory,
  pointProfileValidation,
  parsePositiveCount,
  projectPointProfileTotal,
} from "./projectPointProfileSelectors";

describe("projectPointProfileSelectors", () => {
  it("derives the included total for optional connector templates", () => {
    let rows = [emptyProjectPointProfileCategory()];
    rows = addProjectPointProfileTemplate(rows, "high_power");
    rows = addProjectPointProfileTemplate(rows, "low_power");
    rows = addProjectPointProfileTemplate(rows, "signal");
    rows[1].count_per_sample = 4;
    rows[2].count_per_sample = 5;
    rows[3].count_per_sample = 24;

    expect(projectPointProfileTotal(rows)).toBe(33);
    expect(moveProjectPointProfileCategory(rows, 3, -1).map((row) => row.label)).toEqual([
      "", "High Power", "Signal", "Low Power",
    ]);
  });

  it("keeps decimal count input invalid instead of coercing it", () => {
    const rows = [{ category_id: null, category_ordinal: 0, label: "Signal", count_per_sample: "1.5", record_prefix: "SIG", included: true }];

    expect(pointProfileValidation(rows)).toMatch(/positive count/i);
    expect(projectPointProfileTotal(rows)).toBe(0);
  });

  it("accepts a raw whole-number string and rejects unsafe count formats", () => {
    expect(parsePositiveCount("4")).toBe(4);
    expect(projectPointProfileTotal([{ category_id: null, category_ordinal: 0, label: "HP", count_per_sample: "4", record_prefix: "HP", included: true }])).toBe(4);
    for (const invalid of ["1.5", "", " ", "0", "-1", "+4", "1e2", "4x", "9007199254740992"]) {
      expect(parsePositiveCount(invalid)).toBeNull();
    }
  });
});
