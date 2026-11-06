import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { loadPlanningSeed, savePlanningSeed } from '../../api/toolsPlanning';
import { MatrixEditorWorkspace } from '../matrix-editor/MatrixEditorWorkspace';
vi.mock('../../api/client', async () => ({...await vi.importActual('../../api/client'), getProject:vi.fn(()=>{throw new Error('Project access prohibited');}),getProjectLifecycle:vi.fn(()=>{throw new Error('Project access prohibited');}),fetchMatrixEditorSession:vi.fn(()=>{throw new Error('Project access prohibited');})}));
describe('standalone Matrix planning',()=>{
 beforeEach(()=>sessionStorage.clear());
 it('opens a full editable matrix without creating or loading a project',async()=>{
  render(<MatrixEditorWorkspace projectId="" standalone onBackToWorkbench={()=>{}} onEvaluateFees={()=>{}}/>);
  await waitFor(()=>expect((screen.getByRole('button',{name:'Import Matrix'}) as HTMLButtonElement).disabled).toBe(false));
  expect(screen.queryByText('Unable to load project information. Retry before editing Matrix.')).toBeNull();
  expect(screen.getByRole('button',{name:'Fee Evaluation'})).not.toBeNull();
 });
 it('retains live Matrix edits and points when leaving and reopening Tools',async()=>{
  savePlanningSeed({...loadPlanningSeed(),editor_draft:{
    groups:[{draft_group_id:'g1',source_group_snapshot_id:null,group_order:1,group_key:'1',group_label:'1',is_selected:true,sample_quantity_expression:'5',sample_note:null}],
    rows:[{draft_row_id:'r1',source_row_snapshot_id:null,row_order:1,test_item:'LLCR',source_section:'5.1',method:'EIA-364-23',condition:'20mV',requirement:'20mOhm',day_expression:null,is_sample_row:false}],
    cells:[{draft_group_id:'g1',draft_row_id:'r1',cell_value:'1'}],duration_authorities:[],point_profile:{categories:[],delta_r_enabled:true},point_overrides:[],step_text_overrides:[]}});
  const go=vi.fn();
  const first=render(<MatrixEditorWorkspace projectId="" standalone onBackToWorkbench={()=>{}} onEvaluateFees={go}/>);
  const input=await screen.findByLabelText('Row 1 requirement');
  fireEvent.change(input,{target:{value:'Retained edited requirement'}});
  fireEvent.click(screen.getByRole('button',{name:'Fee Evaluation'}));
  await waitFor(()=>expect(go).toHaveBeenCalledOnce());
  expect(loadPlanningSeed().editor_draft?.rows[0].requirement).toBe('Retained edited requirement');
  first.unmount();
  render(<MatrixEditorWorkspace projectId="" standalone onBackToWorkbench={()=>{}} onEvaluateFees={()=>{}}/>);
  expect((await screen.findByLabelText('Row 1 requirement') as HTMLTextAreaElement).value).toBe('Retained edited requirement');
  expect(screen.queryByRole('button',{name:'Test record'})).toBeNull();
 });
});
