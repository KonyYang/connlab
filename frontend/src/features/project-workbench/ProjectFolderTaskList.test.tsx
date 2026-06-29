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
    render(<ProjectFolderTaskListHarness />);

    expect(screen.getByRole("region", { name: "Folder Actions" })).toBeTruthy();
    expect((screen.getByRole("button", { name: "Open" }) as HTMLButtonElement).disabled).toBe(true);
    expect(
      (screen.getByRole("checkbox", {
        name: "Auto sync public working copy",
      }) as HTMLInputElement).disabled
    ).toBe(true);
    expect((screen.getByRole("button", { name: "Sync now" }) as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByRole("button", { name: "Submit" }) as HTMLButtonElement).disabled).toBe(true);
    expect((screen.getByRole("button", { name: "Pull" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("does not render old readiness task details", () => {
    render(<ProjectFolderTaskListHarness />);

    const surfaceText = screen.getByRole("region", { name: "Folder Actions" }).textContent ?? "";
    expect(surfaceText).not.toMatch(
      /Next step|Project Folder progress|Request material|Source Book|Public drive upload|Ready to upload|Already current|Upload to public drive|Refresh public-drive preview/
    );
  });

  it("does not route disabled placeholder actions", async () => {
    const user = userEvent.setup();
    const onTaskAction = vi.fn();
    render(<ProjectFolderTaskListHarness onTaskAction={onTaskAction} />);

    await user.click(screen.getByRole("button", { name: "Sync now" }));
    await user.click(screen.getByRole("button", { name: "Submit" }));
    await user.click(screen.getByRole("button", { name: "Pull" }));

    expect(onTaskAction).not.toHaveBeenCalled();
  });

  it("applies readonly reasons to the shared surface", () => {
    render(
      <ProjectFolderActionsSurface
        tasks={tasks}
        readonlyReason="Activate project before editing is restored."
      />
    );

    expect(screen.getAllByText("Activate project before editing is restored.").length).toBeGreaterThan(0);
    expect(screen.getByRole("button", { name: "Open" }).getAttribute("title")).toBe(
      "Activate project before editing is restored."
    );
  });
});

function ProjectFolderTaskListHarness({
  onTaskAction = vi.fn(),
}: {
  onTaskAction?: (actionTarget: ProjectFolderTaskActionTarget) => void;
}) {
  return (
    <ProjectFolderTaskList
      tasks={tasks}
      currentTaskKey="project_folder"
      selectedTaskKey="project_folder"
      onSelectTask={vi.fn() as (taskKey: ProjectFolderTaskKey) => void}
      onTaskAction={onTaskAction}
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
    statusLabel: "Open",
    status: "neutral",
    summary: "Folder access.",
    actionLabel: "Open",
    actionTarget: null,
    blockers: ["Project folder open is not connected yet."],
    warnings: [],
  },
  {
    key: "public_working_copy",
    title: "Public working copy",
    statusLabel: "Sync",
    status: "neutral",
    summary: "Keep the lab working copy aligned when the sync workflow is connected.",
    actionLabel: "Sync now",
    actionTarget: null,
    blockers: ["Sync workflow is not connected yet."],
    warnings: [],
  },
  {
    key: "approval_package",
    title: "Approval package",
    statusLabel: "Submit",
    status: "neutral",
    summary: "Submit controlled output after package workflow checks are connected.",
    actionLabel: "Submit",
    actionTarget: null,
    blockers: ["Submit workflow is not connected yet."],
    warnings: [],
  },
  {
    key: "approved_folder",
    title: "Approved folder",
    statusLabel: "Pull",
    status: "neutral",
    summary: "Bring approved public results back after pull workflow wiring exists.",
    actionLabel: "Pull",
    actionTarget: null,
    blockers: ["Pull workflow is not connected yet."],
    warnings: [],
  },
];
