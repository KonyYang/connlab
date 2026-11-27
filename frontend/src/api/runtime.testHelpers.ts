import {beforeEach} from "vitest";
import {bindRuntime} from "../runtimeEnvironment";
export const testRuntime={schema_version:1 as const,environment:"development" as const,instance_id:"unit-data-instance",default_output_paths:{Projects:"D:/ConnLabDevFiles/Projects",Materials:"D:/ConnLabDevFiles/Library",TemporaryMaterials:"D:/ConnLabDevFiles/TemporaryProjects"}};
beforeEach(()=>bindRuntime(testRuntime));
export function runtimeResponse(body?:BodyInit|null,init:ResponseInit={}){const headers=new Headers(init.headers);headers.set("X-ConnLab-Instance",testRuntime.instance_id);headers.set("X-ConnLab-Environment",testRuntime.environment);return new Response(body,{...init,headers});}
