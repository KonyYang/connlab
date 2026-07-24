import { act, cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type {
  FeeEvaluationDraft,
  FeeEvaluationEditedFileExportRequest,
  FeeEvaluationLineItem,
} from "../../api/client";
import type {
  FeeEvaluationEditableField,
  FeeEvaluationPreviewRow,
} from "./feeEvaluationPreviewModel";
import { FeeEvaluationReviewExportPage } from "./FeeEvaluationReviewExportPage";

const apiMocks = vi.hoisted(() => ({
  confirmFeeVersion: vi.fn(),
  fetchConfirmedMatrixFeeDraft: vi.fn(),
  generateConfirmedMatrixFeeFileDownload: vi.fn(),
  getConfirmedFeeLatest: vi.fn(),
  getFeeEvaluationPricingDraft: vi.fn(),
  getProject: vi.fn(),
  getProjectLifecycle: vi.fn(),
  listProjectLtrs: vi.fn(),
  saveFeeEvaluationPricingDraft: vi.fn(),
}));

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return { ...actual, ...apiMocks };
});

vi.mock("./FeeEvaluationPreviewTable", () => ({
  FeeEvaluationPreviewTable: (props: {
    rows: FeeEvaluationPreviewRow[];
    saveState: { kind: string };
    generateDisabledReason: string | null;
    onGenerateFeeFile: () => void;
    onRowEditChange: (
      lineId: string,
      field: FeeEvaluationEditableField,
      value: string
    ) => void;
  }) => (
    <div>
      <output data-testid="visible-pricing-rows">
        {props.rows
          .map((row) =>
            [
              row.description,
              row.unitPrice,
              row.unitType,
              row.units,
              row.baseFee,
              row.discount,
              row.notes,
            ].join("|")
          )
          .join("\n")}
      </output>
      <output data-testid="pricing-save-state">{props.saveState.kind}</output>
      <button
        type="button"
        onClick={() => {
          const row = props.rows.find((candidate) => candidate.rowKind === "matrix_step");
          if (row) {
            props.onRowEditChange(row.lineId, "notes", "session edit");
          }
        }}
      >
        Edit matrix note
      </button>
      <button
        type="button"
        disabled={Boolean(props.generateDisabledReason)}
        onClick={props.onGenerateFeeFile}
      >
        Fee Form
      </button>
    </div>
  ),
}));

describe("FeeEvaluationReviewExportPage pricing-draft hydration", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
    vi.restoreAllMocks();
  });

  it("renders the server rebase candidate and reloads current_v2 before confirming", async () => {
    const candidate = pricingPayload({
      unit_price: "77",
      units: "3",
      testing_fee: "231",
      notes: "preserved manual note",
    });
    const reloaded = deferred<Record<string, unknown>>();
    arrangeContext();
    apiMocks.getFeeEvaluationPricingDraft
      .mockResolvedValueOnce(pricingResponse("rebase_required", 4, candidate))
      .mockReturnValueOnce(reloaded.promise);
    apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValue(
      pricingResponse("current_v2", 5, candidate)
    );
    apiMocks.confirmFeeVersion.mockResolvedValue({ status: "current" });

    render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />
    );

    await waitFor(() =>
      expect(screen.getByTestId("visible-pricing-rows").textContent).toContain(
        "Visual Examination|77|per sample|3|0|0%|preserved manual note"
      )
    );
    const feeForm = screen.getByRole("button", { name: "Fee Form" });
    expect((feeForm as HTMLButtonElement).disabled).toBe(true);
    fireEvent.click(feeForm);
    expect(apiMocks.generateConfirmedMatrixFeeFileDownload).not.toHaveBeenCalled();
    expect(apiMocks.saveFeeEvaluationPricingDraft).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Update Fee" }));
    await waitFor(() => expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1));
    expect((feeForm as HTMLButtonElement).disabled).toBe(true);
    expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledWith(
      "P1",
      expect.objectContaining({
        expected_generation: 4,
        expected_payload_fingerprint: "payload-4",
        rows: expect.arrayContaining([
          expect.objectContaining({ unit_price: "77", units: "3" }),
        ]),
      })
    );
    expect(apiMocks.confirmFeeVersion).not.toHaveBeenCalled();
    expect(apiMocks.getFeeEvaluationPricingDraft).toHaveBeenCalledTimes(2);

    reloaded.resolve(pricingResponse("current_v2", 5, candidate));
    await waitFor(() => expect(apiMocks.confirmFeeVersion).toHaveBeenCalledTimes(1));
    await waitFor(() => expect((feeForm as HTMLButtonElement).disabled).toBe(false));
  });

  it("does not seed-save a missing pricing draft during load", async () => {
    arrangeContext();
    apiMocks.getFeeEvaluationPricingDraft.mockResolvedValue(
      pricingResponse("missing", null, null)
    );

    render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />
    );

    await screen.findByTestId("visible-pricing-rows");
    expect((screen.getByRole("button", { name: "Fee Form" }) as HTMLButtonElement).disabled).toBe(true);
    await act(async () => {
      await new Promise((resolve) => window.setTimeout(resolve, 900));
    });
    expect(apiMocks.saveFeeEvaluationPricingDraft).not.toHaveBeenCalled();
  });

  it("does not restore Cancel over a newer server generation", async () => {
    const baseline = pricingPayload({ notes: "entry note" });
    arrangeContext();
    apiMocks.getFeeEvaluationPricingDraft
      .mockResolvedValueOnce(pricingResponse("current_v2", 1, baseline))
      .mockResolvedValueOnce(pricingResponse("current_v2", 3, baseline));
    apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValue(
      pricingResponse("current_v2", 2, pricingPayload({ notes: "session edit" }))
    );
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage
        projectId="P1"
        onBackToWorkbench={onBackToWorkbench}
      />
    );

    await waitFor(() =>
      expect(screen.getByTestId("visible-pricing-rows").textContent).toContain(
        "entry note"
      )
    );
    fireEvent.click(screen.getByRole("button", { name: "Edit matrix note" }));
    await waitFor(() =>
      expect(screen.getByTestId("visible-pricing-rows").textContent).toContain(
        "session edit"
      )
    );
    await waitFor(
      () => expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1),
      { timeout: 1600 }
    );
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    await waitFor(() => expect(apiMocks.getFeeEvaluationPricingDraft).toHaveBeenCalledTimes(2));

    expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1);
    expect(onBackToWorkbench).not.toHaveBeenCalled();
    expect(
      await screen.findByText("Fee Evaluation pricing changed. Refresh before leaving.")
    ).toBeTruthy();
    expect((screen.getByRole("button", { name: "Fee Form" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("restores the entry payload with the latest session-owned CAS", async () => {
    const baseline = pricingPayload({ notes: "entry note" });
    const edited = pricingPayload({ notes: "session edit" });
    arrangeContext();
    apiMocks.getFeeEvaluationPricingDraft
      .mockResolvedValueOnce(pricingResponse("current_v2", 1, baseline))
      .mockResolvedValueOnce(pricingResponse("current_v2", 2, edited))
      .mockResolvedValueOnce(pricingResponse("current_v2", 3, baseline));
    apiMocks.saveFeeEvaluationPricingDraft
      .mockResolvedValueOnce(pricingResponse("current_v2", 2, edited))
      .mockResolvedValueOnce(pricingResponse("current_v2", 3, baseline));
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage
        projectId="P1"
        onBackToWorkbench={onBackToWorkbench}
      />
    );
    await waitFor(() =>
      expect(screen.getByTestId("visible-pricing-rows").textContent).toContain(
        "entry note"
      )
    );
    fireEvent.click(screen.getByRole("button", { name: "Edit matrix note" }));
    await waitFor(
      () => expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1),
      { timeout: 1600 }
    );
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    await waitFor(() => expect(onBackToWorkbench).toHaveBeenCalledTimes(1));

    expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(2);
    expect(apiMocks.saveFeeEvaluationPricingDraft.mock.calls[1]?.[1]).toMatchObject({
      expected_pricing_draft_edit_id: "fed-1",
      expected_generation: 2,
      expected_payload_fingerprint: "payload-2",
      rows: [expect.objectContaining({ notes: "entry note" })],
    });
    expect(apiMocks.getFeeEvaluationPricingDraft).toHaveBeenCalledTimes(3);
  });
});

function arrangeContext(): void {
  apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(draft());
  apiMocks.getProject.mockResolvedValue({
    project_id: "P1",
    project_no: "CP-001",
    product_name: "Connector",
    requestor: "Lab User",
    status: "folder_created",
  });
  apiMocks.listProjectLtrs.mockResolvedValue([{ ltr_number: "DL-001" }]);
  apiMocks.getProjectLifecycle.mockResolvedValue({
    lifecycle_state: "active",
    closure_type: null,
    status: "folder_created",
    readonly: false,
    allowed_actions: ["stop"],
    warnings: [],
  });
  apiMocks.getConfirmedFeeLatest.mockResolvedValue({ status: "missing" });
}

function pricingResponse(
  status: "missing" | "current_v2" | "rebase_required",
  generation: number | null,
  payload: FeeEvaluationEditedFileExportRequest | null
): Record<string, unknown> {
  return {
    status,
    current_confirmed_matrix_id: "cmv-1",
    current_confirmed_revision: 1,
    current_fee_rule_version_id: "fee_rules_v2026_07_17_r6",
    saved_confirmed_matrix_id: generation === null ? null : "cmv-1",
    saved_confirmed_revision: generation === null ? null : 1,
    saved_fee_rule_version_id:
      generation === null ? null : "fee_rules_v2026_07_17_r6",
    saved_draft_edit_id: generation === null ? null : "fed-1",
    saved_generation: generation,
    saved_source_context_fingerprint: generation === null ? null : "context-1",
    saved_payload_fingerprint: generation === null ? null : `payload-${generation}`,
    saved_updated_at:
      generation === null ? null : `2026-07-24T09:0${generation}:00+00:00`,
    saved_validation_token: generation === null ? null : `token-${generation}`,
    payload,
  };
}

function pricingPayload(
  rowOverrides: Partial<FeeEvaluationEditedFileExportRequest["rows"][number]> = {}
): FeeEvaluationEditedFileExportRequest {
  return {
    rows: [
      {
        source_line_id: "cmv-1:g1:row-1:1:0",
        confirmed_group_id: "cmg-1",
        confirmed_row_id: "row-1",
        step_token: "1",
        step_index: 0,
        spend_time: "0",
        unit_price: "10",
        unit_type: "per sample",
        units: "1",
        base_fee: "0",
        discount: "0%",
        testing_fee: "10",
        notes: "",
        ...rowOverrides,
      },
    ],
    manual_rows: [],
    summary: {
      condition_confirmation_spend_time: "0",
      external_cost: "0",
      external_cost_note: "",
      lab_manpower_hourly_rate: "200",
    },
  };
}

function draft(): FeeEvaluationDraft {
  return {
    header: {
      project_id: "P1",
      confirmed_matrix_id: "cmv-1",
      confirmed_revision: 1,
      pricing_rule_version_id: "fee_rules_v2026_07_17_r6",
      pricing_source_file_name: "Testing Fee Evaluation.xls",
      pricing_source_hash: "sha256:test",
      pricing_effective_from: "2026-07-17",
      generated_at: "2026-07-24T09:00:00+00:00",
    },
    draft_status: "ready",
    total_fee: "10",
    review_required_count: 0,
    warnings: [],
    groups: [
      {
        group_key: "g1",
        group_label: "Group 1",
        sample_quantity_expression: "5",
        manual_line_items: [manualLine("sample-preparation:g1", "Sample preparation")],
        line_items: [matrixLine()],
      },
    ],
    manual_line_items: [manualLine("manual-report-preparation", "Report preparation")],
  };
}

function matrixLine(): FeeEvaluationLineItem {
  return {
    ...lineBase(),
    line_id: "cmv-1:g1:row-1",
    test_item: "Visual Examination",
    step_tokens: ["1"],
  };
}

function manualLine(lineId: string, testItem: string): FeeEvaluationLineItem {
  return {
    ...lineBase(),
    line_id: lineId,
    test_item: testItem,
    spend_time: "1",
    step_tokens: [],
  };
}

function lineBase(): FeeEvaluationLineItem {
  return {
    line_id: "line",
    status: "calculated",
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
    test_item: "Visual Examination",
    section: "6.1",
    method: "Visual",
    condition: "",
    requirement: "",
    step_tokens: ["1"],
    matched_rule_id: "fee-rule",
    matched_rule_version_id: "fee_rules_v2026_07_17_r6",
    matched_rule_name: "Visual Examination",
    match_reason: "exact",
    calculation_strategy: "per_sample",
    spend_time: "0",
    unit_label: "per sample",
    unit_price: "10",
    units: "1",
    base_fee: "0",
    discount_percent: "0",
    testing_fee: "10",
    warnings: [],
    field_metadata: [],
  };
}

function deferred<T>(): {
  promise: Promise<T>;
  resolve: (value: T) => void;
} {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((nextResolve) => {
    resolve = nextResolve;
  });
  return { promise, resolve };
}
