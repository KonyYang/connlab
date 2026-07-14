import { describe, expect, it } from "vitest";
import { parsePointExpression, pointProfileValidation, projectPointProfileTotal } from "./projectPointProfileSelectors";

describe("projectPointProfileSelectors", () => {
  it("derives the compact total without expanding point previews", () => {
    const rows = [
      { category_id: null, prefix: "HP", point_expression: "1-4" },
      { category_id: null, prefix: "LP", point_expression: "1,2,3,4,5" },
      { category_id: null, prefix: "SIG", point_expression: "1-24" },
    ];
    expect(projectPointProfileTotal(rows)).toBe(33);
    expect(parsePointExpression("1,2,3,4,5")).toEqual([1, 2, 3, 4, 5]);
  });

  it("blocks invalid expressions and duplicate prefixes before confirm", () => {
    expect(pointProfileValidation([{ category_id: null, prefix: "HP", point_expression: "1-3" }, { category_id: null, prefix: "hp", point_expression: "5" }])).toMatch(/unique/i);
    expect(pointProfileValidation([{ category_id: null, prefix: "HP", point_expression: "1.5" }])).toMatch(/positive/i);
  });

  it("blocks 257 profile rows before confirm", () => {
    const rows = Array.from({ length: 257 }, (_, index) => ({ category_id: null, prefix: `P${index + 1}`, point_expression: "1" }));
    expect(pointProfileValidation(rows)).toMatch(/256/i);
  });
});
