import { act, renderHook, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";
import { useWorkbenchCopyContext } from "./useWorkbenchCopyContext";
import * as api from "../../api/materialReceipts";
vi.mock("../../api/materialReceipts",()=>({createCopyContextSession:vi.fn(),updateCopyContext:vi.fn()}));
const target={key:"project:p1",project_id:"p1",member_id:null,number:"DL-1",title:"Project",test_item:"",source:"connlab",folder_path:"D:/p1",available:true};
beforeEach(()=>{vi.resetAllMocks();vi.mocked(api.createCopyContextSession).mockResolvedValue({session_id:"browser"});vi.mocked(api.updateCopyContext).mockImplementation(async(session_id,intent,projectId)=>({session_id,intent,token:projectId?`token-${intent}`:null,target:projectId?{...target,key:`project:${projectId}`,project_id:projectId}:null}));});
it("carries only actual Workbench context into Library and clears on other pages",async()=>{
 const view=renderHook(({id,library})=>useWorkbenchCopyContext(id,library),{initialProps:{id:"p1" as string|null,library:false}});
 await waitFor(()=>expect(view.result.current?.target.project_id).toBe("p1"));
 view.rerender({id:null,library:true});
 expect(view.result.current?.target.project_id).toBe("p1");
 expect(api.updateCopyContext).toHaveBeenCalledTimes(1);
 view.rerender({id:null,library:false});
 expect(view.result.current).toBeNull();
 await waitFor(()=>expect(api.updateCopyContext).toHaveBeenLastCalledWith("browser",2,null));
 view.rerender({id:null,library:true});
 await waitFor(()=>expect(api.updateCopyContext).toHaveBeenLastCalledWith("browser",3,null));
 expect(view.result.current).toBeNull();
});
it("does not revive delayed activation after a newer clear",async()=>{
 let resolve!:(value:api.CopyContextState)=>void;
 vi.mocked(api.updateCopyContext).mockImplementation((session_id,intent,id)=>id?new Promise(done=>{resolve=done;}):Promise.resolve({session_id,intent,token:null,target:null}));
 const view=renderHook(({id,library})=>useWorkbenchCopyContext(id,library),{initialProps:{id:"p1" as string|null,library:false}});
 await waitFor(()=>expect(api.updateCopyContext).toHaveBeenCalledOnce());
 view.rerender({id:null,library:false});
 await waitFor(()=>expect(api.updateCopyContext).toHaveBeenCalledTimes(2));
 await act(async()=>resolve({session_id:"browser",intent:1,token:"old",target}));
 expect(view.result.current).toBeNull();
});
it("boots directly in Library with no inferred target and carries pending real activation",async()=>{
 const direct=renderHook(()=>useWorkbenchCopyContext(null,true));
 await waitFor(()=>expect(api.updateCopyContext).toHaveBeenLastCalledWith("browser",1,null));
 expect(direct.result.current).toBeNull();direct.unmount();
 let resolve!:(value:api.CopyContextState)=>void;
 vi.mocked(api.updateCopyContext).mockImplementation(()=>new Promise(done=>{resolve=done;}));
 const live=renderHook(({id,library})=>useWorkbenchCopyContext(id,library),{initialProps:{id:"p1" as string|null,library:false}});
 await waitFor(()=>expect(api.updateCopyContext).toHaveBeenCalledTimes(2));
 live.rerender({id:null,library:true});
 await act(async()=>resolve({session_id:"browser",intent:1,token:"active",target}));
 expect(live.result.current?.token).toBe("active");
});

it("enables the copy destination after the open Workbench creates its folder", async () => {
 vi.mocked(api.updateCopyContext).mockResolvedValueOnce({session_id:"browser",intent:1,target:null,token:null});
 const view = renderHook(() => useWorkbenchCopyContext("p1",false));
 await waitFor(() => expect(api.updateCopyContext).toHaveBeenCalledTimes(1));
 expect(view.result.current).toBeNull();
 act(() => { window.dispatchEvent(new CustomEvent("connlab:project-folder-changed",{detail:"p1"})); });
 await waitFor(() => expect(view.result.current?.target.project_id).toBe("p1"));
});
