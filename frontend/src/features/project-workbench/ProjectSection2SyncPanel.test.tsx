import { afterEach, describe, expect, it, vi } from "vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import type { ProjectSection2SyncResponse } from "../../api/client";
import { ProjectSection2SyncPanel } from "./ProjectSection2SyncPanel";

describe("ProjectSection2SyncPanel", () => {
  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it("shows changed Section 2 fields from the preview", () => {
    render(
      <ProjectSection2SyncPanel
        preview={preview("ready")}
        loading={false}
        syncing={false}
        error={null}
        onRefresh={vi.fn()}
        onSync={vi.fn()}
      />
    );

    expect(screen.getByText("Section 2 dates")).toBeTruthy();
    expect(screen.getByText("Confirmed Matrix has newer Section 2 dates.")).toBeTruthy();
    expect(screen.getByText("Received date")).toBeTruthy();
    expect(screen.getByText("2026-05-01 -> 2026-06-01")).toBeTruthy();
    expect(screen.getByText("Estimated completion")).toBeTruthy();
    expect(screen.getByText("2026-05-10 -> 2026-06-08")).toBeTruthy();
  });

  it("syncs with the previewed Confirmed Matrix identity", () => {
    const onSync = vi.fn();
    render(
      <ProjectSection2SyncPanel
        preview={preview("ready")}
        loading={false}
        syncing={false}
        error={null}
        onRefresh={vi.fn()}
        onSync={onSync}
      />
    );

    fireEvent.click(screen.getByRole("button", { name: "Sync Section 2 dates" }));

    expect(onSync).toHaveBeenCalledWith({
      expected_confirmed_matrix_id: "CM1",
      expected_confirmed_revision: 3
    });
  });

  it("shows blocker copy and disables sync when no active Confirmed Matrix exists", () => {
    render(
      <ProjectSection2SyncPanel
        preview={null}
        loading={false}
        syncing={false}
        error="Confirm Matrix authority before syncing Section 2 dates."
        onRefresh={vi.fn()}
        onSync={vi.fn()}
      />
    );

    expect(screen.getByText("Confirm Matrix authority before syncing Section 2 dates.")).toBeTruthy();
    expect(
      (screen.getByRole("button", { name: "Sync Section 2 dates" }) as HTMLButtonElement).disabled
    ).toBe(true);
  });
});

function preview(status: ProjectSection2SyncResponse["status"]): ProjectSection2SyncResponse {
  return {
    project_id: "P1",
    application_form_id: "FORM1",
    confirmed_matrix_id: "CM1",
    confirmed_revision: 3,
    status,
    fields: [
      {
        field_key: "received_date",
        source_field_key: "sample_received_date",
        source_value: "2026-06-01",
        current_value: "2026-05-01",
        next_value: "2026-06-01",
        status: "will_change",
        message: "Section 2 will be updated from Confirmed Matrix."
      },
      {
        field_key: "estimated_completion_date",
        source_field_key: "estimated_completion_date",
        source_value: "2026-06-08",
        current_value: "2026-05-10",
        next_value: "2026-06-08",
        status: "will_change",
        message: "Section 2 will be updated from Confirmed Matrix."
      }
    ]
  };
}
