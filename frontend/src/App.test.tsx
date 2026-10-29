import type { ReactNode } from "react";
import { render, screen } from "@testing-library/react";
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
}));
vi.mock("./pages/ProjectMatrixEditorPage", () => ({ ProjectMatrixEditorPage: ({ projectId }: { projectId: string }) => <section aria-label="Matrix editor">{projectId}</section> }));

beforeEach(() => {
  sessionStorage.clear();
  vi.mocked(listProjectRegistryRows).mockResolvedValue([]);
  vi.mocked(libraryApi.getLibraryRuntime).mockResolvedValue({ library_root: "D:/test-library", projects_root: "D:/test-library/projects", data_root: "D:/test-library/data", database_path: "D:/test-library/data/connlab.sqlite3", configured: true, format_version: 1 });
  vi.mocked(libraryApi.listLibraryMembers).mockResolvedValue({ items: [] });
  vi.mocked(listLegacyProjects).mockResolvedValue([]);
});

it.each(["/projects/import", "/tools/project-library"])("opens project receiving from %s and returns to Projects", async (path) => {
  vi.mocked(libraryApi.getLibraryRuntime).mockResolvedValue({ library_root: "D:/test-library", projects_root: "D:/test-library/projects", data_root: "D:/test-library/data", database_path: "D:/test-library/data/connlab.sqlite3", configured: true, format_version: 1 });
  window.history.replaceState({}, "", path);
  render(<App />);
  expect(await screen.findByRole("heading", { name: "Import Projects" })).toBeTruthy();
  expect(await screen.findByRole("button", { name: "Choose Project Folders" })).toBeTruthy();
  expect(screen.getByTestId("active-area").textContent).toBe("projects");
  await userEvent.setup().click(screen.getByRole("button", { name: "Back to Projects" }));
  await userEvent.setup().click(await screen.findByRole("button", { name: "Import Projects" }));
  expect(window.location.pathname).toBe("/projects/import");
  expect(await screen.findByRole("button", { name: "Choose Project Folders" })).toBeTruthy();
});

it.each(["", "batch-1"])("preserves list and import return context for batch=%s before continuing to Matrix", async (batchId) => {
  const record: libraryApi.LibraryMember = { member_id: "member-1", project_id: "project-1", ltr_number: "DL-2026-09-032", title: "CPI-450", folder_path: "D:/test-library/projects/CPI", revision: 1, batch_id: batchId || null, snapshot_status: "current", snapshot_created_at: "2026-10-27", warnings: [], can_continue: true };
  vi.mocked(libraryApi.listLibraryMembers).mockResolvedValue({ items: [record] });
  vi.mocked(listProjectRegistryRows).mockResolvedValue([{ project_id: "project-1", display_project_id: "DL-2026-09-032", display_project_id_kind: "registered", has_registered_ltr: true, requestor: "Lab", status: "active", progress: 0, sample_description: "CPI-450" }]);
  vi.mocked(libraryApi.getLibraryMember).mockResolvedValue(record);
  vi.mocked(libraryApi.getLibraryFiles).mockResolvedValue({ items: [], warnings: [] });
  vi.mocked(libraryApi.getPortableInfo).mockResolvedValue({ status: "current", fingerprint: "current", created_at: "2026-10-27", format_version: 1, record_counts: { projects: 1 }, file_count: 2, warnings: [], blockers: [] });
  const suffix = batchId ? `?batch=${batchId}` : "";
  const user = userEvent.setup();
  window.history.replaceState({}, "", `/project-library${suffix}`);
  render(<App />);
  await user.click(await screen.findByText("Project Files", {exact:true}));
  await user.click(screen.getByRole("button", {name:"Browse Files"}));
  expect(window.location.pathname).toBe("/project-library/member-1");
  expect(window.location.search).toBe(suffix);
  await user.click(await screen.findByRole("button", { name: "Back to Projects" }));
  expect(window.location.pathname + window.location.search).toBe(`/projects${suffix}`);
  await user.click(await screen.findByRole("button", { name: "Import Projects" }));
  await user.click(await screen.findByText("Advanced"));
  await user.click(screen.getByRole("button", { name: "Link Folders Without Copying" }));
  await user.click(await screen.findByRole("button", { name: "Back to Import Projects" }));
  await user.click(await screen.findByRole("button", { name: "Back to Projects" }));
  expect(window.location.pathname + window.location.search).toBe(`/projects${suffix}`);
  await user.click(await screen.findByText("Project Files", {exact:true}));
  await user.click(screen.getByRole("button", {name:"Browse Files"}));
  await user.click(await screen.findByRole("button", { name: "Matrix" }));
  expect(window.location.pathname).toBe("/projects/project-1/matrix-editor");
  expect(await screen.findByLabelText("Matrix editor")).toBeTruthy();
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
  await user.click(await screen.findByRole("button", { name: "Open Manual legacy" }));
  expect(window.location.pathname).toBe("/legacy-projects/historical");
  await user.click(await screen.findByRole("button", { name: "Back to Projects" }));
  expect(await screen.findByRole("button", { name: "Open Manual legacy" })).toBeTruthy();
  expect(window.location.pathname).toBe("/projects");
  expect(screen.queryByRole("region", { name: "Project Workbench" })).toBeNull();
  await user.click(screen.getByRole("button", { name: "Import Projects" }));
  expect(window.location.pathname).toBe("/projects/import");
  expect(await screen.findByRole("button", { name: "Choose Project Folders" })).toBeTruthy();
});

it("keeps old folder-linking links accessible and returns to the common import flow", async () => {
  window.history.replaceState({}, "", "/tools/legacy-projects");
  render(<App />);
  expect(await screen.findByRole("heading", { name: "Link Existing Folders" })).toBeTruthy();
  await userEvent.setup().click(screen.getByRole("button", { name: "Back to Import Projects" }));
  await userEvent.setup().click(await screen.findByText("Advanced"));
  expect(screen.getByRole("button", { name: "Link Folders Without Copying" })).toBeTruthy();
  expect(window.location.pathname).toBe("/projects/import");
  await userEvent.setup().click(screen.getByRole("button", { name: "Link Folders Without Copying" }));
  expect(await screen.findByRole("heading", { name: "Link Existing Folders" })).toBeTruthy();
});

vi.mock("./components/layout/AppShell", () => ({
  AppShell: ({ children, onNavigate, activeRoute }: { children: ReactNode; onNavigate: (path: string) => void; activeRoute: string }) => (
    <>
      <output data-testid="active-area">{activeRoute}</output>
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
  ProjectWorkbenchPage: ({ onOpenBasicInformation }: { onOpenBasicInformation: () => void }) => (
    <section aria-label="Project Workbench">
      <button type="button" onClick={onOpenBasicInformation}>Basic Information</button>
    </section>
  ),
}));

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
