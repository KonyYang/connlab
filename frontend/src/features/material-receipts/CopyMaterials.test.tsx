import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { CopyMaterials } from "./CopyMaterials";
import { ApiRequestError } from "../../api/client";
import * as api from "../../api/materialReceipts";
import { searchReferenceLibrary } from "../../api/referenceLibrary";
vi.mock("../../api/materialReceipts",async()=>({...await vi.importActual<typeof import("../../api/materialReceipts")>("../../api/materialReceipts"),previewMaterialCopy:vi.fn(),confirmMaterialCopy:vi.fn(),getReceiptBatch:vi.fn(),retryReceipt:vi.fn()}));
vi.mock("../../api/referenceLibrary",()=>({searchReferenceLibrary:vi.fn(),openReferenceFile:vi.fn()}));
const source={key:"receipt:old",project_id:null,member_id:null,number:"Old-1",title:"Old product",test_item:"",source:"received",available:true,folder_path:"D:/old-managed"};
const target={...source,key:"project:p1",project_id:"p1",number:"New-1",title:"Current product",source:"connlab",folder_path:"D:/current"};
const context={session_id:"session",token:"context-1",intent:1,target};
beforeEach(()=>{vi.resetAllMocks();vi.mocked(searchReferenceLibrary).mockResolvedValue({projects:[target],files:[],total:0,warnings:[]});});
it("requires target review and explicit confirmation for a selected file",async()=>{
 const user=userEvent.setup();const copied=vi.fn();
 const plan={status:"ready" as const,candidates:[],plan_id:"copy-plan",fingerprint:"hash",target_path:"D:/current",items:[{relative_path:"Reports/report.docx",target_relative:"补充资料/batch/report.docx",directory:false,action:"supplement",reason:"Existing report retained."}]};
 vi.mocked(api.previewMaterialCopy).mockResolvedValue(plan);
 vi.mocked(api.confirmMaterialCopy).mockResolvedValue({batch_id:"copy1",status:"completed",target_key:"project:p1",target_path:"D:/current",source_path:"D:/old-managed/Reports/report.docx",receipt_id:null,items:[],counts:{supplemented:1},directory_counts:{}});
 render(<CopyMaterials source={source} file={{name:"report.docx",relative_path:"Reports/report.docx",is_directory:false,modified_at:null,extension:".docx"}} context={context} onClose={vi.fn()} onCopied={copied}/>);
 await screen.findByText("Project location: D:/current");
 expect(api.confirmMaterialCopy).not.toHaveBeenCalled();
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Check destination"}));});
 expect(api.previewMaterialCopy).toHaveBeenCalledWith({source_key:"receipt:old",relative_path:"Reports/report.docx",context:{session_id:"session",token:"context-1"},target_relative_directory:"Reference materials"});
 expect(await screen.findByText("补充资料/batch/report.docx")).toBeTruthy();
 expect(api.confirmMaterialCopy).not.toHaveBeenCalled();
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Confirm copy"}));});
 expect(api.confirmMaterialCopy).toHaveBeenCalledWith(plan,{session_id:"session",token:"context-1"});expect(copied).toHaveBeenCalled();
});

it("keeps a lost copy result bound to its operation and can show target materials",async()=>{
 const user=userEvent.setup();const history=vi.fn();
 vi.mocked(api.previewMaterialCopy).mockResolvedValue({status:"ready",candidates:[],plan_id:"copy",fingerprint:"hash",batch_id:"bcopy",items:[],target_path:"D:/current"});
 vi.mocked(api.confirmMaterialCopy).mockRejectedValue(new Error("Response lost"));
 render(<CopyMaterials source={source} file={{name:"report.docx",relative_path:"report.docx",is_directory:false,modified_at:null,extension:".docx"}} context={context} onClose={vi.fn()} onCopied={vi.fn()} onTargetMaterials={history}/>);
 await screen.findByText("Project location: D:/current");
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Check destination"}));});
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Confirm copy"}));});
 expect(await screen.findByText("Response lost")).toBeTruthy();
 expect(screen.getByLabelText("Target directory within project").hasAttribute("disabled")).toBe(true);
 await act(async()=>{await user.click(screen.getByRole("button",{name:"View target materials"}));});
 expect(history).toHaveBeenCalledWith(target);expect(api.confirmMaterialCopy).toHaveBeenCalledTimes(1);
});

it("requires a fresh missing-result check after a retry response is lost",async()=>{
 const user=userEvent.setup();
 vi.mocked(api.previewMaterialCopy).mockResolvedValue({status:"ready",candidates:[],plan_id:"copy",fingerprint:"hash",batch_id:"bcopy",items:[],target_path:"D:/current"});
 vi.mocked(api.confirmMaterialCopy).mockRejectedValue(new Error("Response lost"));
 vi.mocked(api.getReceiptBatch).mockRejectedValue(new ApiRequestError("Not found",404,null));
 render(<CopyMaterials source={source} file={{name:"report.docx",relative_path:"report.docx",is_directory:false,modified_at:null,extension:".docx"}} context={context} onClose={vi.fn()} onCopied={vi.fn()}/>);
 await screen.findByText("Project location: D:/current");
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Check destination"}));});
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Confirm copy"}));});
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Check copy result"}));});
 expect(screen.getByRole("button",{name:"Review copy again"})).toBeTruthy();
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Retry confirmed copy"}));});
 expect(screen.queryByRole("button",{name:"Review copy again"})).toBeNull();
 expect(api.confirmMaterialCopy).toHaveBeenCalledTimes(2);
});


it("requires a live Workbench context instead of offering a target selector", async()=>{
 render(<CopyMaterials source={source} file={{name:"report.docx",relative_path:"report.docx",is_directory:false,modified_at:null,extension:".docx"}} onClose={vi.fn()} onCopied={vi.fn()}/>);
 expect(screen.queryByLabelText("Target project")).toBeNull();
 expect(await screen.findByText(/Open the target Project Workbench/)).toBeTruthy();
 expect(api.previewMaterialCopy).not.toHaveBeenCalled();
});


it("drops delayed previews when the live Workbench switches and clears retry controls",async()=>{
 const user=userEvent.setup();let resolve!:(plan:api.ReceiptPlan)=>void;
 vi.mocked(api.previewMaterialCopy).mockImplementation(()=>new Promise(done=>{resolve=done;}));
 const props={source,file:{name:"report.docx",relative_path:"report.docx",is_directory:false,modified_at:null,extension:".docx"},onClose:vi.fn(),onCopied:vi.fn()};
 const view=render(<CopyMaterials {...props} context={context}/>);
 await user.click(screen.getByRole("button",{name:"Check destination"}));
 const next={...context,token:"context-2",intent:2,target:{...target,key:"project:p2",project_id:"p2",number:"New-2",folder_path:"D:/next"}};
 view.rerender(<CopyMaterials {...props} context={next}/>);
 await act(async()=>resolve({status:"ready",plan_id:"old",fingerprint:"old",candidates:[],items:[],target_path:"D:/current"}));
 expect(screen.queryByRole("button",{name:"Confirm copy"})).toBeNull();
 expect(screen.getByText("Project location: D:/next")).toBeTruthy();
 view.rerender(<CopyMaterials {...props} context={null}/>);
 expect(screen.queryByRole("button",{name:"Retry confirmed copy"})).toBeNull();
 expect(screen.queryByRole("button",{name:"Check destination"})).toBeNull();
 expect(api.confirmMaterialCopy).not.toHaveBeenCalled();
});

it.each(["switch", "clear"])("invalidates confirmed-operation retry controls after Workbench %s",async mode=>{
 const user=userEvent.setup();
 const plan={status:"ready" as const,candidates:[],plan_id:"old-copy",fingerprint:"hash",batch_id:"old-batch",items:[],target_path:"D:/current"};
 vi.mocked(api.previewMaterialCopy).mockResolvedValue(plan);
 vi.mocked(api.confirmMaterialCopy).mockResolvedValue({batch_id:"old-batch",status:"incomplete",target_key:"project:p1",target_path:"D:/current",source_path:"D:/old-managed/report.docx",receipt_id:null,items:[],counts:{failed:1},directory_counts:{}});
 const props={source,file:{name:"report.docx",relative_path:"report.docx",is_directory:false,modified_at:null,extension:".docx"},onClose:vi.fn(),onCopied:vi.fn()};
 const view=render(<CopyMaterials {...props} context={context}/>);
 await user.click(screen.getByRole("button",{name:"Check destination"}));await user.click(await screen.findByRole("button",{name:"Confirm copy"}));
 expect(await screen.findByRole("button",{name:"Retry copy"})).toBeTruthy();
 const next=mode==="clear" ? null : {...context,token:"context-B",intent:2,target:{...target,key:"project:p2",project_id:"p2",number:"New-B",folder_path:"D:/B"}};
 view.rerender(<CopyMaterials {...props} context={next}/>);
 expect(screen.queryByRole("button",{name:"Retry copy"})).toBeNull();
 expect(screen.queryByRole("button",{name:"Confirm copy"})).toBeNull();
 expect(screen.queryByRole("button",{name:"Retry confirmed copy"})).toBeNull();
 expect(api.retryReceipt).not.toHaveBeenCalled();expect(api.confirmMaterialCopy).toHaveBeenCalledTimes(1);
});
