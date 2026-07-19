import type {
  ProjectPointProfileCategory,
  ProjectPointProfileCrCoverageMode,
} from "../../api/client";

export type ProjectPointProfileDraftCategory = {
  category_id: string | null;
  prefix: string;
  point_expression: string;
  cr_selected?: boolean;
};

export function emptyProjectPointProfileCategory(): ProjectPointProfileDraftCategory {
  return { category_id: null, prefix: "", point_expression: "", cr_selected: true };
}

export function projectPointProfileCrCoverageMode(
  rows: ProjectPointProfileDraftCategory[],
): ProjectPointProfileCrCoverageMode {
  return rows.length > 0 && rows.every((row) => Boolean(row.cr_selected))
    ? "follow_llcr"
    : "custom";
}

export function projectPointProfileTotal(rows: ProjectPointProfileDraftCategory[]): number {
  return rows.reduce((total, row) => total + (parsePointExpression(row.point_expression)?.length ?? 0), 0);
}

export function projectPointProfileCrTotal(
  rows: ProjectPointProfileDraftCategory[],
  mode: ProjectPointProfileCrCoverageMode,
): number {
  if (mode === "follow_llcr") return projectPointProfileTotal(rows);
  return projectPointProfileTotal(rows.filter((row) => Boolean(row.cr_selected)));
}

export function pointProfileValidation(
  rows: ProjectPointProfileDraftCategory[],
  crCoverageMode: ProjectPointProfileCrCoverageMode = "follow_llcr",
): string | null {
  if (rows.length > 256) return "Point Profile supports at most 256 rows.";
  if (!rows.length) return "Add at least one point profile row.";
  const prefixes = new Set<string>();
  let total = 0;
  for (const row of rows) {
    const prefix = row.prefix.trim();
    const points = parsePointExpression(row.point_expression);
    if (!/^[A-Za-z][A-Za-z0-9_-]{0,63}$/.test(prefix)) return "Each Prefix must use 1-64 letters, digits, _ or -.";
    if (!points) return "Each Test points value needs positive integers or ascending ranges.";
    if (prefixes.has(prefix.toLocaleLowerCase())) return "Prefixes must be unique.";
    prefixes.add(prefix.toLocaleLowerCase());
    total += points.length;
  }
  if (total > 8192) return "Point Profile total may not exceed 8192.";
  if (crCoverageMode === "custom" && !rows.some((row) => Boolean(row.cr_selected))) {
    return "Select at least one category for custom CR coverage.";
  }
  return null;
}

export function parsePointExpression(value: string): number[] | null {
  if (!value.trim() || value.length > 1024) return null;
  const points = new Set<number>();
  for (const token of value.split(",")) {
    const match = /^\s*([1-9][0-9]*)(?:\s*-\s*([1-9][0-9]*))?\s*$/.exec(token);
    if (!match) return null;
    const start = Number(match[1]);
    const end = Number(match[2] ?? start);
    if (end < start || end > 9999) return null;
    for (let point = start; point <= end; point += 1) {
      points.add(point);
      if (points.size > 4096) return null;
    }
  }
  return [...points].sort((left, right) => left - right);
}

export function localPointProfileRows(
  categories: ProjectPointProfileCategory[] | null | undefined,
  selectedCategoryIds: string[] = [],
): ProjectPointProfileDraftCategory[] {
  if (!categories?.length) return [emptyProjectPointProfileCategory()];
  const selected = new Set(selectedCategoryIds);
  return categories.map((category) => ({
    category_id: category.category_id,
    prefix: category.record_prefix,
    point_expression: category.point_expression ?? category.legacy_contiguous_suggestion ?? "",
    cr_selected: selected.has(category.category_id ?? ""),
  }));
}
