import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { ApiRequestError, pickExternalResourcePath } from "../../api/client";
import { abandonFolderResolution, applyFolderResolution, previewFolderResolution, resumeFolderResolution } from "../../api/projectFolderResolution";
import { ProjectFolderResolutionDialog } from "./ProjectFolderResolutionDialog";

vi.mock("../../api/projectFolderResolution", () => ({
  previewFolderResolution: vi.fn(), applyFolderResolution: vi.fn(), resumeFolderResolution: vi.fn(), abandonFolderResolution: vi.fn(),
}));
vi.mock("../../api/client", async (original) => ({
  ...(await original<typeof import("../../api/client")>()), pickExternalResourcePath: vi.fn(),
}));

const oldPath = "D:/Former/Project";
function open(pendingOperation: string | null = null) {
  const onResolved = vi.fn();
  const onRecheck = vi.fn().mockResolvedValue(undefined);
  render(<ProjectFolderResolutionDialog projectId="P1" registeredPath={oldPath} pendingOperation={pendingOperation}
    onResolved={onResolved} onRecheck={onRecheck} onCancel={vi.fn()} />);
  return {user: userEvent.setup(), onResolved, onRecheck};
}
const completed = {operation_id: "saved", status: "completed", directory_available: true,
  official_project_folder_path: "D:/New/Project", issues: [], message: null};

beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(previewFolderResolution).mockImplementation(async (project_id, choice) => ({
    project_id, strategy: choice.strategy, old_path: oldPath, target_path: (choice.path ?? "D:/Default") + "/Project",
    expected_context: "checked",
  }));
  vi.mocked(applyFolderResolution).mockResolvedValue(completed);
  vi.mocked(resumeFolderResolution).mockResolvedValue(completed);
});

it("checks the chosen folder and reuses the same confirmation after a lost response", async () => {
  vi.mocked(pickExternalResourcePath).mockResolvedValueOnce({path: null}).mockResolvedValueOnce({path: "E:/Moved"});
  vi.mocked(applyFolderResolution).mockRejectedValueOnce(new TypeError("Connection lost"));
  const {user, onRecheck, onResolved} = open();
  await user.click(screen.getByRole("button", {name: /Choose project folder/}));
  expect(previewFolderResolution).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", {name: /Choose project folder/}));
  expect(await screen.findByText("E:/Moved/Project")).toBeTruthy();
  expect(screen.getByText(oldPath)).toBeTruthy();
  expect(applyFolderResolution).not.toHaveBeenCalled();
  const confirm = screen.getByRole("button", {name: "Link folder"});
  await user.click(confirm);
  expect((await screen.findByRole("alert")).textContent).toContain("Connection lost");
  expect(onRecheck).toHaveBeenCalledOnce();
  await user.click(confirm);
  expect(applyFolderResolution).toHaveBeenCalledTimes(2);
  const [first, retry] = vi.mocked(applyFolderResolution).mock.calls;
  expect(first).toEqual(["P1", {strategy: "relink", path: "E:/Moved"}, "checked", expect.any(String)]);
  expect(retry).toEqual(first);
  expect(onResolved).toHaveBeenCalledOnce();
});

it("previews the default and another parent, and requires a new preview after a stale confirmation", async () => {
  vi.mocked(pickExternalResourcePath).mockResolvedValue({path: "D:/Other"});
  vi.mocked(applyFolderResolution).mockRejectedValueOnce(new ApiRequestError("Destination changed", 409, null));
  const {user, onResolved} = open();
  await user.click(screen.getByRole("radio", {name: "Create a new working folder"}));
  expect(await screen.findByText("D:/Default/Project")).toBeTruthy();
  await user.click(screen.getByRole("button", {name: /Choose another parent/}));
  expect(await screen.findByText("D:/Other/Project")).toBeTruthy();
  expect(applyFolderResolution).not.toHaveBeenCalled();
  const confirm = screen.getByRole("button", {name: "Create working folder"});
  await user.click(confirm);
  expect((await screen.findByRole("alert")).textContent).toContain("Destination changed");
  expect(confirm).toHaveProperty("disabled", true);
  await user.click(screen.getByRole("button", {name: "Refresh preview"}));
  await waitFor(() => expect(confirm).toHaveProperty("disabled", false));
  await user.click(confirm);
  expect(onResolved).toHaveBeenCalledOnce();
});

it("resumes the stored operation without sending another create or link request", async () => {
  const {user, onResolved} = open("original-operation");
  expect(screen.queryByRole("radio")).toBeNull();
  await user.click(screen.getByRole("button", {name: "Resume folder change"}));
  expect(resumeFolderResolution).toHaveBeenCalledOnce();
  expect(resumeFolderResolution).toHaveBeenCalledWith("P1", "original-operation");
  expect(previewFolderResolution).not.toHaveBeenCalled();
  expect(applyFolderResolution).not.toHaveBeenCalled();
  expect(onResolved).toHaveBeenCalledOnce();
});

it("can keep the old registration and leave files from an interrupted change in place", async () => {
  vi.mocked(abandonFolderResolution).mockResolvedValue({status: "abandoned", directory_available: false});
  const {user, onResolved} = open("unfinished");
  expect(screen.getByText(/files already created/i)).toBeTruthy();
  await user.click(screen.getByRole("button", {name: "Keep previous location"}));
  expect(abandonFolderResolution).toHaveBeenCalledWith("P1", "unfinished");
  expect(resumeFolderResolution).not.toHaveBeenCalled();
  expect(onResolved).toHaveBeenCalledOnce();
});

it("offers resume when the new location is already registered", async () => {
  const message = "The new location is already registered. Resume the folder change.";
  vi.mocked(abandonFolderResolution).mockRejectedValue(new ApiRequestError(message, 409, null));
  const {user, onResolved} = open("unfinished");
  await user.click(screen.getByRole("button", {name: "Keep previous location"}));
  expect((await screen.findByRole("alert")).textContent).toBe(message);
  expect(onResolved).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", {name: "Resume folder change"}));
  expect(resumeFolderResolution).toHaveBeenCalledWith("P1", "unfinished");
});
