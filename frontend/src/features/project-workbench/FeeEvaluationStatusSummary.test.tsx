import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, render, screen } from "@testing-library/react";
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
      />
    );

    expect(await screen.findByText("Missing")).toBeTruthy();
    expect(screen.getByText("Confirm Matrix authority before fee review.")).toBeTruthy();
  });

  it("shows needs-review draft readiness from the fee draft", async () => {
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft("needs_review", 2));

    render(
      <FeeEvaluationStatusSummary
        projectId="P1"
        outputStatus={feeOutputStatus("missing", "No output path is available yet.")}
      />
    );

    expect(await screen.findByText("Needs review")).toBeTruthy();
    expect(screen.getByText("2 line(s) require operator review.")).toBeTruthy();
  });

  it("shows ready when the draft is deterministic and output status is current", async () => {
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft("ready", 0));

    render(
      <FeeEvaluationStatusSummary
        projectId="P1"
        outputStatus={feeOutputStatus(
          "current",
          "Output reference is aligned with the current authority context."
        )}
      />
    );

    expect(await screen.findByText("Draft ready")).toBeTruthy();
    expect(
      screen.getByText("All fee lines are calculated from the active rule version.")
    ).toBeTruthy();
  });

  it("uses Workbench output freshness for stale status", async () => {
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft("ready", 0));

    render(
      <FeeEvaluationStatusSummary
        projectId="P1"
        outputStatus={feeOutputStatus(
          "stale",
          "Output reference was captured before the current authority version."
        )}
      />
    );

    expect(await screen.findByText("Stale")).toBeTruthy();
    expect(
      screen.getByText("Output reference was captured before the current authority version.")
    ).toBeTruthy();
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
