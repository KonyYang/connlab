import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type {
  ConfirmedMatrixSnapshot,
  Project,
  ProjectPackagePreview,
  ProjectTestPlanDraft,
} from "../../api/client";
import { ProjectWorkbenchLayout } from "./ProjectWorkbenchLayout";
import type { ProjectRuntimeConsoleModel } from "./useProjectRuntimeConsoleModel";

vi.mock("./ProjectFolderCreationPanel", () => ({
  ProjectFolderCreationPanel: () => <section>Folder setup panel</section>,
}));

vi.mock("./ProjectSection2SyncPanel", () => ({
  ProjectSection2SyncPanel: () => <section>Section 2 dates panel</section>,
}));

vi.mock("./ProjectPackagePreviewPanel", () => ({
  ProjectPackagePreviewPanel: () => <section>Project package panel</section>,
}));

vi.mock("./ProjectWorkbenchMatrixProjectionPanel", () => ({
  ProjectWorkbenchMatrixProjectionPanel: () => <section>Matrix projection panel</section>,
}));

vi.mock("./FeeEvaluationStatusSummary", () => ({
  FeeEvaluationStatusSummary: () => <section>Fee summary panel</section>,
}));

describe("ProjectWorkbenchLayout lifecycle modes", () => {
  it("shows temporary planning without formal package or execution surfaces", () => {
    const onOpenFeeEvaluation = vi.fn();
    renderWorkbench({
      latestLtr: null,
      matrixAuthorityDraft: null,
      packagePreview: null,
    }, undefined, { onOpenFeeEvaluation });

    expect(screen.getByText("Temporary planning")).toBeTruthy();
    expect(screen.getByText("Plan Matrix and fee before DL registration")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Open Matrix" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Open Fee Evaluation" })).toBeTruthy();
    expect(screen.getByText("Build Matrix and estimate fee before DL registration.")).toBeTruthy();
    expect(onOpenFeeEvaluation).not.toHaveBeenCalled();
    expect(screen.queryByText("Folder setup panel")).toBeNull();
    expect(screen.queryByText("Section 2 dates panel")).toBeNull();
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.queryByText("Matrix projection panel")).toBeNull();
    expect(screen.queryByLabelText("Step workspace")).toBeNull();
  });

  it("uses project_no as DL fallback when latest LTR lookup is unavailable", () => {
    renderWorkbench(
      {
        latestLtr: null,
        activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
        matrixAuthorityDraft: testPlanDraft,
        packagePreview: readyPackagePreview,
      },
      {
        project_no: "DL-2026-06-777",
      }
    );

    expect(screen.getByText("Package preparation")).toBeTruthy();
    expect(
      screen.getByText(/DL-2026-06-777 \| Connector Sample \| spec.docx/)
    ).toBeTruthy();
    expect(screen.queryByText("Temporary planning")).toBeNull();
  });

  it("focuses DL projects without active Matrix authority on Matrix setup", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      matrixAuthorityDraft: null,
      matrixCandidateDraft: testPlanDraft,
      packagePreview: null,
    });

    expect(screen.getByText("Matrix authority setup")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Confirm Matrix authority" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Open Matrix" })).toBeTruthy();
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.queryByLabelText("Step workspace")).toBeNull();
  });

  it("separates package preparation from execution once active Matrix exists", async () => {
    const user = userEvent.setup();
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      packagePreview: readyPackagePreview,
    });

    expect(screen.getByText("Package preparation")).toBeTruthy();
    expect(screen.getByText("Project package panel")).toBeTruthy();
    expect(screen.queryByText("Folder setup panel")).toBeNull();
    expect(screen.queryByText("Matrix projection panel")).toBeNull();
    expect(screen.queryByLabelText("Step workspace")).toBeNull();

    await user.click(screen.getByRole("tab", { name: "Execution" }));

    expect(screen.getByText("Execution console")).toBeTruthy();
    expect(screen.getByText("Matrix projection panel")).toBeTruthy();
    expect(screen.getByLabelText("Step workspace")).toBeTruthy();
    expect(screen.queryByText("Project package panel")).toBeNull();
  });

  it("shows overview as a lifecycle summary without package or execution work surfaces", async () => {
    const user = userEvent.setup();
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      packagePreview: blockedPackagePreview,
    });

    await user.click(screen.getByRole("tab", { name: "Overview" }));

    expect(screen.getByText("Lifecycle summary")).toBeTruthy();
    expect(screen.getByText("Current blockers")).toBeTruthy();
    expect(
      screen.getAllByText("Project folder template is inactive in Settings.").length
    ).toBeGreaterThan(0);
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.queryByText("Matrix projection panel")).toBeNull();
    expect(screen.queryByLabelText("Step workspace")).toBeNull();
  });

  it("opens Settings from the next action when the folder template blocks package readiness", async () => {
    const user = userEvent.setup();
    const onOpenSettings = vi.fn();
    renderWorkbench(
      {
        latestLtr: "DL-2026-06-001",
        activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
        matrixAuthorityDraft: testPlanDraft,
        packagePreview: folderTemplateBlockedPackagePreview,
      },
      {},
      { onOpenSettings }
    );

    const settingsButton = screen.getByRole("button", { name: "Open Settings" });
    expect(settingsButton).toBeTruthy();
    await user.click(settingsButton);
    expect(onOpenSettings).toHaveBeenCalledTimes(1);
  });

  it("uses active confirmed Matrix authority even when legacy test-plan drafts are absent", async () => {
    const user = userEvent.setup();
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: null,
      matrixCandidateDraft: testPlanDraft,
      packagePreview: readyPackagePreview,
    });

    expect(screen.getByText("Package preparation")).toBeTruthy();
    expect(screen.getByText("Project package panel")).toBeTruthy();
    expect(screen.queryByText("Matrix authority setup")).toBeNull();

    await user.click(screen.getByRole("tab", { name: "Execution" }));

    expect(screen.getByText("Execution console")).toBeTruthy();
    expect(screen.getByText("Matrix projection panel")).toBeTruthy();
    expect(screen.getByLabelText("Step workspace")).toBeTruthy();
  });

  it("keeps package mode checklist-first with secondary links and collapsed detail panels", async () => {
    const user = userEvent.setup();
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      packagePreview: blockedPackagePreview,
    });

    expect(screen.getByText("Package preparation")).toBeTruthy();
    expect(screen.getByText("Prepare controlled package files before placing them in Submitted Material.")).toBeTruthy();
    expect(screen.getByText("Project package panel")).toBeTruthy();
    expect(screen.getByText("Secondary links")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Matrix Editor" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Fee Evaluation" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Open Matrix" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Open Fee Evaluation" })).toBeNull();
    expect(screen.queryByText("Folder setup panel")).toBeNull();
    expect(screen.queryByText("Section 2 dates panel")).toBeNull();
    expect(screen.queryByText("Fee summary panel")).toBeNull();

    await user.click(screen.getByRole("button", { name: "Folder setup details" }));

    expect(screen.getByText("Folder setup panel")).toBeTruthy();
    expect(screen.queryByText("Section 2 dates panel")).toBeNull();
    expect(screen.queryByText("Fee summary panel")).toBeNull();
  });
});

function renderWorkbench(
  overrides: Partial<ProjectRuntimeConsoleModel> = {},
  projectOverrides: Partial<Project> = {},
  callbacks: Partial<Pick<
    ProjectWorkbenchLayoutPropsForTest,
    "onBack" | "onOpenMatrixEditor" | "onOpenFeeEvaluation"
    | "onOpenSettings"
  >> = {}
): void {
  const currentProject = { ...project, ...projectOverrides };
  render(
    <ProjectWorkbenchLayout
      runtimeModel={buildRuntimeModel(overrides, currentProject)}
      project={currentProject}
      onBack={callbacks.onBack ?? vi.fn()}
      onOpenMatrixEditor={callbacks.onOpenMatrixEditor ?? vi.fn()}
      onOpenFeeEvaluation={callbacks.onOpenFeeEvaluation ?? vi.fn()}
      onOpenSettings={callbacks.onOpenSettings ?? vi.fn()}
    />
  );
}

type ProjectWorkbenchLayoutPropsForTest = Parameters<typeof ProjectWorkbenchLayout>[0];

function buildRuntimeModel(
  overrides: Partial<ProjectRuntimeConsoleModel>,
  currentProject: Project = project
): ProjectRuntimeConsoleModel {
  return {
    baselineItems: [],
    error: null,
    folderReady: false,
    folderResources: {
      outputRoot: null,
      template: null,
    },
    latestLtr: "DL-2026-06-001",
    activeConfirmedMatrixSnapshot: null,
    activeConfirmedMatrixLoading: false,
    matrixAuthorityDraft: null,
    matrixCandidateDraft: null,
    matrixDraft: null,
    matrixDraftError: null,
    matrixDraftLoading: false,
    message: null,
    packagePreview: null,
    packagePreviewError: null,
    packagePreviewLoading: false,
    project: currentProject,
    projectId: currentProject.project_id,
    runtimeAuthoritySync: {
      hasActiveAuthority: false,
      hasUnconfirmedCandidate: false,
      authorityVersion: null,
      candidateVersion: null,
      snapshotVersion: null,
      shouldRefreshProjection: false,
    },
    runtimeProjectionError: null,
    runtimeProjectionLoading: false,
    runtimeProjectionSnapshot: null,
    runtimeSelectedTokenReference: null,
    section2SyncError: null,
    section2SyncLoading: false,
    section2SyncPreview: null,
    section2SyncSyncing: false,
    setRuntimeSelectedTokenReference: vi.fn(),
    onFolderCreated: vi.fn(),
    onRefreshPackagePreview: vi.fn(),
    onRefreshSection2Sync: vi.fn(),
    onSyncSection2: vi.fn(),
    versionStatus: {
      upstream: [],
      downstream: [],
    },
    ...overrides,
  } as ProjectRuntimeConsoleModel;
}

const project: Project = {
  project_id: "2cd4b0e7ff6f4df99448c9ffdd78629f",
  product_name: "Connector Sample",
  requestor: "Lab User",
  status: "active",
};

const testPlanDraft: ProjectTestPlanDraft = {
  draft_id: "draft-1",
  project_id: project.project_id,
  source_document_path: "C:/Specs/spec.docx",
  source_document_name: "spec.docx",
  source_format: "docx",
  source_asset_id: null,
  source_case_id: null,
  source_draft_id: null,
  status: "draft",
  version: 1,
  payload: {
    groups: [],
    warnings: [],
    blockers: [],
  },
  created_at: "2026-06-11T00:00:00Z",
  updated_at: "2026-06-11T00:00:00Z",
  reviewed_at: null,
};

const readyPackagePreview: ProjectPackagePreview = {
  project_id: project.project_id,
  status: "ready",
  project_folder: {
    status: "ready",
    path: "C:/Projects/DL-2026-06-001",
    message: "Latest project folder is available.",
  },
  authority_context: {
    confirmed_matrix_id: "CM1",
    confirmed_revision: 1,
    confirmed_fee_id: "CF1",
    confirmed_fee_revision: 1,
    confirmed_fee_status: "current",
  },
  required_items: [],
  optional_items: [],
  blockers: [],
  warnings: [],
};

const blockedPackagePreview: ProjectPackagePreview = {
  ...readyPackagePreview,
  status: "blocked",
  project_folder: {
    status: "blocked",
    path: null,
    message: "Create the project folder before previewing package targets.",
  },
  blockers: [
    "Create the project folder before previewing package targets.",
    "Confirm Fee before preparing the project package.",
  ],
  warnings: ["One Section 2 source date is missing."],
};

const folderTemplateBlockedPackagePreview: ProjectPackagePreview = {
  ...blockedPackagePreview,
  blockers: ["Enable project folder template in Settings."],
};

const confirmedMatrixSnapshot: ConfirmedMatrixSnapshot = {
  version: {
    confirmed_matrix_id: "CM1",
    project_id: project.project_id,
    project_matrix_draft_id: "pmd-1",
    source_import_id: "smi-1",
    source_snapshot_id: "sms-1",
    confirmed_revision: 1,
    is_active_authority: true,
    status: "active",
    confirmed_by: "Lab User",
    confirmed_at: "2026-06-11T00:00:00Z",
    superseded_by_confirmed_matrix_id: null,
    superseded_at: null,
    superseded_reason: null,
    pre_test_buffer_days: null,
    post_test_buffer_days: null,
    sample_received_date: null,
    planned_test_start_date: null,
    planned_test_complete_date: null,
    estimated_completion_date: null,
  },
  groups: [],
  rows: [],
  cells: [],
};
