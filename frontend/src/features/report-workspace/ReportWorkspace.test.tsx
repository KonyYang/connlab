import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { ReportWorkspace } from "./ReportWorkspace";

vi.mock("../../api/client", async () => {
  const actual = await vi.importActual<typeof import("../../api/client")>("../../api/client");
  return {
    ...actual,
    fetchReportWorkspace: vi.fn(),
    fetchCurrentReport: vi.fn(),
    fetchCurrentCustomerReport: vi.fn(),
    inspectLlcrResultWorkbook: vi.fn(),
    confirmLlcrResultImport: vi.fn(),
    generateInitialReportRevision: vi.fn(),
    previewCurrentReportLlcrUpdate: vi.fn(),
    updateCurrentReportLlcr: vi.fn(),
    previewCurrentReportEquipmentList: vi.fn(),
    updateCurrentReportEquipmentList: vi.fn(),
    publishManagedReport: vi.fn(),
    downloadCurrentReport: vi.fn(),
    generateCurrentCustomerReport: vi.fn(),
    downloadCurrentCustomerReport: vi.fn(),
    cancelLlcrResultPreview: vi.fn(),
  };
});

const state: api.ReportWorkspaceState = {
  project_id: "project-1",
  basic_information_status: "confirmed",
  confirmed_basic_information_version: 2,
  active_confirmed_matrix_id: "matrix-1",
  active_confirmed_matrix_revision: 4,
  latest_report_revision: null,
  datasets: [],
  report_revisions: [],
};

const currentReport: api.CurrentReport = {
  status: "ready",
  mode: "official",
  file_name: "DL-001 Qualification Testing Report_Rev_A.docx",
  file_sha256: "a".repeat(64),
  report_revision_id: null,
  folder_path: "D:\\Test Project\\DL-001\\Official Test",
  official_folder_path: "D:\\Test Project\\DL-001\\Official Test",
  can_publish_to_official: false,
  download_url: "/api/projects/project-1/report-workspace/current-report/download",
};

const customerReport: api.CustomerReportState = {
  project_id: "project-1",
  status: "stale",
  mode: "official",
  file_name: "DL-001-CR Qualification Testing Report_Rev_A.docx",
  file_sha256: "b".repeat(64),
  internal_report_sha256: "a".repeat(64),
  generated_from_internal_sha256: "c".repeat(64),
  can_generate: true,
  blockers: [],
  warnings: ["The current Internal Report changed after this customer report was generated."],
  download_url: "/api/projects/project-1/report-workspace/current-customer-report/download",
};

const preview: api.LlcrImportPreview = {
  preview_id: "preview-1",
  project_id: "project-1",
  confirmed_matrix_id: "matrix-1",
  confirmed_matrix_revision: 4,
  source: { file_name: "LLCR.xlsx", sha256: "sha", size_bytes: 500 },
  parser_profile_version: "connlab-llcr-v1",
  detected_sheets: ["Summary", "P"],
  can_confirm: true,
  sample_count: 6,
  test_point_count: 24,
  result_count: 1,
  diagnostics: [],
  entries: [
    {
      result_id: "result-1",
      group_label: "1",
      matrix_step_token: "2",
      stage: "initial",
      stage_label: "Initial",
      requirement: "≤ 0.198 mΩ",
      unit: "mΩ",
      measurement_count: 24,
      summary_min: "0.031",
      summary_max: "0.082",
      summary_average: "0.0565",
      provisional_outcome: "pass",
      confirmed_outcome: null,
      override_reason: null,
      source_range: "P!B10:Y10",
      report_target: "Group 1 / Step 2",
    },
  ],
};

const equipmentPreview: api.EquipmentListPreview = {
  project_id: "project-1",
  status: "ready",
  current_report: currentReport,
  source_file_name: "EquipmentID.docx",
  source_sha256: "b".repeat(64),
  catalog_file_name: "equipment.xlsx",
  catalog_sha256: "c".repeat(64),
  rows: [
    {
      source_reference: "DG-Q-0033",
      status: "matched",
      item: "Digital multimeter",
      manufacturer: "Keysight",
      id_number: "DG-Q-0033",
      last_calibration: "01 Jan 2025",
      calibration_due: "01 Jan 2026",
      source_sheet: "All Equip.",
      expired: true,
      external_reason: null,
    },
  ],
  blockers: [],
  warnings: ["Calibration is expired for DG-Q-0033 (01 Jan 2026)."],
  requires_expired_acknowledgement: true,
};

describe("ReportWorkspace", () => {
  beforeEach(() => {
    Object.defineProperty(URL, "createObjectURL", {
      configurable: true,
      value: vi.fn(() => "blob:customer-report"),
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      configurable: true,
      value: vi.fn(),
    });
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
    vi.mocked(api.fetchReportWorkspace).mockResolvedValue(state);
    vi.mocked(api.fetchCurrentReport).mockResolvedValue(currentReport);
    vi.mocked(api.fetchCurrentCustomerReport).mockResolvedValue(customerReport);
    vi.mocked(api.inspectLlcrResultWorkbook).mockResolvedValue(preview);
    vi.mocked(api.previewCurrentReportEquipmentList).mockResolvedValue(equipmentPreview);
    vi.mocked(api.updateCurrentReportEquipmentList).mockResolvedValue({
      project_id: "project-1",
      file_name: currentReport.file_name!,
      mode: "official",
      changed: true,
      current_sha256: "d".repeat(64),
      archive_path: "C:\\Project\\History\\Report\\old.docx",
      updated_by: "Lab User",
    });
    vi.mocked(api.confirmLlcrResultImport).mockResolvedValue({
      dataset_id: "dataset-1",
      dataset_type: "llcr",
      revision: 1,
      project_id: "project-1",
      confirmed_matrix_id: "matrix-1",
      confirmed_matrix_revision: 4,
      source_file_name: "LLCR.xlsx",
      source_sha256: "sha",
      parser_profile_version: "connlab-llcr-v1",
      validation_status: "confirmed",
      confirmed_at: "2026-08-29T09:00:00Z",
      confirmed_by: "Lab User",
      entries: [{ ...preview.entries[0], confirmed_outcome: "pass" }],
    });
  });

  it("shows an explicit loading state while workspace authority is loading", () => {
    vi.mocked(api.fetchReportWorkspace).mockReturnValue(new Promise(() => undefined));

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);

    expect(screen.getByRole("status").textContent).toContain("Loading Report Workspace...");
  });

  it("exposes the current report, LLCR import preview, and confirmation", async () => {
    const user = userEvent.setup();
    const onBack = vi.fn();
    render(<ReportWorkspace projectId="project-1" onBack={onBack} />);

    expect(await screen.findByRole("heading", { name: "Report Workspace" })).toBeTruthy();
    expect(screen.getByText("Project project-1")).toBeTruthy();
    expect(screen.getAllByText(currentReport.file_name!).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Confirmed Matrix revision 4")).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Current report ready" })).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Generate initial report" })).toBeNull();

    const fileInput = screen.getByLabelText("LLCR result workbook");
    fireEvent.change(fileInput, {
      target: { files: [new File(["xlsx"], "LLCR.xlsx")] },
    });
    await user.click(screen.getByRole("button", { name: "Inspect LLCR workbook" }));

    expect(await screen.findByRole("dialog", { name: "LLCR import preview" })).toBeTruthy();
    expect(screen.getByText("Group 1 / Step 2")).toBeTruthy();
    expect(screen.getByText("0.031 / 0.082 / 0.0565 mΩ")).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Confirm LLCR dataset" }));
    await waitFor(() => expect(api.confirmLlcrResultImport).toHaveBeenCalledTimes(1));
    expect(api.confirmLlcrResultImport).toHaveBeenCalledWith(
      "project-1",
      expect.objectContaining({
        preview_id: "preview-1",
        decisions: [{ result_id: "result-1", outcome: "pass", override_reason: null }],
      })
    );
  });

  it("enables initial generation only when no current report exists", async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchCurrentReport).mockResolvedValue({
      status: "missing",
      mode: null,
      file_name: null,
      file_sha256: null,
      report_revision_id: null,
      folder_path: null,
      official_folder_path: null,
      can_publish_to_official: false,
      download_url: null,
    });
    vi.mocked(api.generateInitialReportRevision).mockResolvedValue({
      report_revision_id: "report-revision-1",
      revision: 1,
      file_name: "DL-001 Qualification Testing Report_Rev_A.docx",
      file_sha256: "b".repeat(64),
      size_bytes: 1024,
      confirmed_matrix_id: "matrix-1",
      result_dataset_id: null,
      base_report_revision_id: null,
      created_at: "2026-08-30T09:00:00Z",
      created_by: "Lab User",
      download_url: "/api/projects/project-1/report-workspace/revisions/report-revision-1/download",
    });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);

    const generateButton = await screen.findByRole("button", { name: "Generate initial report" });
    expect(generateButton).toHaveProperty("disabled", false);
    await user.click(generateButton);

    expect(api.generateInitialReportRevision).toHaveBeenCalledWith("project-1");
  });

  it("blocks an outcome override until a reason is supplied", async () => {
    const user = userEvent.setup();
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("heading", { name: "Report Workspace" });
    fireEvent.change(screen.getByLabelText("LLCR result workbook"), {
      target: { files: [new File(["xlsx"], "LLCR.xlsx")] },
    });
    await user.click(screen.getByRole("button", { name: "Inspect LLCR workbook" }));
    await user.selectOptions(await screen.findByLabelText("Final outcome for Group 1 / Step 2"), "fail");

    expect(screen.getByRole("button", { name: "Confirm LLCR dataset" })).toHaveProperty("disabled", true);
    await user.type(screen.getByLabelText("Override reason for Group 1 / Step 2"), "Visual damage");
    expect(screen.getByRole("button", { name: "Confirm LLCR dataset" })).toHaveProperty("disabled", false);
  });

  it("cancels the staged preview before closing the dialog", async () => {
    const user = userEvent.setup();
    vi.mocked(api.cancelLlcrResultPreview).mockResolvedValue(undefined);
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await screen.findByRole("heading", { name: "Report Workspace" });
    fireEvent.change(screen.getByLabelText("LLCR result workbook"), {
      target: { files: [new File(["xlsx"], "LLCR.xlsx")] },
    });
    await user.click(screen.getByRole("button", { name: "Inspect LLCR workbook" }));
    await user.click(await screen.findByRole("button", { name: /^Cancel$/ }));

    await waitFor(() => expect(api.cancelLlcrResultPreview).toHaveBeenCalledWith(
      "project-1",
      "preview-1"
    ));
    expect(screen.queryByRole("dialog", { name: "LLCR import preview" })).toBeNull();
  });

  it("updates only the LLCR region of the current report without selecting a revision", async () => {
    const user = userEvent.setup();
    const dataset = {
      dataset_id: "dataset-1",
      dataset_type: "llcr" as const,
      revision: 1,
      project_id: "project-1",
      confirmed_matrix_id: "matrix-1",
      confirmed_matrix_revision: 4,
      source_file_name: "LLCR.xlsx",
      source_sha256: "sha",
      parser_profile_version: "connlab-llcr-v1",
      validation_status: "confirmed",
      confirmed_at: "2026-08-29T09:00:00Z",
      confirmed_by: "Lab User",
      entries: [{ ...preview.entries[0], confirmed_outcome: "pass" as const }],
    };
    vi.mocked(api.fetchReportWorkspace).mockResolvedValue({
      ...state,
      datasets: [dataset],
    });
    vi.mocked(api.previewCurrentReportLlcrUpdate).mockResolvedValue({
      project_id: "project-1",
      dataset_id: "dataset-1",
      status: "ready",
      current_report: currentReport,
      blockers: [],
      warnings: [],
    });
    vi.mocked(api.updateCurrentReportLlcr).mockResolvedValue({
      project_id: "project-1",
      dataset_id: "dataset-1",
      file_name: currentReport.file_name!,
      mode: "official",
      changed: true,
      current_sha256: "b".repeat(64),
      archive_path: "C:\\Project\\History\\Report\\old.docx",
      updated_by: "Lab User",
    });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    expect(
      await screen.findByText("LLCR Result and Comment cells and Appendix A")
    ).toBeTruthy();
    await user.click(await screen.findByRole("button", { name: "Update LLCR results" }));

    expect(api.previewCurrentReportLlcrUpdate).toHaveBeenCalledWith(
      "project-1",
      "dataset-1"
    );
    expect(api.updateCurrentReportLlcr).toHaveBeenCalledWith("project-1", {
      dataset_id: "dataset-1",
      expected_report_sha256: "a".repeat(64),
      updated_by: "Lab User",
    });
    expect(await screen.findByText(/Updated LLCR results in/)).toBeTruthy();
    expect(screen.queryByText("Report draft history")).toBeNull();
  });

  it("publishes the current managed draft to the official project folder explicitly", async () => {
    const user = userEvent.setup();
    const managed: api.CurrentReport = {
      ...currentReport,
      mode: "managed_draft",
      file_name: "DL-001 Qualification Testing Report_Rev_A_Draft (9).docx",
      folder_path: "D:\\PythonProject\\connlab\\data\\generated_test_reports\\project-1",
      official_folder_path: "D:\\Test Project\\DL-001\\Official Test",
      can_publish_to_official: true,
    };
    vi.mocked(api.fetchCurrentReport).mockResolvedValue(managed);
    vi.mocked(api.publishManagedReport).mockResolvedValue({
      ...currentReport,
      file_name: "DL-001 Qualification Testing Report_Rev_A.docx",
    });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);

    expect(await screen.findByRole("heading", { name: "Publish current report" })).toBeTruthy();
    expect((await screen.findAllByText("ConnLab managed draft")).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Destination: Official project folder")).toBeTruthy();
    await user.click(
      screen.getByRole("button", { name: "Publish current draft to project folder" })
    );

    expect(api.publishManagedReport).toHaveBeenCalledWith(
      "project-1",
      "a".repeat(64)
    );
    expect(await screen.findByText(/Published the current report to/)).toBeTruthy();
  });

  it("previews EquipmentID matches and requires expired-calibration acknowledgement", async () => {
    const user = userEvent.setup();
    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);

    await user.click(await screen.findByRole("button", { name: "Preview Equipment List" }));

    expect(await screen.findByRole("dialog", { name: "Equipment List preview" })).toBeTruthy();
    expect(screen.getByText("Digital multimeter")).toBeTruthy();
    const updateButton = screen.getByRole("button", { name: "Update Equipment List" });
    expect(updateButton).toHaveProperty("disabled", true);
    await user.click(screen.getByLabelText("I reviewed the expired calibration warning"));
    expect(updateButton).toHaveProperty("disabled", false);
    await user.click(updateButton);

    expect(api.updateCurrentReportEquipmentList).toHaveBeenCalledWith("project-1", {
      expected_report_sha256: "a".repeat(64),
      expected_source_sha256: "b".repeat(64),
      expected_catalog_sha256: "c".repeat(64),
      acknowledge_expired: true,
      external_overrides: [],
      updated_by: "Lab User",
    });
    expect(await screen.findByText(/Updated Equipment List in/)).toBeTruthy();
  });

  it("allows an unmatched device to continue as an ID-only Word-manual row", async () => {
    const user = userEvent.setup();
    const unmatchedPreview: api.EquipmentListPreview = {
      ...equipmentPreview,
      requires_expired_acknowledgement: false,
      warnings: [
        "Equipment reference 'DG-Q-0851' was not found. It will be added with ID only; complete it manually in Word.",
      ],
      rows: [{
        source_reference: "DG-Q-0851",
        status: "unmatched",
        item: "",
        manufacturer: "",
        id_number: "DG-Q-0851",
        last_calibration: "",
        calibration_due: "",
        source_sheet: null,
        expired: false,
        external_reason: null,
      }],
    };
    vi.mocked(api.previewCurrentReportEquipmentList).mockResolvedValue(unmatchedPreview);

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Preview Equipment List" }));

    expect(await screen.findByText(/Rows needing attention keep only confirmed values/)).toBeTruthy();
    await user.type(screen.getByLabelText("Item for DG-Q-0851"), "Thermal shock chamber");
    await user.click(screen.getByRole("button", { name: "Recheck external entries" }));

    await waitFor(() => {
      expect(api.previewCurrentReportEquipmentList).toHaveBeenLastCalledWith(
        "project-1",
        []
      );
    });
    const updateButton = screen.getByRole("button", { name: "Update Equipment List" });
    expect(updateButton).toHaveProperty("disabled", false);
    await user.click(updateButton);

    expect(api.updateCurrentReportEquipmentList).toHaveBeenCalledWith("project-1", {
      expected_report_sha256: "a".repeat(64),
      expected_source_sha256: "b".repeat(64),
      expected_catalog_sha256: "c".repeat(64),
      acknowledge_expired: false,
      external_overrides: [],
      updated_by: "Lab User",
    });
  });

  it("updates a stale customer report from the current internal report with both fingerprints", async () => {
    const user = userEvent.setup();
    vi.mocked(api.generateCurrentCustomerReport).mockResolvedValue({
      kind: "published",
      result: {
        project_id: "project-1",
        mode: "official",
        file_name: customerReport.file_name!,
        file_sha256: "d".repeat(64),
        source_report_sha256: "a".repeat(64),
        changed: true,
        archive_path: "D:\\Test Project\\DL-001\\History\\Report\\old.docx",
      },
    });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);

    expect(await screen.findByRole("heading", { name: "Customer report" })).toBeTruthy();
    expect(screen.getByText("Needs update")).toBeTruthy();
    expect(screen.getByText(customerReport.warnings[0])).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Update customer report" }));

    expect(api.generateCurrentCustomerReport).toHaveBeenCalledWith("project-1", {
      expected_internal_report_sha256: "a".repeat(64),
      expected_customer_report_sha256: "b".repeat(64),
    });
    expect(await screen.findByText(/Updated the customer report/)).toBeTruthy();
  });

  it("refreshes and asks before regenerating a customer report deleted after preview", async () => {
    const user = userEvent.setup();
    const missingCustomerReport: api.CustomerReportState = {
      ...customerReport,
      status: "missing",
      file_name: null,
      file_sha256: null,
      generated_from_internal_sha256: null,
      warnings: [],
      download_url: null,
    };
    vi.mocked(api.fetchCurrentCustomerReport)
      .mockResolvedValueOnce(customerReport)
      .mockResolvedValue(missingCustomerReport);
    vi.mocked(api.generateCurrentCustomerReport).mockReset();
    vi.mocked(api.generateCurrentCustomerReport)
      .mockRejectedValueOnce(
        new api.ApiRequestError(
          "The customer report was deleted or moved after the page was loaded.",
          409,
          {
            code: "customer_report_missing_after_preview",
            message: "The customer report was deleted or moved after the page was loaded.",
            can_regenerate: true,
          }
        )
      )
      .mockResolvedValueOnce({
        kind: "published",
        result: {
          project_id: "project-1",
          mode: "official",
          file_name: customerReport.file_name!,
          file_sha256: "d".repeat(64),
          source_report_sha256: "a".repeat(64),
          changed: true,
          archive_path: null,
        },
      });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Update customer report" }));

    expect(
      await screen.findByRole("alertdialog", { name: "Customer report not found" })
    ).toBeTruthy();
    expect(
      screen.getByText(/deleted or moved from the project folder/i)
    ).toBeTruthy();
    expect(screen.queryByText("Report workflow failed.")).toBeNull();

    await user.click(screen.getByRole("button", { name: "Generate new customer report" }));

    expect(api.generateCurrentCustomerReport).toHaveBeenNthCalledWith(2, "project-1", {
      expected_internal_report_sha256: "a".repeat(64),
      expected_customer_report_sha256: null,
    });
    expect(
      await screen.findByText(/Generated a new customer report.*No previous file was archived/)
    ).toBeTruthy();
  });

  it("cancels customer report regeneration without creating a replacement", async () => {
    const user = userEvent.setup();
    const missingCustomerReport: api.CustomerReportState = {
      ...customerReport,
      status: "missing",
      file_name: null,
      file_sha256: null,
      generated_from_internal_sha256: null,
      warnings: [],
      download_url: null,
    };
    vi.mocked(api.fetchCurrentCustomerReport)
      .mockResolvedValueOnce(customerReport)
      .mockResolvedValue(missingCustomerReport);
    vi.mocked(api.generateCurrentCustomerReport).mockReset();
    vi.mocked(api.generateCurrentCustomerReport).mockRejectedValueOnce(
      new api.ApiRequestError(
        "The customer report was deleted or moved after the page was loaded.",
        409,
        {
          code: "customer_report_missing_after_preview",
          message: "The customer report was deleted or moved after the page was loaded.",
          can_regenerate: true,
        }
      )
    );

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Update customer report" }));
    await user.click(
      await screen.findByRole("button", { name: "Cancel" })
    );

    expect(screen.queryByRole("alertdialog", { name: "Customer report not found" })).toBeNull();
    expect(api.generateCurrentCustomerReport).toHaveBeenCalledTimes(1);
    expect(screen.getByRole("button", { name: "Generate customer report" })).toBeTruthy();
  });

  it("does not claim that an unchanged customer report was archived", async () => {
    const user = userEvent.setup();
    vi.mocked(api.generateCurrentCustomerReport).mockResolvedValue({
      kind: "published",
      result: {
        project_id: "project-1",
        mode: "official",
        file_name: customerReport.file_name!,
        file_sha256: customerReport.file_sha256!,
        source_report_sha256: customerReport.internal_report_sha256!,
        changed: false,
        archive_path: null,
      },
    });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Update customer report" }));

    expect(await screen.findByText(/was already current/)).toBeTruthy();
    expect(screen.queryByText(/archived automatically/)).toBeNull();
  });

  it("downloads the generated customer report when no official project folder exists", async () => {
    const user = userEvent.setup();
    vi.mocked(api.fetchCurrentCustomerReport).mockResolvedValue({
      ...customerReport,
      status: "missing",
      mode: "managed_download",
      file_name: null,
      file_sha256: null,
      generated_from_internal_sha256: null,
      warnings: ["No official project folder is available; generation will download a copy."],
      download_url: null,
    });
    vi.mocked(api.generateCurrentCustomerReport).mockResolvedValue({
      kind: "download",
      download: {
        blob: new Blob(["customer"]),
        fileName: "DL-001-CR Qualification Testing Report_Rev_A_Draft.docx",
      },
    });

    render(<ReportWorkspace projectId="project-1" onBack={vi.fn()} />);
    await user.click(await screen.findByRole("button", { name: "Generate and download customer report" }));

    expect(api.generateCurrentCustomerReport).toHaveBeenCalledWith("project-1", {
      expected_internal_report_sha256: "a".repeat(64),
      expected_customer_report_sha256: null,
    });
    expect(await screen.findByText("Generated and downloaded the customer report.")).toBeTruthy();
  });
});
