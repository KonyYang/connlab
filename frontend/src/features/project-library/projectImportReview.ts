import {
  inspectPortableProject, planLibraryIntake, restorePortableProject,
  type LibraryBatch, type LibraryCandidate, type LibraryFileAssignment, type LibraryIntakePlan,
  type PortableRestorePlan, type PortableRestoreResult,
} from "../../api/projectLibrary";

export async function reviewImportCandidates(candidates: LibraryCandidate[], signal: AbortSignal, assignments?: LibraryFileAssignment[]) {
  const ordinary = candidates.filter(row => !row.has_portable);
  const snapshots: PortableRestorePlan[] = [];
  const plan: LibraryIntakePlan | null = ordinary.length
    ? await (assignments ? planLibraryIntake(ordinary.map(row => row.source_path), signal, assignments) : planLibraryIntake(ordinary.map(row => row.source_path), signal))
    : null;
  for (const row of candidates.filter(row => row.has_portable)) {
    if (signal.aborted) return { plan: null, snapshots: [], projectsRoot: undefined };
    snapshots.push(await inspectPortableProject(row.source_path, signal));
  }
  const roots = [...new Set([plan?.projects_root, ...snapshots.map(row => row.projects_root)].filter((value): value is string => typeof value === "string" && Boolean(value)))];
  if (roots.length > 1) throw new Error("The save location changed during checking. Check the selected folders again before importing.");
  return { plan, snapshots, projectsRoot: roots[0] };
}

export function readyImportPaths(plan: LibraryIntakePlan | null, snapshots: PortableRestorePlan[]) {
  return [...(plan?.items ?? []), ...snapshots]
    .filter(row => row.status === "ready" && !("blockers" in row && row.blockers.length))
    .map(row => row.source_path);
}

export type SnapshotImportOutcome = {
  source_path: string; title: string; status: "added" | "already_added" | "failed";
  member_id: string | null; message: string; result?: PortableRestoreResult;
};

export async function receiveSavedProjects(plans: PortableRestorePlan[], isCurrent: () => boolean) {
  const outcomes: SnapshotImportOutcome[] = [];
  for (const plan of plans) {
    if (!isCurrent()) break;
    try {
      const result = await restorePortableProject({ plan_id: plan.plan_id, fingerprint: plan.fingerprint, ...(plan.resolution ? { resolution: plan.resolution } : {}) });
      outcomes.push({ source_path: plan.source_path, title: plan.title, status: result.status === "already_added" ? "already_added" : "added", member_id: result.member.member_id,
        message: result.status === "history_kept" ? "Historical copy kept. The current working project is unchanged." : "Project and saved test data imported.", result });
    } catch (cause) {
      outcomes.push({ source_path: plan.source_path, title: plan.title, status: "failed", member_id: null, message: (cause as Error).message });
    }
  }
  return outcomes;
}

/** A UI summary only: backend batch identities remain unchanged for recovery. */
export function combinedImportResults(batch: LibraryBatch | null, snapshots: SnapshotImportOutcome[]): LibraryBatch | null {
  if (!snapshots.length) return batch;
  const items = [...(batch?.items ?? []), ...snapshots];
  return {
    batch_id: batch?.batch_id ?? snapshots.find(row => row.result)?.result?.member.batch_id ?? "saved-project-results",
    status: batch?.status ?? "completed", items,
    counts: {
      added: items.filter(row => row.status === "added").length,
      already_added: items.filter(row => row.status === "already_added").length,
      review: items.filter(row => row.status === "review").length,
      failed: items.filter(row => row.status === "failed").length,
    },
  };
}

export function selectedImportProblem(plan: LibraryIntakePlan | null, snapshots: PortableRestorePlan[], selected: string[]) {
  const chosen = [...(plan?.items ?? []), ...snapshots].filter(row => selected.includes(row.source_path));
  const key = (path: string) => path.replace(/\\/g, "/").replace(/\/+$/, "").toLowerCase();
  const paths = chosen.map(row => key(row.source_path) + "/").sort();
  for (let index = 1; index < paths.length; index++) {
    if (paths[index].startsWith(paths[index - 1])) {
      return "Some selected folders contain one another. Select one complete project folder before importing.";
    }
  }
  const saved = new Set(snapshots.map(row => row.source_path)), numbers = new Map<string, boolean>();
  for (const row of chosen) {
    if (!row.ltr_number) continue;
    const number = row.ltr_number.toLowerCase(), snapshot = saved.has(row.source_path);
    if (numbers.has(number) && (numbers.get(number) || snapshot)) {
      return "These selected copies use the same LTR. Import one copy first, then check the other and choose how to retain it.";
    }
    numbers.set(number, snapshot);
  }
  return "";
}
