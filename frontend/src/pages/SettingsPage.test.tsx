import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { downloadSupportDiagnosticBundle, listExternalResources, validateExternalResource, saveExternalResource, type ExternalResource } from "../api/client";
import { SettingsPage } from "./SettingsPage";

vi.mock("../api/client", async (importOriginal) => ({
  ...(await importOriginal<typeof import("../api/client")>()),
  listExternalResources: vi.fn(),
  validateExternalResource: vi.fn(),
  saveExternalResource: vi.fn(),
  downloadSupportDiagnosticBundle: vi.fn()
}));

describe("SettingsPage", () => {
  beforeEach(() => {
    vi.mocked(validateExternalResource).mockReset();
    vi.mocked(saveExternalResource).mockReset();
    vi.mocked(listExternalResources).mockReset();
    vi.mocked(listExternalResources).mockResolvedValue([]);
    vi.mocked(downloadSupportDiagnosticBundle).mockResolvedValue({
      blob: new Blob(["diagnostics"]),
      fileName: "ConnLab_Diagnostics_20260825.zip"
    });
  });

  it("loads only non-secret external resource settings", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        configured: false,
        overridden_by_environment: false,
        password: null
      })
    } as Response);

    render(<SettingsPage />);

    expect(await screen.findByText("Editable file locations")).toBeTruthy();
    await waitFor(() => expect(listExternalResources).toHaveBeenCalledTimes(1));
    expect(fetchMock).not.toHaveBeenCalled();
    expect(screen.queryByLabelText("LTR workbook password")).toBeNull();
    fetchMock.mockRestore();
  });

  it("downloads a privacy-bounded diagnostic package from support settings", async () => {
    const createObjectURL = vi.fn(() => "blob:diagnostics");
    const revokeObjectURL = vi.fn();
    const clickDownload = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => undefined);
    Object.defineProperty(window.URL, "createObjectURL", { configurable: true, value: createObjectURL });
    Object.defineProperty(window.URL, "revokeObjectURL", { configurable: true, value: revokeObjectURL });

    render(<SettingsPage />);
    fireEvent.click(await screen.findByRole("button", { name: "Export diagnostic package" }));

    await waitFor(() => expect(downloadSupportDiagnosticBundle).toHaveBeenCalledTimes(1));
    expect(await screen.findByText("Diagnostic package downloaded.")).toBeTruthy();
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:diagnostics");
    expect(clickDownload).toHaveBeenCalledTimes(1);
    clickDownload.mockRestore();
  });

  it("does not repeat a missing file path in the validation message", async () => {
    vi.mocked(listExternalResources).mockResolvedValue([
      {
        resource_id: "standard-version",
        resource_type: "standard_record_excel",
        path: "D:\\Source\\Foreign file directory.xls",
        active: true,
        validation_status: "invalid",
        last_validated_at: null,
        validation_failure_reason:
          "Expected an existing file: D:\\Source\\Foreign file directory.xls",
        worksheet_name: "认可标准"
      }
    ]);

    render(<SettingsPage />);

    vi.mocked(validateExternalResource).mockImplementation(async () => (await listExternalResources())[0]);
    const input = await screen.findByLabelText("Standard version file path");
    expect(input.getAttribute("title")).toBe("File does not exist.");
    expect(input.getAttribute("title")).not.toContain("D:\\Source");
  });
});


function locationResource(overrides: Partial<ExternalResource> = {}): ExternalResource {
  return {resource_id: "temp", resource_type: "temporary_materials_root", path: "D:/Materials",
    active: true, validation_status: "invalid", last_validated_at: null,
    validation_failure_reason: "Expected an existing directory: D:/Materials", worksheet_name: null, ...overrides};
}

describe("Automatic location validation", () => {
  beforeEach(() => {vi.mocked(listExternalResources).mockReset(); vi.mocked(validateExternalResource).mockReset(); vi.mocked(saveExternalResource).mockReset();});

it("rechecks saved locations on entry without saving paths or requiring Enter", async () => {
  const resource = locationResource();
  vi.mocked(listExternalResources).mockResolvedValue([resource]);
  vi.mocked(validateExternalResource).mockResolvedValue({...resource, validation_status: "valid", validation_failure_reason: null});
  render(<SettingsPage />);
  const input = await screen.findByLabelText("Temporary materials folder path");
  await waitFor(() => expect(input.getAttribute("aria-invalid")).toBe("false"));
  expect(validateExternalResource).toHaveBeenCalledWith("temporary_materials_root");
  expect(saveExternalResource).not.toHaveBeenCalled();
});

it("refreshes validation when returning to the window and coalesces repeated focus", async () => {
  const resource = locationResource();
  vi.mocked(listExternalResources).mockResolvedValue([resource]);
  vi.mocked(validateExternalResource).mockResolvedValue(resource);
  render(<SettingsPage />);
  const input = await screen.findByLabelText("Temporary materials folder path");
  await waitFor(() => expect(validateExternalResource).toHaveBeenCalledTimes(1));
  expect(input.getAttribute("aria-invalid")).toBe("true");
  vi.mocked(validateExternalResource).mockResolvedValue({...resource, validation_status: "valid", validation_failure_reason: null});
  fireEvent.focus(window); fireEvent.focus(window); fireEvent.focus(window);
  await waitFor(() => expect(input.getAttribute("aria-invalid")).toBe("false"));
  expect(validateExternalResource).toHaveBeenCalledTimes(2);
});

it("keeps unrelated unsaved edits while a slow background check completes", async () => {
  const resource = locationResource();
  const standard = locationResource({resource_id:"std", resource_type:"standard_record_excel", path:"D:/standard.xlsx", worksheet_name:"Methods"});
  let finish!: (value: ExternalResource) => void;
  vi.mocked(listExternalResources).mockResolvedValue([resource, standard]);
  vi.mocked(validateExternalResource).mockReturnValue(new Promise(resolve => {finish=resolve;}));
  render(<SettingsPage />);
  const input = await screen.findByLabelText("Standard version file path");
  await waitFor(() => expect(validateExternalResource).toHaveBeenCalledTimes(1));
  fireEvent.change(input, {target:{value:"D:/edited.xlsx"}});
  finish({...resource, validation_status:"valid", validation_failure_reason:null});
  await waitFor(() => expect(screen.getByLabelText("Temporary materials folder path").getAttribute("aria-invalid")).toBe("false"));
  expect((input as HTMLInputElement).value).toBe("D:/edited.xlsx");
  expect(input.getAttribute("aria-invalid")).toBe("false");
  expect(validateExternalResource).toHaveBeenCalledTimes(1);
});

it("serializes full validation and continues after one resource fails", async () => {
  const resource = locationResource();
  const standard = locationResource({resource_id:"std", resource_type:"standard_record_excel", path:"D:/standard.xlsx"});
  const output = locationResource({resource_id:"output", resource_type:"project_output_root", path:"D:/projects"});
  const template = locationResource({resource_id:"ir", resource_type:"ir_dwv_record_template", path:"D:/IR.xlsx"});
  let finish!: (value: ExternalResource) => void;
  vi.mocked(listExternalResources).mockResolvedValue([resource, standard, output, template]);
  vi.mocked(validateExternalResource).mockReturnValueOnce(new Promise(resolve => {finish=resolve;}))
    .mockResolvedValueOnce({...output, validation_status:"valid", validation_failure_reason:null})
    .mockRejectedValueOnce(new Error("Workbook could not be checked"))
    .mockResolvedValueOnce({...template, validation_status:"valid", validation_failure_reason:null});
  render(<SettingsPage />);
  await screen.findByLabelText("Temporary materials folder path");
  await waitFor(() => expect(validateExternalResource).toHaveBeenCalledTimes(1));
  finish({...resource, validation_status:"valid", validation_failure_reason:null});
  await waitFor(() => expect(validateExternalResource).toHaveBeenCalledTimes(4));
  expect(screen.getByLabelText("Standard version file path").getAttribute("title")).toBe("Workbook could not be checked");
  await waitFor(() => expect(screen.getByLabelText("IR/DWV record template path").getAttribute("aria-invalid")).toBe("false"));
});

it("does not apply an old validation result to a newly edited and saved path", async () => {
  const resource = locationResource();
  const changed = {...resource, path:"D:/NewMaterials", validation_status:"valid" as const, validation_failure_reason:null};
  let finish!: (value: ExternalResource) => void;
  vi.mocked(listExternalResources).mockResolvedValue([resource]);
  vi.mocked(validateExternalResource).mockReturnValueOnce(new Promise(resolve => {finish=resolve;})).mockResolvedValue(changed);
  vi.mocked(saveExternalResource).mockResolvedValue(changed);
  render(<SettingsPage />);
  const input = await screen.findByLabelText("Temporary materials folder path");
  await waitFor(() => expect(validateExternalResource).toHaveBeenCalledTimes(1));
  fireEvent.change(input, {target:{value:changed.path}});
  fireEvent.blur(input);
  finish(resource);
  await waitFor(() => expect(saveExternalResource).toHaveBeenCalled());
  await waitFor(() => expect(input.getAttribute("aria-invalid")).toBe("false"));
  expect((input as HTMLInputElement).value).toBe(changed.path);
});



it("stops queued background validation after leaving Settings", async () => {
  const resource = locationResource();
  const output = locationResource({resource_id:"output", resource_type:"project_output_root", path:"D:/projects"});
  let finish!: (value: ExternalResource) => void;
  vi.mocked(listExternalResources).mockResolvedValue([resource, output]);
  vi.mocked(validateExternalResource).mockReturnValue(new Promise(resolve => {finish=resolve;}));
  const view = render(<SettingsPage />);
  await screen.findByLabelText("Temporary materials folder path");
  await waitFor(() => expect(validateExternalResource).toHaveBeenCalledTimes(1));
  view.unmount();
  finish(resource);
  await new Promise(resolve => setTimeout(resolve, 0));
  expect(validateExternalResource).toHaveBeenCalledTimes(1);
});
});
