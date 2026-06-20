import type { ProjectBasicInformationResponse } from "../../api/client";
import { BASIC_INFORMATION_FIELD_LABELS } from "./basicInformationFieldConfig";

export type BasicInformationDisplayItem = {
  key: string;
  label: string;
  value: string;
};

const SUMMARY_KEYS = [
  "project_type",
  "requested_by",
  "project_leader",
  "lab_performing_tests",
  "test_result",
  "sub_contract",
  "test_fee",
];

const SUMMARY_EXCLUDED_KEYS = new Set(["dl_number", "product_description", "test_item"]);

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
  const values = response?.latest_confirmed?.values;
  if (!values) {
    return [];
  }
  return SUMMARY_KEYS.flatMap((key) => {
    const value = values[key]?.trim();
    if (!value || SUMMARY_EXCLUDED_KEYS.has(key)) {
      return [];
    }
    return [
      {
        key,
        label: BASIC_INFORMATION_FIELD_LABELS[key] ?? key,
        value,
      },
    ];
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
