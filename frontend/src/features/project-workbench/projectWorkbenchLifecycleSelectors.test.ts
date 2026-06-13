import { describe, expect, it } from "vitest";
import {
  deriveProjectWorkbenchLifecycle,
  type WorkbenchLifecycleInput,
} from "./projectWorkbenchLifecycleSelectors";

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
  section2Status: null,
  hasPackagePreviewError: false,
};
