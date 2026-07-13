import type {
  ContactMeasurementPlanFamily,
  ContactMeasurementPlanTarget,
  ContactMeasurementPlanWorkspace,
} from "../../api/client";

export type ContactMeasurementPlanSummaryView = {
  statusLabel: string;
  readings: { llcr: string; crSpecifiedCurrent: string };
  warning: string | null;
  canOpenSetup: boolean;
};

export type ContactMeasurementKind = "llcr" | "cr_specified_current";

export type ContactMeasurementFamilyHighWater = Record<ContactMeasurementKind, number>;

export type FreeformFamilyOrigin = "starter" | "added" | "template" | "persisted";
export type FreeformFamilyOrigins = Readonly<Record<string, FreeformFamilyOrigin>>;

const FREEFORM_ID = /^ff-(llcr|cr)-(\d+)$/;

export function selectContactMeasurementPlanSummary(
  workspace: ContactMeasurementPlanWorkspace | null
): ContactMeasurementPlanSummaryView {
  if (!workspace) {
    return emptySummary("Loading");
  }
  const needsReview = workspace.summary.needs_review_count;
  return {
    statusLabel: statusLabel(workspace.status),
    readings: {
      llcr: readingLabel(workspace, "llcr"),
      crSpecifiedCurrent: readingLabel(workspace, "cr_specified_current"),
    },
    warning:
      needsReview > 0
        ? `${needsReview} contact measurement change${needsReview === 1 ? "" : "s"} requires review.`
        : workspace.diagnostics[0] ?? null,
    canOpenSetup: workspace.status !== "disabled" && workspace.status !== "authority_corrupt",
  };
}

export function addFreeformContactFamily(
  target: ContactMeasurementPlanTarget,
  highWater: ContactMeasurementFamilyHighWater,
  template?: "high_power" | "low_power" | "signal"
): ContactMeasurementPlanTarget {
  const kind = target.contact_kind;
  const nextNumber = Math.max(highWater[kind], highestFreeformNumber(target.families, kind)) + 1;
  const templateValues = templateFamily(template, nextNumber);
  return {
    ...target,
    families: [
      ...target.families,
      {
        family_id: `ff-${kind === "llcr" ? "llcr" : "cr"}-${nextNumber}`,
        family_ordinal: target.families.length,
        label: templateValues.label,
        count_per_sample: 1,
        record_label: templateValues.label,
        record_prefix: templateValues.prefix,
        included: true,
        is_custom: true,
      },
    ],
  };
}

export function ensureDefaultFreeformFamily(
  target: ContactMeasurementPlanTarget,
  highWater: ContactMeasurementFamilyHighWater
): ContactMeasurementPlanTarget {
  return target.families.length === 0 ? addFreeformContactFamily(target, highWater) : target;
}

export function initializeFreeformRecordLabelsForOrigins(
  target: ContactMeasurementPlanTarget,
  origins: FreeformFamilyOrigins
): ContactMeasurementPlanTarget {
  return {
    ...target,
    families: target.families.map((family) => {
      const mayInitializeRecordLabel = family.is_custom
        && FREEFORM_ID.test(family.family_id)
        && isLocalFreeformOrigin(origins[family.family_id])
        && !family.record_label.trim()
        && Boolean(family.label.trim());
      return mayInitializeRecordLabel
        ? { ...family, record_label: family.label.trim() }
        : family;
    }),
  };
}

export function mergePersistedFreeformFamilyOrigins(
  origins: FreeformFamilyOrigins,
  workspace: ContactMeasurementPlanWorkspace
): Record<string, FreeformFamilyOrigin> {
  const next = { ...origins };
  workspace.targets.flatMap((target) => target.families)
    .filter((family) => FREEFORM_ID.test(family.family_id))
    .forEach((family) => {
      next[family.family_id] ??= "persisted";
    });
  return next;
}

export function markIntroducedFreeformFamilyOrigins(
  origins: FreeformFamilyOrigins,
  source: ContactMeasurementPlanTarget,
  target: ContactMeasurementPlanTarget,
  origin: Exclude<FreeformFamilyOrigin, "persisted">
): Record<string, FreeformFamilyOrigin> {
  const sourceIds = new Set(source.families.map((family) => family.family_id));
  const next = { ...origins };
  target.families
    .filter((family) => FREEFORM_ID.test(family.family_id) && !sourceIds.has(family.family_id))
    .forEach((family) => {
      next[family.family_id] = origin;
    });
  return next;
}

export function moveFreeformFamilyOrigin(
  origins: FreeformFamilyOrigins,
  previousFamilyId: string,
  renewedFamilyId: string
): Record<string, FreeformFamilyOrigin> {
  const next = { ...origins };
  next[renewedFamilyId] = origins[previousFamilyId] ?? "persisted";
  return next;
}

export function workspaceFreeformFamilySemantics(
  workspace: ContactMeasurementPlanWorkspace
): Record<string, string> {
  return Object.fromEntries(
    workspace.targets.flatMap((target) => target.families)
      .filter((family) => FREEFORM_ID.test(family.family_id))
      .map((family) => [family.family_id, freeformFamilySemanticKey(family)])
  );
}

export function freeformFamilySemanticKey(
  family: ContactMeasurementPlanFamily
): string {
  return `${family.label.normalize("NFKC").trim().toLowerCase()}|${family.record_prefix.normalize("NFKC").trim().toUpperCase()}`;
}

export function freeformFamilyNumber(familyId: string): number {
  const match = /^ff-(?:llcr|cr)-(\d+)$/.exec(familyId);
  return match ? Number(match[1]) : 1;
}

export function contactMeasurementFamilyPayload(
  families: ContactMeasurementPlanFamily[]
) {
  return families.map((family) => ({
    family_id: family.family_id,
    label: family.label,
    count_per_sample: family.count_per_sample,
    record_label: family.record_label,
    record_prefix: family.record_prefix,
    included: family.included,
    is_custom: family.is_custom,
  }));
}

export function cloneContactMeasurementTarget(
  target: ContactMeasurementPlanTarget
): ContactMeasurementPlanTarget {
  return { ...target, families: target.families.map((family) => ({ ...family })) };
}

export function resolveWorkspaceSelectedTarget(
  workspace: ContactMeasurementPlanWorkspace,
  preferredStableTargetKey: string | null
): ContactMeasurementPlanTarget | null {
  return workspace.targets.find(
    (target) => target.stable_target_key === preferredStableTargetKey && target.eligible
  ) ?? workspace.targets.find((target) => target.eligible) ?? null;
}

export function editableContactMeasurementTarget(
  target: ContactMeasurementPlanTarget,
  workspace: ContactMeasurementPlanWorkspace
): ContactMeasurementPlanTarget {
  return ensureDefaultFreeformFamily(
    cloneContactMeasurementTarget(target),
    workspace.family_id_high_water_by_kind
  );
}

export function renewFreeformContactFamilyIdentity(
  target: ContactMeasurementPlanTarget,
  familyId: string,
  highWater: ContactMeasurementFamilyHighWater
): ContactMeasurementPlanTarget {
  const family = target.families.find((item) => item.family_id === familyId);
  if (!family || !FREEFORM_ID.test(family.family_id)) return target;
  const nextNumber = Math.max(highWater[target.contact_kind], highestFreeformNumber(target.families, target.contact_kind)) + 1;
  const kind = target.contact_kind === "llcr" ? "llcr" : "cr";
  return {
    ...target,
    families: target.families.map((item) => item.family_id === familyId
      ? { ...item, family_id: `ff-${kind}-${nextNumber}` }
      : item),
  };
}

export function moveContactFamily(
  target: ContactMeasurementPlanTarget,
  familyId: string,
  direction: -1 | 1
): ContactMeasurementPlanTarget {
  const index = target.families.findIndex((family) => family.family_id === familyId);
  const nextIndex = index + direction;
  if (index < 0 || nextIndex < 0 || nextIndex >= target.families.length) return target;
  const families = [...target.families];
  [families[index], families[nextIndex]] = [families[nextIndex], families[index]];
  return { ...target, families: families.map((family, familyOrdinal) => ({ ...family, family_ordinal: familyOrdinal })) };
}

export function resolveFreeformPrefix(value: string, label: string, fallbackNumber: number): string {
  const normalized = value.normalize("NFKC").toUpperCase().replace(/[^A-Z0-9]/g, "");
  if (normalized.length >= 1 && normalized.length <= 64) return normalized;
  const labelPrefix = label.normalize("NFKC").toUpperCase().replace(/[^A-Z0-9]/g, "");
  return labelPrefix.length >= 1 && labelPrefix.length <= 64 ? labelPrefix : `C${fallbackNumber}`;
}

export function nextFamilyHighWater(
  current: ContactMeasurementFamilyHighWater,
  workspace: ContactMeasurementPlanWorkspace | null
): ContactMeasurementFamilyHighWater {
  const server = workspace?.family_id_high_water_by_kind ?? { llcr: 0, cr_specified_current: 0 };
  return {
    llcr: Math.max(current.llcr, server.llcr, highestWorkspaceFamilyNumber(workspace, "llcr")),
    cr_specified_current: Math.max(
      current.cr_specified_current,
      server.cr_specified_current,
      highestWorkspaceFamilyNumber(workspace, "cr_specified_current")
    ),
  };
}

export function validateContactMeasurementFamilies(
  families: ContactMeasurementPlanFamily[]
): string | null {
  const ids = new Set<string>();
  const labels = new Map<string, string>();
  const prefixes = new Set<string>();
  for (const family of families) {
    if (!family.family_id.trim() || ids.has(family.family_id)) {
      return "Contact family ids must be unique.";
    }
    if (!family.label.trim() || !family.record_label.trim() || !family.record_prefix.trim()) {
      return "Contact family label and prefix are required.";
    }
    if (!Number.isInteger(family.count_per_sample) || family.count_per_sample < 0) {
      return "Contact family count per sample must be a non-negative integer.";
    }
    if (family.included && family.count_per_sample <= 0) {
      return "Included contact family count per sample must be a positive integer.";
    }
    const prefix = family.record_prefix.normalize("NFKC").toUpperCase();
    if (family.family_id.startsWith("ff-") && (prefix.length < 1 || prefix.length > 64 || /[^A-Z0-9]/.test(prefix))) {
      return "Freeform contact prefix must use 1 to 64 ASCII letters or digits.";
    }
    if (family.family_id.startsWith("ff-")) {
      const label = family.label.normalize("NFKC").trim().toLowerCase();
      const owner = labels.get(label);
      if (owner && owner !== family.family_id) return "Contact family labels must be unique.";
      labels.set(label, family.family_id);
    }
    ids.add(family.family_id);
    if (prefixes.has(prefix)) return "Contact family prefixes must be unique.";
    prefixes.add(prefix);
  }
  return null;
}

function highestFreeformNumber(
  families: ContactMeasurementPlanFamily[],
  kind: ContactMeasurementKind
): number {
  const idKind = kind === "llcr" ? "llcr" : "cr";
  return families.reduce((highest, family) => {
    const match = FREEFORM_ID.exec(family.family_id);
    return match?.[1] === idKind ? Math.max(highest, Number(match[2])) : highest;
  }, 0);
}

function highestWorkspaceFamilyNumber(
  workspace: ContactMeasurementPlanWorkspace | null,
  kind: ContactMeasurementKind
): number {
  return (workspace?.targets ?? []).reduce(
    (highest, target) => target.contact_kind === kind ? Math.max(highest, highestFreeformNumber(target.families, kind)) : highest,
    0
  );
}

function templateFamily(template: "high_power" | "low_power" | "signal" | undefined, nextNumber: number) {
  if (template === "high_power") return { label: "High Power", prefix: "HP" };
  if (template === "low_power") return { label: "Low Power", prefix: "LP" };
  if (template === "signal") return { label: "Signal", prefix: "SIG" };
  return { label: "", prefix: `C${nextNumber}` };
}

function isLocalFreeformOrigin(origin: FreeformFamilyOrigin | undefined): boolean {
  return origin === "starter" || origin === "added" || origin === "template";
}

function emptySummary(statusLabel: string): ContactMeasurementPlanSummaryView {
  return {
    statusLabel,
    readings: { llcr: "-", crSpecifiedCurrent: "-" },
    warning: null,
    canOpenSetup: false,
  };
}

function readingLabel(
  workspace: ContactMeasurementPlanWorkspace,
  kind: "llcr" | "cr_specified_current"
): string {
  const values = new Set(
    workspace.targets
      .filter((target) => target.included && target.contact_kind === kind)
      .map((target) => target.readings_per_sample)
  );
  if (values.size === 0) return "-";
  return values.size === 1 ? String([...values][0]) : "Multiple";
}

function statusLabel(status: string): string {
  const labels: Record<string, string> = {
    not_started: "Not started",
    draft: "Draft",
    needs_review: "Needs review",
    confirmed: "Confirmed",
    complete: "Confirmed",
    partial_compatible: "Partially compatible",
    authority_corrupt: "Blocked",
    disabled: "Blocked",
  };
  return labels[status] ?? "Review required";
}
