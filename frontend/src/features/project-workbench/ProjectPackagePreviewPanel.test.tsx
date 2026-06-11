import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { ProjectPackagePreview } from "../../api/client";
import { ProjectPackagePreviewPanel } from "./ProjectPackagePreviewPanel";

describe("ProjectPackagePreviewPanel", () => {
  it("renders blockers and package outputs without execute actions, task copy, or future-scope items", () => {
    const { container } = render(
      <ProjectPackagePreviewPanel
        preview={blockedPreview}
        loading={false}
        error={null}
        onRefresh={vi.fn()}
      />
    );

    expect(screen.getByText("Package outputs")).toBeTruthy();
    expect(screen.getByText("Package readiness has blockers.")).toBeTruthy();
    expect(
      screen.getByText("Confirm Fee before preparing the project package.")
    ).toBeTruthy();
    expect(screen.getByText("Test Record")).toBeTruthy();
    expect(screen.getByText("Fee Form")).toBeTruthy();
    expect(screen.getByText("Ready to generate from active Confirmed Matrix.")).toBeTruthy();
    expect(screen.queryByText("Evidence placement candidates")).toBeNull();
    expect(container.textContent).not.toContain("later package execution concern");
    expect(container.textContent).not.toContain("TASK_313");
    expect(screen.queryByRole("button", { name: /execute/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /publish/i })).toBeNull();
    expect(screen.queryByRole("button", { name: /generate package/i })).toBeNull();
  });

  it("refreshes preview from the only action", async () => {
    const user = userEvent.setup();
    const onRefresh = vi.fn();
    render(
      <ProjectPackagePreviewPanel
        preview={readyPreview}
        loading={false}
        error={null}
        onRefresh={onRefresh}
      />
    );

    await user.click(screen.getByRole("button", { name: "Refresh preview" }));

    expect(onRefresh).toHaveBeenCalledTimes(1);
  });
});

const blockedPreview: ProjectPackagePreview = {
  project_id: "P1",
  status: "blocked",
  project_folder: {
    status: "ready",
    path: "C:/Projects/DL-2026-05-003",
    message: "Latest project folder is available for package targets.",
  },
  authority_context: {
    confirmed_matrix_id: "CM1",
    confirmed_revision: 1,
    confirmed_fee_id: null,
    confirmed_fee_revision: null,
    confirmed_fee_status: "missing",
  },
  required_items: [
    {
      key: "test_record",
      label: "Test Record",
      status: "ready",
      target_folder: "C:/Projects/DL-2026-05-003",
      target_path: null,
      message: "Ready to generate from active Confirmed Matrix in TASK_313.",
    },
    {
      key: "fee_form",
      label: "Fee Form",
      status: "blocked",
      target_folder: "C:/Projects/DL-2026-05-003",
      target_path: null,
      message: "Confirm Fee before Fee Form package generation.",
    },
  ],
  optional_items: [
    {
      key: "evidence_placement_candidates",
      label: "Evidence placement candidates",
      status: "deferred",
      target_folder: null,
      target_path: null,
      message: "Evidence placement remains a later package execution concern.",
    },
  ],
  blockers: ["Confirm Fee before preparing the project package."],
  warnings: [],
};

const readyPreview: ProjectPackagePreview = {
  ...blockedPreview,
  status: "ready",
  authority_context: {
    ...blockedPreview.authority_context,
    confirmed_fee_id: "CF1",
    confirmed_fee_revision: 1,
    confirmed_fee_status: "current",
  },
  required_items: blockedPreview.required_items.map((item) => ({
    ...item,
    status: "ready",
    message: `Ready: ${item.label}`,
  })),
  blockers: [],
};
