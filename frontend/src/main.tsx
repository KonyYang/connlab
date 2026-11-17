import {StrictMode} from "react";
import {createRoot} from "react-dom/client";
import {bootstrapRuntime} from "./api/runtime";
import "./styles.css";
const root=createRoot(document.getElementById("root") as HTMLElement);
async function start(){
 root.render(<main className="runtime-connection" role="status">Connecting to ConnLab…</main>);
 try{const runtime=await bootstrapRuntime();const {default:App}=await import("./App");document.title=runtime.environment==="development"?"ConnLab Dev":"ConnLab";root.render(<StrictMode><App key={runtime.instance_id}/></StrictMode>);}
 catch(cause){root.render(<main className="runtime-connection"><p role="alert">{(cause as Error).message}</p><button className="ui-primary-action" onClick={()=>void start()}>Retry connection</button></main>);}
}
window.addEventListener("connlab-runtime-changed",()=>root.render(<main className="runtime-connection"><p role="alert">The connected data instance changed. Saved work remains with its original instance.</p><button className="ui-primary-action" onClick={()=>window.location.reload()}>Reload ConnLab</button></main>));
void start();
