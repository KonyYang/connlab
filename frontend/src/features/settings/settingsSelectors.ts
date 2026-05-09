import type {
  ExternalResource,
  ExternalResourceType,
  ExternalResourceValidationStatus
} from "../../api/client";
import { SHARED_RESOURCE_CONFIGS, type SettingsResourceConfig } from "./settingsResourceConfig";

export type SettingsResourceRow = SettingsResourceConfig & {
  resource: ExternalResource | null;
  path: string;
  active: boolean;
  statusLabel: string;
  statusTone: "neutral" | "success" | "danger";
  failureReason: string | null;
  lastChecked: string;
};

export function buildSettingsResourceRows(
  resources: ExternalResource[]
): SettingsResourceRow[] {
  const byType = new Map<ExternalResourceType, ExternalResource>(
    resources.map((resource) => [resource.resource_type, resource])
  );

  return SHARED_RESOURCE_CONFIGS.map((config) => {
    const resource = byType.get(config.resourceType) ?? null;
    const status = resource?.validation_status ?? "not_validated";
    return {
      ...config,
      resource,
      path: resource?.path ?? "",
      active: resource?.active ?? true,
      statusLabel: statusLabel(status, resource?.validation_failure_reason ?? null),
      statusTone: statusTone(status),
      failureReason: resource?.validation_failure_reason ?? null,
      lastChecked: formatLastChecked(resource?.last_validated_at ?? null)
    };
  });
}

function statusLabel(
  status: ExternalResourceValidationStatus,
  failureReason: string | null
): string {
  if (status === "valid") {
    return "Valid";
  }
  if (status === "invalid") {
    return failureReason?.includes("Expected an existing") ? "Missing" : "Invalid";
  }
  return "Not checked";
}

function statusTone(status: ExternalResourceValidationStatus): "neutral" | "success" | "danger" {
  if (status === "valid") {
    return "success";
  }
  if (status === "invalid") {
    return "danger";
  }
  return "neutral";
}

function formatLastChecked(value: string | null): string {
  if (!value) {
    return "Never";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString();
}
