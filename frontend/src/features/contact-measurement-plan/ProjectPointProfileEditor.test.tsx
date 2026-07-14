import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import { ProjectPointProfileEditor } from "./ProjectPointProfileEditor";
import type { ProjectPointProfileModel } from "./projectPointProfileModelTypes";

const initialRows = [
  { category_id: "ppc-1", prefix: "HP", point_expression: "1-4" },
  { category_id: "ppc-2", prefix: "LP", point_expression: "1-5" },
  { category_id: "ppc-3", prefix: "Signal", point_expression: "1-24" },
];

describe("ProjectPointProfileEditor delete activation", () => {
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
  const model = {
    workspace: null,
    rows,
    loading: false,
    busy,
    error: null,
    total: rows.length,
    validation: null,
    updateRow: vi.fn(),
    addCategory: vi.fn(),
    removeCategory: (index: number) => {
      onRemove(index);
      setRows((current) => current.filter((_, currentIndex) => currentIndex !== index));
    },
    confirm: async () => false,
  } as ProjectPointProfileModel;
  return <ProjectPointProfileEditor model={model} onCancel={() => {}} onConfirmed={() => {}} />;
}
