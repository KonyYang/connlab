import { act, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import * as api from "../../api/existingProjects";
import { ExistingProjectsPanel } from "./ExistingProjectsPanel";
vi.mock("../../api/existingProjects", () => ({scanExistingProjects:vi.fn(),previewExistingProject:vi.fn(),registerExistingProject:vi.fn(),listExistingLocations:vi.fn()}));
const source: api.ExistingSource = {path:"C:/test/sample",name:"Old sample",source_kind:"manual",source_project_id:null,source_number:null,
  source_number_origin:"none",source_fingerprint:"source",root_identity:"root",manifest_error:null};
const preview: api.ExistingPreview = {...source,token:"reviewed",conflicts:[],targets:[],existing:null,suggested_number:"LEG-001",notice:"Files only; no Matrix confirmation."};
beforeEach(() => {vi.clearAllMocks(); vi.mocked(api.listExistingLocations).mockResolvedValue([]);
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
});
