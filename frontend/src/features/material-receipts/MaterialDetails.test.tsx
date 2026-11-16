import {render,screen} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {expect,it,vi} from "vitest";
import {MaterialDetails} from "./MaterialDetails";
const project={key:"archive:one",project_id:null,member_id:null,number:"OLD",title:"Connector",test_item:"Temperature",source:"received",available:true,folder_path:"D:/Library/Old"};
it("shows existing low-cost information without adding archive editing, history or business state",()=>{
 render(<MaterialDetails project={project} onClose={vi.fn()} onBrowse={vi.fn()} onProject={vi.fn()}/>);
 expect(screen.getByText("Connector")).toBeTruthy();expect(screen.getByText("Test items: Temperature")).toBeTruthy();
 expect(screen.queryByRole("textbox")).toBeNull();expect(screen.queryByRole("button",{name:/Edit|Locate|Supplement/})).toBeNull();expect(screen.queryByText(/Receipt history|Declared project state/)).toBeNull();
});
it("retains the native workspace boundary",async()=>{
 const open=vi.fn();render(<MaterialDetails project={{...project,key:"project:p1",project_id:"p1"}} onClose={vi.fn()} onBrowse={vi.fn()} onProject={open}/>);
 await userEvent.setup().click(screen.getByRole("button",{name:"Project workspace"}));expect(open).toHaveBeenCalledWith("p1");
});
