import { describe, expect, it } from "vitest";
import type {
  ProjectLifecycleResponse,
  ProjectRegistryRow,
} from "../../api/client";
import {
  filterRegistryRowsForView,
  registryLifecycleLabel,
  registryNextStepLabel,
  registryStatusLabel,
  registryViewForRow,
} from "./projectRegistryLifecycleViews";

describe("project registry lifecycle views", () => {
  it("keeps stopped temporary projects in Planning", () => {
    const row = registryRow({
      display_project_id: "TMP-AABBCCDD",
      display_project_id_kind: "temporary",
      has_registered_ltr: false,
      ltr_number: null,
      registered_ltr_number: null,
      status: "cancelled",
    });
    const lifecycle = projectLifecycle({ lifecycle_state: "stopped" });

    expect(registryViewForRow(row, lifecycle)).toBe("planning");
    expect(registryLifecycleLabel(row, lifecycle)).toBe("Stopped");
    expect(registryNextStepLabel(row, lifecycle)).toBe("Review or resume in Workbench");
  });

  it("keeps stopped registered projects in On-going", () => {
    const row = registryRow({
      display_project_id: "DL-2026-06-001",
      display_project_id_kind: "registered",
      has_registered_ltr: true,
      status: "cancelled",
    });
    const lifecycle = projectLifecycle({ lifecycle_state: "stopped" });

    expect(registryViewForRow(row, lifecycle)).toBe("ongoing");
    expect(registryStatusLabel(row, lifecycle)).toBe("Stopped");
  });

  it("classifies closed completed and administrative projects as Closed", () => {
    const completed = registryRow({
      project_id: "P-CLOSED-C",
      display_project_id: "DL-2026-06-002",
      status: "closed",
    });
    const administrative = registryRow({
      project_id: "P-CLOSED-A",
      display_project_id: "DL-2026-06-003",
      status: "closed",
    });

    expect(
      registryLifecycleLabel(
        completed,
        projectLifecycle({ lifecycle_state: "closed", closure_type: "completed" })
      )
    ).toBe("Closed: Completed");
    expect(
      registryLifecycleLabel(
        administrative,
        projectLifecycle({ lifecycle_state: "closed", closure_type: "administrative" })
      )
    ).toBe("Closed: Administrative");
    expect(
      filterRegistryRowsForView(
        [
          { row: completed, lifecycle: projectLifecycle({ lifecycle_state: "closed", closure_type: "completed" }) },
          { row: administrative, lifecycle: projectLifecycle({ lifecycle_state: "closed", closure_type: "administrative" }) },
        ],
        "closed"
      ).map(({ row }) => row.project_id)
    ).toEqual(["P-CLOSED-C", "P-CLOSED-A"]);
  });

  it("uses cancelled only as a stopped compatibility fallback, not a Closed view", () => {
    const row = registryRow({
      display_project_id: "DL-2026-06-004",
      status: "cancelled",
      has_registered_ltr: true,
    });

    expect(registryLifecycleLabel(row, null)).toBe("Stopped");
    expect(registryViewForRow(row, null)).toBe("ongoing");
    expect(filterRegistryRowsForView([{ row, lifecycle: null }], "closed")).toEqual([]);
  });

  it("does not expose backend enum tokens in labels or next-step copy", () => {
    const row = registryRow({ status: "cancelled" });
    const completed = projectLifecycle({
      lifecycle_state: "closed",
      closure_type: "completed",
    });

    const copy = [
      registryLifecycleLabel(row, completed),
      registryStatusLabel(row, completed),
      registryNextStepLabel(row, completed),
    ].join(" ");

    expect(copy).not.toMatch(/closed_completed|closed_administrative|cancelled|lifecycle_state|closure_type/);
  });
});

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

function projectLifecycle(
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
