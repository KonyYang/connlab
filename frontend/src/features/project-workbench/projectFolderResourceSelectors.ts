import type { ExternalResource } from "../../api/client";

type FolderResourceType = "project_folder_template" | "project_output_root";

export type ConfiguredFolderResources = {
  template: ExternalResource | null;
  outputRoot: ExternalResource | null;
};

export function configuredFolderResources(
  resources: ExternalResource[]
): ConfiguredFolderResources {
  return {
    template: findResource(resources, "project_folder_template"),
    outputRoot: findResource(resources, "project_output_root")
  };
}

export function resourceBlockedReason(
  resource: ExternalResource | null,
  label: string
): string | null {
  if (!resource) {
    return `Configure ${label} in Settings before previewing the project folder.`;
  }
  if (!resource.active) {
    return `${label} is inactive in Settings. Enable it before previewing the project folder.`;
  }
  if (resource.validation_status !== "valid") {
    if (resource.validation_failure_reason) {
      return `${label} is not valid: ${resource.validation_failure_reason}`;
    }
    return `${label} must be validated in Settings before previewing the project folder.`;
  }
  return null;
}

function findResource(
  resources: ExternalResource[],
  resourceType: FolderResourceType
): ExternalResource | null {
  return resources.find((item) => item.resource_type === resourceType) ?? null;
}
