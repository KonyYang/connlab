import { describe, expect, it } from "vitest";

import type { MatrixEditorSessionDraft, MatrixPreviewResponse } from "../../api/client";
import { buildMatrixFromSessionSeedDraft } from "./matrixEditorDraftModel";

describe("buildMatrixFromSessionSeedDraft", () => {
  it("does not reuse a consumed draft row when a re-imported preview falls back by position", () => {
    const draft: MatrixEditorSessionDraft = {
      groups: [],
      rows: [
        {
          draft_row_id: "draft-visual",
          source_row_snapshot_id: "source-visual",
          row_order: 1,
          test_item: "VISUAL EXAMINATION",
          source_section: "7.1",
          is_sample_row: false,
        },
        {
          draft_row_id: "draft-reseating",
          source_row_snapshot_id: "source-reseating",
          row_order: 2,
          test_item: "Reseating.",
          source_section: "7.8",
          is_sample_row: false,
        },
      ],
      cells: [],
    };
    const preview: MatrixPreviewResponse = {
      source_document_path: "spec.pdf",
      source_document_name: "spec.pdf",
      source_format: "pdf",
      capability_status: "available",
      generated_at: "2026-08-25T00:00:00Z",
      candidate_tables: [],
      groups: [],
      rows: [
        {
          source_row_index: 1,
          test_item: "Reseating.",
          source_section: "7.8",
          group_tokens: {},
          is_sample_row: false,
        },
        {
          source_row_index: 2,
          test_item: "Crimping/Wending Tensile Strength",
          source_section: "7.6/7.7",
          group_tokens: {},
          is_sample_row: false,
        },
      ],
      warnings: [],
      blockers: [],
    };

    const result = buildMatrixFromSessionSeedDraft(draft, preview);

    expect(result.rows.map((row) => row.item)).toEqual([
      "Reseating.",
      "Crimping/Wending Tensile Strength",
      "VISUAL EXAMINATION",
    ]);
    expect(result.rows.map((row) => row.id)).toEqual([
      "draft-reseating",
      "source-row-2",
      "draft-visual",
    ]);
    expect(result.rows.map((row) => row.sourceRowSnapshotId)).toEqual([
      "source-reseating",
      null,
      "source-visual",
    ]);
  });
});
