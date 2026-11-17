import {bindRuntime, getRuntimeEnvironment, invalidateRuntimeBinding, requireRuntimeEnvironment, type RuntimeEnvironment} from "../runtimeEnvironment";
export async function bootstrapRuntime():Promise<RuntimeEnvironment> {
 const base=import.meta.env.VITE_API_BASE_URL??"";
 const response=await fetch(`${base}/api/runtime-environment`,{headers:{Accept:"application/json"},cache:"no-store"});
 if(!response.ok)throw new Error("Unable to connect to ConnLab. Check that the corresponding backend is running, then retry.");
 const value=await response.json() as RuntimeEnvironment;
 const expected=document.querySelector<HTMLMetaElement>('meta[name="connlab-environment"]')?.content;
 if(!expected || value.environment!==expected)throw new Error("The frontend is connected to a different environment. Start the corresponding backend and retry.");
 bindRuntime(value);return value;
}
export async function boundFetch(input:RequestInfo|URL,init:RequestInit={}):Promise<Response>{
 const binding=requireRuntimeEnvironment();
 const headers=new Headers(init.headers);headers.set("X-ConnLab-Instance",binding.instance_id);headers.set("X-ConnLab-Environment",binding.environment);
 const response=await fetch(input,{...init,headers});
 const now=getRuntimeEnvironment();
 if(!now || now.instance_id!==binding.instance_id || now.environment!==binding.environment || response.headers.get("X-ConnLab-Instance")!==binding.instance_id || response.headers.get("X-ConnLab-Environment")!==binding.environment){
  invalidateRuntimeBinding();throw new Error("The connected data instance changed. Reload ConnLab before continuing.");
 }
 return response;
}

export function boundResourceUrl(path:string):string{
 const binding=requireRuntimeEnvironment();
 const url=new URL(path,window.location.origin);
 if(url.origin!==window.location.origin || !url.pathname.startsWith("/api/"))throw new Error("The generated file location is not a ConnLab resource.");
 url.searchParams.set("connlab_instance",binding.instance_id);url.searchParams.set("connlab_environment",binding.environment);
 return url.pathname+url.search+url.hash;
}
