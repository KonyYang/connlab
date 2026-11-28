export type StoragePurpose = "Projects" | "Library" | "TemporaryProjects" | "Template";
export type RuntimeEnvironment = {
  schema_version: 1;
  environment: "development" | "release";
  instance_id: string;
  default_output_paths: Record<string, string>;
  storage_locations?: Record<StoragePurpose, string>;
  storage_root?: string | null;
  storage_warnings?: string[];
};
let current: RuntimeEnvironment | null = null;
export function getRuntimeEnvironment(): RuntimeEnvironment | null {return current;}
export function requireRuntimeEnvironment():RuntimeEnvironment {if(!current)throw new Error("Connect to the data instance before continuing.");return current;}
export function bindRuntime(value:RuntimeEnvironment) {
 if(value.schema_version!==1 || !["development","release"].includes(value.environment) || typeof value.instance_id!=="string" || !value.instance_id) throw new Error("The connected ConnLab version cannot identify its data instance.");
 current=value;
}
export function clearRuntimeBinding(){current=null;}
export function invalidateRuntimeBinding(){current=null;window.dispatchEvent(new Event("connlab-runtime-changed"));}
export function storageNamespace(key:string){const value=requireRuntimeEnvironment();return `connlab:${value.environment}:${value.instance_id}:${key}`;}
function scopedStorage(kind:"sessionStorage"|"localStorage") {return {
 getItem(key:string){return current?window[kind].getItem(storageNamespace(key)):null;},
 setItem(key:string,value:string){if(current)window[kind].setItem(storageNamespace(key),value);},
 removeItem(key:string){if(current)window[kind].removeItem(storageNamespace(key));}
};}
export const runtimeSessionStorage=scopedStorage("sessionStorage");
export const runtimeLocalStorage=scopedStorage("localStorage");
