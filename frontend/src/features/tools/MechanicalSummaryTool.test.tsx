import { fireEvent, render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MechanicalSummaryTool } from './MechanicalSummaryTool';
import { previewMechanicalFolder, generateMechanicalFolder, type FolderAnalysis } from '../../api/mechanicalSummary';
vi.mock('../../api/mechanicalSummary', () => ({ previewMechanicalFolder: vi.fn(), generateMechanicalFolder: vi.fn() }));
const analysis = (sample = '#1'): FolderAnalysis => ({ project: 'DL-2026-09-031', ready: Boolean(sample), ignored: [], errors: [], sections: [{
  id: 'abc:0', sha256: 'abc', source: 'test/force.pdf', name: 'Contact Retention', kind: 'retention', sheet: null,
  rows: [{curve:'1.20',sample,colour:'',part:'',value:241.07}], source_text:'Original record', information: {},
  force_fields:[],force_field:'',withdraw_magnitude:false,tables:[],issues: sample ? [] : ['Enter sample'],
}] });
const preview = vi.mocked(previewMechanicalFolder), generate = vi.mocked(generateMechanicalFolder);
beforeEach(() => {
  vi.clearAllMocks(); localStorage.clear();
  preview.mockResolvedValue(analysis());
  generate.mockResolvedValue({blob:new Blob(['xlsx']),fileName:'new-summary.xlsx'});
  vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(() => undefined);
  vi.stubGlobal('URL',{createObjectURL:vi.fn(()=>'blob:summary'),revokeObjectURL:vi.fn()});
});
describe('Mechanical Summary folder workflow', () => {
  it('selects a folder and automatically downloads when all source mappings are known', async () => {
    render(<MechanicalSummaryTool/>);
    const picker=screen.getByLabelText('Select mechanical test folder') as HTMLInputElement;
    expect(picker.hasAttribute('webkitdirectory')).toBe(true);
    const click=vi.spyOn(picker,'click');
    fireEvent.click(screen.getByRole('button',{name:'Mechanical Summary',exact:true}));
    expect(click).toHaveBeenCalledOnce();
    fireEvent.change(picker,{target:{files:[new File(['data'],'force.pdf')]}});
    expect(await screen.findByText('new-summary.xlsx')).toBeTruthy();
    expect(generate).toHaveBeenCalledOnce();
    expect(screen.queryByText('Select test type')).toBeNull();
  });
  it('asks only for unresolved mappings, preserves cancellation and keeps numeric values out of review', async () => {
    preview.mockResolvedValueOnce(analysis(''));
    render(<MechanicalSummaryTool/>);
    const picker=screen.getByLabelText('Select mechanical test folder');
    fireEvent.change(picker,{target:{files:[new File(['data'],'force.pdf')]}});
    const sample=await screen.findByLabelText('Sample for curve 1.20');
    expect(generate).not.toHaveBeenCalled();
    fireEvent.change(picker,{target:{files:[]}});
    await userEvent.type(sample,'#3');
    fireEvent.click(screen.getByRole('button',{name:'Generate Summary'}));
    expect(await screen.findByText('new-summary.xlsx')).toBeTruthy();
    expect(generate.mock.calls[0][1]?.sections['abc:0'].rows).toEqual([{curve:'1.20',sample:'#3',colour:'',part:''}]);
  });
  it('does not download after leaving the tool while generation is running', async () => {
    let finish!: (a: Awaited<ReturnType<typeof generateMechanicalFolder>>) => void;
    generate.mockReturnValueOnce(new Promise(resolve=>{finish=resolve;}));
    const rendered=render(<MechanicalSummaryTool/>);
    fireEvent.change(screen.getByLabelText('Select mechanical test folder'),{target:{files:[new File(['data'],'force.pdf')]}});
    await screen.findByText('Generating workbook…');
    rendered.unmount();
    await act(async()=>finish({blob:new Blob(['xlsx']),fileName:'stale.xlsx'}));
    expect(HTMLAnchorElement.prototype.click).not.toHaveBeenCalled();
  });
});

it('keeps the unresolved section open while the user finishes colour and metadata', async () => {
  preview.mockResolvedValueOnce(analysis(''));
  render(<MechanicalSummaryTool/>);
  fireEvent.change(screen.getByLabelText('Select mechanical test folder'),{target:{files:[new File(['data'],'force.pdf')]}});
  await userEvent.type(await screen.findByLabelText('Sample for curve 1.20'),'#3');
  expect(screen.getByLabelText('Colour for curve 1.20').closest('details')?.open).toBe(true);
});

it('does not apply saved confirmations from another project or changed source', async () => {
  localStorage.setItem('connlab.mechanical-folder.v1.DL-2026-09-032',JSON.stringify({project:'DL-2026-09-032',sections:{'abc:0':{rows:[{curve:'1.20',sample:'wrong'}]}}}));
  localStorage.setItem('connlab.mechanical-folder.v1.DL-2026-09-031',JSON.stringify({project:'DL-2026-09-031',sections:{'older:0':{rows:[{curve:'1.20',sample:'old'}]}}}));
  preview.mockResolvedValueOnce(analysis(''));
  render(<MechanicalSummaryTool/>);
  fireEvent.change(screen.getByLabelText('Select mechanical test folder'),{target:{files:[new File(['data'],'force.pdf')]}});
  expect((await screen.findByLabelText('Sample for curve 1.20') as HTMLInputElement).value).toBe('');
  expect(preview).toHaveBeenCalledOnce();
  expect(generate).not.toHaveBeenCalled();
});
