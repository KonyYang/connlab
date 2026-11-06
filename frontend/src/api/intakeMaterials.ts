import { requestJson } from './client';
export type MaterialsPreview = { root: string; folder_name: string; files: string[] };
const post = (body: unknown): RequestInit => ({method:'POST', headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
export const previewIntakeMaterials = (id: string) => requestJson<MaterialsPreview>(`/api/intake/packages/${encodeURIComponent(id)}/materials`);
export const saveIntakeMaterials = (id: string, folderName: string) => requestJson<{path:string;folder_name:string;files:string[]}>(`/api/intake/packages/${encodeURIComponent(id)}/materials`,post({folder_name:folderName}));
export const openMaterialsFolder = (folderName: string) => requestJson<{status:string;message:string}>('/api/intake/materials/open-folder',post({folder_name:folderName}));
