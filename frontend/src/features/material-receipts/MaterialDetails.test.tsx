import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { MaterialDetails } from "./MaterialDetails";
import * as api from "../../api/materialReceipts";
vi.mock("../../api/materialReceipts", () => ({ getReceiptDetail: vi.fn(), editReceiptMetadata: vi.fn(), pickReceiptFolder: vi.fn(), previewReceiptLocation: vi.fn(), confirmReceiptLocation: vi.fn(), getCatalogReceiptHistory: vi.fn(), getReceiptBatch: vi.fn(), retryReceipt: vi.fn() }));
const project = { key: "receipt:r1", receipt_id: "r1", project_id: null, member_id: null, number: "Legacy/2001-a", title: "Product", test_item: "", source: "received", available: true, folder_path: "D:/received" };
const detail = { receipt_id: "r1", number: "Legacy/2001-a", product_name: "Product", test_keywords: "Temperature", description: "old PC", material_state: "completed", folder_path: "D:/received", source_path: "C:/old", revision: 1, batch_id: "b1", created_at: "2026-11-14", available: true, batch: { batch_id: "b1", status: "completed", source_path: "C:/old", target_path: "D:/received", target_key: "receipt:r1", receipt_id: "r1", items: [], counts: {}, directory_counts: {} } };
beforeEach(() => { vi.resetAllMocks(); vi.mocked(api.getCatalogReceiptHistory).mockResolvedValue({items:[]}); vi.mocked(api.getReceiptDetail).mockResolvedValue(detail); vi.mocked(api.editReceiptMetadata).mockResolvedValue(detail); });
it("edits only receipt information and refreshes details", async () => {
 const user = userEvent.setup(); const changed = vi.fn();
 render(<MaterialDetails project={project} onClose={vi.fn()} onBrowse={vi.fn()} onProject={vi.fn()} onChanged={changed} />);
 await screen.findByText("Declared project state: Completed");
 await act(async () => { await user.click(screen.getByRole("button", { name: "Edit materials information" })); });
 await act(async () => { await user.clear(screen.getByLabelText("Product name")); await user.type(screen.getByLabelText("Product name"), "New product"); await user.click(screen.getByRole("button", { name: "Save information" })); });
 expect(api.editReceiptMetadata).toHaveBeenCalledWith("r1", { revision: 1, product_name: "New product", test_keywords: "Temperature", material_state: "completed" });
 expect(changed).toHaveBeenCalled(); expect(screen.queryByText("Prepare to Take")).toBeNull();
});

it.each([true,false])("shows daily details without source, history or relocation (receipt=%s)",async received=>{
 const native={...project,key:"project:p1",receipt_id:undefined,project_id:"p1",source:"connlab",folder_path:"D:/Projects/Native"};
 const openProject=vi.fn();const user=userEvent.setup();
 render(<MaterialDetails project={received?project:native} onClose={vi.fn()} onBrowse={vi.fn()} onProject={openProject} onChanged={vi.fn()}/>);
 if(received) await screen.findByText("Declared project state: Completed");
 expect(screen.queryAllByText(/Receipt history|Original source/)).toHaveLength(0);
 expect(screen.queryByText("C:/old")).toBeNull();
 expect(screen.queryByRole("button",{name:/Locate|Retry receipt|View receipt/})).toBeNull();
 expect(api.getCatalogReceiptHistory).not.toHaveBeenCalled();
 expect(api.getReceiptBatch).not.toHaveBeenCalled();
 expect(api.retryReceipt).not.toHaveBeenCalled();
 if(!received){
  expect(screen.getByText("Managed location: D:/Projects/Native")).toBeTruthy();
  await user.click(screen.getByRole("button",{name:"Project workspace"}));
  expect(openProject).toHaveBeenCalledWith("p1");
 }
});
