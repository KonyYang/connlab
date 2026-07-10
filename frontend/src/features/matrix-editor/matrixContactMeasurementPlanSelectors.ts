import type {
  MatrixStepContactFamily,
  MatrixStepContactPlan,
  MatrixStepQuantityItem,
} from "../../api/client";
import type { MatrixStepQuantityIdentity } from "./matrixStepQuantitySelectors";

export type ContactMeasurementKind = "llcr" | "cr_specified_current";

export type ContactFamilyDraft = {
  familyId: string;
  familyLabel: string;
  countPerSample: string;
  recordPrefix: string;
  included: boolean;
  isCustom: boolean;
};

export type ContactPlanProfiles = Record<ContactMeasurementKind, ContactFamilyDraft[]>;

export type ContactPlanTarget = {
  item: MatrixStepQuantityItem;
  plan: MatrixStepContactPlan;
  status: "Eligible" | "Applied" | "Excluded" | "Manual override";
};

export type ContactPlanApplyResult = {
  items: MatrixStepQuantityItem[];
  changed: boolean;
  reviewRequired: boolean;
};

const CONTACT_PLAN_SOURCE = "matrix_contact_plan";

export const DEFAULT_CONTACT_PLAN_PROFILES: ContactPlanProfiles = {
  llcr: [
    family("high_power_pin", "High Power Pin", "HP"),
    family("low_power_pin", "Low Power Pin", "LP"),
    family("signal_pin", "Signal Pin", "SIG"),
  ],
  cr_specified_current: [
    family("specified_current_contact", "Specified Current Contact", "CR"),
  ],
};

export function contactMeasurementKindForItem(
  item: Pick<MatrixStepQuantityItem, "test_item">
): ContactMeasurementKind | null {
  const normalized = normalizeTestItem(item.test_item);
  if (/\bllcr\b/.test(normalized) || normalized.includes("low level contact resistance")) {
    return "llcr";
  }
  if (
    normalized.includes("contact resistance") &&
    !normalized.includes("low level") &&
    (normalized.includes("specified current") ||
      normalized.includes("power") ||
      normalized.includes("current rating"))
  ) {
    return "cr_specified_current";
  }
  return null;
}

export function isContactMeasurementTarget(item: MatrixStepQuantityItem): boolean {
  return contactMeasurementKindForItem(item) !== null;
}

export function filterNonContactStepQuantities(
  items: MatrixStepQuantityItem[]
): MatrixStepQuantityItem[] {
  return items.filter((item) => !isContactMeasurementTarget(item));
}

export function countContactTargets(items: MatrixStepQuantityItem[]): number {
  return items.filter(isContactMeasurementTarget).length;
}

export function buildContactPlanTargets(items: MatrixStepQuantityItem[]): ContactPlanTarget[] {
  return items.flatMap((item) => {
    const kind = contactMeasurementKindForItem(item);
    if (kind === null) {
      return [];
    }
    const plan = item.contact_plan ?? emptyTargetPlan(kind);
    const status = !plan.included
      ? "Excluded"
      : item.contact_plan && item.contact_plan.readings_per_sample
        ? "Applied"
        : !isBlankContactTarget(item)
          ? "Manual override"
          : "Eligible";
    return [{ item, plan, status }];
  });
}

export function deriveReadingsPerSample(families: ContactFamilyDraft[]): string | null {
  let total = 0;
  for (const entry of families) {
    if (!entry.included) {
      continue;
    }
    const count = parseNonNegativeNumber(entry.countPerSample);
    if (count === null) {
      return null;
    }
    total += count;
  }
  return total > 0 ? formatNumber(total) : null;
}

export function validateContactPlanProfiles(
  profiles: ContactPlanProfiles,
  activeKinds: Iterable<ContactMeasurementKind> = Object.keys(profiles) as ContactMeasurementKind[]
): string | null {
  for (const kind of new Set(activeKinds)) {
    for (const family of profiles[kind]) {
      if (!family.familyLabel.trim()) {
        return `${PROFILE_LABELS[kind]} contact families need a label.`;
      }
      if (!/^[A-Za-z0-9_]{1,16}$/.test(family.recordPrefix.trim())) {
        return `${PROFILE_LABELS[kind]} contact prefixes use up to 16 letters, numbers, or underscores.`;
      }
      if (family.included && parseNonNegativeNumber(family.countPerSample) === null) {
        return `Enter a non-negative count for each included ${PROFILE_LABELS[kind]} contact family.`;
      }
    }
  }
  return null;
}

export function applyContactPlanToBlankTargets(
  items: MatrixStepQuantityItem[],
  profiles: ContactPlanProfiles
): ContactPlanApplyResult {
  let changed = false;
  let reviewRequired = false;
  const nextItems = items.map((item) => {
    const kind = contactMeasurementKindForItem(item);
    if (kind === null || !isBlankContactTarget(item)) {
      return item;
    }
    const currentPlan = item.contact_plan ?? emptyTargetPlan(kind);
    if (!currentPlan.included) {
      return { ...item, contact_plan: currentPlan };
    }
    const families = profiles[kind];
    const readingsPerSample = deriveReadingsPerSample(families);
    const contactPlan = planForTarget(kind, families, readingsPerSample, currentPlan);
    changed = true;
    if (readingsPerSample === null) {
      reviewRequired = true;
      return {
        ...item,
        source: CONTACT_PLAN_SOURCE,
        review_required: true,
        review_reason: "Confirm contact family counts.",
        contact_plan: contactPlan,
      };
    }
    return {
      ...item,
      test_points_per_sample: readingsPerSample,
      readings_per_point: "1",
      contact_points_per_sample: readingsPerSample,
      total_readings: readingsPerSample,
      source: CONTACT_PLAN_SOURCE,
      review_required: false,
      review_reason: null,
      contact_plan: contactPlan,
    };
  });
  return { items: nextItems, changed, reviewRequired };
}

export function updateContactTargetCoverage(
  items: MatrixStepQuantityItem[],
  identity: MatrixStepQuantityIdentity,
  included: boolean,
  exclusionReason: string
): MatrixStepQuantityItem[] {
  return items.map((item) => {
    if (!isSameTarget(item, identity)) {
      return item;
    }
    const kind = contactMeasurementKindForItem(item);
    if (kind === null || (!isBlankContactTarget(item) && !item.contact_plan)) {
      return item;
    }
    const currentPlan = item.contact_plan ?? emptyTargetPlan(kind);
    return {
      ...item,
      contact_plan: {
        ...currentPlan,
        included,
        coverage_status: included ? "eligible" : "excluded",
        exclusion_reason: included ? null : exclusionReason,
      },
    };
  });
}

export function updateContactFamilyCount(
  profiles: ContactPlanProfiles,
  kind: ContactMeasurementKind,
  familyId: string,
  value: string
): ContactPlanProfiles {
  return updateFamily(profiles, kind, familyId, { countPerSample: value });
}

export function updateContactFamilyIncluded(
  profiles: ContactPlanProfiles,
  kind: ContactMeasurementKind,
  familyId: string,
  included: boolean
): ContactPlanProfiles {
  return updateFamily(profiles, kind, familyId, { included });
}

export function updateContactFamilyLabel(
  profiles: ContactPlanProfiles,
  kind: ContactMeasurementKind,
  familyId: string,
  familyLabel: string
): ContactPlanProfiles {
  return updateFamily(profiles, kind, familyId, { familyLabel });
}

export function updateContactFamilyPrefix(
  profiles: ContactPlanProfiles,
  kind: ContactMeasurementKind,
  familyId: string,
  recordPrefix: string
): ContactPlanProfiles {
  return updateFamily(profiles, kind, familyId, { recordPrefix });
}

export function addCustomContactFamily(
  profiles: ContactPlanProfiles,
  kind: ContactMeasurementKind,
  persistedFamilyIds: Iterable<string> = []
): ContactPlanProfiles {
  const nextId = `custom-${kind}-${nextCustomFamilySequence(
    kind,
    profiles[kind].map((entry) => entry.familyId),
    persistedFamilyIds
  )}`;
  return {
    ...profiles,
    [kind]: [...profiles[kind], family(nextId, "Custom contact", "CUSTOM", true)],
  };
}

function nextCustomFamilySequence(
  kind: ContactMeasurementKind,
  profileIds: Iterable<string>,
  persistedIds: Iterable<string>
): number {
  const pattern = new RegExp(`^custom-${kind}-(\\d+)$`);
  let highest = 0;
  for (const familyId of [...profileIds, ...persistedIds]) {
    const match = pattern.exec(familyId);
    if (match) {
      highest = Math.max(highest, Number(match[1]));
    }
  }
  return highest + 1;
}

export function removeCustomContactFamily(
  profiles: ContactPlanProfiles,
  kind: ContactMeasurementKind,
  familyId: string
): ContactPlanProfiles {
  return {
    ...profiles,
    [kind]: profiles[kind].filter((entry) => entry.familyId !== familyId || !entry.isCustom),
  };
}

function family(
  familyId: string,
  familyLabel: string,
  recordPrefix: string,
  isCustom = false
): ContactFamilyDraft {
  return {
    familyId,
    familyLabel,
    countPerSample: "",
    recordPrefix,
    included: true,
    isCustom,
  };
}

const PROFILE_LABELS: Record<ContactMeasurementKind, string> = {
  llcr: "LLCR",
  cr_specified_current: "CR specified current",
};

function emptyTargetPlan(kind: ContactMeasurementKind): MatrixStepContactPlan {
  return {
    contact_kind: kind,
    coverage_status: "eligible",
    included: true,
    exclusion_reason: null,
    is_override: false,
    readings_per_sample: null,
    families: [],
  };
}

function planForTarget(
  kind: ContactMeasurementKind,
  families: ContactFamilyDraft[],
  readingsPerSample: string | null,
  currentPlan: MatrixStepContactPlan
): MatrixStepContactPlan {
  return {
    ...currentPlan,
    contact_kind: kind,
    coverage_status: "eligible",
    included: true,
    exclusion_reason: null,
    readings_per_sample: readingsPerSample,
    families: families.map(toApiFamily),
  };
}

function toApiFamily(entry: ContactFamilyDraft): MatrixStepContactFamily {
  const label = entry.familyLabel.trim();
  return {
    family_id: entry.familyId,
    family_label: label,
    count_per_sample: entry.countPerSample.trim(),
    record_label: label.toLowerCase().endsWith("contact") ? label : `${label} contact`,
    record_prefix: entry.recordPrefix.trim().toUpperCase(),
    included: entry.included,
    is_custom: entry.isCustom,
  };
}

function updateFamily(
  profiles: ContactPlanProfiles,
  kind: ContactMeasurementKind,
  familyId: string,
  patch: Partial<ContactFamilyDraft>
): ContactPlanProfiles {
  return {
    ...profiles,
    [kind]: profiles[kind].map((entry) =>
      entry.familyId === familyId ? { ...entry, ...patch } : entry
    ),
  };
}

function isBlankContactTarget(item: MatrixStepQuantityItem): boolean {
  if (item.source.startsWith("basic_information_")) {
    return true;
  }
  return (
    !item.test_points_per_sample?.trim() &&
    !item.readings_per_point?.trim() &&
    !item.contact_points_per_sample?.trim()
  );
}

function isSameTarget(
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

function normalizeTestItem(value: string): string {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
}

function parseNonNegativeNumber(value: string): number | null {
  const trimmed = value.trim();
  if (!trimmed) {
    return null;
  }
  const parsed = Number(trimmed);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
}

function formatNumber(value: number): string {
  return Number.isInteger(value) ? String(value) : String(Number(value.toFixed(6)));
}
