import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import type { PortableRestorePlan } from "../../api/projectLibrary";
import { ProjectImportSnapshots } from "./ProjectImportSnapshots";

const project: PortableRestorePlan = {
  plan_id: "review", fingerprint: "verified", project_id: "P1", title: "Connector test", ltr_number: "DL-2026-07-006",
  source_path: "D:/source", target_path: "D:/Projects/Test", status: "ready", created_at: "2026-10-29T10:00:00Z",
  resolution_options: [], resolution: null, source_signature: "source", target_revision: null, backup_path: null,
  record_counts: { confirmed_matrix_versions: 2, result_dataset_revisions: 6 }, file_count: 7,
  warnings: ["Original source is missing."], blockers: [],
};

it("shows data gaps and only backend-offered conflict choices, without enabling an unresolved copy", async () => {
  const user = userEvent.setup(), resolve = vi.fn();
  render(<ProjectImportSnapshots plans={[{ ...project, status: "conflict", resolution_options: ["keep_as_history"] }]} selected={[]} disabled={false} onResolve={resolve} />);
  expect(screen.getByRole("status").textContent).toContain("does not fill missing source files");
  await user.click(screen.getByText("Review 1 warning"));
  expect(screen.getByText("Original source is missing.").closest("details")).toHaveProperty("open", true);
  expect(screen.getByRole("checkbox", { name: "Select Connector test" })).toHaveProperty("disabled", true);
  expect(screen.queryByRole("radio", { name: "Replace Working Copy" })).toBeNull();
  await user.click(screen.getByRole("radio", { name: "Keep as History" }));
  expect(resolve).toHaveBeenCalledWith("D:/source", "keep_as_history");
});

it("makes replacement and recovery-point consequences explicit in the final review", () => {
  render(<ProjectImportSnapshots plans={[{ ...project, resolution: "replace_working_copy", backup_path: "D:/Recovery/Before import" }]} selected={[project.source_path]} disabled confirmation />);
  expect(screen.getByRole("alert").textContent).toContain("current working copy will be replaced");
  expect(screen.getByRole("alert").textContent).toContain("D:/Recovery/Before import");
  expect(screen.queryByRole("checkbox")).toBeNull();
});

it("keeps large snapshot selections browsable without losing off-page selections", async () => {
  const user = userEvent.setup(), toggle = vi.fn();
  const projects = Array.from({ length: 25 }, (_, index) => ({ ...project, source_path: `D:/Source/${index}`, title: `Project ${index + 1}` }));
  render(<ProjectImportSnapshots plans={projects} selected={projects.map(row => row.source_path)} disabled={false} onToggle={toggle} />);
  expect(screen.getAllByRole("checkbox")).toHaveLength(20);
  expect(screen.queryByRole("checkbox", { name: "Select Project 25" })).toBeNull();
  await user.click(screen.getByRole("button", { name: "Next projects with saved data" }));
  expect(screen.getByRole("checkbox", { name: "Select Project 25" })).toHaveProperty("checked", true);
  await user.click(screen.getByRole("checkbox", { name: "Select Project 25" }));
  expect(toggle).toHaveBeenCalledWith("D:/Source/24", false);
});
