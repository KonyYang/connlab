import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type {
  ConfirmedMatrixSnapshot,
  Project,
  OfficialFolderCheckPreview,
  ProjectPackagePreview,
  RequestMaterialPreview,
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

vi.mock("../../api/client", () => ({
  previewTemporaryProjectDelete: vi.fn(() => new Promise(() => {})),
  deleteTemporaryProject: vi.fn().mockResolvedValue({
    project_id: "2cd4b0e7ff6f4df99448c9ffdd78629f",
    deleted: true,
    deleted_temporary_context: true,
  }),
  stopProject: vi.fn().mockResolvedValue({
    project_id: "2cd4b0e7ff6f4df99448c9ffdd78629f",
    previous_status: "draft",
    status: "cancelled",
    status_label: "Stopped",
    reason: "Project will not continue.",
    audit_recorded: true,
  }),
}));

describe("ProjectWorkbenchLayout lifecycle modes", () => {
  it("shows temporary planning without formal package or execution surfaces", () => {
    const onOpenFeeEvaluation = vi.fn();
    renderWorkbench({
      latestLtr: null,
      matrixAuthorityDraft: null,
      packagePreview: null,
    }, undefined, { onOpenFeeEvaluation });

    expect(screen.getByText("Temporary Planning")).toBeTruthy();
    expect(screen.getByText("Plan Matrix and fee before DL registration")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Open Matrix" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Open Fee Evaluation" })).toHaveProperty(
      "disabled",
      true
    );
    expect(screen.getByText(/This project has no registered LTR Number yet/)).toBeTruthy();
    expect(screen.getByText(/Official package actions require LTR registration/)).toBeTruthy();
    expect(screen.getByText("Project lifecycle")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Stop project" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Delete temporary project" })).toBeTruthy();
    expect(onOpenFeeEvaluation).not.toHaveBeenCalled();
    expect(screen.queryByText("Folder setup panel")).toBeNull();
    expect(screen.queryByText("Section 2 dates panel")).toBeNull();
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.queryByText("Matrix projection panel")).toBeNull();
    expect(screen.queryByLabelText("Step workspace")).toBeNull();
  });

  it("enables temporary Fee planning only when a Matrix draft exists", async () => {
    const user = userEvent.setup();
    const onOpenFeeEvaluation = vi.fn();
    renderWorkbench({
      latestLtr: null,
      matrixDraft: testPlanDraft,
      packagePreview: null,
    }, undefined, { onOpenFeeEvaluation });

    const feeButton = screen.getByRole("button", { name: "Open Fee Evaluation" });
    expect(feeButton).toHaveProperty("disabled", false);
    await user.click(feeButton);
    expect(onOpenFeeEvaluation).toHaveBeenCalledTimes(1);
  });

  it("does not offer temporary planning or promotion for cancelled no-DL projects", () => {
    renderWorkbench(
      {
        latestLtr: null,
        matrixAuthorityDraft: null,
        packagePreview: null,
      },
      { status: "cancelled" }
    );

    expect(screen.getByText("Stopped project")).toBeTruthy();
    expect(screen.getByText("No action")).toBeTruthy();
    expect(screen.queryByText("Temporary Planning")).toBeNull();
    expect(screen.queryByRole("button", { name: "Stop project" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Convert to Formal Project" })).toBeNull();
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
        sample_description: "Coolpower HDF 3.40mm pin",
        test_item: "Qualification Testing",
      }
    );

    expect(screen.getByText("Project Folder preparation")).toBeTruthy();
    expect(
      screen.getByText("DL-2026-06-777 Coolpower HDF 3.40mm pin Qualification Testing")
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
    expect(screen.getByRole("button", { name: "Stop project" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Delete temporary project" })).toBeNull();
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
      requestMaterialPreview: collectedRequestMaterialPreview,
      folderReady: true,
    });

    expect(screen.getByText("Project Folder preparation")).toBeTruthy();
    expect(screen.getAllByText("Request material").length).toBeGreaterThan(0);
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.queryByText("Folder setup panel")).toBeNull();
    expect(screen.queryByText("Matrix projection panel")).toBeNull();
    expect(screen.queryByLabelText("Step workspace")).toBeNull();

    await user.click(screen.getByRole("tab", { name: "Execution" }));

    expect(screen.getByText("Execution console")).toBeTruthy();
    expect(screen.getByText("Matrix projection panel")).toBeTruthy();
    expect(screen.getByLabelText("Step workspace")).toBeTruthy();
    expect(screen.queryByText("Project package panel")).toBeNull();
  });

  it("does not show a redundant overview tab when package preparation is the main task", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      folderReady: true,
      packagePreview: feeBlockedPackagePreview,
      requestMaterialPreview: collectedRequestMaterialPreview,
    });

    expect(screen.queryByRole("tab", { name: "Overview" })).toBeNull();
    expect(screen.getByRole("tab", { name: "Project Folder" })).toBeTruthy();
    expect(screen.getByRole("tab", { name: "Execution" })).toBeTruthy();
    expect(screen.getByText("Project Folder preparation")).toBeTruthy();
    expect(
      screen.getAllByText("Confirm Fee before preparing the project folder.").length
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
      requestMaterialPreview: collectedRequestMaterialPreview,
      folderReady: true,
    });

    expect(screen.getByText("Project Folder preparation")).toBeTruthy();
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.queryByText("Matrix authority setup")).toBeNull();

    await user.click(screen.getByRole("tab", { name: "Execution" }));

    expect(screen.getByText("Execution console")).toBeTruthy();
    expect(screen.getByText("Matrix projection panel")).toBeTruthy();
    expect(screen.getByLabelText("Step workspace")).toBeTruthy();
  });

  it("shows the Project Folder task list without secondary package links", async () => {
    const user = userEvent.setup();
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      packagePreview: blockedPackagePreview,
      requestMaterialPreview: readyRequestMaterialPreview,
      folderReady: true,
    });

    expect(screen.getByText("Project Folder preparation")).toBeTruthy();
    expect(
      screen.getAllByText("Prepare local project files before public-drive submission.").length
    ).toBeGreaterThan(0);
    expect(screen.getAllByText("Request material").length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Collect request material" })).toBeTruthy();
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.queryByText("Secondary links")).toBeNull();
    expect(screen.queryByRole("button", { name: "Matrix Editor" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Fee Evaluation" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Open Matrix" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Open Fee Evaluation" })).toBeNull();
    expect(screen.queryByText("Folder setup panel")).toBeNull();
    expect(screen.queryByText("Section 2 dates panel")).toBeNull();
    expect(screen.queryByText("Fee summary panel")).toBeNull();

    expect(user).toBeTruthy();
  });

  it("shows folder structure repair as the single next action", async () => {
    const user = userEvent.setup();
    const onRepairOfficialFolderStructure = vi.fn();
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      packagePreview: readyPackagePreview,
      requestMaterialPreview: collectedRequestMaterialPreview,
      officialFolderCheckPreview: missingOfficialFolderCheckPreview,
      folderReady: true,
      onRepairOfficialFolderStructure,
    });

    expect(screen.getByText("Folder structure")).toBeTruthy();
    expect(screen.getAllByText("Missing folders").length).toBeGreaterThan(0);

    await user.click(screen.getByRole("button", { name: "Repair folder structure" }));

    expect(onRepairOfficialFolderStructure).toHaveBeenCalledTimes(1);
  });

  it("uses official folder check as the Customer Feedback source in the Project Folder list", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      packagePreview: customerFeedbackReadyPackagePreview,
      requestMaterialPreview: collectedRequestMaterialPreview,
      officialFolderCheckPreview: customerFeedbackDeferredOfficialFolderCheckPreview,
      folderReady: true,
    });

    expect(screen.getByText("Customer Feedback form")).toBeTruthy();
    expect(screen.getAllByText("Deferred").length).toBeGreaterThan(0);
    expect(screen.queryByText("Customer Feedback form ready from package preview")).toBeNull();
  });

  it("shows one local project folder creation action before package preparation", async () => {
    const user = userEvent.setup();
    const onCreateOfficialWorkspace = vi.fn();
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      officialWorkspacePreview: {
        project_id: "project-1",
        dl_number: "DL-2026-06-001",
        status: "ready",
        local_workspace_root: "D:/Projects",
        local_workspace_path: "D:/Projects/DL-2026-06-001",
        source_book_path: "D:/Projects/DL-2026-06-001/Source Book",
        template_path: "D:/Template/DL-XXXX-YY-ZZZ project",
        official_project_folder_path:
          "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
        manifest_path: "D:/Projects/DL-2026-06-001/.connlab/manifest.json",
        template_root_mode: "template_root",
        blockers: [],
        warnings: [],
        planned_paths: [],
      },
      officialWorkspaceCreating: false,
      onCreateOfficialWorkspace,
    });

    expect(
      screen.getByRole("button", { name: "Create local project folder" })
    ).toBeTruthy();
    expect(
      screen.getByText("The official project folder has not been created locally.")
    ).toBeTruthy();
    expect(screen.getByRole("button", { name: "Stop project" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Delete temporary project" })).toBeNull();
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.queryByRole("button", { name: "Open Settings" })).toBeNull();

    await user.click(
      screen.getByRole("button", { name: "Create local project folder" })
    );

    expect(onCreateOfficialWorkspace).toHaveBeenCalledTimes(1);
  });

  it("shows missing workspace settings as a blocker without a create shortcut", () => {
    const onCreateOfficialWorkspace = vi.fn();
    renderWorkbench(
      {
        latestLtr: "DL-2026-06-001",
        activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
        matrixAuthorityDraft: testPlanDraft,
        officialWorkspacePreview: {
          project_id: "project-1",
          dl_number: "DL-2026-06-001",
          status: "blocked",
          local_workspace_root: null,
          local_workspace_path: null,
          source_book_path: null,
          template_path: null,
          official_project_folder_path: null,
          manifest_path: null,
          template_root_mode: null,
          blockers: [
            "Project default save location is not configured.",
            "Template folder is not configured.",
          ],
          warnings: [],
          planned_paths: [],
        },
        officialWorkspaceCreating: false,
        onCreateOfficialWorkspace,
      }
    );

    expect(
      screen.getByText("Project folder template is not ready")
    ).toBeTruthy();
    expect(
      screen.getByText("ConnLab project folder template is not ready.")
    ).toBeTruthy();
    expect(
      screen.getByText(
        "Creation is unavailable until the ConnLab project template is ready."
      )
    ).toBeTruthy();
    expect(screen.queryByText("Configure workspace paths")).toBeNull();
    expect(screen.queryByText("Project default save location is not configured.")).toBeNull();
    expect(
      screen.queryByRole("button", { name: "Create local project folder" })
    ).toBeNull();
    expect(screen.queryByRole("button", { name: "Open Settings" })).toBeNull();
    expect(onCreateOfficialWorkspace).not.toHaveBeenCalled();
  });

  it("treats completed official workspace preview as project folder ready", async () => {
    const user = userEvent.setup();
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      folderReady: false,
      officialWorkspacePreview: {
        project_id: "project-1",
        dl_number: "DL-2026-06-001",
        status: "completed",
        local_workspace_root: "D:/Projects",
        local_workspace_path: "D:/Projects/DL-2026-06-001",
        source_book_path: "D:/Projects/DL-2026-06-001/Source Book",
        template_path: "D:/Template/DL-XXXX-YY-ZZZ project",
        official_project_folder_path:
          "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
        manifest_path: "D:/Projects/DL-2026-06-001/.connlab/manifest.json",
        template_root_mode: "template_root",
        blockers: [],
        warnings: [],
        planned_paths: [],
      },
      packagePreview: readyPackagePreview,
    });

    expect(
      screen.queryByRole("button", { name: "Create local project folder" })
    ).toBeNull();

    expect(screen.getAllByText("Project folder").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Created").length).toBeGreaterThan(0);
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
    officialWorkspacePreview: null,
    officialWorkspaceLoading: false,
    officialWorkspaceCreating: false,
    officialWorkspaceError: null,
    officialWorkspaceResult: null,
    officialFolderCheckPreview: null,
    officialFolderCheckLoading: false,
    officialFolderCheckRepairing: false,
    officialFolderCheckError: null,
    officialFolderRepairResult: null,
    requestMaterialPreview: null,
    requestMaterialLoading: false,
    requestMaterialCollecting: false,
    requestMaterialError: null,
    setRuntimeSelectedTokenReference: vi.fn(),
    onFolderCreated: vi.fn(),
    onRefreshPackagePreview: vi.fn(),
    onRefreshOfficialWorkspacePreview: vi.fn(),
    onCreateOfficialWorkspace: vi.fn(),
    onRefreshOfficialFolderCheck: vi.fn(),
    onRepairOfficialFolderStructure: vi.fn(),
    onRefreshRequestMaterial: vi.fn(),
    onCollectRequestMaterial: vi.fn(),
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

const feeBlockedPackagePreview: ProjectPackagePreview = {
  ...readyPackagePreview,
  status: "blocked",
  blockers: ["Confirm Fee before preparing the project folder."],
};

const folderTemplateBlockedPackagePreview: ProjectPackagePreview = {
  ...blockedPackagePreview,
  blockers: ["Enable project folder template in Settings."],
};

const customerFeedbackReadyPackagePreview: ProjectPackagePreview = {
  ...readyPackagePreview,
  required_items: [
    {
      key: "customer_feedback_form",
      label: "Customer Feedback form",
      status: "ready",
      message: "Customer Feedback form ready from package preview",
      target_path: "D:/Projects/DL-2026-06-001/Customer Feedback.docx",
    },
  ],
};

const readyRequestMaterialPreview: RequestMaterialPreview = {
  project_id: project.project_id,
  local_workspace_path: "D:/Projects/DL-2026-06-001",
  source_book_path: "D:/Projects/DL-2026-06-001/Source Book",
  official_project_folder_path:
    "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
  status: "ready",
  items: [
    {
      source_asset_id: "asset-1",
      source_asset_type: "application_form",
      source_role: "selected_application_form",
      source_name: "application.docx",
      source_path: "D:/Intake/application.docx",
      dedupe_key: "path:d:/intake/application.docx",
      target_area: "submitted_material",
      target_path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Submitted Material/application.docx",
      action: "copy",
      status: "planned",
      message: "Ready to copy.",
      review_required: false,
      size_bytes: 100,
      sha256: "a".repeat(64),
    },
  ],
  blockers: [],
  warnings: [],
};

const collectedRequestMaterialPreview: RequestMaterialPreview = {
  ...readyRequestMaterialPreview,
  status: "collected",
  items: readyRequestMaterialPreview.items.map((item) => ({
    ...item,
    status: "copied",
    message: "Copied.",
  })),
};

const missingOfficialFolderCheckPreview: OfficialFolderCheckPreview = {
  project_id: project.project_id,
  status: "missing",
  local_workspace_path: "D:/Projects/DL-2026-06-001",
  official_project_folder_path:
    "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
  required_folders: [
    {
      key: "photos",
      label: "Photos",
      kind: "folder",
      status: "missing",
      path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Photos",
      message: "Folder is missing.",
      repairable: true,
    },
  ],
  required_files: [
    {
      key: "submitted_material",
      label: "Submitted Material",
      kind: "file",
      status: "ready",
      path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Submitted Material/application.docx",
      message: "Confirmed collected files are present.",
      repairable: false,
    },
  ],
  blockers: [],
  warnings: [],
  next_action: "repair_folders",
};

const customerFeedbackDeferredOfficialFolderCheckPreview: OfficialFolderCheckPreview = {
  ...missingOfficialFolderCheckPreview,
  status: "ready",
  required_folders: [],
  required_files: [
    {
      key: "submitted_material",
      label: "Submitted Material",
      kind: "file",
      status: "ready",
      path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Submitted Material/application.docx",
      message: "Confirmed collected files are present.",
      repairable: false,
    },
    {
      key: "customer_feedback",
      label: "Customer Feedback form",
      kind: "file",
      status: "deferred",
      path: null,
      message: "Customer Feedback generation is handled by a later task.",
      repairable: false,
    },
  ],
  next_action: "none",
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
