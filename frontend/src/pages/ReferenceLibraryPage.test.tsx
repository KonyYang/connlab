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
it("keeps unavailable entries out of the main list but offers their registered location and a refresh action", async () => {
 const user=userEvent.setup();
 const missing={...project,key:"project:missing",project_id:"missing",number:"OLD-MISSING",folder_path:"D:/missing",available:false};
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[missing,project],files:[],total:0,warnings:[]});
 render(<ReferenceLibraryPage onOpenProject={vi.fn()}/>);
 await screen.findByRole("button",{name:"温升记录.xlsx"});
 expect(screen.queryByRole("button",{name:/OLD-MISSING.*ConnLab project/})).toBeNull();
 await user.click(screen.getByText("1 material location unavailable"));
 await user.click(screen.getByRole("button",{name:"View location for OLD-MISSING"}));
 expect(screen.getByText("D:/missing")).toBeTruthy();
 expect(screen.getByText(/Restore access to the registered folder, then refresh/)).toBeTruthy();
 expect(screen.getByRole("button",{name:"Refresh materials"})).toBeTruthy();
 expect(screen.getByRole("button",{name:"Open folder",exact:true})).toHaveProperty("disabled",true);
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

it("explains file selection and missing Workbench target without blocking ordinary file access",async()=>{
 const user=userEvent.setup();render(<ReferenceLibraryPage onOpenProject={vi.fn()}/>);
 await screen.findByRole("button",{name:"温升记录.xlsx"});
 expect(screen.getByText("Select a file to open or copy.")).toBeTruthy();
 expect(screen.getByRole("region",{name:"Copy destination"}).textContent).toContain("Open the target project's Workbench");
 await user.click(screen.getByRole("button",{name:"温升记录.xlsx"}));
 expect(screen.getByRole("status",{name:"File selection"}).textContent).toContain(file.relative_path);
 expect(screen.getByRole("button",{name:"Open file",exact:true})).toHaveProperty("disabled",false);
 expect(screen.getByRole("button",{name:"Copy to current project…"})).toHaveProperty("disabled",true);
});
it("browsing project B changes the source and clears file selection but keeps explicit Workbench A as destination",async()=>{
 const user=userEvent.setup();const b={...project,key:"project:p2",project_id:"p2",number:"DL-B",title:"Product B",folder_path:"D:/B"};
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[project,b],files:[],total:0,warnings:[]});
 const context={session_id:"session",token:"A-context",intent:1,target:project};
 const view=render(<ReferenceLibraryPage copyContext={context} onOpenProject={vi.fn()}/>);
 await screen.findByRole("button",{name:"温升记录.xlsx"});
 await user.click(screen.getByRole("button",{name:"温升记录.xlsx"}));
 await user.click(screen.getByRole("button",{name:/DL-B Product B/}));
 await screen.findByRole("button",{name:"温升记录.xlsx"});
 expect(screen.getByLabelText("Browsing materials").textContent).toContain("Product B");
 expect(screen.getByRole("status",{name:"File selection"}).textContent).toContain("Select a file");
 expect(screen.getByRole("region",{name:"Copy destination"}).textContent).toContain("DL-2026-08-079");
 expect(screen.getByRole("region",{name:"Copy destination"}).textContent).toContain("D:/isolated");
 view.rerender(<ReferenceLibraryPage copyContext={null} onOpenProject={vi.fn()}/>);
 expect(screen.getByRole("region",{name:"Copy destination"}).textContent).not.toContain("D:/isolated");
});

it("distinguishes an explicitly searched project with no linked materials from a missing registered location",async()=>{
 const user=userEvent.setup();const open=vi.fn();render(<ReferenceLibraryPage onOpenProject={open}/>);
 await screen.findByRole("button",{name:"温升记录.xlsx"});
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[{...project,folder_path:"",available:false}],files:[],total:0,warnings:[]});
 await user.type(screen.getByLabelText("Search project materials"),"PwrBlade");await user.click(screen.getByRole("button",{name:"Search",exact:true}));
 await user.click(await screen.findByRole("button",{name:"Open project Workbench"}));
 expect(open).toHaveBeenCalledWith("p1");
 expect(screen.getByText(/No materials linked yet. Open the project Workbench/)).toBeTruthy();
 expect(screen.queryByText(/Original material location is unavailable/)).toBeNull();
});
it("does not describe retained unavailable locations as absent materials",async()=>{
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[{...project,folder_path:"D:/offline",available:false}],files:[],total:0,warnings:[]});
 render(<ReferenceLibraryPage onOpenProject={vi.fn()}/>);
 expect(await screen.findByText("No available material locations. Review the location warning.")).toBeTruthy();
 expect(screen.queryByText("No materials to show. Receive existing files.")).toBeNull();
});
