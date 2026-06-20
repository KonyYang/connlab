import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import type { ProjectBasicInformationResponse } from "../../api/client";
import { ProjectBasicInformationSummaryCard } from "./ProjectBasicInformationSummaryCard";

describe("ProjectBasicInformationSummaryCard", () => {
  it("shows unconfirmed state without an inline edit action", () => {
    render(
      <ProjectBasicInformationSummaryCard
        basicInformation={response("unconfirmed", null, ["Project Leader"])}
        loading={false}
        error={null}
      />
    );

    expect(screen.getByText("Project Basic Information")).toBeTruthy();
    expect(screen.getByText("Unconfirmed")).toBeTruthy();
    expect(screen.getByText("Confirm from Basic Information")).toBeTruthy();
    expect(screen.getByText("Project Leader")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Edit" })).toBeNull();
  });

  it("renders compact confirmed summary without duplicate project identity fields", async () => {
    const user = userEvent.setup();
    render(
      <ProjectBasicInformationSummaryCard
        basicInformation={response("confirmed", confirmedRecord())}
        loading={false}
        error={null}
      />
    );

    expect(screen.getByText("Confirmed")).toBeTruthy();
    expect(screen.getByText("Project Type")).toBeTruthy();
    expect(screen.getByText("NPD")).toBeTruthy();
    expect(screen.queryByText("DL/LTR Number")).toBeNull();
    expect(screen.queryByText("Product Description")).toBeNull();
    expect(screen.queryByText("Test Item")).toBeNull();

    await user.click(screen.getByRole("button", { name: "View" }));

    expect(screen.getByText("All confirmed fields")).toBeTruthy();
    expect(screen.getByText("DL-2026-05-011")).toBeTruthy();
    expect(screen.getByText("Coolpower HDF")).toBeTruthy();
    expect(screen.getByText("Qualification Testing")).toBeTruthy();
  });

  it("shows needs-review state and changed field count", () => {
    render(
      <ProjectBasicInformationSummaryCard
        basicInformation={response("needs_review", confirmedRecord(), [], ["requested_by"])}
        loading={false}
        error={null}
      />
    );

    expect(screen.getByText("Needs review")).toBeTruthy();
    expect(screen.getByText("1 source field changed")).toBeTruthy();
    expect(screen.getByText("Confirm from Basic Information")).toBeTruthy();
  });
});

function response(
  status: ProjectBasicInformationResponse["status"],
  latestConfirmed: ProjectBasicInformationResponse["latest_confirmed"],
  missingLabels: string[] = [],
  changedFields: string[] = []
): ProjectBasicInformationResponse {
  const values = confirmedRecord().values;
  return {
    project_id: "P1",
    status,
    draft: { values },
    latest_confirmed: latestConfirmed,
    field_suggestions: {},
    changed_source_fields: changedFields,
    missing_required_fields: missingLabels.map((label) => label.toLowerCase()),
    missing_required_labels: missingLabels,
    blockers: [],
    warnings: [],
  };
}

function confirmedRecord(): NonNullable<ProjectBasicInformationResponse["latest_confirmed"]> {
  return {
    record_id: "BASIC-1",
    project_id: "P1",
    status: "confirmed",
    version: 1,
    values: {
      dl_number: "DL-2026-05-011",
      project_type: "NPD",
      product_description: "Coolpower HDF",
      test_item: "Qualification Testing",
      requested_by: "MP Cao",
      project_leader: "Even Yang",
      lab_performing_tests: "Dongguan",
      test_result: "In progress",
      sub_contract: "Yes",
      test_fee: "1630.00",
    },
    source_signature: "{}",
    created_at: "2026-06-20T09:00:00+00:00",
    updated_at: "2026-06-20T09:00:00+00:00",
    confirmed_at: "2026-06-20T09:00:00+00:00",
    confirmed_by: "Lab User",
  };
}
