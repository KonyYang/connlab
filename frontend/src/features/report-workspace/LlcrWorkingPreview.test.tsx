import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import type { LlcrImportPreview } from "../../api/client";
import { LlcrImportPreviewDialog } from "./LlcrImportPreviewDialog";

const preview: LlcrImportPreview = {
  preview_id: "pending", project_id: "P1", confirmed_matrix_id: "M1", confirmed_matrix_revision: 1,
  source: { file_name: "readings.xlsx", sha256: "s", size_bytes: 100 }, parser_profile_version: "1",
  detected_sheets: ["SIG"], can_confirm: false, sample_count: 2, test_point_count: 1, result_count: 0,
  entries: [], diagnostics: [{ code: "missing", severity: "blocked", message: "Sample 02: missing SIG!E11", group_label: "1", step_token: "2" }],
};

it("keeps a blocked import in its chapter, lets the user choose corrected Excel, then offers confirmation separately from writing Word", () => {
  const onReplace = vi.fn(), onConfirm = vi.fn();
  const props = { preview, drafts: {}, confirming: false, canceling: false, onDraftChange: vi.fn(), onCancel: vi.fn(), onConfirm, onReplace };
  const view = render(<LlcrImportPreviewDialog {...props} />);
  expect(screen.queryByRole("dialog")).toBeNull();
  expect(screen.getByText(/SIG!E11/)).toBeTruthy();
  expect(screen.queryByRole("button", { name: "Confirm readings" })).toBeNull();
  const file = new File(["replacement"], "corrected.xlsx");
  fireEvent.change(screen.getByLabelText("Corrected LLCR workbook"), { target: { files: [file] } });
  expect(onReplace).toHaveBeenCalledWith(file);
  view.rerender(<LlcrImportPreviewDialog {...props} preview={{ ...preview, can_confirm: true, diagnostics: [] }} />);
  fireEvent.click(screen.getByRole("button", { name: "Confirm readings" }));
  expect(onConfirm).toHaveBeenCalledOnce();
  expect(screen.queryByRole("button", {name: /Update.*working copy/i})).toBeNull();
});
