import { afterEach, describe, expect, it, vi } from "vitest";
import {
  act,
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
    confirmFeeVersion: apiMocks.confirmFeeVersion,
    fetchConfirmedMatrixFeeDraft: apiMocks.fetchConfirmedMatrixFeeDraft,
    generateConfirmedMatrixFeeFileDownload:
      apiMocks.generateConfirmedMatrixFeeFileDownload,
    getConfirmedFeeLatest: apiMocks.getConfirmedFeeLatest,
    getFeeEvaluationPricingDraft: apiMocks.getFeeEvaluationPricingDraft,
    getProjectLifecycle: apiMocks.getProjectLifecycle,
    getProject: apiMocks.getProject,
    listProjectLtrs: apiMocks.listProjectLtrs,
    discardFeeEvaluationPricingDraft: apiMocks.discardFeeEvaluationPricingDraft,
    saveFeeEvaluationPricingDraft: apiMocks.saveFeeEvaluationPricingDraft,
  };
});

describe("FeeEvaluationReviewExportPage", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
    vi.restoreAllMocks();
    vi.useRealTimers();
    vi.unstubAllGlobals();
  });

  it("renders the editable Fee Evaluation preview without the removed review details surface", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());
    const onBackToWorkbench = vi.fn();

    const { container } = render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />
    );

    const feeEvaluationTitle = await screen.findByText(
      "DL-2026-001 Coolpower HDF 3.40mm pin Qualification Testing"
    );
    expect(feeEvaluationTitle).toBeTruthy();
    expect(feeEvaluationTitle.className).toContain("fee-evaluation-preview-title");
    expect(feeEvaluationTitle.getAttribute("title")).toBe(
      "DL-2026-001 Coolpower HDF 3.40mm pin Qualification Testing"
    );
    expect(screen.queryByText(/Matrix line\(s\)/)).toBeNull();
    expect(container.querySelector(".fee-evaluation-topbar")).toBeNull();
    expect(screen.queryByLabelText("Fee summary")).toBeNull();
    expect(screen.queryByLabelText("Matrix basic fill export")).toBeNull();
    expect(screen.queryByText("Excel output")).toBeNull();
    expect(screen.queryByText("Output directory")).toBeNull();
    expect(screen.queryByText("Selected total")).toBeNull();
    expect(screen.queryByText("Output freshness")).toBeNull();
    expect(screen.queryByText("Rule version")).toBeNull();
    expect(screen.queryByText("Review details")).toBeNull();
    expect(screen.queryByLabelText("Confirmed by")).toBeNull();
    expect(screen.queryByText("Confirmed by")).toBeNull();
    expect(screen.queryByLabelText("Confirmed Fee status")).toBeNull();
    expect(screen.queryByText("Fee authority is current.")).toBeNull();

    const tables = screen.getAllByRole("table");
    expect(tables).toHaveLength(1);
    expect(tables[0].getAttribute("aria-label")).toBe("Testing Prices preview rows");

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
    expect(screen.getByText("Total Testing Fee")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Fee Form" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Back to Workbench" })).toBeNull();
    const completionDock = screen.getByLabelText("Fee Evaluation completion actions");
    expect(completionDock.classList.contains("fee-evaluation-completion-dock")).toBe(true);
    const cancelButton = within(completionDock).getByRole("button", {
      name: "Cancel",
    });
    expect(within(completionDock).getByRole("button", { name: "Update Fee" })).toBeTruthy();
    fireEvent.click(cancelButton);
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
      "Man-hour",
      "Description",
      "Unit Price",
      "Unit Type",
      "Units",
      "Base Fee",
      "Discount",
      "Testing Fee",
      "Notes",
    ]) {
      expect(within(previewTable).getByRole("columnheader", { name: column })).toBeTruthy();
    }
    expect(within(previewTable).queryByRole("columnheader", { name: "Price Percent Off" })).toBeNull();
    expect(within(previewTable).getAllByText("1").length).toBeGreaterThan(0);
    expect(within(previewTable).getAllByText("Visual Examination").length).toBeGreaterThan(0);
    expect(
      within(previewTable).getAllByText(
        "Review: Photo count is not available from Matrix authority."
      ).length
    ).toBeGreaterThan(0);
    expect(within(previewTable).getByText("Report preparation")).toBeTruthy();
    expect(within(previewTable).queryByText("Condition confirmation")).toBeNull();
    expect(within(previewTable).queryByText("External Cost (tooling / purchase cost)")).toBeNull();
    expect(screen.getByLabelText("Condition confirmation spend time")).toBeTruthy();
    expect(screen.getByLabelText("External Cost preview")).toBeTruthy();
    expect(screen.getByLabelText("Lab manpower hourly rate")).toBeTruthy();
    expect(screen.getByLabelText("Unit Price for Fixture setup")).toBeTruthy();
    expect(screen.getByLabelText("Units for Fixture setup")).toBeTruthy();
    expect(screen.getAllByLabelText("Unit Type").length).toBeGreaterThan(0);
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
    expect(screen.queryByText("Selected total")).toBeNull();
    expect(screen.queryByText("Fee")).toBeNull();
    expect(screen.getByLabelText("Selected group fee").textContent).toContain("120.00");
  });

  it("updates Working hours and Grand Cost when the group filter changes", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(
      createDraftWithTwoCalculatedGroups()
    );

    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />
    );

    await screen.findByRole("table", { name: "Testing Prices preview rows" });
    fireEvent.change(screen.getByLabelText("Spend Time for group Group 1 step 1"), {
      target: { value: "1" },
    });
    fireEvent.change(screen.getByLabelText("Spend Time for group Group 2 step 1"), {
      target: { value: "2" },
    });

    const totals = screen.getByLabelText("Testing Prices totals");
    expect(within(totals).getByText("Working hours")).toBeTruthy();
    expect(within(totals).getByText("8.0")).toBeTruthy();
    expect(within(totals).getByText("125.00")).toBeTruthy();

    fireEvent.change(screen.getByLabelText("Preview group"), {
      target: { value: "Group 1" },
    });

    expect(screen.getByLabelText("Selected group fee").textContent).toContain("100.00");
    expect(within(totals).getByText("Grand Cost")).toBeTruthy();
    expect(within(totals).getByText("1.5")).toBeTruthy();
    expect(within(totals).getByText("100.00")).toBeTruthy();
  });

  it("clears local cost preview values when the project draft reloads", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());

    const { rerender } = render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />
    );

    const externalCostInput = await screen.findByLabelText("External Cost preview");
    fireEvent.change(externalCostInput, { target: { value: "500" } });
    fireEvent.change(screen.getByLabelText("Lab manpower hourly rate"), {
      target: { value: "125" },
    });
    fireEvent.change(screen.getByLabelText("Condition confirmation spend time"), {
      target: { value: "2" },
    });

    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithTwoCalculatedGroups());
    rerender(<FeeEvaluationReviewExportPage projectId="P2" onBackToWorkbench={vi.fn()} />);

    await waitFor(() => {
      expect(apiMocks.fetchConfirmedMatrixFeeDraft).toHaveBeenCalledWith("P2");
    });
    await waitFor(() => {
      expect(
        (screen.getByLabelText("External Cost preview") as HTMLInputElement).value
      ).toBe("0");
      expect(
        (screen.getByLabelText("Lab manpower hourly rate") as HTMLInputElement).value
      ).toBe("200");
      expect(
        (screen.getByLabelText("Condition confirmation spend time") as HTMLInputElement)
          .value
      ).toBe("0");
    });
  });

  it("sends current edited preview values to the Fee Form download", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());
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

    fireEvent.change(await screen.findByLabelText("Unit Price for Visual Examination"), {
      target: { value: "10" },
    });
    fireEvent.change(screen.getByLabelText("Units for Visual Examination"), {
      target: { value: "3" },
    });
    fireEvent.change(screen.getByLabelText("Base Fee for Visual Examination"), {
      target: { value: "2" },
    });
    fireEvent.change(screen.getByLabelText("Discount for Visual Examination"), {
      target: { value: "10%" },
    });
    fireEvent.change(screen.getByLabelText("Notes for Visual Examination"), {
      target: { value: "discount approved" },
    });
    expect(screen.getAllByText("29").length).toBeGreaterThan(0);

    fireEvent.change(screen.getByLabelText("Spend Time for group Group 1 step 1"), {
      target: { value: "1" },
    });
    fireEvent.change(screen.getByLabelText("Condition confirmation spend time"), {
      target: { value: "0.5" },
    });
    fireEvent.change(screen.getByLabelText("External Cost preview"), {
      target: { value: "150" },
    });
    fireEvent.change(screen.getByLabelText("External Cost note"), {
      target: { value: "tooling" },
    });
    fireEvent.change(screen.getByLabelText("Lab manpower hourly rate"), {
      target: { value: "125" },
    });

    expect(
      screen.getByText("Lab manpower cost exceeds Grand Cost. Review pricing before sending the fee form.")
    ).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Fee Form" }));

    await waitFor(() => {
      expect(apiMocks.generateConfirmedMatrixFeeFileDownload).toHaveBeenCalled();
    });
    const payload = apiMocks.generateConfirmedMatrixFeeFileDownload.mock.calls[0][1];
    expect(apiMocks.generateConfirmedMatrixFeeFileDownload).toHaveBeenCalledWith(
      "P1",
      expect.any(Object)
    );
    expect(payload.rows[0]).toMatchObject({
      source_line_id: "cmv-1:g1:row-1:1:0",
      confirmed_group_id: "cmg-1",
      confirmed_row_id: "row-1",
      step_token: "1",
      step_index: 0,
      spend_time: "1",
    });
    expect(payload.rows[0].notes).toBe("discount approved");
    expect(payload.summary).toMatchObject({
      condition_confirmation_spend_time: "0.5",
      external_cost: "150",
      external_cost_note: "tooling",
      lab_manpower_hourly_rate: "125",
    });
    expect(payload.manual_rows[0]).toMatchObject({
      row_kind: "sample_preparation",
      confirmed_group_id: "cmg-1",
      group_key: "g1",
      group_label: "Group 1",
      spend_time: "0.5",
      unit_price: "50",
      unit_type: "per sample",
      units: "5",
      base_fee: "0",
      discount: "100%",
      notes: "",
    });
    expect(payload.manual_rows[1]).toMatchObject({
      row_kind: "report_preparation",
      spend_time: "4",
      unit_price: "600",
      unit_type: "per report",
      units: "1",
      discount: "100%",
    });
    expect(
      await screen.findByText(
        /^DL-2026-001 Fee Evaluation Draft \d{14}\.xls downloaded\.$/
      )
    ).toBeTruthy();
  });

  it("autosaves current pricing draft edits through the pricing draft endpoint", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());
    apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValue(currentPricingDraftResponse());

    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />
    );

    expect(await screen.findByRole("table", { name: "Testing Prices preview rows" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Save changes" })).toBeNull();
    fireEvent.change(await screen.findByLabelText("Unit Price for Visual Examination"), {
      target: { value: "12" },
    });
    expect(screen.queryByText("Unsaved changes.")).toBeNull();
    expect(apiMocks.saveFeeEvaluationPricingDraft).not.toHaveBeenCalled();

    await waitFor(() => {
      expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledWith(
        "P1",
        expect.objectContaining({
          rows: expect.arrayContaining([
            expect.objectContaining({
              source_line_id: "cmv-1:g1:row-1:1:0",
              unit_price: "12",
            }),
          ]),
        }),
        expect.objectContaining({ signal: expect.any(AbortSignal) })
      );
    }, { timeout: 1600 });
    expect(screen.queryByText("Saved pricing draft.")).toBeNull();
  });

  it("seeds a missing pricing draft from defaults and confirms without an extra save", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithTwoCalculatedGroups());
    apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValue({
      ...currentPricingDraftResponse(),
      saved_draft_edit_id: "fed-seeded",
    });
    apiMocks.confirmFeeVersion.mockResolvedValue(
      createConfirmedFeeLatest({
        status: "current",
        pricingDraftEditId: "fed-seeded",
        testingFeeTotal: "125.00",
      })
    );

    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />
    );

    await screen.findByRole("table", { name: "Testing Prices preview rows" });
    await waitFor(() => {
      expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1);
    }, { timeout: 1600 });
    fireEvent.click(screen.getByRole("button", { name: "Update Fee" }));

    await waitFor(() => {
      expect(apiMocks.confirmFeeVersion).toHaveBeenCalledWith("P1", {
        confirmed_by: "Lab User",
        expected_pricing_draft_edit_id: "fed-seeded",
        summary: {
          testing_fee_total: "125.00",
          working_hours: "5.0",
          lab_manpower_cost: "1000",
          external_cost: "0",
          grand_cost: "125.00",
        },
      });
    });
    expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
    expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1);
  });

  it("confirms Fee Evaluation with the latest autosaved draft id without saving again", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithTwoCalculatedGroups());
    apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValue({
      ...currentPricingDraftResponse(),
      saved_draft_edit_id: "fed-current",
    });
    apiMocks.confirmFeeVersion.mockResolvedValue(
      createConfirmedFeeLatest({
        status: "current",
        pricingDraftEditId: "fed-current",
        testingFeeTotal: "150.00",
      })
    );

    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />
    );

    await screen.findByRole("table", { name: "Testing Prices preview rows" });
    fireEvent.change(screen.getByLabelText("Preview group"), {
      target: { value: "Group 1" },
    });
    fireEvent.change(screen.getByLabelText("Unit Price for Group 1 calculated"), {
      target: { value: "120" },
    });
    fireEvent.change(screen.getByLabelText("External Cost preview"), {
      target: { value: "5" },
    });
    expect(
      (screen.getByRole("button", { name: "Update Fee" }) as HTMLButtonElement)
        .disabled
    ).toBe(true);
    await waitFor(() => {
      expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1);
    }, { timeout: 1600 });
    fireEvent.click(screen.getByRole("button", { name: "Update Fee" }));

    await waitFor(() => {
      expect(apiMocks.confirmFeeVersion).toHaveBeenCalledWith("P1", {
        confirmed_by: "Lab User",
        expected_pricing_draft_edit_id: "fed-current",
        summary: {
          testing_fee_total: "145.00",
          working_hours: "5.0",
          lab_manpower_cost: "1000",
          external_cost: "5",
          grand_cost: "150.00",
        },
      });
    });
    expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
    expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1);
    expect(screen.queryByText("Confirmed")).toBeNull();
    expect(screen.queryByText("Fee authority is current.")).toBeNull();
  });

  it("keeps status card hidden when saved pricing draft id differs from confirmed fee id", async () => {
    arrangeSuccessfulContext({
      pricingDraft: {
        status: "current",
        current_confirmed_matrix_id: "cmv-1",
        current_confirmed_revision: 1,
        current_fee_rule_version_id: "fee_rules_v2026_06_03",
        saved_draft_edit_id: "fed-newer",
        payload: null,
      },
      confirmedFee: createConfirmedFeeLatest({
        status: "current",
        pricingDraftEditId: "fed-confirmed",
      }),
    });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    await screen.findByRole("table", { name: "Testing Prices preview rows" });
    expect(screen.queryByText("Unconfirmed saved changes")).toBeNull();
  });

  it("loads a promoted current pricing draft and allows Update Fee when authority is missing", async () => {
    arrangeSuccessfulContext({
      pricingDraft: currentPricingDraftResponse({
        saved_draft_edit_id: "fed-promoted",
        payload: promotedPricingDraftPayload({
          unit_price: "33",
          units: "2",
          testing_fee: "66",
          notes: "promoted pricing note",
        }),
      }),
      confirmedFee: createConfirmedFeeLatest({ status: "missing" }),
    });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());
    apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValue(currentPricingDraftResponse({
      saved_draft_edit_id: "fed-promoted-blank-unit",
    }));
    apiMocks.confirmFeeVersion.mockResolvedValue(
      createConfirmedFeeLatest({
        status: "current",
        pricingDraftEditId: "fed-promoted",
        testingFeeTotal: "66.00",
      })
    );

    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />
    );

    expect(await screen.findByDisplayValue("promoted pricing note")).toBeTruthy();
    expect(screen.queryByText("Not confirmed")).toBeNull();
    expect(screen.queryByText("Save pricing draft before updating Fee.")).toBeNull();
    expect(screen.queryByText(/fee_rebase|payload_signature|\/api\//i)).toBeNull();
    expect(screen.getByRole("button", { name: "Update Fee" })).toHaveProperty(
      "disabled",
      false
    );

    fireEvent.click(screen.getByRole("button", { name: "Update Fee" }));

    await waitFor(() => {
      expect(apiMocks.confirmFeeVersion).toHaveBeenCalledWith(
        "P1",
        expect.objectContaining({
          expected_pricing_draft_edit_id: "fed-promoted",
        })
      );
    });
  });

  it("normalizes blank unit type from promoted pricing draft before autosave", async () => {
    arrangeSuccessfulContext({
      pricingDraft: currentPricingDraftResponse({
        saved_draft_edit_id: "fed-promoted-blank-unit",
        payload: promotedPricingDraftPayload({
          unit_type: "",
          notes: "promoted pricing note",
        }),
      }),
      confirmedFee: createConfirmedFeeLatest({ status: "missing" }),
    });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());

    const { unmount } = render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />
    );

    expect(await screen.findByDisplayValue("promoted pricing note")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("Notes for Visual Examination"), {
      target: { value: "operator note survives" },
    });

    await waitFor(() => {
      expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1);
    }, { timeout: 1600 });
    const payload = apiMocks.saveFeeEvaluationPricingDraft.mock.calls[0]?.[1];
    expect(payload.rows[0]).toMatchObject({
      unit_type: "per photo",
      notes: "operator note survives",
    });
    unmount();
  });

  it("normalizes pending numeric values from promoted pricing draft before confirming", async () => {
    arrangeSuccessfulContext({
      pricingDraft: currentPricingDraftResponse({
        saved_draft_edit_id: "fed-promoted-pending-numeric",
        payload: promotedPricingDraftPayload({
          spend_time: "Pending",
          unit_price: "Pending",
          units: "Pending",
          base_fee: "Pending",
          discount: "Pending",
          testing_fee: "Pending",
          notes: "promoted numeric note",
        }),
      }),
      confirmedFee: createConfirmedFeeLatest({ status: "missing" }),
    });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());
    apiMocks.confirmFeeVersion.mockResolvedValue(
      createConfirmedFeeLatest({
        status: "current",
        pricingDraftEditId: "fed-promoted-pending-numeric",
        testingFeeTotal: "10.00",
      })
    );

    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />
    );

    expect(await screen.findByDisplayValue("promoted numeric note")).toBeTruthy();
    expect(screen.getByLabelText("Selected group fee").textContent).toContain("10.00");
    expect(screen.getByRole("button", { name: "Update Fee" })).toHaveProperty(
      "disabled",
      false
    );

    fireEvent.click(screen.getByRole("button", { name: "Update Fee" }));

    await waitFor(() => {
      expect(apiMocks.confirmFeeVersion).toHaveBeenCalledWith("P1", {
        confirmed_by: "Lab User",
        expected_pricing_draft_edit_id: "fed-promoted-pending-numeric",
        summary: {
          testing_fee_total: "10.00",
          working_hours: "4.5",
          lab_manpower_cost: "900",
          external_cost: "0",
          grand_cost: "10.00",
        },
      });
    });
    expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
  });

  it("allows Update Fee refresh when confirmed fee is stale and promoted draft is current", async () => {
    arrangeSuccessfulContext({
      pricingDraft: currentPricingDraftResponse({
        saved_draft_edit_id: "fed-promoted-updated",
        payload: promotedPricingDraftPayload({
          unit_price: "10",
          testing_fee: "10",
          notes: "stale authority refresh",
        }),
      }),
      confirmedFee: createConfirmedFeeLatest({
        status: "stale",
        pricingDraftEditId: "fed-old",
      }),
    });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());
    apiMocks.confirmFeeVersion.mockResolvedValue(
      createConfirmedFeeLatest({
        status: "current",
        pricingDraftEditId: "fed-promoted-updated",
      })
    );

    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />
    );

    expect(await screen.findByDisplayValue("stale authority refresh")).toBeTruthy();
    expect(screen.queryByText("Confirmed Fee stale")).toBeNull();
    await waitFor(() => {
      expect(screen.getByRole("button", { name: "Update Fee" })).toHaveProperty(
        "disabled",
        false
      );
    });

    fireEvent.click(screen.getByRole("button", { name: "Update Fee" }));

    await waitFor(() => {
      expect(apiMocks.confirmFeeVersion).toHaveBeenCalledWith(
        "P1",
        expect.objectContaining({
          expected_pricing_draft_edit_id: "fed-promoted-updated",
        })
      );
    });
  });

  it("keeps status card hidden when confirmed fee is current but no current pricing draft is loaded", async () => {
    arrangeSuccessfulContext({
      pricingDraft: {
        status: "missing",
        current_confirmed_matrix_id: "cmv-1",
        current_confirmed_revision: 1,
        current_fee_rule_version_id: "fee_rules_v2026_06_03",
        saved_draft_edit_id: null,
        payload: null,
      },
      confirmedFee: createConfirmedFeeLatest({
        status: "current",
        pricingDraftEditId: "fed-confirmed",
      }),
    });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    await screen.findByRole("table", { name: "Testing Prices preview rows" });
    expect(screen.queryByText("Unconfirmed pricing draft")).toBeNull();
  });

  it("keeps status card hidden while disabling confirm for local pricing changes", async () => {
    arrangeSuccessfulContext({
      pricingDraft: {
        status: "current",
        current_confirmed_matrix_id: "cmv-1",
        current_confirmed_revision: 1,
        current_fee_rule_version_id: "fee_rules_v2026_06_03",
        saved_draft_edit_id: "fed-1",
        payload: null,
      },
      confirmedFee: createConfirmedFeeLatest({
        status: "current",
        pricingDraftEditId: "fed-1",
      }),
    });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    await screen.findByRole("table", { name: "Testing Prices preview rows" });
    expect(screen.queryByText("Confirmed")).toBeNull();
    fireEvent.change(screen.getByLabelText("Unit Price for Visual Examination"), {
      target: { value: "12" },
    });
    expect(screen.queryByText("Unconfirmed local changes")).toBeNull();
    expect(screen.getByRole("button", { name: "Update Fee" })).toHaveProperty(
      "disabled",
      true
    );
  });

  it("does not confirm when autosave succeeds without a pricing draft id", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());
    apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValue({
      status: "current",
      current_confirmed_matrix_id: "cmv-1",
      current_confirmed_revision: 1,
      current_fee_rule_version_id: "fee_rules_v2026_06_03",
      saved_draft_edit_id: null,
      payload: null,
    });

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    fireEvent.change(await screen.findByLabelText("Unit Price for Visual Examination"), {
      target: { value: "12" },
    });

    expect(
      await screen.findAllByText(
        "Save returned no pricing draft id. Retry before updating."
      )
    ).toHaveLength(2);
    expect(
      (screen.getByRole("button", { name: "Update Fee" }) as HTMLButtonElement)
        .disabled
    ).toBe(true);
    expect(apiMocks.confirmFeeVersion).not.toHaveBeenCalled();
  });

  it("returns to Workbench without deleting the current pricing draft when unchanged", async () => {
    arrangeSuccessfulContext({ pricingDraft: currentPricingDraftResponse() });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());
    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage
        projectId="P1"
        onBackToWorkbench={onBackToWorkbench}
      />
    );

    await screen.findByRole("table", { name: "Testing Prices preview rows" });
    expect(screen.queryByText("Loaded saved pricing draft.")).toBeNull();
    fireEvent.click(await screen.findByRole("button", { name: "Cancel" }));

    expect(apiMocks.discardFeeEvaluationPricingDraft).not.toHaveBeenCalled();
    expect(apiMocks.saveFeeEvaluationPricingDraft).not.toHaveBeenCalled();
    expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
  });

  it("keeps closed projects read-only and blocks Fee writes", async () => {
    arrangeSuccessfulContext({
      pricingDraft: currentPricingDraftResponse(),
      lifecycle: lifecycleResponse({
        lifecycle_state: "closed",
        closure_type: "completed",
        status: "closed",
        readonly: true,
        allowed_actions: [],
      }),
    });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());

    render(
      <FeeEvaluationReviewExportPage
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    expect(await screen.findByText("Project closed: Completed")).toBeTruthy();
    expect(
      screen
        .getAllByLabelText("Unit Price for Visual Examination")
        .every((input) => (input as HTMLInputElement).disabled)
    ).toBe(true);
    const updateButton = screen.getByRole("button", { name: "Update Fee" });
    expect(updateButton).toHaveProperty("disabled", true);
    fireEvent.click(updateButton);
    fireEvent.click(screen.getByRole("button", { name: "Fee Form" }));
    expect(apiMocks.confirmFeeVersion).not.toHaveBeenCalled();
    expect(apiMocks.saveFeeEvaluationPricingDraft).not.toHaveBeenCalled();
    expect(apiMocks.generateConfirmedMatrixFeeFileDownload).not.toHaveBeenCalled();
  });

  it("restores the entry baseline before leaving when autosave already saved edits", async () => {
    arrangeSuccessfulContext({
      pricingDraft: currentPricingDraftResponse({
        payload: promotedPricingDraftPayload({
          notes: "baseline note",
          unit_price: "10",
          testing_fee: "10",
        }),
      }),
    });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());
    apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValue(currentPricingDraftResponse());
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage
        projectId="P1"
        onBackToWorkbench={onBackToWorkbench}
      />
    );

    expect(await screen.findByDisplayValue("baseline note")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("Notes for Visual Examination"), {
      target: { value: "dirty note" },
    });
    await waitFor(() => {
      expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1);
    }, { timeout: 1600 });

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    await waitFor(() => {
      expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(2);
    });

    const restorePayload = apiMocks.saveFeeEvaluationPricingDraft.mock.calls[1]?.[1];
    expect(restorePayload).toMatchObject({
      expected_confirmed_matrix_id: "cmv-1",
      expected_confirmed_revision: 1,
      expected_fee_rule_version_id: "fee_rules_v2026_06_03",
    });
    expect(restorePayload.rows[0]).toMatchObject({
      notes: "baseline note",
      unit_price: "10",
      testing_fee: "10",
    });
    expect(apiMocks.discardFeeEvaluationPricingDraft).not.toHaveBeenCalled();
    expect(onBackToWorkbench).toHaveBeenCalledTimes(1);
  });

  it("stays on Fee Evaluation when baseline restore fails", async () => {
    arrangeSuccessfulContext({ pricingDraft: currentPricingDraftResponse() });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());
    apiMocks.saveFeeEvaluationPricingDraft.mockRejectedValue(
      new Error("Unable to restore Fee Evaluation pricing before leaving.")
    );
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />
    );

    await screen.findByRole("table", { name: "Testing Prices preview rows" });
    fireEvent.change(screen.getByLabelText("Unit Price for Visual Examination"), {
      target: { value: "12" },
    });
    await screen.findByText("Saving pricing draft before update.");

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    await waitFor(() => {
      expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1);
    });
    expect(apiMocks.discardFeeEvaluationPricingDraft).not.toHaveBeenCalled();
    expect(onBackToWorkbench).not.toHaveBeenCalled();
    expect(
      await screen.findAllByText(
        "Unable to restore Fee Evaluation pricing before leaving."
      )
    ).toHaveLength(2);
  });

  it("stays on Fee Evaluation when in-flight autosave cannot be confirmed safe", async () => {
    arrangeSuccessfulContext({ pricingDraft: currentPricingDraftResponse() });
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());
    apiMocks.saveFeeEvaluationPricingDraft.mockReturnValue(new Promise(() => undefined));
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const abortSpy = vi.spyOn(AbortController.prototype, "abort");
    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />
    );

    await screen.findByRole("table", { name: "Testing Prices preview rows" });
    vi.useFakeTimers();
    fireEvent.change(screen.getByLabelText("Unit Price for Visual Examination"), {
      target: { value: "12" },
    });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(800);
    });
    expect(apiMocks.saveFeeEvaluationPricingDraft).toHaveBeenCalledTimes(1);

    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1500);
    });
    vi.useRealTimers();

    expect(abortSpy).not.toHaveBeenCalled();
    expect(apiMocks.discardFeeEvaluationPricingDraft).not.toHaveBeenCalled();
    expect(onBackToWorkbench).not.toHaveBeenCalled();
    expect(
      await screen.findAllByText(
        "Fee Evaluation is still saving. Wait a moment and retry Cancel."
      )
    ).toHaveLength(2);
  });

  it("stays on Fee Evaluation when the Matrix or fee context changed before restore", async () => {
    arrangeSuccessfulContext({ pricingDraft: currentPricingDraftResponse() });
    apiMocks.getFeeEvaluationPricingDraft
      .mockResolvedValueOnce(currentPricingDraftResponse())
      .mockResolvedValueOnce(
        currentPricingDraftResponse({
          current_confirmed_matrix_id: "cmv-2",
          current_confirmed_revision: 2,
        })
      );
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraftWithEditableSingleLine());
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const onBackToWorkbench = vi.fn();

    render(
      <FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={onBackToWorkbench} />
    );

    await screen.findByRole("table", { name: "Testing Prices preview rows" });
    fireEvent.change(screen.getByLabelText("Unit Price for Visual Examination"), {
      target: { value: "12" },
    });
    await screen.findByText("Saving pricing draft before update.");
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    await waitFor(() => {
      expect(apiMocks.getFeeEvaluationPricingDraft).toHaveBeenCalledTimes(2);
    });
    expect(apiMocks.saveFeeEvaluationPricingDraft).not.toHaveBeenCalled();
    expect(apiMocks.discardFeeEvaluationPricingDraft).not.toHaveBeenCalled();
    expect(onBackToWorkbench).not.toHaveBeenCalled();
    expect(
      await screen.findAllByText(
        "Fee Evaluation context changed. Refresh before leaving."
      )
    ).toHaveLength(2);
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
      expect(apiMocks.generateConfirmedMatrixFeeFileDownload).toHaveBeenCalledWith(
        "P1",
        expect.any(Object)
      );
    });
    expect(clickSpy).toHaveBeenCalledTimes(1);
    expect(
      await screen.findByText(
        /^DL-2026-001 Fee Evaluation Draft \d{14}\.xls downloaded\.$/
      )
    ).toBeTruthy();
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

  it("shows the template-missing download error instead of a Matrix blocker", async () => {
    arrangeSuccessfulContext();
    apiMocks.fetchConfirmedMatrixFeeDraft.mockResolvedValue(createDraft());
    apiMocks.generateConfirmedMatrixFeeFileDownload.mockRejectedValue(
      new ApiRequestError(
        "Template does not exist: D:\\Source\\Template\\Testing Fee Evaluation-Even.optimized-v1.xls",
        404,
        "Template does not exist: D:\\Source\\Template\\Testing Fee Evaluation-Even.optimized-v1.xls"
      )
    );

    render(<FeeEvaluationReviewExportPage projectId="P1" onBackToWorkbench={vi.fn()} />);

    fireEvent.click(await screen.findByRole("button", { name: "Fee Form" }));

    expect(
      await screen.findByText(
        "Template does not exist: D:\\Source\\Template\\Testing Fee Evaluation-Even.optimized-v1.xls"
      )
    ).toBeTruthy();
    expect(
      screen.queryByText("Confirm Matrix authority before generating the Fee file.")
    ).toBeNull();
  });
});

function arrangeSuccessfulContext(
  input: {
    folderPath?: string | null;
    pricingDraft?: Record<string, unknown>;
    confirmedFee?: Record<string, unknown>;
    lifecycle?: Record<string, unknown>;
  } = {}
): void {
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
  apiMocks.getProjectLifecycle.mockResolvedValue(
    input.lifecycle ?? lifecycleResponse()
  );
  apiMocks.getFeeEvaluationPricingDraft.mockResolvedValue(
    input.pricingDraft ?? {
      status: "missing",
      current_confirmed_matrix_id: "cmv-1",
      current_confirmed_revision: 1,
      current_fee_rule_version_id: "fee_rules_v2026_06_03",
      saved_draft_edit_id: null,
      payload: null,
    }
  );
  apiMocks.saveFeeEvaluationPricingDraft.mockResolvedValue(currentPricingDraftResponse());
  apiMocks.getConfirmedFeeLatest.mockResolvedValue(
    input.confirmedFee ?? createConfirmedFeeLatest({ status: "missing" })
  );
}

function lifecycleResponse(overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
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
    ...overrides,
  };
}

function currentPricingDraftResponse(
  overrides: Record<string, unknown> = {}
): Record<string, unknown> {
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

function promotedPricingDraftPayload(
  rowOverrides: Record<string, unknown> = {}
): Record<string, unknown> {
  return {
    rows: [
      {
        source_line_id: "cmv-1:g1:row-1:1:0",
        confirmed_group_id: "cmg-1",
        confirmed_row_id: "row-1",
        step_token: "1",
        step_index: 0,
        spend_time: "1",
        unit_price: "10",
        unit_type: "sample",
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

function createConfirmedFeeLatest(input: {
  status: "missing" | "current" | "stale";
  pricingDraftEditId?: string;
  testingFeeTotal?: string;
}): Record<string, unknown> {
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
            pricing_draft_edit_id: input.pricingDraftEditId ?? "fed-1",
            pricing_effective_from: null,
            confirmed_by: "Lab User",
            confirmed_at: "2026-06-10T09:00:00+00:00",
            confirmation_note: null,
            summary: {
              testing_fee_total: input.testingFeeTotal ?? "100.00",
              working_hours: "0.0",
              lab_manpower_cost: "0",
              external_cost: "0",
              grand_cost: input.testingFeeTotal ?? "100.00",
            },
          },
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
        manual_line_items: [createSamplePreparationLine()],
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
            line_id: "cmv-1:g1:row-1",
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
    manual_line_items: [createReportPreparationLine()],
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
        manual_line_items: [
          createSamplePreparationLine({
            line_id: "sample-preparation:g2",
            group_key: "g2",
            group_label: "Group 2",
            confirmed_group_id: "cmg-2",
            units: "3",
          }),
        ],
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

function createDraftWithTwoCalculatedGroups() {
  return {
    ...createDraft(),
    groups: [
      {
        group_key: "g1",
        group_label: "Group 1",
        sample_quantity_expression: "5",
        manual_line_items: [createSamplePreparationLine()],
        line_items: [
          createLine({
            line_id: "g1-calculated",
            test_item: "Group 1 calculated",
            unit_price: "100.00",
            units: "1",
            base_fee: "0.00",
            discount_percent: "0",
            testing_fee: "100.00",
          }),
        ],
      },
      {
        group_key: "g2",
        group_label: "Group 2",
        sample_quantity_expression: "3",
        manual_line_items: [
          createSamplePreparationLine({
            line_id: "sample-preparation:g2",
            group_key: "g2",
            group_label: "Group 2",
            confirmed_group_id: "cmg-2",
            units: "3",
          }),
        ],
        line_items: [
          createLine({
            line_id: "g2-calculated",
            group_key: "g2",
            group_label: "Group 2",
            confirmed_group_id: "cmg-2",
            confirmed_row_id: "row-2",
            test_item: "Group 2 calculated",
            unit_price: "25.00",
            units: "1",
            base_fee: "0.00",
            discount_percent: "0",
            testing_fee: "25.00",
          }),
        ],
      },
    ],
  };
}

function createDraftWithEditableSingleLine() {
  return {
    ...createDraft(),
    groups: [
      {
        group_key: "g1",
        group_label: "Group 1",
        sample_quantity_expression: "5",
        manual_line_items: [createSamplePreparationLine()],
        line_items: [
          createLine({
            line_id: "cmv-1:g1:row-1",
            status: "review_required",
            review_required: true,
            review_reason: "Photo count is not available from Matrix authority.",
            test_item: "Visual Examination",
            matched_rule_name: "Visual Examination",
            matched_rule_id: "fee_rule_visual_exam",
            calculation_strategy: "per_photo",
            unit_label: "photo",
            unit_price: "10.00",
            units: null,
            base_fee: null,
            discount_percent: null,
            testing_fee: null,
          }),
        ],
      },
    ],
  };
}

function createSamplePreparationLine(
  overrides: Partial<FeeEvaluationLineItem> = {}
): FeeEvaluationLineItem {
  return createLine({
    line_id: "sample-preparation:g1",
    confirmed_row_id: "",
    source_row_id: null,
    row_order: 0,
    test_item: "Sample preparation",
    step_tokens: [],
    spend_time: "0.5",
    matched_rule_id: "fee_rule_sample_preparation",
    matched_rule_name: "Sample preparation",
    match_reason: "backend_manual_default",
    calculation_strategy: "per_sample",
    unit_label: "sample",
    unit_price: "50",
    units: "5",
    base_fee: "0",
    discount_percent: "100",
    testing_fee: "0",
    field_metadata: [
      {
        field: "unit_price",
        state: "auto_filled",
        source: "Sample preparation",
        message: null,
      },
    ],
    ...overrides,
  });
}

function createReportPreparationLine(
  overrides: Partial<FeeEvaluationLineItem> = {}
): FeeEvaluationLineItem {
  return createLine({
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
    spend_time: "4",
    matched_rule_id: "fee_rule_report_preparation",
    matched_rule_name: "Report preparation",
    match_reason: "backend_manual_default",
    calculation_strategy: "fixed_per_group",
    unit_label: "report",
    unit_price: "600",
    units: "1",
    base_fee: "0",
    discount_percent: "100",
    testing_fee: "0",
    field_metadata: [
      {
        field: "unit_price",
        state: "auto_filled",
        source: "Report preparation",
        message: null,
      },
    ],
    ...overrides,
  });
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
    spend_time: "",
    unit_label: "group",
    unit_price: "100.00",
    units: "1",
    base_fee: "0.00",
    discount_percent: "0",
    testing_fee: "100.00",
    warnings: [],
  };
}
