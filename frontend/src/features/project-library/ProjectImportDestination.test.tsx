import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { ProjectImportDestination } from "./ProjectImportDestination";
import * as api from "../../api/projectLibrary";

vi.mock("../../api/projectLibrary", () => ({
  saveLibraryDestination: vi.fn(), openLibraryDestination: vi.fn(), pickLibraryDestination: vi.fn(),
}));
const runtime: api.LibraryRuntime = { library_root: "D:/app", data_root: "D:/app/Data", database_path: "D:/app/Data/connlab.sqlite3", projects_root: "D:/unused-default", configured: false, format_version: 1 };
beforeEach(() => vi.resetAllMocks());

it("guides first-use setup without presenting the unused fallback as an import destination", async () => {
  const onChanged = vi.fn();
  vi.mocked(api.pickLibraryDestination).mockResolvedValue("D:/Projects Dev");
  vi.mocked(api.saveLibraryDestination).mockResolvedValue({ ...runtime, configured: true, projects_root: "D:/Projects Dev" });
  const user = userEvent.setup();
  render(<ProjectImportDestination runtime={runtime} disabled={false} onChanged={onChanged} />);
  expect(screen.queryByText("D:/unused-default")).toBeNull();
  await user.click(screen.getByRole("button", { name: "Choose Save Location" }));
  expect(screen.getByLabelText("Save imported projects to")).toHaveProperty("value", "D:/Projects Dev");
  expect(api.saveLibraryDestination).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "Use This Location" }));
  expect(api.saveLibraryDestination).toHaveBeenCalledWith("D:/Projects Dev");
  expect(onChanged).toHaveBeenCalledWith(expect.objectContaining({ configured: true, projects_root: "D:/Projects Dev", database_path: runtime.database_path }));
});

it("keeps a failed save editable and never reports the rejected location as configured", async () => {
  const user = userEvent.setup(), onChanged = vi.fn();
  vi.mocked(api.saveLibraryDestination).mockRejectedValue(new Error("The selected location is unavailable."));
  render(<ProjectImportDestination runtime={runtime} disabled={false} onChanged={onChanged} />);
  await user.type(screen.getByLabelText("Save imported projects to"), "D:/offline");
  await user.click(screen.getByRole("button", { name: "Use This Location" }));
  expect((await screen.findByRole("alert")).textContent).toContain("unavailable");
  expect(onChanged).not.toHaveBeenCalled();
  expect(screen.getByRole("button", { name: "Use This Location" })).toHaveProperty("disabled", false);
});

it("opens the server-validated location and preserves an explicit managed-library binding", async () => {
  const user = userEvent.setup();
  vi.mocked(api.openLibraryDestination).mockResolvedValue({ status: "opened", message: "Opened." });
  render(<ProjectImportDestination runtime={{ ...runtime, configured: true, projects_root: "D:/Library/Projects", destination_editable: false }} disabled={false} onChanged={vi.fn()} />);
  expect(screen.getByText("D:/Library/Projects")).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Change" })).toBeNull();
  await user.click(screen.getByRole("button", { name: "Open Folder" }));
  expect(api.openLibraryDestination).toHaveBeenCalledWith();
});

it("explains a failed folder open without changing the save location", async () => {
  const user = userEvent.setup(), changed = vi.fn();
  vi.mocked(api.openLibraryDestination).mockResolvedValue({ status: "blocked", message: "Access was denied." });
  render(<ProjectImportDestination runtime={{ ...runtime, configured: true }} disabled={false} onChanged={changed} />);
  await user.click(screen.getByRole("button", { name: "Open Folder" }));
  expect((await screen.findByRole("alert")).textContent).toContain("Access was denied.");
  expect(changed).not.toHaveBeenCalled();
});
