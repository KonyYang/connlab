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
  fetchConfirmedMatrixFeeDraft: vi.fn(),
  generateConfirmedMatrixFeeFileDownload: vi.fn(),
  getProject: vi.fn(),
  listProjectLtrs: vi.fn(),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return {
    ...actual,
    fetchConfirmedMatrixFeeDraft: apiMocks.fetchConfirmedMatrixFeeDraft,
    generateConfirmedMatrixFeeFileDownload:
      apiMocks.generateConfirmedMatrixFeeFileDownload,
    getProject: apiMocks.getProject,
    listProjectLtrs: apiMocks.listProjectLtrs,
  };
});

describe("FeeEvaluationReviewExportPage", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("renders Fee File preview before secondary review details", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());
    const onBackToWorkbench = vi.fn();

    const { container } = render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />
    );

    expect(await screen.findByText("Fee Evaluation")).toBeTruthy();
    expect(screen.queryByText(/Matrix line\(s\)/)).toBeNull();
    expect(container.querySelector(".fee-evaluation-topbar")).toBeNull();
    expect(screen.queryByLabelText("Fee summary")).toBeNull();
    expect(screen.queryByLabelText("Matrix basic fill export")).toBeNull();
    expect(screen.queryByText("Excel output")).toBeNull();
    expect(screen.queryByText("Output directory")).toBeNull();
    expect(screen.queryByText("Selected total")).toBeNull();
    expect(screen.queryByText("Output freshness")).toBeNull();
    expect(screen.queryByText("Rule version")).toBeNull();
    expect(screen.getByText("Review details")).toBeTruthy();
    expect(screen.getByText("Test Fee Total")).toBeTruthy();
    expect(screen.getAllByText("Pending Excel confirmation").length).toBeGreaterThan(0);

    const tables = screen.getAllByRole("table");
    expect(tables[0].getAttribute("aria-label")).toBe("Testing Prices preview rows");
    expect(tables[1].getAttribute("aria-label")).toBe("Fee Evaluation review rows");

    const previewTable = screen.getByRole("table", {
      name: "Testing Prices preview rows",
    });
    const previewFilter = screen.getByLabelText("Preview group");
    expect((previewFilter as HTMLSelectElement).value).toBe("all");
    expect(screen.getByText("Preview group").className).toContain(
      "fee-evaluation-sr-only"
    );
    expect(screen.queryByText("Fee")).toBeNull();
    expect(screen.getByLabelText("Selected group fee")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Fee Form" })).toBeTruthy();
    expect(screen.getAllByText("Pending Excel confirmation").length).toBeGreaterThan(0);
    const previewSurface = screen.getByLabelText("Testing Prices preview");
    const backButton = within(previewSurface).getByRole("button", {
      name: "Back to Workbench",
    });
    fireEvent.click(backButton);
    expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
    const headerBand = screen.getByLabelText("Testing Prices header");
    expect(within(headerBand).getByText("LTR Number")).toBeTruthy();
    expect(within(headerBand).getByText("DL-2026-001")).toBeTruthy();
    expect(within(headerBand).getByText("Requestor")).toBeTruthy();
    expect(within(headerBand).getByText("Lab User")).toBeTruthy();
    expect(within(headerBand).getByText("Test description")).toBeTruthy();
    expect(within(headerBand).getAllByText("Pending").length).toBeGreaterThan(0);
    for (const column of [
      "Group",
      "Step",
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
    expect(within(previewTable).queryByRole("columnheader", { name: "Price Percent Off" })).toBeNull();
    expect(within(previewTable).getAllByText("1").length).toBeGreaterThan(0);
    expect(within(previewTable).getAllByText("Pending").length).toBeGreaterThan(0);
    expect(within(previewTable).getAllByText("Visual Examination").length).toBeGreaterThan(0);
    expect(within(previewTable).getByText("Report preparation")).toBeTruthy();
    expect(within(previewTable).getByText("Condition confirmation")).toBeTruthy();
    expect(within(previewTable).getByText("External Cost (tooling / purchase cost)")).toBeTruthy();
    expect(screen.getByLabelText("Grand Cost preview")).toBeTruthy();
    expect(screen.getByLabelText("Lab manpower cost preview")).toBeTruthy();

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

  it("filters the Testing Prices preview by group and updates the group fee card", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithTwoGroups());

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    const previewTable = await screen.findByRole("table", {
      name: "Testing Prices preview rows",
    });
    expect(within(previewTable).getByText("Group 2 calculated")).toBeTruthy();

    fireEvent.change(screen.getByLabelText("Preview group"), {
      target: { value: "Group 1" },
    });

    expect(within(previewTable).getByText("Fixture setup")).toBeTruthy();
    expect(within(previewTable).queryByText("Group 2 calculated")).toBeNull();
    expect(within(previewTable).getByText("Report preparation")).toBeTruthy();
    expect(within(previewTable).getByText("Condition confirmation")).toBeTruthy();
    expect(within(previewTable).getByText("External Cost (tooling / purchase cost)")).toBeTruthy();
    expect(screen.queryByText("Selected total")).toBeNull();
    expect(screen.queryByText("Fee")).toBeNull();
    expect(screen.getAllByText("100.00").length).toBeGreaterThan(0);
  });

  it("shows a local preview loss warning without sending cost values to the Fee Form download", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());
    apiMocks.generateConfirmedMatrixFeeFileDownload.mockResolvedValue({
      blob: new Blob(["xls"], { type: "application/vnd.ms-excel" }),
      fileName: "Fee-P1.xls",
    });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:fee-file"),
      revokeObjectURL: vi.fn(),
    });

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    fireEvent.change(await screen.findByLabelText("Grand Cost preview"), {
      target: { value: "100" },
    });
    fireEvent.change(screen.getByLabelText("Lab manpower cost preview"), {
      target: { value: "125" },
    });

    expect(
      screen.getByText("Lab manpower cost exceeds Grand Cost. Review pricing before sending the fee form.")
    ).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Fee Form" }));

    await waitFor(() => {
      expect(apiMocks.generateConfirmedMatrixFeeFileDownload).toHaveBeenCalledWith("P1");
    });
  });

  it("keeps the Fee file action enabled when the project folder path is missing", async () => {
    arrangeSuccessfulContext({ folderPath: null });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    const exportButton = await screen.findByRole("button", { name: "Fee Form" });
    expect((exportButton as HTMLButtonElement).disabled).toBe(false);
    expect(
      screen.queryByText("Create the project folder before generating the workbook.")
    ).toBeNull();
  });

  it("downloads the generated Fee file through the direct download endpoint", async () => {
    arrangeSuccessfulContext({ folderPath: null });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());
    apiMocks.generateConfirmedMatrixFeeFileDownload.mockResolvedValue({
      blob: new Blob(["xls"], { type: "application/vnd.ms-excel" }),
      fileName: "Fee-P1.xls",
    });
    const clickSpy = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => undefined);
    vi.stubGlobal("URL", {
      createObjectURL: vi.fn(() => "blob:fee-file"),
      revokeObjectURL: vi.fn(),
    });

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    fireEvent.click(await screen.findByRole("button", { name: "Fee Form" }));

    await waitFor(() => {
      expect(apiMocks.generateConfirmedMatrixFeeFileDownload).toHaveBeenCalledWith("P1");
    });
    expect(clickSpy).toHaveBeenCalledTimes(1);
    expect(await screen.findByText("Fee-P1.xls downloaded.")).toBeTruthy();
  });

  it("shows timeout cleanup guidance from structured API detail", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());
    apiMocks.generateConfirmedMatrixFeeFileDownload.mockRejectedValue(
      new ApiRequestError("Fee Evaluation export timed out after 90 seconds.", 503, {
        message: "Fee Evaluation export timed out after 90 seconds.",
        elapsed_seconds: 90,
        manual_cleanup_warning: "Close the Excel instance opened by ConnLab if it remains.",
      })
    );

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    fireEvent.click(await screen.findByRole("button", { name: "Fee Form" }));

    expect(
      await screen.findByText("Fee Evaluation export timed out after 90 seconds.")
    ).toBeTruthy();
    expect(screen.getByText("Close the Excel instance opened by ConnLab if it remains.")).toBeTruthy();
  });
});

function arrangeSuccessfulContext(_input: { folderPath?: string | null } = {}): void {
  apiMocks.getProject.mockResolvedValue({
    project_id: "P1",
    project_no: "CP-001",
    product_name: "CoolPower HDF",
    requestor: "Lab User",
    status: "folder_created",
  });
  apiMocks.listProjectLtrs.mockResolvedValue([{ ltr_number: "DL-2026-001" }]);
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
            step_tokens: ["2", "3"],
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

function createDraftWithTwoGroups() {
  const draft = createDraft();
  return {
    ...draft,
    groups: [
      draft.groups[0],
      {
        group_key: "g2",
        group_label: "Group 2",
        sample_quantity_expression: "3",
        line_items: [
          createLine({
            line_id: "g2-calculated",
            group_key: "g2",
            group_label: "Group 2",
            confirmed_group_id: "cmg-2",
            confirmed_row_id: "row-2",
            test_item: "Group 2 calculated",
            testing_fee: "25.00",
            unit_price: "25.00",
            units: "1",
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
