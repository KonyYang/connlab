import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { MatrixMethodVersionSyncPanel } from "./MatrixMethodVersionSyncPanel";

describe("MatrixMethodVersionSyncPanel", () => {
  it("presents safe proposals and applies only selected rows", async () => {
    const onToggle = vi.fn();
    const onApply = vi.fn();
    render(
      <MatrixMethodVersionSyncPanel
        disabled={false}
        busy={null}
        error={null}
        message={null}
        selectedRowIds={new Set(["R1"])}
        preview={{
          project_id: "P1",
          project_matrix_draft_id: "D1",
          base_confirmed_matrix_id: "CM1",
          resource_id: "STD1",
          resource_path: "standard.xlsx",
          worksheet_name: "认可标准",
          catalog_fingerprint: "catalog",
          target_fingerprint: "target",
          preview_fingerprint: "preview",
          generated_at: "now",
          rows: [
            {
              draft_row_id: "R1",
              row_order: 1,
              test_item: "Contact resistance",
              current_method: "EIA-364-04A",
              method_core: "364-04",
              matched_standard_code: "EIA-364-04B",
              catalog_revision: "B",
              catalog_year: null,
              source_row_number: 3,
              proposed_method: "EIA-364-04B",
              status: "update_available",
              reason: null,
              selectable: true,
            },
          ],
        }}
        onPreview={vi.fn()}
        onToggle={onToggle}
        onApply={onApply}
      />
    );

    expect(screen.getByText("EIA-364-04A")).toBeTruthy();
    expect(screen.getByText("EIA-364-04B")).toBeTruthy();
    await userEvent.click(screen.getByLabelText("Select Contact resistance Method update"));
    expect(onToggle).toHaveBeenCalledWith("R1", false);
    await userEvent.click(screen.getByRole("button", { name: "Apply selected" }));
    expect(onApply).toHaveBeenCalledTimes(1);
  });

  it("exposes the stacked narrow-row layout without horizontal overflow", () => {
    render(
      <MatrixMethodVersionSyncPanel
        disabled={false}
        busy={null}
        error={null}
        message={null}
        selectedRowIds={new Set(["R1"])}
        preview={{
          project_id: "P1",
          project_matrix_draft_id: "D1",
          base_confirmed_matrix_id: "CM1",
          resource_id: "STD1",
          resource_path: "standard.xlsx",
          worksheet_name: "认可标准",
          catalog_fingerprint: "catalog",
          target_fingerprint: "target",
          preview_fingerprint: "preview",
          generated_at: "now",
          rows: [
            {
              draft_row_id: "R1",
              row_order: 1,
              test_item: "Contact resistance",
              current_method: "EIA-364-04A",
              method_core: "364-04",
              matched_standard_code: "EIA-364-04B",
              catalog_revision: "B",
              catalog_year: null,
              source_row_number: 3,
              proposed_method: "EIA-364-04B",
              status: "update_available",
              reason: null,
              selectable: true,
            },
          ],
        }}
        onPreview={vi.fn()}
        onToggle={vi.fn()}
        onApply={vi.fn()}
      />
    );

    const current = screen.getByText("EIA-364-04A");
    const proposed = screen.getByText("EIA-364-04B");
    const status = screen.getByText("update available");
    const row = current.closest("tr");

    expect(row?.classList.contains("matrix-method-sync-row")).toBe(true);
    expect(current.classList.contains("matrix-method-sync-current")).toBe(true);
    expect(current.getAttribute("data-label")).toBe("Current");
    expect(proposed.classList.contains("matrix-method-sync-proposed")).toBe(true);
    expect(proposed.getAttribute("data-label")).toBe("Proposed");
    expect(status.classList.contains("matrix-method-sync-status")).toBe(true);
    expect(status.getAttribute("data-label")).toBe("Status");
    expect(row?.children[2]).toBe(current);
    expect(row?.children[3]).toBe(proposed);
  });
});
