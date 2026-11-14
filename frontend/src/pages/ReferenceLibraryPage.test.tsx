import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, it, vi } from "vitest";
import { ReferenceLibraryPage } from "./ReferenceLibraryPage";
import * as api from "../api/referenceLibrary";
import { getLegacyProject } from "../api/legacyProjects";
vi.mock("../api/referenceLibrary", () => ({ searchReferenceLibrary: vi.fn(), openReferenceFile: vi.fn(), browseReferenceFiles: vi.fn() }));
vi.mock("../api/legacyProjects", () => ({ getLegacyProject: vi.fn(), changeLegacyProjectLocation: vi.fn() }));
const project = { key: "project:p1", project_id: "p1", member_id: null, number: "DL-2026-08-079", title: "PwrBlade", test_item: "温升", source: "connlab", available: true, folder_path: "D:/isolated" };
const file = { name: "温升记录.xlsx", relative_path: "Records/温升记录.xlsx", is_directory: false, modified_at: "2026-11-14T01:00:00Z", extension: ".xlsx" };
beforeEach(() => {
 window.history.replaceState(null,"","/reference"); sessionStorage.clear(); vi.resetAllMocks();
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
it("keeps unavailable entries, aggregates issues and uses ordinary linked details", async () => {
 const user=userEvent.setup(); const old=vi.fn();
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[{...project,key:"linked:old",project_id:null,source:"linked",available:false}],files:[],total:0,warnings:["Search incomplete: original location unavailable"]});
 render(<ReferenceLibraryPage onOpenProject={vi.fn()} onOpenLinked={old}/>);
 await screen.findByText("Original material location is unavailable. The entry is retained.");
 expect(screen.getByText("1 material location(s) unavailable")).toBeTruthy();
 expect(screen.getByRole("button",{name:"Open folder",exact:true}).hasAttribute("disabled")).toBe(true);
 await act(async()=>{await user.click(screen.getByRole("button",{name:"Materials information"}));});
 expect(screen.getByRole("dialog")).toBeTruthy(); expect(old).not.toHaveBeenCalled();
 expect(screen.queryByText("Prepare to Take")).toBeNull();
});
it("distinguishes unassociated materials from a lost location", async () => {
 vi.mocked(api.searchReferenceLibrary).mockResolvedValue({projects:[{...project,folder_path:"",available:false}],files:[],total:0,warnings:[]});
 render(<ReferenceLibraryPage onOpenProject={vi.fn()}/>);
 await screen.findByRole("button",{name:/DL-2026-08-079.*No materials linked yet/});
 expect(screen.queryByText("Original material location is unavailable. The entry is retained.")).toBeNull();
 expect(screen.queryByRole("alert")).toBeNull();
});
