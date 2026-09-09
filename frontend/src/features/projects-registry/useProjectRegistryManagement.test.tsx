import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { ApiRequestError } from "../../api/client";
import * as api from "../../api/projectRegistryManagement";
import { useProjectRegistryManagement } from "./useProjectRegistryManagement";
vi.mock("../../api/projectRegistryManagement", () => ({previewProjectRegistryAction: vi.fn(), moveProjectToTrash: vi.fn(), restoreManagedProject: vi.fn()}));
const preview = (id: string, token = id): api.ProjectRegistryPreview => ({
  project: {project_id: id, display_project_id: "DL-2026-01-002", sample_description: id,
    requestor: "Lab", created_on: "2026-01-01", lifecycle_state: "active", close_reason_label: null,
    registry_state: "active", registry_revision: 0, changed_at: null, reason: null, test_item: null},
  action: "trash", token, conflicts: [], blockers: [], retained_data: [], warnings: [],
});
describe("project registry request ownership", () => {
  beforeEach(() => vi.resetAllMocks());
  it("keeps the latest selected independent record when an older preview arrives late", async () => {
    let resolveA!: (value: api.ProjectRegistryPreview) => void;
    vi.mocked(api.previewProjectRegistryAction).mockImplementation((id) => id === "A"
      ? new Promise((resolve) => {resolveA = resolve;}) : Promise.resolve(preview("B")));
    const {result} = renderHook(() => useProjectRegistryManagement("active", vi.fn()));
    act(() => {void result.current.open("A", "trash");});
    await act(async () => {await result.current.open("B", "trash");});
    await act(async () => {resolveA(preview("A"));});
    expect(result.current.preview?.project.project_id).toBe("B");
  });
  it("locks duplicate submissions and requires a fresh preview after a conflict", async () => {
    vi.mocked(api.previewProjectRegistryAction).mockResolvedValue(preview("A"));
    vi.mocked(api.moveProjectToTrash).mockRejectedValue(new ApiRequestError("Changed", 409, {}));
    const onChanged = vi.fn();
    const {result} = renderHook(() => useProjectRegistryManagement("active", onChanged));
    await act(async () => {await result.current.open("A", "trash");});
    await act(async () => {await Promise.all([result.current.trash("Created by mistake"), result.current.trash("Created by mistake")]);});
    expect(api.moveProjectToTrash).toHaveBeenCalledTimes(1);
    expect(result.current.stale).toBe(true);
    expect(result.current.preview?.project.project_id).toBe("A");
    await act(async () => {await result.current.trash("Created by mistake");});
    expect(api.moveProjectToTrash).toHaveBeenCalledTimes(1);
    vi.mocked(api.previewProjectRegistryAction).mockResolvedValue(preview("A", "new-token"));
    await act(async () => {await result.current.refresh();});
    vi.mocked(api.moveProjectToTrash).mockResolvedValue({...preview("A").project, registry_state: "trash"});
    await act(async () => {await result.current.trash("Created by mistake");});
    expect(api.moveProjectToTrash).toHaveBeenLastCalledWith("A", {token: "new-token", reason: "Created by mistake"});
    expect(onChanged).toHaveBeenCalledTimes(1);
  });
  it("invalidates pending previews when moving to a different registry area", async () => {
    let resolve!: (value: api.ProjectRegistryPreview) => void;
    vi.mocked(api.previewProjectRegistryAction).mockImplementation(() => new Promise((r) => {resolve = r;}));
    const {result, rerender} = renderHook(({area}) => useProjectRegistryManagement(area, vi.fn()), {initialProps: {area: "active"}});
    act(() => {void result.current.open("A", "trash");});
    rerender({area: "history"});
    await act(async () => {resolve(preview("A"));});
    await waitFor(() => expect(result.current.target).toBeNull());
    expect(result.current.preview).toBeNull();
  });
});
