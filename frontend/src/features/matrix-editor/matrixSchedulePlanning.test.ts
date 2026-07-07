import { describe, expect, it } from "vitest";
import {
  calculateMatrixSchedule,
  emptySchedulePlan,
} from "./matrixSchedulePlanning";

describe("matrixSchedulePlanning", () => {
  it("calculates selected group test days with decimal multipliers", () => {
    const result = calculateMatrixSchedule(
      [
        {
          id: "r1",
          isSampleRow: false,
          dayExpression: "0.5x",
          groups: { g1: "1,2", g2: "3" },
        },
        {
          id: "r2",
          isSampleRow: false,
          dayExpression: "1",
          groups: { g1: "4", g2: "" },
        },
      ],
      [
        { id: "g1", name: "1", isSelected: true },
        { id: "g2", name: "2", isSelected: false },
      ],
      emptySchedulePlan()
    );

    expect(result.groupDays.g1).toBe(2);
    expect(result.groupDays.g2).toBeUndefined();
    expect(result.criticalGroupDays).toBe(2);
    expect(result.isValid).toBe(true);
  });

  it("counts ideographic comma and PDF comma mojibake tokens for multiplier days", () => {
    const result = calculateMatrixSchedule(
      [
        {
          id: "r1",
          isSampleRow: false,
          dayExpression: "0.5x",
          groups: { g1: "1、8 2Ўў3" },
        },
      ],
      [{ id: "g1", name: "1", isSelected: true }],
      emptySchedulePlan()
    );

    expect(result.groupDays.g1).toBe(2);
    expect(result.criticalGroupDays).toBe(2);
    expect(result.isValid).toBe(true);
  });

  it("ignores invalid day expressions on rows without selected group tokens", () => {
    const result = calculateMatrixSchedule(
      [
        {
          id: "r1",
          isSampleRow: false,
          dayExpression: "bad",
          groups: { g1: "", g2: "1" },
        },
      ],
      [
        { id: "g1", name: "1", isSelected: true },
        { id: "g2", name: "2", isSelected: false },
      ],
      emptySchedulePlan()
    );

    expect(result.rowErrors).toEqual({});
    expect(result.isValid).toBe(true);
  });

  it("validates calendar date anchors using rounded-up critical group days", () => {
    const result = calculateMatrixSchedule(
      [
        {
          id: "r1",
          isSampleRow: false,
          dayExpression: "2.5",
          groups: { g1: "1" },
        },
      ],
      [{ id: "g1", name: "1", isSelected: true }],
      {
        postTestBufferDays: "1",
        sampleReceivedDate: "2026-06-01",
        plannedTestStartDate: "2026-06-02",
        plannedTestCompleteDate: "2026-06-04",
        estimatedCompletionDate: "2026-06-05",
      }
    );

    expect(result.dateError).toContain("Test complete is earlier");
    expect(result.invalidDateFields).toEqual({ plannedTestCompleteDate: true });
    expect(result.isValid).toBe(false);
  });

  it("rejects impossible date strings without browser normalization", () => {
    const result = calculateMatrixSchedule(
      [],
      [{ id: "g1", name: "1", isSelected: true }],
      {
        postTestBufferDays: "",
        sampleReceivedDate: "2026-02-31",
        plannedTestStartDate: "2026-03-01",
        plannedTestCompleteDate: "2026-03-01",
        estimatedCompletionDate: "2026-03-01",
      }
    );

    expect(result.dateError).toContain("YYYY-MM-DD");
    expect(result.invalidDateFields).toEqual({ sampleReceivedDate: true });
  });

  it("requires planned start to be on or after sample received", () => {
    const result = calculateMatrixSchedule(
      [
        {
          id: "r1",
          isSampleRow: false,
          dayExpression: "1",
          groups: { g1: "1" },
        },
      ],
      [{ id: "g1", name: "1", isSelected: true }],
      {
        postTestBufferDays: "",
        sampleReceivedDate: "2026-06-05",
        plannedTestStartDate: "2026-06-04",
        plannedTestCompleteDate: "2026-06-06",
        estimatedCompletionDate: "2026-06-07",
      }
    );

    expect(result.dateError).toContain("Planned start is earlier than sample received date.");
    expect(result.invalidDateFields).toEqual({ plannedTestStartDate: true });
    expect(result.isValid).toBe(false);
  });

  it("requires estimated completion to include post-test buffer", () => {
    const result = calculateMatrixSchedule(
      [
        {
          id: "r1",
          isSampleRow: false,
          dayExpression: "1",
          groups: { g1: "1" },
        },
      ],
      [{ id: "g1", name: "1", isSelected: true }],
      {
        postTestBufferDays: "2",
        sampleReceivedDate: "2026-06-01",
        plannedTestStartDate: "2026-06-01",
        plannedTestCompleteDate: "2026-06-02",
        estimatedCompletionDate: "2026-06-02",
      }
    );

    expect(result.dateError).toContain(
      "Estimated completion is earlier than test complete plus post-test buffer."
    );
    expect(result.invalidDateFields).toEqual({ estimatedCompletionDate: true });
    expect(result.isValid).toBe(false);
  });
});
