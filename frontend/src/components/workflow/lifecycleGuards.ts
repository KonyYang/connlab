type LifecycleOperation =
  | "ltr_preview"
  | "ltr_commit"
  | "folder_preview"
  | "folder_generate"
  | "evidence_preview"
  | "evidence_place";

const LTR_ALLOWED = new Set(["confirmed", "precheck_passed"]);

export function lifecycleBlockReason(
  status: string | null | undefined,
  operation: LifecycleOperation
): string | null {
  if (!status) {
    return "Project state is still loading.";
  }
  if (status === "closed" || status === "cancelled") {
    return `Project is ${status}; reopen or create a correction workflow before changing project records or files.`;
  }
  if (operation === "ltr_preview" || operation === "ltr_commit") {
    return ltrReason(status);
  }
  if (operation === "folder_preview" || operation === "folder_generate") {
    return folderReason(status);
  }
  if (operation === "evidence_place") {
    return evidenceReason(status);
  }
  return null;
}

function ltrReason(status: string): string | null {
  if (status === "ltr_registered" || status === "folder_created") {
    return "Project already has a registered LTR; use renumber or correction workflow for changes.";
  }
  if (!LTR_ALLOWED.has(status)) {
    return `LTR registration requires confirmed project data before preview or commit. Current project status is ${status}.`;
  }
  return null;
}

function folderReason(status: string): string | null {
  if (status === "folder_created") {
    return "Project folder has already been created; use evidence or correction workflow for later changes.";
  }
  if (status !== "ltr_registered") {
    return `Project folder generation requires a registered LTR first. Current project status is ${status}.`;
  }
  return null;
}

function evidenceReason(status: string): string | null {
  if (status !== "folder_created") {
    return `Evidence placement requires a generated project folder first. Current project status is ${status}.`;
  }
  return null;
}
