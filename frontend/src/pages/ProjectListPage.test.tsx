import { render, screen, waitFor } from "@testing-library/react";
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
    expect(row?.querySelector(".registry-action-cell .row-action")).toBe(actionButton);
    expect(screen.queryByRole("button", { name: /Stop|Resume|Close|Delete/i })).toBeNull();

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
