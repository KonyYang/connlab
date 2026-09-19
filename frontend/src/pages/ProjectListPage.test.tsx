import { render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type {
  ProjectLifecycleResponse,
  ProjectRegistryRow,
} from "../api/client";
import {
  getProjectLifecycle,
  listProjectRegistryRows,
} from "../api/client";
import { ProjectListPage } from "./ProjectListPage";
import * as managementApi from "../api/projectRegistryManagement";
vi.mock("../api/projectRegistryManagement", () => ({listManagedProjects: vi.fn(), previewProjectRegistryAction: vi.fn(), moveProjectToTrash: vi.fn(), restoreManagedProject: vi.fn()}));

vi.mock("../api/client", async () => {
  const actual = await vi.importActual<typeof import("../api/client")>("../api/client");
  return {
    ...actual,
    listProjectRegistryRows: vi.fn(),
    getProjectLifecycle: vi.fn(),
  };
});

const listProjectRegistryRowsMock = vi.mocked(listProjectRegistryRows);
const getProjectLifecycleMock = vi.mocked(getProjectLifecycle);

describe("ProjectListPage lifecycle registry views", () => {
  beforeEach(() => {
    window.sessionStorage.clear();
    listProjectRegistryRowsMock.mockReset();
    getProjectLifecycleMock.mockReset();
    vi.mocked(managementApi.listManagedProjects).mockResolvedValue([]);
  });

  it("labels the normal registry area by its actual function", async () => {
    mockRows([]);
    render(<ProjectListPage onOpenProject={vi.fn()} />);

    const active = await screen.findByRole("button", { name: "Active" });
    const search = screen.getByRole("textbox", { name: "Search projects" });
    const projectView = screen.getByRole("combobox", { name: "Project view" });
    const toolbar = search.closest(".register-toolbar");

    expect(active).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Projects" })).toBeNull();
    expect(toolbar).not.toBeNull();
    expect(toolbar?.contains(projectView)).toBe(true);
    expect(toolbar?.contains(active)).toBe(true);
    expect(Boolean(search.compareDocumentPosition(active) & Node.DOCUMENT_POSITION_FOLLOWING)).toBe(true);
    expect(Boolean(projectView.compareDocumentPosition(active) & Node.DOCUMENT_POSITION_FOLLOWING)).toBe(true);
  });

  it("places registry controls in the shell top-bar action slot when available", async () => {
    const topBarActions = document.createElement("div");
    topBarActions.dataset.topBarActions = "true";
    document.body.appendChild(topBarActions);
    try {
      mockRows([]);
      render(<ProjectListPage onOpenProject={vi.fn()} />);

      await screen.findByRole("button", { name: "Active" });
      expect(topBarActions.querySelector(".register-toolbar")).not.toBeNull();
      expect(document.querySelector(".project-register-panel > .register-toolbar")).toBeNull();
    } finally {
      topBarActions.remove();
    }
  });

  it("moves an exact record into the recycle bin, exits the normal view and safely previews Undo", async () => {
    const user = userEvent.setup();
    mockRows([registryRow({project_id: "original-A", display_project_id: "DL-2026-01-002"})]);
    mockLifecycle({"original-A": lifecycle({project_id: "original-A", allowed_actions: ["close"]})});
    const entry: managementApi.ProjectRegistryEntry = {project_id: "original-A", display_project_id: "DL-2026-01-002",
      sample_description: "Original connector", test_item: "LLCR", requestor: "Lab", created_on: "2026-01-01",
      lifecycle_state: "active", close_reason_label: null, registry_state: "active", registry_revision: 0, changed_at: null, reason: null};
    vi.mocked(managementApi.previewProjectRegistryAction).mockResolvedValue({project: entry, action: "trash", token: "token-A", conflicts: [], blockers: [], warnings: [], retained_data: []});
    vi.mocked(managementApi.moveProjectToTrash).mockResolvedValue({...entry, registry_state: "trash", registry_revision: 1});
    render(<ProjectListPage onOpenProject={vi.fn()} />);
    await user.click(await screen.findByRole("button", {name: "Delete project DL-2026-01-002"}));
    const dialog = within(await screen.findByRole("dialog"));
    await user.selectOptions(await dialog.findByLabelText("Deletion reason"), "Created by mistake");
    listProjectRegistryRowsMock.mockResolvedValue([]);
    await user.click(dialog.getByRole("button", {name: "Move to recycle bin"}));
    expect(managementApi.moveProjectToTrash).toHaveBeenCalledWith("original-A", {token: "token-A", reason: "Created by mistake"});
    await waitFor(() => expect(screen.queryByRole("table")).toBeNull());
    await user.click(screen.getByRole("button", {name: "Undo"}));
    expect(managementApi.previewProjectRegistryAction).toHaveBeenLastCalledWith("original-A", "restore");
  });

  it("offers a recycle bin with separate record identities and history restore", async () => {
    const user = userEvent.setup(); mockRows([]);
    vi.mocked(managementApi.listManagedProjects).mockResolvedValue([{project_id: "unique-deleted-A", display_project_id: "DL-2026-01-002",
      sample_description: "Old connector", test_item: "LLCR", requestor: "Lab", created_on: "2026-01-01",
      lifecycle_state: "closed", close_reason_label: "Completed", registry_state: "trash", registry_revision: 1, changed_at: "2026-01-02", reason: "Duplicate"}]);
    render(<ProjectListPage onOpenProject={vi.fn()} />);
    await user.click(screen.getByRole("button", {name: "Trash"}));
    expect(await screen.findByText("Old connector")).toBeTruthy();
    expect(screen.getByText(/Record unique-delet/)).toBeTruthy();
    expect(screen.getByRole("button", {name: "View read-only details"})).toBeTruthy();
    await user.click(screen.getByRole("button", {name: "History"}));
    await waitFor(() => expect(managementApi.listManagedProjects).toHaveBeenLastCalledWith("history"));
  });

  it("keeps project closing in Workbench instead of exposing it in the registry", async () => {
    mockRows([registryRow({project_id: "A", display_project_id: "DL-2026-01-002"})]);
    mockLifecycle({"A": lifecycle({project_id: "A", allowed_actions: ["close"]})});
    render(<ProjectListPage onOpenProject={vi.fn()} />);
    const row = await screen.findByText("DL-2026-01-002");
    const actions = row.closest("tr")?.querySelector(".project-registry-action-buttons");
    expect(actions?.querySelector('[aria-label="Close project DL-2026-01-002"]')).toBeNull();
    expect(screen.queryByRole("dialog", {name: /Close project/})).toBeNull();
  });

  it("defaults to the On-going view for active operational projects", async () => {
    mockRows([
      registryRow({ project_id: "P-ACTIVE", display_project_id: "DL-2026-06-001" }),
      registryRow({
        project_id: "P-CLOSED",
        display_project_id: "DL-2026-06-002",
        status: "closed",
      }),
    ]);
    mockLifecycle({
      "P-ACTIVE": lifecycle({ project_id: "P-ACTIVE" }),
      "P-CLOSED": lifecycle({
        project_id: "P-CLOSED",
        lifecycle_state: "closed",
        closure_type: "completed",
        status: "closed",
      }),
    });

    render(<ProjectListPage onOpenProject={vi.fn()} />);

    expect(await screen.findByText("DL-2026-06-001")).toBeTruthy();
    expect(screen.queryByText("DL-2026-06-002")).toBeNull();
    expect(screen.getByLabelText("Project view")).toHaveProperty("value", "ongoing");
  });

  it("defaults Project IDs to newest first and lets the operator switch to oldest first", async () => {
    const user = userEvent.setup();
    mockRows([
      registryRow({ project_id: "P-OLD", display_project_id: "DL-2026-06-001" }),
      registryRow({ project_id: "P-NEW", display_project_id: "DL-2026-07-003" }),
    ]);
    mockLifecycle({
      "P-OLD": lifecycle({ project_id: "P-OLD" }),
      "P-NEW": lifecycle({ project_id: "P-NEW" }),
    });

    render(<ProjectListPage onOpenProject={vi.fn()} />);

    expect(await projectIdsInTable()).toEqual(["DL-2026-07-003", "DL-2026-06-001"]);
    const sortButton = screen.getByRole("button", { name: "Sort Project ID ascending" });

    await user.click(sortButton);

    expect(await projectIdsInTable()).toEqual(["DL-2026-06-001", "DL-2026-07-003"]);
    expect(screen.getByRole("button", { name: "Sort Project ID descending" })).toBeTruthy();
  });

  it("shows completed and administrative closed projects in the Closed view", async () => {
    const user = userEvent.setup();
    mockRows([
      registryRow({ project_id: "P-CLOSED-C", display_project_id: "DL-2026-06-010", status: "closed" }),
      registryRow({ project_id: "P-CLOSED-A", display_project_id: "DL-2026-06-011", status: "closed" }),
    ]);
    mockLifecycle({
      "P-CLOSED-C": lifecycle({
        project_id: "P-CLOSED-C",
        lifecycle_state: "closed",
        closure_type: "completed",
        status: "closed",
      }),
      "P-CLOSED-A": lifecycle({
        project_id: "P-CLOSED-A",
        lifecycle_state: "closed",
        closure_type: "administrative",
        status: "closed",
      }),
    });

    render(<ProjectListPage onOpenProject={vi.fn()} />);
    await user.selectOptions(await screen.findByLabelText("Project view"), "closed");

    expect(await screen.findByText("DL-2026-06-010")).toBeTruthy();
    expect(screen.getByText("Closed: Completed")).toBeTruthy();
    expect(screen.getByText("View readonly completed archive")).toBeTruthy();
    expect(screen.getByText("DL-2026-06-011")).toBeTruthy();
    expect(screen.getByText("Closed: Administrative")).toBeTruthy();
    expect(screen.getByText("View readonly administrative archive")).toBeTruthy();
    expect(screen.getAllByRole("button", { name: /Open archive/ })).toHaveLength(2);
  });

  it("keeps stopped temporary projects in Planning and stopped registered projects in On-going", async () => {
    const user = userEvent.setup();
    mockRows([
      registryRow({
        project_id: "P-STOP-TMP",
        display_project_id: "TMP-AABBCCDD",
        display_project_id_kind: "temporary",
        has_registered_ltr: false,
        ltr_number: null,
        registered_ltr_number: null,
        status: "cancelled",
      }),
      registryRow({
        project_id: "P-STOP-DL",
        display_project_id: "DL-2026-06-012",
        status: "cancelled",
      }),
    ]);
    mockLifecycle({
      "P-STOP-TMP": lifecycle({
        project_id: "P-STOP-TMP",
        lifecycle_state: "stopped",
        status: "cancelled",
        readonly: true,
      }),
      "P-STOP-DL": lifecycle({
        project_id: "P-STOP-DL",
        lifecycle_state: "stopped",
        status: "cancelled",
        readonly: true,
      }),
    });

    render(<ProjectListPage onOpenProject={vi.fn()} />);

    expect(await screen.findByText("DL-2026-06-012")).toBeTruthy();
    expect(screen.queryByText("TMP-AABBCCDD")).toBeNull();
    expect(screen.getByText("Review or resume in Workbench")).toBeTruthy();
    expect(screen.getByRole("button", { name: /Open Workbench.*DL-2026-06-012/ })).toBeTruthy();

    await user.selectOptions(screen.getByLabelText("Project view"), "planning");

    expect(await screen.findByText("TMP-AABBCCDD")).toBeTruthy();
    expect(screen.queryByText("DL-2026-06-012")).toBeNull();
    expect(screen.getByText("Stopped")).toBeTruthy();
    expect(screen.getByText("Resume or administratively archive from Workbench")).toBeTruthy();
    expect(screen.getByRole("button", { name: /Open Workbench.*TMP-AABBCCDD/ })).toBeTruthy();
  });

  it("does not render lifecycle write actions from the registry", async () => {
    mockRows([
      registryRow({
        project_id: "P-STOP-DL",
        display_project_id: "DL-2026-06-013",
        status: "cancelled",
      }),
    ]);
    mockLifecycle({
      "P-STOP-DL": lifecycle({
        project_id: "P-STOP-DL",
        lifecycle_state: "stopped",
        status: "cancelled",
        readonly: true,
        allowed_actions: ["resume", "close"],
      }),
    });

    render(<ProjectListPage onOpenProject={vi.fn()} />);

    expect(await screen.findByRole("button", { name: /Open Workbench/ })).toBeTruthy();
    expect(screen.queryByRole("button", { name: /Stop|Resume|Close|Delete/i })).toBeNull();
  });

  it("exposes priority row markers for narrow-width status next step and action visibility", async () => {
    const onOpenProject = vi.fn();
    mockRows([
      registryRow({
        project_id: "P-NARROW",
        display_project_id: "DL-2026-06-020",
        status: "folder_created",
      }),
    ]);
    mockLifecycle({
      "P-NARROW": lifecycle({ project_id: "P-NARROW" }),
    });

    render(<ProjectListPage onOpenProject={onOpenProject} />);

    expect(await screen.findByText("DL-2026-06-020")).toBeTruthy();
    const actionButton = screen.getByRole("button", { name: /Open Workbench.*DL-2026-06-020/ });
    const row = actionButton.closest("tr");
    expect(row).not.toBeNull();
    expect(row?.classList.contains("project-registry-row")).toBe(true);

    const labels = Array.from(row?.querySelectorAll("td") ?? []).map((cell) =>
      cell.getAttribute("data-label")
    );
    expect(labels).toEqual([
      "Project ID",
      "Sample Description",
      "Test Item",
      "Status",
      "Next Step",
      "Action",
    ]);

    expect(row?.querySelector(".registry-project-id-cell")?.getAttribute("data-label")).toBe("Project ID");
    expect(row?.querySelector(".registry-status-cell")?.getAttribute("data-label")).toBe("Status");
    expect(row?.querySelector(".registry-next-step-cell")?.getAttribute("data-label")).toBe("Next Step");
    expect(row?.querySelector(".registry-action-cell")?.getAttribute("data-label")).toBe("Action");
    expect(row?.querySelector(".registry-action-cell .project-registry-action-buttons")).toBeTruthy();
    expect(row?.querySelector(".registry-action-cell .project-registry-icon-action")).toBe(actionButton);
    expect(screen.queryByRole("button", { name: "Manage project DL-2026-06-020" })).toBeNull();

    await userEvent.click(actionButton);
    expect(onOpenProject).toHaveBeenCalledWith("P-NARROW");
  });

  it("uses Workbench route copy for active planning and folder-created rows", async () => {
    const user = userEvent.setup();
    const onOpenProject = vi.fn();
    mockRows([
      registryRow({
        project_id: "P-FOLDER",
        display_project_id: "DL-2026-06-015",
        status: "folder_created",
      }),
      registryRow({
        project_id: "P-TMP",
        display_project_id: "TMP-ROUTE01",
        display_project_id_kind: "temporary",
        has_registered_ltr: false,
        ltr_number: null,
        registered_ltr_number: null,
      }),
    ]);
    mockLifecycle({
      "P-FOLDER": lifecycle({ project_id: "P-FOLDER" }),
      "P-TMP": lifecycle({ project_id: "P-TMP" }),
    });

    render(<ProjectListPage onOpenProject={onOpenProject} />);

    expect(await screen.findByText("DL-2026-06-015")).toBeTruthy();
    expect(screen.getByText("Folder Created")).toBeTruthy();
    expect(screen.getByText("Continue setup in Workbench")).toBeTruthy();
    await user.click(screen.getByRole("button", { name: /Open Workbench.*DL-2026-06-015/ }));
    expect(onOpenProject).toHaveBeenCalledWith("P-FOLDER");

    await user.selectOptions(screen.getByLabelText("Project view"), "planning");

    expect(await screen.findByText("TMP-ROUTE01")).toBeTruthy();
    expect(screen.getByText("Continue planning in Workbench")).toBeTruthy();
    await user.click(screen.getByRole("button", { name: /Open Workbench.*TMP-ROUTE01/ }));
    expect(onOpenProject).toHaveBeenCalledWith("P-TMP");
  });

  it("keeps rows visible with compatibility labels when lifecycle overlay loading fails", async () => {
    mockRows([
      registryRow({
        project_id: "P-FALLBACK",
        display_project_id: "DL-2026-06-014",
        status: "cancelled",
      }),
    ]);
    getProjectLifecycleMock.mockRejectedValue(new Error("Lifecycle service unavailable"));

    render(<ProjectListPage onOpenProject={vi.fn()} />);

    expect(await screen.findByText("DL-2026-06-014")).toBeTruthy();
    expect(screen.getByText("Stopped")).toBeTruthy();
    expect(screen.getByRole("button", { name: /Open Workbench.*DL-2026-06-014/ })).toBeTruthy();
    expect(screen.getByText(/Lifecycle status unavailable/)).toBeTruthy();
    expect(screen.queryByText(/cancelled|lifecycle_state|closure_type|closed_completed|closed_administrative/)).toBeNull();
  });
});

function mockRows(rows: ProjectRegistryRow[]): void {
  listProjectRegistryRowsMock.mockResolvedValue(rows);
}

async function projectIdsInTable(): Promise<string[]> {
  await screen.findByRole("button", { name: /Sort Project ID/ });
  return screen
    .getAllByRole("row")
    .slice(1)
    .map((row) => row.querySelector<HTMLElement>("[data-label='Project ID']")?.textContent ?? "");
}

function mockLifecycle(overlays: Record<string, ProjectLifecycleResponse>): void {
  getProjectLifecycleMock.mockImplementation((projectId: string) => {
    const overlay = overlays[projectId];
    if (!overlay) {
      return Promise.reject(new Error(`No lifecycle mock for ${projectId}`));
    }
    return Promise.resolve(overlay);
  });
}

function registryRow(overrides: Partial<ProjectRegistryRow> = {}): ProjectRegistryRow {
  return {
    project_id: "P1",
    ltr_number: "DL-2026-06-001",
    sample_description: "Connector sample",
    test_item: "Qualification",
    requestor: "Lab User",
    business_unit: null,
    status: "active",
    progress: 0,
    notes: null,
    display_project_id: "DL-2026-06-001",
    display_project_id_kind: "registered",
    has_registered_ltr: true,
    temporary_project_id: null,
    registered_ltr_number: "DL-2026-06-001",
    temporary_source_asset_ids: [],
    ...overrides,
  };
}

function lifecycle(
  overrides: Partial<ProjectLifecycleResponse> = {}
): ProjectLifecycleResponse {
  return {
    project_id: "P1",
    lifecycle_state: "active",
    closure_type: null,
    status_label: "Active",
    readonly: false,
    allowed_actions: ["stop", "close"],
    status: "active",
    stopped_at: null,
    stopped_reason: null,
    closed_at: null,
    closed_reason: null,
    completion_summary: null,
    warnings: [],
    ...overrides,
  };
}
