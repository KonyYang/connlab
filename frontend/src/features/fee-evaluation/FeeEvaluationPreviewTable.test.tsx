import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { FeeEvaluationPreviewTable } from "./FeeEvaluationPreviewTable";

describe("FeeEvaluationPreviewTable", () => {
  afterEach(() => {
    cleanup();
  });

  it("renders stale pricing draft guidance as a non-error status notice", () => {
    render(
      <FeeEvaluationPreviewTable
        costPreviewValues={{
          conditionConfirmationSpendTime: "0",
          externalCost: "0",
          externalCostNote: "",
          labManpowerHourlyRate: "200",
        }}
        costRisk={{ severity: "none", message: null }}
        confirmFeeActionState={{ kind: "idle" }}
        downloadState={{ kind: "idle" }}
        generateDisabledReason={null}
        grandCostLabel="0.00"
        groupFilter="all"
        groupOptions={[]}
        header={{
          ltrNumber: "DL-2026-001",
          requestor: "MP Cao",
          site: "Pending",
          testDescription: "Pending",
        }}
        identityLine="DL-2026-001"
        labManpowerCostLabel="0"
        onCostPreviewChange={vi.fn()}
        onGenerateFeeFile={vi.fn()}
        onGroupFilterChange={vi.fn()}
        onRowEditChange={vi.fn()}
        rows={[]}
        saveState={{
          kind: "stale",
          message:
            "Automatic Fee defaults changed. Review the refreshed values, then update Fee.",
        }}
        scopeFeeLabel="0.00"
        totals={{
          testFeeTotal: "0",
          workingHours: "0",
          grandCost: "0",
          labManpowerCost: "0",
          externalCost: "0",
          preparedBy: "Pending",
          approvedBy: "Pending",
          confirmationLabel: "Pending",
        }}
      />
    );

    const notice = screen.getByRole("status");
    expect(notice.textContent).toContain("Automatic Fee defaults changed");
    expect(notice.className).toContain("fee-evaluation-save-notice");
    expect(screen.queryByRole("alert")).toBeNull();
  });
});
