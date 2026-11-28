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

it.each([
  [500, "Internal Server Error"],
  [503, "Service unavailable"],
  [409, '{"detail":{"code":"REPORT_CONFLICT"}}'],
  [200, '{"private":"unverified result"}'],
])("rejects an unidentified HTTP %i response without disconnecting the project", async (status, body) => {
  bindRuntime(runtime("development", "a"));
  runtimeSessionStorage.setItem("draft", "work in progress");
  const fetcher = vi.fn()
    .mockResolvedValueOnce(new Response(String(body), {status: Number(status), headers: {"Content-Type": "application/json"}}))
    .mockResolvedValueOnce(new Response("project", {headers: {"X-ConnLab-Instance": "a", "X-ConnLab-Environment": "development"}}));
  vi.stubGlobal("fetch", fetcher);

  await expect(boundFetch("/api/report-status")).rejects.toThrow(String(status));
  expect(runtimeSessionStorage.getItem("draft")).toBe("work in progress");
  expect(await (await boundFetch("/api/project")).text()).toBe("project");
});

it.each([[409, "RUNTIME_INSTANCE_MISMATCH"], [503, "RUNTIME_INSTANCE_CHANGED"]] as const)(
  "stops the session for an explicit HTTP %i instance guard", async (status, code) => {
    bindRuntime(runtime("development", "a"));
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json({detail: {code}}, {status})));
    await expect(boundFetch("/api/project")).rejects.toThrow(/changed/);
    expect(() => storageNamespace("draft")).toThrow();
  },
);

it("discards a delayed response from an old session without disconnecting the new one", async () => {
  bindRuntime(runtime("development", "a"));
  let complete!: (result: Response) => void;
  vi.stubGlobal("fetch", vi.fn(() => new Promise<Response>((resolve) => { complete = resolve; })));
  const pending = boundFetch("/api/project");
  bindRuntime(runtime("development", "b"));
  runtimeSessionStorage.setItem("draft", "new instance draft");
  complete(new Response("old instance data", {headers: {"X-ConnLab-Instance": "a", "X-ConnLab-Environment": "development"}}));
  await expect(pending).rejects.toThrow();
  expect(runtimeSessionStorage.getItem("draft")).toBe("new instance draft");
});
