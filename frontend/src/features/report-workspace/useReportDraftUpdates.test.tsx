import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { useReportDraftUpdates } from "./useReportDraftUpdates";

vi.mock("../../api/client", async () => ({
  ...await vi.importActual("../../api/client"),
  fetchReportUpdateSource: vi.fn(), updateReportDraftLlcr: vi.fn(), updateReportDraftEquipment: vi.fn(),
  selectReportUpdateSource: vi.fn(), downloadReportWorkingDraft: vi.fn(),
}));

const source = { status: "ready", mode: "download_draft", file_name: "DL-001 Report_Draft.docx",
  file_sha256: "a".repeat(64), report_revision_id: null, folder_path: null, official_folder_path: null,
  can_publish_to_official: false, download_url: null } as api.CurrentReport;
const updated = { project_id: "P1", mode: "download_draft", file_name: source.file_name!, changed: true,
  current_sha256: "b".repeat(64), archive_path: null, draft_revision_id: "1".repeat(32) } as api.ReportSectionUpdateResult;

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(api.fetchReportUpdateSource).mockResolvedValue(source);
  vi.mocked(api.updateReportDraftLlcr).mockResolvedValue(updated);
  vi.mocked(api.updateReportDraftEquipment).mockResolvedValue({ ...updated, status: "completed",
    statistics: { filled: 1, unmatched: [], incomplete: [], expired: [] } });
  vi.mocked(api.downloadReportWorkingDraft).mockResolvedValue({ blob: new Blob(["report"]), fileName: source.file_name! });
});

function callbacks() {
  return { save: vi.fn(), onUpdated: vi.fn(), onEquipmentRequired: vi.fn(), onEquipmentCompleted: vi.fn() };
}

it("chains equipment after LLCR using the last successful draft hash", async () => {
  const events = callbacks();
  const { result } = renderHook(() => useReportDraftUpdates("P1", events));
  await waitFor(() => expect(result.current.source?.status).toBe("ready"));
  await act(async () => { await result.current.updateLlcr("dataset-1"); });
  await act(async () => { await result.current.updateEquipment({ referencesText: "Q-0033" }); });
  expect(api.updateReportDraftEquipment).toHaveBeenCalledWith("P1", "b".repeat(64), { referencesText: "Q-0033" });
  expect(events.save).toHaveBeenCalledTimes(2);
});

it("retains the updated draft and retries its download without repeating the update", async () => {
  vi.mocked(api.downloadReportWorkingDraft).mockRejectedValueOnce(new Error("offline"));
  const events = callbacks();
  const { result } = renderHook(() => useReportDraftUpdates("P1", events));
  await waitFor(() => expect(result.current.source?.status).toBe("ready"));
  await act(async () => { await result.current.updateLlcr("dataset-1"); });
  expect(result.current.downloadError).toContain("Download failed");
  expect(result.current.source?.file_sha256).toBe("b".repeat(64));
  await act(async () => { await result.current.download(); });
  expect(events.save).toHaveBeenCalledTimes(1);
  expect(api.updateReportDraftLlcr).toHaveBeenCalledTimes(1);
});

it("asks for a source only when missing and resumes the pending update on the selected draft", async () => {
  vi.mocked(api.fetchReportUpdateSource).mockResolvedValue({ ...source, status: "missing", mode: null, file_sha256: null });
  vi.mocked(api.selectReportUpdateSource).mockResolvedValue(updated);
  const { result } = renderHook(() => useReportDraftUpdates("P1", callbacks()));
  await waitFor(() => expect(result.current.source?.status).toBe("missing"));
  await act(async () => { await result.current.updateLlcr("dataset-1"); });
  expect(result.current.selectOpen).toBe(true);
  expect(api.updateReportDraftLlcr).not.toHaveBeenCalled();
  await act(async () => { await result.current.select(new File(["report"], "Internal.docx")); });
  expect(api.updateReportDraftLlcr).toHaveBeenCalledWith("P1", "dataset-1", "b".repeat(64));
  expect(result.current.selectOpen).toBe(false);
});

it("suppresses a late update after changing projects", async () => {
  let finish!: (value: api.ReportSectionUpdateResult) => void;
  vi.mocked(api.updateReportDraftLlcr).mockImplementation(() => new Promise(resolve => { finish = resolve; }));
  const events = callbacks();
  const { result, rerender } = renderHook(({ project }) => useReportDraftUpdates(project, events), { initialProps: { project: "P1" } });
  await waitFor(() => expect(result.current.source?.status).toBe("ready"));
  let running!: Promise<void>;
  act(() => { running = result.current.updateLlcr("dataset-1"); });
  rerender({ project: "P2" });
  await act(async () => { finish(updated); await running; });
  expect(events.save).not.toHaveBeenCalled();
  expect(api.downloadReportWorkingDraft).not.toHaveBeenCalled();
  expect(result.current.lastResult).toBeNull();
});

it("prevents duplicate updates while keeping missing-equipment input actionable", async () => {
  vi.mocked(api.updateReportDraftEquipment).mockResolvedValue({ status: "source_required", project_id: "P1" });
  const events = callbacks();
  const { result } = renderHook(() => useReportDraftUpdates("P1", events));
  await waitFor(() => expect(result.current.source?.status).toBe("ready"));
  await act(async () => { await Promise.all([result.current.updateEquipment(), result.current.updateEquipment()]); });
  expect(api.updateReportDraftEquipment).toHaveBeenCalledTimes(1);
  expect(events.onEquipmentRequired).toHaveBeenCalledOnce();
  expect(events.save).not.toHaveBeenCalled();
});

it("reports a source reload failure and clears it after a successful retry", async () => {
  const { result } = renderHook(() => useReportDraftUpdates("P1", callbacks()));
  await waitFor(() => expect(result.current.source?.status).toBe("ready"));
  vi.mocked(api.fetchReportUpdateSource).mockRejectedValueOnce(new Error("offline"));
  await act(async () => { await result.current.refresh().catch(() => undefined); });
  expect(result.current.error).toContain("Unable to check");
  await act(async () => { await result.current.refresh(); });
  expect(result.current.error).toBeNull();
});
