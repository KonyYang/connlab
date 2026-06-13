import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState, type ReactElement } from "react";
import { describe, expect, it, vi } from "vitest";
import type { PublicDriveUploadPreview, RequestMaterialPreview } from "../../api/client";
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
        publicDriveUploadPreview={publicDrivePreview}
        onTaskAction={onTaskAction}
      />
    );

    await user.click(screen.getByRole("button", { name: "Upload to public drive" }));

    expect(onTaskAction).toHaveBeenCalledWith("public_drive_upload");
  });
});

function ProjectFolderTaskListHarness({
  currentTaskKey,
  requestMaterialPreview,
  publicDriveUploadPreview,
  onTaskAction = vi.fn(),
}: {
  currentTaskKey: ProjectFolderTaskKey;
  requestMaterialPreview: RequestMaterialPreview;
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
