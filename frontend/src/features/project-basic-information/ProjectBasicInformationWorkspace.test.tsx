import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { ProjectBasicInformationResponse } from "../../api/client";
import { ProjectBasicInformationWorkspace } from "./ProjectBasicInformationWorkspace";

const api = vi.hoisted(() => ({
  getProjectBasicInformation: vi.fn(),
  saveProjectBasicInformationDraft: vi.fn(),
  confirmProjectBasicInformation: vi.fn(),
}));

vi.mock("../../api/client", () => api);

describe("ProjectBasicInformationWorkspace", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("loads draft values, auto-saves edits, and keeps DL number in confirm payload", async () => {
    const user = userEvent.setup();
    const onBackToWorkbench = vi.fn();
    api.getProjectBasicInformation.mockResolvedValue(response());
    api.saveProjectBasicInformationDraft.mockResolvedValue(
      response({ project_leader: "Even Yang" })
    );
    api.confirmProjectBasicInformation.mockResolvedValue(
      response({ project_leader: "Even Yang" }, "confirmed")
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={onBackToWorkbench}
      />
    );

    expect(await screen.findByDisplayValue("DL-2026-05-011")).toHaveProperty(
      "readOnly",
      true
    );
    expect(screen.getByDisplayValue("20 Jun 2026")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Save Draft" })).toBeNull();
    await user.clear(screen.getByLabelText("Project Leader"));
    await user.type(screen.getByLabelText("Project Leader"), "Even Yang");

    await waitFor(() =>
      expect(api.saveProjectBasicInformationDraft).toHaveBeenCalledWith("P1", {
        ...response().draft.values,
        project_leader: "Even Yang",
      })
    );

    await user.click(screen.getByRole("button", { name: "Confirm" }));

    await waitFor(() =>
      expect(api.confirmProjectBasicInformation).toHaveBeenCalledWith(
        "P1",
        {
          ...response().draft.values,
          project_leader: "Even Yang",
        },
        "Lab User"
      )
    );
    expect(onBackToWorkbench).toHaveBeenCalledWith({ refreshBasicInformation: true });
  });

  it("disables confirm while an automatic draft save is pending", async () => {
    const user = userEvent.setup();
    api.getProjectBasicInformation.mockResolvedValue(response());
    api.saveProjectBasicInformationDraft.mockReturnValue(new Promise(() => {}));

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    await screen.findByDisplayValue("DL-2026-05-011");
    await user.clear(screen.getByLabelText("Project Leader"));
    await user.type(screen.getByLabelText("Project Leader"), "Even Yang");

    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Confirm" })).toHaveProperty(
        "disabled",
        true
      )
    );
  });

  it("returns to Workbench on Cancel without saving or confirming", async () => {
    const user = userEvent.setup();
    const onBackToWorkbench = vi.fn();
    api.getProjectBasicInformation.mockResolvedValue(response());

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={onBackToWorkbench}
      />
    );

    await screen.findByText("Basic Information");
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(api.saveProjectBasicInformationDraft).not.toHaveBeenCalled();
    expect(api.confirmProjectBasicInformation).not.toHaveBeenCalled();
    expect(onBackToWorkbench).toHaveBeenCalledWith({ refreshBasicInformation: false });
  });

  it("shows missing required labels and source review hints", async () => {
    api.getProjectBasicInformation.mockResolvedValue(
      response(
        { project_leader: "" },
        "needs_review",
        ["Project Leader"],
        ["requested_by"]
      )
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    expect(await screen.findByText("Project Leader")).toBeTruthy();
    expect(screen.getByText("Needs review")).toBeTruthy();
    expect(screen.getByText("Requested by changed in source material.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Confirm" })).toHaveProperty(
      "disabled",
      false
    );
  });
});

function response(
  overrides: Record<string, string> = {},
  status: ProjectBasicInformationResponse["status"] = "unconfirmed",
  missingLabels: string[] = [],
  changedFields: string[] = []
): ProjectBasicInformationResponse {
  const values = {
    dl_number: "DL-2026-05-011",
    project_type: "NPD",
    description_pn: "PN-123",
    product_description: "Coolpower HDF",
    test_item: "Qualification Testing",
    requested_by: "MP Cao",
    project_leader: "MP Cao",
    lab_performing_tests: "Dongguan",
    date_lab_received_samples: "20 Jun 2026",
    ...overrides,
  };
  return {
    project_id: "P1",
    status,
    draft: { values },
    latest_confirmed:
      status === "confirmed"
        ? {
            record_id: "BASIC-1",
            project_id: "P1",
            status: "confirmed",
            version: 1,
            values,
            source_signature: "{}",
            created_at: "2026-06-20T09:00:00+00:00",
            updated_at: "2026-06-20T09:00:00+00:00",
            confirmed_at: "2026-06-20T09:00:00+00:00",
            confirmed_by: "Lab User",
          }
        : null,
    field_suggestions: {
      requested_by: {
        field_key: "requested_by",
        source: "application_form",
        source_value: "Changed Requester",
        needs_review: changedFields.includes("requested_by"),
      },
    },
    changed_source_fields: changedFields,
    missing_required_fields: missingLabels.map((label) => label.toLowerCase()),
    missing_required_labels: missingLabels,
    blockers: [],
    warnings: [],
  };
}
