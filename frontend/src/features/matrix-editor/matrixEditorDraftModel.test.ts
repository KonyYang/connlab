import { describe, expect, it } from "vitest";

import type { MatrixEditorSessionDraft, MatrixPreviewResponse } from "../../api/client";
import { buildMatrixFromSessionSeedDraft } from "./matrixEditorDraftModel";

describe("buildMatrixFromSessionSeedDraft", () => {
  it("matches repeated test identities one-to-one without appending a duplicate draft row", () => {
    const draft: MatrixEditorSessionDraft = {
      groups: [
        {
          draft_group_id: "draft-group-1",
          source_group_snapshot_id: "source-group-1",
          group_order: 1,
          group_key: "g1",
          group_label: "1",
          is_selected: true,
          sample_quantity_expression: "3+3",
        },
      ],
      rows: [
        {
          draft_row_id: "draft-ir-initial",
          source_row_snapshot_id: "source-ir-initial",
          row_order: 1,
          test_item: "INSULATION RESISTANCE",
          source_section: "6.2",
          requirement: "Initial ≥1500MΩ",
          is_sample_row: false,
        },
        {
          draft_row_id: "draft-ir-final",
          source_row_snapshot_id: "source-ir-final",
          row_order: 2,
          test_item: "INSULATION RESISTANCE",
          source_section: "6.2",
          requirement: "Final ≥5000MΩ",
          is_sample_row: false,
        },
      ],
      cells: [
        {
          draft_row_id: "draft-ir-initial",
          draft_group_id: "draft-group-1",
          cell_value: "3,9",
        },
        {
          draft_row_id: "draft-ir-final",
          draft_group_id: "draft-group-1",
          cell_value: "4,10",
        },
      ],
    };
    const preview: MatrixPreviewResponse = {
      source_document_path: "spec.pdf",
      source_document_name: "spec.pdf",
      source_format: "pdf",
      capability_status: "available",
      generated_at: "2026-09-03T00:00:00Z",
      candidate_tables: [],
      groups: [
        {
          group_key: "g1",
          group_label: "1",
          source_table_index: 0,
          extraction_status: "loaded",
          sample_quantity_expression: "3+3",
          sample_note: null,
          steps: [],
        },
      ],
      rows: [
        {
          source_row_index: 1,
          test_item: "INSULATION RESISTANCE",
          source_section: "6.2",
          requirement: "Initial ≥1500MΩ",
          group_tokens: { "1": "3,9" },
          is_sample_row: false,
        },
        {
          source_row_index: 2,
          test_item: "INSULATION RESISTANCE",
          source_section: "6.2",
          requirement: "Final ≥5000MΩ",
          group_tokens: { "1": "4,10" },
          is_sample_row: false,
        },
      ],
      warnings: [],
      blockers: [],
    };

    const result = buildMatrixFromSessionSeedDraft(draft, preview);

    expect(result.rows.map((row) => row.id)).toEqual([
      "draft-ir-initial",
      "draft-ir-final",
    ]);
    expect(result.rows.map((row) => row.groups["draft-group-1"])).toEqual([
      "3,9",
      "4,10",
    ]);
  });

  it("keeps the saved row order and never restores rows from an older source preview", () => {
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
      "VISUAL EXAMINATION",
      "Reseating.",
    ]);
    expect(result.rows.map((row) => row.id)).toEqual([
      "draft-visual",
      "draft-reseating",
    ]);
    expect(result.rows.map((row) => row.sourceRowSnapshotId)).toEqual([
      "source-visual",
      "source-reseating",
    ]);
  });

  it("does not resurrect deleted IPX7 or overwrite cleared fields and renamed groups", () => {
    const draft: MatrixEditorSessionDraft = {
      groups: [{ draft_group_id: "g", group_key: "g1", group_order: 1,
        group_label: "Edited", is_selected: true, sample_quantity_expression: "5" }],
      rows: [{ draft_row_id: "r", row_order: 1, test_item: "Visual", method: "",
        condition: "", requirement: "", is_sample_row: false }],
      cells: [{ draft_row_id: "r", draft_group_id: "g", cell_value: "1" }],
    };
    const preview: MatrixPreviewResponse = {
      source_document_path: "matrix.xlsx", source_document_name: "matrix.xlsx", source_format: "xlsx",
      capability_status: "available", generated_at: "", candidate_tables: [], warnings: [], blockers: [],
      groups: [{ group_key: "g1", group_label: "Original", source_table_index: 0,
        extraction_status: "loaded", sample_quantity_expression: "3", sample_note: null, steps: [] }],
      rows: [
        { source_row_index: 1, test_item: "Visual", method: "Original", group_tokens: {g1: "1"}, is_sample_row: false },
        { source_row_index: 2, test_item: "IPX7 testing", group_tokens: {g1: "2"}, is_sample_row: false },
      ],
    };
    const result = buildMatrixFromSessionSeedDraft(draft, preview);
    expect(result.rows.map(row => row.item)).toEqual(["Visual"]);
    expect(result.rows[0].method).toBe("");
    expect(result.groups[0].name).toBe("Edited");
    expect(buildMatrixFromSessionSeedDraft({...draft, rows: [], cells: []}, preview).rows).toEqual([]);
  });
});
