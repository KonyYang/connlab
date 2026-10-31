import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { encryptLocalFile, encryptLocalFolder } from "../../api/client";
import { EncryptionTool } from "./EncryptionTool";

vi.mock("../../api/client", () => ({ encryptLocalFile: vi.fn(), encryptLocalFolder: vi.fn() }));
const completed = { cancelled: false as const, folder: "D:/Lab", summary: { succeeded: 1, failed: 1, skipped: 2 },
  entries: [{ file: "no-number.xlsx", status: "Failed", reason: "Excel files must start with DL-YYYY-MM-NNN." }] };

beforeEach(() => {
  vi.resetAllMocks();
  vi.stubGlobal("URL", { createObjectURL: vi.fn(() => "blob:encrypted"), revokeObjectURL: vi.fn() });
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
  vi.mocked(encryptLocalFolder).mockResolvedValue(completed);
});

it("chooses a local folder and reports saved siblings without uploads or downloads", async () => {
  render(<EncryptionTool />);
  await userEvent.click(screen.getByRole("button", { name: "Choose Folder" }));
  expect(await screen.findByText(/1 encrypted.*1 failed.*2 skipped/)).toBeTruthy();
  expect(screen.getByText("D:/Lab")).toBeTruthy();
  expect(screen.queryByLabelText("Select Office Folder")).toBeNull();
  expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
  await userEvent.click(screen.getByText("Failed files (1)"));
  expect(screen.getByText(/no-number.xlsx.*DL-YYYY-MM-NNN/)).toBeTruthy();
});

it("keeps previous feedback on picker cancellation and allows retry after errors", async () => {
  render(<EncryptionTool />);
  const button = screen.getByRole("button", { name: "Choose Folder" });
  await userEvent.click(button);
  await screen.findByText("D:/Lab");
  vi.mocked(encryptLocalFolder).mockResolvedValueOnce({ cancelled: true });
  await userEvent.click(button);
  expect(screen.getByText("D:/Lab")).toBeTruthy();
  vi.mocked(encryptLocalFolder).mockRejectedValueOnce(new Error("Check folder access."));
  await userEvent.click(button);
  expect((await screen.findByRole("alert")).textContent).toContain("Check folder access");
  await userEvent.click(button);
  expect(screen.queryByRole("alert")).toBeNull();
});

it("prevents concurrent operations and ignores late feedback after leaving", async () => {
  let finish!: (result: Awaited<ReturnType<typeof encryptLocalFolder>>) => void;
  vi.mocked(encryptLocalFolder).mockReturnValueOnce(new Promise(resolve => { finish = resolve; }));
  const mounted = render(<EncryptionTool />);
  await userEvent.click(screen.getByRole("button", { name: "Choose Folder" }));
  expect(screen.getByRole("button", { name: "Create Encrypted Copy" })).toHaveProperty("disabled", true);
  await userEvent.click(screen.getByRole("button", { name: "Create Encrypted Copy" }));
  expect(encryptLocalFile).not.toHaveBeenCalled();
  mounted.unmount();
  await act(async () => finish(completed));
  expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
});

it("clearly reports zero successful files", async () => {
  vi.mocked(encryptLocalFolder).mockResolvedValue({ ...completed, summary: { succeeded: 0, failed: 1, skipped: 0 } });
  render(<EncryptionTool />);
  await userEvent.click(screen.getByRole("button", { name: "Choose Folder" }));
  expect(await screen.findByText(/No files were encrypted/)).toBeTruthy();
});

it.each([".ppt", ".pptx"])("saves a single %s presentation beside the source without downloading", async suffix => {
  vi.mocked(encryptLocalFile).mockResolvedValue({ cancelled: false, folder: "D:/Lab", summary: { succeeded: 1, failed: 0, skipped: 0 },
    entries: [{ file: `slides${suffix}`, status: "Encrypted", reason: "", output: `slides_Secured${suffix}` }] });
  render(<EncryptionTool />);
  await userEvent.click(screen.getByRole("button", { name: "Create Encrypted Copy" }));
  expect((await screen.findByRole("status", { name: "Saved Encrypted File" })).textContent).toContain(`slides_Secured${suffix}`);
  expect(screen.queryByLabelText("Select Office File")).toBeNull();
  expect(URL.createObjectURL).not.toHaveBeenCalled();
  expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
});
