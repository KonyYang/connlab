import type { ExternalResourceType } from "../../api/client";

export type SettingsResourceCategory =
  | "Public registration and record files"
  | "Default locations";

export type SettingsResourceConfig = {
  resourceType: ExternalResourceType;
  label: string;
  category: SettingsResourceCategory;
  expectedKind: string;
  registryBacked: true;
};

export const SHARED_RESOURCE_CONFIGS: SettingsResourceConfig[] = [
  {
    resourceType: "ltr_workbook",
    label: "LTR registration workbook",
    category: "Public registration and record files",
    expectedKind: "Excel file",
    registryBacked: true
  },
  {
    resourceType: "standard_record_excel",
    label: "Standard version file path",
    category: "Public registration and record files",
    expectedKind: "Excel file",
    registryBacked: true
  },
  {
    resourceType: "equipment_calibration_excel",
    label: "Equipment calibration Excel",
    category: "Public registration and record files",
    expectedKind: "Excel file",
    registryBacked: true
  },
  {
    resourceType: "project_output_root",
    label: "Project default save location",
    category: "Default locations",
    expectedKind: "Folder",
    registryBacked: true
  },
  {
    resourceType: "project_folder_template",
    label: "Template folder",
    category: "Default locations",
    expectedKind: "Folder",
    registryBacked: true
  },
  {
    resourceType: "official_public_drive_root",
    label: "Public Project locations",
    category: "Default locations",
    expectedKind: "Folder",
    registryBacked: true
  }
];
