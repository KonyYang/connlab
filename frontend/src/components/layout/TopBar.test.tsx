import { act, render, screen, waitFor, within } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { AppShell } from "./AppShell";
import { TopBar } from "./TopBar";
import userEvent from "@testing-library/user-event";
import { getLocalProfile } from "../../api/localIdentity";
import { refreshCurrentProfile } from "../../currentUser";
import { getPublicFolderWorkflowContext, openLocalProjectFolder } from "../../api/client";

vi.mock("../../api/client", async original => ({ ...await original<typeof import("../../api/client")>(),
  getPublicFolderWorkflowContext: vi.fn(), openLocalProjectFolder: vi.fn() }));

function availability(projectId: string, available: boolean) {
  return { project_id: projectId, local_official_folder_available: available } as Awaited<ReturnType<typeof getPublicFolderWorkflowContext>>;
}

vi.mock("../../api/localIdentity", async original => ({ ...await original<typeof import("../../api/localIdentity")>(),
  getLocalProfile: vi.fn() }));

beforeEach(async () => {
  vi.resetAllMocks();
  vi.mocked(getLocalProfile).mockResolvedValue({ profile: null });
  await refreshCurrentProfile();
});

describe("compact top context bar", () => {
  it("shows the page title and reserves a page-action slot without global placeholder controls", () => {
    render(<TopBar activeRoute="projects" actions={<button type="button">Refresh</button>} />);

    expect(screen.getByRole("heading", { name: "Projects" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Refresh" })).toBeTruthy();
    expect(screen.getByRole("banner").querySelector(".top-bar-actions")).toBeTruthy();
    expect(screen.queryByRole("search")).toBeNull();
    expect(screen.queryByRole("button", { name: "Help" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Local notifications" })).toBeNull();
  });

  it("uses the route title when a page does not provide an override", () => {
    render(<TopBar activeRoute="tools" />);

    expect(screen.getByRole("heading", { name: "Tools" })).toBeTruthy();
  });

  it("uses the compact Workspace title for the project workbench", () => {
    render(<TopBar activeRoute="workbench" />);

    expect(screen.getByRole("heading", { name: "Workspace" })).toBeTruthy();
  });

  it("keeps the Workbench title bar outside its independently scrollable content region", () => {
    render(
      <AppShell activeRoute="workbench">
        <p>Workbench content</p>
      </AppShell>
    );

    const workspace = screen.getByText("Workbench content").closest(".app-workspace");
    expect(workspace?.className).toContain("app-workspace-workbench");
    expect(workspace?.querySelector(".app-main-scroll-region")?.textContent).toContain(
      "Workbench content"
    );
  });

  it("keeps AppShell top-bar actions compatible while the slot is context-owned", () => {
    render(
      <AppShell activeRoute="projects" topBarActions={<button type="button">Refresh</button>}>
        <p>Project content</p>
      </AppShell>
    );

    expect(screen.getByRole("button", { name: "Refresh" })).toBeTruthy();
    expect(screen.getByLabelText("Page actions").contains(screen.getByRole("button", { name: "Refresh" }))).toBe(true);
  });
});


it("opens only the scoped project's folder from the page header", async () => {
  vi.mocked(getPublicFolderWorkflowContext).mockResolvedValue(availability("P1", true));
  vi.mocked(openLocalProjectFolder).mockResolvedValue({ project_id: "P1", status: "opened", message: "Opened", local_official_folder_path: "D:/P1" });
  const user = userEvent.setup();
  const view = render(<AppShell activeRoute="workbench" topBarTitle="Report" projectFolderId="P1"><p>Report content</p></AppShell>);
  expect(within(screen.getByLabelText("Primary navigation")).queryByRole("button", { name: "Folders" })).toBeNull();
  const folder = within(screen.getByRole("banner")).getByRole<HTMLButtonElement>("button", { name: "Open project folder" });
  await waitFor(() => expect(folder.disabled).toBe(false));
  await user.click(folder);
  expect(openLocalProjectFolder).toHaveBeenCalledExactlyOnceWith("P1");
  view.rerender(<AppShell activeRoute="projects"><p>Project list</p></AppShell>);
  expect(screen.queryByRole("button", { name: "Open project folder" })).toBeNull();
});


it("discards the prior project's pending availability after switching projects", async () => {
  let resolveFirst!: (value: ReturnType<typeof availability>) => void;
  vi.mocked(getPublicFolderWorkflowContext)
    .mockImplementationOnce(() => new Promise(resolve => { resolveFirst = resolve; }))
    .mockResolvedValueOnce(availability("P2", false));
  const view = render(<TopBar activeRoute="workbench" titleOverride="Matrix Editor" projectFolderId="P1" />);
  view.rerender(<TopBar activeRoute="workbench" titleOverride="Matrix Editor" projectFolderId="P2" />);
  await act(async () => resolveFirst(availability("P1", true)));
  const folder = screen.getByRole<HTMLButtonElement>("button", { name: "Open project folder" });
  expect(folder.disabled).toBe(true);
  await userEvent.click(folder);
  expect(openLocalProjectFolder).not.toHaveBeenCalled();
});

it("refreshes the folder action only when the current project's folder changes", async () => {
  vi.mocked(getPublicFolderWorkflowContext)
    .mockResolvedValueOnce(availability("P1", false))
    .mockResolvedValueOnce(availability("P1", true));
  render(<TopBar activeRoute="workbench" titleOverride="Basic Information" projectFolderId="P1" />);
  const folder = screen.getByRole<HTMLButtonElement>("button", { name: "Open project folder" });
  await waitFor(() => expect(getPublicFolderWorkflowContext).toHaveBeenCalledTimes(1));
  expect(folder.disabled).toBe(true);
  act(() => window.dispatchEvent(new CustomEvent("connlab:project-folder-changed", { detail: "P2" })));
  expect(getPublicFolderWorkflowContext).toHaveBeenCalledTimes(1);
  act(() => window.dispatchEvent(new CustomEvent("connlab:project-folder-changed", { detail: "P1" })));
  await waitFor(() => expect(folder.disabled).toBe(false));
});

it("shows an actionable folder-path fallback in the header on browser-only hosts", async () => {
  vi.mocked(getPublicFolderWorkflowContext).mockResolvedValue(availability("P1", true));
  vi.mocked(openLocalProjectFolder).mockResolvedValue({ project_id: "P1", status: "unsupported", message: "Open this path in File Explorer.", local_official_folder_path: "D:/P1" });
  const user = userEvent.setup();
  const write = vi.spyOn(navigator.clipboard, "writeText").mockRejectedValueOnce(new Error("Clipboard unavailable"));
  render(<TopBar activeRoute="workbench" titleOverride="Fee Evaluation" projectFolderId="P1" />);
  const folder = screen.getByRole<HTMLButtonElement>("button", { name: "Open project folder" });
  await waitFor(() => expect(folder.disabled).toBe(false));
  await user.click(folder);
  expect((await screen.findByRole("alert")).textContent).toContain("D:/P1");
  await user.click(folder);
  expect((await screen.findByRole("status")).textContent).toContain("Project folder path copied");
  expect(write).toHaveBeenLastCalledWith("D:/P1");
  write.mockRestore();
});
