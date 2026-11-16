import {StrictMode} from "react";
import {act,render,screen,waitFor} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {beforeEach,expect,it,vi} from "vitest";
import {ReceiveMaterials} from "./ReceiveMaterials";
import * as api from "../../api/materialReceipts";
vi.mock("../../api/materialReceipts",()=>({pickReceiptFolder:vi.fn(),startArchivePreview:vi.fn(),confirmArchive:vi.fn(),getArchiveJob:vi.fn(),cancelArchiveJob:vi.fn(),getArchiveOperation:vi.fn(),retryArchive:vi.fn()}));
const plan={status:"ready" as const,source_path:"C:/Old Connector",target_path:"D:/Library/Old Connector",plan_id:"plan",fingerprint:"hash",batch_id:"operation",file_count:1};
const completed={batch_id:"operation",status:"completed",target_key:"archive:one",target_path:plan.target_path,items:[],counts:{copied:1},directory_counts:{}};
beforeEach(()=>{vi.resetAllMocks();sessionStorage.clear();vi.mocked(api.pickReceiptFolder).mockResolvedValue(plan.source_path);vi.mocked(api.startArchivePreview).mockResolvedValue({job_id:"preview"});vi.mocked(api.confirmArchive).mockResolvedValue({job_id:"copy"});vi.mocked(api.getArchiveJob).mockImplementation(async id=>({status:"done",result:id==="preview"?plan:completed}));});
it("opens the picker directly and receives after exactly one concise confirmation",async()=>{
 const user=userEvent.setup();const received=vi.fn();render(<ReceiveMaterials onClose={vi.fn()} onReceived={received}/>);
 expect(await screen.findByRole("button",{name:"Receive",exact:true})).toBeTruthy();
 expect(api.pickReceiptFolder).toHaveBeenCalledOnce();
 expect(screen.queryByLabelText("Project number")).toBeNull();expect(screen.queryByLabelText("Declared project state")).toBeNull();
 expect(api.confirmArchive).not.toHaveBeenCalled();await user.click(screen.getByRole("button",{name:"Receive",exact:true}));
 await waitFor(()=>expect(received).toHaveBeenCalledWith("archive:one"));expect(api.confirmArchive).toHaveBeenCalledOnce();
});
it("picker cancellation exits without creating an operation",async()=>{
 const close=vi.fn();vi.mocked(api.pickReceiptFolder).mockResolvedValue(null);render(<ReceiveMaterials onClose={close} onReceived={vi.fn()}/>);
 await waitFor(()=>expect(close).toHaveBeenCalled());expect(api.startArchivePreview).not.toHaveBeenCalled();expect(api.confirmArchive).not.toHaveBeenCalled();
});
it("same-name conflict only offers skip or a deliberately independent copy",async()=>{
 const user=userEvent.setup();vi.mocked(api.getArchiveJob).mockResolvedValue({status:"done",result:{...plan,status:"conflict"}});
 render(<ReceiveMaterials onClose={vi.fn()} onReceived={vi.fn()}/>);
 await user.click(await screen.findByRole("button",{name:"Keep independent copy"}));
 expect(api.startArchivePreview).toHaveBeenLastCalledWith(plan.source_path,true);expect(api.confirmArchive).not.toHaveBeenCalled();
});

it("opens exactly one native picker under StrictMode",async()=>{
 render(<StrictMode><ReceiveMaterials onClose={vi.fn()} onReceived={vi.fn()}/></StrictMode>);
 await screen.findByRole("button",{name:"Receive",exact:true});expect(api.pickReceiptFolder).toHaveBeenCalledOnce();
});
it("ignores a late native picker result after leaving",async()=>{
 let finish!:(path:string)=>void;vi.mocked(api.pickReceiptFolder).mockImplementation(()=>new Promise(resolve=>{finish=resolve;}));
 const view=render(<ReceiveMaterials onClose={vi.fn()} onReceived={vi.fn()}/>);view.unmount();finish("C:/late");
 await Promise.resolve();expect(api.startArchivePreview).not.toHaveBeenCalled();
});
it("retains an incomplete operation and continues it instead of creating a new preview",async()=>{
 const user=userEvent.setup();vi.mocked(api.getArchiveJob).mockImplementation(async id=>({status:"done",result:id==="preview"?plan:{...completed,status:"incomplete",message:"Registration incomplete",phase:"index_pending"}}));
 vi.mocked(api.retryArchive).mockResolvedValue({job_id:"retry"});
 const received=vi.fn();render(<ReceiveMaterials onClose={vi.fn()} onReceived={received}/>);
 await user.click(await screen.findByRole("button",{name:"Receive",exact:true}));
 await user.click(await screen.findByRole("button",{name:"Continue receipt"}));
 expect(api.retryArchive).toHaveBeenCalledWith("operation");expect(api.startArchivePreview).toHaveBeenCalledOnce();expect(received).not.toHaveBeenCalled();
});

it("allows leaving while the worker is still cancelling and never reports completion",async()=>{
 const user=userEvent.setup();const close=vi.fn(),received=vi.fn();
 vi.mocked(api.getArchiveJob).mockImplementation(async id=>({status:id==="preview"?"done":"working",result:id==="preview"?plan:undefined}));
 vi.mocked(api.cancelArchiveJob).mockResolvedValue({status:"cancellation_requested"});
 const view=render(<ReceiveMaterials onClose={close} onReceived={received}/>);
 await user.click(await screen.findByRole("button",{name:"Receive",exact:true}));
 await user.click(await screen.findByRole("button",{name:"Cancel processing"}));
 await user.click(screen.getByRole("button",{name:"Back to library"}));
 expect(close).toHaveBeenCalled();expect(received).not.toHaveBeenCalled();expect(api.cancelArchiveJob).toHaveBeenCalled();view.unmount();
});

it("selects an existing canonical receipt key without confirming or duplicating it",async()=>{
 const received=vi.fn();vi.mocked(api.getArchiveJob).mockResolvedValue({status:"done",result:{status:"existing",source_path:plan.target_path,target_path:plan.target_path,target_key:"receipt:retained"}});
 render(<ReceiveMaterials onClose={vi.fn()} onReceived={received}/>);
 await waitFor(()=>expect(received).toHaveBeenCalledWith("receipt:retained"));
 expect(api.confirmArchive).not.toHaveBeenCalled();
});

it("shows no web dialog during the native picker or preparation, then one real confirmation",async()=>{
 const user=userEvent.setup(),otherPage=vi.fn();
 let choose!:(value:string)=>void,prepare!:(value:api.ArchiveJob)=>void;
 vi.mocked(api.pickReceiptFolder).mockImplementation(()=>new Promise(resolve=>{choose=resolve;}));
 vi.mocked(api.getArchiveJob).mockImplementation(()=>new Promise(resolve=>{prepare=resolve;}));
 render(<><button onClick={otherPage}>Other page</button><ReceiveMaterials onClose={vi.fn()} onReceived={vi.fn()}/></>);
 expect(screen.queryByRole("dialog")).toBeNull();expect(screen.queryByRole("button",{name:"Cancel"})).toBeNull();
 await act(async()=>choose(plan.source_path));
 await screen.findByText("Preparing materials…");expect(screen.queryByRole("dialog")).toBeNull();
 await user.click(screen.getByRole("button",{name:"Other page"}));expect(otherPage).toHaveBeenCalledOnce();
 await act(async()=>prepare({status:"done",result:plan}));
 expect(screen.getAllByRole("dialog")).toHaveLength(1);
 expect(screen.getByText(`Source: ${plan.source_path}`)).toBeTruthy();expect(screen.getByText(`Target: ${plan.target_path}`)).toBeTruthy();
 expect(api.confirmArchive).not.toHaveBeenCalled();
 await user.click(screen.getByRole("button",{name:"Receive",exact:true}));expect(api.confirmArchive).toHaveBeenCalledOnce();
});

it("cancels preparation before its start response and discards a late result",async()=>{
 const user=userEvent.setup(),close=vi.fn(),received=vi.fn();
 let start!:(value:{job_id:string})=>void;
 vi.mocked(api.startArchivePreview).mockImplementation(()=>new Promise(resolve=>{start=resolve;}));
 vi.mocked(api.cancelArchiveJob).mockResolvedValue({status:"cancellation_requested"});
 const view=render(<ReceiveMaterials onClose={close} onReceived={received}/>);
 await screen.findByText("Preparing materials…");expect(screen.queryByRole("dialog")).toBeNull();
 await user.click(screen.getByRole("button",{name:"Cancel",exact:true}));expect(close).toHaveBeenCalledOnce();
 await act(async()=>start({job_id:"late-preview"}));
 expect(api.cancelArchiveJob).toHaveBeenCalledWith("late-preview");expect(api.getArchiveJob).not.toHaveBeenCalled();
 expect(api.confirmArchive).not.toHaveBeenCalled();expect(received).not.toHaveBeenCalled();expect(screen.queryByRole("dialog")).toBeNull();view.unmount();
});

it("loads an original incomplete operation without reopening the picker",async()=>{
 vi.mocked(api.getArchiveOperation).mockResolvedValue({...completed,status:"incomplete",message:"Registration incomplete"});
 render(<ReceiveMaterials initialOperation="original" onClose={vi.fn()} onReceived={vi.fn()}/>);
 await screen.findByRole("button",{name:"Continue receipt"});
 expect(api.getArchiveOperation).toHaveBeenCalledWith("original");expect(api.pickReceiptFolder).not.toHaveBeenCalled();
});

it("cancels an in-flight preview and ignores its late ready confirmation",async()=>{
 const user=userEvent.setup(),close=vi.fn(),received=vi.fn();let prepare!:(value:api.ArchiveJob)=>void;
 vi.mocked(api.getArchiveJob).mockImplementation(()=>new Promise(resolve=>{prepare=resolve;}));
 vi.mocked(api.cancelArchiveJob).mockResolvedValue({status:"cancellation_requested"});
 const view=render(<ReceiveMaterials onClose={close} onReceived={received}/>);
 await screen.findByText("Preparing materials…");await user.click(screen.getByRole("button",{name:"Cancel",exact:true}));
 expect(api.cancelArchiveJob).toHaveBeenCalledWith("preview");expect(close).toHaveBeenCalledOnce();
 await act(async()=>prepare({status:"done",result:plan}));
 expect(screen.queryByRole("dialog")).toBeNull();expect(api.confirmArchive).not.toHaveBeenCalled();expect(received).not.toHaveBeenCalled();view.unmount();
});
