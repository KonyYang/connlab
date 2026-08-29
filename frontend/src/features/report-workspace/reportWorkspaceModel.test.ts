import { describe, expect, it } from "vitest";
import type { LlcrImportPreview, ReportWorkspaceState } from "../../api/client";
import {
  buildLlcrConfirmationDecisions,
  deriveReportWorkspaceReadiness,
  formatLlcrSummary,
  validateLlcrConfirmation,
} from "./reportWorkspaceModel";

const state: ReportWorkspaceState = {
  project_id: "project-1",
  basic_information_status: "confirmed",
  confirmed_basic_information_version: 3,
  active_confirmed_matrix_id: "matrix-7",
  active_confirmed_matrix_revision: 7,
  latest_report_revision: null,
  datasets: [],
  report_revisions: [],
};

const preview: LlcrImportPreview = {
  preview_id: "preview-1",
  project_id: "project-1",
  confirmed_matrix_id: "matrix-7",
  confirmed_matrix_revision: 7,
  source: { file_name: "LLCR.xlsx", sha256: "abc", size_bytes: 123 },
  parser_profile_version: "connlab-llcr-v1",
  detected_sheets: ["Summary", "P"],
  can_confirm: true,
  sample_count: 6,
  test_point_count: 24,
  result_count: 1,
  diagnostics: [],
  entries: [
    {
      result_id: "result-1",
      group_label: "1",
      matrix_step_token: "2",
      stage: "initial",
      stage_label: "Initial",
      requirement: "≤ 0.198 mΩ",
      unit: "mΩ",
      measurement_count: 24,
      summary_min: "0.031",
      summary_max: "0.082",
      summary_average: "0.0565",
      provisional_outcome: "pass",
      confirmed_outcome: null,
      override_reason: null,
      source_range: "P!B10:Y10",
      report_target: "Group 1 / Step 2",
    },
  ],
};

describe("reportWorkspaceModel", () => {
  it("requires confirmed Basic Information and an active Confirmed Matrix for initial drafts", () => {
    expect(deriveReportWorkspaceReadiness(state)).toMatchObject({
      canGenerateInitialDraft: true,
      initialDraftBlocker: null,
      canGenerateLlcrDraft: false,
    });
    expect(
      deriveReportWorkspaceReadiness({ ...state, basic_information_status: "missing" })
    ).toMatchObject({
      canGenerateInitialDraft: false,
      initialDraftBlocker: "Confirm Basic Information before generating a report draft.",
    });
  });

  it("treats a dataset from an older revision of the same Matrix as stale", () => {
    const dataset = {
      dataset_id: "dataset-1",
      dataset_type: "llcr" as const,
      revision: 1,
      project_id: "project-1",
      confirmed_matrix_id: "matrix-7",
      confirmed_matrix_revision: 6,
      source_file_name: "LLCR.xlsx",
      source_sha256: "abc",
      parser_profile_version: "connlab-llcr-v1",
      validation_status: "confirmed",
      confirmed_at: "2026-08-29T09:00:00Z",
      confirmed_by: "Lab User",
      entries: [],
    };

    expect(deriveReportWorkspaceReadiness({ ...state, datasets: [dataset] })).toMatchObject({
      canGenerateLlcrDraft: false,
      llcrDraftBlocker: "The latest LLCR Result Dataset is stale for the active Confirmed Matrix.",
    });
  });

  it("requires a reason only when the user changes the provisional outcome", () => {
    const matching = { "result-1": { outcome: "pass" as const, overrideReason: "" } };
    expect(validateLlcrConfirmation(preview, matching)).toEqual([]);
    expect(buildLlcrConfirmationDecisions(preview, matching)).toEqual([
      { result_id: "result-1", outcome: "pass", override_reason: null },
    ]);

    const overridden = { "result-1": { outcome: "fail" as const, overrideReason: "" } };
    expect(validateLlcrConfirmation(preview, overridden)).toEqual([
      "Group 1 / Step 2 needs an override reason.",
    ]);
  });

  it("keeps blocking parser diagnostics authoritative", () => {
    const blocked = {
      ...preview,
      can_confirm: false,
      diagnostics: [
        {
          code: "missing_stage",
          severity: "error",
          message: "Final stage is missing.",
          group_label: "1",
          step_token: "2",
        },
      ],
    };
    expect(
      validateLlcrConfirmation(blocked, {
        "result-1": { outcome: "pass", overrideReason: "" },
      })
    ).toContain("Resolve every blocking diagnostic before confirmation.");
  });

  it("formats floating-point tails for preview without changing the payload", () => {
    const entry = {
      ...preview.entries[0],
      summary_min: "0.00399999999999999",
      summary_max: "0.00400000000000001",
      summary_average: "0.003999999999999996",
    };

    expect(formatLlcrSummary(entry)).toBe("0.004 / 0.004 / 0.004 mΩ");
    expect(entry.summary_max).toBe("0.00400000000000001");
  });
});
