import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import * as api from "../../api/reportAuthoring";
import { ReportAuthoringPanel } from "./ReportAuthoringPanel";

vi.mock("../../api/reportAuthoring", () => ({
  getReportAuthoring: vi.fn(), uploadReportSource: vi.fn(), saveReportMapping: vi.fn(),
  selectReportBase: vi.fn(), downloadReportArtifact: vi.fn(),
  previewReportFacts: vi.fn(), applyReportFacts: vi.fn(),
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

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason: Error) => void;
  const promise = new Promise<T>((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
}

const editable: api.ReportAuthoringState = { ...state, mappings: [{
  mapping_id: 'identity', source_id: 'source-1', kind: 'identity', label: 'Product identity',
  source_locator: 'approved source', report_text: 'Old product', value: 'New product', reason: 'Confirmed',
  status: 'confirmed', group_id: '', row_id: '', step_token: '', sample_ids: [], matrix_id: '', confirmed_by: '', confirmed_at: '',
}], outputs: [{ output_id: 'copy1', file_name: 'Working.docx', status: 'needs_review', operation: 'prepare_base',
  issues: [], download_url: '/working', base_source_id: 'source-1' }] };

async function startPendingFactUpdate(pending: ReturnType<typeof deferred<api.ReportAuthoringState>>) {
  vi.mocked(api.getReportAuthoring).mockResolvedValue(editable);
  vi.mocked(api.previewReportFacts).mockResolvedValue({ output_sha256: 'a', mapping_ids: ['identity'], preview_sha256: 'p',
    changes: [{ old: 'Old product', new: 'New product', occurrences: 1, parts: ['word/document.xml'] }] });
  vi.mocked(api.applyReportFacts).mockReturnValue(pending.promise);
  const view = render(<ReportAuthoringPanel projectId="P1" />);
  fireEvent.click(screen.getByText('Prepare report from an approved source'));
  await screen.findByText('Approved.docx', { selector: 'span' });
  fireEvent.change(screen.getByLabelText('Source file'), { target: { files: [new File(['x'], 'next.docx')] } });
  fireEvent.click(screen.getByText('Preview confirmed text replacements'));
  fireEvent.click(await screen.findByText('Apply to a new working copy'));
  return view;
}

it.each(['resolve', 'reject'] as const)('locks parent and sibling operations while a fact update is pending and releases on %s', async outcome => {
  const pending = deferred<api.ReportAuthoringState>();
  await startPendingFactUpdate(pending);
  for (const label of ['Retain source copy', 'Use as report base', 'Reload saved evidence', 'Download Working.docx', 'Inspect photo slots', 'Generate customer review copy']) {
    expect(screen.getByRole('button', { name: label }).matches(':disabled')).toBe(true);
  }
  fireEvent.click(screen.getByText('Retain source copy'));
  expect(api.uploadReportSource).not.toHaveBeenCalled();
  await act(async () => { outcome === 'resolve' ? pending.resolve({ ...editable, revision: 2 }) : pending.reject(new Error('Recoverable update failure')); });
  expect(screen.getByText('Retain source copy').matches(':disabled')).toBe(false);
  expect(screen.getByText('Use as report base').matches(':disabled')).toBe(false);
  if (outcome === 'reject') expect(screen.getByRole('alert').textContent).toContain('Recoverable update failure');
});

it('does not let an old child response overwrite or unlock a new project operation', async () => {
  const old = deferred<api.ReportAuthoringState>();
  const view = await startPendingFactUpdate(old);
  const next = deferred<api.ReportAuthoringState>();
  vi.mocked(api.getReportAuthoring).mockReturnValueOnce(next.promise);
  view.rerender(<ReportAuthoringPanel projectId="P2" />);
  fireEvent.click(screen.getByText('Prepare report from an approved source'));
  await act(async () => { old.resolve({ ...editable, revision: 99 }); });
  expect(screen.queryByText('Approved.docx', { selector: 'span' })).toBeNull();
  expect(screen.getByText('Reload saved evidence').matches(':disabled')).toBe(true);
  await act(async () => { next.resolve({ ...state, project_id: 'P2', sources: [] }); });
  expect(screen.getByText('Reload saved evidence').matches(':disabled')).toBe(false);
});
