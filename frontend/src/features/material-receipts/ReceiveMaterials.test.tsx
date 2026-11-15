import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { ReceiveMaterials } from "./ReceiveMaterials";
import * as api from "../../api/materialReceipts";
vi.mock("../../api/materialReceipts", () => ({ getReceiptRuntime: vi.fn(), setReceiptDestination: vi.fn(), pickReceiptFolder: vi.fn(), previewReceipt: vi.fn(), confirmReceipt: vi.fn(), getReceiptBatch: vi.fn(), retryReceipt: vi.fn() }));
const ready = { status: "ready" as const, plan_id: "plan", fingerprint: "hash", batch_id: "batch", candidates: [], target_path: "D:/received/old", items: [{ relative_path: "report.docx", target_relative: "补充资料/date-source/report.docx", directory: false, action: "supplement", reason: "Existing content retained." }] };
beforeEach(() => { vi.resetAllMocks(); sessionStorage.clear(); vi.mocked(api.getReceiptRuntime).mockResolvedValue({ root_path: "D:/received", revision: 1, configured: true, available: true }); vi.mocked(api.pickReceiptFolder).mockResolvedValue("C:/source/DL-2026-08-079"); vi.mocked(api.previewReceipt).mockResolvedValue(ready); vi.mocked(api.confirmReceipt).mockResolvedValue({ batch_id: "batch", status: "completed", target_path: "D:/received/old", source_path: "C:/source", target_key: "receipt:r1", receipt_id: "r1", items: [], counts: { copied: 0, skipped: 0, supplemented: 1, failed: 0 }, directory_counts: {} }); });
it("selects and reviews without copying, shows conflict location, confirms explicitly", async () => {
 const user = userEvent.setup(); render(<ReceiveMaterials onClose={vi.fn()} onReceived={vi.fn()} />);
 await screen.findByText("Materials library folder: D:/received");
 await act(async () => { await user.click(screen.getByRole("button", { name: "Choose source folder" })); });
 expect(api.previewReceipt).not.toHaveBeenCalled(); expect(api.confirmReceipt).not.toHaveBeenCalled();
 await act(async () => { await user.click(screen.getByRole("button", { name: "Review receipt" })); });
 expect(await screen.findByText("补充资料/date-source/report.docx")).toBeTruthy();
 expect(api.confirmReceipt).not.toHaveBeenCalled();
 await act(async () => { await user.click(screen.getByRole("button", { name: "Confirm receipt" })); });
 expect(api.confirmReceipt).toHaveBeenCalledWith(ready);
 expect(await screen.findByText("Materials received and verified.")).toBeTruthy();
});
it("invalidates review when information changes", async () => {
 const user = userEvent.setup(); render(<ReceiveMaterials onClose={vi.fn()} onReceived={vi.fn()} />);
 await screen.findByText("Materials library folder: D:/received");
 await act(async () => { await user.type(screen.getByLabelText("Source folder"), "C:/old"); await user.click(screen.getByRole("button", { name: "Review receipt" })); });
 await screen.findByRole("button", { name: "Confirm receipt" });
 await act(async () => { await user.type(screen.getByLabelText("Product name"), "Updated"); });
 expect(screen.queryByRole("button", { name: "Confirm receipt" })).toBeNull();
});

it("requires an explicit same-number destination and binds the next review to it", async () => {
 const user = userEvent.setup();
 const candidate = { key: "receipt:existing", receipt_id: "existing", project_id: null, member_id: null, number: "Legacy/2001-a", title: "Existing product", test_item: "", folder_path: "D:/received/existing", source: "received", available: true, can_supplement: true, reason: "" };
 vi.mocked(api.previewReceipt).mockResolvedValueOnce({ status: "choose_target", candidates: [candidate] }).mockResolvedValueOnce(ready);
 render(<ReceiveMaterials onClose={vi.fn()} onReceived={vi.fn()} />);
 await screen.findByText("Materials library folder: D:/received");
 await act(async () => { await user.type(screen.getByLabelText("Source folder"), "C:/old"); await user.type(screen.getByLabelText("Project number"), "Legacy/2001-a"); await user.click(screen.getByRole("button", { name: "Review receipt" })); });
 const target = await screen.findByRole("radio", { name: /Existing product/ });
 expect((target as HTMLInputElement).checked).toBe(false);
 expect(api.confirmReceipt).not.toHaveBeenCalled();
 await act(async () => { await user.click(target); await user.click(screen.getByRole("button", { name: "Review receipt" })); });
 expect(api.previewReceipt).toHaveBeenLastCalledWith(expect.objectContaining({ target_key: "receipt:existing", number: "Legacy/2001-a" }));
 expect(screen.getByRole("button", { name: "Confirm receipt" })).toBeTruthy();
});
it("checks a lost confirmation result on reopen without automatically copying again", async () => {
 const user = userEvent.setup();
 vi.mocked(api.confirmReceipt).mockRejectedValueOnce(new Error("Connection lost"));
 const view = render(<ReceiveMaterials onClose={vi.fn()} onReceived={vi.fn()} />);
 await screen.findByText("Materials library folder: D:/received");
 await act(async () => { await user.type(screen.getByLabelText("Source folder"), "C:/old"); await user.click(screen.getByRole("button", { name: "Review receipt" })); });
 await act(async () => { await user.click(screen.getByRole("button", { name: "Confirm receipt" })); });
 expect(await screen.findByText("Connection lost")).toBeTruthy();
 view.unmount();
 vi.mocked(api.getReceiptBatch).mockResolvedValue({ batch_id: "batch", status: "completed", target_path: "D:/received/old", source_path: "C:/old", target_key: "receipt:r1", receipt_id: "r1", items: [], counts: { copied: 1 }, directory_counts: {} });
 render(<ReceiveMaterials onClose={vi.fn()} onReceived={vi.fn()} />);
 await screen.findByText("Materials received and verified.");
 expect(api.getReceiptBatch).toHaveBeenCalledWith("batch");
 expect(api.confirmReceipt).toHaveBeenCalledTimes(1);
});


it("uses the configured location without destination controls or configuration writes", async () => {
 const user=userEvent.setup(); render(<ReceiveMaterials onClose={vi.fn()} onReceived={vi.fn()}/>);
 await screen.findByText("Materials library folder: D:/received");
 expect(screen.queryByLabelText("Materials library folder")).toBeNull();
 expect(screen.queryByRole("button",{name:"Choose save location"})).toBeNull();
 expect(screen.queryByRole("button",{name:"Use save location"})).toBeNull();
 await user.type(screen.getByLabelText("Source folder"),"C:/source");
 await user.click(screen.getByRole("button",{name:"Review receipt"}));
 expect(api.previewReceipt).toHaveBeenCalledWith(expect.objectContaining({source:"C:/source"}));
 expect(api.setReceiptDestination).not.toHaveBeenCalled();
});

it.each([false,true])("directs unavailable or unset receive locations to Settings (configured=%s)",async(configured)=>{
 vi.mocked(api.getReceiptRuntime).mockResolvedValue({root_path:configured?"D:/offline":"",revision:1,configured,available:false});
 render(<ReceiveMaterials onClose={vi.fn()} onReceived={vi.fn()}/>);
 const link=await screen.findByRole("link",{name:"Open Settings"});
 expect(link.getAttribute("href")).toBe("/settings");
 expect(screen.getByRole("alert").textContent).toContain("Materials library folder");
 expect(screen.getByRole("button",{name:"Review receipt"}).hasAttribute("disabled")).toBe(true);
 expect(api.confirmReceipt).not.toHaveBeenCalled();
});


it("offers Settings when default library initialization fails",async()=>{
 vi.mocked(api.getReceiptRuntime).mockRejectedValue(new Error("The material location is unavailable or cannot be written."));
 render(<ReceiveMaterials onClose={vi.fn()} onReceived={vi.fn()}/>);
 expect(await screen.findByRole("alert")).toHaveProperty("textContent",expect.stringContaining("cannot be written"));
 expect(screen.getByRole("link",{name:"Open Settings"}).getAttribute("href")).toBe("/settings");
 expect(screen.getByRole("button",{name:"Review receipt"}).hasAttribute("disabled")).toBe(true);
 expect(api.confirmReceipt).not.toHaveBeenCalled();
});
