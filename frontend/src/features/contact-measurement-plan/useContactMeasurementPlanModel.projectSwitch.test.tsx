import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api/client";
import { useContactMeasurementPlanModel } from "./useContactMeasurementPlanModel";

vi.mock("../../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../../api/client")>()),
  fetchContactMeasurementPlanWorkspace: vi.fn(),
}));

const apiMocks = vi.mocked(api);

describe("useContactMeasurementPlanModel project switch reload guards", () => {
  beforeEach(() => vi.resetAllMocks());

  it("does not let a resolved old-project reload clear the new project's busy state", async () => {
    const oldReload = deferred<api.ContactMeasurementPlanWorkspace>();
    const newReload = deferred<api.ContactMeasurementPlanWorkspace>();
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(workspace("PA", "fingerprint-a"))
      .mockImplementationOnce(() => oldReload.promise)
      .mockResolvedValueOnce(workspace("PB", "fingerprint-b"))
      .mockImplementationOnce(() => newReload.promise);
    const { result, rerender } = renderHook(
      ({ projectId }) => useContactMeasurementPlanModel({ projectId }),
      { initialProps: { projectId: "PA" } }
    );
    await waitFor(() => expect(result.current.workspace?.project_id).toBe("PA"));
    let oldOperation: Promise<void>;
    act(() => { oldOperation = result.current.reloadLatest(); });
    await waitFor(() => expect(result.current.busy).toBe("reload"));

    rerender({ projectId: "PB" });
    await waitFor(() => expect(result.current.workspace?.project_id).toBe("PB"));
    let newOperation: Promise<void>;
    act(() => { newOperation = result.current.reloadLatest(); });
    await waitFor(() => expect(result.current.busy).toBe("reload"));

    oldReload.resolve(workspace("PA", "fingerprint-a2"));
    await act(async () => { await oldOperation; });

    expect(result.current.workspace?.project_id).toBe("PB");
    expect(result.current.busy).toBe("reload");
    expect(result.current.message).toBeNull();
    expect(result.current.error).toBeNull();

    newReload.resolve(workspace("PB", "fingerprint-b2"));
    await act(async () => { await newOperation; });
    expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-b2");
    expect(result.current.busy).toBeNull();
    expect(result.current.message).toBe("Latest contact measurement plan loaded.");
  });

  it("does not let a rejected old-project reload write an error into the new project", async () => {
    const oldReload = deferred<api.ContactMeasurementPlanWorkspace>();
    const newReload = deferred<api.ContactMeasurementPlanWorkspace>();
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(workspace("PA", "fingerprint-a"))
      .mockImplementationOnce(() => oldReload.promise)
      .mockResolvedValueOnce(workspace("PB", "fingerprint-b"))
      .mockImplementationOnce(() => newReload.promise);
    const { result, rerender } = renderHook(
      ({ projectId }) => useContactMeasurementPlanModel({ projectId }),
      { initialProps: { projectId: "PA" } }
    );
    await waitFor(() => expect(result.current.workspace?.project_id).toBe("PA"));
    let oldOperation: Promise<void>;
    act(() => { oldOperation = result.current.reloadLatest(); });

    rerender({ projectId: "PB" });
    await waitFor(() => expect(result.current.workspace?.project_id).toBe("PB"));
    let newOperation: Promise<void>;
    act(() => { newOperation = result.current.reloadLatest(); });
    await waitFor(() => expect(result.current.busy).toBe("reload"));

    oldReload.reject(new Error("Project A reload failed"));
    await act(async () => { await oldOperation; });

    expect(result.current.workspace?.project_id).toBe("PB");
    expect(result.current.busy).toBe("reload");
    expect(result.current.message).toBeNull();
    expect(result.current.error).toBeNull();

    newReload.resolve(workspace("PB", "fingerprint-b2"));
    await act(async () => { await newOperation; });
  });

  it("invalidates an old reload when returning to the same project after an ABA switch", async () => {
    const oldReload = deferred<api.ContactMeasurementPlanWorkspace>();
    const returnReload = deferred<api.ContactMeasurementPlanWorkspace>();
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(workspace("PA", "fingerprint-a1"))
      .mockImplementationOnce(() => oldReload.promise)
      .mockResolvedValueOnce(workspace("PB", "fingerprint-b1"))
      .mockResolvedValueOnce(workspace("PA", "fingerprint-a-return"))
      .mockImplementationOnce(() => returnReload.promise);
    const { result, rerender } = renderHook(
      ({ projectId }) => useContactMeasurementPlanModel({ projectId }),
      { initialProps: { projectId: "PA" } }
    );
    await waitFor(() => expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-a1"));
    let oldOperation: Promise<void>;
    act(() => { oldOperation = result.current.reloadLatest(); });
    rerender({ projectId: "PB" });
    await waitFor(() => expect(result.current.workspace?.project_id).toBe("PB"));
    rerender({ projectId: "PA" });
    await waitFor(() => expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-a-return"));
    let returnOperation: Promise<void>;
    act(() => { returnOperation = result.current.reloadLatest(); });
    await waitFor(() => expect(result.current.busy).toBe("reload"));

    oldReload.resolve(workspace("PA", "fingerprint-a-old"));
    await act(async () => { await oldOperation; });

    expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-a-return");
    expect(result.current.busy).toBe("reload");
    expect(result.current.message).toBeNull();
    expect(result.current.error).toBeNull();

    returnReload.resolve(workspace("PA", "fingerprint-a2"));
    await act(async () => { await returnOperation; });
    expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-a2");
    expect(result.current.message).toBe("Latest contact measurement plan loaded.");
  });

  it("does not let a rejected old reload contaminate return-A state after an ABA switch", async () => {
    const oldReload = deferred<api.ContactMeasurementPlanWorkspace>();
    const returnReload = deferred<api.ContactMeasurementPlanWorkspace>();
    apiMocks.fetchContactMeasurementPlanWorkspace
      .mockResolvedValueOnce(workspace("PA", "fingerprint-a1"))
      .mockImplementationOnce(() => oldReload.promise)
      .mockResolvedValueOnce(workspace("PB", "fingerprint-b1"))
      .mockResolvedValueOnce(workspace("PA", "fingerprint-a-return"))
      .mockImplementationOnce(() => returnReload.promise);
    const { result, rerender } = renderHook(
      ({ projectId }) => useContactMeasurementPlanModel({ projectId }),
      { initialProps: { projectId: "PA" } }
    );
    await waitFor(() => expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-a1"));
    let oldOperation: Promise<void>;
    act(() => { oldOperation = result.current.reloadLatest(); });
    rerender({ projectId: "PB" });
    await waitFor(() => expect(result.current.workspace?.project_id).toBe("PB"));
    rerender({ projectId: "PA" });
    await waitFor(() => expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-a-return"));
    let returnOperation: Promise<void>;
    act(() => { returnOperation = result.current.reloadLatest(); });
    await waitFor(() => expect(result.current.busy).toBe("reload"));

    oldReload.reject(new Error("Old A reload failed"));
    await act(async () => { await oldOperation; });

    expect(result.current.workspace?.editable_revision_fingerprint).toBe("fingerprint-a-return");
    expect(result.current.busy).toBe("reload");
    expect(result.current.message).toBeNull();
    expect(result.current.error).toBeNull();

    returnReload.resolve(workspace("PA", "fingerprint-a2"));
    await act(async () => { await returnOperation; });
  });
});

function deferred<T>() {
  let resolve!: (value: T) => void;
  let reject!: (reason?: unknown) => void;
  const promise = new Promise<T>((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

function workspace(projectId: string, fingerprint: string): api.ContactMeasurementPlanWorkspace {
  return {
    status: "draft",
    project_id: projectId,
    active_confirmed_revision_id: "confirmed-1",
    editable_revision_id: "draft-1",
    editable_revision_state: "draft",
    editable_revision_fingerprint: fingerprint,
    revision: { revision_id: "draft-1", revision_sequence: 1, state: "draft", fingerprint },
    matrix_binding: {
      base_confirmed_matrix_id: "cmv-1",
      base_matrix_revision: 1,
      current_confirmed_matrix_id: "cmv-1",
      current_matrix_revision: 1,
      matrix_binding_fingerprint: "cmv-1:1",
    },
    targets: [],
    impacts: [],
    summary: {
      included_target_count: 0,
      total_target_count: 0,
      needs_review_count: 0,
      readings_by_kind: { llcr: null, cr_specified_current: null },
    },
    diagnostics: [],
    family_id_high_water_by_kind: { llcr: 0, cr_specified_current: 0 },
  };
}
