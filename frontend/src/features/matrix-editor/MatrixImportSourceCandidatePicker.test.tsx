import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MatrixImportSourceCandidatePicker } from "./MatrixImportSourceCandidatePicker";

describe("MatrixImportSourceCandidatePicker", () => {
  it("preserves API order and requires explicit selection", () => {
    const onUseCandidate = vi.fn();
    render(
      <MatrixImportSourceCandidatePicker
        candidates={[
          { source_asset_id: "source-1", original_name: "matrix.docx", extension: ".docx", asset_type: "attachment", candidate_kind: "likely_spec_or_matrix", reason: "Matrix keywords found.", stored_file_available: true },
          { source_asset_id: "source-2", original_name: "request.docx", extension: ".docx", asset_type: "application_form", candidate_kind: "fallback_word_attachment", reason: "Word attachment fallback.", stored_file_available: false },
        ]}
        loading={false}
        previewBusy={false}
        error={null}
        onCancel={vi.fn()}
        onUploadOtherFile={vi.fn()}
        onUseCandidate={onUseCandidate}
      />
    );

    const names = screen.getAllByTestId("matrix-import-source-name");
    expect(names.map((element) => element.textContent)).toEqual(["matrix.docx", "request.docx"]);
    expect(screen.getByText("Recommended")).toBeTruthy();
    expect(screen.getByText(".docx · attachment")).toBeTruthy();
    expect(screen.getByText("Matrix keywords found.")).toBeTruthy();
    expect(onUseCandidate).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Use this file: matrix.docx" }));
    expect(onUseCandidate).toHaveBeenCalledWith("source-1");
    expect(screen.getByRole("button", { name: "Use this file: request.docx" })).toHaveProperty("disabled", true);
    expect(screen.getByText("Unavailable")).toBeTruthy();
  });

  it("keeps upload and cancel available for empty and failed loads", () => {
    const onCancel = vi.fn();
    const onUploadOtherFile = vi.fn();
    render(
      <MatrixImportSourceCandidatePicker candidates={[]} loading={false} previewBusy={false} error="Could not load project sources." onCancel={onCancel} onUploadOtherFile={onUploadOtherFile} onUseCandidate={vi.fn()} />
    );

    expect(screen.getByText("Could not load project sources.")).toBeTruthy();
    expect(screen.getByText("No project candidates are available. Upload another file to continue.")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Upload other file" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));
    expect(onUploadOtherFile).toHaveBeenCalledOnce();
    expect(onCancel).toHaveBeenCalledOnce();
  });
});
