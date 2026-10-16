import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ProjectRegistryBatchPanel } from "./ProjectRegistryBatchPanel";
import * as api from "../../api/projectRegistryManagement";
vi.mock("../../api/projectRegistryManagement",()=>({previewRegistryBatch:vi.fn(),moveRegistryBatch:vi.fn()}));
describe("recoverable batch management",()=>{
  it("requires preview, preserves selection on failure, and cancel never moves records",async()=>{
    vi.mocked(api.previewRegistryBatch).mockResolvedValue({action:"trash",destination:"active",token:"batch",blockers:[],items:[]});
    vi.mocked(api.moveRegistryBatch).mockRejectedValue(new Error("One selected record changed"));
    const user=userEvent.setup();render(<ProjectRegistryBatchPanel location="active" rows={[{project_id:"p1",label:"TMP-1",temporary:true}]} onChanged={vi.fn()}/>);
    await user.click(screen.getByRole("button",{name:"Batch record management"}));
    await user.click(screen.getByRole("checkbox",{name:"Select TMP-1"}));
    await user.type(screen.getByRole("textbox",{name:"Removal reason"}),"Old test record");
    await user.click(screen.getByRole("button",{name:"Preview selected records"}));
    await user.click(await screen.findByRole("button",{name:"Cancel batch review"}));
    expect(api.moveRegistryBatch).not.toHaveBeenCalled();expect(screen.getByRole("checkbox",{name:"Select TMP-1"})).toHaveProperty("checked",true);
    await user.click(screen.getByRole("button",{name:"Preview selected records"}));
    await user.dblClick(await screen.findByRole("button",{name:"Confirm batch move"}));
    await waitFor(()=>expect(api.moveRegistryBatch).toHaveBeenCalledTimes(1));
    expect(await screen.findByRole("alert")).toBeTruthy();expect(screen.getByRole("checkbox",{name:"Select TMP-1"})).toHaveProperty("checked",true);
  });
});
