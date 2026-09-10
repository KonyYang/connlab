import type { FeeFormImportRow } from "../../api/client";
import type { FeeEvaluationPreviewRow, FeeEvaluationRowEdits } from "./feeEvaluationPreviewModel";

export type FeeImportMode = "matrix" | "prices";
export type FeeImportChange = { row: FeeEvaluationPreviewRow; values: FeeEvaluationRowEdits };
export type FeeImportConflict = { key: string; description: string; candidates: FeeEvaluationRowEdits[] };
const normalize = (text: string) => text.trim().replace(/\s+/g, " ").toLowerCase();
const groupKey = (text: string) => normalize(text).replace(/^group\s+/, "");
const itemKey = (row: {description: string; rowKind: string}) => `${row.rowKind}:${normalize(row.description)}`;

export function planFeeImport(source: FeeFormImportRow[], targets: FeeEvaluationPreviewRow[],
  mode: FeeImportMode, selections: Record<string, number>) {
  const changes: FeeImportChange[] = [];
  const skipped: string[] = [];
  const conflicts: FeeImportConflict[] = [];
  if (mode === "matrix") {
    const groups = new Map<string, FeeEvaluationPreviewRow[]>();
    for (const target of targets) {
      const key = target.rowKind === "manual_trailing" ? "__report__" : groupKey(target.groupLabel);
      groups.set(key, [...(groups.get(key) ?? []), target]);
    }
    for (const [key, rows] of groups) {
      const imported = source.filter(row => (row.rowKind === "manual_trailing" ? "__report__" : groupKey(row.group)) === key);
      if (rows.length !== imported.length || rows.some((row, index) => itemKey(row) !== itemKey(imported[index]))) {
        skipped.push(key === "__report__" ? "Report preparation: no unique matching row." : `Group ${rows[0].groupLabel}: test order or descriptions differ.`);
        continue;
      }
      rows.forEach((row, index) => {
        // Empty numeric cells are missing inputs, never an instruction to erase current values.
        const values = Object.fromEntries(Object.entries(imported[index].values)
          .filter(([field, value]) => field === "notes" || value !== "")) as FeeEvaluationRowEdits;
        changes.push({row, values});
      });
    }
  } else {
    const keys = new Set(targets.map(itemKey));
    for (const key of keys) {
      const rows = targets.filter(row => itemKey(row) === key);
      const candidates: FeeEvaluationRowEdits[] = [];
      for (const imported of source.filter(row => itemKey(row) === key)) {
        const {unitPrice, unitType, baseFee} = imported.values;
        if (unitPrice === "" || unitType === "" || baseFee === "") continue;
        const candidate = {unitPrice, unitType, baseFee};
        if (!candidates.some(value => JSON.stringify(value) === JSON.stringify(candidate))) candidates.push(candidate);
      }
      if (!candidates.length) {
        skipped.push(`${rows[0].description}: no matching complete price.`);
        continue;
      }
      if (candidates.length > 1) conflicts.push({key, description: rows[0].description, candidates});
      const candidate = candidates.length === 1 ? candidates[0] : candidates[selections[key]];
      if (candidate) rows.forEach(row => changes.push({row, values: candidate}));
    }
  }
  return {changes, skipped, conflicts};
}
