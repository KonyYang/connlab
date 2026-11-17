import {beforeEach} from "vitest";
import {bindRuntime} from "../runtimeEnvironment";
export const testRuntime={schema_version:1 as const,environment:"development" as const,instance_id:"unit-data-instance",default_output_paths:{Projects:"D:/ConnLabDev/Projects",Materials:"D:/ConnLabDev/Materials",TemporaryMaterials:"D:/ConnLabDev/TemporaryMaterials"}};
beforeEach(()=>bindRuntime(testRuntime));
export function runtimeResponse(body?:BodyInit|null,init:ResponseInit={}){const headers=new Headers(init.headers);headers.set("X-ConnLab-Instance",testRuntime.instance_id);headers.set("X-ConnLab-Environment",testRuntime.environment);return new Response(body,{...init,headers});}
