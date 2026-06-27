import { describe, expect, it } from "vitest";
import {
  deriveProjectWorkbenchLifecycleActions,
  deriveProjectWorkbenchLifecycle,
  type WorkbenchLifecycleInput,
} from "./projectWorkbenchLifecycleSelectors";
import type { ProjectLifecycleResponse } from "../../api/client";
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

describe("deriveProjectWorkbenchLifecycleActions", () => {
  it("allows Stop only for active projects with an explicit stop action", () => {
    expect(
      deriveProjectWorkbenchLifecycleActions(
        lifecycleResponse({ allowed_actions: ["stop", "close"] }),
        baseInput.lifecycleReadonlyView,
        { hasRegisteredProject: true }
      )
    ).toMatchObject({
      primaryAction: "stop",
      canStop: true,
      canResume: false,
      canClose: true,
      canCloseCompleted: true,
      canCloseAdministrative: true,
      preferredClosePath: "completed",
    });

    expect(
      deriveProjectWorkbenchLifecycleActions(
        lifecycleResponse({ allowed_actions: ["close"] }),
        baseInput.lifecycleReadonlyView
      )
    ).toMatchObject({
      primaryAction: "none",
      canStop: false,
      canResume: false,
      canClose: true,
      canCloseCompleted: false,
      canCloseAdministrative: true,
      preferredClosePath: "administrative",
    });
  });

  it("allows Resume and completed/admin close for stopped registered projects", () => {
    const actions = deriveProjectWorkbenchLifecycleActions(
      lifecycleResponse({
        lifecycle_state: "stopped",
        status: "cancelled",
        status_label: "Stopped",
        readonly: true,
        allowed_actions: ["resume", "close"],
      }),
      stoppedReadonlyView,
      { hasRegisteredProject: true }
    );

    expect(actions).toMatchObject({
      primaryAction: "resume",
      canStop: false,
      canResume: true,
      canClose: true,
      canCloseCompleted: true,
      canCloseAdministrative: true,
      preferredClosePath: "completed",
      readonlyReason:
        "This project is paused. Review and preview actions remain available; editing resumes after the project is resumed.",
    });
  });

  it("defaults temporary no-DL projects to administrative close", () => {
    const actions = deriveProjectWorkbenchLifecycleActions(
      lifecycleResponse({ allowed_actions: ["stop", "close"] }),
      baseInput.lifecycleReadonlyView,
      { hasRegisteredProject: false }
    );

    expect(actions).toMatchObject({
      canStop: true,
      canClose: true,
      canCloseCompleted: false,
      canCloseAdministrative: true,
      preferredClosePath: "administrative",
    });
  });

  it("does not offer lifecycle write actions for closed projects", () => {
    expect(
      deriveProjectWorkbenchLifecycleActions(
        lifecycleResponse({
          lifecycle_state: "closed",
          closure_type: "completed",
          status: "closed",
          status_label: "Closed",
          readonly: true,
          allowed_actions: [],
        }),
        closedCompletedReadonlyView
      )
    ).toMatchObject({
      primaryAction: "none",
      canStop: false,
      canResume: false,
      canClose: false,
      canCloseCompleted: false,
      canCloseAdministrative: false,
      preferredClosePath: null,
    });
  });

  it("does not expose raw lifecycle enum copy in close action labels", () => {
    const actions = deriveProjectWorkbenchLifecycleActions(
      lifecycleResponse({ allowed_actions: ["stop", "close"] }),
      baseInput.lifecycleReadonlyView,
      { hasRegisteredProject: true }
    );

    expect(JSON.stringify(actions)).not.toMatch(
      /lifecycle_state|closure_type|closed_completed|closed_administrative|cancelled/
    );
    expect(actions.completedCloseLabel).toBe("Close as completed");
    expect(actions.administrativeCloseLabel).toBe("Close administratively");
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

function lifecycleResponse(
  overrides: Partial<ProjectLifecycleResponse> = {}
): ProjectLifecycleResponse {
  return {
    project_id: "project-1",
    lifecycle_state: "active",
    closure_type: null,
    status_label: "Active",
    readonly: false,
    allowed_actions: ["stop"],
    status: "active",
    stopped_at: null,
    stopped_reason: null,
    closed_at: null,
    closed_reason: null,
    completion_summary: null,
    warnings: [],
    ...overrides,
  };
}
