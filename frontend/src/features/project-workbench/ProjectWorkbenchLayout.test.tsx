import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type {
  ConfirmedMatrixSnapshot,
  ConfirmedFeeLatestResponse,
  Project,
  ProjectBasicInformationResponse,
  OfficialFolderCheckPreview,
  ProjectPackagePreview,
  PublicDriveUploadPreview,
  ProjectFolderRequiredFormsPreview,
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
  it("labels the topbar back button as the Projects overview navigation", async () => {
    const user = userEvent.setup();
    const onBack = vi.fn();
    renderWorkbench({}, undefined, { onBack });

    const backButton = screen.getByRole("button", { name: "Back to projects" });
    expect(backButton.getAttribute("title")).toBe("Back to Projects overview");
    expect(screen.queryByText("Project Workbench")).toBeNull();

    await user.click(backButton);
    expect(onBack).toHaveBeenCalledTimes(1);
  });

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

  it("uses lifecycle readonly state to block active Matrix write actions", async () => {
    const user = userEvent.setup();
    const onCreateOfficialWorkspace = vi.fn();
    renderWorkbench({
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      lifecycle: {
        project_id: "2cd4b0e7ff6f4df99448c9ffdd78629f",
        lifecycle_state: "closed",
        closure_type: "completed",
        status: "closed",
        status_label: "Closed",
        stopped_at: null,
        closed_at: "2026-06-27T09:00:00Z",
        allowed_actions: [],
        readonly: true,
        warnings: [],
      },
      matrixAuthorityDraft: testPlanDraft,
      officialWorkspacePreview: {
        project_id: "2cd4b0e7ff6f4df99448c9ffdd78629f",
        status: "ready",
        official_project_folder_path: "D:/ConnLab/Projects/DL-2026-06-001",
        blockers: [],
        warnings: [],
        planned_paths: [],
        conflict_paths: [],
      },
      onCreateOfficialWorkspace,
    });

    expect(screen.getAllByText("Project closed as completed").length).toBeGreaterThan(0);
    const folderButton = screen.getByRole("button", {
      name: "Generate project folder",
    });
    expect(folderButton).toHaveProperty("disabled", true);
    await user.click(folderButton);
    expect(onCreateOfficialWorkspace).not.toHaveBeenCalled();
  });

  it("hides lifecycle write controls for closed projects without active Matrix authority", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: null,
      matrixAuthorityDraft: null,
      matrixCandidateDraft: testPlanDraft,
      packagePreview: null,
      lifecycle: {
        project_id: "2cd4b0e7ff6f4df99448c9ffdd78629f",
        lifecycle_state: "closed",
        closure_type: "completed",
        status: "closed",
        status_label: "Closed",
        stopped_at: null,
        closed_at: "2026-06-27T09:00:00Z",
        allowed_actions: [],
        readonly: true,
        warnings: [],
      },
    });

    expect(screen.getAllByText("Project closed as completed").length).toBeGreaterThan(0);
    expect(screen.getByText("Read-only project")).toBeTruthy();
    expect(
      screen.getAllByText(
        "This project is archived as completed. Project data is read-only."
      ).length
    ).toBeGreaterThan(0);
    expect(screen.queryByRole("button", { name: "Stop project" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Edit Matrix" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Confirm Matrix authority" })).toBeNull();
    expect(screen.queryByText("Project lifecycle")).toBeNull();
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

    expect(screen.getByRole("region", { name: "Test Execution Workspace" })).toBeTruthy();
    expect(screen.getByLabelText("Project Workbench actions")).toBeTruthy();
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

  it("uses header actions and Matrix workspace once active Matrix exists", async () => {
    const user = userEvent.setup();
    const onOpenBasicInformation = vi.fn();
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      packagePreview: readyPackagePreview,
      requestMaterialPreview: collectedRequestMaterialPreview,
      folderReady: true,
    }, {}, { onOpenBasicInformation });

    expect(screen.getByRole("region", { name: "Test Execution Workspace" })).toBeTruthy();
    expect(screen.queryByLabelText("Project commands")).toBeNull();
    const actionBar = screen.getByLabelText("Project Workbench actions");
    expect(actionBar).toBeTruthy();
    expect(screen.getByRole("button", { name: "Matrix Editor" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Fee Evaluation" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Basic Information" })).toBeTruthy();
    expect(actionBar.textContent).toMatch(
      /Matrix Editor\s*Fee Evaluation\s*Basic Information\s*Update project folder/
    );
    await user.click(screen.getByRole("button", { name: "Basic Information" }));
    expect(onOpenBasicInformation).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("button", { name: "Folder ready" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Generate folder" })).toBeNull();
    expect(screen.getByRole("button", { name: "Update project folder" })).toBeTruthy();
    expect(screen.queryByText("Matrix confirmed")).toBeNull();
    expect(screen.queryByText("Fee confirmed")).toBeNull();
    expect(screen.queryByText("Folder generated")).toBeNull();
    expect(screen.getByText("Matrix projection panel")).toBeTruthy();
    expect(screen.getByLabelText("Step workspace")).toBeTruthy();
    expect(screen.getByLabelText("Folder Action")).toBeTruthy();
    expect(screen.queryByText("Project folder details")).toBeNull();
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.queryByText("Folder setup panel")).toBeNull();
    expect(screen.queryByRole("tab", { name: "Project Folder" })).toBeNull();
    expect(screen.queryByRole("tab", { name: "Execution" })).toBeNull();
  });

  it("shows the on-demand LTR Information update card after Folder Action", () => {
    const { container } = renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      packagePreview: readyPackagePreview,
      requestMaterialPreview: collectedRequestMaterialPreview,
      folderReady: true,
      basicInformation: confirmedBasicInformation,
    });

    const folderActionCard = screen.getByLabelText("Folder Action");
    const basicInformationCard = screen.getByLabelText("LTR Information");
    expect(basicInformationCard).toBeTruthy();
    expect(
      Boolean(
        folderActionCard.compareDocumentPosition(basicInformationCard) &
          globalThis.Node.DOCUMENT_POSITION_FOLLOWING
      )
    ).toBe(true);
    expect(screen.queryByText("Confirmed")).toBeNull();
    const summaryLabels = Array.from(
      container.querySelectorAll(".runtime-console-basic-information-list.is-summary dt")
    ).map((item) => item.textContent);
    expect(summaryLabels).toEqual([]);
    expect(screen.queryByText("In progress")).toBeNull();
    expect(screen.queryByText("1630.00")).toBeNull();
    expect(screen.queryByText("PO-123")).toBeNull();
    expect(screen.queryByText("NPD")).toBeNull();
    expect(screen.queryByText("Qualification")).toBeNull();
    expect(screen.queryByText("MP Cao")).toBeNull();
    expect(screen.queryByText("Even Yang")).toBeNull();
    expect(screen.queryByText("None")).toBeNull();
    expect(screen.queryByText("DL")).toBeNull();
    expect(screen.queryByText("DL/LTR Number")).toBeNull();
    expect(screen.queryByText("Product Description")).toBeNull();
    expect(screen.queryByText("Description P/N")).toBeNull();
    expect(screen.queryByText("Test Item")).toBeNull();
    expect(screen.queryByRole("button", { name: "Edit" })).toBeNull();
    expect(screen.queryByRole("button", { name: "View" })).toBeNull();
    expect(screen.getByRole("button", { name: "LTR update preview" }).hasAttribute("disabled")).toBe(false);
  });

  it("does not show mode tabs when the active Matrix workspace is the main task", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      folderReady: true,
      packagePreview: feeBlockedPackagePreview,
      requestMaterialPreview: collectedRequestMaterialPreview,
    });

    expect(screen.queryByRole("tab", { name: "Overview" })).toBeNull();
    expect(screen.queryByRole("tab", { name: "Project Folder" })).toBeNull();
    expect(screen.queryByRole("tab", { name: "Execution" })).toBeNull();
    expect(screen.getByRole("region", { name: "Test Execution Workspace" })).toBeTruthy();
    expect(screen.getByLabelText("Folder Action").textContent).toContain("Required forms");
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.getByText("Matrix projection panel")).toBeTruthy();
    expect(screen.getByLabelText("Step workspace")).toBeTruthy();
  });

  it("disables Update project folder when Required forms are blocked by Basic Information", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      folderReady: true,
      packagePreview: readyPackagePreview,
      requestMaterialPreview: collectedRequestMaterialPreview,
      requiredFormsPreview: basicInformationBlockedRequiredFormsPreview,
    });

    const folderButton = screen.getByRole("button", { name: "Update project folder" });
    expect(folderButton).toHaveProperty("disabled", true);
    expect(folderButton.getAttribute("title")).toBe(
      "Confirm Basic Information before generating Project Folder outputs."
    );
    const folderAction = screen.getByLabelText("Folder Action");
    expect(folderAction.textContent).toContain("Required forms");
    expect(folderAction.textContent).toContain(
      "Confirm Basic Information before generating Required forms."
    );
    expect(folderAction.textContent).toContain(
      "Confirm Basic Information before generating Project Folder outputs."
    );
  });

  it("keeps Update project folder disabled when an earlier folder task masks the Required forms blocker", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      folderReady: true,
      packagePreview: readyPackagePreview,
      requestMaterialPreview: readyRequestMaterialPreview,
      requiredFormsPreview: basicInformationBlockedRequiredFormsPreview,
    });

    expect(screen.getByLabelText("Folder Action").textContent).toContain(
      "Request material"
    );
    const folderButton = screen.getByRole("button", { name: "Update project folder" });
    expect(folderButton).toHaveProperty("disabled", true);
    expect(folderButton.getAttribute("title")).toBe(
      "Confirm Basic Information before generating Project Folder outputs."
    );
  });

  it("keeps the project folder button enabled when package template readiness is blocked", () => {
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

    expect(screen.getByRole("button", { name: "Generate project folder" })).toHaveProperty(
      "disabled",
      false
    );
    expect(screen.queryByRole("button", { name: "Open Settings" })).toBeNull();
    expect(onOpenSettings).not.toHaveBeenCalled();
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

    expect(screen.getByRole("region", { name: "Test Execution Workspace" })).toBeTruthy();
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.queryByText("Matrix authority setup")).toBeNull();
    expect(screen.getByText("Matrix projection panel")).toBeTruthy();
    expect(screen.getByLabelText("Step workspace")).toBeTruthy();
    expect(user).toBeTruthy();
  });

  it("keeps Project Folder details out of the active Matrix workspace", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      packagePreview: blockedPackagePreview,
      requestMaterialPreview: readyRequestMaterialPreview,
      folderReady: true,
    });

    expect(screen.getByRole("region", { name: "Test Execution Workspace" })).toBeTruthy();
    expect(screen.getByText("Matrix projection panel")).toBeTruthy();
    expect(screen.getAllByText("Request material").length).toBeGreaterThan(0);
    expect(screen.queryByLabelText("Project Folder progress")).toBeNull();
    expect(screen.queryByText("Project folder details")).toBeNull();
    expect(
      screen.getAllByRole("button", { name: "Collect request material" }).length
    ).toBeGreaterThan(0);
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.queryByText("Secondary links")).toBeNull();
    expect(screen.getByRole("button", { name: "Matrix Editor" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Open Matrix" })).toBeNull();
    expect(screen.getByRole("button", { name: "Fee Evaluation" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Open Fee" })).toBeNull();
    expect(screen.queryByText("Folder setup panel")).toBeNull();
    expect(screen.queryByText("Section 2 dates panel")).toBeNull();
    expect(screen.queryByText("Fee summary panel")).toBeNull();
  });

  it("maps Confirmed Fee latest status into Project Folder authority readiness", async () => {
    const cases: Array<{
      confirmedFeeLatest: ConfirmedFeeLatestResponse;
      selectedTask: string;
      expectedStatus: string;
    }> = [
      {
        confirmedFeeLatest: confirmedFeeLatest("missing"),
        selectedTask: "Confirmed Fee authority",
        expectedStatus: "Missing",
      },
      {
        confirmedFeeLatest: confirmedFeeLatest("stale"),
        selectedTask: "Confirmed Fee authority",
        expectedStatus: "Stale",
      },
      {
        confirmedFeeLatest: confirmedFeeLatest("current"),
        selectedTask: "Required forms",
        expectedStatus: "Ready to generate",
      },
    ];

    for (const item of cases) {
      const { unmount } = renderWorkbench({
        latestLtr: "DL-2026-06-001",
        activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
        matrixAuthorityDraft: testPlanDraft,
        folderReady: true,
        packagePreview: readyPackagePreview,
        requestMaterialPreview: collectedRequestMaterialPreview,
        officialFolderCheckPreview: customerFeedbackDeferredOfficialFolderCheckPreview,
        requiredFormsPreview: readyRequiredFormsPreview,
        confirmedFeeLatest: item.confirmedFeeLatest,
      });

      expect(screen.getByLabelText("Folder Action").textContent).toContain(
        item.selectedTask
      );
      expect(screen.getAllByText(item.expectedStatus).length).toBeGreaterThan(0);
      const feeButton = screen.getByRole("button", { name: "Fee Evaluation" });
      if (item.confirmedFeeLatest.status !== "current") {
        expect(screen.queryByRole("button", { name: "Generate required forms" })).toBeNull();
        expect(feeButton.className).not.toContain("is-review-required");
        expect(feeButton.getAttribute("title")).toBeNull();
      } else {
        expect(feeButton.className).not.toContain("is-review-required");
        expect(feeButton.getAttribute("title")).toBeNull();
        expect(
          screen.getAllByRole("button", { name: "Generate required forms" }).length
        ).toBeGreaterThan(0);
      }
      unmount();
    }
  });

  it("highlights Fee Evaluation when the current confirmed Fee has auto-rebased rows to review", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      folderReady: true,
      packagePreview: readyPackagePreview,
      requestMaterialPreview: collectedRequestMaterialPreview,
      confirmedFeeLatest: confirmedFeeLatest("current", { feeReviewRequiredCount: 2 }),
    });

    const feeButton = screen.getByRole("button", { name: "Fee Evaluation" });

    expect(feeButton.className).toContain("is-review-required");
    expect(feeButton.getAttribute("title")).toBe(
      "2 Fee Evaluation rows need pricing review."
    );
  });

  it("shows official workspace workflow errors from the project folder action", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      officialWorkspaceError: "Official project folder is missing.",
    });

    const alert = screen.getByRole("alert");

    expect(alert.textContent).toContain("Project folder workflow");
    expect(alert.textContent).toContain("Official project folder is missing.");
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

    expect(screen.getAllByText("Local project folder").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Needs repair").length).toBeGreaterThan(0);

    await user.click(screen.getAllByRole("button", { name: "Repair folder structure" })[0]);

    expect(onRepairOfficialFolderStructure).toHaveBeenCalledTimes(1);
  });

  it("does not use package preview Customer Feedback as the Project Folder source", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      packagePreview: customerFeedbackReadyPackagePreview,
      requestMaterialPreview: collectedRequestMaterialPreview,
      officialFolderCheckPreview: customerFeedbackDeferredOfficialFolderCheckPreview,
      folderReady: true,
    });

    expect(screen.getAllByText("Required forms").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Deferred").length).toBeGreaterThan(0);
    expect(screen.queryByText("Customer Feedback form")).toBeNull();
    expect(screen.queryByText("Customer Feedback form ready from package preview")).toBeNull();
  });

  it("keeps public-drive upload checklist details out of the active Matrix workspace", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      packagePreview: readyPackagePreview,
      requestMaterialPreview: collectedRequestMaterialPreview,
      officialFolderCheckPreview: customerFeedbackDeferredOfficialFolderCheckPreview,
      publicDriveUploadPreview: readyPublicDriveUploadPreview,
      folderReady: true,
    });

    expect(screen.queryByRole("button", { name: /Public drive upload/ })).toBeNull();
    expect(screen.queryByLabelText("Selected Project Folder task")).toBeNull();
    expect(
      screen.queryByText(
        "D:/PublicProjects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test"
      )
    ).toBeNull();
    expect(screen.queryByText("Submitted Material/application.docx")).toBeNull();
    expect(screen.getByLabelText("Folder Action")).toBeTruthy();
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

    expect(screen.getByRole("button", { name: "Generate project folder" })).toBeTruthy();
    expect(
      screen.getAllByText("Create the official project folder from the standard template.").length
    ).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Stop project" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Delete temporary project" })).toBeNull();
    expect(screen.queryByText("Project package panel")).toBeNull();
    expect(screen.queryByRole("button", { name: "Open Settings" })).toBeNull();

    await user.click(screen.getByRole("button", { name: "Generate project folder" }));

    expect(onCreateOfficialWorkspace).toHaveBeenCalledTimes(1);
  });

  it("asks for an explicit conflict strategy before rebuilding an existing project folder", async () => {
    const user = userEvent.setup();
    const onCreateOfficialWorkspace = vi.fn();
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      officialWorkspacePreview: {
        project_id: "project-1",
        dl_number: "DL-2026-06-001",
        status: "exists",
        local_workspace_root: "D:/Projects",
        local_workspace_path: "D:/Projects/DL-2026-06-001",
        source_book_path: "D:/Projects/DL-2026-06-001/Source Book",
        template_path: "D:/Template/DL-XXXX-YY-ZZZ project",
        official_project_folder_path:
          "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
        manifest_path: "D:/Projects/DL-2026-06-001/.connlab/manifest.json",
        template_root_mode: "template_root",
        blockers: ["Official project folder already exists."],
        warnings: [],
        planned_paths: [],
        conflict_paths: [
          "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
        ],
        conflict_options: [
          {
            key: "backup_and_recreate",
            label: "Backup and Rebuild",
            description: "Move the existing folder to a timestamped backup first.",
          },
          {
            key: "overwrite_rebuild",
            label: "Overwrite",
            description: "Replace the existing folder after staging the new template copy.",
          },
        ],
      },
      officialWorkspaceCreating: false,
      onCreateOfficialWorkspace,
    });

    await user.click(screen.getByRole("button", { name: "Generate project folder" }));

    expect(onCreateOfficialWorkspace).not.toHaveBeenCalled();
    expect(screen.getByRole("dialog", { name: "Project folder already exists" })).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Backup and Rebuild" }));

    expect(onCreateOfficialWorkspace).toHaveBeenCalledWith("backup_and_recreate");
  });

  it("disables the permanent project folder action until current Fee authority exists", () => {
    const onCreateOfficialWorkspace = vi.fn();
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      confirmedFeeLatest: confirmedFeeLatest("stale"),
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
      onCreateOfficialWorkspace,
    });

    const folderButton = screen.getByRole("button", { name: "Generate project folder" });
    expect(folderButton).toHaveProperty("disabled", true);
    expect(folderButton.getAttribute("title")).toBe(
      "Update Fee before generating the project folder."
    );
    expect(screen.queryByText("Fee needs update")).toBeNull();
    expect(onCreateOfficialWorkspace).not.toHaveBeenCalled();
  });

  it("keeps the permanent project folder action clickable when workspace preflight is blocked", async () => {
    const user = userEvent.setup();
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

    const folderButton = screen.getByRole("button", { name: "Generate project folder" });
    expect(folderButton).toHaveProperty("disabled", false);
    expect(folderButton.getAttribute("title")).toBeNull();
    expect(
      screen.getAllByText(
        "Project folder generation is unavailable until the template and target path are ready."
      ).length
    ).toBeGreaterThan(0);
    expect(screen.queryByText("Configure workspace paths")).toBeNull();
    expect(screen.queryByText("Project default save location is not configured.")).toBeNull();
    expect(screen.queryAllByRole("button", { name: "Create project folder" })).toHaveLength(0);
    expect(screen.queryByRole("button", { name: "Open Settings" })).toBeNull();

    await user.click(folderButton);

    expect(onCreateOfficialWorkspace).toHaveBeenCalledTimes(1);
  });

  it("asks for an explicit update strategy when completed official workspace already exists", async () => {
    const user = userEvent.setup();
    const onCreateOfficialWorkspace = vi.fn();
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
      onCreateOfficialWorkspace,
    });

    const folderButton = screen.getByRole("button", { name: "Update project folder" });
    expect(folderButton).toHaveProperty("disabled", false);
    expect(folderButton.getAttribute("title")).toBeNull();

    await user.click(folderButton);

    expect(onCreateOfficialWorkspace).not.toHaveBeenCalled();
    expect(screen.getByRole("dialog", { name: "Project folder already exists" })).toBeTruthy();
    expect(
      screen.getByText("D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test")
    ).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Backup and Rebuild" }));

    expect(onCreateOfficialWorkspace).toHaveBeenCalledWith("backup_and_recreate");
    expect(screen.getByLabelText("Folder Action")).toBeTruthy();
  });

  it("asks before updating a recorded project folder while preview is still loading", async () => {
    const user = userEvent.setup();
    const onCreateOfficialWorkspace = vi.fn();
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      folderReady: true,
      officialWorkspacePreview: null,
      packagePreview: readyPackagePreview,
      onCreateOfficialWorkspace,
    });

    await user.click(screen.getByRole("button", { name: "Update project folder" }));

    expect(onCreateOfficialWorkspace).not.toHaveBeenCalled();
    expect(screen.getByRole("dialog", { name: "Project folder already exists" })).toBeTruthy();
    expect(screen.getByText("Existing project folder")).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onCreateOfficialWorkspace).not.toHaveBeenCalled();
    expect(
      screen.queryByRole("dialog", { name: "Project folder already exists" })
    ).toBeNull();
  });

  it("blocks navigation clicks while the project folder workflow is running", () => {
    renderWorkbench({
      latestLtr: "DL-2026-06-001",
      activeConfirmedMatrixSnapshot: confirmedMatrixSnapshot,
      matrixAuthorityDraft: testPlanDraft,
      folderReady: true,
      officialWorkspaceCreating: true,
      officialWorkspaceProgressLabel: "Updating Application Form",
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

    const dialog = screen.getByRole("dialog", {
      name: "Project folder update in progress",
    });
    expect(dialog).toBeTruthy();
    expect(dialog.textContent).toContain("Keep this page open until the operation finishes.");
    expect(dialog.textContent).toContain("Current step");
    expect(dialog.textContent).toContain("Updating Application Form");
    expect(dialog.textContent).toContain("Updating Customer Feedback Form");
    expect(dialog.textContent).toContain("Updating Fee Form");
    expect(screen.getByRole("button", { name: "Generating..." })).toHaveProperty(
      "disabled",
      true
    );
  });
});

function renderWorkbench(
  overrides: Partial<ProjectRuntimeConsoleModel> = {},
  projectOverrides: Partial<Project> = {},
  callbacks: Partial<Pick<
    ProjectWorkbenchLayoutPropsForTest,
    "onBack" | "onOpenMatrixEditor" | "onOpenFeeEvaluation"
    | "onOpenBasicInformation" | "onOpenSettings"
  >> = {}
): ReturnType<typeof render> {
  const currentProject = { ...project, ...projectOverrides };
  return render(
    <ProjectWorkbenchLayout
      runtimeModel={buildRuntimeModel(overrides, currentProject)}
      project={currentProject}
      onBack={callbacks.onBack ?? vi.fn()}
      onOpenMatrixEditor={callbacks.onOpenMatrixEditor ?? vi.fn()}
      onOpenFeeEvaluation={callbacks.onOpenFeeEvaluation ?? vi.fn()}
      onOpenBasicInformation={callbacks.onOpenBasicInformation ?? vi.fn()}
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
    confirmedFeeLatest: {
      status: "current",
      current_confirmed_matrix_id: "CM1",
      current_confirmed_revision: 1,
      current_fee_rule_version_id: "fee-rule-1",
      confirmed_fee: null,
    },
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
    officialWorkspaceProgressLabel: null,
    officialWorkspaceError: null,
    officialWorkspaceResult: null,
    officialFolderCheckPreview: null,
    officialFolderCheckLoading: false,
    officialFolderCheckRepairing: false,
    officialFolderCheckError: null,
    officialFolderRepairResult: null,
    publicDriveUploadPreview: null,
    publicDriveUploadLoading: false,
    publicDriveUploading: false,
    publicDriveUploadError: null,
    publicDriveUploadResult: null,
    requestMaterialPreview: null,
    requestMaterialLoading: false,
    requestMaterialCollecting: false,
    requestMaterialError: null,
    basicInformation: null,
    basicInformationLoading: false,
    basicInformationError: null,
    setRuntimeSelectedTokenReference: vi.fn(),
    onFolderCreated: vi.fn(),
    onRefreshPackagePreview: vi.fn(),
    onRefreshOfficialWorkspacePreview: vi.fn(),
    onCreateOfficialWorkspace: vi.fn(),
    onRefreshOfficialFolderCheck: vi.fn(),
    onRepairOfficialFolderStructure: vi.fn(),
    onRefreshPublicDriveUploadPreview: vi.fn(),
    onRefreshBasicInformation: vi.fn(),
    onUploadPublicDriveProjectFolder: vi.fn(),
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

const confirmedBasicInformation: ProjectBasicInformationResponse = {
  project_id: "P1",
  status: "confirmed",
  draft: {
    values: {
      dl_number: "DL-2026-05-011",
      project_type: "NPD",
      product_description: "Coolpower HDF",
      description_pn: "HDF-34",
      test_item: "Qualification Testing",
      test_type: "Product/Process Qualification",
      test_type_in_sheet: "Qualification",
      requested_by: "MP Cao",
      location: "Dongguan",
      project_leader: "Even Yang",
      lab_performing_tests: "Dongguan",
      test_result: "In progress",
      failed_item: "None",
      sample_deposition: "Send Back",
      sub_contract: "Yes",
      test_fee: "1630.00",
      remarks_po: "PO-123",
    },
  },
  latest_confirmed: {
    record_id: "BASIC-1",
    project_id: "P1",
    status: "confirmed",
    version: 1,
    values: {
      dl_number: "DL-2026-05-011",
      project_type: "NPD",
      product_description: "Coolpower HDF",
      description_pn: "HDF-34",
      test_item: "Qualification Testing",
      test_type: "Product/Process Qualification",
      test_type_in_sheet: "Qualification",
      requested_by: "MP Cao",
      location: "Dongguan",
      project_leader: "Even Yang",
      lab_performing_tests: "Dongguan",
      test_result: "In progress",
      failed_item: "None",
      sample_deposition: "Send Back",
      sub_contract: "Yes",
      test_fee: "1630.00",
      remarks_po: "PO-123",
    },
    source_signature: "{}",
    created_at: "2026-06-20T09:00:00+00:00",
    updated_at: "2026-06-20T09:00:00+00:00",
    confirmed_at: "2026-06-20T09:00:00+00:00",
    confirmed_by: "Lab User",
  },
  field_suggestions: {},
  changed_source_fields: [],
  missing_required_fields: [],
  missing_required_labels: [],
  blockers: [],
  warnings: [],
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

const readyRequiredFormsPreview: ProjectFolderRequiredFormsPreview = {
  project_id: project.project_id,
  status: "ready",
  official_project_folder_path:
    "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
  confirmed_matrix_id: "CM1",
  confirmed_revision: 1,
  confirmed_fee_id: "CF1",
  confirmed_fee_revision: 1,
  confirmed_fee_pricing_draft_edit_id: "fed-current",
  confirmed_basic_information_version: 1,
  confirmed_basic_information_source_signature_hash: "basic-hash",
  customer_feedback_template_path: "D:/Template/Customer Feedback.xlsx",
  items: [
    {
      key: "fee_form",
      label: "Fee Form",
      target_path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/DL-2026-06-001_Fee_Form.xls",
      status: "ready",
      action: "generate",
      message: "Fee Form can be generated.",
    },
  ],
  blockers: [],
  warnings: [],
};

const basicInformationBlockedRequiredFormsPreview: ProjectFolderRequiredFormsPreview = {
  ...readyRequiredFormsPreview,
  status: "blocked",
  official_project_folder_path: null,
  confirmed_matrix_id: null,
  confirmed_revision: null,
  confirmed_fee_id: null,
  confirmed_fee_revision: null,
  confirmed_fee_pricing_draft_edit_id: null,
  confirmed_basic_information_version: null,
  confirmed_basic_information_source_signature_hash: null,
  customer_feedback_template_path: null,
  items: [],
  blockers: ["Confirm Basic Information before generating Project Folder outputs."],
};

function confirmedFeeLatest(
  status: ConfirmedFeeLatestResponse["status"],
  options: { feeReviewRequiredCount?: number } = {}
): ConfirmedFeeLatestResponse {
  return {
    status,
    current_confirmed_matrix_id: "CM1",
    current_confirmed_revision: 1,
    current_fee_rule_version_id: "fee-rule-1",
    fee_review_required_count: options.feeReviewRequiredCount ?? 0,
    confirmed_fee:
      status === "missing"
        ? null
        : {
            confirmed_fee_id: "CF1",
            project_id: project.project_id,
            confirmed_fee_revision: 1,
            confirmed_matrix_id: "CM1",
            confirmed_revision: 1,
            fee_rule_version_id: "fee-rule-1",
            pricing_draft_edit_id:
              status === "current" ? "fed-current" : "fed-old",
            pricing_effective_from: null,
            summary: {
              testing_fee_total: "100.00",
              working_hours: "1.0",
              lab_manpower_cost: "50",
              external_cost: "0",
              grand_cost: "150.00",
            },
            confirmed_by: "Lab User",
            confirmed_at: "2026-06-15T00:00:00+00:00",
            confirmation_note: null,
          },
  };
}

const readyPublicDriveUploadPreview: PublicDriveUploadPreview = {
  project_id: project.project_id,
  status: "ready",
  local_official_folder_path:
    "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
  public_project_folder_path:
    "D:/PublicProjects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
  items: [
    {
      kind: "file",
      relative_path: "Submitted Material/application.docx",
      local_path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Submitted Material/application.docx",
      public_path:
        "D:/PublicProjects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Submitted Material/application.docx",
      action: "add",
      status: "ready",
      message: "Ready to add.",
    },
    {
      kind: "directory",
      relative_path: "Photos",
      local_path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Photos",
      public_path:
        "D:/PublicProjects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Photos",
      action: "skip",
      status: "current",
      message: "Already exists.",
    },
  ],
  blockers: [],
  warnings: [],
  counts: {
    add: 1,
    update: 0,
    skip: 1,
    conflict: 0,
    deferred: 0,
  },
  next_action: "upload",
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
