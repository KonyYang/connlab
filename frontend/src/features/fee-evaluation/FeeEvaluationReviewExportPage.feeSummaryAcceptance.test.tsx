// Page-level acceptance coverage for the Fee Evaluation summary contract.
//
// Complements feeSummaryAcceptance.contract.test.ts (model path) by driving
// the real component: preview rows render from the Matrix fee draft, hydrate
// from the saved pricing draft, and the Confirm button issues the confirm
// request whose summary must match the shared acceptance samples in
// tests/contract_fixtures/fee_summary_acceptance_cases.json.
//
// Cases reused here:
// - baseline_simple: full Confirm path summary equals the golden sample.
// - multi_group_rows_all_counted: with the preview group filter set to one
//   group, Confirm must still send the FULL summary (contract: Confirm
//   reviews all active groups, including rows hidden by the group filter).

import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import type {
  FeeEvaluationDraft,
  FeeEvaluationEditedFileExportRequest,
  FeeEvaluationLineItem,
} from "../../api/client";
import { FeeEvaluationReviewExportPage } from "./FeeEvaluationReviewExportPage";

const apiMocks = vi.hoisted(() => ({
  inspectFeeForm: vi.fn(),
  fetchConfirmedMatrixFeeDraft: vi.fn(),
  generateConfirmedMatrixFeeFileDownload: vi.fn(),
  previewFeeFormPublication: vi.fn(),
  publishFeeForm: vi.fn(),
  confirmFeeVersion: vi.fn(),
  getConfirmedFeeLatest: vi.fn(),
  getFeeEvaluationPricingDraft: vi.fn(),
  getProjectLifecycle: vi.fn(),
  getProject: vi.fn(),
  listProjectLtrs: vi.fn(),
  discardFeeEvaluationPricingDraft: vi.fn(),
  saveFeeEvaluationPricingDraft: vi.fn(),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return {
    ...actual,
    inspectFeeForm: apiMocks.inspectFeeForm,
    confirmFeeVersion: apiMocks.confirmFeeVersion,
    fetchConfirmedMatrixFeeDraft: apiMocks.fetchConfirmedMatrixFeeDraft,
    generateConfirmedMatrixFeeFileDownload:
      apiMocks.generateConfirmedMatrixFeeFileDownload,
    previewFeeFormPublication: apiMocks.previewFeeFormPublication,
    publishFeeForm: apiMocks.publishFeeForm,
    getConfirmedFeeLatest: apiMocks.getConfirmedFeeLatest,
    getFeeEvaluationPricingDraft: apiMocks.getFeeEvaluationPricingDraft,
    getProjectLifecycle: apiMocks.getProjectLifecycle,
    getProject: apiMocks.getProject,
    listProjectLtrs: apiMocks.listProjectLtrs,
    discardFeeEvaluationPricingDraft: apiMocks.discardFeeEvaluationPricingDraft,
    saveFeeEvaluationPricingDraft: apiMocks.saveFeeEvaluationPricingDraft,
  };
});

describe("FeeEvaluationReviewExportPage fee summary acceptance", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    arrangeSuccessfulContext();
  });

  afterEach(() => {
    cleanup();
  });

  it("baseline_simple: Confirm sends the golden summary from the preview rows", async () => {
    // Golden case: one matrix row (fee 41, spend 1.5), external 150, rate 200.
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(
      createDraftWithSingleGroup({ fee: "41", spendTime: "1.5" })
    );
    let payload = payloadForGroups([
      { groupKey: "g1", groupLabel: "Group 1", confirmedGroupId: "cmg-1", rows: [{ fee: "41", spendTime: "1.5" }] },
    ], { externalCost: "150" });
    let generation = 1;
    const response = () => currentPricingDraftResponse({
      status: "current_v2",
      saved_generation: generation,
      saved_source_context_fingerprint: "context-1",
      saved_payload_fingerprint: `p${generation}`,
      saved_validation_token: `t${generation}`,
      payload,
    });
    apiMocks.getFeeEvaluationPricingDraft.mockImplementation(async () => response());
    apiMocks.saveFeeEvaluationPricingDraft.mockImplementation(async (_projectId, input) => {
      payload = JSON.parse(JSON.stringify(input, (_key, entry) => typeof entry === "string" ? entry.trim() : entry));
      generation += 1;
      return response();
    });
    apiMocks.confirmFeeVersion.mockResolvedValue(createConfirmedFeeLatest({ status: "current" }));
    const onBack = vi.fn();
    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBack} />);

    const confirm = await screen.findByRole("button", { name: "Confirm" });
    await waitFor(() => expect(confirm).toHaveProperty("disabled", false));
    fireEvent.click(confirm);

    await waitFor(() => expect(onBack).toHaveBeenCalledTimes(1));
    expect(apiMocks.confirmFeeVersion).toHaveBeenCalledWith("P1", expect.objectContaining({
      summary: {
        testing_fee_total: "41.00",
        working_hours: "1.5",
        lab_manpower_cost: "300",
        external_cost: "150",
        grand_cost: "191.00",
      },
    }));
  });

  it("multi_group_rows_all_counted: group filter does not change the Confirm summary", async () => {
    // Golden case: Group 1 (fee 41, spend 1) + Group 2 (fee 25, spend 2).
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(
      createDraftWithTwoGroups([
        { groupKey: "g1", groupLabel: "Group 1", confirmedGroupId: "cmg-1", rowId: "row-1", fee: "41", spendTime: "1" },
        { groupKey: "g2", groupLabel: "Group 2", confirmedGroupId: "cmg-2", rowId: "row-2", fee: "25", spendTime: "2" },
      ])
    );
    let payload = payloadForGroups([
      { groupKey: "g1", groupLabel: "Group 1", confirmedGroupId: "cmg-1", rows: [{ fee: "41", spendTime: "1" }] },
      { groupKey: "g2", groupLabel: "Group 2", confirmedGroupId: "cmg-2", rows: [{ fee: "25", spendTime: "2" }] },
    ], { externalCost: "0" });
    let generation = 1;
    const response = () => currentPricingDraftResponse({
      status: "current_v2",
      saved_generation: generation,
      saved_source_context_fingerprint: "context-1",
      saved_payload_fingerprint: `p${generation}`,
      saved_validation_token: `t${generation}`,
      payload,
    });
    apiMocks.getFeeEvaluationPricingDraft.mockImplementation(async () => response());
    apiMocks.saveFeeEvaluationPricingDraft.mockImplementation(async (_projectId, input) => {
      payload = JSON.parse(JSON.stringify(input, (_key, entry) => typeof entry === "string" ? entry.trim() : entry));
      generation += 1;
      return response();
    });
    apiMocks.confirmFeeVersion.mockResolvedValue(createConfirmedFeeLatest({ status: "current" }));
    const onBack = vi.fn();
    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBack} />);

    // Scope the preview to Group 1: the scoped fee label shows 41.00, but
    // Confirm must still review all active groups per the contract.
    const groupFilter = await screen.findByLabelText("Preview group");
    fireEvent.change(groupFilter, { target: { value: "Group 1" } });
    await waitFor(() =>
      expect(screen.getByLabelText("Selected group fee").textContent).toContain("41.00")
    );

    const confirm = screen.getByRole("button", { name: "Confirm" });
    await waitFor(() => expect(confirm).toHaveProperty("disabled", false));
    fireEvent.click(confirm);

    await waitFor(() => expect(onBack).toHaveBeenCalledTimes(1));
    expect(apiMocks.confirmFeeVersion).toHaveBeenCalledWith("P1", expect.objectContaining({
      summary: {
        testing_fee_total: "66.00",
        working_hours: "3.0",
        lab_manpower_cost: "600",
        external_cost: "0",
        grand_cost: "66.00",
      },
    }));
  });
});

type GroupSpec = {
  groupKey: string;
  groupLabel: string;
  confirmedGroupId: string;
  rowId?: string;
  fee: string;
  spendTime: string;
};

function arrangeSuccessfulContext(): void {
  apiMocks.getProject.mockResolvedValue({
    project_id: "P1",
    project_no: "CP-001",
    product_name: "CoolPower HDF",
    sample_description: "Coolpower HDF 3.40mm pin",
    test_item: "Qualification Testing",
    requestor: "Lab User",
    status: "folder_created",
  });
  apiMocks.listProjectLtrs.mockResolvedValue([{ ltr_number: "DL-2026-001" }]);
  apiMocks.getProjectLifecycle.mockResolvedValue({
    project_id: "P1",
    lifecycle_state: "active",
    closure_type: null,
    status: "folder_created",
    previous_project_status: null,
    stopped_at: null,
    closed_at: null,
    updated_at: "2026-06-27T09:00:00Z",
    allowed_actions: ["stop"],
    readonly: false,
    warnings: [],
  });
  apiMocks.getFeeEvaluationPricingDraft.mockResolvedValue({
    status: "missing",
    current_confirmed_matrix_id: "cmv-1",
    current_confirmed_revision: 1,
    current_fee_rule_version_id: "fee_rules_v2026_06_03",
    saved_draft_edit_id: null,
    payload: null,
  });
  apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValue(currentPricingDraftResponse());
  apiMocks.getConfirmedFeeLatest.mockResolvedValue(createConfirmedFeeLatest({ status: "missing" }));
  apiMocks.previewFeeFormPublication.mockResolvedValue({
    mode: "download",
    status: "ready",
    authority_status: "unconfirmed",
    existing_file: false,
    existing_modified_at: null,
    blockers: [],
    preview_token: "draft-preview",
  });
}

function currentPricingDraftResponse(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    status: "current",
    current_confirmed_matrix_id: "cmv-1",
    current_confirmed_revision: 1,
    current_fee_rule_version_id: "fee_rules_v2026_06_03",
    saved_confirmed_matrix_id: "cmv-1",
    saved_confirmed_revision: 1,
    saved_fee_rule_version_id: "fee_rules_v2026_06_03",
    saved_draft_edit_id: "fed-1",
    saved_updated_at: "2026-06-14T09:00:00+00:00",
    payload: null,
    ...overrides,
  };
}

function createConfirmedFeeLatest(input: { status: "missing" | "current" | "stale" }): Record<string, unknown> {
  return {
    status: input.status,
    current_confirmed_matrix_id: "cmv-1",
    current_confirmed_revision: 1,
    current_fee_rule_version_id: "fee_rules_v2026_06_03",
    confirmed_fee:
      input.status === "missing"
        ? null
        : {
            confirmed_fee_id: "cfv-1",
            project_id: "P1",
            confirmed_fee_revision: 1,
            confirmed_matrix_id: "cmv-1",
            confirmed_revision: 1,
            fee_rule_version_id: "fee_rules_v2026_06_03",
            pricing_draft_edit_id: "fed-1",
            pricing_effective_from: null,
            confirmed_by: "Lab User",
            confirmed_at: "2026-06-10T09:00:00+00:00",
            confirmation_note: null,
            summary: {
              testing_fee_total: "41.00",
              working_hours: "1.5",
              lab_manpower_cost: "300",
              external_cost: "150",
              grand_cost: "191.00",
            },
          },
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
    spend_time: "0",
    unit_label: "group",
    unit_price: "0",
    units: "1",
    base_fee: "0",
    discount_percent: "0",
    testing_fee: "0",
    warnings: [],
  };
}

function matrixLine(spec: GroupSpec): FeeEvaluationLineItem {
  return {
    ...baseLine(),
    line_id: `cmv-1:${spec.groupKey}:${spec.rowId ?? "row-1"}`,
    group_key: spec.groupKey,
    group_label: spec.groupLabel,
    confirmed_group_id: spec.confirmedGroupId,
    confirmed_row_id: spec.rowId ?? "row-1",
    spend_time: spec.spendTime,
    unit_price: "0",
    units: "1",
    base_fee: spec.fee,
    discount_percent: "0",
    testing_fee: spec.fee,
  };
}

// Manual rows contribute zero so the golden totals come from matrix rows only.
function zeroSamplePreparationLine(groupKey: string, groupLabel: string, confirmedGroupId: string): FeeEvaluationLineItem {
  return {
    ...baseLine(),
    line_id: `sample-preparation:${groupKey}`,
    confirmed_row_id: "",
    source_row_id: null,
    row_order: 0,
    test_item: "Sample preparation",
    step_tokens: [],
    spend_time: "0",
    matched_rule_id: "fee_rule_sample_preparation",
    matched_rule_name: "Sample preparation",
    match_reason: "backend_manual_default",
    calculation_strategy: "per_sample",
    unit_label: "sample",
    unit_price: "0",
    units: "1",
    base_fee: "0",
    discount_percent: "0",
    testing_fee: "0",
    group_key: groupKey,
    group_label: groupLabel,
    confirmed_group_id: confirmedGroupId,
    field_metadata: [],
  };
}

function zeroReportPreparationLine(): FeeEvaluationLineItem {
  return {
    ...baseLine(),
    line_id: "manual-report-preparation",
    group_key: "",
    group_label: "",
    confirmed_group_id: "",
    sample_quantity_expression: "",
    confirmed_row_id: "",
    source_row_id: null,
    row_order: 0,
    test_item: "Report preparation",
    step_tokens: [],
    spend_time: "0",
    matched_rule_id: "fee_rule_report_preparation",
    matched_rule_name: "Report preparation",
    match_reason: "backend_manual_default",
    calculation_strategy: "fixed_per_group",
    unit_label: "report",
    unit_price: "0",
    units: "1",
    base_fee: "0",
    discount_percent: "0",
    testing_fee: "0",
    field_metadata: [],
  };
}

function draftHeader(): FeeEvaluationDraft["header"] {
  return {
    project_id: "P1",
    confirmed_matrix_id: "cmv-1",
    confirmed_revision: 1,
    pricing_rule_version_id: "fee_rules_v2026_06_03",
    pricing_source_file_name: "Testing Fee Evaluation-Even.xls",
    pricing_source_hash: "sha256:abc",
    pricing_effective_from: "2026-06-03",
    generated_at: "2026-06-04T10:00:00+08:00",
  };
}

function createDraftWithSingleGroup(input: { fee: string; spendTime: string }): FeeEvaluationDraft {
  return {
    header: draftHeader(),
    draft_status: "needs_review",
    total_fee: null,
    review_required_count: 0,
    warnings: [],
    groups: [
      {
        group_key: "g1",
        group_label: "Group 1",
        sample_quantity_expression: "5",
        manual_line_items: [zeroSamplePreparationLine("g1", "Group 1", "cmg-1")],
        line_items: [matrixLine({ groupKey: "g1", groupLabel: "Group 1", confirmedGroupId: "cmg-1", fee: input.fee, spendTime: input.spendTime })],
      },
    ],
    manual_line_items: [zeroReportPreparationLine()],
  };
}

function createDraftWithTwoGroups(specs: GroupSpec[]): FeeEvaluationDraft {
  return {
    header: draftHeader(),
    draft_status: "needs_review",
    total_fee: null,
    review_required_count: 0,
    warnings: [],
    groups: specs.map((spec) => ({
      group_key: spec.groupKey,
      group_label: spec.groupLabel,
      sample_quantity_expression: "5",
      manual_line_items: [zeroSamplePreparationLine(spec.groupKey, spec.groupLabel, spec.confirmedGroupId)],
      line_items: [matrixLine(spec)],
    })),
    manual_line_items: [zeroReportPreparationLine()],
  };
}

type PayloadGroup = {
  groupKey: string;
  groupLabel: string;
  confirmedGroupId: string;
  rows: { fee: string; spendTime: string }[];
};

function payloadForGroups(
  groups: PayloadGroup[],
  options: { externalCost: string }
): FeeEvaluationEditedFileExportRequest {
  return {
    rows: groups.flatMap((group) =>
      group.rows.map((row, index) => ({
        source_line_id: `cmv-1:${group.groupKey}:row-${index + 1}:1:0`,
        confirmed_group_id: group.confirmedGroupId,
        confirmed_row_id: `row-${index + 1}`,
        step_token: "1",
        step_index: 0,
        spend_time: row.spendTime,
        unit_price: "0",
        unit_type: "group",
        units: "1",
        base_fee: row.fee,
        discount: "0%",
        testing_fee: row.fee,
        notes: "",
      }))
    ),
    manual_rows: [
      ...groups.map((group) => ({
        row_kind: "sample_preparation" as const,
        confirmed_group_id: group.confirmedGroupId,
        group_key: group.groupKey,
        group_label: group.groupLabel,
        spend_time: "0",
        unit_price: "0",
        unit_type: "sample",
        units: "1",
        base_fee: "0",
        discount: "0%",
        testing_fee: "0",
        notes: "",
      })),
      {
        row_kind: "report_preparation" as const,
        confirmed_group_id: "",
        group_key: "",
        group_label: "",
        spend_time: "0",
        unit_price: "0",
        unit_type: "report",
        units: "1",
        base_fee: "0",
        discount: "0%",
        testing_fee: "0",
        notes: "",
      },
    ],
    summary: {
      condition_confirmation_spend_time: "0",
      external_cost: options.externalCost,
      external_cost_note: "",
      lab_manpower_hourly_rate: "200",
    },
  };
}
