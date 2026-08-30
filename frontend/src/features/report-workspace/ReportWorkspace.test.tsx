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
    inspectLlcrResultWorkbook: vi.fn(),
    confirmLlcrResultImport: vi.fn(),
    generateInitialReportRevision: vi.fn(),
    previewCurrentReportLlcrUpdate: vi.fn(),
    updateCurrentReportLlcr: vi.fn(),
    downloadCurrentReport: vi.fn(),
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
  download_url: "/api/projects/project-1/report-workspace/current-report/download",
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

describe("ReportWorkspace", () => {
  beforeEach(() => {
    vi.mocked(api.fetchReportWorkspace).mockResolvedValue(state);
    vi.mocked(api.fetchCurrentReport).mockResolvedValue(currentReport);
    vi.mocked(api.inspectLlcrResultWorkbook).mockResolvedValue(preview);
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

  it("exposes initial generation, LLCR import preview, confirmation, and the current report", async () => {
    const user = userEvent.setup();
    const onBack = vi.fn();
    render(<ReportWorkspace projectId="project-1" onBack={onBack} />);

    expect(await screen.findByRole("heading", { name: "Report Workspace" })).toBeTruthy();
    expect(screen.getByText("Project project-1")).toBeTruthy();
    expect(screen.getAllByText(currentReport.file_name!).length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("Confirmed Matrix revision 4")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Generate initial report" })).toHaveProperty("disabled", true);

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
});
