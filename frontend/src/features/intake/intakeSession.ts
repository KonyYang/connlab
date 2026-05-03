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
    packageImport: session.packageImport ?? null,
    selectedAssetId: textOrNull(session.selectedAssetId),
    selectedWordAssetId: textOrNull(session.selectedWordAssetId),
    selectedPrecheckCaseId: textOrNull(session.selectedPrecheckCaseId),
    sourceMode: session.sourceMode === "word" ? "word" : "msg",
    directWordName: textOrNull(session.directWordName)
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
