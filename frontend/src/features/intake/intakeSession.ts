import type { IntakePackageImport } from "../../api/client";

const INTAKE_SESSION_STORAGE_KEY = "connlab:intake-session";

export type IntakeSourceMode = "msg" | "word";

export type IntakeSessionState = {
  packageImport: IntakePackageImport | null;
  selectedAssetId: string | null;
  selectedWordAssetId: string | null;
  selectedPrecheckCaseId: string | null;
  sourceMode: IntakeSourceMode;
  directWordName: string | null;
};

export const EMPTY_INTAKE_SESSION: IntakeSessionState = {
  packageImport: null,
  selectedAssetId: null,
  selectedWordAssetId: null,
  selectedPrecheckCaseId: null,
  sourceMode: "msg",
  directWordName: null
};

export function loadIntakeSession(): IntakeSessionState {
  try {
    const raw = window.sessionStorage.getItem(INTAKE_SESSION_STORAGE_KEY);
    if (!raw) {
      return EMPTY_INTAKE_SESSION;
    }
    return normalizeIntakeSession(JSON.parse(raw));
  } catch {
    return EMPTY_INTAKE_SESSION;
  }
}

export function saveIntakeSession(session: IntakeSessionState): void {
  try {
    if (isEmptyIntakeSession(session)) {
      window.sessionStorage.removeItem(INTAKE_SESSION_STORAGE_KEY);
      return;
    }
    window.sessionStorage.setItem(INTAKE_SESSION_STORAGE_KEY, JSON.stringify(session));
  } catch {
    return;
  }
}

export function clearIntakeSession(): void {
  try {
    window.sessionStorage.removeItem(INTAKE_SESSION_STORAGE_KEY);
  } catch {
    return;
  }
}

function normalizeIntakeSession(value: unknown): IntakeSessionState {
  if (!value || typeof value !== "object") {
    return EMPTY_INTAKE_SESSION;
  }
  const session = value as Partial<IntakeSessionState>;
  return {
    packageImport: normalizePackageImport(session.packageImport),
    selectedAssetId: textOrNull(session.selectedAssetId),
    selectedWordAssetId: textOrNull(session.selectedWordAssetId),
    selectedPrecheckCaseId: textOrNull(session.selectedPrecheckCaseId),
    sourceMode: session.sourceMode === "word" ? "word" : "msg",
    directWordName: textOrNull(session.directWordName)
  };
}

function normalizePackageImport(value: unknown): IntakeSessionState["packageImport"] {
  if (!value || typeof value !== "object") {
    return null;
  }
  const packageImport = value as {
    package_id?: unknown;
    source_type?: unknown;
    package_status?: unknown;
    source_original_name?: unknown;
    subject?: unknown;
    sender_name?: unknown;
    sender_email?: unknown;
    received_at?: unknown;
    asset_count?: unknown;
    candidate_count?: unknown;
    next_action?: unknown;
    assets?: unknown;
    duplicate_check?: unknown;
    resolution_action?: unknown;
  };
  if (
    typeof packageImport.package_id !== "string" ||
    typeof packageImport.source_type !== "string" ||
    typeof packageImport.package_status !== "string" ||
    typeof packageImport.source_original_name !== "string" ||
    typeof packageImport.asset_count !== "number" ||
    typeof packageImport.candidate_count !== "number" ||
    typeof packageImport.next_action !== "string" ||
    !Array.isArray(packageImport.assets)
  ) {
    return null;
  }
  return {
    package_id: packageImport.package_id,
    source_type: packageImport.source_type,
    package_status: packageImport.package_status,
    source_original_name: packageImport.source_original_name,
    subject: typeof packageImport.subject === "string" ? packageImport.subject : null,
    sender_name: typeof packageImport.sender_name === "string" ? packageImport.sender_name : null,
    sender_email: typeof packageImport.sender_email === "string" ? packageImport.sender_email : null,
    received_at: typeof packageImport.received_at === "string" ? packageImport.received_at : null,
    asset_count: packageImport.asset_count,
    candidate_count: packageImport.candidate_count,
    next_action: packageImport.next_action,
    assets: packageImport.assets as IntakePackageImport["assets"],
    duplicate_check:
      typeof packageImport.duplicate_check === "object"
        ? (packageImport.duplicate_check as IntakePackageImport["duplicate_check"])
        : undefined,
    resolution_action:
      typeof packageImport.resolution_action === "string" ? packageImport.resolution_action : undefined
  };
}

function textOrNull(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

function isEmptyIntakeSession(session: IntakeSessionState): boolean {
  return (
    session.packageImport === null &&
    session.selectedAssetId === null &&
    session.selectedWordAssetId === null &&
    session.selectedPrecheckCaseId === null &&
    session.sourceMode === EMPTY_INTAKE_SESSION.sourceMode &&
    session.directWordName === null
  );
}
