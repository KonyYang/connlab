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

export function addCustomContactFamily(
  target: ContactMeasurementPlanTarget
): ContactMeasurementPlanTarget {
  const nextNumber = target.families.reduce((highest, family) => {
    const match = /^custom-(\d+)$/.exec(family.family_id);
    return match ? Math.max(highest, Number(match[1])) : highest;
  }, 0) + 1;
  const familyId = `custom-${nextNumber}`;
  return {
    ...target,
    families: [
      ...target.families,
      {
        family_id: familyId,
        family_ordinal: target.families.length,
        label: "Custom contact",
        count_per_sample: 0,
        record_label: "Custom contact",
        record_prefix: `C${nextNumber}`,
        included: true,
        is_custom: true,
      },
    ],
  };
}

export function validateContactMeasurementFamilies(
  families: ContactMeasurementPlanFamily[]
): string | null {
  const ids = new Set<string>();
  for (const family of families) {
    if (!family.family_id.trim() || ids.has(family.family_id)) {
      return "Contact family ids must be unique.";
    }
    if (!family.label.trim() || !family.record_label.trim() || !family.record_prefix.trim()) {
      return "Contact family label, record label, and prefix are required.";
    }
    if (!Number.isInteger(family.count_per_sample) || family.count_per_sample < 0) {
      return "Contact family count per sample must be a non-negative integer.";
    }
    ids.add(family.family_id);
  }
  return null;
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
