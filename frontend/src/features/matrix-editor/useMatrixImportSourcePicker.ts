import { useCallback } from "react";

import { listProjectTestPlanSourceCandidates, type MatrixSourceCandidate } from "../../api/client";
import {
  hasMatrixImportSourcePicker,
  pickMatrixImportSourceFromDesktop,
} from "../../desktop/pathPickerBridge";

export type MatrixImportSourceChoice =
  | { kind: "browser"; candidates?: MatrixSourceCandidate[]; warnings?: string[]; error?: string | null }
  | { kind: "cancelled" }
  | { kind: "selected"; path: string }
  | { kind: "unsupported"; path: string };

export async function chooseMatrixImportSource(
  projectId: string
): Promise<MatrixImportSourceChoice> {
  if (!hasMatrixImportSourcePicker()) {
    try {
      const projection = await listProjectTestPlanSourceCandidates(projectId);
      return {
        kind: "browser",
        candidates: projection.candidates,
        warnings: projection.warnings,
        error: null,
      };
    } catch {
      return {
        kind: "browser",
        candidates: [],
        warnings: [],
        error: "Could not load project sources. You can upload another file instead.",
      };
    }
  }
  let initialDirectory: string | null = null;
  try {
    const projection = await listProjectTestPlanSourceCandidates(projectId);
    initialDirectory = projection.preferred_import_directory;
  } catch {
    // Directory projection is an optional convenience; the OS picker remains usable.
  }
  const path = await pickMatrixImportSourceFromDesktop(initialDirectory);
  if (!path) {
    return { kind: "cancelled" };
  }
  const extension = path.slice(path.lastIndexOf(".")).toLowerCase();
  if (extension === ".doc") {
    return { kind: "browser" };
  }
  if (extension !== ".pdf" && extension !== ".docx") {
    return { kind: "unsupported", path };
  }
  return { kind: "selected", path };
}

export function useMatrixImportSourcePicker(projectId: string) {
  return useCallback(() => chooseMatrixImportSource(projectId), [projectId]);
}
