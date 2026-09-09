import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { useProjectFolderGeneration } from "./useProjectFolderGeneration";

const api = vi.hoisted(() => ({ getProjectFolderGeneration: vi.fn(), previewProjectFolderGeneration: vi.fn(),
  startProjectFolderGeneration: vi.fn(), resumeProjectFolderGeneration: vi.fn() }));
vi.mock("../../api/client", () => api);
const operation = { project_id: "p", operation_id: "operation", status: "running", step: 3, completed_steps: [], message: null };
beforeEach(() => { vi.resetAllMocks(); api.getProjectFolderGeneration.mockResolvedValue(null); });
afterEach(() => { vi.useRealTimers(); });

it("starts one backend operation and reconnects without browser-owned writes", async () => {
  api.previewProjectFolderGeneration.mockResolvedValue({ expected_context: "preview" });
  api.startProjectFolderGeneration.mockResolvedValue(operation);
  const { result, unmount } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "shown-preview"));
  await act(async () => { await result.current.start(); });
  expect(api.startProjectFolderGeneration).toHaveBeenCalledTimes(1);
  expect(api.startProjectFolderGeneration.mock.calls[0][1].expected_context).toBe("shown-preview");
  expect(api.previewProjectFolderGeneration).not.toHaveBeenCalled();
  expect(result.current.busy).toBe(true);
  unmount();
  api.getProjectFolderGeneration.mockResolvedValue(operation);
  const reconnected = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "shown-preview"));
  await waitFor(() => expect(reconnected.result.current.busy).toBe(true));
  expect(api.startProjectFolderGeneration).toHaveBeenCalledTimes(1);
});

it("resumes the original operation instead of replaying a rebuild choice", async () => {
  api.getProjectFolderGeneration.mockResolvedValue({ ...operation, status: "interrupted" });
  api.resumeProjectFolderGeneration.mockResolvedValue(operation);
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "shown-preview"));
  await waitFor(() => expect(result.current.canResume).toBe(true));
  await act(async () => { await result.current.start("overwrite_rebuild"); });
  expect(api.resumeProjectFolderGeneration).toHaveBeenCalledWith("p", "operation");
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
});

it("releases project-local pending state after navigation and ignores the old response", async () => {
  let resolveOld!: (value: unknown) => void;
  api.startProjectFolderGeneration.mockReturnValueOnce(new Promise(resolve => { resolveOld = resolve; }));
  const { result, rerender } = renderHook(({ project }) => useProjectFolderGeneration(project, vi.fn(), "shown"), { initialProps: { project: "A" } });
  let pending!: Promise<void>;
  await act(async () => { pending = result.current.start(); });
  expect(result.current.busy).toBe(true);
  rerender({ project: "B" });
  await waitFor(() => expect(result.current.busy).toBe(false));
  await act(async () => { resolveOld({ ...operation, project_id: "A" }); await pending; });
  expect(result.current.operation).toBeNull();
  expect(result.current.busy).toBe(false);
});

it("reports a failed completion refresh without an unhandled promise", async () => {
  api.getProjectFolderGeneration.mockResolvedValue({ ...operation, status: "completed" });
  const { result } = renderHook(() => useProjectFolderGeneration("p", () => Promise.reject(new Error("offline")), "shown"));
  await waitFor(() => expect(result.current.error).toContain("could not refresh"));
});

it("keeps a start blocker visible while polling finds no saved operation", async () => {
  vi.useFakeTimers();
  api.startProjectFolderGeneration.mockRejectedValue(
    new Error("Project Schedule is not confirmed.")
  );
  const { result, unmount } = renderHook(() =>
    useProjectFolderGeneration("p", vi.fn(), "shown-preview")
  );

  await act(async () => {
    await result.current.start();
  });
  expect(result.current.error).toBe("Project Schedule is not confirmed.");

  await act(async () => {
    await vi.advanceTimersByTimeAsync(1000);
  });
  expect(result.current.error).toBe("Project Schedule is not confirmed.");

  unmount();
});

it("clears a transient connection warning after polling reconnects", async () => {
  vi.useFakeTimers();
  api.getProjectFolderGeneration
    .mockRejectedValueOnce(new Error("offline"))
    .mockResolvedValue(null);
  const { result, unmount } = renderHook(() =>
    useProjectFolderGeneration("p", vi.fn(), "shown-preview")
  );

  await act(async () => {
    await Promise.resolve();
  });
  expect(result.current.error).toContain("Connection interrupted");

  await act(async () => {
    await vi.advanceTimersByTimeAsync(1000);
  });
  expect(result.current.error).toBeNull();

  unmount();
});

it("explicitly restarts corrected inputs with the newly shown preview and no old conflict choice", async () => {
  api.getProjectFolderGeneration.mockResolvedValue({ ...operation, status: "blocked", can_restart: true });
  api.startProjectFolderGeneration.mockResolvedValue({ ...operation, operation_id: "new" });
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "fresh-shown"));
  await waitFor(() => expect(result.current.canRestart).toBe(true));
  await act(async () => { await result.current.restart(undefined, "confirmed-preview"); });
  expect(api.startProjectFolderGeneration).toHaveBeenCalledWith("p", expect.objectContaining({
    replaces_operation_id: "operation", expected_context: "confirmed-preview", conflict_strategy: undefined,
  }));
  expect(api.resumeProjectFolderGeneration).not.toHaveBeenCalled();
  expect(api.previewProjectFolderGeneration).not.toHaveBeenCalled();
});
