import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { encryptLocalFile, encryptLocalFolder } from "../../api/client";
import { bindRuntime, clearRuntimeBinding } from "../../runtimeEnvironment";
import { EncryptionTool } from "./EncryptionTool";

vi.mock("../../api/client", () => ({ encryptLocalFile: vi.fn(), encryptLocalFolder: vi.fn() }));
const completed = { cancelled: false as const, folder: "D:/Lab", summary: { succeeded: 1, failed: 1, skipped: 2 },
  entries: [{ file: "no-number.xlsx", status: "Failed", reason: "Excel files must start with DL-YYYY-MM-NNN." }] };

const devRuntime = { schema_version: 1 as const, environment: "development" as const, instance_id: "dev-encryption", default_output_paths: {} };

beforeEach(() => {
  window.localStorage.clear();
  bindRuntime(devRuntime);
  vi.resetAllMocks();
  vi.stubGlobal("URL", { createObjectURL: vi.fn(() => "blob:encrypted"), revokeObjectURL: vi.fn() });
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
  vi.mocked(encryptLocalFolder).mockResolvedValue(completed);
});

afterEach(clearRuntimeBinding);

async function showChoices() {
  await userEvent.click(screen.getByRole("button", { name: "Encryption options" }));
}

it("chooses a local folder and reports saved siblings without uploads or downloads", async () => {
  render(<EncryptionTool />);
  await showChoices();
  await userEvent.click(screen.getByRole("menuitem", { name: /Encrypt a folder/ }));
  expect(await screen.findByText(/1 encrypted.*1 failed.*2 skipped/)).toBeTruthy();
  expect(screen.getByText("D:/Lab")).toBeTruthy();
  expect(screen.queryByLabelText("Select Office Folder")).toBeNull();
  expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
  expect(screen.queryByText(/Failed files/)).toBeNull();
  expect(screen.queryByText(/no-number.xlsx/)).toBeNull();
});

it("keeps previous feedback on picker cancellation and allows retry after errors", async () => {
  render(<EncryptionTool />);
  await showChoices();
  await userEvent.click(screen.getByRole("menuitem", { name: /Encrypt a folder/ }));
  await screen.findByText("D:/Lab");
  const button = screen.getByRole("button", { name: "Encrypt Folder", exact: true });
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
  await showChoices();
  await userEvent.click(screen.getByRole("menuitem", { name: /Encrypt a folder/ }));
  expect(screen.queryByRole("menu")).toBeNull();
  expect(screen.getByRole("button", { name: "Working..." })).toHaveProperty("disabled", true);
  const options = screen.getByRole("button", { name: "Encryption options" });
  expect(options).toHaveProperty("disabled", true);
  await userEvent.click(options);
  expect(encryptLocalFile).not.toHaveBeenCalled();
  mounted.unmount();
  await act(async () => finish(completed));
  expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
});

it("clearly reports zero successful files", async () => {
  vi.mocked(encryptLocalFolder).mockResolvedValue({ ...completed, summary: { succeeded: 0, failed: 1, skipped: 0 } });
  render(<EncryptionTool />);
  await showChoices();
  await userEvent.click(screen.getByRole("menuitem", { name: /Encrypt a folder/ }));
  expect(await screen.findByText(/No files were encrypted/)).toBeTruthy();
});

it.each([".ppt", ".pptx"])("saves a single %s presentation beside the source without downloading", async suffix => {
  vi.mocked(encryptLocalFile).mockResolvedValue({ cancelled: false, folder: "D:/Lab", summary: { succeeded: 1, failed: 0, skipped: 0 },
    entries: [{ file: `slides${suffix}`, status: "Encrypted", reason: "", output: `slides_Secured${suffix}` }] });
  render(<EncryptionTool />);
  await userEvent.click(screen.getByRole("button", { name: "Encrypt File", exact: true }));
  expect((await screen.findByRole("status", { name: "Saved Encrypted File" })).textContent).toContain(`slides_Secured${suffix}`);
  expect(screen.queryByLabelText("Select Office File")).toBeNull();
  expect(URL.createObjectURL).not.toHaveBeenCalled();
  expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
});


it("opens the two-action menu with the keyboard and restores focus on Escape", async () => {
  const user = userEvent.setup();
  render(<><EncryptionTool /><button type="button">Other tool</button></>);
  const entry = screen.getByRole("button", { name: "Encryption options" });
  expect(entry.getAttribute("aria-expanded")).toBe("false");
  entry.focus();
  await user.keyboard("{ArrowDown}");
  const file = screen.getByRole("menuitem", { name: /Encrypt one file/ });
  const folder = screen.getByRole("menuitem", { name: /Encrypt a folder/ });
  expect(entry.getAttribute("aria-expanded")).toBe("true");
  expect(document.activeElement).toBe(file);
  await user.keyboard("{ArrowDown}");
  expect(document.activeElement).toBe(folder);
  await user.keyboard("{Escape}");
  expect(screen.queryByRole("menu")).toBeNull();
  expect(document.activeElement).toBe(entry);
  await user.click(entry);
  await user.click(screen.getByRole("button", { name: "Other tool" }));
  expect(screen.queryByRole("menu")).toBeNull();
  expect(encryptLocalFile).not.toHaveBeenCalled();
  expect(encryptLocalFolder).not.toHaveBeenCalled();
});

it("remembers a confirmed mode and keeps release storage separate", async () => {
  const user = userEvent.setup();
  vi.mocked(encryptLocalFile).mockResolvedValue({ cancelled: true });
  const first = render(<EncryptionTool />);
  await user.click(screen.getByRole("button", { name: "Encrypt File", exact: true }));
  expect(encryptLocalFile).toHaveBeenCalledTimes(1);
  expect(encryptLocalFolder).not.toHaveBeenCalled();
  await user.click(screen.getByRole("button", { name: "Encryption options" }));
  const folderChoice = screen.getByRole("menuitem", { name: /Encrypt a folder/ });
  vi.mocked(encryptLocalFolder).mockResolvedValueOnce({ cancelled: true });
  await user.click(folderChoice);
  expect(screen.getByRole("button", { name: "Encrypt File", exact: true })).toBeTruthy();
  expect(screen.queryByRole("menu")).toBeNull();
  await user.click(screen.getByRole("button", { name: "Encryption options" }));
  await user.click(screen.getByRole("menuitem", { name: /Encrypt a folder/ }));
  await screen.findByRole("button", { name: "Encrypt Folder", exact: true });
  first.unmount();

  const release = { ...devRuntime, environment: "release" as const, instance_id: "release-encryption" };
  bindRuntime(release);
  const separate = render(<EncryptionTool />);
  expect(screen.getByRole("button", { name: "Encrypt File", exact: true })).toBeTruthy();
  separate.unmount();
  bindRuntime(devRuntime);
  render(<EncryptionTool />);
  await user.click(screen.getByRole("button", { name: "Encrypt Folder", exact: true }));
  expect(encryptLocalFolder).toHaveBeenCalledTimes(3);
});
