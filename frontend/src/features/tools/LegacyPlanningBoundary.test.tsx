import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, vi, expect, beforeEach } from 'vitest';
import { LegacyPlanningBoundary } from './LegacyPlanningBoundary';
import { getProject } from '../../api/client';
import { fetchLegacyPlanningRecovery, loadPlanningSeed, calculatePlanningFees } from '../../api/toolsPlanning';
vi.mock('../../api/client',async()=>({...await vi.importActual('../../api/client'),getProject:vi.fn()}));
vi.mock('../../api/toolsPlanning',async()=>({...await vi.importActual('../../api/toolsPlanning'),fetchLegacyPlanningRecovery:vi.fn(),calculatePlanningFees:vi.fn()}));

describe('retained temporary URL recovery',()=>{
 beforeEach(()=>{sessionStorage.clear();vi.clearAllMocks();});
 it('renders formal workspaces normally',async()=>{
  vi.mocked(getProject).mockResolvedValue({is_legacy_temporary:false} as never);
  render(<LegacyPlanningBoundary projectId="formal" onTools={()=>{}} onIntake={()=>{}}><p>Formal Matrix editor</p></LegacyPlanningBoundary>);
  expect(await screen.findByText('Formal Matrix editor')).not.toBeNull();
  expect(fetchLegacyPlanningRecovery).not.toHaveBeenCalled();
 });
 it('recovers an incomplete legacy Matrix without requiring fees to calculate or rendering lifecycle actions',async()=>{
  vi.mocked(getProject).mockResolvedValue({is_legacy_temporary:true} as never);
  const seed={...loadPlanningSeed(),project_id:'legacy',editor_draft:{groups:[],rows:[],cells:[],duration_authorities:[]}};
  vi.mocked(fetchLegacyPlanningRecovery).mockResolvedValue({seed,fee_values:null,retained_fee_values:null,unmatched_fee_rows:['Fee edits retained without transfer: Select at least one Matrix group.']});
  vi.spyOn(window,'confirm').mockReturnValue(true);
  const onTools=vi.fn();
  render(<LegacyPlanningBoundary projectId="legacy" onTools={onTools} onIntake={()=>{}}><button>Apply LTR Number</button></LegacyPlanningBoundary>);
  await screen.findByText(/Fee edits retained without transfer/);
  expect(screen.queryByRole('button',{name:'Apply LTR Number'})).toBeNull();
  expect((screen.getByRole('button',{name:'Download retained edits'}) as HTMLButtonElement).disabled).toBe(false);
  fireEvent.click(screen.getByRole('button',{name:'Copy Matrix and fees to Tools'}));
  await waitFor(()=>expect(onTools).toHaveBeenCalledOnce());
  expect(loadPlanningSeed().editor_draft).toEqual(seed.editor_draft);
  expect(loadPlanningSeed().project_id).toBe('');
  expect(calculatePlanningFees).not.toHaveBeenCalled();
 });
});
