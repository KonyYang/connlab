import type { Project } from "../api/client";

type ProjectIdentityInput = {
  project: Project | null | undefined;
  latestLtr?: string | null;
  projectId: string;
  productFallback?: string | null;
  testItemFallback?: string | null;
};

export function buildProjectIdentityLine({
  project,
  latestLtr,
  projectId,
  productFallback,
  testItemFallback,
}: ProjectIdentityInput): string {
  const projectReference = deriveProjectReference({
    latestLtr,
    projectNo: project?.project_no,
    projectId: project?.project_id ?? projectId,
  });
  const projectLabel =
    cleanText(project?.sample_description) ||
    cleanText(project?.product_name) ||
    cleanText(productFallback) ||
    "Connector Project";
  const testItem = cleanText(project?.test_item) || cleanText(testItemFallback);

  return [projectReference, projectLabel, testItem].filter(Boolean).join(" ");
}

export function deriveProjectReference({
  latestLtr,
  projectNo,
  projectId,
}: {
  latestLtr?: string | null;
  projectNo?: string | null;
  projectId: string;
}): string {
  return cleanText(latestLtr) || cleanText(projectNo) || temporaryProjectId(projectId);
}

export function deriveRegisteredProjectReference(
  latestLtr: string | null | undefined,
  projectNo: string | null | undefined
): string | null {
  return cleanText(latestLtr) || cleanText(projectNo) || null;
}

function temporaryProjectId(projectId: string): string {
  return `TMP-${projectId.slice(0, 8).toUpperCase()}`;
}

function cleanText(value: string | null | undefined): string {
  return value?.trim() ?? "";
}
