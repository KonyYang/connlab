import { render, screen } from "@testing-library/react";
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

it("shows an imported project in the standard workbench without a special file setup card", () => {
  render(<ProjectWorkbenchPage {...props()} />);
  expect(screen.getByRole("region", { name: "Standard workbench" })).toBeTruthy();
  expect(screen.queryByRole("complementary", { name: "Project files and setup" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Browse Files" })).toBeNull();
});

it("also keeps restored imported data free of the special file setup card", () => {
  vi.mocked(useProjectWorkbenchModel).mockReturnValue({ ...model, basicInformation: { status: "confirmed" }, activeConfirmedMatrixSnapshot: { confirmed_matrix_id: "matrix-1" } } as unknown as ProjectWorkbenchModel);
  render(<ProjectWorkbenchPage {...props()} />);
  expect(screen.queryByRole("complementary", { name: "Project files and setup" })).toBeNull();
  expect(screen.queryByRole("button", { name: "Browse Files" })).toBeNull();
});

it("keeps the existing workbench unchanged for projects without an imported file binding", () => {
  vi.mocked(useProjectWorkbenchModel).mockReturnValue({ ...model, project: { ...model.project, library_member_id: null } } as unknown as ProjectWorkbenchModel);
  render(<ProjectWorkbenchPage {...props()} />);
  expect(screen.queryByRole("button", { name: "Browse Files" })).toBeNull();
  expect(screen.getByRole("region", { name: "Standard workbench" })).toBeTruthy();
});
