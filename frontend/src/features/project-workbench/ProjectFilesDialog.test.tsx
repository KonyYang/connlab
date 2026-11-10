import { StrictMode, useState } from "react";
import { act, cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ProjectFilesDialog } from "./ProjectFilesDialog";
import { previewProjectFiles, startProjectFiles, getProjectFilesOperation, resumeProjectFilesOperation,
  type ProjectFilesPreview, type ProjectFileOperation } from "../../api/client";
vi.mock("../../api/client", () => ({previewProjectFiles: vi.fn(), startProjectFiles: vi.fn(), getProjectFilesOperation: vi.fn(), resumeProjectFilesOperation: vi.fn()}));
const previewMock = vi.mocked(previewProjectFiles);
const startMock = vi.mocked(startProjectFiles);
const getMock = vi.mocked(getProjectFilesOperation);
const resumeMock = vi.mocked(resumeProjectFilesOperation);
function preview(): ProjectFilesPreview {
  return {project_id: "p1", workspace_token: "workspace-facts", status: "ready", blockers: [], warnings: [], operation: null, items: [
    {key: "fee_form", label: "Fee Form", target_path: "Fee/Fee.xlsx", status: "ready", default_action: "generate_missing", source_token: "fee-v1", message: null, warnings: []},
    {key: "customer_feedback_form", label: "Customer Feedback Form", target_path: "Feedback.docx", status: "exists", default_action: "skip", source_token: "feedback-v1", message: "Existing document retained", warnings: []},
    {key: "test_record", label: "Test Record", target_path: "Record.xlsx", status: "blocked", default_action: "skip", source_token: null, message: "Confirm the Matrix before generating this file.", warnings: []},
  ]};
}
function operation(overrides: Partial<ProjectFileOperation> = {}): ProjectFileOperation {
 return {project_id:"p1",operation_id:"operation-1",status:"queued",outcome:null,can_resume:false,message:null,warnings:[],items:[{key:"fee_form",label:"Fee Form",status:"pending",action:"generate_missing",outcome:null,message:null,target_path:"Fee/Fee.xlsx"}],...overrides};
}
beforeEach(() => { vi.resetAllMocks(); previewMock.mockResolvedValue(preview()); startMock.mockResolvedValue(operation()); getMock.mockResolvedValue(operation()); });
afterEach(() => {cleanup(); vi.useRealTimers();});
describe("project file review", () => {
 it("preselects only absent ready files and submits reviewed tokens with no paths", async () => {
  render(<ProjectFilesDialog projectId="p1" onClose={vi.fn()} />);
  await screen.findByRole("checkbox",{name:"Fee Form"});
  await waitFor(() => expect(screen.getByRole("checkbox",{name:"Fee Form"})).toHaveProperty("checked",true));
  expect(screen.getByRole("checkbox",{name:"Customer Feedback Form"})).toHaveProperty("checked",false);
  expect(screen.getByRole("checkbox",{name:"Test Record"})).toHaveProperty("disabled",true);
  expect(screen.getByText("Confirm the Matrix before generating this file.")).toBeTruthy();
  await userEvent.click(screen.getByRole("button",{name:"Generate selected files"}));
  expect(startMock).toHaveBeenCalledWith("p1", {request_id: expect.any(String), workspace_token:"workspace-facts", items:[
   {key:"fee_form",source_token:"fee-v1",action:"generate_missing"}, {key:"customer_feedback_form",source_token:"feedback-v1",action:"skip"}, {key:"test_record",source_token:null,action:"skip"}]});
  expect(screen.getByText("You can close this dialog. Generation continues in the background.")).toBeTruthy();
 });
 it("requires one batch confirmation before backup replacements and invalidates approval when selection changes", async () => {
  render(<ProjectFilesDialog projectId="p1" onClose={vi.fn()} />);
  const select = await screen.findByRole("combobox",{name:"Customer Feedback Form existing file action"});
  await userEvent.selectOptions(select,"replace_with_backup");
  await userEvent.click(screen.getByRole("button",{name:"Generate selected files"}));
  expect(startMock).not.toHaveBeenCalled();
  expect(screen.getByRole("region",{name:"Confirm replacements"})).toBeTruthy();
  await userEvent.click(screen.getByRole("checkbox",{name:"Fee Form"}));
  expect(screen.queryByRole("button",{name:"Confirm backup and generate"})).toBeNull();
  await userEvent.click(screen.getByRole("button",{name:"Generate selected files"}));
  await userEvent.click(screen.getByRole("button",{name:"Confirm backup and generate"}));
  expect(startMock.mock.calls[0][1].items).toContainEqual({key:"customer_feedback_form",source_token:"feedback-v1",action:"replace_with_backup"});
 });
 it("invalidates file readiness if the latest preview cannot refresh", async () => {
  render(<ProjectFilesDialog projectId="p1" onClose={vi.fn()} />);
  await screen.findByRole("checkbox",{name:"Fee Form"});
  previewMock.mockRejectedValueOnce(new Error("D:/private/backend traceback"));
  await userEvent.click(screen.getByRole("button",{name:"Refresh files"}));
  await screen.findByRole("alert");
  expect(screen.getByRole("button",{name:"Generate selected files"})).toHaveProperty("disabled",true);
  expect(screen.queryByText(/D:\/private/)).toBeNull();
 });
 it("reopens saved running work without starting or resuming it", async () => {
  previewMock.mockResolvedValue({...preview(),operation:operation({status:"running"})});
  const close=vi.fn(); const view=render(<ProjectFilesDialog projectId="p1" onClose={close}/>);
  await screen.findByText("Generating files…");
  await userEvent.click(screen.getByRole("button",{name:"Close"})); expect(close).toHaveBeenCalledOnce();
  view.unmount(); render(<ProjectFilesDialog projectId="p1" onClose={close}/>);
  await screen.findByText("Generating files…");
  expect(previewMock).toHaveBeenCalledTimes(2); expect(startMock).not.toHaveBeenCalled(); expect(resumeMock).not.toHaveBeenCalled();
 });
 it("only resumes explicitly recoverable interrupted work", async () => {
  const saved=operation({status:"interrupted",can_resume:true});
  previewMock.mockResolvedValue({...preview(),operation:saved}); getMock.mockResolvedValue(saved); resumeMock.mockResolvedValue(operation({status:"running"}));
  render(<ProjectFilesDialog projectId="p1" onClose={vi.fn()}/>);
  await userEvent.click(await screen.findByRole("button",{name:"Resume saved operation"}));
  expect(resumeMock).toHaveBeenCalledWith("p1","operation-1"); expect(startMock).not.toHaveBeenCalled();
 });
 it("ignores late preview responses after switching projects", async () => {
  let finish!: (value:ProjectFilesPreview)=>void;
  previewMock.mockReturnValueOnce(new Promise(resolve => {finish=resolve;}));
  const view=render(<ProjectFilesDialog projectId="p1" onClose={vi.fn()}/>);
  previewMock.mockResolvedValue({...preview(),project_id:"p2",items:[]});
  view.rerender(<ProjectFilesDialog projectId="p2" onClose={vi.fn()}/>);
  await waitFor(()=>expect(previewMock).toHaveBeenCalledWith("p2"));
  await act(async()=>{finish(preview());});
  expect(screen.queryByRole("checkbox",{name:"Fee Form"})).toBeNull();
 });
 it("contains keyboard focus while loading and ready and allows Escape to dismiss", async () => {
  let finishPreview!: (value: ProjectFilesPreview) => void;
  previewMock.mockReturnValueOnce(new Promise(resolve => {finishPreview=resolve;}));
  const close=vi.fn(); render(<ProjectFilesDialog projectId="p1" onClose={close}/>);
  const dialog=screen.getByRole("dialog");
  const generate=within(dialog).getByRole("button",{name:"Generate selected files"});
  const closeButton=within(dialog).getByRole("button",{name:"Close"});
  expect(generate).toHaveProperty("disabled",true);
  expect(document.activeElement).toBe(closeButton);
  await userEvent.tab(); expect(document.activeElement).toBe(closeButton);
  await act(async () => {finishPreview(preview());});
  // File rows can appear before the default selection enables generation.
  await waitFor(() => expect(generate).toHaveProperty("disabled",false));
  generate.focus(); expect(document.activeElement).toBe(generate);
  await userEvent.tab(); expect(document.activeElement).toBe(screen.getByRole("checkbox",{name:"Fee Form"}));
  await userEvent.keyboard("{Escape}"); expect(close).toHaveBeenCalledOnce();
 });
 it("keeps focus inside after starting generation so Escape dismisses without another operation", async () => {
  const close=vi.fn(); render(<ProjectFilesDialog projectId="p1" onClose={close}/>);
  const dialog=screen.getByRole("dialog");
  const generate=within(dialog).getByRole("button",{name:"Generate selected files"});
  await waitFor(() => expect(generate).toHaveProperty("disabled",false));
  await userEvent.click(generate); await screen.findByText("Generating files…");
  expect(dialog.contains(document.activeElement)).toBe(true);
  expect(document.activeElement).toBe(within(dialog).getByRole("button",{name:"Close"}));
  await userEvent.keyboard("{Escape}"); expect(close).toHaveBeenCalledOnce();
  expect(startMock).toHaveBeenCalledOnce(); expect(resumeMock).not.toHaveBeenCalled();
 });
 it("hands focus to Close during a deferred refresh and preserves valid focus once ready", async () => {
  render(<ProjectFilesDialog projectId="p1" onClose={vi.fn()}/>);
  const dialog=screen.getByRole("dialog");
  const generate=within(dialog).getByRole("button",{name:"Generate selected files"});
  await waitFor(() => expect(generate).toHaveProperty("disabled",false));
  let finishPreview!: (value: ProjectFilesPreview) => void;
  previewMock.mockReturnValueOnce(new Promise(resolve => {finishPreview=resolve;}));
  await userEvent.click(within(dialog).getByRole("button",{name:"Refresh files"}));
  const closeButton=within(dialog).getByRole("button",{name:"Close"});
  expect(document.activeElement).toBe(closeButton);
  expect(closeButton).toHaveProperty("disabled",false);
  await userEvent.tab(); expect(document.activeElement).toBe(closeButton);
  await act(async () => {finishPreview({...preview()});});
  await waitFor(() => expect(generate).toHaveProperty("disabled",false));
  expect(document.activeElement).toBe(closeButton);
  expect(startMock).not.toHaveBeenCalled(); expect(resumeMock).not.toHaveBeenCalled();
 });
 it("returns focus to its opening control after dismissal in StrictMode", async () => {
  function Harness() {
    const [open,setOpen]=useState(false);
    return <><button type="button" onClick={() => setOpen(true)}>Open file review</button>
      {open ? <ProjectFilesDialog projectId="p1" onClose={() => setOpen(false)}/> : null}</>;
  }
  render(<StrictMode><Harness/></StrictMode>);
  const trigger=screen.getByRole("button",{name:"Open file review"});
  await userEvent.click(trigger);
  await waitFor(() => expect(screen.getByRole("button",{name:"Generate selected files"})).toHaveProperty("disabled",false));
  await userEvent.click(screen.getByRole("button",{name:"Close"}));
  expect(screen.queryByRole("dialog")).toBeNull(); expect(document.activeElement).toBe(trigger);
 });
 it("polls active work to a partial completion and reloads conditions without recovery", async () => {
  const completed=operation({status:"completed",outcome:"partial",items:[
   {key:"fee_form",label:"Fee Form",status:"completed",action:"generate_missing",outcome:"generated",message:null,target_path:"Fee/Fee.xlsx"},
   {key:"test_record",label:"Test Record",status:"failed",action:"generate_missing",outcome:null,message:"Close the output workbook and try again.",target_path:"Record.xlsx"}
  ]});
  previewMock.mockResolvedValueOnce({...preview(),operation:operation({status:"running"})});
  getMock.mockResolvedValue(completed); previewMock.mockResolvedValue({...preview(),workspace_token:"fresh-after-batch",operation:completed});
  render(<ProjectFilesDialog projectId="p1" onClose={vi.fn()}/>);
  await screen.findByText("Batch completed with issues",{}, {timeout:3000});
  expect(screen.getByText("1 generated · 0 replaced · 0 skipped · 0 need input · 1 failed")).toBeTruthy();
  await waitFor(()=>expect(screen.getByRole("button",{name:"Generate selected files"})).toHaveProperty("disabled",false));
  expect(resumeMock).not.toHaveBeenCalled();expect(startMock).not.toHaveBeenCalled();
 });
 it("ignores a late start response after selecting a different project", async () => {
  let finish!:(value:ProjectFileOperation)=>void;
  startMock.mockReturnValueOnce(new Promise(resolve=>{finish=resolve;}));
  const view=render(<ProjectFilesDialog projectId="p1" onClose={vi.fn()}/>);
  await waitFor(()=>expect(screen.getByRole("button",{name:"Generate selected files"})).toHaveProperty("disabled",false));
  await userEvent.click(screen.getByRole("button",{name:"Generate selected files"}));
  previewMock.mockResolvedValue({...preview(),project_id:"p2",items:[]});
  view.rerender(<ProjectFilesDialog projectId="p2" onClose={vi.fn()}/>);
  await waitFor(()=>expect(previewMock).toHaveBeenCalledWith("p2"));
  await act(async()=>{finish(operation());});
  expect(screen.queryByRole("region",{name:"File generation progress"})).toBeNull();
  expect(screen.getByRole("button",{name:"Generate selected files"})).toHaveProperty("disabled",true);
 });
 it("requires fresh review after file facts change during replacement confirmation", async () => {
  render(<ProjectFilesDialog projectId="p1" onClose={vi.fn()}/>);
  await userEvent.selectOptions(await screen.findByRole("combobox",{name:"Customer Feedback Form existing file action"}),"replace_with_backup");
  await userEvent.click(screen.getByRole("button",{name:"Generate selected files"}));
  previewMock.mockResolvedValue({...preview(),workspace_token:"changed-target",items:preview().items.map(item=>({...item,source_token:item.source_token ? "new-source-fact" : null}))});
  await userEvent.click(screen.getByRole("button",{name:"Refresh files"}));
  await waitFor(()=>expect(screen.getByRole("checkbox",{name:"Customer Feedback Form"})).toHaveProperty("checked",false));
  expect(screen.queryByRole("button",{name:"Confirm backup and generate"})).toBeNull();expect(startMock).not.toHaveBeenCalled();
 });
 it("does not offer recovery for an operation that cannot resume", async () => {
  previewMock.mockResolvedValue({...preview(),operation:operation({status:"interrupted",can_resume:false})});
  render(<ProjectFilesDialog projectId="p1" onClose={vi.fn()}/>);
  const button=await screen.findByRole("button",{name:"Resume saved operation"});expect(button).toHaveProperty("disabled",true);
  await userEvent.click(button);expect(resumeMock).not.toHaveBeenCalled();expect(startMock).not.toHaveBeenCalled();
 });

 it("uses a new batch request after reconnecting to a completed failed attempt", async () => {
  const completed=operation({status:"completed",outcome:"partial",items:[{key:"fee_form",label:"Fee Form",status:"failed",action:"generate_missing",outcome:null,message:"Close the workbook and try again.",target_path:"Fee/Fee.xlsx"}]});
  startMock.mockRejectedValueOnce(new Error("Lost acknowledgement"));
  render(<ProjectFilesDialog projectId="p1" onClose={vi.fn()}/>);
  await waitFor(()=>expect(screen.getByRole("button",{name:"Generate selected files"})).toHaveProperty("disabled",false));
  await userEvent.click(screen.getByRole("button",{name:"Generate selected files"}));
  await screen.findByRole("alert");
  const firstRequest=startMock.mock.calls[0][1].request_id;
  previewMock.mockResolvedValue({...preview(),operation:completed});
  await userEvent.click(screen.getByRole("button",{name:"Refresh files"}));
  await screen.findByText("Batch completed with issues");
  await waitFor(()=>expect(screen.getByRole("button",{name:"Generate selected files"})).toHaveProperty("disabled",false));
  await userEvent.click(screen.getByRole("button",{name:"Generate selected files"}));
  expect(startMock.mock.calls[1][1].request_id).not.toBe(firstRequest);
 });

});
