import { act, cleanup, renderHook } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type {
  MatrixEditorSessionSeed,
  ProjectMatrixDraftSaveRequest,
} from "../../api/client";
import { useMatrixDraftPersistence } from "./useMatrixDraftPersistence";

const apiMocks = vi.hoisted(() => ({
  discard: vi.fn(),
  save: vi.fn(),
}));

vi.mock("../../api/client", () => ({
  discardMatrixEditorSessionDraft: apiMocks.discard,
  isProjectLifecycleReadonlyErrorDetail: () => false,
  saveMatrixEditorSessionDraft: apiMocks.save,
}));

const basePayload: ProjectMatrixDraftSaveRequest = {
  groups: [
    {
      draft_group_id: "group-1",
      group_key: "g1",
      group_label: "1",
      group_order: 1,
      is_selected: true,
    },
  ],
  rows: [
    {
      draft_row_id: "row-1",
      is_sample_row: false,
      row_order: 1,
      test_item: "Visual Examination",
    },
  ],
  cells: [
    {
      cell_value: "1",
      draft_group_id: "group-1",
      draft_row_id: "row-1",
    },
  ],
};

const seed: MatrixEditorSessionSeed = {
  active_confirmed_matrix_id: "confirmed-1",
  active_confirmed_revision: 3,
  active_source_import_id: "import-1",
  active_source_snapshot_id: "snapshot-1",
  editor_draft: null,
  project_id: "P1",
  source_status: "available",
};

const savedResponse = {
  active_confirmed_matrix_id: "confirmed-1",
  active_confirmed_revision: 3,
  draft_status: "current" as const,
  draft_updated_at: "2026-08-22T00:00:00Z",
  editor_draft_id: "draft-2",
  saved_payload_signature: "saved-2",
};

type HookProps = {
  payload: ProjectMatrixDraftSaveRequest;
  signature: string;
};

function renderPersistence(
  initialProps: HookProps,
  onBackToWorkbench = vi.fn(),
  onError = vi.fn(),
) {
  return {
    ...renderHook(
      ({ payload, signature }: HookProps) =>
        useMatrixDraftPersistence({
          currentPayload: payload,
          currentSignature: signature,
          draftLoading: false,
          durationAuthorities: [],
          onBackToWorkbench,
          onError,
          projectId: "P1",
          readonlyMessage: null,
          sourcePreview: null,
        }),
      { initialProps },
    ),
    onBackToWorkbench,
    onError,
  };
}

describe("useMatrixDraftPersistence", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    apiMocks.save.mockReset().mockResolvedValue(savedResponse);
    apiMocks.discard.mockReset().mockResolvedValue({ discarded: true });
    vi.spyOn(window, "confirm").mockReturnValue(true);
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  it("autosaves a changed draft and exposes the current saved tokens", async () => {
    const view = renderPersistence({ payload: basePayload, signature: "base" });
    act(() =>
      view.result.current.hydrateSession({
        baselineSignature: "base",
        hasEditorDraft: false,
        seed,
      }),
    );

    view.rerender({
      payload: { ...basePayload, post_test_buffer_days: "1" },
      signature: "changed",
    });
    await act(() => vi.advanceTimersByTimeAsync(800));

    expect(apiMocks.save).toHaveBeenCalledWith(
      "P1",
      expect.objectContaining({
        expected_active_confirmed_matrix_id: "confirmed-1",
        expected_active_confirmed_revision: 3,
        post_test_buffer_days: "1",
      }),
      expect.objectContaining({ signal: expect.any(AbortSignal) }),
    );
    expect(view.result.current.hasCurrentSavedDraft).toBe(true);
    expect(view.result.current.savedEditorDraftId).toBe("draft-2");
    expect(view.result.current.savedPayloadSignature).toBe("saved-2");
    expect(view.result.current.saveState).toBe("saved");
  });

  it("does not autosave before the first confirmed Matrix authority", async () => {
    const view = renderPersistence({ payload: basePayload, signature: "base" });
    act(() =>
      view.result.current.hydrateSession({
        baselineSignature: "base",
        hasEditorDraft: false,
        seed: {
          ...seed,
          active_confirmed_matrix_id: null,
          active_confirmed_revision: null,
        },
      }),
    );

    view.rerender({
      payload: { ...basePayload, post_test_buffer_days: "2" },
      signature: "changed",
    });
    await act(() => vi.advanceTimersByTimeAsync(2000));

    expect(apiMocks.save).not.toHaveBeenCalled();
  });

  it("uses an in-flight autosave result when Cancel discards the draft", async () => {
    let resolveSave: ((value: typeof savedResponse) => void) | null = null;
    apiMocks.save.mockImplementationOnce(
      () =>
        new Promise<typeof savedResponse>((resolve) => {
          resolveSave = resolve;
        }),
    );
    const view = renderPersistence({ payload: basePayload, signature: "base" });
    act(() =>
      view.result.current.hydrateSession({
        baselineSignature: "base",
        hasEditorDraft: false,
        seed,
      }),
    );
    view.rerender({
      payload: { ...basePayload, post_test_buffer_days: "3" },
      signature: "changed",
    });
    await act(() => vi.advanceTimersByTimeAsync(800));

    let cancelPromise: Promise<void>;
    act(() => {
      cancelPromise = view.result.current.cancel();
    });
    expect(apiMocks.discard).not.toHaveBeenCalled();
    await act(async () => {
      resolveSave?.(savedResponse);
      await cancelPromise!;
    });

    expect(apiMocks.discard).toHaveBeenCalledWith("P1", {
      expected_editor_draft_id: "draft-2",
      expected_saved_payload_signature: "saved-2",
    });
    expect(view.onBackToWorkbench).toHaveBeenCalledOnce();
  });

  it("bounds Cancel waiting and falls back to the hydrated draft tokens", async () => {
    apiMocks.save.mockImplementationOnce(() => new Promise(() => {}));
    const view = renderPersistence({ payload: basePayload, signature: "base" });
    act(() =>
      view.result.current.hydrateSession({
        baselineSignature: "base",
        hasEditorDraft: true,
        seed: {
          ...seed,
          editor_draft_id: "draft-existing",
          saved_payload_signature: "saved-existing",
        },
      }),
    );
    view.rerender({
      payload: { ...basePayload, post_test_buffer_days: "4" },
      signature: "changed",
    });
    await act(() => vi.advanceTimersByTimeAsync(800));
    const saveSignal = apiMocks.save.mock.calls[0][2].signal as AbortSignal;

    let cancelPromise: Promise<void>;
    act(() => {
      cancelPromise = view.result.current.cancel();
    });
    await act(async () => {
      await vi.advanceTimersByTimeAsync(1500);
      await cancelPromise!;
    });

    expect(saveSignal.aborted).toBe(true);
    expect(apiMocks.discard).toHaveBeenCalledWith("P1", {
      expected_editor_draft_id: "draft-existing",
      expected_saved_payload_signature: "saved-existing",
    });
    expect(view.onBackToWorkbench).toHaveBeenCalledOnce();
  });

  it("keeps the editor open and reports a discard failure", async () => {
    apiMocks.discard.mockRejectedValueOnce(new Error("Draft changed before cancel."));
    const view = renderPersistence({ payload: basePayload, signature: "base" });
    act(() =>
      view.result.current.hydrateSession({
        baselineSignature: "base",
        hasEditorDraft: true,
        seed: {
          ...seed,
          editor_draft_id: "draft-existing",
          saved_payload_signature: "saved-existing",
        },
      }),
    );

    await act(() => view.result.current.cancel());

    expect(view.onBackToWorkbench).not.toHaveBeenCalled();
    expect(view.onError).toHaveBeenCalledWith("Draft changed before cancel.");
    expect(view.result.current.saveState).toBe("error");
    expect(view.result.current.isCancelling).toBe(false);
  });
});
