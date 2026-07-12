import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { ContactMeasurementPlanWorkspace } from "../../api/client";
import { ContactMeasurementPlanSummaryCard } from "./ContactMeasurementPlanSummaryCard";

describe("ContactMeasurementPlanSummaryCard", () => {
  it("shows a compact review summary and opens the dedicated setup workspace", async () => {
    const user = userEvent.setup();
    const onOpenSetup = vi.fn();

    render(
      <ContactMeasurementPlanSummaryCard
        workspace={workspace()}
        loading={false}
        onOpenSetup={onOpenSetup}
        compatibilityRow={<span>Specialized record workbook</span>}
      />
    );

    expect(screen.getByText("Needs review")).toBeTruthy();
    expect(screen.getByText("2 / 3 targets")).toBeTruthy();
    expect(screen.getByText("LLCR: -")).toBeTruthy();
    expect(screen.getByText("Specialized record workbook")).toBeTruthy();

    await user.click(screen.getByRole("button", { name: "Contact measurement setup" }));
    expect(onOpenSetup).toHaveBeenCalledOnce();
  });
});

function workspace(): ContactMeasurementPlanWorkspace {
  return {
    status: "needs_review",
    project_id: "P1",
    active_confirmed_revision_id: "confirmed-1",
    editable_revision_id: "draft-2",
    editable_revision_state: "needs_review",
    editable_revision_fingerprint: "fingerprint-2",
    revision: { revision_id: "draft-2", revision_sequence: 2, state: "needs_review", fingerprint: "fingerprint-2" },
    matrix_binding: {
      base_confirmed_matrix_id: "cmv-1",
      base_matrix_revision: 1,
      current_confirmed_matrix_id: "cmv-2",
      current_matrix_revision: 2,
      matrix_binding_fingerprint: "cmv-2:2",
    },
    targets: [],
    impacts: [],
    summary: {
      included_target_count: 2,
      total_target_count: 3,
      needs_review_count: 1,
      readings_by_kind: { llcr: null, cr_specified_current: 2 },
    },
    diagnostics: [],
  };
}
