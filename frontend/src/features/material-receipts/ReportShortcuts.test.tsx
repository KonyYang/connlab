import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { MaterialFiles } from "./MaterialFiles";
import * as reports from "../../api/reportShortcuts";
import * as files from "../../api/referenceLibrary";
vi.mock("../../api/reportShortcuts",()=>({getReportShortcuts:vi.fn(),setReportShortcut:vi.fn(),clearReportShortcut:vi.fn()}));
vi.mock("../../api/referenceLibrary",()=>({browseReferenceFiles:vi.fn(),openReferenceFile:vi.fn(),searchReferenceLibrary:vi.fn()}));
const project={key:"receipt:r1",project_id:null,member_id:null,number:"OLD",title:"Materials",test_item:"",source:"received",folder_path:"D:/materials",available:true};
const file={name:"new.docx",relative_path:"Reports/new.docx",is_directory:false,modified_at:null,extension:".docx"};
const renderFiles=()=>render(<MaterialFiles project={project} query="" kind="all" refresh={0} onError={vi.fn()} onWarnings={vi.fn()} onCopy={vi.fn()}/>);
beforeEach(()=>{vi.resetAllMocks();vi.mocked(reports.getReportShortcuts).mockResolvedValue({key:project.key,items:[]});vi.mocked(files.browseReferenceFiles).mockResolvedValue({key:project.key,root:project.folder_path,current_directory:"",location_state:"available",items:[file],warnings:[]});});
it("sets first shortcut quietly and allows the same file in both roles",async()=>{
 const user=userEvent.setup();renderFiles();
 await user.click(await screen.findByRole("button",{name:"new.docx"}));
 await user.click(screen.getByText("More"));
 const internal={role:"internal" as const,relative_path:file.relative_path,available:true,modified_at:null};
 vi.mocked(reports.setReportShortcut).mockResolvedValueOnce({key:project.key,items:[internal]});
 await user.click(screen.getByRole("button",{name:"Set as Internal report"}));
 expect(reports.setReportShortcut).toHaveBeenCalledWith(project.key,"internal",file.relative_path,null,false);
 expect(screen.queryByRole("dialog")).toBeNull();
 const shortcut=await screen.findByRole("button",{name:"Internal report · new.docx"});
 await user.click(shortcut);
 expect(files.openReferenceFile).toHaveBeenCalledWith(project.key,file.relative_path);
 vi.mocked(reports.setReportShortcut).mockResolvedValueOnce({key:project.key,items:[internal,{...internal,role:"customer"}]});
 await user.click(screen.getByRole("button",{name:"Set as Customer report"}));
 expect(await screen.findByRole("button",{name:"Customer report · new.docx"})).toBeTruthy();
 expect(screen.queryByRole("dialog")).toBeNull();
});
it("shows old and new paths before replacing and cancels associations directly",async()=>{
 const user=userEvent.setup();const old={role:"internal" as const,relative_path:"Reports/old.docx",available:true,modified_at:null};
 vi.mocked(reports.getReportShortcuts).mockResolvedValue({key:project.key,items:[old]});renderFiles();
 await user.click(await screen.findByRole("button",{name:"new.docx"}));await user.click(screen.getByText("More"));
 await user.click(screen.getByRole("button",{name:"Replace Internal report"}));
 expect(screen.getByRole("dialog")).toBeTruthy();expect(screen.getByText("Current: Reports/old.docx")).toBeTruthy();expect(screen.getByText("Selected: Reports/new.docx")).toBeTruthy();
 expect(reports.setReportShortcut).not.toHaveBeenCalled();
 vi.mocked(reports.setReportShortcut).mockResolvedValue({key:project.key,items:[{...old,relative_path:file.relative_path}]});
 await user.click(screen.getByRole("button",{name:"Confirm replacement"}));
 await waitFor(()=>expect(reports.setReportShortcut).toHaveBeenCalledWith(project.key,"internal",file.relative_path,old.relative_path,true));
 vi.mocked(reports.clearReportShortcut).mockResolvedValue({key:project.key,items:[]});
 await user.click(screen.getAllByRole("button",{name:"Remove Internal report shortcut"})[0]);
 expect(reports.clearReportShortcut).toHaveBeenCalledWith(project.key,"internal",file.relative_path);
});


it.each([false,true])("can remove a missing report with no file rows, root available=%s",async available=>{
 const user=userEvent.setup();const locate=vi.fn();
 vi.mocked(reports.getReportShortcuts).mockResolvedValue({key:project.key,items:[{role:"internal",relative_path:"missing.docx",available:false,modified_at:null}]});
 vi.mocked(files.browseReferenceFiles).mockResolvedValue({key:project.key,root:project.folder_path,current_directory:"",location_state:"available",items:[],warnings:[]});
 vi.mocked(reports.clearReportShortcut).mockResolvedValue({key:project.key,items:[]});
 render(<MaterialFiles project={{...project,available}} query="" kind="all" refresh={0} onError={vi.fn()} onWarnings={vi.fn()} onCopy={vi.fn()} onLocate={locate}/>);
 expect(await screen.findByText("Common reports")).toBeTruthy();
 expect(screen.getByRole("button",{name:"Internal report · missing.docx"}).hasAttribute("disabled")).toBe(true);
 if(!available){await user.click(screen.getByRole("button",{name:"Locate report folder"}));expect(locate).toHaveBeenCalledOnce();}
 else expect(screen.getByRole("button",{name:"Choose replacement for Internal report"})).toBeTruthy();
 await user.click(screen.getByRole("button",{name:"Remove Internal report shortcut"}));
 expect(reports.clearReportShortcut).toHaveBeenCalledWith(project.key,"internal","missing.docx");
 await waitFor(()=>expect(screen.queryByText("Common reports")).toBeNull());
});


it("keeps a missing pointer and explicitly reviews the selected replacement",async()=>{
 const user=userEvent.setup();vi.mocked(reports.getReportShortcuts).mockResolvedValue({key:project.key,items:[{role:"customer",relative_path:"Reports/missing.pdf",available:false,modified_at:null}]});
 renderFiles();await user.click(await screen.findByRole("button",{name:"Choose replacement for Customer report"}));
 await user.click(await screen.findByRole("button",{name:"new.docx"}));
 expect(screen.getByText("Current: Reports/missing.pdf")).toBeTruthy();
 expect(screen.getByText("Selected: Reports/new.docx")).toBeTruthy();
 expect(reports.setReportShortcut).not.toHaveBeenCalled();
});
