import { act, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import * as api from "../../api/existingProjects";
import { ExistingProjectsPanel } from "./ExistingProjectsPanel";
import { ProjectListPage } from "../../pages/ProjectListPage";
import { getProjectLifecycle, listProjectRegistryRows, type ProjectRegistryRow, type ProjectLifecycleResponse } from "../../api/client";
import * as registry from "../../api/projectRegistryManagement";
vi.mock("../../api/existingProjects", () => ({scanExistingProjects:vi.fn(),previewExistingProject:vi.fn(),registerExistingProject:vi.fn(),listExistingLocations:vi.fn(),listExistingFiles:vi.fn(),existingFileDownloadUrl:vi.fn(),previewExistingRelocation:vi.fn(),relocateExistingLocation:vi.fn()}));
vi.mock("../../api/client",async importOriginal=>({...await importOriginal<typeof import("../../api/client")>(),getProjectLifecycle:vi.fn(),listProjectRegistryRows:vi.fn()}));
vi.mock("../../api/projectRegistryManagement",()=>({listManagedProjects:vi.fn(),previewProjectRegistryAction:vi.fn(),moveProjectToTrash:vi.fn(),restoreManagedProject:vi.fn(),previewRegistryBatch:vi.fn(),moveRegistryBatch:vi.fn()}));
const source: api.ExistingSource = {path:"C:/test/sample",name:"Old sample",source_kind:"manual",source_project_id:null,source_number:null,
  source_number_origin:"none",source_fingerprint:"source",root_identity:"root",manifest_error:null};
const preview: api.ExistingPreview = {...source,token:"reviewed",conflicts:[],targets:[],existing:null,suggested_number:"LEG-001",notice:"Files only; no Matrix confirmation."};
beforeEach(() => {vi.clearAllMocks();window.sessionStorage.clear(); vi.mocked(api.listExistingLocations).mockResolvedValue([]);vi.mocked(api.listExistingFiles).mockResolvedValue({relative_path:"",entries:[],diagnostics:[]});
  vi.mocked(api.scanExistingProjects).mockResolvedValue({candidates:[source],diagnostics:[]});vi.mocked(api.previewExistingProject).mockResolvedValue(preview);});
async function setup() {
  const user=userEvent.setup(); const onChanged=vi.fn();render(<ExistingProjectsPanel onOpenProject={vi.fn()} onChanged={onChanged}/>);
  await user.click(screen.getByRole("button",{name:"Manage existing folders"}));
  await user.type(screen.getByRole("textbox",{name:"Scan roots"}),"C:/test");
  await user.click(screen.getByRole("button",{name:"Scan folders"}));
  await user.click(await screen.findByRole("button",{name:"Review Old sample"}));
  await screen.findByRole("dialog"); return {user,onChanged};
}
describe("existing folder intake", () => {
  it("cancel keeps roots/candidates and never registers files",async()=>{
    const {user}=await setup();await user.click(screen.getByRole("button",{name:"Cancel review"}));
    expect(api.registerExistingProject).not.toHaveBeenCalled();expect(screen.getByRole("textbox",{name:"Scan roots"})).toHaveProperty("value","C:/test");
    expect(screen.getByRole("button",{name:"Review Old sample"})).toBeTruthy();
  });
  it("blocks double submit and retains the decision after failure for fresh preview",async()=>{
    const {user}=await setup();vi.mocked(api.registerExistingProject).mockRejectedValueOnce(new Error("Source changed; review again"));
    await user.dblClick(screen.getByRole("button",{name:"Confirm association"}));
    await waitFor(()=>expect(api.registerExistingProject).toHaveBeenCalledTimes(1));
    expect(await screen.findByRole("alert")).toBeTruthy();
    expect(screen.getByRole("textbox",{name:"Local management number"})).toHaveProperty("value","LEG-001");
    await user.click(screen.getByRole("button",{name:"Refresh review"}));
    await waitFor(()=>expect(api.previewExistingProject).toHaveBeenCalledTimes(2));
    expect(screen.getByRole("button",{name:"Confirm association"})).toHaveProperty("disabled",false);
  });
  it("a failed refresh keeps confirmation blocked and preserves the operator decision",async()=>{
    const {user}=await setup();
    await user.clear(screen.getByRole("textbox",{name:"Local management number"}));
    await user.type(screen.getByRole("textbox",{name:"Local management number"}),"MY-CHOICE");
    vi.mocked(api.previewExistingProject).mockRejectedValueOnce(new Error("Connection unavailable"));
    await user.click(screen.getByRole("button",{name:"Refresh review"}));
    expect(await screen.findByRole("alert")).toBeTruthy();
    expect(screen.getByRole("button",{name:"Confirm association"})).toHaveProperty("disabled",true);
    expect(screen.getByRole("textbox",{name:"Local management number"})).toHaveProperty("value","MY-CHOICE");
    await user.click(screen.getByRole("button",{name:"Refresh review"}));
    await waitFor(()=>expect(screen.getByRole("button",{name:"Confirm association"})).toHaveProperty("disabled",false));
  });
  it("a late initial folder list cannot erase a newly registered association",async()=>{
    let finish!:(value:api.ExistingLocation[])=>void;
    vi.mocked(api.listExistingLocations).mockReturnValueOnce(new Promise(resolve=>{finish=resolve;}));
    const {user,onChanged}=await setup();
    vi.mocked(api.registerExistingProject).mockResolvedValueOnce({location_id:"saved",project_id:"project",path:source.path,
      management_number:"LEG-001",source_number:null,source_project_id:null,source_kind:"manual",registry_state:"active",revision:0,product_name:"Old sample",registered_at:"now"});
    await user.click(screen.getByRole("button",{name:"Confirm association"}));
    await waitFor(()=>expect(onChanged).toHaveBeenCalledOnce());
    await act(async()=>{finish([]);});
    expect(screen.getByText("LEG-001")).toBeTruthy();
    expect(screen.getByRole("button",{name:"Open project"})).toBeTruthy();
  });
  it("shows the registered display identity beside its distinct local management number for conflict review",async()=>{
    const target:api.ExistingTarget={project_id:"local-record",display_project_id:"DL-2026-01-009",number:"LEGACY-NUMBER",name:"Same sample",state:"active",revision:1};
    vi.mocked(api.previewExistingProject).mockResolvedValueOnce({...preview,conflicts:[target],targets:[target]});
    const {user}=await setup();
    expect(screen.getByText(/DL-2026-01-009 · Management number: LEGACY-NUMBER/)).toBeTruthy();
    await user.selectOptions(screen.getByRole("combobox",{name:"Intake decision"}),"link");
    expect(screen.getByRole("option",{name:/DL-2026-01-009 · Management: LEGACY-NUMBER.*local-record/})).toBeTruthy();
  });
  it("a registry revision invalidates an in-flight review instead of letting it unlock old confirmation",async()=>{
    let finish!:(value:api.ExistingPreview)=>void;
    const user=userEvent.setup();
    const view=render(<ExistingProjectsPanel revision={0} onOpenProject={vi.fn()} onChanged={vi.fn()}/>);
    await user.click(screen.getByRole("button",{name:"Manage existing folders"}));
    await user.type(screen.getByRole("textbox",{name:"Scan roots"}),"C:/test");
    await user.click(screen.getByRole("button",{name:"Scan folders"}));
    await user.click(await screen.findByRole("button",{name:"Review Old sample"}));
    await screen.findByRole("dialog");
    vi.mocked(api.previewExistingProject).mockReturnValueOnce(new Promise(resolve=>{finish=resolve;}));
    await user.click(screen.getByRole("button",{name:"Refresh review"}));
    view.rerender(<ExistingProjectsPanel revision={1} onOpenProject={vi.fn()} onChanged={vi.fn()}/>);
    await act(async()=>{finish(preview);});
    expect(screen.getByRole("button",{name:"Confirm association"})).toHaveProperty("disabled",true);
    expect(api.registerExistingProject).not.toHaveBeenCalled();
  });
});

async function openManagedRegistry() {
  let state:registry.ProjectRegistryLocation="active";
  const location:api.ExistingLocation={location_id:"linked",project_id:"record",path:source.path,management_number:"LEG-001",source_number:null,source_project_id:null,source_kind:"manual",registry_state:"active",revision:0,product_name:"Old sample",registered_at:"now"};
  const entry=():registry.ProjectRegistryEntry=>({project_id:"record",display_project_id:"TMP-RECORD",sample_description:"Old sample",test_item:null,requestor:"Lab",created_on:null,lifecycle_state:"active",close_reason_label:null,registry_state:state,registry_revision:state==="active"?0:1,changed_at:null,reason:null});
  vi.mocked(api.listExistingLocations).mockImplementation(async()=>[{...location,registry_state:state}]);
  vi.mocked(listProjectRegistryRows).mockImplementation(async()=>state==="active"?[{project_id:"record",display_project_id:"TMP-RECORD",display_project_id_kind:"temporary",has_registered_ltr:false,requestor:"Lab",status:"active",progress:0} as ProjectRegistryRow]:[]);
  vi.mocked(getProjectLifecycle).mockResolvedValue({project_id:"record",lifecycle_state:"active",registry_state:"active",status:"active",readonly:false,allowed_actions:["close"],warnings:[]} as ProjectLifecycleResponse);
  vi.mocked(registry.listManagedProjects).mockImplementation(async place=>state===place?[entry()]:[]);
  vi.mocked(registry.previewRegistryBatch).mockImplementation(async request=>({...request,token:"batch",items:[],blockers:[]}));
  vi.mocked(registry.moveRegistryBatch).mockImplementation(async request=>{state=request.action==="trash"?"trash":request.destination;return [entry()];});
  vi.mocked(registry.previewProjectRegistryAction).mockImplementation(async(_id,action)=>({project:entry(),action,token:"single",conflicts:[],blockers:[],retained_data:[],warnings:[]}));
  vi.mocked(registry.moveProjectToTrash).mockImplementation(async()=>{state="trash";return entry();});
  vi.mocked(registry.restoreManagedProject).mockImplementation(async(_id,request)=>{state=request.destination;return entry();});
  const user=userEvent.setup();render(<ProjectListPage onOpenProject={vi.fn()}/>);
  await user.selectOptions(screen.getByRole("combobox",{name:"Project view"}),"all");
  await user.click(screen.getByRole("button",{name:"Manage existing folders"}));
  await user.type(screen.getByRole("textbox",{name:"Scan roots"}),"C:/keep-scan-root");
  await user.selectOptions(screen.getByRole("combobox",{name:"Scan depth"}),"2");
  await user.click(screen.getByRole("button",{name:"Scan folders"}));
  await user.click(await screen.findByRole("button",{name:"Browse files / review location"}));
  expect(await screen.findByText("Moved or replaced folder? Review its location")).toBeTruthy();
  return user;
}

async function expectManagedState(state:"active"|"trash") {
  await waitFor(()=>expect(screen.getByText("LEG-001").closest("li")?.textContent).toContain(state));
  expect(screen.getByRole("textbox",{name:"Scan roots"})).toHaveProperty("value","C:/keep-scan-root");
  expect(screen.getByRole("combobox",{name:"Scan depth"})).toHaveProperty("value","2");
  expect(screen.getByRole("button",{name:"Review Old sample"})).toBeTruthy();
  if(state==="trash")expect(screen.queryByText("Moved or replaced folder? Review its location")).toBeNull();
  else expect(screen.getByText("Moved or replaced folder? Review its location")).toBeTruthy();
}

describe("shared registry changes update existing folders",()=>{
  it("batch recycle and restore refresh the expanded list and open files without discarding scan inputs",async()=>{
    const user=await openManagedRegistry();
    await user.click(screen.getByRole("button",{name:"Batch record management"}));
    await user.click(screen.getByRole("checkbox",{name:"Select TMP-RECORD"}));
    await user.type(screen.getByRole("textbox",{name:"Removal reason"}),"Old experiment");
    await user.click(screen.getByRole("button",{name:"Preview selected records"}));
    await user.click(await screen.findByRole("button",{name:"Confirm batch move"}));
    await expectManagedState("trash");
    await user.click(screen.getByRole("button",{name:"Trash"}));
    await user.click(await screen.findByRole("button",{name:"Batch record management"}));
    await user.click(screen.getByRole("checkbox",{name:"Select TMP-RECORD"}));
    await user.click(screen.getByRole("button",{name:"Preview selected records"}));
    await user.click(await screen.findByRole("button",{name:"Confirm batch move"}));
    await expectManagedState("active");
  });
  it("single recycle and Undo restore share the same folder and files refresh",async()=>{
    const user=await openManagedRegistry();
    await user.click(await screen.findByRole("button",{name:"Delete project TMP-RECORD"}));
    const dialog=within(await screen.findByRole("dialog"));
    await user.selectOptions(dialog.getByLabelText("Deletion reason"),"Created by mistake");
    await user.click(dialog.getByRole("button",{name:"Move to recycle bin"}));
    await expectManagedState("trash");
    await user.click(screen.getByRole("button",{name:"Undo"}));
    await user.click(await screen.findByRole("button",{name:"Restore to projects"}));
    await expectManagedState("active");
  });
  it("a delayed relocation response cannot cancel the newer recycle-bin status refresh",async()=>{
    const user=await openManagedRegistry();
    const location:api.ExistingLocation={location_id:"linked",project_id:"record",path:source.path,management_number:"LEG-001",source_number:null,source_project_id:null,source_kind:"manual",registry_state:"active",revision:0,product_name:"Old sample",registered_at:"now"};
    vi.mocked(api.previewExistingRelocation).mockResolvedValue({location,source:{...source,path:"C:/moved"},blockers:[],token:"move"});
    let finishMove!:(value:api.ExistingLocation)=>void;
    let finishStatus!:(value:api.ExistingLocation[])=>void;
    vi.mocked(api.relocateExistingLocation).mockReturnValueOnce(new Promise(resolve=>{finishMove=resolve;}));
    await user.click(screen.getByText("Moved or replaced folder? Review its location"));
    await user.type(screen.getByRole("textbox",{name:"New folder location"}),"C:/moved");
    await user.click(screen.getByRole("button",{name:"Review relocation"}));
    await user.click(await screen.findByRole("button",{name:"Confirm relocation"}));
    vi.mocked(api.listExistingLocations).mockReturnValueOnce(new Promise(resolve=>{finishStatus=resolve;}));
    await user.click(screen.getByRole("button",{name:"Batch record management"}));
    await user.click(screen.getByRole("checkbox",{name:"Select TMP-RECORD"}));
    await user.type(screen.getByRole("textbox",{name:"Removal reason"}),"Old experiment");
    await user.click(screen.getByRole("button",{name:"Preview selected records"}));
    await user.click(await screen.findByRole("button",{name:"Confirm batch move"}));
    await waitFor(()=>expect(finishStatus).toBeTypeOf("function"));
    await act(async()=>{finishMove({...location,path:"C:/moved",revision:1});});
    await act(async()=>{finishStatus([{...location,path:"C:/moved",revision:1,registry_state:"trash"}]);});
    await expectManagedState("trash");
  });
  it("failed status refresh keeps files readable but relocation disabled until a successful retry",async()=>{
    const user=await openManagedRegistry();
    await user.click(screen.getByText("Moved or replaced folder? Review its location"));
    await user.type(screen.getByRole("textbox",{name:"New folder location"}),"C:/keep-location-choice");
    vi.mocked(api.listExistingLocations).mockRejectedValueOnce(new Error("Connection lost"));
    await user.click(screen.getByRole("button",{name:"Batch record management"}));
    await user.click(screen.getByRole("checkbox",{name:"Select TMP-RECORD"}));
    await user.type(screen.getByRole("textbox",{name:"Removal reason"}),"Old experiment");
    await user.click(screen.getByRole("button",{name:"Preview selected records"}));
    await user.click(await screen.findByRole("button",{name:"Confirm batch move"}));
    expect(await screen.findByRole("alert")).toBeTruthy();
    expect(screen.getByRole("button",{name:"Review relocation"})).toHaveProperty("disabled",true);
    expect(screen.getByRole("textbox",{name:"New folder location"})).toHaveProperty("value","C:/keep-location-choice");
    expect(screen.getByRole("button",{name:"Close files"})).toHaveProperty("disabled",false);
    expect(screen.getByText("No visible files in this folder.")).toBeTruthy();
    await user.click(screen.getByRole("button",{name:"Retry folder status"}));
    await expectManagedState("trash");
  });
});
