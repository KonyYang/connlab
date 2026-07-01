import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { NewProjectCompletionDock } from "./NewProjectCompletionDock";
import type { NewProjectSetupConfirmationValues } from "./NewProjectSetupConfirmationPanel";

describe("NewProjectCompletionDock Apply LTR busy state", () => {
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
