import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState, type ReactElement } from "react";
import { describe, expect, it, vi } from "vitest";
import type {
  ProjectFolderRequiredFormsPreview,
  PublicDriveUploadPreview,
  RequestMaterialPreview,
} from "../../api/client";
import { ProjectFolderTaskList } from "./ProjectFolderTaskList";
import type {
  ProjectFolderTaskActionTarget,
  ProjectFolderTaskKey,
  ProjectFolderTaskRow,
} from "./projectFolderTaskSelectors";

describe("ProjectFolderTaskList", () => {
  it("defaults to the current task and lets users inspect another task", async () => {
    const user = userEvent.setup();
    render(
      <ProjectFolderTaskListHarness
        currentTaskKey="request_material"
        requestMaterialPreview={requestMaterialPreview}
        requiredFormsPreview={requiredFormsPreview}
        publicDriveUploadPreview={publicDrivePreview}
      />
    );

    expect(screen.getByLabelText("Selected Project Folder task").textContent).toContain(
      "Request material"
    );
    expect(screen.getByText("Files checked")).toBeTruthy();
    expect(screen.queryByText("Public folder")).toBeNull();

    await user.click(screen.getByRole("button", { name: /Public drive upload/ }));

    expect(screen.getByLabelText("Selected Project Folder task").textContent).toContain(
      "Public drive upload"
    );
    expect(screen.getByText("Public folder")).toBeTruthy();
    expect(screen.getByText("Submitted Material/application.docx")).toBeTruthy();
    expect(screen.queryByText("Files checked")).toBeNull();
  });

  it("routes selected task actions through the task action target", async () => {
    const user = userEvent.setup();
    const onTaskAction = vi.fn();
    render(
      <ProjectFolderTaskListHarness
        currentTaskKey="public_drive_upload"
        requestMaterialPreview={requestMaterialPreview}
        requiredFormsPreview={requiredFormsPreview}
        publicDriveUploadPreview={publicDrivePreview}
        onTaskAction={onTaskAction}
      />
    );

    await user.click(screen.getByRole("button", { name: "Upload to public drive" }));

    expect(onTaskAction).toHaveBeenCalledWith("public_drive_upload");
  });

  it("shows Required forms preview details and routes generation action", async () => {
    const user = userEvent.setup();
    const onTaskAction = vi.fn();
    render(
      <ProjectFolderTaskListHarness
        currentTaskKey="required_forms"
        requestMaterialPreview={requestMaterialPreview}
        requiredFormsPreview={requiredFormsPreview}
        publicDriveUploadPreview={publicDrivePreview}
        onTaskAction={onTaskAction}
      />
    );

    expect(screen.getByLabelText("Selected Project Folder task").textContent).toContain(
      "Required forms"
    );
    expect(screen.getByText("Forms ready to generate")).toBeTruthy();
    expect(screen.getByText("Test Record")).toBeTruthy();
    expect(screen.getByText("Submitted Material/DL-2026-06-001_Test_Record.docx")).toBeTruthy();
    expect(screen.getByText("Customer Feedback Form")).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Generate required forms" }));

    expect(onTaskAction).toHaveBeenCalledWith("required_forms_generate");
  });
});

function ProjectFolderTaskListHarness({
  currentTaskKey,
  requestMaterialPreview,
  requiredFormsPreview,
  publicDriveUploadPreview,
  onTaskAction = vi.fn(),
}: {
  currentTaskKey: ProjectFolderTaskKey;
  requestMaterialPreview: RequestMaterialPreview;
  requiredFormsPreview: ProjectFolderRequiredFormsPreview;
  publicDriveUploadPreview: PublicDriveUploadPreview;
  onTaskAction?: (actionTarget: ProjectFolderTaskActionTarget) => void;
}): ReactElement {
  const [selectedTaskKey, setSelectedTaskKey] = useState<ProjectFolderTaskKey>(
    currentTaskKey
  );
  return (
    <ProjectFolderTaskList
      tasks={tasks}
      currentTaskKey={currentTaskKey}
      selectedTaskKey={selectedTaskKey}
      onSelectTask={setSelectedTaskKey}
      onTaskAction={onTaskAction}
      requestMaterialPreview={requestMaterialPreview}
      requestMaterialError={null}
      requestMaterialLoading={false}
      requiredFormsPreview={requiredFormsPreview}
      requiredFormsError={null}
      requiredFormsLoading={false}
      publicDriveUploadPreview={publicDriveUploadPreview}
      publicDriveUploadError={null}
      publicDriveUploadLoading={false}
    />
  );
}

const tasks: ProjectFolderTaskRow[] = [
  {
    key: "request_material",
    title: "Request material",
    statusLabel: "Collected",
    status: "ready",
    summary: "Original request files and controlled copies are recorded.",
    actionTarget: null,
    detailKind: "request_material",
    blockers: [],
    warnings: [],
  },
  {
    key: "required_forms",
    title: "Required forms",
    statusLabel: "Ready to generate",
    status: "warning",
    summary: "Test Record, Fee Form, Customer Feedback Form need controlled generation.",
    actionLabel: "Generate required forms",
    actionTarget: "required_forms_generate",
    detailKind: "required_forms",
    blockers: [],
    warnings: [],
  },
  {
    key: "section2",
    title: "Application Form Section 2",
    statusLabel: "Not updated",
    status: "neutral",
    summary: "Section 2 write-back status is not checked yet.",
    actionTarget: null,
    detailKind: "section2",
    blockers: [],
    warnings: [],
  },
  {
    key: "public_drive_upload",
    title: "Public drive upload",
    statusLabel: "Ready to upload",
    status: "warning",
    summary: "Review public-drive target changes before uploading.",
    actionLabel: "Upload to public drive",
    actionTarget: "public_drive_upload",
    detailKind: "public_drive",
    blockers: [],
    warnings: [],
  },
];

const requestMaterialPreview: RequestMaterialPreview = {
  project_id: "project-1",
  local_workspace_path: "D:/Projects/DL-2026-06-001",
  source_book_path: "D:/Projects/DL-2026-06-001/Source Book",
  official_project_folder_path:
    "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
  status: "collected",
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
      action: "none",
      status: "copied",
      message: "Copied.",
      review_required: false,
      size_bytes: 100,
      sha256: "a".repeat(64),
    },
  ],
  blockers: [],
  warnings: [],
};

const requiredFormsPreview: ProjectFolderRequiredFormsPreview = {
  project_id: "project-1",
  status: "ready",
  official_project_folder_path:
    "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test",
  confirmed_matrix_id: "matrix-1",
  confirmed_revision: 1,
  confirmed_fee_id: "fee-1",
  confirmed_fee_revision: 1,
  confirmed_fee_pricing_draft_edit_id: "pricing-1",
  customer_feedback_template_path: "D:/Source/Template/Customer Feedback.xlsx",
  items: [
    {
      key: "test_record",
      label: "Test Record",
      target_path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/Submitted Material/DL-2026-06-001_Test_Record.docx",
      status: "ready",
      action: "generate",
      message: "Test Record can be generated.",
    },
    {
      key: "fee_form",
      label: "Fee Form",
      target_path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/DL-2026-06-001_Fee_Form.xls",
      status: "ready",
      action: "generate",
      message: "Fee Form can be generated.",
    },
    {
      key: "customer_feedback_form",
      label: "Customer Feedback Form",
      target_path:
        "D:/Projects/DL-2026-06-001/DL-2026-06-001 Connector Qualification test/DL-2026-06-001_Customer_Feedback_Form.xlsx",
      status: "ready",
      action: "generate",
      message: "Customer Feedback Form can be generated.",
    },
  ],
  blockers: [],
  warnings: [],
};

const publicDrivePreview: PublicDriveUploadPreview = {
  project_id: "project-1",
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
  ],
  blockers: [],
  warnings: [],
  counts: {
    add: 1,
    update: 0,
    skip: 0,
    conflict: 0,
    deferred: 0,
  },
  next_action: "upload",
};
