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
): string | null {
  if (rows.length > 256) return "Point Profile supports at most 256 rows.";
  if (!rows.length) return "Add at least one point profile row.";
  const prefixes = new Set<string>();
  let total = 0;
  for (const row of rows) {
    const prefix = row.prefix.trim();
    const points = parsePointExpression(row.point_expression);
    if (!/^[A-Za-z][A-Za-z0-9_-]{0,63}$/.test(prefix)) return "Each Point category must use 1-64 letters, digits, _ or -.";
    if (!points) return "Each Test points value needs explicit IDs or ascending ranges such as 1-5 or HP1-5.";
    if (prefixes.has(prefix.toLocaleLowerCase())) return "Point categories must be unique.";
    prefixes.add(prefix.toLocaleLowerCase());
    total += points.length;
  }
  if (total > 8192) return "Point Profile total may not exceed 8192.";
  return null;
}

export function parsePointExpression(value: string): string[] | null {
  if (!value.trim() || value.length > 1024) return null;
  const points: string[] = [];
  const seen = new Set<string>();
  for (const token of value.split(",")) {
    const trimmed = token.trim();
    const range = /^([A-Za-z]{0,64})([1-9][0-9]*)\s*-\s*([A-Za-z]{0,64})([1-9][0-9]*)$/.exec(trimmed);
    let expanded: string[];
    if (range) {
      const [, prefix, startText, endPrefix, endText] = range;
      const start = Number(startText);
      const end = Number(endText);
      if ((endPrefix && endPrefix.toLocaleLowerCase() !== prefix.toLocaleLowerCase()) || end < start || end > 9999) return null;
      expanded = Array.from({ length: end - start + 1 }, (_, index) => `${prefix}${start + index}`);
    } else {
      const single = /^(?:[A-Za-z]{0,64}[1-9][0-9]*|[A-Za-z]{1,64})$/.exec(trimmed);
      if (!single) return null;
      const numericSuffix = /([1-9][0-9]*)$/.exec(trimmed)?.[1];
      if (numericSuffix && Number(numericSuffix) > 9999) return null;
      expanded = [trimmed];
    }
    for (const point of expanded) {
      if (seen.has(point)) continue;
      seen.add(point);
      points.push(point);
      if (points.length > 4096) return null;
    }
  }
  return points;
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
