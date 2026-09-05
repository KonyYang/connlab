// Opt-in diagnostic, not a timing gate: VITE_MATRIX_PROFILE=1 npm exec -- vitest run ...
// Function wrappers call through unchanged and are restored; counts explain the Profiler result.
import { Profiler } from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { expect, it, vi } from "vitest";
import { apiMocks, buildSessionSeed, installMatrixEditorWorkspaceTestLifecycle } from "./MatrixEditorWorkspace.testSupport";
import { MatrixEditorWorkspace } from "./MatrixEditorWorkspace";
import * as draftModel from "./matrixEditorDraftModel";
import * as xlsxProjection from "./matrixEditorXlsxExportProjection";
import * as schedule from "./matrixSchedulePlanning";
import * as steps from "./matrixStepWorkspaceModel";

installMatrixEditorWorkspaceTestLifecycle();

it.skipIf(!import.meta.env.VITE_MATRIX_PROFILE)("profiles a fixed 80 row, 8 group Matrix through public input", async () => {
  const seed = buildSessionSeed();
  const group = seed.editor_draft.groups[0];
  const row = seed.editor_draft.rows[0];
  seed.editor_draft.groups = Array.from({ length: 8 }, (_, i) => ({
    ...group, draft_group_id: `group-${i + 1}`, source_group_snapshot_id: `sg-${i + 1}`,
    group_order: i + 1, group_key: `g${i + 1}`, group_label: `${i + 1}`,
  }));
  seed.editor_draft.rows = Array.from({ length: 80 }, (_, i) => ({
    ...row, draft_row_id: `row-${i + 1}`, source_row_snapshot_id: `sr-${i + 1}`,
    row_order: i + 1, test_item: `Examination ${i + 1}`,
  }));
  seed.editor_draft.cells = seed.editor_draft.rows.flatMap((r, i) => seed.editor_draft.groups.map((g) => ({
    draft_row_id: r.draft_row_id, draft_group_id: g.draft_group_id, cell_value: `${i + 1}`,
  })));
  apiMocks.fetchMatrixEditorSession.mockResolvedValueOnce(seed);
  const observed = {
    save: vi.spyOn(draftModel, "buildDraftSavePayload"),
    record: vi.spyOn(draftModel, "buildMatrixEditorTestRecordDraftRequest"),
    xlsx: vi.spyOn(xlsxProjection, "buildMatrixEditorXlsxExportRequest"),
    schedule: vi.spyOn(schedule, "calculateMatrixSchedule"),
    steps: vi.spyOn(steps, "parseStepTokens"),
  };
  let durations: number[] = [];
  try {
    render(<Profiler id="Matrix" onRender={(_id, _phase, duration) => durations.push(duration)}>
      <MatrixEditorWorkspace projectId="P1" onBackToWorkbench={() => {}} />
    </Profiler>);
    const description = await screen.findByLabelText("Step 1 description");
    const cell = screen.getByLabelText("Row 1 1");
    for (const [action, input, value] of [
      ["description", description, (i: number) => `Measured text ${i}`],
      ["cell", cell, (i: number) => i % 2 ? "1" : "1(a)"],
    ] as const) {
      durations = [];
      Object.values(observed).forEach((spy) => spy.mockClear());
      for (let i = 0; i < 10; i++) fireEvent.change(input, { target: { value: value(i) } });
      const sorted = [...durations].sort((a, b) => a - b);
      console.info("MATRIX_PROFILE", JSON.stringify({
        action, rows: 80, groups: 8, changes: 10, commits: durations.length,
        renderTotalMs: +durations.reduce((a, b) => a + b, 0).toFixed(2),
        renderMedianMs: +sorted[Math.floor(sorted.length / 2)].toFixed(2),
        calls: Object.fromEntries(Object.entries(observed).map(([key, spy]) => [key, spy.mock.calls.length])),
      }));
      expect((input as HTMLTextAreaElement).value).toBe(value(9));
    }
  } finally {
    Object.values(observed).forEach((spy) => spy.mockRestore());
  }
}, 30000);
