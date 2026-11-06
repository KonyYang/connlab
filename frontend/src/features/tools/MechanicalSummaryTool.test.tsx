import { fireEvent, render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { MechanicalSummaryTool } from './MechanicalSummaryTool';
import { previewMechanicalFolder, generateMechanicalFolder, exportMechanicalReportPackage, type FolderAnalysis } from '../../api/mechanicalSummary';
vi.mock('../../api/mechanicalSummary', () => ({ previewMechanicalFolder: vi.fn(), generateMechanicalFolder: vi.fn(), exportMechanicalReportPackage: vi.fn() }));
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
  vi.mocked(exportMechanicalReportPackage).mockResolvedValue({blob:new Blob(['zip']),fileName:'Mechanical_ReportResults.zip'});
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
  it('exports reviewed sources for Report without a project link or another workbook generation', async () => {
    preview.mockResolvedValueOnce(analysis(''));
    render(<MechanicalSummaryTool/>);
    const source = new File(['data'], 'force.pdf');
    fireEvent.change(screen.getByLabelText('Select mechanical test folder'), { target: { files: [source] } });
    const sample = await screen.findByLabelText('Sample for curve 1.20');
    expect(screen.getByRole('button', { name: 'Export for Report' }).hasAttribute('disabled')).toBe(true);
    await userEvent.type(sample, '#3');
    fireEvent.click(screen.getByRole('button', { name: 'Export for Report' }));
    expect(await screen.findByText('Mechanical_ReportResults.zip')).toBeTruthy();
    expect(exportMechanicalReportPackage).toHaveBeenCalledWith([source], expect.objectContaining({
      sections: { 'abc:0': expect.objectContaining({ rows: [{ curve: '1.20', sample: '#3', colour: '', part: '' }] }) },
    }));
    expect(generate).not.toHaveBeenCalled();
    expect(screen.getByRole('button', { name: 'Generate Summary' })).toBeTruthy();
    expect(screen.getByText(/In Report preparation/)).toBeTruthy();
  });
  it('retains the review after a package export failure and supports retry', async () => {
    vi.mocked(exportMechanicalReportPackage).mockRejectedValueOnce(new Error('The source could not be verified. Review it and retry.'));
    render(<MechanicalSummaryTool/>);
    fireEvent.change(screen.getByLabelText('Select mechanical test folder'), { target: { files: [new File(['data'], 'force.pdf')] } });
    await screen.findByText('new-summary.xlsx');
    fireEvent.click(screen.getByRole('button', { name: 'Export for Report' }));
    expect((await screen.findByRole('alert')).textContent).toContain('The source could not be verified');
    expect(screen.getByLabelText('Sample for curve 1.20')).toHaveProperty('value', '#1');
    fireEvent.click(screen.getByRole('button', { name: 'Export for Report' }));
    expect(await screen.findByText('Mechanical_ReportResults.zip')).toBeTruthy();
  });
  it('does not download an exported package after leaving the tool', async () => {
    let finish!: (value: Awaited<ReturnType<typeof exportMechanicalReportPackage>>) => void;
    vi.mocked(exportMechanicalReportPackage).mockReturnValueOnce(new Promise(resolve => { finish = resolve; }));
    const view = render(<MechanicalSummaryTool/>);
    fireEvent.change(screen.getByLabelText('Select mechanical test folder'), { target: { files: [new File(['data'], 'force.pdf')] } });
    await screen.findByText('new-summary.xlsx');
    vi.mocked(HTMLAnchorElement.prototype.click).mockClear();
    fireEvent.click(screen.getByRole('button', { name: 'Export for Report' }));
    await screen.findByText('Preparing report package…');
    view.unmount();
    await act(async () => finish({ blob: new Blob(['zip']), fileName: 'stale.zip' }));
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
