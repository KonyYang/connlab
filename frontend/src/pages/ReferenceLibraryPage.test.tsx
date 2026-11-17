import "../api/runtime.testHelpers";
import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { ReferenceLibraryPage } from "./ReferenceLibraryPage";
import * as api from "../api/referenceLibrary";
import * as archive from "../api/materialReceipts";
vi.mock("../api/materialReceipts",()=>({refreshArchive:vi.fn(),getArchiveJob:vi.fn(),cancelArchiveJob:vi.fn(),pickReceiptFolder:vi.fn(),startArchivePreview:vi.fn()}));
import {getReportShortcuts} from "../api/reportShortcuts";
import { getLegacyProject } from "../api/legacyProjects";
vi.mock("../api/referenceLibrary", () => ({ searchReferenceLibrary: vi.fn(), openReferenceFile: vi.fn(), browseReferenceFiles: vi.fn() }));
vi.mock("../api/reportShortcuts",()=>({getReportShortcuts:vi.fn(async()=>({key:"project:p1",items:[]}))}));
vi.mock("../api/legacyProjects", () => ({ getLegacyProject: vi.fn(), changeLegacyProjectLocation: vi.fn() }));
const project = { key: "project:p1", project_id: "p1", member_id: null, number: "DL-2026-08-079", title: "PwrBlade", test_item: "温升", source: "connlab", available: true, folder_path: "D:/isolated" };
const file = { name: "温升记录.xlsx", relative_path: "Records/温升记录.xlsx", is_directory: false, modified_at: "2026-11-14T01:00:00Z", extension: ".xlsx" };
beforeEach(() => {
 window.history.replaceState(null,"","/reference"); sessionStorage.clear(); vi.resetAllMocks();
 vi.mocked(archive.refreshArchive).mockResolvedValue({job_id:"scan"});vi.mocked(archive.getArchiveJob).mockResolvedValue({status:"done",result:{warnings:[]}});
 vi.mocked(getReportShortcuts).mockResolvedValue({key:"project:p1",items:[]});
 vi.mocked(getLegacyProject).mockResolvedValue({ record_id: "old", revision: 1, folder_path: "D:/isolated", name: "PwrBlade", number: "DL-2026-08-079", number_evidence: [], notes: [], imported_at: "", updated_at: "" });
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({ projects: [project], files: [], total: 0, warnings: [] });
 vi.mocked(api.browseReferenceFiles).mockResolvedValue({ key:project.key, root:project.folder_path, current_directory:"",location_state:"available",items:[file],warnings:[] });
 vi.mocked(api.openReferenceFile).mockResolvedValue({ status:"opened", message:"File opened." });
});
it("shows projects beside actual managed files and opens the selected file", async () => {
 const user=userEvent.setup(); render(<ReferenceLibraryPage onOpenProject={vi.fn()}/>);
 const filename=await screen.findByRole("button",{name:"温升记录.xlsx"});
 expect(screen.getByText("D:/isolated")).toBeTruthy();
 await act(async()=>{await user.click(filename);await user.click(screen.getByRole("button",{name:"Open file",exact:true}));});
 expect(api.openReferenceFile).toHaveBeenCalledWith(project.key,file.relative_path,false);
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Open folder",exact:true}));});
 expect(api.openReferenceFile).toHaveBeenCalledWith(project.key);
 const before=vi.mocked(api.browseReferenceFiles).mock.calls.length;
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Refresh"}));});
 await waitFor(()=>expect(vi.mocked(api.browseReferenceFiles).mock.calls.length).toBeGreaterThan(before));
});
it("searches filenames across projects and supports type filtering", async () => {
 const user=userEvent.setup(); render(<ReferenceLibraryPage onOpenProject={vi.fn()}/>);
 await screen.findByRole("button",{name:"温升记录.xlsx"});
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[project],files:[{key:project.key,title:project.title,number:project.number,name:file.name,relative_path:file.relative_path,directory:"Records",kind:"record"}],total:1,warnings:[]});
 await act(async()=>{await user.type(screen.getByLabelText("Search project materials"),"PwrBlade 温升");await user.click(screen.getByRole("button",{name:"Search",exact:true}));});
 await waitFor(()=>expect(api.searchReferenceLibrary).toHaveBeenCalledWith("PwrBlade 温升","all","all",project.key,0,expect.any(AbortSignal)));
 await act(async()=>{await user.selectOptions(screen.getByLabelText("Material type"),"record");});
 await waitFor(()=>expect(api.searchReferenceLibrary).toHaveBeenCalledWith("PwrBlade 温升","all","record",project.key,0,expect.any(AbortSignal)));
});
it("hides unavailable materials without a repair list and restores them after refresh", async () => {
 const user=userEvent.setup();
 const missing=Array.from({length:60},(_,i)=>({...project,key:`linked:old-${i}`,number:`OLD-${i}`,project_id:null,source:"linked",available:false}));
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[...missing,project],files:[],total:0,warnings:[]});
 render(<ReferenceLibraryPage onOpenProject={vi.fn()}/>);
 await screen.findByRole("button",{name:"温升记录.xlsx"});
 expect(screen.queryByText(/OLD-0/)).toBeNull();
 expect(screen.queryByRole("button",{name:/Locate/i})).toBeNull();
 expect(screen.queryByText(/material location\(s\) unavailable/)).toBeNull();
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[{...missing[0],available:true},project],files:[],total:0,warnings:[]});
 await user.click(screen.getByRole("button",{name:"Refresh"}));
 expect(await screen.findByRole("button",{name:/OLD-0/})).toBeTruthy();
});
it("preserves actionable scan warnings and search failures",async()=>{
 const user=userEvent.setup();
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[project],files:[],total:0,warnings:["Search incomplete: scan limit reached"]});
 render(<ReferenceLibraryPage onOpenProject={vi.fn()}/>);
 expect(await screen.findByText("Search incomplete: scan limit reached")).toBeTruthy();
 vi.mocked(api.searchReferenceLibrary).mockRejectedValue(new Error("Could not load materials."));
 await user.click(screen.getByRole("button",{name:"Refresh"}));
 expect(await screen.findByRole("alert")).toHaveProperty("textContent",expect.stringContaining("Could not load materials."));
 expect(screen.getByRole("button",{name:"Retry"})).toBeTruthy();
});
it("does not list projects with no associated materials",async()=>{
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[{...project,folder_path:"",available:false}],files:[],total:0,warnings:[]});
 render(<ReferenceLibraryPage onOpenProject={vi.fn()}/>);
 expect(await screen.findByText(/No materials to show/)).toBeTruthy();
 expect(screen.queryByRole("button",{name:/DL-2026-08-079/})).toBeNull();
 expect(screen.queryByRole("alert")).toBeNull();
});

it("keeps an exact member entry when a project with the same member id has another root",async()=>{
 window.history.replaceState(null,"","/reference?entry=member:m1");
 const native={...project,member_id:"m1"};
 const member={...project,key:"member:m1",member_id:"m1",title:"Received originals",source:"received",folder_path:"D:/separate-copy"};
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[native,member],files:[],total:0,warnings:[]});
 render(<ReferenceLibraryPage onOpenProject={vi.fn()}/>);
 expect(await screen.findByText("D:/separate-copy")).toBeTruthy();
 await waitFor(()=>expect(api.browseReferenceFiles).toHaveBeenCalledWith("member:m1","",expect.any(AbortSignal)));
 expect(getReportShortcuts).toHaveBeenCalledWith("member:m1",expect.any(AbortSignal));
});

it("keeps incomplete receipts visible and allows search while a scan cancellation is pending",async()=>{
 const user=userEvent.setup();
 vi.mocked(archive.getArchiveJob).mockResolvedValue({status:"cancellation_requested"});
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[{...project,key:"archive:pending",project_id:null,available:false,operation_id:"pending",intake_status:"incomplete"}],files:[],total:0,warnings:[]});
 const view=render(<ReferenceLibraryPage onOpenProject={vi.fn()}/>);
 expect(await screen.findByRole("button",{name:"Continue receipt"})).toBeTruthy();
 await screen.findByRole("button",{name:"Cancelling scan…"});
 expect(screen.getByRole("button",{name:"Search",exact:true})).not.toHaveProperty("disabled",true);
 await user.type(screen.getByRole("textbox",{name:"Search project materials"}),"old folder");
 await user.click(screen.getByRole("button",{name:"Search",exact:true}));
 await waitFor(()=>expect(api.searchReferenceLibrary).toHaveBeenCalledWith("old folder","all","all","",0,expect.any(AbortSignal)));
 view.unmount();
});

it("prevents duplicate receipt pickers while leaving library search usable",async()=>{
 const user=userEvent.setup();let choose!:(source:string)=>void;
 vi.mocked(archive.pickReceiptFolder).mockImplementation(()=>new Promise(resolve=>{choose=resolve;}));
 const view=render(<ReferenceLibraryPage onOpenProject={vi.fn()}/>);
 await screen.findByRole("button",{name:"温升记录.xlsx"});
 const receive=screen.getByRole("button",{name:"Receive materials"});await user.click(receive);await user.click(receive);
 expect(receive).toHaveProperty("disabled",true);expect(archive.pickReceiptFolder).toHaveBeenCalledOnce();
 expect(screen.queryByRole("dialog")).toBeNull();
 await user.type(screen.getByRole("textbox",{name:"Search project materials"}),"record");
 await user.click(screen.getByRole("button",{name:"Search",exact:true}));
 await waitFor(()=>expect(api.searchReferenceLibrary).toHaveBeenCalledWith("record","all","all","",0,expect.any(AbortSignal)));
 view.unmount();await act(async()=>choose("C:/late"));expect(archive.startArchivePreview).not.toHaveBeenCalled();
});
