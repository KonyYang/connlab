import { act, cleanup, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { useMatrixEditorContext } from "./useMatrixEditorContext";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("Matrix editor project context", () => {
  it("waits for lifecycle permissions and supports retry after a failed read", async () => {
    let allowLifecycle: ((response: Response) => void) | undefined;
    let fail = true;
    vi.stubGlobal("fetch", vi.fn(async (url: string) => {
      if (url.endsWith("/lifecycle")) {
        if (fail) return new Response("{}", { status: 503 });
        return new Promise<Response>((resolve) => { allowLifecycle = resolve; });
      }
      return new Response(JSON.stringify(url.endsWith("/ltr") ? [] : { project_id: "P1" }));
    }));
    const { result } = renderHook(() => useMatrixEditorContext("P1"));
    await waitFor(() => expect(result.current.error).toContain("Retry"));
    expect(result.current.project).toBeNull();
    fail = false;
    act(() => result.current.retry());
    await waitFor(() => expect(allowLifecycle).toBeDefined());
    expect(result.current.loading).toBe(true);
    await act(async () => allowLifecycle!(new Response(JSON.stringify({ readonly: true, lifecycle_state: "closed" }))));
    expect(result.current.loading).toBe(false);
    expect(result.current.lifecycle?.readonly).toBe(true);
    expect(result.current.error).toBeNull();
  });

  it("never exposes a late response from a previous project", async () => {
    let finishFirst: ((response: Response) => void) | undefined;
    vi.stubGlobal("fetch", vi.fn(async (url: string) => {
      if (url === "/api/projects/P1") return new Promise<Response>((resolve) => { finishFirst = resolve; });
      return new Response(JSON.stringify(url.endsWith("/ltr") ? [] :
        url.endsWith("/lifecycle") ? { readonly: false } : { project_id: "P2" }));
    }));
    const { result, rerender } = renderHook(({ id }) => useMatrixEditorContext(id), { initialProps: { id: "P1" } });
    rerender({ id: "P2" });
    await waitFor(() => expect(result.current.project?.project_id).toBe("P2"));
    await act(async () => finishFirst!(new Response(JSON.stringify({ project_id: "P1" }))));
    expect(result.current.project?.project_id).toBe("P2");
  });

  it("loads identity and lifecycle without scanning folders or preparing outputs", async () => {
    const responses: Record<string, unknown> = {
      "/api/projects/P1": { project_id: "P1", product_name: "Connector", status: "active" },
      "/api/projects/P1/ltr": [{ ltr_number: "LTR-1" }],
      "/api/projects/P1/lifecycle": { project_id: "P1", lifecycle_state: "active", readonly: false },
    };
    const requested: string[] = [];
    vi.stubGlobal("fetch", vi.fn(async (url: string) => {
      requested.push(url);
      return new Response(JSON.stringify(responses[url] ?? { detail: "Not required by editor" }), {
        status: url in responses ? 200 : 404,
        headers: { "Content-Type": "application/json" },
      });
    }));
    const { result } = renderHook(() => useMatrixEditorContext("P1"));
    await waitFor(() => expect(result.current.latestLtr).toBe("LTR-1"));
    expect(result.current.project?.project_id).toBe("P1");
    expect(result.current.lifecycle?.readonly).toBe(false);
    expect(requested.sort()).toEqual(Object.keys(responses).sort());
  });
});
