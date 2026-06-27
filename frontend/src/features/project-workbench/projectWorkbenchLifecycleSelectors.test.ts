import { describe, expect, it } from "vitest";
import {
  deriveProjectWorkbenchLifecycle,
  type WorkbenchLifecycleInput,
} from "./projectWorkbenchLifecycleSelectors";
import type { ProjectLifecycleReadonlyView } from "../project-lifecycle/projectLifecycleReadonlyModel";

describe("deriveProjectWorkbenchLifecycle", () => {
  it("keeps projects without a DL number in temporary planning", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: false,
      hasActiveMatrix: false,
    });

    expect(lifecycle.mode).toBe("temporary_planning");
    expect(lifecycle.stageLabel).toBe("Temporary planning");
    expect(lifecycle.nextAction.actionTarget).toBe("matrix");
    expect(lifecycle.nextAction.title).toBe("Plan Matrix and fee before DL registration");
    expect(lifecycle.tabs.map((tab) => tab.mode)).toEqual(["temporary_planning"]);
  });

  it("focuses registered projects without active Matrix authority on setup", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: false,
      hasCandidateMatrix: true,
    });

    expect(lifecycle.mode).toBe("registered_setup");
    expect(lifecycle.stageLabel).toBe("Matrix authority setup");
    expect(lifecycle.nextAction.title).toBe("Confirm Matrix authority");
    expect(lifecycle.nextAction.actionTarget).toBe("matrix");
    expect(lifecycle.tabs.map((tab) => tab.mode)).toEqual(["registered_setup"]);
  });

  it("defaults active Matrix projects to Project Folder request-material collection", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      folderReady: true,
      packageStatus: "blocked",
      packageBlockers: ["Confirm Fee before preparing the project package."],
      requestMaterialStatus: "ready",
    });

    expect(lifecycle.mode).toBe("package_preparation");
    expect(lifecycle.stageLabel).toBe("Project Folder preparation");
    expect(lifecycle.nextAction.tone).toBe("neutral");
    expect(lifecycle.nextAction.title).toBe("Collect request material");
    expect(lifecycle.nextAction.actionTarget).toBe("request_material");
    expect(lifecycle.tabs.map((tab) => tab.label)).toEqual([
      "Project Folder",
      "Execution",
    ]);
  });

  it("routes project folder blockers after request material is collected", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      folderReady: true,
      requestMaterialStatus: "collected",
      packageStatus: "blocked",
      packageBlockers: ["Confirm Fee before preparing the project folder."],
    });

    expect(lifecycle.nextAction.tone).toBe("blocked");
    expect(lifecycle.nextAction.title).toBe("Resolve project folder blockers");
    expect(lifecycle.nextAction.reason).toBe(
      "Confirm Fee before preparing the project folder."
    );
    expect(lifecycle.nextAction.actionTarget).toBe("fee");
  });

  it("keeps stopped no-DL projects out of temporary planning", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: false,
      lifecycleReadonlyView: stoppedReadonlyView,
      hasActiveMatrix: false,
    });

    expect(lifecycle.mode).toBe("overview");
    expect(lifecycle.stageLabel).toBe("Project stopped");
    expect(lifecycle.nextAction.title).toBe("Read-only project");
    expect(lifecycle.nextAction.actionTarget).toBeUndefined();
    expect(lifecycle.tabs.map((tab) => tab.mode)).toEqual(["temporary_planning"]);
  });

  it("uses lifecycle readonly state instead of legacy cancelled status", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      isCancelled: false,
      lifecycleReadonlyView: closedCompletedReadonlyView,
      hasActiveMatrix: true,
    });

    expect(lifecycle.mode).toBe("package_preparation");
    expect(lifecycle.stageLabel).toBe("Project closed as completed");
    expect(lifecycle.nextAction.title).toBe("Read-only project");
    expect(lifecycle.nextAction.actionTarget).toBeUndefined();
    expect(lifecycle.tabs.map((tab) => tab.mode)).toEqual([
      "package_preparation",
      "execution_console",
    ]);
  });

  it("keeps registered setup readable for closed projects without active Matrix authority", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      isCancelled: false,
      lifecycleReadonlyView: closedCompletedReadonlyView,
      hasActiveMatrix: false,
      hasCandidateMatrix: true,
    });

    expect(lifecycle.mode).toBe("overview");
    expect(lifecycle.stageLabel).toBe("Project closed as completed");
    expect(lifecycle.nextAction.title).toBe("Read-only project");
    expect(lifecycle.nextAction.actionTarget).toBeUndefined();
    expect(lifecycle.tabs.map((tab) => tab.mode)).toEqual(["registered_setup"]);
  });

  it("routes missing folder structure to repair action", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      folderReady: true,
      requestMaterialStatus: "collected",
      officialFolderCheckStatus: "missing",
    });

    expect(lifecycle.nextAction.title).toBe("Repair folder structure");
    expect(lifecycle.nextAction.reason).toBe("Required local project folders are missing.");
    expect(lifecycle.nextAction.actionTarget).toBe("official_folder_repair");
  });

  it("routes folder check request errors to refresh action", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      folderReady: true,
      requestMaterialStatus: "collected",
      hasOfficialFolderCheckError: true,
    });

    expect(lifecycle.nextAction.title).toBe("Refresh project folder check");
    expect(lifecycle.nextAction.actionTarget).toBe("official_folder_refresh");
  });

  it("shows upload to public drive when public-drive preview is ready", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      folderReady: true,
      requestMaterialStatus: "collected",
      officialFolderCheckStatus: "ready",
      packageStatus: "ready",
      publicDrivePreviewStatus: "ready",
    });

    expect(lifecycle.nextAction.title).toBe("Upload Project Folder to public drive");
    expect(lifecycle.nextAction.actionLabel).toBe("Upload to public drive");
    expect(lifecycle.nextAction.actionTarget).toBe("public_drive_upload");
  });

  it("does not show public-drive upload before project folder readiness is loaded", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      folderReady: true,
      requestMaterialStatus: "collected",
      officialFolderCheckStatus: "ready",
      packageStatus: null,
      publicDrivePreviewStatus: "ready",
    });

    expect(lifecycle.nextAction.title).toBe("Check project folder readiness");
    expect(lifecycle.nextAction.actionTarget).toBe("package");
  });

  it("blocks public-drive upload when preview reports conflict", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      folderReady: true,
      requestMaterialStatus: "collected",
      officialFolderCheckStatus: "ready",
      packageStatus: "ready",
      publicDrivePreviewStatus: "conflict",
      publicDrivePreviewBlockers: ["Resolve public-drive conflicts before upload."],
    });

    expect(lifecycle.nextAction.title).toBe("Review public-drive conflict");
    expect(lifecycle.nextAction.reason).toBe("Resolve public-drive conflicts before upload.");
    expect(lifecycle.nextAction.actionTarget).toBeUndefined();
  });

  it("keeps missing Public Project locations as a reminder without a Settings shortcut", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      folderReady: true,
      requestMaterialStatus: "collected",
      officialFolderCheckStatus: "ready",
      packageStatus: "ready",
      publicDrivePreviewStatus: "blocked",
      publicDrivePreviewBlockers: ["Public Project locations is not configured."],
    });

    expect(lifecycle.nextAction.title).toBe("Public-drive upload is not ready");
    expect(lifecycle.nextAction.actionTarget).toBeUndefined();
  });

  it("does not show collect again when request material only needs manual review", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      folderReady: true,
      requestMaterialStatus: "review_required",
      requestMaterialWarnings: [],
      packageStatus: "blocked",
      packageBlockers: ["Confirm Fee before preparing the project folder."],
    });

    expect(lifecycle.nextAction.tone).toBe("warning");
    expect(lifecycle.nextAction.title).toBe("Review request material");
    expect(lifecycle.nextAction.actionTarget).toBeUndefined();
  });

  it("routes inactive folder template blockers to Settings", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      folderTemplateReady: false,
      packageStatus: "blocked",
      packageBlockers: ["Enable project folder template in Settings."],
    });

    expect(lifecycle.nextAction.title).toBe("Enable project folder template");
    expect(lifecycle.nextAction.actionLabel).toBe("Open Settings");
    expect(lifecycle.nextAction.actionTarget).toBe("settings");
  });

  it("does not return an overview mode for active Matrix projects", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle(
      {
        ...baseInput,
        hasLtr: true,
        hasActiveMatrix: true,
        packageStatus: "blocked",
      },
      "overview"
    );

    expect(lifecycle.mode).toBe("package_preparation");
    expect(lifecycle.stageLabel).toBe("Project Folder preparation");
    expect(lifecycle.tabs.map((tab) => tab.mode)).toEqual([
      "package_preparation",
      "execution_console",
    ]);
  });

  it("allows operators to switch active Matrix projects into execution console", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle(
      {
        ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      packageStatus: "ready",
      requestMaterialStatus: "collected",
    },
      "execution_console"
    );

    expect(lifecycle.mode).toBe("execution_console");
    expect(lifecycle.stageLabel).toBe("Execution console");
    expect(lifecycle.nextAction.tone).toBe("ready");
    expect(lifecycle.nextAction.title).toBe("Use Matrix as the execution map");
    expect(lifecycle.tabs.map((tab) => tab.mode)).toEqual([
      "package_preparation",
      "execution_console",
    ]);
  });
});

const baseInput: WorkbenchLifecycleInput = {
  hasLtr: false,
  isCancelled: false,
  lifecycleReadonlyView: {
    mode: "active",
    readonly: false,
    title: "Project active",
    message: "",
    allowedActions: [],
    canResume: false,
    canClose: true,
    canWriteBusinessData: true,
    canUseReadonlyPreview: true,
  },
  hasActiveMatrix: false,
  hasCandidateMatrix: false,
  folderReady: false,
  folderTemplateReady: null,
  packageStatus: null,
  packageBlockers: [],
  packageWarnings: [],
  requestMaterialStatus: null,
  requestMaterialBlockers: [],
  requestMaterialWarnings: [],
  hasRequestMaterialPreviewError: false,
  officialFolderCheckStatus: null,
  officialFolderCheckBlockers: [],
  officialFolderCheckWarnings: [],
  hasOfficialFolderCheckError: false,
  section2Status: null,
  hasPackagePreviewError: false,
  publicDrivePreviewStatus: null,
  publicDrivePreviewBlockers: [],
  publicDrivePreviewWarnings: [],
  hasPublicDrivePreviewError: false,
};

const stoppedReadonlyView: ProjectLifecycleReadonlyView = {
  mode: "stopped_readonly",
  readonly: true,
  title: "Project stopped",
  message:
    "This project is paused. Review and preview actions remain available; editing resumes after the project is resumed.",
  allowedActions: ["resume", "close"],
  canResume: true,
  canClose: true,
  canWriteBusinessData: false,
  canUseReadonlyPreview: true,
};

const closedCompletedReadonlyView: ProjectLifecycleReadonlyView = {
  mode: "closed_completed_readonly",
  readonly: true,
  title: "Project closed as completed",
  message: "This project is archived as completed. Project data is read-only.",
  allowedActions: [],
  canResume: false,
  canClose: false,
  canWriteBusinessData: false,
  canUseReadonlyPreview: true,
};
