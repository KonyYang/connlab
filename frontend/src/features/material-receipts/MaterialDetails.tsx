import {useState} from "react";
import {createPortal} from "react-dom";
import type {ReferenceProject} from "../../api/referenceLibrary";
import {openReferenceFile} from "../../api/referenceLibrary";
import "./materials.css";
export function MaterialDetails({project,onClose,onBrowse,onProject}:{project:ReferenceProject;onClose:()=>void;onBrowse:(key:string)=>void;onProject:(id:string)=>void;onChanged?:()=>void}){
 const [error,setError]=useState("");
 return createPortal(<div className="materials-overlay"><section className="materials-dialog" role="dialog" aria-modal="true" aria-label="Materials information">
 <header><h2>{project.number||project.title}</h2><button onClick={onClose}>Close details</button></header><strong>{project.title}</strong>
 {error && <p role="alert">{error}</p>}{project.test_item && <p>Test items: {project.test_item}</p>}<p className="materials-path">Managed location: {project.folder_path}</p>
 <div className="materials-actions"><button disabled={!project.available} onClick={()=>void openReferenceFile(project.key).catch(cause=>setError((cause as Error).message))}>Open folder</button><button disabled={!project.available} onClick={()=>onBrowse(project.key)}>Browse files</button>{project.project_id && <button onClick={()=>onProject(project.project_id!)}>Project workspace</button>}</div>
 </section></div>,document.body);
}
