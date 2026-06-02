import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MatrixSchedulePlanningCard } from "./MatrixSchedulePlanningCard";
import type { MatrixScheduleCalculation, MatrixSchedulePlan } from "./matrixSchedulePlanning";

const emptyPlan: MatrixSchedulePlan = {
  postTestBufferDays: "",
  sampleReceivedDate: "2026-06-01",
  plannedTestStartDate: "2026-06-02",
  plannedTestCompleteDate: "2026-06-03",
  estimatedCompletionDate: "2026-06-04",
};

const blankDatePlan: MatrixSchedulePlan = {
  postTestBufferDays: "1",
  sampleReceivedDate: "",
  plannedTestStartDate: "",
  plannedTestCompleteDate: "",
  estimatedCompletionDate: "",
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

    expect(screen.getByText("Longest Test Group 8a: 2.5 d")).toBeTruthy();
    expect(screen.getByLabelText("Test complete").classList.contains("is-invalid")).toBe(true);
    expect(screen.getByLabelText("Test complete").getAttribute("aria-invalid")).toBe("true");
    expect(screen.getByLabelText("Planned start").classList.contains("is-invalid")).toBe(false);
  });

  it("shows date values in native date input format", () => {
    render(
      <MatrixSchedulePlanningCard
        plan={{
          postTestBufferDays: "",
          sampleReceivedDate: "2026-06-01",
          plannedTestStartDate: "2026-06-02",
          plannedTestCompleteDate: "2026-06-03",
          estimatedCompletionDate: "2026-06-04",
        }}
        groups={[{ id: "g1", name: "1", isSelected: true }]}
        calculation={buildCalculation()}
        onChange={vi.fn()}
      />
    );

    expect(screen.getByLabelText("Sample received").getAttribute("value")).toBe("2026-06-01");
    expect(screen.getByLabelText("Planned start").getAttribute("value")).toBe("2026-06-02");
    expect(screen.getByLabelText("Test complete").getAttribute("value")).toBe("2026-06-03");
    expect(screen.getByLabelText("Estimated completion").getAttribute("value")).toBe("2026-06-04");
  });

  it("marks empty planned date fields for attention", () => {
    render(
      <MatrixSchedulePlanningCard
        plan={blankDatePlan}
        groups={[{ id: "g8", name: "8a", isSelected: true }]}
        calculation={{ ...buildCalculation(), invalidDateFields: {}, dateError: null, isValid: true }}
        onChange={vi.fn()}
      />
    );

    expect(screen.getByLabelText("Sample received").classList.contains("is-invalid")).toBe(true);
    expect(screen.getByLabelText("Planned start").classList.contains("is-invalid")).toBe(true);
    expect(screen.getByLabelText("Test complete").classList.contains("is-invalid")).toBe(true);
    expect(screen.getByLabelText("Estimated completion").classList.contains("is-invalid")).toBe(true);
  });

  it("preselects complete and estimated dates from planned start", () => {
    const onChange = vi.fn();
    render(
      <MatrixSchedulePlanningCard
        plan={blankDatePlan}
        groups={[{ id: "g8", name: "8a", isSelected: true }]}
        calculation={{ ...buildCalculation(), invalidDateFields: {}, dateError: null, isValid: true }}
        onChange={onChange}
      />
    );

    fireEvent.change(screen.getByLabelText("Planned start"), {
      target: { value: "2026-06-03" },
    });

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({
        plannedTestStartDate: "2026-06-03",
        plannedTestCompleteDate: "2026-06-06",
        estimatedCompletionDate: "2026-06-07",
      })
    );
  });

  it("updates estimated completion when post-test buffer changes", () => {
    const onChange = vi.fn();
    render(
      <MatrixSchedulePlanningCard
        plan={{
          ...blankDatePlan,
          plannedTestStartDate: "2026-06-03",
          plannedTestCompleteDate: "2026-06-06",
          estimatedCompletionDate: "2026-06-07",
        }}
        groups={[{ id: "g8", name: "8a", isSelected: true }]}
        calculation={{ ...buildCalculation(), invalidDateFields: {}, dateError: null, isValid: true }}
        onChange={onChange}
      />
    );

    fireEvent.change(screen.getByLabelText("Post-test buffer"), {
      target: { value: "2" },
    });

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({
        plannedTestCompleteDate: "2026-06-06",
        estimatedCompletionDate: "2026-06-08",
      })
    );
  });

  it("updates estimated completion when test complete changes", () => {
    const onChange = vi.fn();
    render(
      <MatrixSchedulePlanningCard
        plan={{
          ...blankDatePlan,
          postTestBufferDays: "2",
          plannedTestStartDate: "2026-06-03",
          plannedTestCompleteDate: "",
          estimatedCompletionDate: "",
        }}
        groups={[{ id: "g8", name: "8a", isSelected: true }]}
        calculation={{ ...buildCalculation(), invalidDateFields: {}, dateError: null, isValid: true }}
        onChange={onChange}
      />
    );

    fireEvent.change(screen.getByLabelText("Test complete"), {
      target: { value: "2026-06-06" },
    });

    expect(onChange).toHaveBeenCalledWith(
      expect.objectContaining({
        plannedTestCompleteDate: "2026-06-06",
        estimatedCompletionDate: "2026-06-08",
      })
    );
  });
});
