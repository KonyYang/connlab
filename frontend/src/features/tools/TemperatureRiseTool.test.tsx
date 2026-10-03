import { act, fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { analyzeTemperatureRise, exportTemperatureRise, previewTemperatureRise, suggestTemperatureRise, type TemperatureBlock } from "../../api/client";
import { TemperatureRiseTool } from "./TemperatureRiseTool";

vi.mock("../../api/client", () => ({ analyzeTemperatureRise: vi.fn(), exportTemperatureRise: vi.fn(), previewTemperatureRise: vi.fn(), suggestTemperatureRise: vi.fn() }));
const block: TemperatureBlock = { id: "0", sheet: "Data", header_row: 31, row_count: 3,
  headers: ["Scan", "Time", "1_HS", "2_C", "Ambient", "Current (VDC)"],
  records: [32, 33, 34].map((row) => ({ row, values: [row - 31, "12:00", 24, 23, 20, 10 * (row - 31)] })),
  suggested_mapping: { ambient: 4, current: 5, channels: [{ column: 2, sample: "1", point: "HS" }, { column: 3, sample: "2", point: "C" }] },
  current_metadata: [320, "Current", true, 6666.67], candidate_rows: [32, 33, 34] };

beforeEach(() => {
  vi.clearAllMocks();
  vi.mocked(previewTemperatureRise).mockResolvedValue({ blocks: [block] });
  vi.mocked(suggestTemperatureRise).mockResolvedValue({ candidate_rows: [33, 34] });
  vi.mocked(analyzeTemperatureRise).mockResolvedValue({ points: [{ row: 33, current: 20, maximum: 6, average_of_max: 5, single_max: { "1": 6, "2": 4 } }],
    candidate_rows: [32, 33, 34], max_curve: { a: .01, b: .1, c: 0, r_squared: .999 }, avg_curve: { a: .01, b: .09, c: 0, r_squared: .999 },
    target_current: 66.545852, derating: [{ ambient: 20, allowable_rise: 105, basic_current: 100, derated_current: 80 }], extrapolated: true });
  vi.mocked(exportTemperatureRise).mockResolvedValue({ blob: new Blob(["xlsx"]), fileName: "new.xlsx" });
  vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => undefined);
  vi.stubGlobal("URL", { createObjectURL: vi.fn(() => "blob:temperature"), revokeObjectURL: vi.fn() });
});

async function preview() {
  const user = userEvent.setup();
  await user.upload(screen.getByLabelText("Measurement file"), new File(["csv"], "data.csv", { type: "text/csv" }));
  await user.click(screen.getByRole("button", { name: "Preview Measurement Data" }));
  await screen.findByText(/3 confirmed rows/);
  return user;
}

it("allows channel mapping and point exclusion before calculation and downloads a new workbook", async () => {
  render(<TemperatureRiseTool />);
  const user = await preview();
  await user.click(screen.getByLabelText("Use row 32"));
  await user.clear(screen.getByLabelText("Sample for 2_C"));
  await user.type(screen.getByLabelText("Sample for 2_C"), "Other");
  await user.click(screen.getByRole("button", { name: "Calculate Preview" }));
  await screen.findByText("66.5 A");
  expect(vi.mocked(analyzeTemperatureRise).mock.calls[0][1]).toMatchObject({ selected_rows: [33, 34], current_mode: "amperes", zero_intercept: true, derating_factor: .8 });
  expect(vi.mocked(analyzeTemperatureRise).mock.calls[0][1].mapping.channels[1].sample).toBe("Other");
  await user.click(screen.getByRole("button", { name: "Download Temperature Rise Workbook" }));
  expect((await screen.findByRole("status")).textContent).toBe("new.xlsx");
  expect(URL.revokeObjectURL).toHaveBeenCalledWith("blob:temperature");
  await user.click(screen.getByLabelText("Force zero intercept"));
  expect(screen.queryByRole("button", { name: "Download Temperature Rise Workbook" })).toBeNull();
});

it("refreshes point suggestions after changing the current column and reports calculation errors", async () => {
  render(<TemperatureRiseTool />);
  const user = await preview();
  fireEvent.change(screen.getByLabelText("Current channel"), { target: { value: "2" } });
  await user.click(screen.getByRole("button", { name: "Refresh Stage Suggestions" }));
  expect(suggestTemperatureRise).toHaveBeenCalledWith(expect.any(File), "0", 2);
  vi.mocked(analyzeTemperatureRise).mockRejectedValueOnce(new Error("Fit requires distinct current levels."));
  await user.click(screen.getByRole("button", { name: "Calculate Preview" }));
  expect((await screen.findByRole("alert")).textContent).toContain("distinct current levels");
  expect(exportTemperatureRise).not.toHaveBeenCalled();
});

it("suppresses a late export after leaving Tools", async () => {
  const { unmount } = render(<TemperatureRiseTool />);
  const user = await preview();
  await user.click(screen.getByRole("button", { name: "Calculate Preview" }));
  await screen.findByText("66.5 A");
  let finish!: (value: { blob: Blob; fileName: string }) => void;
  vi.mocked(exportTemperatureRise).mockReturnValueOnce(new Promise((resolve) => { finish = resolve; }));
  await user.click(screen.getByRole("button", { name: "Download Temperature Rise Workbook" }));
  unmount();
  await act(async () => finish({ blob: new Blob(["late"]), fileName: "late.xlsx" }));
  expect(URL.createObjectURL).not.toHaveBeenCalled();
});

it("resets current conversion when selecting a new file and reads scan/time by actual headers", async () => {
  render(<TemperatureRiseTool />);
  const user = await preview();
  await user.selectOptions(screen.getByLabelText("Current values"), "voltage");
  fireEvent.change(screen.getByLabelText("Voltage-to-current gain"), { target: { value: "6666.67" } });
  const reordered: TemperatureBlock = { ...block, headers: ["Current", "Ambient", "1_HS", "Scan", "Time"],
    records: [{ row: 32, values: [10, 20, 22, 7, "2026-08-19 12:00"] }],
    candidate_rows: [32], suggested_mapping: { ambient: 1, current: 0, channels: [{ column: 2, sample: "1", point: "HS" }] } };
  vi.mocked(previewTemperatureRise).mockResolvedValueOnce({ blocks: [reordered] });
  await user.upload(screen.getByLabelText("Measurement file"), new File(["new"], "other.csv", { type: "text/csv" }));
  await user.click(screen.getByRole("button", { name: "Preview Measurement Data" }));
  await screen.findByText("7 · 2026-08-19 12:00");
  expect((screen.getByLabelText("Current values") as HTMLSelectElement).value).toBe("amperes");
  expect((screen.getByLabelText("Voltage-to-current gain") as HTMLInputElement).value).toBe("1");
});

it("does not silently add zero-temperature rows for trailing ambient separators", async () => {
  render(<TemperatureRiseTool />);
  const user = await preview();
  fireEvent.change(screen.getByLabelText("Ambient temperatures (°C, comma separated)"), { target: { value: "20, 125,;" } });
  await user.click(screen.getByRole("button", { name: "Calculate Preview" }));
  await screen.findByText("66.5 A");
  expect(vi.mocked(analyzeTemperatureRise).mock.calls[0][1].ambient_temperatures).toEqual([20, 125]);
});
