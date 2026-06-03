import type { ExternalResourceType } from "../api/client";

type DesktopPathPickerBridge = {
  pickExternalResourcePath: (
    resourceType: ExternalResourceType
  ) => Promise<string | null>;
};

declare global {
  interface Window {
    connlabDesktopPathPicker?: DesktopPathPickerBridge;
  }
}

export function hasDesktopPathPickerBridge(): boolean {
  return typeof window.connlabDesktopPathPicker?.pickExternalResourcePath === "function";
}

export function pickExternalResourcePathFromDesktop(
  resourceType: ExternalResourceType
): Promise<string | null> {
  const picker = window.connlabDesktopPathPicker;
  if (!picker) {
    return Promise.resolve(null);
  }
  return picker.pickExternalResourcePath(resourceType);
}
