import { afterEach, describe, expect, it, vi } from "vitest";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { ApiRequestError } from "../../api/client";
import { FeeEvaluationReviewPanel } from "./FeeEvaluationReviewPanel";

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

describe("FeeEvaluationReviewPanel", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("renders loading then calculated and review-required fee rows", async () => {
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());

    render(<FeeEvaluationReviewPanel projectId="P1" ltrNumber="DL-001" />);

    expect(screen.getByText("Loading Fee Evaluation draft...")).toBeTruthy();
    expect(await screen.findByRole("heading", { name: "Fee Evaluation" })).toBeTruthy();
    expect(apiMocks.fetchConfirmedMatrixFeeDraft).toHaveBeenCalledWith("P1");
    expect(screen.getByText("DL-001")).toBeTruthy();
    expect(screen.getAllByText("fee_rules_v2026_06_03").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("2026-06-03")).toBeTruthy();
    expect(screen.getByText("2 lines require review")).toBeTruthy();
    expect(screen.getByText("Review required before total can be trusted.")).toBeTruthy();
    expect(screen.getByText("Total pending review")).toBeTruthy();

    const table = screen.getByRole("table", { name: "Fee Evaluation review rows" });
    const fixtureRow = within(table)
      .getAllByRole("row")
      .find((row) => within(row).queryAllByText("Fixture setup").length > 0);
    expect(fixtureRow).toBeTruthy();
    expect(within(fixtureRow as HTMLElement).getByText("Calculated")).toBeTruthy();
    expect(within(fixtureRow as HTMLElement).getAllByText("100.00")).toHaveLength(2);

    const visualRow = within(table)
      .getAllByRole("row")
      .find((row) => within(row).queryAllByText("Visual Examination").length > 0);
    expect(visualRow).toBeTruthy();
    expect(within(visualRow as HTMLElement).getByText("Review required")).toBeTruthy();
    expect(
      within(visualRow as HTMLElement).getByText("Photo count is not available from Matrix authority.")
    ).toBeTruthy();
    expect(screen.queryByRole("button", { name: /export/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /generate/i })).toBeNull();
  });

  it("renders no-authority state when the backend returns 404", async () => {
    apiMocks.fetchConfirmedMatrixFeeDraft.mockRejectedValue(
      new ApiRequestError("Active confirmed matrix not found.", 404, null)
    );

    render(<FeeEvaluationReviewPanel projectId="P1" />);

    expect(
      await screen.findByText("No active confirmed matrix yet. Confirm Matrix authority first.")
    ).toBeTruthy();
  });

  it("shows empty draft state for an active matrix without fee rows", async () => {
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue({
      ...createDraft(),
      draft_status: "empty",
      review_required_count: 0,
      groups: [],
    });

    render(<FeeEvaluationReviewPanel projectId="P1" />);

    expect(
      await screen.findByText("Active confirmed matrix found, but no fee rows are available.")
    ).toBeTruthy();
  });

  it("keeps operator edits local and marks the row as changed", async () => {
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());

    render(<FeeEvaluationReviewPanel projectId="P1" />);

    await waitFor(() => {
      expect(screen.getAllByText("Visual Examination").length).toBeGreaterThanOrEqual(1);
    });
    const unitsInputs = screen.getAllByLabelText("Units");
    fireEvent.change(unitsInputs[1], { target: { value: "12" } });

    expect(screen.getByText("Local review edits only. Reloading discards changes.")).toBeTruthy();
    const table = screen.getByRole("table", { name: "Fee Evaluation review rows" });
    const visualRow = within(table)
      .getAllByRole("row")
      .find((row) => within(row).queryAllByText("Visual Examination").length > 0);
    expect(visualRow).toBeTruthy();
    expect(within(visualRow as HTMLElement).getByText("Edited locally")).toBeTruthy();
  });
});

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
    warnings: [
      {
        code: "missing_pricing_effective_from",
        message: "Pricing effective date requires operator review.",
        scope: "draft",
      },
    ],
    groups: [
      {
        group_key: "g1",
        group_label: "Group 1",
        sample_quantity_expression: "5",
        line_items: [
          {
            line_id: "cmv-1:g1:fixture",
            status: "calculated",
            review_required: false,
            review_reason: null,
            confirmed_matrix_id: "cmv-1",
            confirmed_revision: 1,
            group_key: "g1",
            group_label: "Group 1",
            confirmed_group_id: "cmg-1",
            sample_quantity_expression: "5",
            confirmed_row_id: "fixture",
            source_row_id: "smr-fixture",
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
          },
          {
            line_id: "cmv-1:g1:visual",
            status: "review_required",
            review_required: true,
            review_reason: "Photo count is not available from Matrix authority.",
            confirmed_matrix_id: "cmv-1",
            confirmed_revision: 1,
            group_key: "g1",
            group_label: "Group 1",
            confirmed_group_id: "cmg-1",
            sample_quantity_expression: "5",
            confirmed_row_id: "visual",
            source_row_id: "smr-visual",
            row_order: 2,
            test_item: "Visual Examination",
            section: "6.2",
            method: "EIA-364-18",
            condition: "10x",
            requirement: "No damage",
            step_tokens: ["2"],
            matched_rule_id: "fee_rule_visual_exam",
            matched_rule_version_id: "fee_rules_v2026_06_03",
            matched_rule_name: "Visual Examination",
            match_reason: "alias",
            calculation_strategy: "per_photo",
            unit_label: "photo",
            unit_price: "10.00",
            units: null,
            base_fee: "0.00",
            discount_percent: "0",
            testing_fee: null,
            warnings: [
              {
                code: "manual_units_required",
                message: "Photo count is not available from Matrix authority.",
                scope: "line",
              },
            ],
          },
        ],
      },
    ],
  };
}
