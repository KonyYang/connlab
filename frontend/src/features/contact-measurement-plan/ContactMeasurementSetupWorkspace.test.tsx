import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { ContactMeasurementPlanWorkspace } from "../../api/client";
import { ContactMeasurementSetupWorkspace } from "./ContactMeasurementSetupWorkspace";

const model = vi.hoisted(() => ({ current: null as Record<string, unknown> | null }));

vi.mock("./useContactMeasurementPlanModel", () => ({
  useContactMeasurementPlanModel: () => model.current,
}));

describe("ContactMeasurementSetupWorkspace", () => {
  it("renders freeform category controls, optional templates, and stale recovery actions", () => {
    model.current = buildModel();

    render(<ContactMeasurementSetupWorkspace projectId="P1" onBackToMatrix={() => {}} />);

    expect(screen.getByLabelText("High Power label")).toBeTruthy();
    expect(screen.getByLabelText("Include High Power contact family")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Add category" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Use High Power template" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Remove category" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Reload latest" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Discard local edits" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Re-apply saved edits" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Add category" }));
    fireEvent.click(screen.getByRole("button", { name: "Reload latest" }));
    fireEvent.click(screen.getByRole("button", { name: "Discard local edits" }));
    fireEvent.click(screen.getByRole("button", { name: "Re-apply saved edits" }));

    expect(model.current?.addFreeformFamily).toHaveBeenCalledOnce();
    expect(model.current?.reloadLatest).toHaveBeenCalledOnce();
    expect(model.current?.discardStaleLocalEdits).toHaveBeenCalledOnce();
    expect(model.current?.reapplySavedEdits).toHaveBeenCalledOnce();
  });
});

function buildModel(): Record<string, unknown> {
  const workspace = workspaceFixture();
  return {
    workspace,
    loading: false,
    busy: null,
    error: "Contact measurement plan changed. Reload before continuing.",
    message: null,
    selectedTarget: workspace.targets[0],
    dirty: true,
    staleLocalTarget: workspace.targets[0],
    selectTarget: vi.fn(),
    updateSelectedTarget: vi.fn(),
    cancelSelectedTarget: vi.fn(),
    addFreeformFamily: vi.fn(),
    removeFamily: vi.fn(),
    moveFamily: vi.fn(),
    resolveSelectedFamilyPrefix: vi.fn(),
    finalizeSelectedFamilyLabel: vi.fn(),
    openDraft: vi.fn(),
    saveSelectedTarget: vi.fn(),
    saveDraft: vi.fn(),
    confirmPlan: vi.fn(),
    refreshImpacts: vi.fn(),
    acceptCompatible: vi.fn(),
    rebindSelectedTarget: vi.fn(),
    reloadLatest: vi.fn(),
    discardStaleLocalEdits: vi.fn(),
    reapplySavedEdits: vi.fn(),
  };
}

function workspaceFixture(): ContactMeasurementPlanWorkspace {
  return {
    status: "draft",
    project_id: "P1",
    active_confirmed_revision_id: "confirmed-1",
    editable_revision_id: "draft-1",
    editable_revision_state: "draft",
    editable_revision_fingerprint: "fingerprint-1",
    revision: { revision_id: "draft-1", revision_sequence: 2, state: "draft", fingerprint: "fingerprint-1" },
    matrix_binding: {
      base_confirmed_matrix_id: "cmv-1",
      base_matrix_revision: 1,
      current_confirmed_matrix_id: "cmv-1",
      current_matrix_revision: 1,
      matrix_binding_fingerprint: "cmv-1:1",
    },
    targets: [{
      stable_target_key: "cmp-target:v1|group:cg-1|row:cr-1|step:1|suffix:",
      group_label: "Group 1",
      test_item: "LLCR",
      contact_kind: "llcr",
      step_sequence: 1,
      step_suffix_note: "",
      sample_quantity_expression: "2",
      eligible: true,
      included: true,
      exclusion_reason: null,
      is_override: false,
      coverage_state: "included",
      readings_per_sample: 4,
      target_review_state: "unchanged",
      target_review_reason: null,
      families: [{
        family_id: "hp",
        family_ordinal: 0,
        label: "High Power",
        count_per_sample: 4,
        record_label: "High Power record",
        record_prefix: "HP",
        included: true,
        is_custom: false,
      }],
    }],
    impacts: [],
    summary: { included_target_count: 1, total_target_count: 1, needs_review_count: 0, readings_by_kind: { llcr: 4 } },
    diagnostics: [],
    family_id_high_water_by_kind: { llcr: 0, cr_specified_current: 0 },
  };
}
