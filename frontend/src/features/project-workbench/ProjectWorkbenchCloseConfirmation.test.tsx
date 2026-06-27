import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { ProjectOutputStatusSummary } from "../../api/client";
import { ProjectWorkbenchCloseConfirmation } from "./ProjectWorkbenchCloseConfirmation";
import type { WorkbenchLifecycleActionsViewModel } from "./projectWorkbenchLifecycleSelectors";

describe("ProjectWorkbenchCloseConfirmation", () => {
  it("requires close note and acknowledgements before completed close", async () => {
    const user = userEvent.setup();
    const onCloseCompletedProject = vi.fn();

    render(
      <ProjectWorkbenchCloseConfirmation
        lifecycleActions={registeredCloseActions}
        lifecycleBusy={false}
        onCloseAdministrativeProject={vi.fn()}
        onCloseCompletedProject={onCloseCompletedProject}
        outputStatusSummary={outputStatusSummary}
        projectIdentity="DL-2026-06-001 Connector Sample"
        projectReference="DL-2026-06-001"
      />
    );

    await user.click(screen.getByRole("button", { name: "Close as completed" }));

    expect(screen.getByText("Output status summary")).toBeTruthy();
    expect(screen.getByText("Test Record")).toBeTruthy();
    expect(screen.getByText("Current")).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Confirm completed close" }));
    expect(screen.getByText("Close note is required.")).toBeTruthy();
    expect(onCloseCompletedProject).not.toHaveBeenCalled();

    await user.type(screen.getByLabelText("Close note"), "Outputs reviewed.");
    await user.click(
      screen.getByLabelText(
        "I manually confirm this project is ready to archive as completed."
      )
    );
    await user.click(
      screen.getByLabelText("I reviewed the available output status summary.")
    );
    await user.click(screen.getByRole("button", { name: "Confirm completed close" }));

    expect(onCloseCompletedProject).toHaveBeenCalledWith("Outputs reviewed.");
  });

  it("defaults temporary/no-DL close UX to administrative close only", async () => {
    const user = userEvent.setup();
    const onCloseAdministrativeProject = vi.fn();

    render(
      <ProjectWorkbenchCloseConfirmation
        lifecycleActions={temporaryCloseActions}
        lifecycleBusy={false}
        onCloseAdministrativeProject={onCloseAdministrativeProject}
        onCloseCompletedProject={vi.fn()}
        outputStatusSummary={null}
        projectIdentity="Temporary project project-1"
        projectReference={null}
      />
    );

    expect(screen.queryByRole("button", { name: "Close as completed" })).toBeNull();
    await user.click(screen.getByRole("button", { name: "Close administratively" }));
    expect(screen.getByText(/archives the project without marking testing complete/)).toBeTruthy();

    await user.click(
      screen.getByRole("button", { name: "Confirm administrative close" })
    );
    expect(screen.getByText("Administrative close reason is required.")).toBeTruthy();
    expect(onCloseAdministrativeProject).not.toHaveBeenCalled();

    await user.type(screen.getByLabelText("Administrative reason"), "Duplicate request.");
    await user.click(
      screen.getByRole("button", { name: "Confirm administrative close" })
    );

    expect(onCloseAdministrativeProject).toHaveBeenCalledWith("Duplicate request.");
  });
});

const registeredCloseActions: WorkbenchLifecycleActionsViewModel = {
  primaryAction: "stop",
  canStop: true,
  canResume: false,
  canClose: true,
  canCloseCompleted: true,
  canCloseAdministrative: true,
  preferredClosePath: "completed",
  completedCloseLabel: "Close as completed",
  administrativeCloseLabel: "Close administratively",
  readonlyReason: null,
};

const temporaryCloseActions: WorkbenchLifecycleActionsViewModel = {
  ...registeredCloseActions,
  canCloseCompleted: false,
  preferredClosePath: "administrative",
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
