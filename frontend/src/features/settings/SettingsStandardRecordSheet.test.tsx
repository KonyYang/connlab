import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { SettingsExternalResourcesPanel } from "./SettingsExternalResourcesPanel";

const standardResource = {
  resource_id: "std-1",
  resource_type: "standard_record_excel" as const,
  path: "standard.xlsx",
  active: true,
  validation_status: "valid" as const,
  last_validated_at: null,
  validation_failure_reason: null,
  worksheet_name: "Methods",
};

function renderPanel(onSave = vi.fn().mockResolvedValue(undefined)) {
  render(
    <SettingsExternalResourcesPanel
      resources={[standardResource]}
      savingType={null}
      passwordStatus={null}
      savingPassword={false}
      browseEnabled={false}
      pathValidationMessages={{} as never}
      onPathChange={vi.fn()}
      onSave={onSave}
      onPasswordSave={vi.fn()}
      onBrowse={vi.fn().mockResolvedValue(null)}
    />
  );
  return onSave;
}

describe("Standard record worksheet setting", () => {
  it("omits worksheet_name when the path auto-saves", async () => {
    const onSave = renderPanel();
    expect(screen.getByText("Standard version file path")).toBeTruthy();
    const path = screen.getByLabelText("Standard version file path");
    expect(screen.queryByLabelText("Standard version file path path")).toBeNull();
    expect(path.getAttribute("title")).toBe("Standard version file path");
    await userEvent.clear(path);
    await userEvent.type(path, "updated.xlsx");
    await userEvent.tab();

    expect(onSave).toHaveBeenCalledWith("standard_record_excel", {
      path: "updated.xlsx",
      active: true,
    });
  });

  it("sends explicit null when the Standard sheet is cleared", async () => {
    const onSave = renderPanel();
    const sheet = screen.getByLabelText("Standard record sheet");
    expect((sheet as HTMLInputElement).value).toBe("Methods");
    await userEvent.clear(sheet);
    await userEvent.tab();

    expect(onSave).toHaveBeenCalledWith("standard_record_excel", {
      path: "standard.xlsx",
      active: true,
      worksheet_name: null,
    });
  });
});
