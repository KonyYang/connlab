import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  executeProjectFileEncryption,
  previewProjectFileEncryption,
} from "../../api/client";
import { ProjectFileEncryptionAction } from "./ProjectFileEncryptionAction";

vi.mock("../../api/client", async () => {
  const actual = await vi.importActual<typeof import("../../api/client")>("../../api/client");
  return {
    ...actual,
    previewProjectFileEncryption: vi.fn(),
    executeProjectFileEncryption: vi.fn(),
  };
});

const previewMock = vi.mocked(previewProjectFileEncryption);
const executeMock = vi.mocked(executeProjectFileEncryption);

describe("ProjectFileEncryptionAction", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    previewMock.mockResolvedValue({
      project_id: "P1",
      status: "conflict",
      plan_token: "token-1",
      conflict_count: 1,
      blockers: [],
      warnings: ["Nonrecursive scan."],
      items: [
        {
          file_name: "record.docx",
          location: "test_results",
          office_kind: "word",
          mode: "secured_copy",
          conflict: true,
        },
      ],
    });
    executeMock.mockResolvedValue({
      project_id: "P1",
      encrypted_count: 0,
      skipped_count: 1,
      failed_count: 0,
      items: [],
    });
  });

  it("previews trusted candidates before showing overwrite, skip, and cancel", async () => {
    const user = userEvent.setup();
    render(<ProjectFileEncryptionAction projectId="P1" available />);

    await user.click(screen.getByRole("button", { name: "Preview" }));

    expect(previewMock).toHaveBeenCalledWith("P1");
    const dialog = await screen.findByRole("dialog", { name: "Encrypt project files preview" });
    expect(dialog.getAttribute("aria-modal")).toBe("true");
    expect(screen.getByText("record.docx")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Overwrite all" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Skip all" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Cancel" })).toBeTruthy();
  });

  it("executes skip-all with the preview token and reports the result", async () => {
    const user = userEvent.setup();
    render(<ProjectFileEncryptionAction projectId="P1" available />);

    await user.click(screen.getByRole("button", { name: "Preview" }));
    await user.click(await screen.findByRole("button", { name: "Skip all" }));

    await waitFor(() => {
      expect(executeMock).toHaveBeenCalledWith("P1", {
        expected_plan_token: "token-1",
        conflict_action: "skip",
      });
    });
    expect((await screen.findByRole("status")).textContent).toContain(
      "Encrypted 0; skipped 1; failed 0."
    );
  });

  it("stays disabled until an official project folder exists", () => {
    render(<ProjectFileEncryptionAction projectId="P1" available={false} />);

    const button = screen.getByRole("button", { name: "Preview" }) as HTMLButtonElement;
    expect(button.disabled).toBe(true);
    expect(button.title).toContain("Create the local project folder");
  });
});
