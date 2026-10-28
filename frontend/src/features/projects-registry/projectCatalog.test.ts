import { describe, expect, it } from "vitest";
import type { ProjectRegistryRow } from "../../api/client";
import type { LibraryMember } from "../../api/projectLibrary";
import type { LegacyProjectRecord } from "../../api/legacyProjects";
import { buildProjectCatalog, selectProjectCatalog } from "./projectCatalog";

const row: ProjectRegistryRow = { project_id: "project-1", display_project_id: "DL-2026-01-001", display_project_id_kind: "registered", has_registered_ltr: true, requestor: "Lab User", status: "active", progress: 0, sample_description: "Original sample" };
const member: LibraryMember = { member_id: "same-id", project_id: "project-1", ltr_number: "DL-2026-01-001", title: "Renamed project", folder_path: "D:/projects/renamed", revision: 1, batch_id: "batch-one", snapshot_status: "missing", snapshot_created_at: null, warnings: [], can_continue: true };
const linked: LegacyProjectRecord = { record_id: "same-id", name: "Renamed project", number: "DL-2026-01-001", number_evidence: [], folder_path: "D:/projects/linked", notes: [], revision: 1, imported_at: "", updated_at: "" };

describe("project catalog identity and filtering", () => {
  it("combines only a known workspace identity, retaining title/path search and same-LTR independent records", () => {
    const catalog = buildProjectCatalog([{ row, lifecycle: null }], [member, { ...member, member_id: "unclaimed", project_id: null }], [linked]);
    expect(catalog.map(item => item.key)).toEqual(["project:project-1", "member:unclaimed", "linked:same-id"]);
    expect(selectProjectCatalog(catalog, "all", "D:/projects/renamed")).toHaveLength(2);
    expect(selectProjectCatalog(catalog, "all", "Original sample")).toHaveLength(1);
    expect(selectProjectCatalog(catalog, "files", "Renamed project")).toHaveLength(2);
    expect(selectProjectCatalog(catalog, "ongoing", "Renamed project")).toHaveLength(1);
  });

  it("never resurfaces a retained workspace and keeps unchecked identities out of incomplete results", () => {
    expect(buildProjectCatalog([], [member], [], { registryComplete: false })).toEqual([]);
    for (const registry_state of ["trash", "history"] as const) {
      expect(buildProjectCatalog([{ row: { ...row, registry_state }, lifecycle: null }], [member], [])).toEqual([]);
    }
    expect(buildProjectCatalog([], [member], [], { retainedProjectIds: ["project-1"] })).toEqual([]);
    expect(buildProjectCatalog([], [{ ...member, is_history: true }], [], { retainedProjectIds: ["project-1"] })).toEqual([]);
    expect(buildProjectCatalog([], [{ ...member, is_history: true }], [], { registryComplete: false })).toEqual([]);
    expect(buildProjectCatalog([], [member], [])).toHaveLength(1);
    expect(buildProjectCatalog([], [{ ...member, is_history: true }], [])).toHaveLength(1);
  });

  it("shows only members of an import batch while keeping historical copies distinct", () => {
    const snapshot = { ...member, member_id: "historical", is_history: true, batch_id: "batch-two" };
    const registry = [{ row, lifecycle: null }];
    expect(buildProjectCatalog(registry, [member, snapshot], [linked], {batchId: "batch-one"}).map(item => item.key)).toEqual(["project:project-1"]);
    const historical = buildProjectCatalog(registry, [member, snapshot], [linked], {batchId: "batch-two"});
    expect(historical.map(item => item.key)).toEqual(["member:historical"]);
    expect(selectProjectCatalog(historical, "closed", "")).toHaveLength(1);
    expect(selectProjectCatalog(historical, "files", "")).toHaveLength(0);
    expect(registry[0].row).toBe(row);
    expect(member.title).toBe("Renamed project");
  });
});
