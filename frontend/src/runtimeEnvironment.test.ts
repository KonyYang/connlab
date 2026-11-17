import {afterEach, beforeEach, expect, it, vi} from "vitest";
import {bindRuntime, clearRuntimeBinding, runtimeSessionStorage, storageNamespace} from "./runtimeEnvironment";
import {boundFetch, bootstrapRuntime} from "./api/runtime";
const runtime=(environment:"development"|"release",instance_id:string)=>({schema_version:1 as const,environment,instance_id,default_output_paths:{Projects:"P",Materials:"M",TemporaryMaterials:"T"}});
beforeEach(()=>{sessionStorage.clear();clearRuntimeBinding();});
afterEach(()=>vi.unstubAllGlobals());
it("keeps simultaneous environments and data instances separate across refresh/rebind",()=>{
 bindRuntime(runtime("development","a"));runtimeSessionStorage.setItem("draft","dev");
 bindRuntime(runtime("release","b"));expect(runtimeSessionStorage.getItem("draft")).toBeNull();runtimeSessionStorage.setItem("draft","release");
 bindRuntime(runtime("development","c"));expect(runtimeSessionStorage.getItem("draft")).toBeNull();
 bindRuntime(runtime("development","a"));expect(runtimeSessionStorage.getItem("draft")).toBe("dev");
 bindRuntime(runtime("release","b"));expect(runtimeSessionStorage.getItem("draft")).toBe("release");
});
it("does not read or delete unowned legacy business state before bootstrap",()=>{sessionStorage.setItem("draft","legacy");expect(runtimeSessionStorage.getItem("draft")).toBeNull();bindRuntime(runtime("development","a"));expect(runtimeSessionStorage.getItem("draft")).toBeNull();expect(sessionStorage.getItem("draft")).toBe("legacy");});
it("binds JSON and multipart requests and stops a changed backend before consuming its data",async()=>{
 bindRuntime(runtime("development","a"));
 const fetcher=vi.fn().mockResolvedValue(new Response("{}",{headers:{"X-ConnLab-Instance":"b","X-ConnLab-Environment":"release"}}));vi.stubGlobal("fetch",fetcher);
 const body=new FormData();body.set("file",new Blob(["dev upload"]),"source.txt");
 await expect(boundFetch("/api/upload",{method:"POST",body})).rejects.toThrow(/changed/);
 expect(new Headers(fetcher.mock.calls[0][1].headers).get("X-ConnLab-Instance")).toBe("a");
 expect(fetcher.mock.calls[0][1].body).toBe(body);
 expect(()=>storageNamespace("draft")).toThrow();
});

it("rejects a first connection to a backend from a different explicit frontend entry",async()=>{
 const meta=document.createElement("meta");meta.name="connlab-environment";meta.content="development";document.head.append(meta);
 vi.stubGlobal("fetch",vi.fn().mockResolvedValue(new Response(JSON.stringify(runtime("release","b")))));
 await expect(bootstrapRuntime()).rejects.toThrow(/different environment/);
 expect(()=>storageNamespace("draft")).toThrow();meta.remove();
});
