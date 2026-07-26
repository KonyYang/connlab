import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MatrixEditorXlsxExportButton } from "./MatrixEditorXlsxExportButton";

describe("MatrixEditorXlsxExportButton", () => {
  it("exposes lifecycle reason and dispatches no request", () => {
    const onExport = vi.fn();
    render(<MatrixEditorXlsxExportButton disabledReason="Project is closed." busy={false} onExport={onExport} />);
    const button = screen.getByRole("button", { name: "Export Matrix" });
    expect((button as HTMLButtonElement).disabled).toBe(true);
    expect(button.getAttribute("title")).toBe("Project is closed.");
    fireEvent.click(button);
    expect(onExport).not.toHaveBeenCalled();
  });
});
