import type { ProjectBasicInformationResponse } from "../../api/client";
import {
  BASIC_INFORMATION_FIELD_LABELS,
  normalizeBasicInformationFieldValues,
  normalizeBasicInformationDateValue,
} from "./basicInformationFieldConfig";

export type BasicInformationDisplayItem = {
  key: string;
  label: string;
  value: string;
};

const SUMMARY_KEYS = [
  "test_result",
  "test_fee",
  "sub_contract",
  "remarks_po",
  "location",
  "sample_deposition",
  "project_type",
  "test_type_in_sheet",
  "requested_by",
  "project_leader",
  "failed_item",
];

const WORKBENCH_SUMMARY_LABELS: Record<string, string> = {
  location: "Location",
};

export function selectBasicInformationStatusLabel(
  response: ProjectBasicInformationResponse | null
): string {
  if (!response) {
    return "Unavailable";
  }
  if (response.status === "confirmed") {
    return "Confirmed";
  }
  if (response.status === "needs_review") {
    return "Needs review";
  }
  return "Unconfirmed";
}

export function selectBasicInformationMissingLabels(
  response: ProjectBasicInformationResponse | null
): string[] {
  return response?.missing_required_labels ?? [];
}

export function selectChangedSourceFieldLabels(
  response: ProjectBasicInformationResponse | null
): string[] {
  if (!response) {
    return [];
  }
  return response.changed_source_fields.map(
    (fieldKey) => BASIC_INFORMATION_FIELD_LABELS[fieldKey] ?? fieldKey
  );
}

export function selectWorkbenchSummaryItems(
  response: ProjectBasicInformationResponse | null
): BasicInformationDisplayItem[] {
  const confirmedValues = response?.latest_confirmed?.values;
  if (!confirmedValues) {
    return [];
  }
  const values = normalizeBasicInformationFieldValues(confirmedValues);
  return SUMMARY_KEYS.map((key) => {
    const value = values[key]?.trim() || "-";
    return {
      key,
      label: WORKBENCH_SUMMARY_LABELS[key] ?? BASIC_INFORMATION_FIELD_LABELS[key] ?? key,
      value,
    };
  });
}

export function selectConfirmedViewItems(
  response: ProjectBasicInformationResponse | null
): BasicInformationDisplayItem[] {
  const values = response?.latest_confirmed?.values;
  if (!values) {
    return [];
  }
  return Object.entries(values)
    .filter(([, value]) => value.trim())
    .map(([key, value]) => ({
      key,
      label: BASIC_INFORMATION_FIELD_LABELS[key] ?? key,
      value,
    }));
}

export function sourceReviewMessage(fieldLabel: string): string {
  return `${fieldLabel} changed in source material.`;
}

export function requiresBasicInformationConfirmation(
  response: ProjectBasicInformationResponse | null,
  values: Record<string, string>
): boolean {
  if (!response) return false;
  if (!response.latest_confirmed || response.changed_source_fields.length > 0) return true;
  const current = normalizeBasicInformationFieldValues(values);
  const confirmed = normalizeBasicInformationFieldValues(response.latest_confirmed.values);
  return Array.from(new Set([...Object.keys(current), ...Object.keys(confirmed)])).some((key) => {
    const normalize = key === "date_lab_received_samples" || key === "requested_completion_date"
      ? normalizeBasicInformationDateValue
      : (value: string) => value.trim();
    return normalize(current[key] ?? "") !== normalize(confirmed[key] ?? "");
  });
}
