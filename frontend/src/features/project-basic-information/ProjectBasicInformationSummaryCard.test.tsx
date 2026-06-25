import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { ProjectBasicInformationResponse } from "../../api/client";
import {
  commitLtrWorkbookBasicInformationSync,
  openLtrWorkbookBasicInformationSyncReadonly,
  previewLtrWorkbookBasicInformationSync,
} from "../../api/client";
import { ProjectBasicInformationSummaryCard } from "./ProjectBasicInformationSummaryCard";

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return {
    ...actual,
    previewLtrWorkbookBasicInformationSync: vi.fn(),
    commitLtrWorkbookBasicInformationSync: vi.fn(),
    openLtrWorkbookBasicInformationSyncReadonly: vi.fn(),
  };
});

const previewLtrWorkbookBasicInformationSyncMock = vi.mocked(
  previewLtrWorkbookBasicInformationSync
);
const commitLtrWorkbookBasicInformationSyncMock = vi.mocked(
  commitLtrWorkbookBasicInformationSync
);
const openLtrWorkbookBasicInformationSyncReadonlyMock = vi.mocked(
  openLtrWorkbookBasicInformationSyncReadonly
);

describe("ProjectBasicInformationSummaryCard", () => {
  beforeEach(() => {
    previewLtrWorkbookBasicInformationSyncMock.mockReset();
    commitLtrWorkbookBasicInformationSyncMock.mockReset();
    openLtrWorkbookBasicInformationSyncReadonlyMock.mockReset();
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

    expect(screen.getByLabelText("LTR Information")).toBeTruthy();
    expect(screen.queryByText("LTR Information")).toBeNull();
    expect(screen.getByText("Unconfirmed")).toBeTruthy();
    expect(screen.getByText("Confirm from Basic Information")).toBeTruthy();
    expect(screen.getByText("Project Leader")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Edit" })).toBeNull();
    expect(screen.getByRole("button", { name: "LTR update preview" }).hasAttribute("disabled")).toBe(true);
  });

  it("renders an on-demand confirmed LTR workbook update entry", () => {
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
    expect(summaryLabels).toEqual([]);
    expect(screen.queryByText("In progress")).toBeNull();
    expect(screen.queryByText("1630.00")).toBeNull();
    expect(screen.queryByText("DL")).toBeNull();
    expect(screen.queryByText("Description P/N")).toBeNull();
    expect(screen.queryByText("Test Item")).toBeNull();
    expect(screen.queryByRole("button", { name: "View" })).toBeNull();
    expect(screen.getByRole("button", { name: "LTR update preview" }).hasAttribute("disabled")).toBe(false);
  });

  it("does not render empty LTR summary placeholders before preview", () => {
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

    expect(screen.queryByText("Failed item")).toBeNull();
    expect(screen.queryByText("-")).toBeNull();
  });

  it("does not render controlled defaults before preview", () => {
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

    expect(screen.queryByText("Test Result")).toBeNull();
    expect(screen.queryByText("OK")).toBeNull();
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
    expect(screen.getByRole("button", { name: "LTR update preview" }).hasAttribute("disabled")).toBe(true);
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
          changed: false,
        },
        {
          field_name: "description_pn",
          label: "Description P/N",
          current_value: "Old P/N",
          pending_value: "Coolpower HDF 3.40mm pin",
          changed: true,
        },
        {
          field_name: "test_item",
          label: "Test Item",
          current_value: "Old testing",
          pending_value: "Qualification Testing",
          changed: true,
        },
        {
          field_name: "test_type_in_sheet",
          label: "Test Type",
          current_value: "Old type",
          pending_value: "Partial Qualification",
          changed: true,
        },
        {
          field_name: "requested_by",
          label: "Requested by",
          current_value: "Old requester",
          pending_value: "MP Cao",
          changed: true,
        },
        {
          field_name: "location",
          label: "Location",
          current_value: "Suzhou",
          pending_value: "Dongguan",
          changed: true,
        },
        {
          field_name: "project_leader",
          label: "Project Leader",
          current_value: "Old leader",
          pending_value: "Even Yang",
          changed: true,
        },
        {
          field_name: "test_result",
          label: "Test Result",
          current_value: "In progress",
          pending_value: "OK",
          changed: true,
        },
        {
          field_name: "failed_item",
          label: "Failed item",
          current_value: "Old failed item",
          pending_value: "None",
          changed: true,
        },
        {
          field_name: "sample_deposition",
          label: "Sample deposition",
          current_value: "Old sample deposition",
          pending_value: "Send Back",
          changed: true,
        },
        {
          field_name: "sub_contract",
          label: "Sub-contract",
          current_value: "Yes",
          pending_value: "No",
          changed: true,
        },
        {
          field_name: "test_fee",
          label: "Test Fee",
          current_value: "1200",
          pending_value: "12531",
          changed: true,
        },
        {
          field_name: "remarks_po",
          label: "Remarks (PO)",
          current_value: "Old PO",
          pending_value: "PO-123",
          changed: true,
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
    openLtrWorkbookBasicInformationSyncReadonlyMock.mockResolvedValue({
      project_id: "P1",
      ltr_number: "DL-2026-05-011",
      workbook_path: "P:\\LTR\\LTR.xlsx",
      sheet_name: "2026",
      row_number: 42,
      column_number: 4,
      selected_cell: "D42",
      message: "LTR workbook opened read-only at D42.",
    });

    const { container } = render(
      <ProjectBasicInformationSummaryCard
        projectId="P1"
        basicInformation={response("confirmed", confirmedRecord())}
        loading={false}
        error={null}
      />
    );

    await user.click(screen.getByRole("button", { name: "LTR update preview" }));

    expect(previewLtrWorkbookBasicInformationSyncMock).toHaveBeenCalledWith("P1");
    expect(await screen.findByText("DL-2026-05-011")).toBeTruthy();
    expect(screen.queryByText("LTR workbook update preview")).toBeNull();
    const previewHeading = container.querySelector(".runtime-console-ltr-sync-heading");
    expect(previewHeading?.textContent).toContain("DL-2026-05-011");
    expect(screen.getByText("P:\\LTR\\LTR.xlsx")).toBeTruthy();
    expect(screen.queryByText("2026 row 42")).toBeNull();
    const contextLabels = Array.from(
      container.querySelectorAll(".runtime-console-ltr-sync-context dt")
    ).map((item) => item.textContent);
    expect(contextLabels).toEqual(["Open read-only workbook"]);
    await user.click(screen.getByRole("button", { name: "Open read-only workbook" }));
    expect(openLtrWorkbookBasicInformationSyncReadonlyMock).toHaveBeenCalledWith("P1");
    expect(
      screen.queryByText("Review the current LTR workbook row before updating it.")
    ).toBeNull();
    expect(screen.getByText("LTR workbook")).toBeTruthy();
    expect(screen.getByText("LTR of Basic Info")).toBeTruthy();
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
    expect(screen.getAllByText("Test Result").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("In progress").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("OK")).toBeTruthy();
    expect(screen.getByText("1200")).toBeTruthy();
    expect(screen.getByText("12531")).toBeTruthy();
    expect(container.querySelectorAll(".runtime-console-ltr-sync-comparison tbody tr.is-changed").length).toBe(12);

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

    await user.click(screen.getByRole("button", { name: "LTR update preview" }));

    expect(await screen.findByText("DL-2026-05-011")).toBeTruthy();
    expect(screen.queryByText("LTR workbook update is blocked")).toBeNull();
    expect(screen.getByText("The registered LTR row was not found in the configured workbook.")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Confirm update" })).toBeNull();
  });

  it("disables commit when the LTR workbook already matches Basic Information", async () => {
    const user = userEvent.setup();
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
          current_value: "OK",
          pending_value: "OK",
          changed: false,
        },
      ],
      confirmed_basic_information_version: 1,
      confirmed_basic_information_source_signature_hash: "hash-1",
      blockers: [],
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

    await user.click(screen.getByRole("button", { name: "LTR update preview" }));

    expect(await screen.findByText("LTR workbook")).toBeTruthy();
    expect(screen.queryByText("LTR workbook is already up to date.")).toBeNull();
    expect(screen.getByRole("button", { name: "Confirm update" }).hasAttribute("disabled")).toBe(true);
    expect(commitLtrWorkbookBasicInformationSyncMock).not.toHaveBeenCalled();
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

    await user.click(screen.getByRole("button", { name: "LTR update preview" }));

    expect(
      await screen.findByText(
        "The LTR workbook cannot be opened safely. Close Excel copies of the workbook and retry."
      )
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
          changed: true,
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

    await user.click(screen.getByRole("button", { name: "LTR update preview" }));
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
