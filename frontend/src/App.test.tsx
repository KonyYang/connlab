import type { ReactNode } from "react";
import { act, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import { listLegacyProjects, getLegacyProject } from "./api/legacyProjects";
import { getProject, listProjectRegistryRows } from "./api/client";
vi.mock("./api/client", async () => ({ ...await vi.importActual<typeof import("./api/client")>("./api/client"), getProject: vi.fn(), listProjectRegistryRows: vi.fn(), getProjectLifecycle: vi.fn().mockRejectedValue(new Error("Lifecycle unavailable")) }));
import * as libraryApi from "./api/projectLibrary";
import * as receipts from "./api/materialReceipts";
import * as referenceApi from "./api/referenceLibrary";
vi.mock("./api/materialReceipts", () => ({ startArchivePreview: vi.fn(),getArchiveJob:vi.fn(),cancelArchiveJob:vi.fn(),confirmArchive:vi.fn(),refreshArchive:vi.fn(),getArchiveOperation:vi.fn(),retryArchive:vi.fn(),getReceiptRuntime: vi.fn(), pickReceiptFolder: vi.fn(), previewReceipt: vi.fn(), confirmReceipt: vi.fn(), getReceiptBatch: vi.fn(), createCopyContextSession: vi.fn(async()=>({session_id:"test-browser"})), updateCopyContext: vi.fn(async(session_id,intent)=>({session_id,intent,token:null,target:null})) }));
vi.mock("./api/reportShortcuts",()=>({getReportShortcuts:vi.fn(async()=>({key:"project:p1",items:[]}))}));
vi.mock("./api/referenceLibrary", () => ({ searchReferenceLibrary: vi.fn(), openReferenceFile: vi.fn() }));

vi.mock("./api/projectLibrary", async () => ({
  ...await vi.importActual<typeof import("./api/projectLibrary")>("./api/projectLibrary"),
  getLibraryRuntime: vi.fn(), listLibraryMembers: vi.fn(), getLibraryMember: vi.fn(), getLibraryFiles: vi.fn(), getPortableInfo: vi.fn(),
  pickLibraryFolder: vi.fn(), scanLibrarySources: vi.fn(), planLibraryIntake: vi.fn(), startLibraryBatch: vi.fn(),
  inspectPortableProject: vi.fn(), planPortableRestore: vi.fn(), restorePortableProject: vi.fn(), getLibraryBatch: vi.fn(), resumeLibraryBatch: vi.fn(),
}));
vi.mock("./pages/ProjectMatrixEditorPage", () => ({ ProjectMatrixEditorPage: ({ projectId }: { projectId: string }) => <section aria-label="Matrix editor">{projectId}</section> }));

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(receipts.startArchivePreview).mockResolvedValue({job_id:"preview"});
  vi.mocked(receipts.refreshArchive).mockResolvedValue({job_id:"scan"});
  vi.mocked(receipts.getArchiveJob).mockImplementation(async id=>({status:"done",result:id==="scan"?{warnings:[]}:{status:"ready",source_path:"C:/old/Connector",target_path:"D:/received/Connector",plan_id:"p",fingerprint:"h",batch_id:"b"}}));
  vi.mocked(receipts.getReceiptRuntime).mockResolvedValue({ root_path: "D:/received", revision: 1, configured: true, available: true });
  vi.mocked(receipts.pickReceiptFolder).mockResolvedValue("C:/old/Connector");
  vi.mocked(referenceApi.searchReferenceLibrary).mockResolvedValue({ projects: [], files: [], warnings: [], total: 0 });
  sessionStorage.clear(); localStorage.clear();
  vi.mocked(getProject).mockImplementation(async projectId => ({
    project_id: projectId, product_name: "Connector", requestor: "Lab",
    status: "active", is_legacy_temporary: false,
  }));
  vi.mocked(listProjectRegistryRows).mockResolvedValue([]);
  vi.mocked(libraryApi.getLibraryRuntime).mockResolvedValue({ library_root: "D:/test-library", projects_root: "D:/test-library/projects", data_root: "D:/test-library/data", database_path: "D:/test-library/data/connlab.sqlite3", configured: true, format_version: 1 });
  vi.mocked(libraryApi.listLibraryMembers).mockResolvedValue({ items: [] });
  vi.mocked(libraryApi.pickLibraryFolder).mockResolvedValue(null);
  vi.mocked(listLegacyProjects).mockResolvedValue([]);
});

it("routes ordinary receipt to the library without old adoption or recovery calls", async () => {
  window.history.replaceState({}, "", "/projects");
  const user = userEvent.setup(); render(<App />);
  await user.click(await screen.findByRole("button", { name: "Receive materials" }));
  expect(await screen.findByRole("dialog", { name: "Receive project materials" })).toBeTruthy();
  expect(window.location.pathname).toBe("/reference");
  await screen.findByRole("button", { name: "Receive",exact:true });
  expect(receipts.pickReceiptFolder).toHaveBeenCalledOnce();
  expect(receipts.confirmReceipt).not.toHaveBeenCalled();
  expect(libraryApi.startLibraryBatch).not.toHaveBeenCalled();
  expect(libraryApi.inspectPortableProject).not.toHaveBeenCalled();
  expect(libraryApi.getPortableInfo).not.toHaveBeenCalled();
});

it("closing archive confirmation retains the ordinary library", async () => {
  window.history.replaceState({}, "", "/reference?receive=1");
  const user = userEvent.setup(); render(<App />);
  await user.click(await screen.findByRole("button", { name: "Cancel", exact: true }));
  expect(screen.queryByRole("dialog")).toBeNull();
  expect(receipts.pickReceiptFolder).toHaveBeenCalled();
  expect(window.location.search).toBe("");
});

it.each(["/projects/import", "/projects/import?batch=old-batch", "/tools/project-library"])("retires the old receiving page at %s safely",async(path)=>{
 window.history.replaceState({},"",path);render(<App/>);
 expect(await screen.findByRole("region",{name:"Project materials library"})).toBeTruthy();
 expect(screen.queryByRole("heading",{name:"Import Projects"})).toBeNull();
 expect(screen.queryByRole("region",{name:"Project Workbench"})).toBeNull();
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
  await user.click(await screen.findByRole("button", { name: "Receive materials" }));
  expect(await screen.findByRole("dialog", { name: "Receive project materials" })).toBeTruthy();
  expect(window.location.pathname).toBe("/reference");
  await user.click(screen.getByRole("button", { name: "Cancel", exact: true }));
  await user.click(within(screen.getByRole("navigation", { name: "Test sidebar" })).getByRole("button", { name: "Projects" }));
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
  expect(window.location.pathname).toBe("/reference");
  expect(new URLSearchParams(window.location.search).get("entry")).toBe("linked:historical");
  await user.click(within(screen.getByRole("navigation", { name: "Test sidebar" })).getByRole("button", { name: "Projects" }));
  expect(await screen.findByRole("button", { name: "Open Manual legacy" })).toBeTruthy();
  expect(window.location.pathname).toBe("/projects");
  expect(screen.queryByRole("region", { name: "Project Workbench" })).toBeNull();
  await user.click(screen.getByRole("button", { name: "Receive materials" }));
  expect(await screen.findByRole("dialog", { name: "Receive project materials" })).toBeTruthy();
  expect(window.location.pathname).toBe("/reference");
  expect(libraryApi.pickLibraryFolder).not.toHaveBeenCalled();
});

it("keeps the old direct folder-linking URL accessible without exposing it in the common import flow", async () => {
  window.history.replaceState({}, "", "/tools/legacy-projects");
  render(<App />);
  expect(await screen.findByRole("heading", { name: "Link Existing Folders" })).toBeTruthy();
  await userEvent.setup().click(screen.getByRole("button", { name: "Back to Import Projects" }));
  expect(window.location.pathname).toBe("/projects/import");
  expect(await screen.findByRole("region", { name: "Project materials library" })).toBeTruthy();
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
        <button type="button" onClick={() => onNavigate("/reference")}>Library</button>
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
  await user.click(within(screen.getByRole("navigation", { name: "Test sidebar" })).getByRole("button", { name: "Projects" }));
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
    await user.click(within(screen.getByRole("navigation", { name: "Test sidebar" })).getByRole("button", { name: "Projects" }));

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


it("waits for source preparation before opening the receipt confirmation", async () => {
  let choose!: (source: string) => void;
  let prepare!: (result: receipts.ArchiveJob) => void;
  vi.mocked(receipts.pickReceiptFolder).mockImplementation(() => new Promise(resolve => { choose = resolve; }));
  vi.mocked(receipts.getArchiveJob).mockImplementation(async id => id === "preview"
    ? new Promise(resolve => { prepare = resolve; })
    : {status: "done", result: {warnings: []}});
  window.history.replaceState({}, "", "/reference?receive=1");
  const mounted = render(<App />);
  await waitFor(() => expect(receipts.pickReceiptFolder).toHaveBeenCalledOnce());
  expect(screen.queryByRole("dialog")).toBeNull();
  expect(screen.queryByRole("button", {name: "Receive", exact: true})).toBeNull();
  expect(receipts.startArchivePreview).not.toHaveBeenCalled();

  await act(async () => choose("C:/old/Connector"));
  await screen.findByText("Preparing materials…");
  expect(screen.queryByRole("dialog")).toBeNull();
  expect(receipts.confirmArchive).not.toHaveBeenCalled();
  await act(async () => prepare({status: "done", result: {
    status: "ready", source_path: "C:/old/Connector", target_path: "D:/received/Connector",
    plan_id: "p", fingerprint: "h", batch_id: "b",
  }}));
  const confirmation = await screen.findByRole("dialog", {name: "Receive project materials"});
  expect(screen.getAllByRole("dialog")).toHaveLength(1);
  expect(within(confirmation).getByText("Source: C:/old/Connector")).toBeTruthy();
  expect(within(confirmation).getByText("Target: D:/received/Connector")).toBeTruthy();
  expect(within(confirmation).getByRole("button", {name: "Receive", exact: true})).toBeTruthy();
  expect(receipts.confirmArchive).not.toHaveBeenCalled();
  expect(receipts.confirmReceipt).not.toHaveBeenCalled();
  expect(libraryApi.pickLibraryFolder).not.toHaveBeenCalled();
  mounted.unmount();
});


it("keeps copy intent separate from sidebar last-project navigation memory",async()=>{
 const user=userEvent.setup();window.history.replaceState({},"","/projects/P1");
 render(<App/>);
 await screen.findByRole("region",{name:"Project Workbench"});
 await waitFor(()=>expect(receipts.updateCopyContext).toHaveBeenLastCalledWith("test-browser",1,"P1"));
 const count=vi.mocked(receipts.updateCopyContext).mock.calls.length;
 await user.click(screen.getByRole("button",{name:"Library",exact:true}));
 await screen.findByRole("region",{name:"Project materials library"});
 expect(receipts.updateCopyContext).toHaveBeenCalledTimes(count);
 await user.click(screen.getByRole("button",{name:"Settings",exact:true}));
 await waitFor(()=>expect(receipts.updateCopyContext).toHaveBeenLastCalledWith("test-browser",2,null));
 expect(screen.getByTestId("sidebar-project").textContent).toBe("P1");
 await user.click(screen.getByRole("button",{name:"Library",exact:true}));
 await waitFor(()=>expect(receipts.updateCopyContext).toHaveBeenLastCalledWith("test-browser",3,null));
 expect(screen.getByTestId("sidebar-project").textContent).toBe("P1");
});
