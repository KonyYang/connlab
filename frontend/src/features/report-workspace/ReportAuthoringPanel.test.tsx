import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import * as api from "../../api/reportAuthoring";
import { ReportAuthoringPanel } from "./ReportAuthoringPanel";

vi.mock("../../api/reportAuthoring", () => ({
  getReportAuthoring: vi.fn(), uploadReportSource: vi.fn(), saveReportMapping: vi.fn(),
  selectReportBase: vi.fn(), downloadReportArtifact: vi.fn(),
}));

const state: api.ReportAuthoringState = { project_id: "P1", revision: 1,
  sources: [{ source_id: "source-1", role: "layout_reference", file_name: "Approved.docx", sha256: "a".repeat(64),
    size_bytes: 10, created_at: "2026-10-26", report_dl: "DL-2026-01-001", download_url: "/source" }],
  mappings: [], outputs: [], base_source_id: null, context: { dl_number: "DL-2026-01-002", matrix_id: "matrix-1", steps: [] } };

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(api.getReportAuthoring).mockResolvedValue(state);
});

it("opens retained evidence and saves a missing business decision as pending", async () => {
  vi.mocked(api.saveReportMapping).mockResolvedValue({ ...state, revision: 2, mappings: [{
    mapping_id: "map-1", source_id: "source-1", kind: "specification", label: "Specification revision date",
    source_locator: "Revision record page 27", value: "", reason: "", status: "pending", group_id: "", row_id: "", step_token: "",
    sample_ids: [], matrix_id: "", confirmed_by: "", confirmed_at: "",
  }] });
  render(<ReportAuthoringPanel projectId="P1" />);
  fireEvent.click(screen.getByText("Prepare report from an approved source"));
  await screen.findByText("Approved.docx", { selector: "span" });
  fireEvent.change(screen.getByLabelText("Mapping label"), { target: { value: "Specification revision date" } });
  fireEvent.change(screen.getByLabelText("Source location"), { target: { value: "Revision record page 27" } });
  fireEvent.click(screen.getByRole("button", { name: "Save mapping" }));
  await screen.findByText("Specification revision date");
  expect(api.saveReportMapping).toHaveBeenCalledWith("P1", expect.objectContaining({
    expected_revision: 1, source_id: "source-1", status: "pending", value: "",
  }));
});

it("starts a separate copy from a selected reference and shows unresolved facts", async () => {
  vi.mocked(api.selectReportBase).mockResolvedValue({ ...state, revision: 2, base_source_id: "source-1", outputs: [{
    output_id: "out-1", file_name: "New_Draft.docx", status: "needs_review", operation: "prepare_base",
    issues: ["Review project facts before delivery."], download_url: "/output", base_source_id: "source-1",
  }] });
  render(<ReportAuthoringPanel projectId="P1" />);
  fireEvent.click(screen.getByText("Prepare report from an approved source"));
  await screen.findByText("Approved.docx", { selector: "span" });
  fireEvent.click(screen.getByRole("button", { name: "Use as report base" }));
  await screen.findByText("Review project facts before delivery.");
  expect(api.selectReportBase).toHaveBeenCalledWith("P1", "source-1", 1);
  expect(screen.getByRole("button", { name: "Download New_Draft.docx" })).toBeTruthy();
});

it("does not display an old project's late response after navigation", async () => {
  let release!: (value: api.ReportAuthoringState) => void;
  vi.mocked(api.getReportAuthoring).mockReturnValueOnce(new Promise(resolve => { release = resolve; }));
  const view = render(<ReportAuthoringPanel projectId="P1" />);
  fireEvent.click(screen.getByText("Prepare report from an approved source"));
  await waitFor(() => expect(api.getReportAuthoring).toHaveBeenCalled());
  view.rerender(<ReportAuthoringPanel projectId="P2" />);
  release(state);
  await waitFor(() => expect(screen.queryByText("Approved.docx")).toBeNull());
});
