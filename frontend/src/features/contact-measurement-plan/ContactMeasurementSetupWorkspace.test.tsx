import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContactMeasurementSetupWorkspace } from "./ContactMeasurementSetupWorkspace";

const model = vi.hoisted(() => ({ current: null as Record<string, unknown> | null }));

vi.mock("./useProjectPointProfileModel", () => ({
  useProjectPointProfileModel: () => model.current,
}));

describe("ContactMeasurementSetupWorkspace", () => {
  it("renders the compact confirm-only editor and cancels without draft controls", () => {
    model.current = buildModel();

    render(<ContactMeasurementSetupWorkspace projectId="P1" onBackToMatrix={() => {}} />);

    expect(screen.queryByRole("heading", { name: "Test Points Setup" })).toBeNull();
    expect(screen.getByLabelText("Point category 1")).toBeTruthy();
    expect(screen.getByLabelText("Test point IDs 1")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Add row" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Delete point profile row 1" }).getAttribute("title")).toBe("Delete row");
    expect(screen.queryByRole("button", { name: "Delete" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Save draft" })).toBeNull();
    expect(screen.queryByText("Target coverage")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Add row" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(model.current?.addCategory).toHaveBeenCalledOnce();
  });

  it("disables Add row at the 256-category limit", () => {
    model.current = buildModel(256);

    render(<ContactMeasurementSetupWorkspace projectId="P1" onBackToMatrix={() => {}} />);

    expect(screen.getByRole("button", { name: "Add row" }).hasAttribute("disabled")).toBe(true);
  });
});

function buildModel(rowCount = 1): Record<string, unknown> {
  return {
    workspace: { has_unconfirmed_draft: false, editable_revision: null },
    rows: Array.from({ length: rowCount }, (_, index) => ({
      category_id: null,
      ordinal: index,
      label: "",
      count_per_sample: 0,
      record_prefix: "",
      included: true,
    })),
    loading: false,
    busy: null,
    error: null,
    message: null,
    total: 0,
    validation: null,
    updateRow: vi.fn(),
    addCategory: vi.fn(),
    addTemplate: vi.fn(),
    removeCategory: vi.fn(),
    moveCategory: vi.fn(),
    saveDraft: vi.fn(),
    confirm: vi.fn(),
    discard: vi.fn(),
  };
}
