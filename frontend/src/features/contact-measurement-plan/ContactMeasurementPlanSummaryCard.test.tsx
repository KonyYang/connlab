import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { ProjectPointProfileSummary } from "../../api/client";
import { ContactMeasurementPlanSummaryCard } from "./ContactMeasurementPlanSummaryCard";

describe("ContactMeasurementPlanSummaryCard", () => {
  it("shows confirmed LLCR and custom CR facts without draft detail", () => {
    const { container } = renderCard(summary());

    expect(screen.getByRole("region", { name: "Test points" })).toBeTruthy();
    expect(screen.getByRole("heading", { name: "Test points" })).toBeTruthy();
    expect(screen.getByText("33 points / sample")).toBeTruthy();
    expect(screen.getByText("1 category · 4 points / sample")).toBeTruthy();
    expect(screen.getAllByText("Not set")).toHaveLength(2);
    expect(Array.from(container.querySelectorAll("dt"), (node) => node.textContent)).toEqual([
      "LLCR", "CR", "IR", "DWV",
    ]);
    expect(container.querySelectorAll("dl")).toHaveLength(1);
    expect(screen.queryByText(/confirmed revision/i)).toBeNull();
    expect(screen.queryByText(/targets/i)).toBeNull();
    expect(screen.queryByText("HP: 4")).toBeNull();
  });

  it("shows follow-LLCR CR coverage from the confirmed summary", () => {
    renderCard(summary({ mode: "follow_llcr", selected_category_ids: [], points_per_sample: 33 }));

    expect(screen.getByText("Same as LLCR · 33 points / sample")).toBeTruthy();
  });

  it("uses plural custom coverage and handles a missing runtime CR field", () => {
    const { rerender } = renderCard(summary({
      mode: "custom", selected_category_ids: ["ppc-1", "ppc-2"], points_per_sample: 9,
    }));
    expect(screen.getByText("2 categories · 9 points / sample")).toBeTruthy();

    const missingCrCoverage = summary();
    delete (missingCrCoverage.confirmed_revision as { cr_coverage?: CrCoverage }).cr_coverage;
    rerender(<ContactMeasurementPlanSummaryCard
      summary={missingCrCoverage} loading={false} onOpenSetup={vi.fn()}
    />);
    expect(screen.getAllByText("Not set")).toHaveLength(3);
  });

  it("uses neutral unavailable wording for null or unconfirmed summaries", () => {
    const { rerender } = renderCard(null);
    const unavailable = "Test point summary is not available.";

    expect(screen.getByText(unavailable)).toBeTruthy();
    expect(screen.queryByText(/confirm a project point profile/i)).toBeNull();
    rerender(<ContactMeasurementPlanSummaryCard
      summary={{ ...summary(), confirmed_revision: null }} loading={false} onOpenSetup={vi.fn()}
    />);
    expect(screen.getByText(unavailable)).toBeTruthy();
  });

  it("marks loading as busy and disables Setup without inventing an error state", async () => {
    const user = userEvent.setup();
    const onOpenSetup = vi.fn();
    renderCard(null, true, onOpenSetup);

    const region = screen.getByRole("region", { name: "Test points" });
    const setup = screen.getByRole("button", { name: "Setup" });
    expect(region.getAttribute("aria-busy")).toBe("true");
    expect((setup as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getByText("Test point summary is not available.")).toBeTruthy();
    expect(screen.queryByRole("alert")).toBeNull();
    await user.click(setup);
    expect(onOpenSetup).not.toHaveBeenCalled();
  });

  it("keeps Setup as a native keyboard action", async () => {
    const user = userEvent.setup();
    const onOpenSetup = vi.fn();
    renderCard(summary(), false, onOpenSetup);

    const setup = screen.getByRole("button", { name: "Setup" });
    setup.focus();
    await user.keyboard("{Enter}");
    expect(onOpenSetup).toHaveBeenCalledOnce();
  });
});

type CrCoverage = NonNullable<NonNullable<ProjectPointProfileSummary["confirmed_revision"]>["cr_coverage"]>;

function renderCard(
  value: ProjectPointProfileSummary | null,
  loading = false,
  onOpenSetup = vi.fn(),
) {
  return render(<ContactMeasurementPlanSummaryCard
    summary={value} loading={loading} onOpenSetup={onOpenSetup}
  />);
}

function summary(crCoverage: CrCoverage = {
  mode: "custom", selected_category_ids: ["ppc-1"], points_per_sample: 4,
}): ProjectPointProfileSummary {
  return {
    status: "draft",
    project_id: "P1",
    confirmed_revision: {
      revision_id: "confirmed-1", revision_sequence: 1, state: "confirmed", fingerprint: "fingerprint-1",
      created_at: "2026-07-14T00:00:00Z", confirmed_at: "2026-07-14T00:00:00Z", points_per_sample: 33,
      categories: [{ category_id: "ppc-1", category_ordinal: 0, label: "High Power", count_per_sample: 4, record_prefix: "HP", included: true }],
      cr_coverage: crCoverage,
    },
    points_per_sample: 33, has_unconfirmed_draft: true, diagnostics: [],
  };
}
