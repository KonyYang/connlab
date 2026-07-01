import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ProjectFolderActionsSurface, ProjectFolderTaskList } from "./ProjectFolderTaskList";
import type {
  ProjectFolderTaskActionTarget,
  ProjectFolderTaskKey,
  ProjectFolderTaskRow,
} from "./projectFolderTaskSelectors";

describe("ProjectFolderTaskList", () => {
  it("renders the quiet four-operation Folder Actions surface", () => {
    const { container } = render(<ProjectFolderTaskListHarness />);

    expect(screen.getByRole("region", { name: "Folder Actions" })).toBeTruthy();
    expect(container.querySelector(".runtime-console-folder-operation-list")).toBeTruthy();
    expect(container.querySelectorAll(".runtime-console-folder-operation")).toHaveLength(4);
    expect(
      Array.from(container.querySelectorAll(".runtime-console-folder-operation h3")).map(
        (item) => item.textContent
      )
    ).toEqual(["Project folder", "Public working copy", "Approval package", "Approved folder"]);
    expect(
      screen.getByText("Closed output can be pulled without overwriting local history.")
    ).toBeTruthy();
    expect((screen.getByRole("button", { name: "Open" }) as HTMLButtonElement).disabled).toBe(false);
    expect(
      (screen.getByRole("checkbox", {
        name: "Auto sync public working copy",
      }) as HTMLInputElement).disabled
    ).toBe(false);
    expect((screen.getByRole("button", { name: "Sync now" }) as HTMLButtonElement).disabled).toBe(false);
    expect((screen.getByRole("button", { name: "Submit" }) as HTMLButtonElement).disabled).toBe(false);
    expect((screen.getByRole("button", { name: "Pull" }) as HTMLButtonElement).disabled).toBe(false);
  });

  it("does not render old readiness task details", () => {
    render(<ProjectFolderTaskListHarness />);

    const surfaceText = screen.getByRole("region", { name: "Folder Actions" }).textContent ?? "";
    expect(surfaceText).not.toMatch(
      /Next step|Project Folder progress|Request material|Source Book|Public drive upload|Ready to upload|Already current|Upload to public drive|Refresh public-drive preview/
    );
  });

  it("routes Open, preview-first actions, and Auto sync changes", async () => {
    const user = userEvent.setup();
    const onTaskAction = vi.fn();
    const onAutoSyncChange = vi.fn();
    render(
      <ProjectFolderTaskListHarness
        onTaskAction={onTaskAction}
        onAutoSyncChange={onAutoSyncChange}
      />
    );

    await user.click(screen.getByRole("button", { name: "Open" }));
    await user.click(screen.getByRole("button", { name: "Sync now" }));
    await user.click(screen.getByRole("button", { name: "Submit" }));
    await user.click(screen.getByRole("button", { name: "Pull" }));
    await user.click(
      screen.getByRole("checkbox", { name: "Auto sync public working copy" })
    );

    expect(onTaskAction).toHaveBeenCalledWith("project_folder_open");
    expect(onTaskAction).toHaveBeenCalledWith("public_folder_workflow_sync");
    expect(onTaskAction).toHaveBeenCalledWith("public_folder_workflow_submit");
    expect(onTaskAction).toHaveBeenCalledWith("public_folder_workflow_pull");
    expect(onAutoSyncChange).toHaveBeenCalledWith(false);
  });

  it("routes Project folder Open from keyboard Enter and Space activation", async () => {
    const user = userEvent.setup();
    const onTaskAction = vi.fn();
    render(<ProjectFolderTaskListHarness onTaskAction={onTaskAction} />);

    const openButton = screen.getByRole("button", { name: "Open" });

    openButton.focus();
    expect(document.activeElement).toBe(openButton);
    await user.keyboard("{Enter}");

    expect(onTaskAction).toHaveBeenCalledTimes(1);
    expect(onTaskAction).toHaveBeenLastCalledWith("project_folder_open");

    await user.keyboard(" ");

    expect(onTaskAction).toHaveBeenCalledTimes(2);
    expect(onTaskAction).toHaveBeenLastCalledWith("project_folder_open");
  });

  it("renders operation confirmation controls", async () => {
    const user = userEvent.setup();
    const onTaskConfirm = vi.fn();
    const onTaskCancel = vi.fn();
    render(
      <ProjectFolderActionsSurface
        tasks={[
          {
            ...tasks[2],
            confirming: true,
            operation: "submit",
            confirmLabel: "Confirm submit",
            cancelLabel: "Cancel",
          },
        ]}
        onTaskConfirm={onTaskConfirm}
        onTaskCancel={onTaskCancel}
      />
    );

    await user.click(screen.getByRole("button", { name: "Confirm submit" }));
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(onTaskConfirm).toHaveBeenCalledWith("submit");
    expect(onTaskCancel).toHaveBeenCalledWith("submit");
  });

  it("applies readonly reasons to the shared surface", () => {
    render(
      <ProjectFolderActionsSurface
        tasks={tasks}
        readonlyReason="Activate project before editing is restored."
      />
    );

    expect(screen.getAllByText("Activate project before editing is restored.")).toHaveLength(1);
    expect(screen.getByRole("button", { name: "Open" }).getAttribute("title")).toBeNull();
    expect((screen.getByRole("button", { name: "Open" }) as HTMLButtonElement).disabled).toBe(
      false
    );
    expect(screen.getByRole("button", { name: "Sync now" }).getAttribute("title")).toBe(
      "Activate project before editing is restored."
    );
  });
});

function ProjectFolderTaskListHarness({
  onTaskAction = vi.fn(),
  onAutoSyncChange = vi.fn(),
}: {
  onTaskAction?: (actionTarget: ProjectFolderTaskActionTarget) => void;
  onAutoSyncChange?: (enabled: boolean) => void;
}) {
  return (
    <ProjectFolderTaskList
      tasks={tasks}
      currentTaskKey="project_folder"
      selectedTaskKey="project_folder"
      onSelectTask={vi.fn() as (taskKey: ProjectFolderTaskKey) => void}
      onTaskAction={onTaskAction}
      onAutoSyncChange={onAutoSyncChange}
      requestMaterialPreview={null}
      requestMaterialError={null}
      requestMaterialLoading={false}
      requiredFormsPreview={null}
      requiredFormsError={null}
      requiredFormsLoading={false}
      publicDriveUploadPreview={null}
      publicDriveUploadError={null}
      publicDriveUploadLoading={false}
    />
  );
}

const tasks: ProjectFolderTaskRow[] = [
  {
    key: "project_folder",
    title: "Project folder",
    iconName: "folder",
    statusLabel: "Open",
    status: "neutral",
    summary: "Folder access.",
    context: "Open is not connected yet.",
    actionLabel: "Open",
    actionTarget: "project_folder_open",
    blockers: [],
    warnings: [],
  },
  {
    key: "public_working_copy",
    title: "Public working copy",
    iconName: "cloud-sync",
    statusLabel: "Sync",
    status: "neutral",
    summary: "Keep the lab working copy aligned.",
    context: "Public Open working copy.",
    actionLabel: "Sync now",
    actionTarget: "public_folder_workflow_sync",
    blockers: [],
    warnings: [],
    operation: "sync",
    autoSync: {
      checked: true,
      disabled: false,
      busy: false,
    },
  },
  {
    key: "approval_package",
    title: "Approval package",
    iconName: "folder-move",
    statusLabel: "Submit",
    status: "neutral",
    summary: "Submit controlled output.",
    context: "Preview moves Open output to Closed after confirmation.",
    actionLabel: "Submit",
    actionTarget: "public_folder_workflow_submit",
    blockers: [],
    warnings: [],
    operation: "submit",
  },
  {
    key: "approved_folder",
    title: "Approved folder",
    iconName: "download",
    statusLabel: "Pull",
    status: "neutral",
    summary: "Bring approved public results back.",
    context: "Closed output can be pulled without overwriting local history.",
    actionLabel: "Pull",
    actionTarget: "public_folder_workflow_pull",
    blockers: [],
    warnings: [],
    operation: "pull",
  },
];
