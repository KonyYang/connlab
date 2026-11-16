import {StrictMode} from "react";
import {render,screen,waitFor} from "@testing-library/react";
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
 vi.mocked(api.getArchiveJob).mockResolvedValue({status:"working"});
 vi.mocked(api.cancelArchiveJob).mockResolvedValue({status:"cancellation_requested"});
 const view=render(<ReceiveMaterials onClose={close} onReceived={received}/>);
 await user.click(await screen.findByRole("button",{name:"Cancel processing"}));
 await user.click(screen.getByRole("button",{name:"Back to library"}));
 expect(close).toHaveBeenCalled();expect(received).not.toHaveBeenCalled();expect(api.cancelArchiveJob).toHaveBeenCalled();view.unmount();
});
