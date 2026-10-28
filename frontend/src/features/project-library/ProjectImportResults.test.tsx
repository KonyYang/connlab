import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { LibraryBatch } from "../../api/projectLibrary";
import { ProjectImportResults } from "./ProjectImportResults";

function props(batch: LibraryBatch) {
  return { batch, titlesBySource: {}, busy: false, onOpenMember: vi.fn(), onViewLibrary: vi.fn(), onRefresh: vi.fn(), onResume: vi.fn(), onReceiveMore: vi.fn() };
}
const batch: LibraryBatch = { batch_id: "batch-one", status: "completed", counts: { added: 1, already_added: 1, review: 0, failed: 0 }, items: [
  { source_path: "\\\\computer\\share\\Old Project\\", status: "added", message: "Added", member_id: "added-member" },
  { source_path: "/old/Existing Project/", status: "already_added", message: "Already in library", member_id: "existing-member" },
] };

describe("ProjectImportResults", () => {
  it("uses readable names while preserving the added and existing member navigation context", async () => {
    const callbacks = props(batch), user = userEvent.setup();
    render(<ProjectImportResults {...callbacks} titlesBySource={{ [batch.items[0].source_path]: "Renamed Project" }} />);
    await user.click(screen.getByRole("button", { name: "Open Renamed Project" }));
    expect(callbacks.onOpenMember).toHaveBeenLastCalledWith("added-member", "batch-one");
    await user.click(screen.getByRole("button", { name: "Open Existing Project" }));
    expect(callbacks.onOpenMember).toHaveBeenLastCalledWith("existing-member", undefined);
    await user.click(screen.getByRole("button", { name: "View Added Projects" }));
    expect(callbacks.onViewLibrary).toHaveBeenCalledWith("batch-one");
    expect(screen.getByText(batch.items[0].source_path).closest("details")).toHaveProperty("open", false);
    expect(screen.queryByRole("navigation", { name: "Import result pages" })).toBeNull();
  });

  it("keeps the current page on a status refresh and starts a new batch on its first page", async () => {
    const items = Array.from({ length: 25 }, (_, i) => ({ source_path: `D:/old/Project ${i + 1}`, status: "added", message: "Added", member_id: `id-${i + 1}` }));
    const callbacks = props({ ...batch, items, counts: { ...batch.counts, added: 25, already_added: 0 } });
    const { rerender } = render(<ProjectImportResults {...callbacks} />);
    await userEvent.setup().click(screen.getByRole("button", { name: "Next" }));
    expect(screen.getByRole("button", { name: "Open Project 25" })).toBeTruthy();
    rerender(<ProjectImportResults {...callbacks} batch={{ ...callbacks.batch }} />);
    expect(screen.getByText("Page 2 of 2")).toBeTruthy();
    rerender(<ProjectImportResults {...callbacks} batch={{ ...callbacks.batch, batch_id: "batch-two" }} />);
    expect(screen.getByText("Page 1 of 2")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Open Project 25" })).toBeNull();
    expect(items.map(item => item.source_path)).toEqual(Array.from({ length: 25 }, (_, i) => `D:/old/Project ${i + 1}`));
  });

  it("resumes only on request and locks result actions while the request is pending", async () => {
    const callbacks = props({ ...batch, status: "interrupted" });
    const { rerender } = render(<ProjectImportResults {...callbacks} />);
    expect(callbacks.onResume).not.toHaveBeenCalled();
    await userEvent.setup().click(screen.getByRole("button", { name: "Resume Batch" }));
    expect(callbacks.onResume).toHaveBeenCalledTimes(1);
    rerender(<ProjectImportResults {...callbacks} busy />);
    for (const button of screen.getAllByRole("button")) expect(button).toHaveProperty("disabled", true);
  });
});
