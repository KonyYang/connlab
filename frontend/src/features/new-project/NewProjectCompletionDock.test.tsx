import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { NewProjectCompletionDock } from "./NewProjectCompletionDock";
import type { NewProjectSetupConfirmationValues } from "./NewProjectSetupConfirmationPanel";

describe("NewProjectCompletionDock Apply LTR busy state", () => {
  it("shows an actionable required-information reason while Apply LTR is blocked", () => {
    render(
      <NewProjectCompletionDock
        completionDisabled={true}
        completionLoading={false}
        completionText="3 required fields remaining"
        disabled={false}
        missingKeys={new Set()}
        values={values}
        onChange={vi.fn()}
        onComplete={vi.fn()}
        onCreateTemporaryProject={vi.fn()}
      />
    );

    const reason = screen.getByRole("status");
    expect(reason.textContent).toContain("3 required fields remaining");
    expect(reason.textContent).toContain("Complete the highlighted fields above");
    expect(
      screen.getByRole("button", { name: /Apply LTR Number/ })
    ).toHaveProperty("disabled", true);
  });

  it("does not show a blocker reason when Apply LTR is ready", () => {
    render(
      <NewProjectCompletionDock
        completionDisabled={false}
        completionLoading={false}
        completionText="Required project information complete"
        disabled={false}
        missingKeys={new Set()}
        values={values}
        onChange={vi.fn()}
        onComplete={vi.fn()}
        onCreateTemporaryProject={vi.fn()}
      />
    );

    expect(screen.queryByRole("status")).toBeNull();
  });

  it("shows completion errors inside the dock action area", () => {
    render(
      <NewProjectCompletionDock
        completionDisabled={false}
        completionError="Intake case not found: case-1"
        completionLoading={false}
        completionText="Required project information complete"
        disabled={false}
        missingKeys={new Set()}
        values={values}
        onChange={vi.fn()}
        onComplete={vi.fn()}
        onCreateTemporaryProject={vi.fn()}
      />
    );

    const alert = screen.getByRole("alert");
    expect(alert.textContent).toContain("Intake case not found: case-1");
    expect(alert.closest(".new-project-completion-dock")).toBeTruthy();
  });

  it("shows compact busy status and prevents Apply/temporary actions while loading", async () => {
    const user = userEvent.setup();
    const onComplete = vi.fn();
    const onCreateTemporaryProject = vi.fn();
    render(
      <NewProjectCompletionDock
        completionDisabled={true}
        completionLoading={true}
        completionText="Required project information complete"
        disabled={true}
        missingKeys={new Set()}
        values={values}
        onChange={vi.fn()}
        onComplete={onComplete}
        onCreateTemporaryProject={onCreateTemporaryProject}
      />
    );

    const status = screen.getByRole("status");
    expect(status.textContent).toContain("Applying LTR number");
    expect(status.textContent).toContain(
      "ConnLab may open and update the LTR workbook. Keep this page open."
    );

    const applyButton = screen.getByRole("button", { name: /Applying LTR number/ });
    const temporaryButton = screen.getByRole("button", { name: "Create Temporary Project" });
    expect((applyButton as HTMLButtonElement).disabled).toBe(true);
    expect((temporaryButton as HTMLButtonElement).disabled).toBe(true);

    await user.click(applyButton);
    await user.click(temporaryButton);

    expect(onComplete).not.toHaveBeenCalled();
    expect(onCreateTemporaryProject).not.toHaveBeenCalled();
  });
});

const values: NewProjectSetupConfirmationValues = {
  ltrMode: "auto",
  specifiedLtrNumber: "",
  testItem: "Qualification",
  sampleDescription: "Connector",
  testTypeInSheet: "Qualification",
  projectLeader: "Lab User",
  labPerformingTests: "Dongguan",
};
