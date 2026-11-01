import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import type { PortableRestorePlan } from "../../api/projectLibrary";
import { ProjectImportSnapshotDetails } from "./ProjectImportSnapshots";

const project: PortableRestorePlan = {
  plan_id: "review", fingerprint: "verified", project_id: "P1", title: "Connector test", ltr_number: "DL-2026-07-006",
  source_path: "D:/source", target_path: "D:/Projects/Test", status: "ready", created_at: "2026-10-29T10:00:00Z",
  resolution_options: [], resolution: null, source_signature: "source", target_revision: null, backup_path: null,
  record_counts: { confirmed_matrix_versions: 2, result_dataset_revisions: 6 }, file_count: 7,
  warnings: ["Original source is missing."], blockers: [],
};

it("shows data gaps and only backend-offered conflict choices, without enabling an unresolved copy", async () => {
  const user = userEvent.setup(), resolve = vi.fn();
  render(<ProjectImportSnapshotDetails plan={{ ...project, status: "conflict", resolution_options: ["keep_as_history"] }} disabled={false} onResolve={resolve} />);
  expect(screen.getByText("This project has different data. View the differences, then choose which copy to keep.")).toBeTruthy();
  await user.click(screen.getByText("View Differences"));
  expect(screen.getByText("Original source is missing.").closest("details")).toHaveProperty("open", true);
  expect(screen.queryByRole("button", { name: "Use Imported Version" })).toBeNull();
  await user.click(screen.getByRole("button", { name: "Keep Another Copy" }));
  expect(resolve).toHaveBeenCalledWith("D:/source", "keep_as_history");
});

it("makes replacement and recovery-point consequences explicit in the final review", () => {
  render(<ProjectImportSnapshotDetails plan={{ ...project, resolution: "replace_working_copy", backup_path: "D:/Recovery/Before import" }} disabled onResolve={vi.fn()} />);
  expect(screen.getByRole("alert").textContent).toContain("current working copy will be replaced");
  expect(screen.getByRole("alert").textContent).toContain("D:/Recovery/Before import");
  expect(screen.queryByRole("checkbox")).toBeNull();
});

it("offers no conflict choices when the saved project has blockers", () => {
  render(<ProjectImportSnapshotDetails plan={{ ...project, blockers: ["Saved data is unavailable."], resolution_options: ["replace_working_copy"] }} disabled={false} onResolve={vi.fn()} />);
  expect(screen.getByRole("alert").textContent).toContain("Export this project again from the original computer.");
  expect(screen.queryByRole("button", { name: "Use Imported Version" })).toBeNull();
});
