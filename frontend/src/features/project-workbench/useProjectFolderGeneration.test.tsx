import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { useProjectFolderGeneration, type FolderUpdateReview } from "./useProjectFolderGeneration";

const api = vi.hoisted(() => ({ getProjectFolderGeneration: vi.fn(), previewProjectFolderGeneration: vi.fn(),
  startProjectFolderGeneration: vi.fn(), resumeProjectFolderGeneration: vi.fn(),
  adoptOfficialWorkspace: vi.fn() }));
vi.mock("../../api/client", () => api);
const operation = { project_id: "p", operation_id: "operation", status: "running", step: 3, completed_steps: [], message: null };
beforeEach(() => { vi.resetAllMocks(); api.getProjectFolderGeneration.mockResolvedValue(null); });
afterEach(() => { vi.useRealTimers(); });

it.each([null, "completed", "blocked"])("checks inactive status %s slowly but discovers external work on focus", async (status) => {
  vi.useFakeTimers();
  api.getProjectFolderGeneration.mockResolvedValue(status ? { ...operation, status } : null);
  const { result, unmount } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "shown"));
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  await act(async () => { await vi.advanceTimersByTimeAsync(29000); });
  expect(api.getProjectFolderGeneration).toHaveBeenCalledTimes(1);
  await act(async () => { await vi.advanceTimersByTimeAsync(1000); });
  expect(api.getProjectFolderGeneration).toHaveBeenCalledTimes(2);
  api.getProjectFolderGeneration.mockResolvedValue(operation);
  await act(async () => { window.dispatchEvent(new Event("focus")); });
  expect(result.current.busy).toBe(true);
  await act(async () => { await vi.advanceTimersByTimeAsync(1000); });
  expect(api.getProjectFolderGeneration).toHaveBeenCalledTimes(4);
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
  unmount();
  await act(async () => { window.dispatchEvent(new Event("focus")); await vi.advanceTimersByTimeAsync(30000); });
  expect(api.getProjectFolderGeneration).toHaveBeenCalledTimes(4);
});

it("returns to fast polling immediately after starting from idle", async () => {
  vi.useFakeTimers();
  api.startProjectFolderGeneration.mockResolvedValue(operation);
  const { result, unmount } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "shown"));
  await act(async () => { await vi.advanceTimersByTimeAsync(0); });
  await act(async () => { await result.current.start(); });
  api.getProjectFolderGeneration.mockResolvedValue({ ...operation, status: "completed" });
  await act(async () => { await vi.advanceTimersByTimeAsync(1000); });
  expect(result.current.operation?.status).toBe("completed");
  expect(api.startProjectFolderGeneration).toHaveBeenCalledTimes(1);
  unmount();
});

it("does not overlap status reads when focus returns during an outstanding request", async () => {
  vi.useFakeTimers();
  let resolve!: (value: null) => void;
  api.getProjectFolderGeneration.mockReturnValueOnce(new Promise(done => { resolve = done; }));
  const { unmount } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "shown"));
  await act(async () => {
    window.dispatchEvent(new Event("focus"));
    document.dispatchEvent(new Event("visibilitychange"));
  });
  expect(api.getProjectFolderGeneration).toHaveBeenCalledTimes(1);
  await act(async () => { resolve(null); });
  await act(async () => { await vi.advanceTimersByTimeAsync(30000); });
  expect(api.getProjectFolderGeneration).toHaveBeenCalledTimes(2);
  unmount();
});

it("uses an advanced preview only after an existing folder needs review", async () => {
  api.previewProjectFolderGeneration
    .mockResolvedValueOnce({ expected_context: "ordinary", workspace_preview: { status: "conflict", blockers: ["Review folder"] }, recovery: null })
    .mockResolvedValueOnce({ expected_context: "advanced", workspace_preview: { status: "conflict", blockers: ["Review folder"] }, recovery: null });
  api.startProjectFolderGeneration.mockResolvedValue(operation);
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "old"));
  let review: FolderUpdateReview | undefined;
  await act(async () => { review = (await result.current.update()) || undefined; });
  expect(review?.preview.expected_context).toBe("advanced");
  expect(api.previewProjectFolderGeneration.mock.calls).toEqual([
    ["p", "create"],
    ["p", "backup_rebuild"],
  ]);
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
});

it("requires a separate review before switching from an in-place update to backup and rebuild", async () => {
  api.previewProjectFolderGeneration
    .mockResolvedValueOnce({ expected_context: "ordinary", workspace_preview: { status: "completed", blockers: [] }, recovery: null })
    .mockResolvedValueOnce({ expected_context: "in-place", workspace_preview: { status: "completed", blockers: [] }, recovery: null })
    .mockResolvedValueOnce({ expected_context: "advanced", workspace_preview: { status: "completed", blockers: [] }, recovery: null })
    .mockResolvedValueOnce({ expected_context: "advanced", workspace_preview: { status: "completed", blockers: [] }, recovery: null });
  api.startProjectFolderGeneration.mockResolvedValue(operation);
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "old"));

  let review: FolderUpdateReview | undefined;
  await act(async () => { review = (await result.current.update()) || undefined; });

  expect(review?.preview.expected_context).toBe("in-place");
  expect(api.previewProjectFolderGeneration.mock.calls).toEqual([
    ["p", "create"],
    ["p", "update_in_place"],
  ]);
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();

  let backupReview: FolderUpdateReview | undefined;
  await act(async () => { backupReview = (await result.current.update("backup_and_recreate", review)) || undefined; });
  expect(backupReview?.preview.expected_context).toBe("advanced");
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
  await act(async () => { await result.current.update("backup_and_recreate", backupReview); });

  expect(api.previewProjectFolderGeneration).toHaveBeenLastCalledWith("p", "backup_rebuild");
  expect(api.previewProjectFolderGeneration).toHaveBeenCalledTimes(4);
  expect(api.startProjectFolderGeneration).toHaveBeenCalledWith("p", expect.objectContaining({
    expected_context: "advanced",
    conflict_strategy: "backup_and_recreate",
  }));
});

it("offers an in-place file update for a completed folder without archiving its custom name", async () => {
  const ordinary = { expected_context: "ordinary", workspace_preview: { status: "completed", blockers: [] }, recovery: null };
  const inPlace = { expected_context: "in-place", workspace_preview: { status: "completed", blockers: [] }, recovery: null };
  api.previewProjectFolderGeneration.mockResolvedValueOnce(ordinary).mockResolvedValueOnce(inPlace)
    .mockResolvedValueOnce(inPlace);
  api.startProjectFolderGeneration.mockResolvedValue(operation);
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "ordinary"));
  let review: FolderUpdateReview | undefined;
  await act(async () => { review = (await result.current.update()) || undefined; });
  expect(review?.intent).toBe("update_in_place");
  expect(api.previewProjectFolderGeneration.mock.calls).toEqual([
    ["p", "create"], ["p", "update_in_place"],
  ]);
  await act(async () => { await result.current.update("update_in_place", review); });
  expect(api.startProjectFolderGeneration).toHaveBeenCalledWith("p", expect.objectContaining({
    expected_context: "in-place", conflict_strategy: "update_in_place",
  }));
});

it("does not offer an in-place update when its preview has start blockers", async () => {
  api.previewProjectFolderGeneration
    .mockResolvedValueOnce({ expected_context: "ordinary", workspace_preview: { status: "completed", blockers: [] }, recovery: null })
    .mockResolvedValueOnce({
      expected_context: "advanced",
      start_blockers: ["Fee authority changed after the folder was created."],
      workspace_preview: { status: "completed", blockers: [] },
      recovery: null,
    });
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "old"));

  let review: FolderUpdateReview | void = undefined;
  await act(async () => { review = await result.current.update(); });

  expect(review).toBeUndefined();
  expect(result.current.error).toBe("Fee authority changed after the folder was created.");
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
});

it("links an adoptable folder without starting generation", async () => {
  api.adoptOfficialWorkspace.mockResolvedValue({ workspace_id: "workspace" });
  const completed = vi.fn();
  const { result } = renderHook(() =>
    useProjectFolderGeneration("p", completed, "ordinary")
  );

  await act(async () => { await result.current.update("adopt_existing"); });

  expect(api.adoptOfficialWorkspace).toHaveBeenCalledWith("p");
  expect(api.previewProjectFolderGeneration).not.toHaveBeenCalled();
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
  expect(completed).toHaveBeenCalledTimes(1);
});

it("allows the new project to link while ignoring an older adoption response", async () => {
  let finishOld!: (value: unknown) => void;
  api.adoptOfficialWorkspace.mockImplementation((projectId: string) =>
    projectId === "A"
      ? new Promise(resolve => { finishOld = resolve; })
      : Promise.resolve({ workspace_id: "workspace-B" })
  );
  const completed = vi.fn();
  const { result, rerender } = renderHook(
    ({ id }) => useProjectFolderGeneration(id, completed, "ordinary"),
    { initialProps: { id: "A" } },
  );
  let oldRequest!: Promise<FolderUpdateReview | void>;
  act(() => { oldRequest = result.current.update("adopt_existing"); });

  rerender({ id: "B" });
  await act(async () => { await result.current.update("adopt_existing"); });

  expect(api.adoptOfficialWorkspace.mock.calls).toEqual([["A"], ["B"]]);
  expect(completed).toHaveBeenCalledTimes(1);
  await act(async () => {
    finishOld({ workspace_id: "workspace-A" });
    await oldRequest;
  });
  expect(completed).toHaveBeenCalledTimes(1);
});

it.each([false, true])("routes an interrupted operation with inputs_match=%s safely", async (matches) => {
  api.getProjectFolderGeneration.mockResolvedValue({ ...operation, status: "interrupted", can_restart: true });
  api.previewProjectFolderGeneration.mockResolvedValue({ expected_context: "fresh", workspace_preview: { status: "completed", blockers: [] },
    recovery: { operation_id: "operation", inputs_match: matches, rebuild_pending: false } });
  api.resumeProjectFolderGeneration.mockResolvedValue(operation);
  api.startProjectFolderGeneration.mockResolvedValue(operation);
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "old"));
  let review: FolderUpdateReview | undefined;
  await act(async () => { review = (await result.current.update()) || undefined; });
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
  expect(api.resumeProjectFolderGeneration).not.toHaveBeenCalled();
  await act(async () => { await result.current.update("backup_and_recreate", review); });
  expect(api.startProjectFolderGeneration).toHaveBeenCalledWith("p", expect.objectContaining({ replaces_operation_id: "operation", conflict_strategy: "backup_and_recreate" }));
});

it("never replays a pending destructive rebuild from an ordinary update", async () => {
  api.getProjectFolderGeneration.mockResolvedValue({ ...operation, status: "blocked", can_restart: false });
  api.previewProjectFolderGeneration.mockResolvedValue({ expected_context: "fresh", workspace_preview: { status: "exists", blockers: [] },
    recovery: { operation_id: "operation", inputs_match: true, rebuild_pending: true } });
  api.resumeProjectFolderGeneration.mockResolvedValue(operation);
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "old"));
  let review: FolderUpdateReview | undefined;
  await act(async () => { review = (await result.current.update()) || undefined; });
  expect(review).toEqual(expect.objectContaining({ resumeRebuild: true }));
  expect(api.resumeProjectFolderGeneration).not.toHaveBeenCalled();
  await act(async () => { await result.current.update(undefined, review, true); });
  expect(api.resumeProjectFolderGeneration).toHaveBeenCalledTimes(1);
});

it("does not replace uncheckpointed publication when inputs changed", async () => {
  api.getProjectFolderGeneration.mockResolvedValue({ ...operation, status: "blocked", can_restart: false });
  api.previewProjectFolderGeneration.mockResolvedValue({ expected_context: "fresh", workspace_preview: { status: "completed", blockers: [] },
    recovery: { operation_id: "operation", inputs_match: false, rebuild_pending: false } });
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "old"));
  await act(async () => { await result.current.update(); });
  expect(result.current.error).toContain("safe recovery");
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
});

it.each([
  { status: "blocked", step: 8, message: "Finalization failed" },
  { status: "interrupted", step: 5, message: "File publication interrupted" },
])("offers confirmed recovery for $message after workspace completion", async (pending) => {
  api.getProjectFolderGeneration.mockResolvedValue({ ...operation, ...pending, can_restart: false });
  api.previewProjectFolderGeneration.mockResolvedValue({ expected_context: "fresh", workspace_preview: { status: "completed", blockers: [] },
    recovery: { operation_id: "operation", inputs_match: true, rebuild_pending: false } });
  api.resumeProjectFolderGeneration.mockResolvedValue(operation);
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "old"));
  let review: FolderUpdateReview | undefined;
  await act(async () => { review = (await result.current.update()) || undefined; });
  expect(review).toEqual(expect.objectContaining({ operationId: "operation", resumeRebuild: true }));
  expect(api.resumeProjectFolderGeneration).not.toHaveBeenCalled();
  await act(async () => { await result.current.update(undefined, review, true); });
  expect(api.resumeProjectFolderGeneration).toHaveBeenCalledWith("p", "operation");
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
});

it("requires review for an existing unverified folder and rejects stale confirmation", async () => {
  api.previewProjectFolderGeneration.mockResolvedValue({ expected_context: "fresh", workspace_preview: { status: "exists", blockers: [] }, recovery: null });
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "old"));
  let review: FolderUpdateReview | undefined;
  await act(async () => { review = (await result.current.update()) || undefined; });
  expect(review).toBeTruthy();
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
  api.previewProjectFolderGeneration.mockResolvedValue({ expected_context: "changed", workspace_preview: { status: "exists", blockers: [] }, recovery: null });
  await act(async () => { await result.current.update("backup_and_recreate", review); });
  expect(result.current.error).toContain("preview changed");
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
});

it("does not write on preview failure or start twice on a double click", async () => {
  api.previewProjectFolderGeneration.mockRejectedValue(new Error("Preview unavailable"));
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "old"));
  await act(async () => { await Promise.all([result.current.update(), result.current.update()]); });
  expect(api.previewProjectFolderGeneration).toHaveBeenCalledTimes(1);
  expect(result.current.error).toBe("Preview unavailable");
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
});

it("reports missing generation inputs before offering rebuild choices", async () => {
  api.previewProjectFolderGeneration.mockResolvedValue({ expected_context: "fresh", start_blockers: ["Fee template is missing."],
    workspace_preview: { status: "exists", blockers: ["Existing folder"] }, recovery: null });
  const { result } = renderHook(() => useProjectFolderGeneration("p", vi.fn(), "old"));
  let review: FolderUpdateReview | void = undefined;
  await act(async () => { review = await result.current.update(); });
  expect(review).toBeUndefined();
  expect(result.current.error).toBe("Fee template is missing.");
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
});

it("does not dispatch an old project after switching during update preflight", async () => {
  let finish!: (value: unknown) => void;
  api.previewProjectFolderGeneration.mockReturnValue(new Promise(resolve => { finish = resolve; }));
  const { result, rerender } = renderHook(({ id }) => useProjectFolderGeneration(id, vi.fn(), "old"), { initialProps: { id: "A" } });
  let pending: Promise<FolderUpdateReview | void>;
  await act(async () => { pending = result.current.update(); });
  rerender({ id: "B" });
  await act(async () => {
    finish({ expected_context: "fresh", workspace_preview: { status: "completed", blockers: [] }, recovery: null });
    await pending;
  });
  expect(api.startProjectFolderGeneration).not.toHaveBeenCalled();
  expect(result.current.busy).toBe(false);
});

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
  await act(async () => { await result.current.start("backup_and_recreate"); });
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

it("keeps a start blocker visible through a failed poll and later reconnect", async () => {
  vi.useFakeTimers();
  api.getProjectFolderGeneration
    .mockResolvedValueOnce(null)
    .mockResolvedValueOnce(null)
    .mockRejectedValueOnce(new Error("offline"))
    .mockResolvedValue(null);
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
    await vi.advanceTimersByTimeAsync(30000);
  });
  expect(api.getProjectFolderGeneration).toHaveBeenCalledTimes(3);
  expect(result.current.error).toBe("Project Schedule is not confirmed.");

  await act(async () => {
    await vi.advanceTimersByTimeAsync(1000);
  });
  expect(api.getProjectFolderGeneration).toHaveBeenCalledTimes(4);
  expect(result.current.error).toBe("Project Schedule is not confirmed.");

  unmount();
});

it("keeps a start blocker visible when polling returns an older completed operation", async () => {
  vi.useFakeTimers();
  const completed = { ...operation, status: "completed" };
  api.getProjectFolderGeneration.mockResolvedValue(completed);
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
