import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { createRef } from "react";
import { describe, expect, it, vi } from "vitest";
import { IntakeSourcePanel } from "./IntakeSourcePanel";

describe("IntakeSourcePanel Apply LTR busy lock", () => {
  it("disables import controls and blocks drag-drop import while locked", async () => {
    const user = userEvent.setup();
    const onMsgFileChange = vi.fn();
    const onSelectSourceMode = vi.fn();
    render(
      <IntakeSourcePanel
        directWordName={null}
        importError={null}
        importing={false}
        interactionLocked={true}
        interactionLockedReason="Applying LTR number. Import is paused."
        msgInputRef={createRef<HTMLInputElement>()}
        packageImport={null}
        sourceMode="msg"
        wordInputRef={createRef<HTMLInputElement>()}
        onDirectWordChange={vi.fn()}
        onMsgFileChange={onMsgFileChange}
        onSelectSourceMode={onSelectSourceMode}
      />
    );

    const importButton = screen.getByRole("button", { name: /Import/ });
    expect((importButton as HTMLButtonElement).disabled).toBe(true);
    expect(importButton.getAttribute("title")).toBe("Applying LTR number. Import is paused.");

    await user.click(importButton);
    expect(onSelectSourceMode).not.toHaveBeenCalled();

    const dropZone = screen.getByText("Drop a .msg email file here").closest(".email-drop-zone");
    expect(dropZone).not.toBeNull();
    const file = new File(["message"], "request.msg", { type: "application/vnd.ms-outlook" });
    fireEvent.drop(dropZone as HTMLElement, { dataTransfer: { files: [file] } });

    expect(onSelectSourceMode).not.toHaveBeenCalled();
    expect(onMsgFileChange).not.toHaveBeenCalled();
  });
});
