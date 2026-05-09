import type { ExternalResourceType } from "../../api/client";

export type SettingsResourceCategory = "Shared resources" | "Local machine paths";

export type SettingsResourceConfig = {
  resourceType: ExternalResourceType;
  label: string;
  category: SettingsResourceCategory;
  expectedKind: string;
  registryBacked: true;
};

export type LocalMachinePathConfig = {
  key: string;
  label: string;
  category: SettingsResourceCategory;
  expectedKind: string;
  registryBacked: false;
  note: string;
};

export const SHARED_RESOURCE_CONFIGS: SettingsResourceConfig[] = [
  {
    resourceType: "ltr_workbook",
    label: "LTR workbook",
    category: "Shared resources",
    expectedKind: "Excel file",
    registryBacked: true
  },
  {
    resourceType: "project_folder_template",
    label: "Project folder template",
    category: "Shared resources",
    expectedKind: "Folder",
    registryBacked: true
  },
  {
    resourceType: "project_output_root",
    label: "Project output root",
    category: "Shared resources",
    expectedKind: "Folder",
    registryBacked: true
  },
  {
    resourceType: "application_form_template",
    label: "Application form template",
    category: "Shared resources",
    expectedKind: "Word file",
    registryBacked: true
  },
  {
    resourceType: "standard_record_excel",
    label: "Standard record Excel",
    category: "Shared resources",
    expectedKind: "Excel file",
    registryBacked: true
  },
  {
    resourceType: "equipment_calibration_excel",
    label: "Equipment calibration Excel",
    category: "Shared resources",
    expectedKind: "Excel file",
    registryBacked: true
  }
];

export const LOCAL_MACHINE_PATH_CONFIGS: LocalMachinePathConfig[] = [
  {
    key: "ltr_workbook_backup_directory",
    label: "LTR workbook backup directory",
    category: "Local machine paths",
    expectedKind: "Folder",
    registryBacked: false,
    note: "Configured by local TOML or environment settings for this workstation."
  },
  {
    key: "ltr_workbook_lock_directory",
    label: "LTR workbook lock directory",
    category: "Local machine paths",
    expectedKind: "Folder",
    registryBacked: false,
    note: "Configured by local TOML or environment settings for this workstation."
  }
];
