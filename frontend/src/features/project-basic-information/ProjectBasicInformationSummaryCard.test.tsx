import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ProjectBasicInformationResponse } from "../../api/client";
import {
  commitLtrWorkbookBasicInformationSync,
  previewLtrWorkbookBasicInformationSync,
} from "../../api/client";
import { ProjectBasicInformationSummaryCard } from "./ProjectBasicInformationSummaryCard";

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return {
    ...actual,
    previewLtrWorkbookBasicInformationSync: vi.fn(),
    commitLtrWorkbookBasicInformationSync: vi.fn(),
  };
});

const previewLtrWorkbookBasicInformationSyncMock = vi.mocked(
  previewLtrWorkbookBasicInformationSync
);
const commitLtrWorkbookBasicInformationSyncMock = vi.mocked(
  commitLtrWorkbookBasicInformationSync
);

describe("ProjectBasicInformationSummaryCard", () => {
  beforeEach(() => {
    previewLtrWorkbookBasicInformationSyncMock.mockReset();
    commitLtrWorkbookBasicInformationSyncMock.mockReset();
  });

  it("shows unconfirmed state without an inline edit action", () => {
    render(
      <ProjectBasicInformationSummaryCard
        projectId="P1"
        basicInformation={response("unconfirmed", null, ["Project Leader"])}
        loading={false}
        error={null}
      />
    );

    expect(screen.getByText("LTR Information")).toBeTruthy();
    expect(screen.getByText("Unconfirmed")).toBeTruthy();
    expect(screen.getByText("Confirm from Basic Information")).toBeTruthy();
    expect(screen.getByText("Project Leader")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Edit" })).toBeNull();
    expect(screen.getByRole("button", { name: "Update LTR" }).hasAttribute("disabled")).toBe(true);
  });

  it("renders compact confirmed LTR summary fields in workbench priority order", async () => {
    const user = userEvent.setup();
    const { container } = render(
      <ProjectBasicInformationSummaryCard
        projectId="P1"
        basicInformation={response("confirmed", confirmedRecord())}
        loading={false}
        error={null}
      />
    );

    const summaryLabels = Array.from(
      container.querySelectorAll(".runtime-console-basic-information-list.is-summary dt")
    ).map((item) => item.textContent);

    expect(screen.queryByText("Confirmed")).toBeNull();
    expect(summaryLabels).toEqual([
      "Test Result",
      "Test Fee",
      "Sub-contract",
      "Remarks (PO)",
      "Location",
      "Sample deposition",
      "Project Type",
      "Test Type in sheet",
      "Requested by",
      "Project Leader",
      "Failed item",
    ]);
    expect(screen.getByText("In progress")).toBeTruthy();
    expect(screen.getByText("1630.00")).toBeTruthy();
    expect(screen.getByText("Yes")).toBeTruthy();
    expect(screen.getByText("PO-123")).toBeTruthy();
    expect(screen.getByText("Dongguan")).toBeTruthy();
    expect(screen.getByText("Send Back")).toBeTruthy();
    expect(screen.getByText("NPD")).toBeTruthy();
    expect(screen.getByText("Qualification")).toBeTruthy();
    expect(screen.getByText("MP Cao")).toBeTruthy();
    expect(screen.getByText("Even Yang")).toBeTruthy();
    expect(screen.getByText("None")).toBeTruthy();
    expect(screen.queryByText("DL")).toBeNull();
    expect(screen.queryByText("Description P/N")).toBeNull();
    expect(screen.queryByText("Test Item")).toBeNull();
    expect(screen.getByRole("button", { name: "Update LTR" }).hasAttribute("disabled")).toBe(false);

    await user.click(screen.getByRole("button", { name: "View" }));

    expect(screen.getByText("All confirmed fields")).toBeTruthy();
    expect(screen.getByText("DL-2026-05-011")).toBeTruthy();
    expect(screen.getByText("Coolpower HDF")).toBeTruthy();
    expect(screen.getByText("Qualification Testing")).toBeTruthy();
  });

  it("keeps empty workbench priority fields visible", () => {
    render(
      <ProjectBasicInformationSummaryCard
        projectId="P1"
        basicInformation={response("confirmed", {
          ...confirmedRecord(),
          values: {
            ...confirmedRecord().values,
            failed_item: "",
          },
        })}
        loading={false}
        error={null}
      />
    );

    expect(screen.getByText("Failed item")).toBeTruthy();
    expect(screen.getByText("-")).toBeTruthy();
  });

  it("uses controlled field defaults for older confirmed workbench summaries", () => {
    const values = Object.fromEntries(
      Object.entries(confirmedRecord().values).filter(([key]) => key !== "test_result")
    );
    render(
      <ProjectBasicInformationSummaryCard
        projectId="P1"
        basicInformation={response("confirmed", {
          ...confirmedRecord(),
          values,
        })}
        loading={false}
        error={null}
      />
    );

    expect(screen.getByText("Test Result")).toBeTruthy();
    expect(screen.getByText("OK")).toBeTruthy();
  });

  it("shows needs-review state and changed field count", () => {
    render(
      <ProjectBasicInformationSummaryCard
        projectId="P1"
        basicInformation={response("needs_review", confirmedRecord(), [], ["requested_by"])}
        loading={false}
        error={null}
      />
    );

    expect(screen.getByText("Needs review")).toBeTruthy();
    expect(screen.getByText("1 source field changed")).toBeTruthy();
    expect(screen.getByText("Confirm from Basic Information")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Update LTR" }).hasAttribute("disabled")).toBe(true);
  });

  it("previews and commits the confirmed Basic Information LTR workbook update", async () => {
    const user = userEvent.setup();
    previewLtrWorkbookBasicInformationSyncMock.mockResolvedValue({
      status: "ready",
      project_id: "P1",
      ltr_number: "DL-2026-05-011",
      workbook_path: "P:\\LTR\\LTR.xlsx",
      target_sheet: "2026",
      target_row: 42,
      columns: [
        { column: "J", field_name: "Test Result", value: "OK" },
        { column: "P", field_name: "Test Fee", value: "12531" },
      ],
      comparison_values: [
        {
          field_name: "project_type",
          label: "Project Type",
          current_value: "NPD",
          pending_value: "NPD",
        },
        {
          field_name: "description_pn",
          label: "Description P/N",
          current_value: "Old P/N",
          pending_value: "Coolpower HDF 3.40mm pin",
        },
        {
          field_name: "test_item",
          label: "Test Item",
          current_value: "Old testing",
          pending_value: "Qualification Testing",
        },
        {
          field_name: "test_type_in_sheet",
          label: "Test Type",
          current_value: "Old type",
          pending_value: "Partial Qualification",
        },
        {
          field_name: "requested_by",
          label: "Requested by",
          current_value: "Old requester",
          pending_value: "MP Cao",
        },
        {
          field_name: "location",
          label: "Location",
          current_value: "Suzhou",
          pending_value: "Dongguan",
        },
        {
          field_name: "project_leader",
          label: "Project Leader",
          current_value: "Old leader",
          pending_value: "Even Yang",
        },
        {
          field_name: "test_result",
          label: "Test Result",
          current_value: "In progress",
          pending_value: "OK",
        },
        {
          field_name: "failed_item",
          label: "Failed item",
          current_value: "Old failed item",
          pending_value: "None",
        },
        {
          field_name: "sample_deposition",
          label: "Sample deposition",
          current_value: "Old sample deposition",
          pending_value: "Send Back",
        },
        {
          field_name: "sub_contract",
          label: "Sub-contract",
          current_value: "Yes",
          pending_value: "No",
        },
        {
          field_name: "test_fee",
          label: "Test Fee",
          current_value: "1200",
          pending_value: "12531",
        },
        {
          field_name: "remarks_po",
          label: "Remarks (PO)",
          current_value: "Old PO",
          pending_value: "PO-123",
        },
      ],
      confirmed_basic_information_version: 1,
      confirmed_basic_information_source_signature_hash: "hash-1",
      blockers: [],
      warnings: [],
    });
    commitLtrWorkbookBasicInformationSyncMock.mockResolvedValue({
      project_id: "P1",
      ltr_number: "DL-2026-05-011",
      workbook_path: "P:\\LTR\\LTR.xlsx",
      backup_path: "P:\\LTR\\LTR.xlsx.bak",
      sheet_name: "2026",
      row_number: 42,
      confirmed_basic_information_version: 1,
      confirmed_basic_information_source_signature_hash: "hash-1",
    });

    const { container } = render(
      <ProjectBasicInformationSummaryCard
        projectId="P1"
        basicInformation={response("confirmed", confirmedRecord())}
        loading={false}
        error={null}
      />
    );

    await user.click(screen.getByRole("button", { name: "Update LTR" }));

    expect(previewLtrWorkbookBasicInformationSyncMock).toHaveBeenCalledWith("P1");
    expect(await screen.findByText("LTR workbook update preview")).toBeTruthy();
    const previewHeading = container.querySelector(".runtime-console-ltr-sync-heading");
    expect(previewHeading?.textContent).toContain("LTR workbook update preview");
    expect(previewHeading?.textContent).toContain("DL-2026-05-011");
    expect(screen.getByText("P:\\LTR\\LTR.xlsx")).toBeTruthy();
    expect(screen.getByText("2026 row 42")).toBeTruthy();
    const contextLabels = Array.from(
      container.querySelectorAll(".runtime-console-ltr-sync-context dt")
    ).map((item) => item.textContent);
    expect(contextLabels).toEqual(["Workbook", "Target row"]);
    expect(
      screen.queryByText("Review the current LTR workbook row before updating it.")
    ).toBeNull();
    expect(screen.getByText("Current LTR workbook")).toBeTruthy();
    expect(screen.getByText("Value to write")).toBeTruthy();
    const previewFields = Array.from(
      container.querySelectorAll(".runtime-console-ltr-sync-comparison tbody th")
    ).map((item) => item.textContent);
    expect(previewFields).toEqual([
      "Project Type",
      "Description P/N",
      "Test Item",
      "Test Type",
      "Requested by",
      "Location",
      "Project Leader",
      "Test Result",
      "Failed item",
      "Sample deposition",
      "Sub-contract",
      "Test Fee",
      "Remarks (PO)",
    ]);
    expect(screen.getAllByText("Description P/N").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Test Item").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("Test Result").length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("In progress").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("OK")).toBeTruthy();
    expect(screen.getByText("1200")).toBeTruthy();
    expect(screen.getByText("12531")).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Confirm update" }));

    expect(commitLtrWorkbookBasicInformationSyncMock).toHaveBeenCalledWith("P1", {
      operator_confirmed: true,
      preview_acknowledged: true,
      expected_confirmed_basic_information_version: 1,
      expected_confirmed_basic_information_source_signature_hash: "hash-1",
    });
    expect(
      await screen.findByText("LTR workbook updated: 2026 row 42. Backup retained automatically.")
    ).toBeTruthy();
    expect(screen.queryByText("Backup: P:\\LTR\\LTR.xlsx.bak")).toBeNull();
    expect(screen.queryByText("P:\\LTR\\LTR.xlsx.bak")).toBeNull();
  });

  it("shows blocked LTR preview without a commit action", async () => {
    const user = userEvent.setup();
    previewLtrWorkbookBasicInformationSyncMock.mockResolvedValue({
      status: "blocked",
      project_id: "P1",
      ltr_number: "DL-2026-05-011",
      workbook_path: "P:\\LTR\\LTR.xlsx",
      target_sheet: null,
      target_row: null,
      columns: [],
      comparison_values: [],
      confirmed_basic_information_version: 1,
      confirmed_basic_information_source_signature_hash: "hash-1",
      blockers: ["The registered LTR row was not found in the configured workbook."],
      warnings: [],
    });

    render(
      <ProjectBasicInformationSummaryCard
        projectId="P1"
        basicInformation={response("confirmed", confirmedRecord())}
        loading={false}
        error={null}
      />
    );

    await user.click(screen.getByRole("button", { name: "Update LTR" }));

    expect(await screen.findByText("LTR workbook update is blocked")).toBeTruthy();
    expect(screen.getByText("The registered LTR row was not found in the configured workbook.")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Confirm update" })).toBeNull();
  });

  it("maps workbook lock and stale preview errors to operator copy", async () => {
    const user = userEvent.setup();
    previewLtrWorkbookBasicInformationSyncMock.mockRejectedValue(
      new Error("Permission denied: workbook is locked")
    );

    render(
      <ProjectBasicInformationSummaryCard
        projectId="P1"
        basicInformation={response("confirmed", confirmedRecord())}
        loading={false}
        error={null}
      />
    );

    await user.click(screen.getByRole("button", { name: "Update LTR" }));

    expect(
      await screen.findByText("The LTR workbook appears to be open or locked. Close it and retry.")
    ).toBeTruthy();

    previewLtrWorkbookBasicInformationSyncMock.mockResolvedValue({
      status: "ready",
      project_id: "P1",
      ltr_number: "DL-2026-05-011",
      workbook_path: "P:\\LTR\\LTR.xlsx",
      target_sheet: "2026",
      target_row: 42,
      columns: [{ column: "J", field_name: "Test Result", value: "OK" }],
      comparison_values: [
        {
          field_name: "test_result",
          label: "Test Result",
          current_value: "In progress",
          pending_value: "OK",
        },
      ],
      confirmed_basic_information_version: 1,
      confirmed_basic_information_source_signature_hash: "hash-1",
      blockers: [],
      warnings: [],
    });
    commitLtrWorkbookBasicInformationSyncMock.mockRejectedValue(
      new Error("Basic Information changed after preview")
    );

    await user.click(screen.getByRole("button", { name: "Update LTR" }));
    await user.click(await screen.findByRole("button", { name: "Confirm update" }));

    expect(
      await screen.findByText("Basic Information changed after preview. Refresh before updating LTR.")
    ).toBeTruthy();
  });
});

function response(
  status: ProjectBasicInformationResponse["status"],
  latestConfirmed: ProjectBasicInformationResponse["latest_confirmed"],
  missingLabels: string[] = [],
  changedFields: string[] = []
): ProjectBasicInformationResponse {
  const values = confirmedRecord().values;
  return {
    project_id: "P1",
    status,
    draft: { values },
    latest_confirmed: latestConfirmed,
    field_suggestions: {},
    changed_source_fields: changedFields,
    missing_required_fields: missingLabels.map((label) => label.toLowerCase()),
    missing_required_labels: missingLabels,
    blockers: [],
    warnings: [],
  };
}

function confirmedRecord(): NonNullable<ProjectBasicInformationResponse["latest_confirmed"]> {
  return {
    record_id: "BASIC-1",
    project_id: "P1",
    status: "confirmed",
    version: 1,
    values: {
      dl_number: "DL-2026-05-011",
      project_type: "NPD",
      product_description: "Coolpower HDF",
      description_pn: "HDF-34",
      test_item: "Qualification Testing",
      test_type: "Product/Process Qualification",
      test_type_in_sheet: "Qualification",
      requested_by: "MP Cao",
      location: "Dongguan",
      project_leader: "Even Yang",
      lab_performing_tests: "Dongguan",
      test_result: "In progress",
      failed_item: "None",
      sample_deposition: "Send Back",
      sub_contract: "Yes",
      test_fee: "1630.00",
      remarks_po: "PO-123",
    },
    source_signature: "{}",
    created_at: "2026-06-20T09:00:00+00:00",
    updated_at: "2026-06-20T09:00:00+00:00",
    confirmed_at: "2026-06-20T09:00:00+00:00",
    confirmed_by: "Lab User",
  };
}
