import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { ProjectWorkbenchPage } from "./ProjectWorkbenchPage";
import { useProjectWorkbenchModel, type ProjectWorkbenchModel } from "../features/project-workbench/useProjectWorkbenchModel";

vi.mock("../features/project-workbench/useProjectWorkbenchModel", () => ({ useProjectWorkbenchModel: vi.fn() }));
vi.mock("../features/project-workbench/useProjectRuntimeConsoleModel", () => ({ selectProjectRuntimeConsoleModel: (value: unknown) => value }));
vi.mock("../features/project-workbench/ProjectWorkbenchLayout", () => ({ ProjectWorkbenchLayout: () => <section aria-label="Standard workbench" /> }));

const model = {
  project: { project_id: "imported-project", project_no: null, library_member_id: "imported-member", product_name: "Unnumbered archive", requestor: "Imported project", status: "draft" },
  error: null, basicInformation: null, basicInformationLoading: false,
  activeConfirmedMatrixSnapshot: null, activeConfirmedMatrixLoading: false,
};
const props = () => ({ projectId: "imported-project", onBack: vi.fn(), onOpenMatrixEditor: vi.fn(), onOpenFeeEvaluation: vi.fn(),
  onOpenBasicInformation: vi.fn(), onOpenReportWorkspace: vi.fn(), onOpenSettings: vi.fn(), onBrowseProjectFiles: vi.fn() });

beforeEach(() => { vi.mocked(useProjectWorkbenchModel).mockReturnValue(model as unknown as ProjectWorkbenchModel); });

it("keeps unnumbered imported files available in the common workbench while explaining missing setup", async () => {
  const callbacks = props();
  render(<ProjectWorkbenchPage {...callbacks} />);
  expect(screen.getByRole("region", { name: "Standard workbench" })).toBeTruthy();
  expect(screen.getByText(/Review Basic Information/)).toBeTruthy();
  expect(screen.getByText(/No confirmed Matrix/)).toBeTruthy();
  await userEvent.setup().click(screen.getByRole("button", { name: "Browse Files" }));
  expect(callbacks.onBrowseProjectFiles).toHaveBeenCalledWith("imported-member");
});

it("does not show missing-setup warnings for confirmed restored data", () => {
  vi.mocked(useProjectWorkbenchModel).mockReturnValue({ ...model, basicInformation: { status: "confirmed" }, activeConfirmedMatrixSnapshot: { confirmed_matrix_id: "matrix-1" } } as unknown as ProjectWorkbenchModel);
  render(<ProjectWorkbenchPage {...props()} />);
  expect(screen.getByRole("button", { name: "Browse Files" })).toBeTruthy();
  expect(screen.queryByText(/Review Basic Information/)).toBeNull();
  expect(screen.queryByText(/No confirmed Matrix/)).toBeNull();
});

it("keeps the existing workbench unchanged for projects without an imported file binding", () => {
  vi.mocked(useProjectWorkbenchModel).mockReturnValue({ ...model, project: { ...model.project, library_member_id: null } } as unknown as ProjectWorkbenchModel);
  render(<ProjectWorkbenchPage {...props()} />);
  expect(screen.queryByRole("button", { name: "Browse Files" })).toBeNull();
  expect(screen.getByRole("region", { name: "Standard workbench" })).toBeTruthy();
});
