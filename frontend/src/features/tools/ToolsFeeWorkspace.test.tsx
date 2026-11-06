import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ToolsFeeWorkspace } from './ToolsFeeWorkspace';
import { calculatePlanningFees, loadPlanningSeed, savePlanningSeed } from '../../api/toolsPlanning';
import type { FeeEvaluationDraft, MatrixEditorSessionDraft } from '../../api/client';
import fixture from './planningFee.fixture.json';

vi.mock('../../api/toolsPlanning', async () => ({...await vi.importActual('../../api/toolsPlanning'),calculatePlanningFees:vi.fn()}));
const draft=fixture as FeeEvaluationDraft;
const matrix={groups:[],rows:[],cells:[],duration_authorities:[]} as unknown as MatrixEditorSessionDraft;

describe('Tools fee estimate session',()=>{
 beforeEach(()=>{sessionStorage.clear();vi.clearAllMocks();savePlanningSeed({...loadPlanningSeed(),editor_draft:matrix});vi.mocked(calculatePlanningFees).mockResolvedValue(draft);});
 it('keeps manual units and price on re-entry, and requires explicit recalculation for a changed Matrix',async()=>{
  const first=render(<ToolsFeeWorkspace onBack={()=>{}}/>);
  const price=await screen.findByLabelText('Unit Price for LLCR');
  fireEvent.change(price,{target:{value:'3'}});
  fireEvent.change(screen.getByLabelText('Units for LLCR'),{target:{value:'7'}});
  first.unmount();
  savePlanningSeed({...loadPlanningSeed(),editor_draft:{...matrix,rows:[{draft_row_id:'changed'}]} as never});
  render(<ToolsFeeWorkspace onBack={()=>{}}/>);
  expect((await screen.findByLabelText('Unit Price for LLCR') as HTMLInputElement).value).toBe('3');
  expect((screen.getByLabelText('Units for LLCR') as HTMLInputElement).value).toBe('7');
  expect(screen.getByRole('button',{name:'Recalculate from Matrix'})).not.toBeNull();
  expect(calculatePlanningFees).toHaveBeenCalledOnce();
 });
 it('does not write a late calculation into a new or closed Tools session',async()=>{
  let finish!:(value:FeeEvaluationDraft)=>void;
  vi.mocked(calculatePlanningFees).mockReturnValue(new Promise(resolve=>{finish=resolve;}));
  const view=render(<ToolsFeeWorkspace onBack={()=>{}}/>);
  await waitFor(()=>expect(calculatePlanningFees).toHaveBeenCalledOnce());
  view.unmount();
  await act(async()=>finish(draft));
  expect(sessionStorage.getItem('connlab:tools-fees:v1')).toBeNull();
 });
});
