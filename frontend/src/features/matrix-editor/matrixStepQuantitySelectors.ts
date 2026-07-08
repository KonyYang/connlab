import type { MatrixStepQuantityItem, MatrixStepQuantitySaveItem } from "../../api/client";

export function filterStepQuantitiesForGroup(
  items: MatrixStepQuantityItem[],
  draftGroupId: string | null
): MatrixStepQuantityItem[] {
  if (!draftGroupId) {
    return [];
  }
  return items.filter((item) => item.draft_group_id === draftGroupId);
}

export function updateStepQuantityField(
  items: MatrixStepQuantityItem[],
  identity: MatrixStepQuantityIdentity,
  field: MatrixStepQuantityEditableField,
  value: string
): MatrixStepQuantityItem[] {
  return items.map((item) => {
    if (!isSameStepQuantity(item, identity)) {
      return item;
    }
    const next = {
      ...item,
      [field]: value,
      source: "matrix_step_override",
      review_required: requiresReview(
        field === "test_points_per_sample" ? value : item.test_points_per_sample,
        field === "readings_per_point" ? value : item.readings_per_point
      )
    };
    return {
      ...next,
      total_readings: deriveTotalReadings(
        next.test_points_per_sample,
        next.readings_per_point
      ),
      review_reason: next.review_required ? "Confirm Step quantity values." : null
    };
  });
}

export function applyStepQuantityDefaultsToBlankFields(
  items: MatrixStepQuantityItem[],
  draftGroupId: string | null,
  defaults: MatrixStepQuantityDefaults
): MatrixStepQuantityDefaultsApplyResult {
  if (!draftGroupId) {
    return { items, changed: false };
  }
  let changed = false;
  const nextItems = items.map((item) => {
    if (item.draft_group_id !== draftGroupId) {
      return item;
    }
    const next = {
      ...item,
      test_points_per_sample: fillBlankValue(
        item.test_points_per_sample,
        defaults.test_points_per_sample
      ),
      readings_per_point: fillBlankValue(item.readings_per_point, defaults.readings_per_point),
      contact_points_per_sample: fillBlankValue(
        item.contact_points_per_sample,
        defaults.contact_points_per_sample
      )
    };
    const itemChanged =
      next.test_points_per_sample !== item.test_points_per_sample ||
      next.readings_per_point !== item.readings_per_point ||
      next.contact_points_per_sample !== item.contact_points_per_sample;
    if (!itemChanged) {
      return item;
    }
    changed = true;
    const reviewRequired = requiresReview(
      next.test_points_per_sample,
      next.readings_per_point
    );
    return {
      ...next,
      source: "matrix_step_override",
      review_required: reviewRequired,
      review_reason: reviewRequired ? "Confirm Step quantity values." : null,
      total_readings: deriveTotalReadings(
        next.test_points_per_sample,
        next.readings_per_point
      )
    };
  });
  return { items: nextItems, changed };
}

export function toStepQuantitySaveItems(
  items: MatrixStepQuantityItem[]
): MatrixStepQuantitySaveItem[] {
  return items.map((item) => ({
    draft_group_id: item.draft_group_id,
    draft_row_id: item.draft_row_id,
    step_sequence: item.step_sequence,
    step_suffix_note: item.step_suffix_note ?? null,
    raw_token: item.raw_token ?? null,
    test_points_per_sample: item.test_points_per_sample ?? null,
    readings_per_point: item.readings_per_point ?? null,
    contact_points_per_sample: item.contact_points_per_sample ?? null,
    source: item.source,
    review_required: item.review_required,
    review_reason: item.review_reason ?? null
  }));
}

export function deriveTotalReadings(
  testPointsPerSample?: string | null,
  readingsPerPoint?: string | null
): string | null {
  const points = parseNonNegativeNumber(testPointsPerSample);
  const readings = parseNonNegativeNumber(readingsPerPoint);
  if (points === null || readings === null) {
    return null;
  }
  const total = points * readings;
  return Number.isInteger(total) ? String(total) : String(Number(total.toFixed(6)));
}

export type MatrixStepQuantityEditableField =
  | "test_points_per_sample"
  | "readings_per_point"
  | "contact_points_per_sample";

export type MatrixStepQuantityDefaults = Record<MatrixStepQuantityEditableField, string>;

export type MatrixStepQuantityDefaultsApplyResult = {
  items: MatrixStepQuantityItem[];
  changed: boolean;
};

export type MatrixStepQuantityIdentity = Pick<
  MatrixStepQuantityItem,
  "draft_group_id" | "draft_row_id" | "step_sequence" | "step_suffix_note"
>;

function isSameStepQuantity(
  item: MatrixStepQuantityItem,
  identity: MatrixStepQuantityIdentity
): boolean {
  return (
    item.draft_group_id === identity.draft_group_id &&
    item.draft_row_id === identity.draft_row_id &&
    item.step_sequence === identity.step_sequence &&
    (item.step_suffix_note ?? null) === (identity.step_suffix_note ?? null)
  );
}

function requiresReview(
  testPointsPerSample?: string | null,
  readingsPerPoint?: string | null
): boolean {
  return !testPointsPerSample?.trim() || !readingsPerPoint?.trim();
}

function fillBlankValue(currentValue: string | null | undefined, defaultValue: string): string | null {
  if (currentValue?.trim()) {
    return currentValue;
  }
  const trimmedDefault = defaultValue.trim();
  return trimmedDefault || (currentValue ?? null);
}

function parseNonNegativeNumber(value?: string | null): number | null {
  if (!value?.trim()) {
    return null;
  }
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
}
