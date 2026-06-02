import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MatrixSchedulePlanningCard } from "./MatrixSchedulePlanningCard";
import type { MatrixScheduleCalculation, MatrixSchedulePlan } from "./matrixSchedulePlanning";

const emptyPlan: MatrixSchedulePlan = {
  preTestBufferDays: "",
  postTestBufferDays: "",
  sampleReceivedDate: "2026-06-01",
  plannedTestStartDate: "2026-06-02",
  plannedTestCompleteDate: "2026-06-03",
  estimatedCompletionDate: "2026-06-04",
};

function buildCalculation(): MatrixScheduleCalculation {
  return {
    groupDays: { g1: 1, g8: 2.5 },
    criticalGroupId: "g8",
    criticalGroupDays: 2.5,
    totalCycleDays: 2.5,
    rowErrors: {},
    bufferErrors: {},
    invalidDateFields: { plannedTestCompleteDate: true },
    dateError: "Test complete is earlier than planned start plus critical group days.",
    isValid: false,
  };
}

describe("MatrixSchedulePlanningCard", () => {
  it("shows the critical group name and marks invalid date fields", () => {
    render(
      <MatrixSchedulePlanningCard
        plan={emptyPlan}
        groups={[
          { id: "g1", name: "1", isSelected: true },
          { id: "g8", name: "8a", isSelected: true },
        ]}
        calculation={buildCalculation()}
        onChange={vi.fn()}
      />
    );

    expect(screen.getByText("Critical: 8a | 2.5 d")).toBeTruthy();
    expect(screen.getByLabelText("Test complete").classList.contains("is-invalid")).toBe(true);
    expect(screen.getByLabelText("Test complete").getAttribute("aria-invalid")).toBe("true");
    expect(screen.getByLabelText("Planned start").classList.contains("is-invalid")).toBe(false);
  });
});
