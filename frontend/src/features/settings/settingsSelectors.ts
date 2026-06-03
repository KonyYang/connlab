import type {
  ExternalResource,
  ExternalResourceType
} from "../../api/client";
import { SHARED_RESOURCE_CONFIGS, type SettingsResourceConfig } from "./settingsResourceConfig";

export type SettingsResourceRow = SettingsResourceConfig & {
  resource: ExternalResource | null;
  path: string;
  active: boolean;
};

export function buildSettingsResourceRows(
  resources: ExternalResource[]
): SettingsResourceRow[] {
  const byType = new Map<ExternalResourceType, ExternalResource>(
    resources.map((resource) => [resource.resource_type, resource])
  );

  return SHARED_RESOURCE_CONFIGS.map((config) => {
    const resource = byType.get(config.resourceType) ?? null;
    return {
      ...config,
      resource,
      path: resource?.path ?? "",
      active: resource?.active ?? true
    };
  });
}
