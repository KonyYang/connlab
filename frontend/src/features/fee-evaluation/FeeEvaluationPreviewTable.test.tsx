import { cleanup, fireEvent, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { FeeEvaluationPreviewTable } from "./FeeEvaluationPreviewTable";
import type { FeeEvaluationPreviewRow } from "./feeEvaluationPreviewModel";

describe("FeeEvaluationPreviewTable", () => {
  it("keeps prices independently editable without repeated bulk-price actions", () => {
    const onRowEditChange = vi.fn();
    const source = {
      lineId: "line-a", groupKey: "Aa", groupLabel: "Aa", rowKind: "matrix_step",
      description: "IR", stepToken: "1",
      unitPrice: "5", unitType: "per reading", units: "", baseFee: "",
      discount: "0", spendTime: "0", testingFee: "Pending", notes: "",
      status: "pending", reviewReason: null, fieldMetadata: [], groupTone: "tone-a",
    } as FeeEvaluationPreviewRow;
    render(<FeeEvaluationPreviewTable
      costPreviewValues={{ conditionConfirmationSpendTime: "0", externalCost: "0", externalCostNote: "", labManpowerHourlyRate: "200" }}
      costRisk={{ severity: "none", message: null }} confirmFeeActionState={{ kind: "idle" }}
      downloadState={{ kind: "idle" }} feeFormButtonLabel="Download Draft Fee Form"
      draftPreviewNotice={null} groupFilter="all" groupOptions={["Aa", "Ab"]}
      identityLine="DL-2026-001" labManpowerCostLabel="0"
      onCostPreviewChange={vi.fn()} onGenerateFeeFile={vi.fn()} onGroupFilterChange={vi.fn()}
      onRowEditChange={onRowEditChange}
      rows={[source, { ...source, lineId: "line-b", groupKey: "Ab", groupLabel: "Ab" }]}
      saveState={{ kind: "idle", message: null }} scopeFeeLabel="Pending"
      totals={{ testFeeTotal: "0", workingHours: "0", grandCost: "0", labManpowerCost: "0", externalCost: "0", preparedBy: "", approvedBy: "", confirmationLabel: "" }}
    />);

    expect(screen.queryAllByRole("button", { name: /Apply price to/ })).toHaveLength(0);
    const prices = screen.getAllByLabelText("Unit Price for IR");
    expect(prices).toHaveLength(2);
    fireEvent.change(prices[0], { target: { value: "25" } });
    expect(onRowEditChange).toHaveBeenCalledWith("line-a", "unitPrice", "25");
  });

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
        feeFormButtonLabel="Download Draft Fee Form"
        draftPreviewNotice={null}
        groupFilter="all"
        groupOptions={[]}
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

    const totals = screen.getByLabelText("Testing Prices totals");
    expect(within(totals).getByLabelText("Preview group")).toBeTruthy();
    expect(within(totals).getByLabelText("Selected group fee")).toBeTruthy();
    expect(within(totals).queryByText("Grand Cost")).toBeNull();
  });
});
