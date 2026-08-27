import { describe, expect, it } from "vitest";
import {
  emptyProjectPointProfileCategory,
  parsePointExpression,
  pointProfileValidation,
  projectPointProfileCrCoverageMode,
  projectPointProfileCrTotal,
  projectPointProfileTotal,
} from "./projectPointProfileSelectors";

describe("projectPointProfileSelectors", () => {
  it("derives the compact total without expanding point previews", () => {
    const rows = [
      { category_id: null, prefix: "HP", point_expression: "1-4" },
      { category_id: null, prefix: "LP", point_expression: "1,2,3,4,5" },
      { category_id: null, prefix: "SIG", point_expression: "1-24" },
    ];
    expect(projectPointProfileTotal(rows)).toBe(33);
    expect(parsePointExpression("1,2,3,4,5")).toEqual(["1", "2", "3", "4", "5"]);
  });

  it("accepts explicit point IDs and preserves their entered order", () => {
    expect(parsePointExpression("HP1-5")).toEqual(["HP1", "HP2", "HP3", "HP4", "HP5"]);
    expect(parsePointExpression("1,24,35,2,7,10")).toEqual(["1", "24", "35", "2", "7", "10"]);
    expect(parsePointExpression("P1,PE,P2,P3")).toEqual(["P1", "PE", "P2", "P3"]);
  });

  it("blocks invalid expressions and duplicate prefixes before confirm", () => {
    expect(pointProfileValidation([{ category_id: null, prefix: "HP", point_expression: "1-3" }, { category_id: null, prefix: "hp", point_expression: "5" }])).toMatch(/unique/i);
    expect(pointProfileValidation([{ category_id: null, prefix: "HP", point_expression: "1.5" }])).toMatch(/explicit IDs/i);
  });

  it("blocks 257 profile rows before confirm", () => {
    const rows = Array.from({ length: 257 }, (_, index) => ({ category_id: null, prefix: `P${index + 1}`, point_expression: "1" }));
    expect(pointProfileValidation(rows)).toMatch(/256/i);
  });

  it("derives CR totals from dynamic whole-category selection", () => {
    const rows = [
      { category_id: "ppc-1", prefix: "AUX", point_expression: "1-4", cr_selected: true },
      { category_id: "ppc-2", prefix: "SIG", point_expression: "1-5", cr_selected: false },
      { category_id: "ppc-3", prefix: "PWR", point_expression: "1-20", cr_selected: true },
    ];

    expect(projectPointProfileCrTotal(rows, "follow_llcr")).toBe(29);
    expect(projectPointProfileCrTotal(rows, "custom")).toBe(24);
    expect(pointProfileValidation(rows)).toBeNull();
    expect(
      pointProfileValidation(rows.map((row) => ({ ...row, cr_selected: false }))),
    ).toBeNull();
  });

  it("defaults new rows to CR and derives mode from visible row selection", () => {
    const allSelected = [
      { category_id: "ppc-1", prefix: "AUX", point_expression: "1-4", cr_selected: true },
      { category_id: "ppc-2", prefix: "SIG", point_expression: "1-5", cr_selected: true },
    ];

    expect(emptyProjectPointProfileCategory().cr_selected).toBe(true);
    expect(projectPointProfileCrCoverageMode(allSelected)).toBe("follow_llcr");
    expect(projectPointProfileCrCoverageMode([
      allSelected[0],
      { ...allSelected[1], cr_selected: false },
    ])).toBe("custom");
  });
});
