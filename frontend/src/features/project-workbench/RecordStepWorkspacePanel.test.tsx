import { describe, expect, it } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { RecordStepWorkspacePanel } from "./RecordStepWorkspacePanel";
import type { MatrixProjectionTokenCell } from "./projectWorkbenchMatrixProjectionSelectors";

const selectedToken: MatrixProjectionTokenCell = {
  tokenReference: "Visual::6.1::EIA-364-18B::10x::No damage:g1:1:1",
  groupKey: "g1",
  groupLabel: "Group 1",
  rawToken: "1",
  sequence: 1,
  statusTone: "not_started",
  sampleQuantityExpression: "3",
  testItem: "Visual",
  section: "6.1",
  method: "EIA-364-18B",
  condition: "10x",
  requirement: "No damage",
};

describe("RecordStepWorkspacePanel", () => {
  it("shows an empty state before a matrix token is selected", () => {
    render(
      <RecordStepWorkspacePanel selectedToken={null} statusLabel="Not selected" />
    );

    const panel = screen.getByLabelText("Record Step Workspace");
    expect(within(panel).getByText("Record Step Workspace")).toBeTruthy();
    expect(
      within(panel).getByText("Select a matrix token to review record context.")
    ).toBeTruthy();
  });

  it("renders selected token context needed for Test Record preparation", () => {
    render(
      <RecordStepWorkspacePanel
        selectedToken={selectedToken}
        statusLabel="Not started"
      />
    );

    const panel = screen.getByLabelText("Record Step Workspace");
    for (const expectedText of [
      "Group 1",
      "1",
      "Not started",
      "3",
      "Visual",
      "6.1",
      "EIA-364-18B",
      "10x",
      "No damage",
    ]) {
      expect(within(panel).getByText(expectedText)).toBeTruthy();
    }
  });

  it("shows inactive record, evidence, and review placeholders", () => {
    render(
      <RecordStepWorkspacePanel
        selectedToken={selectedToken}
        statusLabel="Not started"
      />
    );

    const panel = screen.getByLabelText("Record Step Workspace");
    expect(within(panel).getByText("Record draft")).toBeTruthy();
    expect(within(panel).getByText("Evidence / data")).toBeTruthy();
    expect(within(panel).getByText("Review")).toBeTruthy();
    expect(within(panel).getAllByText("Placeholder")).toHaveLength(3);
    expect(within(panel).queryByRole("button")).toBeNull();
  });
});
