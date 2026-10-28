import type { LibraryMember } from "../../api/projectLibrary";
import type { LegacyProjectRecord } from "../../api/legacyProjects";
import { registryStatusLabel, registryNextStepLabel, registryViewForRow, type ProjectRegistryLifecycleRow, type ProjectRegistryView } from "./projectRegistryLifecycleViews";

export type CatalogView = ProjectRegistryView | "files";
export type ProjectCatalogRow =
  | { kind: "registered"; key: string; entry: ProjectRegistryLifecycleRow; members: LibraryMember[] }
  | { kind: "managed"; key: string; member: LibraryMember }
  | { kind: "linked"; key: string; record: LegacyProjectRecord };

export function buildProjectCatalog(registry: ProjectRegistryLifecycleRow[], members: LibraryMember[], linked: LegacyProjectRecord[], { batchId = "", retainedProjectIds = [], registryComplete = true }: { batchId?: string; retainedProjectIds?: string[]; registryComplete?: boolean } = {}): ProjectCatalogRow[] {
  const knownProjects = new Set(registry.map(entry => entry.row.project_id));
  const retained = new Set([...retainedProjectIds, ...registry.filter(entry => entry.row.registry_state && entry.row.registry_state !== "active").map(entry => entry.row.project_id)]);
  const byProject = new Map<string, LibraryMember[]>();
  for (const member of members) {
    if (member.project_id && !member.is_history) byProject.set(member.project_id, [...(byProject.get(member.project_id) ?? []), member]);
  }
  const rows: ProjectCatalogRow[] = registry
    .filter(entry => !entry.row.registry_state || entry.row.registry_state === "active")
    .map(entry => ({ kind: "registered", key: `project:${entry.row.project_id}`, entry, members: byProject.get(entry.row.project_id) ?? [] }));
  for (const member of members) {
    // Only verified identities combine rows. Retained workspaces must not reappear through their folder entry.
    if (member.project_id && (retained.has(member.project_id) || !registryComplete && !knownProjects.has(member.project_id) || !member.is_history && knownProjects.has(member.project_id))) continue;
    rows.push({ kind: "managed", key: `member:${member.member_id}`, member });
  }
  if (batchId) return rows.filter(row => row.kind === "registered" ? row.members.some(member => member.batch_id === batchId) : row.kind === "managed" && row.member.batch_id === batchId);
  rows.push(...linked.map(record => ({ kind: "linked" as const, key: `linked:${record.record_id}`, record })));
  return rows;
}

export function catalogIdentifier(row: ProjectCatalogRow): string {
  return row.kind === "registered" ? row.entry.row.display_project_id : (row.kind === "managed" ? row.member.ltr_number : row.record.number) || "No LTR yet";
}

export function catalogTitle(row: ProjectCatalogRow): string {
  return row.kind === "registered" ? row.entry.row.sample_description || "Not recorded" : row.kind === "managed" ? row.member.title : row.record.name;
}

export function selectProjectCatalog(rows: ProjectCatalogRow[], view: CatalogView, search: string): ProjectCatalogRow[] {
  const query = search.trim().toLocaleLowerCase();
  return rows.filter(row => {
    const rowView = row.kind === "registered" ? registryViewForRow(row.entry.row, row.entry.lifecycle) : row.kind === "managed" && row.member.is_history ? "closed" : "files";
    if (view !== "all" && view !== rowView) return false;
    const fields = row.kind === "registered"
      ? [row.entry.row.test_item, row.entry.row.requestor, row.entry.row.notes, registryStatusLabel(row.entry.row, row.entry.lifecycle), registryNextStepLabel(row.entry.row, row.entry.lifecycle), ...row.members.flatMap(member => [member.title, member.folder_path])]
      : row.kind === "managed" ? [row.member.folder_path, row.member.is_history ? "Historical Copy" : "Files Only", ...row.member.warnings]
      : [row.record.folder_path, "Files Only", ...row.record.notes];
    return [catalogIdentifier(row), catalogTitle(row), ...fields].join(" ").toLocaleLowerCase().includes(query);
  });
}
