import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { NewProjectCompletionDock } from "./NewProjectCompletionDock";
import type { NewProjectSetupConfirmationValues } from "./NewProjectSetupConfirmationPanel";

describe("NewProjectCompletionDock Apply LTR busy state", () => {
  it("lists each missing field and moves keyboard focus to the chosen field", async () => {
    const user = userEvent.setup();
    const onComplete = vi.fn();
    render(
      <>
        <input id="business" aria-label="Business Unit" />
        <input id="quantity" aria-label="Quantity in sample 2" />
        <NewProjectCompletionDock
          completionDisabled={true}
          completionLoading={false}
          requiredActions={[
            { targetId: "business", label: "Select Business Unit" },
            { targetId: "quantity", label: "Sample 2 · Enter Quantity" }
          ]}
          disabled={false}
          missingKeys={new Set()}
          values={values}
          onChange={vi.fn()}
          onComplete={onComplete}
          onSaveMaterials={vi.fn()}
        />
      </>
    );

    const reason = screen.getByRole("status");
    expect(reason.textContent).toContain("2 fields");
    await user.click(screen.getByRole("button", { name: "Select Business Unit" }));
    expect(document.activeElement).toBe(screen.getByLabelText("Business Unit"));
    screen.getByRole("button", { name: "Sample 2 · Enter Quantity" }).focus();
    await user.keyboard("{Enter}");
    expect(document.activeElement).toBe(screen.getByLabelText("Quantity in sample 2"));
    expect(onComplete).not.toHaveBeenCalled();
    expect(
      screen.getByRole("button", { name: /Apply LTR Number/ })
    ).toHaveProperty("disabled", true);
  });

  it("does not show a blocker reason when Apply LTR is ready", () => {
    render(
      <NewProjectCompletionDock
        completionDisabled={false}
        completionLoading={false}
        requiredActions={[]}
        disabled={false}
        missingKeys={new Set()}
        values={values}
        onChange={vi.fn()}
        onComplete={vi.fn()}
        onSaveMaterials={vi.fn()}
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
        requiredActions={[]}
        disabled={false}
        missingKeys={new Set()}
        values={values}
        onChange={vi.fn()}
        onComplete={vi.fn()}
        onSaveMaterials={vi.fn()}
      />
    );

    const alert = screen.getByRole("alert");
    expect(alert.textContent).toContain("Intake case not found: case-1");
    expect(alert.closest(".new-project-completion-dock")).toBeTruthy();
  });

  it("shows compact busy status and prevents Apply/materials actions while loading", async () => {
    const user = userEvent.setup();
    const onComplete = vi.fn();
    const onSaveMaterials = vi.fn();
    render(
      <NewProjectCompletionDock
        completionDisabled={true}
        completionLoading={true}
        requiredActions={[{ targetId: "business", label: "Select Business Unit" }]}
        disabled={true}
        missingKeys={new Set()}
        values={values}
        onChange={vi.fn()}
        onComplete={onComplete}
        onSaveMaterials={onSaveMaterials}
      />
    );

    const status = screen.getByRole("status");
    expect(screen.queryByRole("button", { name: "Select Business Unit" })).toBeNull();
    expect(status.textContent).toContain("Applying LTR number");
    expect(status.textContent).toContain(
      "ConnLab may open and update the LTR workbook. Keep this page open."
    );

    const applyButton = screen.getByRole("button", { name: /Applying LTR number/ });
    const temporaryButton = screen.getByRole("button", { name: "Save materials" });
    expect((applyButton as HTMLButtonElement).disabled).toBe(true);
    expect((temporaryButton as HTMLButtonElement).disabled).toBe(true);

    await user.click(applyButton);
    await user.click(temporaryButton);

    expect(onComplete).not.toHaveBeenCalled();
    expect(onSaveMaterials).not.toHaveBeenCalled();
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
