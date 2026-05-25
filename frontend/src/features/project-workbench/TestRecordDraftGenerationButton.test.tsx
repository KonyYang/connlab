import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { TestRecordDraftGenerationButton } from "./TestRecordDraftGenerationButton";

const apiMocks = vi.hoisted(() => ({
  generateConfirmedMatrixTestRecordDraft: vi.fn(),
}));

vi.mock("../../api/client", () => ({
  generateConfirmedMatrixTestRecordDraft: apiMocks.generateConfirmedMatrixTestRecordDraft,
}));

describe("TestRecordDraftGenerationButton", () => {
  beforeEach(() => {
    apiMocks.generateConfirmedMatrixTestRecordDraft.mockReset();
    globalThis.URL.createObjectURL = vi.fn(() => "blob:mock");
    globalThis.URL.revokeObjectURL = vi.fn();
    vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});
  });

  it("generates a Test Record draft when ready", async () => {
    apiMocks.generateConfirmedMatrixTestRecordDraft.mockResolvedValue(
      new Blob(["docx"], {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      })
    );

    render(<TestRecordDraftGenerationButton projectId="P1" ready />);

    fireEvent.click(screen.getByRole("button", { name: "Generate Test Record Draft" }));

    await waitFor(() => {
      expect(apiMocks.generateConfirmedMatrixTestRecordDraft).toHaveBeenCalledWith("P1");
    });
  });

  it("disables generation when confirmed Matrix preview is not ready", () => {
    render(<TestRecordDraftGenerationButton projectId="P1" ready={false} />);

    expect(
      screen.getByRole("button", { name: "Generate Test Record Draft" }).hasAttribute("disabled")
    ).toBe(true);
    expect(screen.getByText("Confirm Matrix authority before generating a Test Record draft.")).toBeTruthy();
  });

  it("shows an error when generation fails", async () => {
    apiMocks.generateConfirmedMatrixTestRecordDraft.mockRejectedValue(new Error("failed"));

    render(<TestRecordDraftGenerationButton projectId="P1" ready />);

    fireEvent.click(screen.getByRole("button", { name: "Generate Test Record Draft" }));

    expect(await screen.findByText("Unable to generate Test Record draft. Confirm Matrix authority and try again.")).toBeTruthy();
  });
});
