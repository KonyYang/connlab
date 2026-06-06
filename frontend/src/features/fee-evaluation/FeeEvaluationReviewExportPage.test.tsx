import { afterEach, describe, expect, it, vi } from "vitest";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { ApiRequestError, type FeeEvaluationLineItem } from "../../api/client";
import { FeeEvaluationReviewExportPage } from "./FeeEvaluationReviewExportPage";

const apiMocks = vi.hoisted(() => ({
  exportConfirmedMatrixFeeEvaluation: vi.fn(),
  fetchConfirmedMatrixFeeDraft: vi.fn(),
  getLatestProjectFolder: vi.fn(),
  getProject: vi.fn(),
  getProjectOutputStatusSummary: vi.fn(),
  listProjectLtrs: vi.fn(),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return {
    ...actual,
    exportConfirmedMatrixFeeEvaluation: apiMocks.exportConfirmedMatrixFeeEvaluation,
    fetchConfirmedMatrixFeeDraft: apiMocks.fetchConfirmedMatrixFeeDraft,
    getLatestProjectFolder: apiMocks.getLatestProjectFolder,
    getProject: apiMocks.getProject,
    getProjectOutputStatusSummary: apiMocks.getProjectOutputStatusSummary,
    listProjectLtrs: apiMocks.listProjectLtrs,
  };
});

describe("FeeEvaluationReviewExportPage", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders Testing Prices preview before secondary review details", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    expect(await screen.findByText("DL-2026-001 | CoolPower HDF")).toBeTruthy();
    expect(screen.getByText("Testing Prices preview")).toBeTruthy();
    expect(screen.getByText("Review details")).toBeTruthy();
    expect(screen.getByText("Total fee")).toBeTruthy();
    expect(screen.getAllByText("Pending Excel confirmation").length).toBeGreaterThan(0);

    const tables = screen.getAllByRole("table");
    expect(tables[0].getAttribute("aria-label")).toBe("Testing Prices preview rows");
    expect(tables[1].getAttribute("aria-label")).toBe("Fee Evaluation review rows");

    const previewTable = screen.getByRole("table", {
      name: "Testing Prices preview rows",
    });
    const headerBand = screen.getByLabelText("Testing Prices header");
    expect(within(headerBand).getByText("LTR Number")).toBeTruthy();
    expect(within(headerBand).getByText("DL-2026-001")).toBeTruthy();
    expect(within(headerBand).getByText("Requestor")).toBeTruthy();
    expect(within(headerBand).getByText("Lab User")).toBeTruthy();
    expect(within(headerBand).getByText("Test description")).toBeTruthy();
    expect(within(headerBand).getAllByText("Pending").length).toBeGreaterThan(0);
    for (const column of [
      "Group",
      "Spend Time",
      "Description",
      "Unit Price",
      "Unit Type",
      "Units",
      "Base Fee",
      "Discount",
      "Testing Fee",
    ]) {
      expect(within(previewTable).getByRole("columnheader", { name: column })).toBeTruthy();
    }
    expect(within(previewTable).getAllByText("Pending").length).toBeGreaterThan(0);
    expect(within(previewTable).getAllByText("Visual Examination").length).toBeGreaterThan(0);

    const reviewTable = screen.getByRole("table", { name: "Fee Evaluation review rows" });
    expect(within(reviewTable).getAllByText("Fixture setup").length).toBeGreaterThan(0);
    expect(within(reviewTable).getAllByText("Visual Examination").length).toBeGreaterThan(0);
    expect(within(reviewTable).getByText("Unknown specialized test")).toBeTruthy();
    expect(screen.queryByLabelText("Units")).toBeNull();
    expect(screen.queryByLabelText("Base fee")).toBeNull();
    expect(screen.queryByLabelText("Discount")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Review required" }));
    expect(within(reviewTable).queryByText("Fixture setup")).toBeNull();
    expect(within(reviewTable).getAllByText("Visual Examination").length).toBeGreaterThan(0);
    expect(within(reviewTable).getByText("Unknown specialized test")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "No rule match" }));
    expect(within(reviewTable).queryByText("Visual Examination")).toBeNull();
    expect(within(reviewTable).getByText("Unknown specialized test")).toBeTruthy();
  });

  it("disables export when the project folder path is missing", async () => {
    arrangeSuccessfulContext({ folderPath: null });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    const exportButton = await screen.findByRole("button", {
      name: "Generate Excel file",
    });
    expect((exportButton as HTMLButtonElement).disabled).toBe(true);
    expect(
      screen.getByText("Create the project folder before generating the workbook.")
    ).toBeTruthy();
  });

  it("exports Matrix basic fill and shows the generated path", async () => {
    arrangeSuccessfulContext();
    apiMocks.getProjectOutputStatusSummary
      .mockResolvedValueOnce(outputStatusSummary("stale"))
      .mockResolvedValueOnce(outputStatusSummary("current"));
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());
    apiMocks.exportConfirmedMatrixFeeEvaluation.mockResolvedValue(createExportResult());

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    const approvedBy = await screen.findByLabelText("Approved by");
    fireEvent.change(approvedBy, { target: { value: "Lab Manager" } });
    fireEvent.change(screen.getByLabelText("File name"), {
      target: { value: "fee draft" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Generate Excel file" }));

    await waitFor(() => {
      expect(apiMocks.exportConfirmedMatrixFeeEvaluation).toHaveBeenCalledWith("P1", {
        template_path: "D:/Source/Template/Testing Fee Evaluation-Even.optimized-v1.xls",
        output_dir: "D:\\Projects\\DL-2026-001",
        output_file_name: "fee draft.xls",
        overwrite: false,
        allow_review_required: true,
        fill_mode: "matrix_basic",
        approved_by: "Lab Manager",
      });
    });
    expect(await screen.findByText("D:\\Projects\\DL-2026-001\\Fee.xls")).toBeTruthy();
    await waitFor(() => {
      expect(screen.getByText("Current")).toBeTruthy();
    });
  });

  it("shows timeout cleanup guidance from structured API detail", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());
    apiMocks.exportConfirmedMatrixFeeEvaluation.mockRejectedValue(
      new ApiRequestError("Fee Evaluation export timed out after 90 seconds.", 503, {
        message: "Fee Evaluation export timed out after 90 seconds.",
        elapsed_seconds: 90,
        manual_cleanup_warning: "Close the Excel instance opened by ConnLab if it remains.",
      })
    );

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    fireEvent.click(
      await screen.findByRole("button", { name: "Generate Excel file" })
    );

    expect(
      await screen.findByText("Fee Evaluation export timed out after 90 seconds.")
    ).toBeTruthy();
    expect(
      screen.getByText("Close the Excel instance opened by ConnLab if it remains.")
    ).toBeTruthy();
  });
});

function arrangeSuccessfulContext(input: { folderPath?: string | null } = {}): void {
  apiMocks.getProject.mockResolvedValue({
    project_id: "P1",
    project_no: "CP-001",
    product_name: "CoolPower HDF",
    requestor: "Lab User",
    status: "folder_created",
  });
  apiMocks.listProjectLtrs.mockResolvedValue([{ ltr_number: "DL-2026-001" }]);
  if (input.folderPath === null) {
    apiMocks.getLatestProjectFolder.mockRejectedValue(new Error("No folder"));
  } else {
    apiMocks.getLatestProjectFolder.mockResolvedValue({
      folder_id: "folder-1",
      project_id: "P1",
      project_folder_path: input.folderPath ?? "D:\\Projects\\DL-2026-001",
    });
  }
  apiMocks.getProjectOutputStatusSummary.mockResolvedValue(outputStatusSummary("stale"));
}

function outputStatusSummary(status: "current" | "stale") {
  return {
    project_id: "P1",
    active_draft_id: "draft-1",
    active_draft_version: 2,
    items: [
      {
        output_kind: "fee_evaluation",
        status,
        output_path: "D:\\Projects\\old.xls",
        source: "system_generated",
        draft_id: "draft-1",
        draft_version: status === "current" ? 2 : 1,
        reason:
          status === "current"
            ? "Output reference is aligned with the current authority context."
            : "Output reference was captured before the current authority version.",
        updated_at: "2026-06-05T09:00:00+08:00",
      },
    ],
  };
}

function createDraft() {
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
    draft_status: "needs_review",
    total_fee: null,
    review_required_count: 2,
    warnings: [],
    groups: [
      {
        group_key: "g1",
        group_label: "Group 1",
        sample_quantity_expression: "5",
        line_items: [
          createLine({
            line_id: "fixture",
            status: "calculated",
            review_required: false,
            test_item: "Fixture setup",
            matched_rule_name: "Fixture setup",
            matched_rule_id: "fee_rule_fixture",
            calculation_strategy: "fixed_per_group",
            unit_label: "group",
            unit_price: "100.00",
            testing_fee: "100.00",
          }),
          createLine({
            line_id: "visual",
            status: "review_required",
            review_required: true,
            review_reason: "Photo count is not available from Matrix authority.",
            test_item: "Visual Examination",
            matched_rule_name: "Visual Examination",
            matched_rule_id: "fee_rule_visual_exam",
            calculation_strategy: "per_photo",
            unit_label: "photo",
            unit_price: "10.00",
            testing_fee: null,
          }),
          createLine({
            line_id: "unknown",
            status: "no_rule_match",
            review_required: true,
            review_reason: "No deterministic fee rule matched this Matrix row.",
            test_item: "Unknown specialized test",
            matched_rule_name: null,
            matched_rule_id: null,
            calculation_strategy: null,
            unit_label: "manual",
            unit_price: null,
            testing_fee: null,
          }),
        ],
      },
    ],
  };
}

function createLine(overrides: Partial<FeeEvaluationLineItem>): FeeEvaluationLineItem {
  return {
    ...baseLine(),
    ...overrides,
  };
}

function baseLine(): FeeEvaluationLineItem {
  return {
    line_id: "line",
    status: "calculated" as const,
    review_required: false,
    review_reason: null,
    confirmed_matrix_id: "cmv-1",
    confirmed_revision: 1,
    group_key: "g1",
    group_label: "Group 1",
    confirmed_group_id: "cmg-1",
    sample_quantity_expression: "5",
    confirmed_row_id: "row-1",
    source_row_id: "source-row-1",
    row_order: 1,
    test_item: "Fixture setup",
    section: "6.1",
    method: "Fixture",
    condition: "",
    requirement: "",
    step_tokens: ["1"],
    matched_rule_id: "fee_rule_fixture",
    matched_rule_version_id: "fee_rules_v2026_06_03",
    matched_rule_name: "Fixture setup",
    match_reason: "exact",
    calculation_strategy: "fixed_per_group",
    unit_label: "group",
    unit_price: "100.00",
    units: "1",
    base_fee: "0.00",
    discount_percent: "0",
    testing_fee: "100.00",
    warnings: [],
  };
}

function createExportResult() {
  return {
    project_id: "P1",
    output_path: "D:\\Projects\\DL-2026-001\\Fee.xls",
    output_format: "xls",
    status: "generated",
    confirmed_matrix_id: "cmv-1",
    confirmed_revision: 1,
    pricing_rule_version_id: "fee_rules_v2026_06_03",
    pricing_effective_from: "2026-06-03",
    prepared_by: "Lab User",
    approved_by: "Lab Manager",
    output_record_id: "output-1",
    line_traceability: [],
    warnings: ["Review-required lines were exported for manual pricing."],
  };
}
