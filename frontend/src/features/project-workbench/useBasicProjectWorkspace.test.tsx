import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import { useBasicProjectWorkspace } from "./useBasicProjectWorkspace";
const api = vi.hoisted(() => ({ previewBasicProjectWorkspace: vi.fn(), createBasicProjectWorkspace: vi.fn(), resumeBasicProjectWorkspace: vi.fn() }));
vi.mock("../../api/client", () => api);
const preview = (project_id = "p1", status = "ready") => ({ project_id, status, directory_available: false, official_project_folder_path: "D:/isolated/project", target_identity: null, blockers: [], operation_id: null, expected_context: project_id + "-context" });
const completed = { operation_id: "op", status: "completed", directory_available: true, official_project_folder_path: "D:/isolated/project", issues: [], message: null };
beforeEach(() => { vi.resetAllMocks(); api.previewBasicProjectWorkspace.mockImplementation(async (id) => preview(id)); api.createBasicProjectWorkspace.mockResolvedValue(completed); });
it("creates a basic directory using only the backend preview context", async () => {
 const changed = vi.fn(); const { result } = renderHook(() => useBasicProjectWorkspace("p1", changed));
 await waitFor(() => expect(result.current.preview?.status).toBe("ready"));
 api.previewBasicProjectWorkspace.mockResolvedValue({...preview(),directory_available:true});
 await act(() => result.current.create());
 expect(api.createBasicProjectWorkspace).toHaveBeenCalledWith("p1", { expected_context: "p1-context", request_id: expect.any(String), confirm_existing: false });
 expect(result.current.directoryAvailable).toBe(true); expect(changed).toHaveBeenCalledTimes(1);
});
it("requires explicit review of an existing unassociated folder", async () => {
 api.previewBasicProjectWorkspace.mockResolvedValue(preview("p1", "review_required"));
 const { result } = renderHook(() => useBasicProjectWorkspace("p1", vi.fn()));
 await waitFor(() => expect(result.current.preview?.status).toBe("review_required"));
 await act(() => result.current.create()); expect(api.createBasicProjectWorkspace).not.toHaveBeenCalled();
 await act(() => result.current.create(true)); expect(api.createBasicProjectWorkspace).toHaveBeenCalledWith("p1", expect.objectContaining({ confirm_existing: true }));
});
it("resumes the saved basic operation rather than starting a new operation", async () => {
 api.previewBasicProjectWorkspace.mockResolvedValue({ ...preview("p1", "recovery_required"), operation_id: "saved" }); api.resumeBasicProjectWorkspace.mockResolvedValue(completed);
 const { result } = renderHook(() => useBasicProjectWorkspace("p1", vi.fn()));
 await waitFor(() => expect(result.current.preview).toBeTruthy()); await act(() => result.current.create());
 expect(api.resumeBasicProjectWorkspace).toHaveBeenCalledWith("p1", "saved"); expect(api.createBasicProjectWorkspace).not.toHaveBeenCalled();
});
it("keeps the idempotency key after a lost create response", async () => {
 api.createBasicProjectWorkspace.mockRejectedValueOnce(new Error("Connection lost"));
 const { result } = renderHook(() => useBasicProjectWorkspace("p1", vi.fn())); await waitFor(() => expect(result.current.preview).toBeTruthy());
 await act(() => result.current.create()); await act(() => result.current.create());
 expect(api.createBasicProjectWorkspace.mock.calls[0][1].request_id).toBe(api.createBasicProjectWorkspace.mock.calls[1][1].request_id);
});
it("ignores a late create result after switching projects", async () => {
 let resolve!: (x: unknown) => void; api.createBasicProjectWorkspace.mockReturnValue(new Promise(r => { resolve = r; }));
 const changed = vi.fn(); const { result, rerender } = renderHook(({id}) => useBasicProjectWorkspace(id, changed), {initialProps:{id:"p1"}});
 await waitFor(() => expect(result.current.preview).toBeTruthy()); let pending!: Promise<void>; act(() => { pending = result.current.create(); });
 rerender({id:"p2"}); await waitFor(() => expect(result.current.preview?.project_id).toBe("p2"));
 await act(async () => { resolve(completed); await pending; }); expect(result.current.directoryAvailable).toBe(false); expect(changed).not.toHaveBeenCalled();
});

it("uses explicit availability even when a closed project blocks creation", async () => {
 api.previewBasicProjectWorkspace.mockResolvedValue({...preview("p1","blocked"),directory_available:true,blockers:["Project is read-only"]});
 const {result}=renderHook(()=>useBasicProjectWorkspace("p1",vi.fn()));await waitFor(()=>expect(result.current.directoryAvailable).toBe(true));
 await act(()=>result.current.create());expect(api.createBasicProjectWorkspace).not.toHaveBeenCalled();
});
it("does not retain successful availability when a later check finds the folder unavailable", async () => {
 api.previewBasicProjectWorkspace.mockResolvedValue({...preview(),directory_available:true});
 const {result}=renderHook(()=>useBasicProjectWorkspace("p1",vi.fn()));await waitFor(()=>expect(result.current.directoryAvailable).toBe(true));
 api.previewBasicProjectWorkspace.mockResolvedValue({...preview("p1","blocked"),blockers:["Folder no longer exists"]});await act(()=>result.current.refresh());expect(result.current.directoryAvailable).toBe(false);
});

it("retains a failed operation explanation after refreshing readiness", async () => {
 api.createBasicProjectWorkspace.mockResolvedValue({...completed,status:"blocked",directory_available:false,message:"Folder identity changed"});
 const {result}=renderHook(()=>useBasicProjectWorkspace("p1",vi.fn()));await waitFor(()=>expect(result.current.preview).toBeTruthy());await act(()=>result.current.create());
 expect(result.current.error).toBe("Folder identity changed");
});
