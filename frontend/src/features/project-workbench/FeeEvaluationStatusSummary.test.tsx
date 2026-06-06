import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { ApiRequestError } from "../../api/client";
import { FeeEvaluationStatusSummary } from "./FeeEvaluationStatusSummary";
import type { WorkbenchDocumentStatus } from "./projectWorkbenchVersionSelectors";

const apiMocks = vi.hoisted(() => ({
  fetchConfirmedMatrixFeeDraft: vi.fn(),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return {
    ...actual,
    fetchConfirmedMatrixFeeDraft: apiMocks.fetchConfirmedMatrixFeeDraft,
  };
});

describe("FeeEvaluationStatusSummary", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("shows missing when no active confirmed Matrix authority exists", async () => {
    apiMocks.fetchConfirmedMatrixFeeDraft.mockRejectedValue(
      new ApiRequestError("Active confirmed matrix not found.", 404, null)
    );

    render(
      <FeeEvaluationStatusSummary
        projectId="P1"
        outputStatus={feeOutputStatus("missing", "No output path is available yet.")}
        canOpen={false}
        onOpenFeeEvaluation={vi.fn()}
      />
    );

    expect(await screen.findByText("Total fee: Pending Matrix confirmation.")).toBeTruthy();
    expect(screen.getByText("Total fee: Pending Matrix confirmation.")).toBeTruthy();
    expect(
      (screen.getByRole("button", { name: "Open Fee Evaluation" }) as HTMLButtonElement)
        .disabled
    ).toBe(true);
  });

  it("shows needs-review draft readiness from the fee draft", async () => {
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft("needs_review", 2));
    const onOpen = vi.fn();

    render(
      <FeeEvaluationStatusSummary
        projectId="P1"
        outputStatus={feeOutputStatus("missing", "No output path is available yet.")}
        canOpen={true}
        onOpenFeeEvaluation={onOpen}
      />
    );

    expect(await screen.findByText("Total fee: Pending Excel confirmation.")).toBeTruthy();
    expect(screen.getByText("Total fee: Pending Excel confirmation.")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Open Fee Evaluation" }));
    expect(onOpen).toHaveBeenCalledTimes(1);
  });

  it("shows confirmed and total when the draft is deterministic", async () => {
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft("ready", 0));

    render(
      <FeeEvaluationStatusSummary
        projectId="P1"
        outputStatus={feeOutputStatus(
          "current",
          "Output reference is aligned with the current authority context."
        )}
        canOpen={true}
        onOpenFeeEvaluation={vi.fn()}
      />
    );

    expect(await screen.findByText("Total fee: 100.00")).toBeTruthy();
    expect(screen.queryByText(/Output:/)).toBeNull();
  });

  it("keeps Workbench summary focused on total fee instead of output record details", async () => {
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft("ready", 0));

    render(
      <FeeEvaluationStatusSummary
        projectId="P1"
        outputStatus={feeOutputStatus(
          "stale",
          "Output reference was captured before the current authority version."
        )}
        canOpen={true}
        onOpenFeeEvaluation={vi.fn()}
      />
    );

    expect(await screen.findByText("Total fee: 100.00")).toBeTruthy();
    expect(screen.queryByText(/Output:/)).toBeNull();
  });

  it("enables the page action when the fee draft is available", async () => {
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft("needs_review", 2));
    const onOpen = vi.fn();

    render(
      <FeeEvaluationStatusSummary
        projectId="P1"
        outputStatus={feeOutputStatus("missing", "No output path is available yet.")}
        canOpen={false}
        onOpenFeeEvaluation={onOpen}
      />
    );

    expect(await screen.findByText("Total fee: Pending Excel confirmation.")).toBeTruthy();
    const button = screen.getByRole("button", { name: "Open Fee Evaluation" });
    expect((button as HTMLButtonElement).disabled).toBe(false);
    fireEvent.click(button);
    expect(onOpen).toHaveBeenCalledTimes(1);
  });
});

function feeOutputStatus(
  freshness: WorkbenchDocumentStatus["freshness"],
  reason: string
): WorkbenchDocumentStatus {
  return {
    key: "fee_evaluation",
    label: "Fee evaluation",
    freshness,
    path: freshness === "missing" ? null : "D:\\Output\\fee.xlsx",
    reason,
  };
}

function createDraft(draftStatus: "ready" | "empty" | "needs_review", reviewCount: number) {
  return {
    header: {
      project_id: "P1",
      confirmed_matrix_id: "cmv-1",
      confirmed_revision: 1,
      pricing_rule_version_id: "fee_rules_v2026_06_03",
      pricing_source_file_name: "Testing Fee Evaluation-Even.xls",
      pricing_source_hash: "sha256:abc",
      pricing_effective_from: "2026-06-03",
      generated_at: "2026-06-04T10:00:00+08:00",
    },
    draft_status: draftStatus,
    total_fee: draftStatus === "ready" ? "100.00" : null,
    review_required_count: reviewCount,
    groups: [],
    warnings: [],
  };
}
