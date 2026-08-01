import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it, vi } from "vitest";
import { MatrixImportStandardVersionChoiceDialog } from "./MatrixImportStandardVersionChoiceDialog";

function Harness({ onClose = vi.fn() }: { onClose?: () => void }) {
  const [open, setOpen] = useState(false);
  return (
    <>
      <button type="button" onClick={() => setOpen(true)}>Return target</button>
      <MatrixImportStandardVersionChoiceDialog
        open={open}
        busy={false}
        error={null}
        onChooseFile={vi.fn()}
        onSkip={vi.fn()}
        onClose={() => {
          onClose();
          setOpen(false);
        }}
      />
    </>
  );
}

describe("MatrixImportStandardVersionChoiceDialog", () => {
  it("renders the locked accessible copy and focuses the primary action", async () => {
    render(<Harness />);
    await userEvent.click(screen.getByRole("button", { name: "Return target" }));

    const dialog = screen.getByRole("dialog", {
      name: "Standard version file unavailable",
    });
    expect(dialog.getAttribute("aria-modal")).toBe("true");
    expect(
      screen.getByText(
        "Choose a Standard version file, or skip for now and keep the original Method values."
      )
    ).toBeTruthy();
    const choose = screen.getByRole("button", { name: "Choose file" });
    expect(screen.getByRole("button", { name: "Skip for now" })).toBeTruthy();
    expect(document.activeElement).toBe(choose);
  });

  it("closes on Escape and returns focus to the invoking control", async () => {
    const onClose = vi.fn();
    render(<Harness onClose={onClose} />);
    const returnTarget = screen.getByRole("button", { name: "Return target" });
    await userEvent.click(returnTarget);

    await userEvent.keyboard("{Escape}");

    expect(onClose).toHaveBeenCalledTimes(1);
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(document.activeElement).toBe(returnTarget);
  });

  it("keeps actionable validation feedback inside the dialog", () => {
    render(
      <MatrixImportStandardVersionChoiceDialog
        open
        busy={false}
        error="The selected Standard version file could not be validated."
        onChooseFile={vi.fn()}
        onSkip={vi.fn()}
        onClose={vi.fn()}
      />
    );

    expect(screen.getByRole("status").textContent).toContain("could not be validated");
  });
});
