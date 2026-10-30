import { act, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { encryptStandaloneCopy, encryptStandaloneFolder } from "../../api/client";
import { EncryptionTool } from "./EncryptionTool";

vi.mock("../../api/client", () => ({ encryptStandaloneCopy: vi.fn(), encryptStandaloneFolder: vi.fn() }));

function file(path: string) {
  const value = new File(["original"], path.split("/").at(-1)!);
  Object.defineProperty(value, "webkitRelativePath", { value: path });
  return value;
}

beforeEach(() => {
  vi.resetAllMocks();
  vi.stubGlobal("URL", { createObjectURL: vi.fn(() => "blob:encrypted"), revokeObjectURL: vi.fn() });
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
  vi.mocked(encryptStandaloneFolder).mockResolvedValue({ blob: new Blob(["zip"]), fileName: "Encrypted_Folder.zip",
    summary: { succeeded: 1, failed: 1, skipped: 0 } });
});

it("previews recursive Office files and starts one ZIP download only after confirmation", async () => {
  const user = userEvent.setup();
  render(<EncryptionTool />);
  const word = file("项目/report.docx");
  const excel = file("项目/子目录/DL-2026-10-001.xlsx");
  fireEvent.change(screen.getByLabelText("Select Office Folder"), { target: { files: [word, excel, file("项目/photo.png")] } });
  expect(encryptStandaloneFolder).not.toHaveBeenCalled();
  expect(screen.getByText(/2 Word\/Excel files/)).toBeTruthy();
  expect(screen.getByText(/1 other files ignored/)).toBeTruthy();
  await user.click(screen.getByRole("button", { name: "Encrypt Selected Folder" }));
  expect(encryptStandaloneFolder).toHaveBeenCalledWith([word, excel]);
  expect((await screen.findByRole("status", { name: "Downloaded File" })).textContent).toBe("Encrypted_Folder.zip");
  expect(screen.getByText(/1 encrypted.*1 failed/)).toBeTruthy();
  expect(HTMLAnchorElement.prototype.click).toHaveBeenCalledTimes(1);
});

it("keeps cancellation idle and allows retrying a failed folder", async () => {
  const user = userEvent.setup();
  render(<EncryptionTool />);
  const input = screen.getByLabelText("Select Office Folder") as HTMLInputElement;
  fireEvent.change(input, { target: { files: [] } });
  expect(screen.queryByRole("alert")).toBeNull();
  fireEvent.change(input, { target: { files: [file("Folder/report.docx")] } });
  await user.click(screen.getByRole("button", { name: "Cancel Folder Selection" }));
  expect(encryptStandaloneFolder).not.toHaveBeenCalled();
  vi.mocked(encryptStandaloneFolder).mockRejectedValueOnce(new Error("Folder too large."));
  fireEvent.change(input, { target: { files: [file("Folder/report.docx")] } });
  await user.click(screen.getByRole("button", { name: "Encrypt Selected Folder" }));
  expect((await screen.findByRole("alert")).textContent).toContain("Folder too large");
  fireEvent.change(input, { target: { files: [] } });
  expect(screen.getByRole("alert").textContent).toContain("Folder too large");
  await user.click(screen.getByRole("button", { name: "Encrypt Selected Folder" }));
  expect(await screen.findByRole("status", { name: "Downloaded File" })).toBeTruthy();
});

it("prevents concurrent file/folder operations and ignores late downloads after leaving", async () => {
  let finish!: (result: Awaited<ReturnType<typeof encryptStandaloneFolder>>) => void;
  vi.mocked(encryptStandaloneFolder).mockReturnValueOnce(new Promise(resolve => { finish = resolve; }));
  const user = userEvent.setup();
  const mounted = render(<EncryptionTool />);
  fireEvent.change(screen.getByLabelText("Select Office Folder"), { target: { files: [file("Folder/report.docx")] } });
  await user.click(screen.getByRole("button", { name: "Encrypt Selected Folder" }));
  expect(screen.getByLabelText("Select Office File")).toHaveProperty("disabled", true);
  expect(screen.getByLabelText("Select Office Folder")).toHaveProperty("disabled", true);
  fireEvent.change(screen.getByLabelText("Select Office File"), { target: { files: [file("report.docx")] } });
  expect(encryptStandaloneCopy).not.toHaveBeenCalled();
  mounted.unmount();
  await act(async () => finish({ blob: new Blob(["zip"]), fileName: "Encrypted_Folder.zip",
    summary: { succeeded: 1, failed: 0, skipped: 0 } }));
  expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
});

it("does not upload folders with no supported files or files over the upload limit", async () => {
  const user = userEvent.setup();
  render(<EncryptionTool />);
  const input = screen.getByLabelText("Select Office Folder");
  fireEvent.change(input, { target: { files: [file("Folder/photo.png")] } });
  expect(screen.getByRole("alert").textContent).toContain("No supported Word or Excel");
  const large = file("Folder/large.docx");
  Object.defineProperty(large, "size", { value: 101 * 1024 * 1024 });
  fireEvent.change(input, { target: { files: [large] } });
  await user.click(screen.getByRole("button", { name: "Encrypt Selected Folder" }));
  expect((await screen.findByRole("alert")).textContent).toContain("100 MB");
  expect(encryptStandaloneFolder).not.toHaveBeenCalled();
});

it("clearly distinguishes an all-failed outcome from successful encryption", async () => {
  vi.mocked(encryptStandaloneFolder).mockResolvedValue({ blob: new Blob(["csv only"]), fileName: "Encrypted_Folder.zip",
    summary: { succeeded: 0, failed: 1, skipped: 0 } });
  const user = userEvent.setup();
  render(<EncryptionTool />);
  fireEvent.change(screen.getByLabelText("Select Office Folder"), { target: { files: [file("Folder/no-number.xlsx")] } });
  await user.click(screen.getByRole("button", { name: "Encrypt Selected Folder" }));
  expect(await screen.findByText(/No files were encrypted/)).toBeTruthy();
});
