import { useLayoutEffect, useRef, useState } from "react";
import { createCopyContextSession, updateCopyContext, type WorkbenchCopyContext } from "../../api/materialReceipts";

// RAM-only, scoped to this mounted browser app. Sidebar resume memory is unrelated.
export function useWorkbenchCopyContext(projectId: string | null, inLibrary: boolean) {
 const session = useRef<Promise<{session_id:string}> | null>(null);
 const intent = useRef(0);
 const [folderRevision, setFolderRevision] = useState(0);
 const enteredWorkbench = useRef(false);
 const mounted = useRef(true);
 const [active,setActive] = useState<WorkbenchCopyContext | null>(null);
 useLayoutEffect(()=>{mounted.current=true;return()=>{mounted.current=false;};},[]);
 useLayoutEffect(() => {
  if (!projectId) return;
  const update = (event: Event) => {
   if ((event as CustomEvent<string>).detail === projectId) setFolderRevision(value => value + 1);
  };
  window.addEventListener("connlab:project-folder-changed", update);
  return () => window.removeEventListener("connlab:project-folder-changed", update);
 }, [projectId]);
 useLayoutEffect(()=>{
  if (inLibrary && enteredWorkbench.current) return;
  enteredWorkbench.current = Boolean(projectId);
  const current = ++intent.current;
  setActive(null);
  if (!session.current) session.current=createCopyContextSession();
  void session.current.then(async value=>{
   if (!mounted.current || current!==intent.current) return;
   const response=await updateCopyContext(value.session_id,current,projectId);
   if (!mounted.current || current!==intent.current) return;
   if (response.token && response.target) setActive({...response,token:response.token,target:response.target});
  }).catch(()=>{if(mounted.current && current===intent.current){session.current=null;setActive(null);}});
 },[projectId,inLibrary,folderRevision]);
 return (projectId || inLibrary) ? active : null;
}
