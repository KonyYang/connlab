import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { useUploadedCustomerReportJob } from "./useUploadedCustomerReportJob";

vi.mock("../../api/client", async () => ({
  ...await vi.importActual("../../api/client"),
  startStandaloneCustomerReport: vi.fn(),
  readStandaloneCustomerReportJob: vi.fn(),
  downloadStandaloneCustomerReport: vi.fn(),
}));
const running: api.StandaloneCustomerReportJob = { operation_id: "upload-1", status: "running",
  stage: "copying_content", elapsed_seconds: 2, message: null };
const completed: api.StandaloneCustomerReportJob = { ...running, status: "completed", stage: "completed" };
const file = new File(["source"], "Other Report.docx");

describe("uploaded customer report lifecycle", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(api.startStandaloneCustomerReport).mockResolvedValue(running);
    vi.mocked(api.readStandaloneCustomerReportJob).mockResolvedValue(completed);
    vi.mocked(api.downloadStandaloneCustomerReport).mockResolvedValue({ blob: new Blob(["report"]), fileName: "Other-CR Report.docx" });
  });

  it.each(["Other-CR Report.docx", "Other-CR Report draft.docx"])("downloads %s with one draft suffix and displays that same filename", async (sourceName) => {
    vi.mocked(api.startStandaloneCustomerReport).mockResolvedValue(completed);
    const blob = new Blob(["report"]);
    vi.mocked(api.downloadStandaloneCustomerReport).mockResolvedValue({ blob, fileName: sourceName });
    const save = vi.fn();
    const { result } = renderHook(() => useUploadedCustomerReportJob("project-1", save));
    await act(async () => { await result.current.start(file); });
    await waitFor(() => expect(save).toHaveBeenCalledWith({ blob, fileName: "Other-CR Report draft.docx" }));
    expect(result.current.fileName).toBe("Other-CR Report draft.docx");
  });

  it("retains a legacy Draft suffix and its collision number without duplicating Draft", async () => {
    vi.mocked(api.startStandaloneCustomerReport).mockResolvedValue(completed);
    vi.mocked(api.downloadStandaloneCustomerReport).mockResolvedValue({ blob: new Blob(["report"]), fileName: "Other-CR Report_Draft (9).docx" });
    const save = vi.fn();
    const { result } = renderHook(() => useUploadedCustomerReportJob("project-1", save));
    await act(async () => { await result.current.start(file); });
    await waitFor(() => expect(result.current.fileName).toBe("Other-CR Report_Draft (9).docx"));
    expect(save.mock.calls[0][0].fileName).toBe("Other-CR Report_Draft (9).docx");
  });

  it("expires a missing operation rather than keeping generation permanently busy", async () => {
    vi.mocked(api.readStandaloneCustomerReportJob).mockRejectedValue(new api.ApiRequestError("Operation expired", 404));
    const { result } = renderHook(() => useUploadedCustomerReportJob("project-1", vi.fn()));
    await act(async () => { await result.current.start(file); await result.current.retryQuery(); });
    await act(async () => { await result.current.retryQuery(); });
    expect(result.current.busy).toBe(false);
    expect(result.current.error).toMatch(/expired|not available/i);
    expect(result.current.fileName).toBeNull();
  });

  it("prevents duplicate uploads, polls real progress and saves the completed copy once", async () => {
    const save = vi.fn();
    const { result } = renderHook(() => useUploadedCustomerReportJob("project-1", save));
    await act(async () => { await Promise.all([result.current.start(file), result.current.start(file)]); });
    expect(api.startStandaloneCustomerReport).toHaveBeenCalledTimes(1);
    expect(result.current.job?.stage).toBe("copying_content");
    await waitFor(() => expect(save).toHaveBeenCalledTimes(1), { timeout: 2000 });
    expect(result.current.fileName).toBe("Other-CR Report draft.docx");
  });

  it("keeps a lost status response recoverable without starting another conversion", async () => {
    vi.mocked(api.readStandaloneCustomerReportJob).mockRejectedValueOnce(new Error("Connection lost"));
    const { result } = renderHook(() => useUploadedCustomerReportJob("project-1", vi.fn()));
    await act(async () => { await result.current.start(file); });
    await act(async () => { await result.current.retryQuery(); });
    expect(result.current.queryWarning).toBe("Connection lost");
    expect(result.current.busy).toBe(true);
    await act(async () => { await result.current.start(file); });
    expect(api.startStandaloneCustomerReport).toHaveBeenCalledTimes(1);
    await act(async () => { await result.current.retryQuery(); });
    await waitFor(() => expect(result.current.fileName).toBe("Other-CR Report draft.docx"));
  });

  it("retries download without uploading again", async () => {
    vi.mocked(api.startStandaloneCustomerReport).mockResolvedValue(completed);
    vi.mocked(api.downloadStandaloneCustomerReport).mockRejectedValueOnce(new Error("Download interrupted"));
    const save = vi.fn();
    const { result } = renderHook(() => useUploadedCustomerReportJob("project-1", save));
    await act(async () => { await result.current.start(file); });
    await waitFor(() => expect(result.current.downloadError).toBe("Download interrupted"));
    expect(result.current.fileName).toBeNull();
    await act(async () => { await result.current.retryDownload(); });
    expect(save).toHaveBeenCalledTimes(1);
    expect(api.startStandaloneCustomerReport).toHaveBeenCalledTimes(1);
  });

  it("reports expired download output without showing a saved filename", async () => {
    vi.mocked(api.startStandaloneCustomerReport).mockResolvedValue(completed);
    vi.mocked(api.downloadStandaloneCustomerReport).mockRejectedValue(new api.ApiRequestError("Output expired", 410));
    const save = vi.fn();
    const { result } = renderHook(() => useUploadedCustomerReportJob("project-1", save));
    await act(async () => { await result.current.start(file); });
    await waitFor(() => expect(result.current.error).toContain("expired"));
    expect(result.current.fileName).toBeNull();
    expect(result.current.busy).toBe(false);
    expect(save).not.toHaveBeenCalled();
  });

  it("allows another source after validation rejection or a failed conversion", async () => {
    vi.mocked(api.startStandaloneCustomerReport).mockRejectedValueOnce(new api.ApiRequestError("Incompatible report", 422))
      .mockResolvedValueOnce({ ...running, status: "failed", stage: "failed", message: "Word could not open the document" })
      .mockResolvedValueOnce(completed);
    const { result } = renderHook(() => useUploadedCustomerReportJob("project-1", vi.fn()));
    await act(async () => { await result.current.start(file); });
    expect(result.current.error).toBe("Incompatible report");
    expect(result.current.busy).toBe(false);
    await act(async () => { await result.current.start(file); });
    expect(result.current.job?.message).toBe("Word could not open the document");
    expect(result.current.busy).toBe(false);
    await act(async () => { await result.current.start(file); });
    await waitFor(() => expect(result.current.fileName).toBe("Other-CR Report draft.docx"));
  });

  it.each(["switch", "unmount"])("does not download a late upload after %s", async (change) => {
    let resolve!: (value: api.StandaloneCustomerReportJob) => void;
    vi.mocked(api.startStandaloneCustomerReport).mockImplementationOnce(() => new Promise(r => { resolve = r; }));
    const save = vi.fn();
    const { result, rerender, unmount } = renderHook(({ project }) => useUploadedCustomerReportJob(project, save), { initialProps: { project: "project-1" } });
    let request!: Promise<boolean>;
    act(() => { request = result.current.start(file); });
    if (change === "switch") rerender({ project: "project-2" }); else unmount();
    await act(async () => { resolve(completed); await request; });
    expect(api.downloadStandaloneCustomerReport).not.toHaveBeenCalled();
    expect(save).not.toHaveBeenCalled();
  });

  it("does not save a delayed download after changing project", async () => {
    vi.mocked(api.startStandaloneCustomerReport).mockResolvedValue(completed);
    let resolve!: (value: api.BlobDownloadResponse) => void;
    vi.mocked(api.downloadStandaloneCustomerReport).mockImplementationOnce(() => new Promise(r => { resolve = r; }));
    const save = vi.fn();
    const { result, rerender } = renderHook(({ project }) => useUploadedCustomerReportJob(project, save), { initialProps: { project: "project-1" } });
    await act(async () => { await result.current.start(file); });
    await waitFor(() => expect(api.downloadStandaloneCustomerReport).toHaveBeenCalledOnce());
    rerender({ project: "project-2" });
    await act(async () => { resolve({ blob: new Blob(["report"]), fileName: "old.docx" }); });
    expect(save).not.toHaveBeenCalled();
    expect(result.current.fileName).toBeNull();
  });
});
