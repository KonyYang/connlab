import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { MatrixImportSourceCandidatePicker } from "./MatrixImportSourceCandidatePicker";

describe("MatrixImportSourceCandidatePicker", () => {
  it("uses the filename card itself for explicit selection", () => {
    const onUseCandidate = vi.fn();
    render(
      <MatrixImportSourceCandidatePicker
        candidates={[
          { candidate_id: "source-1", file_name: "matrix.docx" },
          { candidate_id: "source-2", file_name: "request.pdf" },
        ]}
        sourceTitle="Submitted Material files"
        loading={false}
        previewBusy={false}
        error={null}
        onCancel={vi.fn()}
        onUploadOtherFile={vi.fn()}
        onUseCandidate={onUseCandidate}
      />
    );

    const names = screen.getAllByTestId("matrix-import-source-name");
    expect(names.map((element) => element.textContent)).toEqual(["matrix.docx", "request.pdf"]);
    expect(screen.getByRole("heading", { name: "Submitted Material files" })).toBeTruthy();
    expect(screen.queryByText("Recommended")).toBeNull();
    expect(screen.queryByText("attachment")).toBeNull();
    expect(screen.queryByText("Matrix keywords found.")).toBeNull();
    expect(onUseCandidate).not.toHaveBeenCalled();
    const matrixCard = screen.getByRole("button", { name: "Select matrix.docx" });
    expect(matrixCard.classList.contains("matrix-import-source-picker-row")).toBe(true);
    expect(matrixCard.textContent).toBe("matrix.docx");
    expect(matrixCard.querySelector("button")).toBeNull();
    fireEvent.click(matrixCard);
    expect(onUseCandidate).toHaveBeenCalledWith("source-1");
  });

  it("confirms a focused filename card from the keyboard", async () => {
    const user = userEvent.setup();
    const onUseCandidate = vi.fn();
    render(
      <MatrixImportSourceCandidatePicker
        candidates={[{ candidate_id: "source-1", file_name: "matrix.docx" }]}
        sourceTitle="Submitted Material files"
        loading={false}
        previewBusy={false}
        error={null}
        onCancel={vi.fn()}
        onUploadOtherFile={vi.fn()}
        onUseCandidate={onUseCandidate}
      />
    );

    const matrixCard = screen.getByRole("button", { name: "Select matrix.docx" });
    matrixCard.focus();
    await user.keyboard("{Enter}");

    expect(onUseCandidate).toHaveBeenCalledWith("source-1");
  });

  it("keeps upload and cancel available for empty and failed loads", () => {
    const onCancel = vi.fn();
    const onUploadOtherFile = vi.fn();
    render(
      <MatrixImportSourceCandidatePicker candidates={[]} sourceTitle="Email attachment files" loading={false} previewBusy={false} error="Could not load project sources." onCancel={onCancel} onUploadOtherFile={onUploadOtherFile} onUseCandidate={vi.fn()} />
    );

    expect(screen.getByText("Could not load project sources.")).toBeTruthy();
    expect(screen.getByText("No project candidates are available. Upload another file to continue.")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Upload other file" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onUploadOtherFile).toHaveBeenCalledOnce();
    expect(onCancel).toHaveBeenCalledOnce();
  });

  it("shows loading and disables source actions while busy", () => {
    render(
      <MatrixImportSourceCandidatePicker
        candidates={[{ candidate_id: "source-1", file_name: "matrix.docx" }]}
        sourceTitle="Project source files"
        loading={true}
        previewBusy={false}
        error={null}
        onCancel={vi.fn()}
        onUploadOtherFile={vi.fn()}
        onUseCandidate={vi.fn()}
      />
    );

    expect(screen.getByText("Loading project sources...")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Select matrix.docx" })).toHaveProperty("disabled", true);
    expect(screen.getByRole("button", { name: "Upload other file" })).toHaveProperty("disabled", true);
    expect(screen.getByRole("button", { name: "Cancel" })).toHaveProperty("disabled", true);
  });
});
