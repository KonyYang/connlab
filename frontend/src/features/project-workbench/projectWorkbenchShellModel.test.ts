import { describe, expect, it } from "vitest";
import type { ProjectLifecycleResponse } from "../../api/client";
import { deriveProjectLifecycleReadonlyView } from "../project-lifecycle/projectLifecycleReadonlyModel";
import {
  deriveProjectWorkbenchShellModel,
  type ProjectWorkbenchShellModelInput,
} from "./projectWorkbenchShellModel";

describe("deriveProjectWorkbenchShellModel", () => {
  it("maps an active temporary project to temporary planning", () => {
    const shell = deriveProjectWorkbenchShellModel(
      shellInput({
        hasRegisteredProject: false,
        hasActiveMatrix: false,
        hasCandidateMatrix: false,
        latestLtr: null,
      })
    );

    expect(shell.lifecycleLabel).toBe("Active");
    expect(shell.formalIdentityLabel).toBe("Temporary planning");
    expect(shell.matrixAuthorityLabel).toBe("No Matrix");
    expect(shell.primaryWorkspace).toBe("temporary_planning");
    expect(shell.primaryWorkspaceLabel).toBe("Temporary planning");
  });

  it("maps a registered project without active Matrix to Matrix setup", () => {
    const shell = deriveProjectWorkbenchShellModel(
      shellInput({
        hasRegisteredProject: true,
        hasActiveMatrix: false,
        hasCandidateMatrix: true,
      })
    );

    expect(shell.formalIdentityLabel).toBe("Registered project");
    expect(shell.matrixAuthorityLabel).toBe("Candidate Matrix");
    expect(shell.primaryWorkspace).toBe("matrix_setup");
    expect(shell.primaryWorkspaceLabel).toBe("Matrix authority setup");
  });

  it("keeps an active Matrix project focused on Matrix authority", () => {
    const shell = deriveProjectWorkbenchShellModel(
      shellInput({
        hasRegisteredProject: true,
        hasActiveMatrix: true,
        hasCandidateMatrix: true,
      })
    );

    expect(shell.matrixAuthorityLabel).toBe("Active Matrix");
    expect(shell.primaryWorkspace).toBe("active_matrix");
    expect(shell.primaryWorkspaceLabel).toBe("Active Matrix workspace");
    expect(shell.outputEntries.map((entry) => entry.label)).toEqual([
      "Basic Information",
      "Project Folder",
      "Required Forms",
      "Fee Evaluation",
      "LTR/Public Drive",
    ]);
  });

  it("uses business-readable stopped copy with readonly reason", () => {
    const lifecycle = lifecycleResponse({
      lifecycle_state: "stopped",
      status: "cancelled",
      status_label: "Stopped",
      stopped_at: "2026-06-26T08:00:00Z",
      stopped_reason: "Customer requested pause.",
      allowed_actions: ["resume", "close"],
      readonly: true,
    });
    const shell = deriveProjectWorkbenchShellModel(
      shellInput({
        lifecycle,
        lifecycleReadonlyView: deriveProjectLifecycleReadonlyView(lifecycle),
        hasRegisteredProject: true,
        hasActiveMatrix: true,
      })
    );

    expect(shell.lifecycleLabel).toBe("Stopped");
    expect(shell.readonly).toBe(true);
    expect(shell.bannerTitle).toBe("Project stopped");
    expect(shell.reasonLine).toBe("Reason: Customer requested pause.");
    expect(shell.primaryWorkspace).toBe("active_matrix");
  });

  it("maps closed completed projects to closed review without archive copy", () => {
    const lifecycle = lifecycleResponse({
      lifecycle_state: "closed",
      closure_type: "completed",
      close_reason_category: "completed",
      close_reason_label: "Completed",
      status: "closed",
      status_label: "Closed",
      closed_at: "2026-06-27T09:00:00Z",
      closed_reason: "All outputs accepted.",
      readonly: true,
      allowed_actions: ["activate"],
    });
    const shell = deriveProjectWorkbenchShellModel(
      shellInput({
        lifecycle,
        lifecycleReadonlyView: deriveProjectLifecycleReadonlyView(lifecycle),
        hasRegisteredProject: true,
        hasActiveMatrix: true,
      })
    );

    expect(shell.lifecycleLabel).toBe("Closed: Completed");
    expect(shell.primaryWorkspace).toBe("readonly_archive");
    expect(shell.allowedLifecycleActions).toEqual([]);
    expect(shell.primaryActionLabel).toBe("Review closed project");
    expect(shell.primaryWorkspaceLabel).toBe("Closed project review");
    const userFacingCopy = [
      shell.lifecycleLabel,
      shell.bannerTitle,
      shell.bannerMessage,
      shell.primaryWorkspaceLabel,
      shell.primaryWorkspaceSummary,
      shell.primaryActionLabel,
    ].join(" ");
    expect(userFacingCopy).not.toMatch(/archive/i);
  });

  it("maps closed non-completed projects without raw enum copy", () => {
    const lifecycle = lifecycleResponse({
      lifecycle_state: "closed",
      closure_type: "administrative",
      close_reason_category: "other",
      close_reason_label: "Other",
      status: "closed",
      status_label: "Closed",
      closed_at: "2026-06-27T09:00:00Z",
      closed_reason: "Business owner closed the project.",
      readonly: true,
      allowed_actions: ["activate"],
    });
    const shell = deriveProjectWorkbenchShellModel(
      shellInput({
        lifecycle,
        lifecycleReadonlyView: deriveProjectLifecycleReadonlyView(lifecycle),
        hasRegisteredProject: true,
        hasActiveMatrix: false,
      })
    );

    expect(shell.lifecycleLabel).toBe("Closed: Other");
    expect(shell.primaryWorkspace).toBe("readonly_archive");
    expect(JSON.stringify(shell)).not.toMatch(
      /cancelled|closed_completed|closed_administrative|lifecycle_state|closure_type/
    );
    const userFacingCopy = [
      shell.lifecycleLabel,
      shell.bannerTitle,
      shell.bannerMessage,
      shell.primaryWorkspaceLabel,
      shell.primaryWorkspaceSummary,
      shell.primaryActionLabel,
    ].join(" ");
    expect(userFacingCopy).not.toMatch(/administrative|archive/i);
  });

  it("keeps the output rail current-feature only", () => {
    const shell = deriveProjectWorkbenchShellModel(shellInput());
    const renderedLabels = shell.outputEntries.map((entry) => entry.label).join(" ");

    expect(renderedLabels).toContain("Basic Information");
    expect(renderedLabels).toContain("Project Folder");
    expect(renderedLabels).not.toMatch(
      /Report generation|StepInstance|AI|permissions|LAN|multi-user/
    );
  });
});

function shellInput(
  overrides: Partial<ProjectWorkbenchShellModelInput> = {}
): ProjectWorkbenchShellModelInput {
  const lifecycle = overrides.lifecycle ?? lifecycleResponse();
  return {
    projectIdentity: "DL-2026-06-001 Connector Sample",
    hasRegisteredProject: true,
    latestLtr: "DL-2026-06-001",
    hasActiveMatrix: false,
    hasCandidateMatrix: true,
    folderReady: false,
    basicInformationStatus: "missing",
    packageStatus: null,
    requiredFormsStatus: null,
    confirmedFeeStatus: "missing",
    publicDriveStatus: null,
    lifecycle,
    lifecycleReadonlyView:
      overrides.lifecycleReadonlyView ?? deriveProjectLifecycleReadonlyView(lifecycle),
    ...overrides,
  };
}

function lifecycleResponse(
  overrides: Partial<ProjectLifecycleResponse> = {}
): ProjectLifecycleResponse {
  return {
    project_id: "2cd4b0e7ff6f4df99448c9ffdd78629f",
    lifecycle_state: "active",
    closure_type: null,
    status_label: "Active",
    readonly: false,
    allowed_actions: ["stop", "close"],
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
