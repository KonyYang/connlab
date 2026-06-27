import type {
  ProjectLifecycleResponse,
  ProjectRegistryRow,
} from "../../api/client";

export type ProjectRegistryView = "ongoing" | "planning" | "closed" | "all";

export type ProjectRegistryLifecycleRow = {
  row: ProjectRegistryRow;
  lifecycle: ProjectLifecycleResponse | null;
  lifecycleError?: string | null;
};

type RegistryLifecycleState =
  | "active"
  | "stopped"
  | "closed_completed"
  | "closed_administrative"
  | "closed";

type OperationalQueue =
  | "planning"
  | "matrix_needed"
  | "ready_to_test"
  | "folder_blocked"
  | "folder_created";

const OPERATIONAL_STATUS_LABELS: Record<OperationalQueue, string> = {
  planning: "Planning",
  matrix_needed: "Matrix Needed",
  ready_to_test: "Ready to Test",
  folder_blocked: "Folder Blocked",
  folder_created: "Folder Created",
};

export function filterRegistryRowsForView(
  rows: ProjectRegistryLifecycleRow[],
  view: ProjectRegistryView
): ProjectRegistryLifecycleRow[] {
  if (view === "all") {
    return rows;
  }
  return rows.filter(({ row, lifecycle }) => registryViewForRow(row, lifecycle) === view);
}

export function registryViewForRow(
  row: ProjectRegistryRow,
  lifecycle: ProjectLifecycleResponse | null
): ProjectRegistryView {
  const state = registryLifecycleState(row, lifecycle);
  if (isClosedLifecycleState(state)) {
    return "closed";
  }
  return hasFormalProjectIdentity(row) ? "ongoing" : "planning";
}

export function registryLifecycleLabel(
  row: ProjectRegistryRow,
  lifecycle: ProjectLifecycleResponse | null
): string {
  const state = registryLifecycleState(row, lifecycle);
  switch (state) {
    case "stopped":
      return "Stopped";
    case "closed_completed":
      return "Closed: Completed";
    case "closed_administrative":
      return "Closed: Administrative";
    case "closed":
      return "Closed";
    case "active":
    default:
      return "Active";
  }
}

export function registryStatusLabel(
  row: ProjectRegistryRow,
  lifecycle: ProjectLifecycleResponse | null
): string {
  const state = registryLifecycleState(row, lifecycle);
  if (state !== "active") {
    return registryLifecycleLabel(row, lifecycle);
  }
  return OPERATIONAL_STATUS_LABELS[classifyOperationalQueue(row)];
}

export function registryNextStepLabel(
  row: ProjectRegistryRow,
  lifecycle: ProjectLifecycleResponse | null
): string {
  const state = registryLifecycleState(row, lifecycle);
  switch (state) {
    case "stopped":
      return hasFormalProjectIdentity(row)
        ? "Review or resume in Workbench"
        : "Resume or administratively archive from Workbench";
    case "closed_completed":
      return "View readonly completed archive";
    case "closed_administrative":
      return "View readonly administrative archive";
    case "closed":
      return "View readonly archive";
    case "active":
    default:
      return operationalNextStepLabel(row);
  }
}

export function registryRowActionLabel(
  row: ProjectRegistryRow,
  lifecycle: ProjectLifecycleResponse | null
): string {
  return isClosedLifecycleState(registryLifecycleState(row, lifecycle))
    ? "Open archive"
    : "Open Workbench";
}

export function registryRowActionAriaLabel(
  row: ProjectRegistryRow,
  lifecycle: ProjectLifecycleResponse | null
): string {
  const action = registryRowActionLabel(row, lifecycle);
  const state = registryLifecycleState(row, lifecycle);
  const stateCopy = isClosedLifecycleState(state) ? "archived project" : "project workspace";
  return `${action} for ${businessIdentifier(row)}, ${stateCopy}`;
}

export function registryLifecycleClassName(
  row: ProjectRegistryRow,
  lifecycle: ProjectLifecycleResponse | null
): string {
  return `registry-lifecycle-${registryLifecycleState(row, lifecycle).replace("_", "-")}`;
}

function registryLifecycleState(
  row: ProjectRegistryRow,
  lifecycle: ProjectLifecycleResponse | null
): RegistryLifecycleState {
  if (lifecycle?.lifecycle_state === "stopped") {
    return "stopped";
  }
  if (lifecycle?.lifecycle_state === "closed") {
    if (lifecycle.closure_type === "completed") {
      return "closed_completed";
    }
    if (lifecycle.closure_type === "administrative") {
      return "closed_administrative";
    }
    return "closed";
  }
  if (row.status === "cancelled") {
    return "stopped";
  }
  if (row.status === "closed") {
    return "closed";
  }
  return "active";
}

function isClosedLifecycleState(state: RegistryLifecycleState): boolean {
  return (
    state === "closed" ||
    state === "closed_completed" ||
    state === "closed_administrative"
  );
}

function classifyOperationalQueue(row: ProjectRegistryRow): OperationalQueue {
  if (row.status === "folder_created") {
    return "folder_created";
  }
  if (row.status === "ltr_registered") {
    return "matrix_needed";
  }
  if (!hasFormalProjectIdentity(row)) {
    return "planning";
  }
  return "matrix_needed";
}

function operationalNextStepLabel(row: ProjectRegistryRow): string {
  switch (classifyOperationalQueue(row)) {
    case "planning":
      return "Continue planning in Workbench";
    case "matrix_needed":
      return "Open Matrix authority";
    case "ready_to_test":
      return "Open Execution map";
    case "folder_blocked":
      return "Review request material";
    case "folder_created":
      return "Continue setup in Workbench";
    default:
      return "Continue planning in Workbench";
  }
}

function hasFormalProjectIdentity(row: ProjectRegistryRow): boolean {
  return (
    row.display_project_id_kind === "registered" ||
    row.has_registered_ltr ||
    hasDisplayText(row.ltr_number) ||
    hasDisplayText(row.registered_ltr_number)
  );
}

function hasDisplayText(value: string | null | undefined): boolean {
  return Boolean(value?.trim());
}

function businessIdentifier(row: ProjectRegistryRow): string {
  return row.display_project_id;
}
