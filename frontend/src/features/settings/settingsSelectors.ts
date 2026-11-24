import type {
  ExternalResource,
  ExternalResourceType
} from "../../api/client";
import { SHARED_RESOURCE_CONFIGS, type SettingsResourceConfig } from "./settingsResourceConfig";

export type SettingsResourceRow = SettingsResourceConfig & {
  resource: ExternalResource | null;
  path: string;
  active: boolean;
  worksheetName: string | null;
};

export function visibleSettingsResourceConfigs(resources: ExternalResource[]): SettingsResourceConfig[] {
  const override = resources.find(resource => resource.resource_type === "ir_dwv_record_template" && resource.active);
  const folder = resources.find(resource => resource.resource_type === "project_folder_template" && resource.active);
  const keepOverride = override?.path.trim() && !isDiscoverableIrDwvTemplate(override.path, folder?.path);
  return SHARED_RESOURCE_CONFIGS.filter(config => config.resourceType !== "ir_dwv_record_template" || keepOverride);
}

function isDiscoverableIrDwvTemplate(file: string, folder: string | undefined): boolean {
  if (!folder?.trim()) return false;
  const path = normalizeLocation(file);
  const separator = path.lastIndexOf("/");
  const name = path.slice(separator + 1);
  return separator >= 0 && path.slice(0, separator) === normalizeLocation(folder)
    && name.endsWith(".xlsx") && !name.startsWith("~$")
    && (name.includes("ir&dwv") || name.includes("fdqf-e-033"));
}

function normalizeLocation(path: string): string {
  return path.trim().replace(/\\/g, "/").replace(/\/+$/, "").toLowerCase();
}

export function buildSettingsResourceRows(
  resources: ExternalResource[]
): SettingsResourceRow[] {
  const byType = new Map<ExternalResourceType, ExternalResource>(
    resources.map((resource) => [resource.resource_type, resource])
  );

  return visibleSettingsResourceConfigs(resources).map((config) => {
    const resource = byType.get(config.resourceType) ?? null;
    return {
      ...config,
      resource,
      path: resource?.path ?? "",
      active: resource?.active ?? true,
      worksheetName:
        config.resourceType === "standard_record_excel"
          ? resource?.worksheet_name ?? "认可标准"
          : null
    };
  });
}
