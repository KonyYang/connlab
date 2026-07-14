import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ContactMeasurementSetupWorkspace } from "./ContactMeasurementSetupWorkspace";

const model = vi.hoisted(() => ({ current: null as Record<string, unknown> | null }));

vi.mock("./useProjectPointProfileModel", () => ({
  useProjectPointProfileModel: () => model.current,
}));

describe("ContactMeasurementSetupWorkspace", () => {
  it("renders the Profile-first editor with a blank category and optional templates", () => {
    model.current = buildModel();

    render(<ContactMeasurementSetupWorkspace projectId="P1" onBackToMatrix={() => {}} />);

    expect(screen.getByRole("heading", { name: "Contact measurement setup" })).toBeTruthy();
    expect(screen.getByLabelText("Category")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Add category" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "High Power template" })).toBeTruthy();
    expect(screen.queryByText("Target coverage")).toBeNull();

    fireEvent.click(screen.getByRole("button", { name: "Add category" }));
    fireEvent.click(screen.getByRole("button", { name: "High Power template" }));
    fireEvent.click(screen.getByRole("button", { name: "Save draft" }));

    expect(model.current?.addCategory).toHaveBeenCalledOnce();
    expect(model.current?.addTemplate).toHaveBeenCalledWith("high_power");
    expect(model.current?.saveDraft).toHaveBeenCalledOnce();
  });
});

function buildModel(): Record<string, unknown> {
  return {
    workspace: { has_unconfirmed_draft: false, editable_revision: null },
    rows: [{
      category_id: null,
      ordinal: 0,
      label: "",
      count_per_sample: 0,
      record_prefix: "",
      included: true,
    }],
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
