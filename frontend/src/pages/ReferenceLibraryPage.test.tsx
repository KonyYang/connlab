import "../api/runtime.testHelpers";
import { act, render, screen, within, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { ReferenceLibraryPage } from "./ReferenceLibraryPage";
import { runtimeSessionStorage } from "../runtimeEnvironment";
import * as api from "../api/referenceLibrary";
import * as archive from "../api/materialReceipts";
vi.mock("../api/materialReceipts",async()=>({...await vi.importActual<typeof import("../api/materialReceipts")>("../api/materialReceipts"),refreshArchive:vi.fn(),getArchiveJob:vi.fn(),cancelArchiveJob:vi.fn(),pickReceiptFolder:vi.fn(),startArchivePreview:vi.fn(),previewMaterialCopy:vi.fn(),confirmMaterialCopy:vi.fn()}));
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
 const user=userEvent.setup(); render(<ReferenceLibraryPage/>);
 const filename=await screen.findByRole("button",{name:"温升记录.xlsx"});
 expect(screen.getByText("D:/isolated")).toBeTruthy();
 await user.click(filename);
 expect(api.openReferenceFile).not.toHaveBeenCalled();
 expect(screen.queryByRole("button",{name:"Open file",exact:true})).toBeNull();
 await user.dblClick(filename);
 expect(api.openReferenceFile).toHaveBeenCalledTimes(1);
 await user.keyboard("{Enter}");
 expect(api.openReferenceFile).toHaveBeenCalledTimes(2);
 expect(api.openReferenceFile).toHaveBeenCalledWith(project.key,file.relative_path,false);
 const folderButton=screen.getByRole("button",{name:"Open folder",exact:true});
 expect(folderButton.textContent).toBe("");
 expect(folderButton.title).toBe("Open folder");
 expect(folderButton.nextElementSibling?.textContent).toBe(project.folder_path);
 await act(async()=>{await user.click(folderButton);});
 expect(api.openReferenceFile).toHaveBeenCalledWith(project.key);
 const before=vi.mocked(api.browseReferenceFiles).mock.calls.length;
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Refresh"}));});
 await waitFor(()=>expect(vi.mocked(api.browseReferenceFiles).mock.calls.length).toBeGreaterThan(before));
});
it("searches filenames across projects and supports type filtering", async () => {
 const user=userEvent.setup(); render(<ReferenceLibraryPage/>);
 await screen.findByRole("button",{name:"温升记录.xlsx"});
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[project],files:[{key:project.key,title:project.title,number:project.number,name:file.name,relative_path:file.relative_path,directory:"Records",kind:"record"}],total:1,warnings:[]});
 const scans=vi.mocked(archive.refreshArchive).mock.calls.length;
 await user.type(screen.getByLabelText("Search project materials"),"PwrBlade 温升");
 expect(archive.refreshArchive).toHaveBeenCalledTimes(scans);
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Search",exact:true}));});
 await waitFor(()=>expect(api.searchReferenceLibrary).toHaveBeenCalledWith("PwrBlade 温升","all","all",project.key,0,expect.any(AbortSignal)));
 await waitFor(()=>expect(archive.refreshArchive).toHaveBeenCalledTimes(scans+1));
 await act(async()=>{await user.selectOptions(screen.getByLabelText("Material type"),"record");});
 await waitFor(()=>expect(api.searchReferenceLibrary).toHaveBeenCalledWith("PwrBlade 温升","all","record",project.key,0,expect.any(AbortSignal)));
});
it("accepts Enter even when the previous index query is still loading",async()=>{
 const user=userEvent.setup();
 vi.mocked(api.searchReferenceLibrary).mockImplementation(async q=>q==="latest"
   ? {projects:[],files:[],total:0,warnings:[]} : new Promise(()=>{}));
 render(<ReferenceLibraryPage/>);
 const input=screen.getByRole("textbox",{name:"Search project materials"});
 await user.type(input,"latest{Enter}");
 expect(await screen.findByText("No matching project materials.")).toBeTruthy();
 expect(archive.refreshArchive).toHaveBeenCalledTimes(2);
});
it("omits missing folders from ordinary browsing, saved selection and search", async () => {
 const user=userEvent.setup();
 const missing={...project,key:"project:missing",project_id:"missing",number:"OLD-MISSING",folder_path:"D:/missing",available:false};
 runtimeSessionStorage.setItem("reference-search",JSON.stringify({project:missing.key}));
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[missing,project],files:[],total:0,warnings:[]});
 render(<ReferenceLibraryPage/>);
 await screen.findByRole("button",{name:"温升记录.xlsx"});
 expect(screen.queryByText("OLD-MISSING")).toBeNull();
 expect(screen.queryByText(/material location unavailable/i)).toBeNull();
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[missing],files:[],total:0,warnings:[]});
 await user.type(screen.getByLabelText("Search project materials"),missing.number);
 await user.click(screen.getByRole("button",{name:"Search",exact:true}));
 expect(await screen.findByText("No matching project materials.")).toBeTruthy();
 expect(screen.queryByText("D:/missing")).toBeNull();
});
it.each([true,false])("opens a stale direct link inline and retries that location (record returned: %s)",async(retained)=>{
 const user=userEvent.setup();
 const missing={...project,key:"archive:old",project_id:null,folder_path:"D:/missing",available:false};
 window.history.replaceState(null,"","/reference?entry=archive:old");
 vi.mocked(api.searchReferenceLibrary).mockImplementation(async(_query,_source,_kind,key)=>({projects:key===missing.key?(retained?[missing]:[]):[project],files:[],total:0,warnings:[]}));
 render(<ReferenceLibraryPage/>);
 const refresh=await screen.findByRole("button",{name:"Refresh materials"});
 expect(screen.queryByRole("button",{name:"Materials information"})).toBeNull();
 const count=vi.mocked(archive.refreshArchive).mock.calls.length;
 await waitFor(()=>expect(refresh).toHaveProperty("disabled",false));
 await user.click(refresh);
 await waitFor(()=>expect(archive.refreshArchive).toHaveBeenCalledTimes(count+1));
 expect(api.browseReferenceFiles).not.toHaveBeenCalled();
});
it("offers one root-offline message with a scan retry and a Settings action",async()=>{
 const user=userEvent.setup(),settings=vi.fn();
 vi.mocked(archive.getArchiveJob).mockResolvedValue({status:"done",result:{available:false,root_path:"D:/offline-library",warnings:["Materials library folder is unavailable. Check its connection in Settings."]}});
 render(<ReferenceLibraryPage onOpenSettings={settings}/>);
 expect(await screen.findByRole("alert")).toHaveProperty("textContent",expect.stringContaining("D:/offline-library"));
 expect(screen.getAllByText(/Materials library folder is unavailable/)).toHaveLength(1);
 await user.click(screen.getByRole("button",{name:"Open Settings"}));
 expect(settings).toHaveBeenCalledOnce();
 vi.mocked(archive.getArchiveJob).mockResolvedValue({status:"done",result:{available:true,warnings:[]}});
 await user.click(screen.getByRole("button",{name:"Retry"}));
 await waitFor(()=>expect(archive.refreshArchive).toHaveBeenCalledTimes(2));
 await waitFor(()=>expect(screen.queryByRole("alert")).toBeNull());
});
it("preserves actionable scan warnings and search failures",async()=>{
 const user=userEvent.setup();
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[project],files:[],total:0,warnings:["Search incomplete: scan limit reached"]});
 render(<ReferenceLibraryPage/>);
 expect(await screen.findByText("Search incomplete: scan limit reached")).toBeTruthy();
 vi.mocked(api.searchReferenceLibrary).mockRejectedValue(new Error("Could not load materials."));
 await user.click(screen.getByRole("button",{name:"Refresh"}));
 expect(await screen.findByRole("alert")).toHaveProperty("textContent",expect.stringContaining("Could not load materials."));
 expect(screen.getByRole("button",{name:"Retry"})).toBeTruthy();
});
it("does not list projects with no associated materials",async()=>{
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[{...project,folder_path:"",available:false}],files:[],total:0,warnings:[]});
 render(<ReferenceLibraryPage/>);
 expect(await screen.findByText(/No materials to show/)).toBeTruthy();
 expect(screen.queryByRole("button",{name:/DL-2026-08-079/})).toBeNull();
 expect(screen.queryByRole("alert")).toBeNull();
});

it("keeps an exact member entry when a project with the same member id has another root",async()=>{
 window.history.replaceState(null,"","/reference?entry=member:m1");
 const native={...project,member_id:"m1"};
 const member={...project,key:"member:m1",member_id:"m1",title:"Received originals",source:"received",folder_path:"D:/separate-copy"};
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[native,member],files:[],total:0,warnings:[]});
 render(<ReferenceLibraryPage/>);
 expect(await screen.findByText("D:/separate-copy")).toBeTruthy();
 await waitFor(()=>expect(api.browseReferenceFiles).toHaveBeenCalledWith("member:m1","",expect.any(AbortSignal)));
 expect(getReportShortcuts).not.toHaveBeenCalled();
});

it("keeps incomplete receipts visible and allows search while a scan cancellation is pending",async()=>{
 const user=userEvent.setup();
 vi.mocked(archive.getArchiveJob).mockResolvedValue({status:"cancellation_requested"});
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[{...project,key:"archive:pending",project_id:null,available:false,operation_id:"pending",intake_status:"incomplete"}],files:[],total:0,warnings:[]});
 const view=render(<ReferenceLibraryPage/>);
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
 const view=render(<ReferenceLibraryPage/>);
 await screen.findByRole("button",{name:"温升记录.xlsx"});
 const receive=screen.getByRole("button",{name:"Receive materials"});await user.click(receive);await user.click(receive);
 expect(receive).toHaveProperty("disabled",true);expect(archive.pickReceiptFolder).toHaveBeenCalledOnce();
 expect(screen.queryByRole("dialog")).toBeNull();
 await user.type(screen.getByRole("textbox",{name:"Search project materials"}),"record");
 await user.click(screen.getByRole("button",{name:"Search",exact:true}));
 await waitFor(()=>expect(api.searchReferenceLibrary).toHaveBeenCalledWith("record","all","all","",0,expect.any(AbortSignal)));
 view.unmount();await act(async()=>choose("C:/late"));expect(archive.startArchivePreview).not.toHaveBeenCalled();
});

it("opens the containing folder directly without a Workbench, a menu or a copy destination",async()=>{
 const user=userEvent.setup();render(<ReferenceLibraryPage/>);
 await user.click(await screen.findByRole("button",{name:"Open containing folder for "+file.name}));
 expect(api.openReferenceFile).toHaveBeenCalledWith(project.key,file.relative_path,true);
 expect(screen.queryByRole("button",{name:/Copy to current project|Open workbench|Actions for/})).toBeNull();
 expect(getReportShortcuts).not.toHaveBeenCalled();
});
it("shows an empty ordinary list without suggesting repair of individual missing locations",async()=>{
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[{...project,folder_path:"D:/offline",available:false}],files:[],total:0,warnings:[]});
 render(<ReferenceLibraryPage/>);
 expect(await screen.findByText(/No materials to show/)).toBeTruthy();
 expect(screen.queryByText(/D:\/offline/)).toBeNull();
 expect(screen.queryByRole("button",{name:/View location/})).toBeNull();
});

it("expands sibling folders in place and clears a hidden file selection",async()=>{
 const user=userEvent.setup();
 const folder=(name:string)=>({...file,name,relative_path:name,is_directory:true});
 vi.mocked(api.browseReferenceFiles).mockImplementation(async(key,dir="")=>({
  key,root:project.folder_path,current_directory:dir,location_state:"available",warnings:[],
  items:dir==="Records"?[file]:dir==="Photos"?[]:[folder("Records"),folder("Photos")]
 }));
 render(<ReferenceLibraryPage/>);
 const records=await screen.findByRole("button",{name:"Records",expanded:false});
 expect(screen.queryByRole("columnheader",{name:/Modified|Type/})).toBeNull();
 expect(screen.queryByText("All materials")).toBeNull();
 expect(vi.mocked(api.browseReferenceFiles).mock.calls.some(call=>call[1]==="Records")).toBeFalsy();
 await user.click(records);
 await user.click(await screen.findByRole("button",{name:file.name}));
 await user.click(screen.getByRole("button",{name:"Photos",expanded:false}));
 expect(await screen.findByText("This folder is empty.")).toBeTruthy();
 expect(screen.getByRole("button",{name:file.name,pressed:true})).toBeTruthy();
 await user.click(screen.getByRole("button",{name:"Records",expanded:true}));
 expect(screen.queryByRole("button",{name:file.name})).toBeNull();
 expect(screen.getByRole("button",{name:"Photos",expanded:true})).toBeTruthy();
 expect(screen.queryByRole("button",{name:"Open containing folder"})).toBeNull();
});

it("pages the two project columns and keeps the file pane on the selected project", async () => {
 const rows=Array.from({length:43}, (_, index) => ({
  ...project, key:"project:"+index, number:"ID-"+index, title:"Sample "+index, folder_path:"D:/sample/"+index
 }));
 window.history.replaceState(null,"","/reference?entry=project:25");
 vi.mocked(api.searchReferenceLibrary).mockImplementation(async query => ({
  projects:query ? [rows[7]] : rows, files:[], total:0, warnings:[]
 }));
 const user=userEvent.setup();
 render(<ReferenceLibraryPage/>);
 const table=within(await screen.findByRole("table",{name:"Project materials"}));
 expect(table.getAllByRole("columnheader").map(cell=>cell.textContent)).toEqual(["Project ID","Sample Description"]);
 await waitFor(()=>expect(screen.getByText("Page 2 / 3")).toBeTruthy());
 expect(table.getAllByRole("row")).toHaveLength(21);
 expect(table.getByRole("button",{name:"ID-25 Sample 25",pressed:true})).toBeTruthy();
 await user.click(screen.getByRole("button",{name:"Next",exact:true}));
 expect(table.getAllByRole("row")).toHaveLength(4);
 expect(screen.getByText("D:/sample/40")).toBeTruthy();
 expect(screen.getByRole("button",{name:"Next",exact:true})).toHaveProperty("disabled",true);
 await user.click(table.getByText("Sample 42"));
 expect(screen.getByText("D:/sample/42")).toBeTruthy();
 await user.click(screen.getByRole("button",{name:"Prev",exact:true}));
 expect(screen.getByText("D:/sample/20")).toBeTruthy();
 await user.type(screen.getByLabelText("Search project materials"),"Sample 7");
 await user.click(screen.getByRole("button",{name:"Search",exact:true}));
 await waitFor(()=>expect(table.getAllByRole("row")).toHaveLength(2));
 expect(screen.getByText("Page 1 / 1")).toBeTruthy();
 expect(screen.getByRole("button",{name:"Prev",exact:true})).toHaveProperty("disabled",true);
 expect(screen.getByText("D:/sample/7")).toBeTruthy();
});
