import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { ProjectPointProfileSummary } from "../../api/client";
import { ContactMeasurementPlanSummaryCard } from "./ContactMeasurementPlanSummaryCard";

describe("ContactMeasurementPlanSummaryCard", () => {
  it("shows only confirmed Point Profile values and opens the dedicated setup workspace", async () => {
    const user = userEvent.setup();
    const onOpenSetup = vi.fn();

    render(
      <ContactMeasurementPlanSummaryCard
        summary={summary()}
        loading={false}
        onOpenSetup={onOpenSetup}
      />
    );

    expect(screen.getByText("Confirmed revision 1")).toBeTruthy();
    expect(screen.getByText("33 points / sample")).toBeTruthy();
    expect(screen.getByText("HP: 4")).toBeTruthy();
    expect(screen.queryByText(/targets/i)).toBeNull();

    await user.click(screen.getByRole("button", { name: "Setup" }));
    expect(onOpenSetup).toHaveBeenCalledOnce();
  });
});

function summary(): ProjectPointProfileSummary {
  return {
    status: "draft",
    project_id: "P1",
    confirmed_revision: {
      revision_id: "confirmed-1", revision_sequence: 1, state: "confirmed", fingerprint: "fingerprint-1",
      created_at: "2026-07-14T00:00:00Z", confirmed_at: "2026-07-14T00:00:00Z", points_per_sample: 33,
      categories: [{ category_id: "ppc-1", category_ordinal: 0, label: "High Power", count_per_sample: 4, record_prefix: "HP", included: true }],
      cr_coverage: { mode: "custom", selected_category_ids: ["ppc-1"], points_per_sample: 4 },
    },
    points_per_sample: 33, has_unconfirmed_draft: true, diagnostics: [],
  };
}
