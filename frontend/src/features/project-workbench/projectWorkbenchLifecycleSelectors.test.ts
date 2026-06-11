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

  it("defaults active Matrix projects with package blockers to package preparation", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      packageStatus: "blocked",
      packageBlockers: ["Confirm Fee before preparing the project package."],
    });

    expect(lifecycle.mode).toBe("package_preparation");
    expect(lifecycle.stageLabel).toBe("Package preparation");
    expect(lifecycle.nextAction.tone).toBe("blocked");
    expect(lifecycle.nextAction.title).toBe("Resolve package blockers");
    expect(lifecycle.nextAction.reason).toBe(
      "Confirm Fee before preparing the project package."
    );
    expect(lifecycle.tabs.map((tab) => tab.mode)).toEqual([
      "overview",
      "package_preparation",
      "execution_console",
    ]);
  });

  it("routes inactive folder template blockers to Settings", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle({
      ...baseInput,
      hasLtr: true,
      hasActiveMatrix: true,
      packageStatus: "blocked",
      packageBlockers: ["Enable project folder template in Settings."],
    });

    expect(lifecycle.nextAction.title).toBe("Resolve package blockers");
    expect(lifecycle.nextAction.reason).toBe(
      "Enable project folder template in Settings."
    );
    expect(lifecycle.nextAction.actionLabel).toBe("Open Settings");
    expect(lifecycle.nextAction.actionTarget).toBe("settings");
  });

  it("shows an overview mode for active Matrix projects", () => {
    const lifecycle = deriveProjectWorkbenchLifecycle(
      {
        ...baseInput,
        hasLtr: true,
        hasActiveMatrix: true,
        packageStatus: "blocked",
      },
      "overview"
    );

    expect(lifecycle.mode).toBe("overview");
    expect(lifecycle.stageLabel).toBe("Project overview");
    expect(lifecycle.tabs.map((tab) => tab.mode)).toEqual([
      "overview",
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
      },
      "execution_console"
    );

    expect(lifecycle.mode).toBe("execution_console");
    expect(lifecycle.stageLabel).toBe("Execution console");
    expect(lifecycle.nextAction.tone).toBe("ready");
    expect(lifecycle.nextAction.title).toBe("Use Matrix as the execution map");
    expect(lifecycle.tabs.map((tab) => tab.mode)).toEqual([
      "overview",
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
  section2Status: null,
  hasPackagePreviewError: false,
};
