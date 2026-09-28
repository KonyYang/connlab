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
  it("keeps only the editable schedule fields and marks invalid dates", () => {
    render(
      <MatrixSchedulePlanningCard
        plan={emptyPlan}
        calculation={buildCalculation()}
        onChange={vi.fn()}
      />
    );

    expect(screen.getByText("Schedule")).toBeTruthy();
    expect(screen.queryByText(/Longest Test Group/)).toBeNull();
    expect(screen.getByLabelText("Test complete").classList.contains("is-invalid")).toBe(true);
    expect(screen.getByLabelText("Test complete").getAttribute("aria-invalid")).toBe("true");
    expect(screen.getByLabelText("Planned start").classList.contains("is-invalid")).toBe(false);
  });

  it("shortens the visible post-test label while preserving its accessible field name", () => {
    render(
      <MatrixSchedulePlanningCard
        plan={emptyPlan}
        calculation={buildCalculation()}
        onChange={vi.fn()}
      />
    );

    expect(screen.getByText("Post-test", { exact: true })).toBeTruthy();
    expect(screen.queryByText("Post-test buffer", { exact: true })).toBeNull();
    expect(screen.queryByText("days", { exact: true })).toBeNull();
    expect(screen.getByLabelText("Post-test buffer")).toBeTruthy();
  });

  it("places Post-test immediately before Estimated completion", () => {
    const { container } = render(
      <MatrixSchedulePlanningCard
        plan={emptyPlan}
        calculation={buildCalculation()}
        onChange={vi.fn()}
      />
    );

    const fieldOrder = Array.from(container.querySelectorAll("input"))
      .map((input) => input.getAttribute("aria-label"));

    expect(fieldOrder).toEqual([
      "Planned start",
      "Test complete",
      "Post-test buffer",
      "Estimated completion",
    ]);
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
        calculation={buildCalculation()}
        onChange={vi.fn()}
      />
    );

    expect(screen.queryByLabelText("Sample received")).toBeNull();
    expect(screen.queryByText(/Sample received:/)).toBeNull();
    expect(screen.getByLabelText("Planned start").getAttribute("value")).toBe("2026-06-02");
    expect(screen.getByLabelText("Test complete").getAttribute("value")).toBe("2026-06-03");
    expect(screen.getByLabelText("Estimated completion").getAttribute("value")).toBe("2026-06-04");
  });

  it("marks empty planned date fields for attention", () => {
    render(
      <MatrixSchedulePlanningCard
        plan={blankDatePlan}
        calculation={{ ...buildCalculation(), invalidDateFields: {}, dateError: null, isValid: true }}
        onChange={vi.fn()}
      />
    );

    expect(screen.getByLabelText("Planned start").classList.contains("is-invalid")).toBe(true);
    expect(screen.getByLabelText("Test complete").classList.contains("is-invalid")).toBe(true);
    expect(screen.getByLabelText("Estimated completion").classList.contains("is-invalid")).toBe(true);
  });

  it("keeps schedule editing in the card without a separate confirmation action", () => {
    render(
      <MatrixSchedulePlanningCard
        plan={emptyPlan}
        calculation={{ ...buildCalculation(), invalidDateFields: {}, dateError: null, isValid: true }}
        onChange={vi.fn()}
      />
    );

    expect(screen.getByLabelText("Planned start")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Confirm schedule" })).toBeNull();
  });

  it("preselects complete and estimated dates from planned start", () => {
    const onChange = vi.fn();
    render(
      <MatrixSchedulePlanningCard
        plan={blankDatePlan}
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
