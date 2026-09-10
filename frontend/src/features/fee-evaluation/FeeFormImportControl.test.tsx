import { fireEvent, render, screen, waitFor, cleanup } from "@testing-library/react";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { FeeFormImportControl } from "./FeeFormImportControl";
import type { FeeEvaluationPreviewRow } from "./feeEvaluationPreviewModel";
const inspect = vi.hoisted(() => vi.fn());
vi.mock("../../api/client", () => ({inspectFeeForm: inspect}));
beforeEach(() => {
  HTMLDialogElement.prototype.showModal = function () { this.setAttribute("open", ""); };
  HTMLDialogElement.prototype.close = function () { this.removeAttribute("open"); };
});
afterEach(() => { cleanup(); vi.clearAllMocks(); });
const rows = [{lineId: "r1", description: "LLCR", groupLabel: "Aa", rowKind: "matrix_step",
  unitPrice: "1", units: "99", unitType: "per reading", baseFee: "0"}] as FeeEvaluationPreviewRow[];
const values = {unitPrice: "10", unitType: "per sample", baseFee: "0", spendTime: "1", units: "5", discount: "0", notes: "source"};

it("previews imported prices and only applies explicitly without changing current quantities", async () => {
  inspect.mockResolvedValue({rows: [{group: "Bb", description: "LLCR", rowKind: "matrix_step", values}]});
  const apply = vi.fn();
  render(<FeeFormImportControl projectId="p" rows={rows} disabled={false} onApply={apply} />);
  fireEvent.click(screen.getByRole("button", {name: "Import Fee Form"}));
  fireEvent.change(screen.getByLabelText("Import mode"), {target: {value: "prices"}});
  fireEvent.change(screen.getByLabelText("Fee Form file"), {target: {files: [new File(["xls"], "fee.xls")]}});
  fireEvent.click(screen.getByRole("button", {name: "Inspect file"}));
  await waitFor(() => expect(screen.getByRole("button", {name: "Apply 1 rows to draft"})).toBeTruthy());
  expect(apply).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole("button", {name: "Apply 1 rows to draft"}));
  expect(apply.mock.calls[0][0][0].values).toEqual({unitPrice: "10", unitType: "per sample", baseFee: "0"});
});

it("never enables import on a read-only page", () => {
  render(<FeeFormImportControl projectId="p" rows={rows} disabled onApply={vi.fn()} />);
  expect(screen.getByRole("button", {name: "Import Fee Form"})).toHaveProperty("disabled", true);
});

it("invalidates a preview when current fee values change and cancellation discards the upload", async () => {
  inspect.mockResolvedValue({rows: [{group: "Aa", description: "LLCR", rowKind: "matrix_step", values}]});
  const apply = vi.fn();
  const view = render(<FeeFormImportControl projectId="p" rows={rows} disabled={false} onApply={apply} />);
  fireEvent.click(screen.getByRole("button", {name: "Import Fee Form"}));
  fireEvent.change(screen.getByLabelText("Fee Form file"), {target: {files: [new File(["xls"], "fee.xls")]}});
  fireEvent.click(screen.getByRole("button", {name: "Inspect file"}));
  await screen.findByRole("button", {name: "Apply 1 rows to draft"});
  view.rerender(<FeeFormImportControl projectId="p" rows={[{...rows[0], unitPrice: "100"}]} disabled={false} onApply={apply} />);
  expect(screen.getByRole("button", {name: "Apply 1 rows to draft"})).toHaveProperty("disabled", true);
  fireEvent.click(screen.getByRole("button", {name: "Cancel import"}));
  expect(apply).not.toHaveBeenCalled();
});
