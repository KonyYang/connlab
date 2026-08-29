import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { MatrixImportDialog } from "./MatrixImportDialog";
import type { MatrixImportDialogView } from "./useMatrixImportWorkflow";

function view(sourceFormat: string): MatrixImportDialogView {
  return {
    actionBusy: false,
    close: vi.fn(),
    error: null,
    fileName: "DL-2026-08-004 Matrix.xlsx",
    importingPreview: false,
    locatorKeyword: "",
    locatorPage: "",
    locatorTableOnPage: "",
    lookupMessage: "Matrix found: 2 groups detected.",
    lookupTone: "success",
    preview: {
      source_document_path: "DL-2026-08-004 Matrix.xlsx",
      source_document_name: "DL-2026-08-004 Matrix.xlsx",
      source_format: sourceFormat,
      capability_status: "supported",
      generated_at: "2026-08-29T00:00:00Z",
      candidate_tables: [],
      rows: [
        {
          source_row_index: 2,
          test_item: "Visual",
          group_tokens: { group_1: "1" },
          is_sample_row: false,
          day_expression: "0",
        },
      ],
      groups: [
        {
          group_key: "group_1",
          group_label: "Group 1",
          source_table_index: 1,
          extraction_status: "xlsx_visible_table",
          steps: [],
        },
      ],
      warnings: ["Day defaults to 0."],
      blockers: [],
    },
    previewPdfSrc: null,
    replace: vi.fn().mockResolvedValue(undefined),
    updateLocator: vi.fn(),
  };
}

describe("MatrixImportDialog", () => {
  it("shows a structured summary and hides document locators for xlsx", () => {
    render(<MatrixImportDialog dialog={view(".xlsx")} readOnly={false} />);

    expect(screen.getByText("ConnLab Matrix workbook")).not.toBeNull();
    expect(screen.getByText("1 Group · 1 test row")).not.toBeNull();
    expect(screen.getByText("Day defaults to 0.")).not.toBeNull();
    expect(screen.queryByText("Page")).toBeNull();
    expect(screen.queryByText("Table on page")).toBeNull();
    expect(screen.queryByText("Table Title / Content Keyword")).toBeNull();
  });
});
