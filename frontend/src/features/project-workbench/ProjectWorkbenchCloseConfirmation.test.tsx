import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { ProjectOutputStatusSummary } from "../../api/client";
import { ProjectWorkbenchCloseConfirmation } from "./ProjectWorkbenchCloseConfirmation";
import type { WorkbenchLifecycleActionsViewModel } from "./projectWorkbenchLifecycleSelectors";

describe("ProjectWorkbenchCloseConfirmation", () => {
  it("uses one business close form with required note", async () => {
    const user = userEvent.setup();
    const onCloseProject = vi.fn();

    render(
      <ProjectWorkbenchCloseConfirmation
        lifecycleActions={registeredCloseActions}
        lifecycleBusy={false}
        onCloseProject={onCloseProject}
        outputStatusSummary={outputStatusSummary}
        projectIdentity="DL-2026-06-001 Connector Sample"
        projectReference="DL-2026-06-001"
      />
    );

    await user.click(screen.getByRole("button", { name: "Close project" }));

    expect(screen.getByText("Output status summary")).toBeTruthy();
    expect(screen.getByText("Test Record")).toBeTruthy();
    expect(screen.getByText("Current")).toBeTruthy();
    expect(screen.getByLabelText("Close reason")).toBeTruthy();
    expect(screen.getByRole("option", { name: "Completed" })).toBeTruthy();
    expect(screen.getByRole("option", { name: "Failed" })).toBeTruthy();
    expect(screen.getByRole("option", { name: "Cannot test" })).toBeTruthy();

    expect(
      (screen.getByRole("button", { name: "Confirm close project" }) as HTMLButtonElement)
        .disabled
    ).toBe(true);
    expect(onCloseProject).not.toHaveBeenCalled();

    await user.selectOptions(screen.getByLabelText("Close reason"), "failed");
    await user.type(screen.getByLabelText("Close note"), "Testing cannot continue.");
    await user.click(screen.getByRole("button", { name: "Confirm close project" }));

    expect(onCloseProject).toHaveBeenCalledWith("failed", "Testing cannot continue.");
  });

  it("defaults temporary close to Other without split close copy", async () => {
    const user = userEvent.setup();
    const onCloseProject = vi.fn();

    render(
      <ProjectWorkbenchCloseConfirmation
        lifecycleActions={temporaryCloseActions}
        lifecycleBusy={false}
        onCloseProject={onCloseProject}
        outputStatusSummary={null}
        projectIdentity="Temporary project project-1"
        projectReference={null}
      />
    );

    expect(screen.queryByText("Close as completed")).toBeNull();
    expect(screen.queryByText("Close administratively")).toBeNull();

    await user.click(screen.getByRole("button", { name: "Close project" }));
    expect((screen.getByLabelText("Close reason") as HTMLSelectElement).value).toBe("other");
    expect(screen.queryByText("Administrative reason")).toBeNull();

    await user.type(screen.getByLabelText("Close note"), "Duplicate request.");
    await user.click(screen.getByRole("button", { name: "Confirm close project" }));

    expect(onCloseProject).toHaveBeenCalledWith("other", "Duplicate request.");
  });
});

const registeredCloseActions: WorkbenchLifecycleActionsViewModel = {
  primaryAction: "close",
  canStop: false,
  canResume: false,
  canClose: true,
  canActivate: false,
  closeActionLabel: "Close project",
  activateActionLabel: "Activate project",
  defaultCloseReasonCategory: "completed",
  closeReasonLabel: null,
  readonlyReason: null,
};

const temporaryCloseActions: WorkbenchLifecycleActionsViewModel = {
  ...registeredCloseActions,
  defaultCloseReasonCategory: "other",
};

const outputStatusSummary: ProjectOutputStatusSummary = {
  project_id: "project-1",
  active_draft_id: "draft-1",
  active_draft_version: 3,
  items: [
    {
      output_kind: "test_record_form",
      status: "current",
      output_path: "D:/Projects/DL-2026-06-001/Test Record.docx",
      source: "system_generated",
      draft_id: "draft-1",
      draft_version: 3,
      reason: "Generated from active Matrix.",
      updated_at: "2026-06-27T08:00:00Z",
    },
    {
      output_kind: "approval_package",
      status: "missing",
      output_path: null,
      source: null,
      draft_id: null,
      draft_version: null,
      reason: "Approval package has not been placed.",
      updated_at: null,
    },
  ],
};
