import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import { ProjectPointProfileEditor } from "./ProjectPointProfileEditor";
import type { ProjectPointProfileModel } from "./projectPointProfileModelTypes";

const initialRows = [
  { category_id: "ppc-1", prefix: "HP", point_expression: "1-4", cr_selected: true },
  { category_id: "ppc-2", prefix: "LP", point_expression: "1-5", cr_selected: false },
  { category_id: "ppc-3", prefix: "Signal", point_expression: "1-24", cr_selected: true },
];

describe("ProjectPointProfileEditor delete activation", () => {
  it("uses the shared inline editor and icon-button vocabulary", () => {
    render(<EditorHarness onRemove={vi.fn()} />);

    expect(screen.getByRole("heading", { name: "LLCR" })).toBeTruthy();
    expect(screen.queryByRole("heading", { name: "LLCR Test Point Confirmation" })).toBeNull();
    expect(screen.getByLabelText("Point category 1").classList.contains("project-point-profile-input")).toBe(true);
    expect(screen.getByLabelText("Test point IDs 1").classList.contains("project-point-profile-input")).toBe(true);

    const deleteButton = screen.getByRole("button", { name: "Delete point profile row HP" });
    expect(deleteButton.classList.contains("project-point-profile-delete")).toBe(true);
    expect(deleteButton.querySelector("svg")).not.toBeNull();
    expect(deleteButton.textContent).not.toContain("🗑");
  });

  it("explains that point expressions identify numbers rather than a quantity", () => {
    render(<EditorHarness onRemove={vi.fn()} />);

    expect(screen.getByRole("columnheader", { name: "Test point IDs" })).toBeTruthy();
    expect(screen.queryByText("Enter point numbers or ranges, for example 1-5. Entering 5 means point 5 only.")).toBeNull();
    expect(screen.getByLabelText("Test point IDs 1").getAttribute("placeholder")).toBe("Example: 1,24,2 or HP1-5,PE");
    expect(screen.getByLabelText("Test point IDs 1").hasAttribute("aria-describedby")).toBe(false);
  });

  it.each([
    ["{Enter}", "Delete point profile row Signal", 2],
    [" ", "Delete point profile row Signal", 2],
  ])("removes exactly the focused row once for keyboard %s", async (key, label, index) => {
    const user = userEvent.setup();
    const onRemove = vi.fn();
    render(<EditorHarness onRemove={onRemove} />);

    const button = screen.getByRole("button", { name: label });
    button.focus();
    await user.keyboard(key);

    expect(onRemove).toHaveBeenCalledTimes(1);
    expect(onRemove).toHaveBeenCalledWith(index);
    expect(screen.queryByRole("button", { name: label })).toBeNull();
    expect(screen.getByRole("button", { name: "Delete point profile row HP" })).toBeTruthy();
  });

  it("removes exactly the clicked row and leaves adjacent rows intact", async () => {
    const user = userEvent.setup();
    const onRemove = vi.fn();
    render(<EditorHarness onRemove={onRemove} />);

    await user.click(screen.getByRole("button", { name: "Delete point profile row LP" }));

    expect(onRemove).toHaveBeenCalledTimes(1);
    expect(onRemove).toHaveBeenCalledWith(1);
    expect(screen.queryByRole("button", { name: "Delete point profile row LP" })).toBeNull();
    expect(screen.getByRole("button", { name: "Delete point profile row HP" })).toBeTruthy();
    expect(screen.getByRole("button", { name: "Delete point profile row Signal" })).toBeTruthy();
  });

  it("does not remove from disabled or empty editor states", async () => {
    const user = userEvent.setup();
    const disabledRemove = vi.fn();
    const { unmount } = render(<EditorHarness busy onRemove={disabledRemove} />);

    await user.click(screen.getByRole("button", { name: "Delete point profile row Signal" }));
    expect(disabledRemove).not.toHaveBeenCalled();

    unmount();
    render(<EditorHarness rows={[]} onRemove={vi.fn()} />);
    expect(screen.queryByRole("button", { name: /Delete point profile row/ })).toBeNull();
  });

  it("shows one row-level CR column without a separate coverage section", async () => {
    const user = userEvent.setup();
    render(<EditorHarness onRemove={vi.fn()} />);

    expect(screen.getByRole("columnheader", { name: "Point category" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "Test point IDs" })).toBeTruthy();
    expect(screen.getByRole("columnheader", { name: "CR" })).toBeTruthy();
    expect(screen.queryByRole("columnheader", { name: "LLCR" })).toBeNull();
    expect((screen.getByRole("checkbox", { name: "Include HP in CR" }) as HTMLInputElement).checked).toBe(true);
    expect((screen.getByRole("checkbox", { name: "Include LP in CR" }) as HTMLInputElement).checked).toBe(false);
    expect((screen.getByRole("checkbox", { name: "Include Signal in CR" }) as HTMLInputElement).checked).toBe(true);
    expect(screen.getAllByRole("checkbox")).toHaveLength(4);
    expect(screen.queryByRole("heading", { name: "CR coverage" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Customize CR" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Use same as LLCR" })).toBeNull();

    await user.click(screen.getByRole("checkbox", { name: "Include Signal in CR" }));
    expect((screen.getByRole("checkbox", { name: "Include Signal in CR" }) as HTMLInputElement).checked).toBe(false);
  });

  it("shows one global LLCR Delta R option enabled by default", async () => {
    const user = userEvent.setup();
    render(<EditorHarness onRemove={vi.fn()} />);

    const option = screen.getByRole("checkbox", { name: "Delta R for LLCR" }) as HTMLInputElement;
    expect(option.checked).toBe(true);
    await user.click(option);
    expect(option.checked).toBe(false);
  });
});

function EditorHarness({
  busy = false,
  rows: initial = initialRows,
  onRemove,
}: {
  busy?: boolean;
  rows?: typeof initialRows;
  onRemove: (index: number) => void;
}) {
  const [rows, setRows] = useState(initial);
  const [deltaREnabled, setDeltaREnabled] = useState(true);
  const crCoverageMode = rows.every((row) => row.cr_selected) ? "follow_llcr" : "custom";
  const model = {
    workspace: null,
    rows,
    loading: false,
    busy,
    error: null,
    total: rows.length,
    crTotal: rows.filter((row) => row.cr_selected).length,
    crSelectedCount: rows.filter((row) => row.cr_selected).length,
    crCoverageMode,
    validation: null,
    deltaREnabled,
    setDeltaREnabled,
    updateRow: vi.fn(),
    addCategory: vi.fn(),
    setCrSelected: (index: number, selected: boolean) => setRows((current) => current.map(
      (row, currentIndex) => currentIndex === index ? { ...row, cr_selected: selected } : row,
    )),
    removeCategory: (index: number) => {
      onRemove(index);
      setRows((current) => current.filter((_, currentIndex) => currentIndex !== index));
    },
    confirm: async () => false,
  } as ProjectPointProfileModel;
  return <ProjectPointProfileEditor model={model} onCancel={() => {}} onConfirmed={() => {}} />;
}
