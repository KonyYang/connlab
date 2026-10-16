import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { getWorkspaceInfo } from "../../api/existingProjects";
import { WorkspaceInfoPanel } from "./WorkspaceInfoPanel";
vi.mock("../../api/existingProjects", () => ({getWorkspaceInfo: vi.fn()}));
describe("active workspace", () => {
  it("shows actual locations and unversioned schema without offering database mutation", async () => {
    vi.mocked(getWorkspaceInfo).mockResolvedValue({runtime_mode: "custom", database_path: "C:/isolated/store.sqlite3",
      data_directory: "C:/isolated", config_path: "C:/isolated/local.toml", application_version: "0.1.0", release: {},
      release_status: "not_available", sqlite_user_version: 0, schema_status: "unversioned", notice: "Keep test copies separate."});
    render(<WorkspaceInfoPanel />);
    await userEvent.click(screen.getByRole("button", {name:"Show workspace details"}));
    expect(await screen.findByText("C:/isolated/store.sqlite3")).toBeTruthy();
    expect(screen.getByText(/No unified schema compatibility version/)).toBeTruthy();
    expect(screen.queryByRole("button", {name: /switch|merge/i})).toBeNull();
  });
  it("can retry a failed information read", async () => {
    vi.mocked(getWorkspaceInfo).mockRejectedValueOnce(new Error("offline")).mockResolvedValueOnce({runtime_mode:"development",
      database_path: ":memory:", data_directory:"test",config_path:"test",application_version:"test",release:{},
      release_status:"not_available",sqlite_user_version:0,schema_status:"unversioned",notice:"test"});
    render(<WorkspaceInfoPanel />);
    await userEvent.click(screen.getByRole("button", {name:"Show workspace details"}));
    await waitFor(() => expect(screen.getByRole("alert")).toBeTruthy());
    await userEvent.click(screen.getByRole("button", {name:"Retry workspace information"}));
    expect(await screen.findByText(":memory:")).toBeTruthy();
  });
});
