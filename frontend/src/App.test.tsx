import type { ReactNode } from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { listLegacyProjects, getLegacyProject } from "./api/legacyProjects";
import { listProjectRegistryRows } from "./api/client";
vi.mock("./api/client", async () => ({ ...await vi.importActual<typeof import("./api/client")>("./api/client"), listProjectRegistryRows: vi.fn(), getProjectLifecycle: vi.fn().mockRejectedValue(new Error("Lifecycle unavailable")) }));
import * as libraryApi from "./api/projectLibrary";

vi.mock("./api/projectLibrary", async () => ({
  ...await vi.importActual<typeof import("./api/projectLibrary")>("./api/projectLibrary"),
  getLibraryRuntime: vi.fn(), listLibraryMembers: vi.fn(), getLibraryMember: vi.fn(), getLibraryFiles: vi.fn(), getPortableInfo: vi.fn(),
  pickLibraryFolder: vi.fn(), scanLibrarySources: vi.fn(), planLibraryIntake: vi.fn(), startLibraryBatch: vi.fn(),
  inspectPortableProject: vi.fn(), planPortableRestore: vi.fn(), restorePortableProject: vi.fn(), getLibraryBatch: vi.fn(), resumeLibraryBatch: vi.fn(),
}));
vi.mock("./pages/ProjectMatrixEditorPage", () => ({ ProjectMatrixEditorPage: ({ projectId }: { projectId: string }) => <section aria-label="Matrix editor">{projectId}</section> }));

beforeEach(() => {
  vi.clearAllMocks();
  sessionStorage.clear(); localStorage.clear();
  vi.mocked(listProjectRegistryRows).mockResolvedValue([]);
  vi.mocked(libraryApi.getLibraryRuntime).mockResolvedValue({ library_root: "D:/test-library", projects_root: "D:/test-library/projects", data_root: "D:/test-library/data", database_path: "D:/test-library/data/connlab.sqlite3", configured: true, format_version: 1 });
  vi.mocked(libraryApi.listLibraryMembers).mockResolvedValue({ items: [] });
  vi.mocked(libraryApi.pickLibraryFolder).mockResolvedValue(null);
  vi.mocked(listLegacyProjects).mockResolvedValue([]);
});

it("opens the native project-folder picker directly from Projects and stays there when cancelled", async () => {
  window.history.replaceState({}, "", "/projects");
  const user = userEvent.setup();
  render(<App />);

  await user.click(await screen.findByRole("button", { name: "Import Projects" }));

  await waitFor(() => expect(libraryApi.pickLibraryFolder).toHaveBeenCalledOnce());
  expect(window.location.pathname).toBe("/projects");
  expect(screen.getByTestId("active-area").textContent).toBe("projects");
  expect(screen.queryByRole("dialog", { name: "Import project" })).toBeNull();
  expect(screen.queryByRole("heading", { name: "Import Projects" })).toBeNull();
});

it("receives one safe selected project in the background and opens its workspace", async () => {
  const source = "D:/old/DL-2026-09-032 Connector";
  vi.mocked(libraryApi.pickLibraryFolder).mockResolvedValue(source);
  vi.mocked(libraryApi.scanLibrarySources).mockResolvedValue({
    items: [{ source_path: source, title: "Connector", ltr_number: "DL-2026-09-032", kind: "project", warnings: [], child_folders: [] }],
    warnings: [], truncated: false,
  });
  vi.mocked(libraryApi.planLibraryIntake).mockResolvedValue({
    plan_id: "plan", fingerprint: "verified", warnings: [],
    items: [{ source_path: source, target_path: "D:/test-library/projects/DL-2026-09-032", title: "Connector", ltr_number: "DL-2026-09-032", status: "ready", warnings: [], can_keep_separate: false }],
  });
  vi.mocked(libraryApi.startLibraryBatch).mockResolvedValue({
    batch_id: "batch", status: "completed", counts: { added: 1, already_added: 0, review: 0, failed: 0 },
    items: [{ source_path: source, status: "added", message: "Added", member_id: "member" }],
  });
  vi.mocked(libraryApi.getLibraryMember).mockResolvedValue({
    member_id: "member", project_id: "verified-project", ltr_number: "DL-2026-09-032", title: "Connector",
    folder_path: "D:/test-library/projects/DL-2026-09-032", revision: 1, batch_id: "batch",
    snapshot_status: "missing", snapshot_created_at: null, warnings: [], can_continue: true,
  });
  window.history.replaceState({}, "", "/projects");
  const user = userEvent.setup();
  render(<App />);

  await user.click(await screen.findByRole("button", { name: "Import Projects" }));

  await waitFor(() => expect(window.location.pathname).toBe("/projects/verified-project"));
  expect(await screen.findByRole("region", { name: "Project Workbench" })).toBeTruthy();
  expect(screen.queryByRole("heading", { name: "Import Projects" })).toBeNull();
});

it("stays on Projects and opens a focused decision dialog only when information is missing", async () => {
  const source = "D:/old/Connector";
  vi.mocked(libraryApi.pickLibraryFolder).mockResolvedValue(source);
  vi.mocked(libraryApi.scanLibrarySources).mockResolvedValue({
    items: [{ source_path: source, title: "Connector", ltr_number: null, kind: "project", warnings: [], child_folders: [] }],
    warnings: [], truncated: false, selection_issue: "needs_ltr",
  });
  window.history.replaceState({}, "", "/projects");
  const user = userEvent.setup();
  render(<App />);

  await user.click(await screen.findByRole("button", { name: "Import Projects" }));

  expect(await screen.findByRole("dialog", { name: "Import project" })).toBeTruthy();
  expect(await screen.findByRole("textbox", { name: "LTR number" })).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Choose Project Folder" })).toBeNull();
  expect(window.location.pathname).toBe("/projects");
});

it("does not reopen the folder picker after leaving Projects from an import decision", async () => {
  const source = "D:/old/Connector";
  vi.mocked(libraryApi.pickLibraryFolder).mockResolvedValue(source);
  vi.mocked(libraryApi.scanLibrarySources).mockResolvedValue({
    items: [{ source_path: source, title: "Connector", ltr_number: null, kind: "project", warnings: [], child_folders: [] }],
    warnings: [], truncated: false, selection_issue: "needs_ltr",
  });
  window.history.replaceState({}, "", "/projects");
  const user = userEvent.setup();
  render(<App />);

  await user.click(await screen.findByRole("button", { name: "Import Projects" }));
  expect(await screen.findByRole("dialog", { name: "Import project" })).toBeTruthy();
  await user.click(screen.getByRole("button", { name: "Settings" }));
  expect(window.location.pathname).toBe("/settings");
  await user.click(screen.getByRole("button", { name: "Projects" }));

  expect(await screen.findByRole("button", { name: "Import Projects" })).toBeTruthy();
  expect(screen.queryByRole("dialog", { name: "Import project" })).toBeNull();
  expect(libraryApi.pickLibraryFolder).toHaveBeenCalledOnce();
});

it.each(["/projects/import", "/projects/import?batch=old-batch", "/tools/project-library"])("opens project receiving from %s and returns to all Projects", async (path) => {
  vi.mocked(libraryApi.getLibraryRuntime).mockResolvedValue({ library_root: "D:/test-library", projects_root: "D:/test-library/projects", data_root: "D:/test-library/data", database_path: "D:/test-library/data/connlab.sqlite3", configured: true, format_version: 1 });
  window.history.replaceState({}, "", path);
  render(<App />);
  expect(await screen.findByRole("heading", { name: "Import Projects" })).toBeTruthy();
  expect(await screen.findByRole("button", { name: "Choose Project Folder" })).toBeTruthy();
  expect(screen.getByTestId("active-area").textContent).toBe("projects");
  await userEvent.setup().click(screen.getByRole("button", { name: "Back to Projects" }));
  expect(window.location.pathname + window.location.search).toBe("/projects");
  await userEvent.setup().click(await screen.findByRole("button", { name: "Import Projects" }));
  await waitFor(() => expect(libraryApi.pickLibraryFolder).toHaveBeenCalled());
  expect(window.location.pathname).toBe("/projects");
  expect(screen.queryByRole("heading", { name: "Import Projects" })).toBeNull();
});

it("shows an imported project in the normal workbench without a special file action", async () => {
  window.history.replaceState({}, "", "/projects/project-1");
  render(<App />);
  expect(await screen.findByRole("region", { name: "Project Workbench" })).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Browse Files" })).toBeNull();
});

it.each(["", "batch-1"])("preserves browsing context but returns from import to all Projects for batch=%s", async (batchId) => {
  const record: libraryApi.LibraryMember = { member_id: "member-1", project_id: "project-1", ltr_number: "DL-2026-09-032", title: "CPI-450", folder_path: "D:/test-library/projects/CPI", revision: 1, batch_id: batchId || null, snapshot_status: "current", snapshot_created_at: "2026-10-27", warnings: [], can_continue: true };
  vi.mocked(libraryApi.listLibraryMembers).mockResolvedValue({ items: [record] });
  vi.mocked(listProjectRegistryRows).mockResolvedValue([{ project_id: "project-1", display_project_id: "DL-2026-09-032", display_project_id_kind: "registered", has_registered_ltr: true, requestor: "Lab", status: "active", progress: 0, sample_description: "CPI-450" }]);
  vi.mocked(libraryApi.getLibraryMember).mockResolvedValue(record);
  vi.mocked(libraryApi.getLibraryFiles).mockResolvedValue({ items: [], warnings: [] });
  vi.mocked(libraryApi.getPortableInfo).mockResolvedValue({ status: "current", fingerprint: "current", created_at: "2026-10-27", format_version: 1, record_counts: { projects: 1 }, file_count: 2, warnings: [], blockers: [] });
  const suffix = batchId ? `?batch=${batchId}` : "";
  const user = userEvent.setup();
  window.history.replaceState({}, "", `/project-library/member-1${suffix}`);
  render(<App />);
  await user.click(await screen.findByRole("button", { name: "Back to Projects" }));
  expect(window.location.pathname + window.location.search).toBe(`/projects${suffix}`);
  await user.click(await screen.findByRole("button", { name: "Import Projects" }));
  await waitFor(() => expect(libraryApi.pickLibraryFolder).toHaveBeenCalled());
  expect(window.location.pathname + window.location.search).toBe(`/projects${suffix}`);
  await user.click(await screen.findByRole("button", { name: /Open Workbench.*DL-2026-09-032/ }));
  expect(window.location.pathname).toBe("/projects/project-1");
  expect(await screen.findByRole("region", { name: "Project Workbench" })).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Browse Files" })).toBeNull();
});

vi.mock("./api/legacyProjects", async () => ({
  ...await vi.importActual<typeof import("./api/legacyProjects")>("./api/legacyProjects"),
  listLegacyProjects: vi.fn(), getLegacyProject: vi.fn(),
}));

it("opens the unified list from the old Legacy URL and returns there after browsing", async () => {
  const record = { record_id: "historical", name: "Manual legacy", number: null, number_evidence: [], folder_path: "D:/old", notes: [], revision: 1, imported_at: "2026-01-01", updated_at: "2026-01-01" };
  vi.mocked(listLegacyProjects).mockResolvedValue([record]);
  vi.mocked(getLegacyProject).mockResolvedValue(record);
  window.history.replaceState({}, "", "/projects?view=legacy");
  const user = userEvent.setup();
  render(<App />);
  await user.selectOptions(await screen.findByLabelText("Project view"), "all");
  await user.click(await screen.findByRole("button", { name: "Open Manual legacy" }));
  expect(window.location.pathname).toBe("/legacy-projects/historical");
  await user.click(await screen.findByRole("button", { name: "Back to Projects" }));
  expect(await screen.findByRole("button", { name: "Open Manual legacy" })).toBeTruthy();
  expect(window.location.pathname).toBe("/projects");
  expect(screen.queryByRole("region", { name: "Project Workbench" })).toBeNull();
  await user.click(screen.getByRole("button", { name: "Import Projects" }));
  await waitFor(() => expect(libraryApi.pickLibraryFolder).toHaveBeenCalled());
  expect(window.location.pathname).toBe("/projects");
  expect(screen.queryByRole("heading", { name: "Import Projects" })).toBeNull();
});

it("keeps the old direct folder-linking URL accessible without exposing it in the common import flow", async () => {
  window.history.replaceState({}, "", "/tools/legacy-projects");
  render(<App />);
  expect(await screen.findByRole("heading", { name: "Link Existing Folders" })).toBeTruthy();
  await userEvent.setup().click(screen.getByRole("button", { name: "Back to Import Projects" }));
  expect(window.location.pathname).toBe("/projects/import");
  expect(await screen.findByRole("button", { name: "Choose Project Folder" })).toBeTruthy();
  expect(screen.queryByText("More Options")).toBeNull();
  expect(screen.queryByRole("button", { name: "Link Folders Without Copying" })).toBeNull();
});

vi.mock("./components/layout/AppShell", () => ({
  AppShell: ({ children, onNavigate, activeRoute, projectId }: { children: ReactNode; onNavigate: (path: string) => void; activeRoute: string; projectId?: string | null }) => (
    <>
      <output data-testid="active-area">{activeRoute}</output>
      <output data-testid="sidebar-project">{projectId ?? "none"}</output>
      <nav aria-label="Test sidebar">
        <button type="button" onClick={() => onNavigate("/settings")}>Settings</button>
        <button type="button" onClick={() => onNavigate("/projects")}>Projects</button>
      </nav>
      {children}
    </>
  ),
}));

vi.mock("./components/support/FrontendDiagnosticsReporter", () => ({
  FrontendDiagnosticsReporter: () => null,
}));

vi.mock("./pages/ProjectWorkbenchPage", () => ({
  ProjectWorkbenchPage: ({ onOpenBasicInformation, onBack }: { onOpenBasicInformation: () => void; onBack: () => void }) => (
    <section aria-label="Project Workbench">
      <button type="button" onClick={onOpenBasicInformation}>Basic Information</button>
      <button type="button" onClick={onBack}>Close project</button>
    </section>
  ),
}));

it("passes the open project to the sidebar across page changes and clears it on close", async () => {
  window.history.replaceState({}, "", "/projects/P1");
  const user = userEvent.setup();
  render(<App />);
  expect(screen.getByTestId("sidebar-project").textContent).toBe("P1");
  await user.click(screen.getByRole("button", { name: "Settings" }));
  expect(screen.getByTestId("sidebar-project").textContent).toBe("P1");
  await user.click(screen.getByRole("button", { name: "Projects" }));
  await user.click(await screen.findByRole("button", { name: "Close project" }));
  expect(screen.getByTestId("sidebar-project").textContent).toBe("none");
});

vi.mock("./pages/ProjectBasicInformationPage", () => ({
  ProjectBasicInformationPage: ({
    projectId,
    initialValuesMode,
    onDraftSaved,
    onBackToWorkbench,
  }: {
    projectId: string;
    initialValuesMode: "draft" | "authoritative";
    onDraftSaved: () => void;
    onBackToWorkbench: (options: { refreshBasicInformation: boolean }) => void;
  }) => (
    <section aria-label="Basic Information">
      <output data-testid="basic-information-entry-mode">
        {projectId}:{initialValuesMode}
      </output>
      <button type="button" onClick={onDraftSaved}>Save draft</button>
      <button
        type="button"
        onClick={() => onBackToWorkbench({ refreshBasicInformation: false })}
      >
        Cancel
      </button>
    </section>
  ),
}));

vi.mock("./pages/SettingsPage", () => ({
  SettingsPage: () => <section aria-label="Settings page" />,
}));

describe("Basic Information route entry behavior", () => {
  beforeEach(() => {
    window.history.replaceState({}, "", "/projects/P1");
  });

  it("imports authority on normal entry and after Cancel", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Basic Information" }));
    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );

    await user.click(screen.getByRole("button", { name: "Cancel" }));
    await user.click(await screen.findByRole("button", { name: "Basic Information" }));

    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );
  });

  it("imports authority on a fresh sidebar return", async () => {
    window.history.replaceState({}, "", "/projects/P1");
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Basic Information" }));
    await screen.findByTestId("basic-information-entry-mode");
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    await user.click(await screen.findByRole("button", { name: "Basic Information" }));
    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );

    await user.click(screen.getByRole("button", { name: "Settings" }));
    expect(await screen.findByLabelText("Settings page")).toBeTruthy();
    await user.click(screen.getByRole("button", { name: "Projects" }));

    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );
  });

  it("keeps normal authority entry after cancelling and navigating elsewhere", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Basic Information" }));
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    await user.click(await screen.findByRole("button", { name: "Settings" }));
    await user.click(await screen.findByRole("button", { name: "Projects" }));
    await user.click(await screen.findByRole("button", { name: "Basic Information" }));

    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );
  });

  it("loads authority for a direct URL without a saved editing session", async () => {
    window.history.replaceState({}, "", "/projects/P1/basic-information");
    render(<App />);
    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );
  });

  it("recovers saved session edits on reload without changing fresh-entry behavior", async () => {
    const user = userEvent.setup();
    const mounted = render(<App />);
    await user.click(await screen.findByRole("button", { name: "Basic Information" }));
    await user.click(await screen.findByRole("button", { name: "Save draft" }));
    mounted.unmount();
    render(<App />);
    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:draft"
    );
    await user.click(screen.getByRole("button", { name: "Cancel" }));
    await user.click(await screen.findByRole("button", { name: "Basic Information" }));
    expect((await screen.findByTestId("basic-information-entry-mode")).textContent).toBe(
      "P1:authoritative"
    );
  });
});
