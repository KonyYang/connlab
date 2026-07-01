import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { AttachmentList } from "./AttachmentList";
import type { IntakeAttachmentViewModel } from "./intakeSelectors";

describe("AttachmentList Apply LTR busy lock", () => {
  it("disables attachment select, open, import, and duplicate actions while locked", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();
    const onOpen = vi.fn();
    const onImport = vi.fn();
    const onDuplicateAction = vi.fn();
    render(
      <AttachmentList
        attachments={[wordAttachment]}
        disabled={true}
        disabledReason="Applying LTR number. Keep this page open."
        duplicateDraft={{
          classification: "exact_existing_application_draft",
          existing_package_id: "PKG-1",
          existing_case_id: "CASE-1",
          existing_source_original_name: "Request.msg",
          incoming_source_original_name: "Request.msg",
          existing_source_size_bytes: 20,
          incoming_source_size_bytes: 20,
          allowed_actions: ["open_existing", "replace_existing"],
          incoming_application_form_name: "Application.docx",
          existing_application_form_name: "Application.docx",
        }}
        packageLoaded={true}
        onDuplicateAction={onDuplicateAction}
        onImport={onImport}
        onOpen={onOpen}
        onSelect={onSelect}
      />
    );

    const selectButton = screen.getByRole("button", { name: /Application.docx/ });
    const importButton = screen.getByRole("button", { name: "Import into editor" });
    expect((selectButton as HTMLButtonElement).disabled).toBe(true);
    expect((importButton as HTMLButtonElement).disabled).toBe(true);
    expect(importButton.getAttribute("title")).toBe("Applying LTR number. Keep this page open.");

    await user.click(selectButton);
    await user.dblClick(selectButton.closest(".attachment-row") as HTMLElement);
    await user.click(importButton);
    await user.click(screen.getByRole("button", { name: "Reinitialize" }));
    await user.click(screen.getByRole("button", { name: "Load existing" }));

    expect(onSelect).not.toHaveBeenCalled();
    expect(onOpen).not.toHaveBeenCalled();
    expect(onImport).not.toHaveBeenCalled();
    expect(onDuplicateAction).not.toHaveBeenCalled();
  });
});

const wordAttachment: IntakeAttachmentViewModel = {
  asset: {
    asset_id: "ASSET-1",
    original_name: "Application.docx",
    extension: ".docx",
    mime_type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    size_bytes: 10,
    asset_role: "candidate_application_form",
  },
  kind: "word",
  label: "Application.docx",
  roleText: "Application form",
  selected: true,
  word: true,
};
