import { describe, expect, it } from "vitest";

import { mapProjectDurationAuthoritiesForSession } from "./MatrixEditorWorkspace";

describe("Matrix Editor duration authority preservation", () => {
  it("preserves normalized authority fields from draft seed to save and confirm payloads", () => {
    const mapped = mapProjectDurationAuthoritiesForSession([
      {
        duration_authority_id: "duration-1",
        group_id: "group-1",
        row_id: "row-1",
        step_sequence: 1,
        step_suffix_note: "",
        duration_value: "2",
        duration_unit: "days",
        normalized_hours: "48",
        source_kind: "import_structured",
        source_field: "duration_authorities[0]",
        source_import_id: "import-1",
        source_fingerprint: "source-fp",
        lineage_fingerprint: "lineage-fp",
        authority_revision: "1",
        status: "usable",
        diagnostic_code: null,
        diagnostic_message: null,
      },
    ]);

    expect(mapped).toEqual([
      {
        draft_duration_authority_id: "duration-1",
        draft_group_id: "group-1",
        draft_row_id: "row-1",
        step_sequence: 1,
        step_suffix_note: "",
        duration_value: "2",
        duration_unit: "days",
        normalized_hours: "48",
        source_kind: "import_structured",
        source_field: "duration_authorities[0]",
        source_import_id: "import-1",
        source_fingerprint: "source-fp",
        lineage_fingerprint: "lineage-fp",
        authority_revision: "1",
        status: "usable",
      },
    ]);
    expect({ duration_authorities: mapped }).toEqual({
      duration_authorities: mapped,
    });
  });

  it("keeps legacy drafts without typed authority empty", () => {
    expect(mapProjectDurationAuthoritiesForSession(undefined)).toEqual([]);
  });
});
