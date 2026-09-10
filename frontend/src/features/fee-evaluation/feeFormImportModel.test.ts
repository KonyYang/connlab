import { describe, expect, it } from "vitest";
import { planFeeImport } from "./feeFormImportModel";
import type { FeeEvaluationPreviewRow } from "./feeEvaluationPreviewModel";

const row = (lineId: string, description: string, groupLabel = "Aa") => ({lineId, description, groupLabel,
  rowKind: "matrix_step", units: "99", spendTime: "7", discount: "25", notes: "keep"} as FeeEvaluationPreviewRow);
const source = (description: string, price = "10", group = "Aa") => ({group, description, rowKind: "matrix_step",
  values: {unitPrice: price, unitType: "per sample", baseFee: "0", units: "5", spendTime: "1", discount: "0", notes: "old"}});

describe("Fee Form import planning", () => {
  it("restores repeated tests by ordered group positions and skips a different group sequence", () => {
    const plan = planFeeImport([source("LLCR", "10"), source("LLCR", "20"), source("IR", "5", "Ab")],
      [row("1", "LLCR"), row("2", "LLCR"), row("3", "CR", "Ab")], "matrix", {});
    expect(plan.changes.map(c => [c.row.lineId, c.values.unitPrice])).toEqual([["1", "10"], ["2", "20"]]);
    expect(plan.skipped).toEqual(["Group Ab: test order or descriptions differ."]);
  });
  it("requires selection for conflicting prices and never imports quantities across projects", () => {
    const sources = [source("LLCR", "10", "1"), source("LLCR", "20", "2")];
    const rows = [row("1", "LLCR"), row("2", "LLCR", "Ac"), row("3", "Other")];
    const plan = planFeeImport(sources, rows, "prices", {});
    expect(plan.changes).toEqual([]);
    expect(plan.conflicts).toHaveLength(1);
    const selected = planFeeImport(sources, rows, "prices", {[plan.conflicts[0].key]: 1});
    expect(selected.changes.map(c => c.values)).toEqual([
      {unitPrice: "20", unitType: "per sample", baseFee: "0"},
      {unitPrice: "20", unitType: "per sample", baseFee: "0"},
    ]);
  });
});
