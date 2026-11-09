import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { expect, it, vi } from "vitest";
import { ProjectPublicFolderBindingDialog } from "./ProjectPublicFolderBindingDialog";
const preview = {project_id:"p1",status:"review_required" as const,expected_context:"context",public_folder_year:2026,full_ltr_number:"DL-2026-09-002A",current_path:null,proposed_path:null,candidates:[{candidate_id:"one",path:"D:/isolated/public/DL-2026-09-002A old"}],can_create:false,blockers:[]};
it("shows a unique full-identifier folder for explicit confirmation without auto-accepting", async () => {
 const confirm=vi.fn(); render(<ProjectPublicFolderBindingDialog preview={preview} busy={false} error={null} onConfirm={confirm} onCancel={vi.fn()} />);
 expect(screen.getByText("DL-2026-09-002A")).toBeTruthy(); expect(screen.getByText(preview.candidates[0].path)).toBeTruthy(); expect(confirm).not.toHaveBeenCalled();
 await userEvent.click(screen.getByRole("button",{name:"Use this folder"})); expect(confirm).toHaveBeenCalledWith("one");
});
it("requires selection among multiple candidates", async () => {
 const confirm=vi.fn();render(<ProjectPublicFolderBindingDialog preview={{...preview,candidates:[...preview.candidates,{candidate_id:"two",path:"D:/isolated/public/DL-2026-09-002A second"}]}} busy={false} error={null} onConfirm={confirm} onCancel={vi.fn()} />);
 const button=screen.getByRole("button",{name:"Use this folder"});expect(button).toHaveProperty("disabled",true);
 await userEvent.click(screen.getByRole("radio",{name:"D:/isolated/public/DL-2026-09-002A second"})); await userEvent.click(button);expect(confirm).toHaveBeenCalledWith("two");
});
it("requires explicit creation confirmation when no candidate exists", async () => {
 const confirm=vi.fn();render(<ProjectPublicFolderBindingDialog preview={{...preview,candidates:[],can_create:true,proposed_path:"D:/isolated/public/new"}} busy={false} error={null} onConfirm={confirm} onCancel={vi.fn()} />);
 expect(confirm).not.toHaveBeenCalled();expect(screen.getByText("D:/isolated/public/new")).toBeTruthy();await userEvent.click(screen.getByRole("button",{name:"Create project folder"})); expect(confirm).toHaveBeenCalledWith("create");
});
