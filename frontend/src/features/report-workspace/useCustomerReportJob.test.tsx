import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { useCustomerReportJob } from "./useCustomerReportJob";

vi.mock("../../api/client", async () => ({
  ...await vi.importActual("../../api/client"),
  startProjectCustomerReportJob: vi.fn(),
  fetchLatestProjectCustomerReportJob: vi.fn(),
  readProjectCustomerReportJob: vi.fn(),
  downloadProjectCustomerReportJob: vi.fn(),
}));

const running: api.ProjectCustomerReportJob = {
  operation_id: "operation-1", project_id: "project-1", status: "running",
  stage: "formatting_document", elapsed_seconds: 19, message: null, error_code: null,
  result: null,
};
const completed: api.ProjectCustomerReportJob = {
  ...running, status: "completed", stage: "completed", elapsed_seconds: 22,
  result: { mode: "managed_download", file_name: "Customer.docx", changed: true, archive_path: null },
};
const input = { expected_internal_report_sha256: "a".repeat(64), expected_customer_report_sha256: null };

describe("project customer report lifecycle", () => {
  beforeEach(() => {
    vi.resetAllMocks();
    sessionStorage.clear();
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue(null);
    vi.mocked(api.startProjectCustomerReportJob).mockResolvedValue(running);
    vi.mocked(api.readProjectCustomerReportJob).mockResolvedValue(completed);
    vi.mocked(api.downloadProjectCustomerReportJob).mockResolvedValue({ blob: new Blob(["report"]), fileName: "Customer.docx" });
  });

  it("prevents duplicate starts, shows real progress and downloads the original run once", async () => {
    const save = vi.fn();
    const { result } = renderHook(() => useCustomerReportJob("project-1", save, 10));
    await waitFor(() => expect(result.current.busy).toBe(false));
    await act(async () => { await Promise.all([result.current.start(input), result.current.start(input)]); });
    expect(api.startProjectCustomerReportJob).toHaveBeenCalledTimes(1);
    expect(result.current.job?.stage).toBe("formatting_document");
    await waitFor(() => expect(save).toHaveBeenCalledTimes(1));
    expect(result.current.job?.status).toBe("completed");
  });

  it("restores a running job without starting another or automatically downloading on reentry", async () => {
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue(running);
    const save = vi.fn();
    const { result } = renderHook(() => useCustomerReportJob("project-1", save, 10));
    await waitFor(() => expect(result.current.job?.status).toBe("completed"));
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
    expect(save).not.toHaveBeenCalled();
    await act(async () => { await result.current.download(); });
    expect(save).toHaveBeenCalledTimes(1);
  });

  it("retains a completed result after download failure and retries without generation", async () => {
    vi.mocked(api.startProjectCustomerReportJob).mockResolvedValue(completed);
    vi.mocked(api.downloadProjectCustomerReportJob).mockRejectedValueOnce(new Error("offline"));
    const { result } = renderHook(() => useCustomerReportJob("project-1", vi.fn(), 10));
    await waitFor(() => expect(result.current.busy).toBe(false));
    await act(async () => { await result.current.start(input); });
    await waitFor(() => expect(result.current.downloadError).toContain("Download failed"));
    expect(result.current.job?.status).toBe("completed");
    await act(async () => { await result.current.download(); });
    expect(result.current.downloadError).toBeNull();
    expect(api.startProjectCustomerReportJob).toHaveBeenCalledTimes(1);
  });

  it("keeps a running job and its last stage when progress polling is temporarily offline", async () => {
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue(running);
    vi.mocked(api.readProjectCustomerReportJob).mockRejectedValue(new Error("offline"));
    const { result } = renderHook(() => useCustomerReportJob("project-1", vi.fn(), 10));
    await waitFor(() => expect(result.current.queryWarning).toContain("Progress temporarily unavailable"));
    expect(result.current.job?.status).toBe("running");
    expect(result.current.busy).toBe(true);
    vi.mocked(api.readProjectCustomerReportJob).mockResolvedValue(completed);
    await act(async () => { await result.current.retryQuery(); });
    expect(result.current.job?.status).toBe("completed");
  });

  it("stops waiting when the server has lost the job", async () => {
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue(running);
    vi.mocked(api.readProjectCustomerReportJob).mockRejectedValue(new api.ApiRequestError("gone", 410, null));
    const { result } = renderHook(() => useCustomerReportJob("project-1", vi.fn(), 10));
    await waitFor(() => expect(result.current.error).toContain("expired or the backend restarted"));
    expect(result.current.busy).toBe(false);
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
  });

  it("does not display a previous project's late response", async () => {
    let resolve!: (job: api.ProjectCustomerReportJob) => void;
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockImplementationOnce(() => new Promise(r => { resolve = r; }));
    const { result, rerender } = renderHook(({ project }) => useCustomerReportJob(project, vi.fn(), 10), { initialProps: { project: "project-1" } });
    rerender({ project: "project-2" });
    await act(async () => { resolve(running); });
    expect(result.current.job).toBeNull();
  });

  it("reconciles a lost start response without marking the backend job failed or starting again", async () => {
    vi.mocked(api.startProjectCustomerReportJob).mockRejectedValue(new TypeError("network lost"));
    const { result } = renderHook(() => useCustomerReportJob("project-1", vi.fn(), 10));
    await waitFor(() => expect(result.current.busy).toBe(false));
    await act(async () => { await result.current.start(input); });
    expect(result.current.queryWarning).toContain("whether generation started");
    expect(result.current.busy).toBe(true);
    await act(async () => { await result.current.start(input); });
    expect(api.startProjectCustomerReportJob).toHaveBeenCalledTimes(1);
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue(completed);
    await act(async () => { await result.current.retryQuery(); });
    expect(result.current.job?.status).toBe("completed");
    expect(result.current.error).toBeNull();
    expect(api.downloadProjectCustomerReportJob).not.toHaveBeenCalled();
  });

  it("restores a completed official result without downloading or generating", async () => {
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue({
      ...completed, result: { ...completed.result!, mode: "official" },
    });
    const { result } = renderHook(() => useCustomerReportJob("project-1", vi.fn(), 10));
    await waitFor(() => expect(result.current.job?.status).toBe("completed"));
    expect(result.current.busy).toBe(false);
    expect(api.startProjectCustomerReportJob).not.toHaveBeenCalled();
    expect(api.downloadProjectCustomerReportJob).not.toHaveBeenCalled();
  });

  it("retains publication failure details and allows an explicit retry", async () => {
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue({
      ...running, status: "failed", error_code: "customer_report_publication_failed", message: "Target changed. Reload before retrying.",
    });
    const { result } = renderHook(() => useCustomerReportJob("project-1", vi.fn(), 10));
    await waitFor(() => expect(result.current.job?.status).toBe("failed"));
    expect(result.current.job?.message).toContain("Target changed");
    expect(result.current.busy).toBe(false);
    await act(async () => { await result.current.start(input); });
    expect(api.startProjectCustomerReportJob).toHaveBeenCalledTimes(1);
  });

  it("does not offer a futile download retry after a retained artifact expires", async () => {
    vi.mocked(api.fetchLatestProjectCustomerReportJob).mockResolvedValue(completed);
    vi.mocked(api.downloadProjectCustomerReportJob).mockRejectedValue(new api.ApiRequestError("expired", 410, null));
    const { result } = renderHook(() => useCustomerReportJob("project-1", vi.fn(), 10));
    await waitFor(() => expect(result.current.job?.status).toBe("completed"));
    await act(async () => { await result.current.download(); });
    expect(result.current.error).toContain("generate a new copy");
    expect(result.current.job).toBeNull();
    expect(result.current.downloadError).toBeNull();
    expect(result.current.busy).toBe(false);
  });
});
