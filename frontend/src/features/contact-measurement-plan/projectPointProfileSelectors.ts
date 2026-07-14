import type { ProjectPointProfileCategory } from "../../api/client";

export type ProjectPointProfileDraftCategory = Omit<ProjectPointProfileCategory, "count_per_sample"> & {
  category_id: string | null;
  count_per_sample: number | string;
};

export function emptyProjectPointProfileCategory(): ProjectPointProfileDraftCategory {
  return {
    category_id: null,
    category_ordinal: 0,
    label: "",
    count_per_sample: 0,
    record_prefix: "",
    included: true,
  };
}

export function addProjectPointProfileTemplate(
  rows: ProjectPointProfileDraftCategory[],
  template: "high_power" | "low_power" | "signal"
): ProjectPointProfileDraftCategory[] {
  const values = template === "high_power"
    ? { label: "High Power", record_prefix: "HP" }
    : template === "low_power"
      ? { label: "Low Power", record_prefix: "LP" }
      : { label: "Signal", record_prefix: "SIG" };
  return normalizeOrdinals([...rows, { ...emptyProjectPointProfileCategory(), ...values }]);
}

export function projectPointProfileTotal(rows: ProjectPointProfileDraftCategory[]): number {
  return rows.reduce((total, row) => total + (row.included ? parsePositiveCount(row.count_per_sample) ?? 0 : 0), 0);
}

export function parsePositiveCount(value: number | string): number | null {
  if (typeof value === "number") return Number.isSafeInteger(value) && value > 0 ? value : null;
  if (!/^[1-9][0-9]*$/.test(value)) return null;
  const parsed = Number(value);
  return Number.isSafeInteger(parsed) ? parsed : null;
}

export function moveProjectPointProfileCategory(
  rows: ProjectPointProfileDraftCategory[], index: number, direction: -1 | 1
): ProjectPointProfileDraftCategory[] {
  const next = index + direction;
  if (index < 0 || next < 0 || next >= rows.length) return rows;
  const reordered = [...rows];
  [reordered[index], reordered[next]] = [reordered[next], reordered[index]];
  return normalizeOrdinals(reordered);
}

export function normalizeOrdinals(rows: ProjectPointProfileDraftCategory[]): ProjectPointProfileDraftCategory[] {
  return rows.map((row, category_ordinal) => ({ ...row, category_ordinal }));
}

export function pointProfileValidation(rows: ProjectPointProfileDraftCategory[]): string | null {
  const labels = new Set<string>();
  const prefixes = new Set<string>();
  for (const row of rows) {
    if (!row.included) continue;
    const label = row.label.normalize("NFKC").trim().toLocaleLowerCase();
    if (!label || parsePositiveCount(row.count_per_sample) === null) {
      return "Each included category needs a name and a positive count.";
    }
    const prefix = row.record_prefix.normalize("NFKC").trim().toUpperCase();
    if (label && labels.has(label)) return "Included category names must be unique.";
    if (prefix && prefixes.has(prefix)) return "Included category prefixes must be unique.";
    labels.add(label);
    if (prefix) prefixes.add(prefix);
  }
  return null;
}
