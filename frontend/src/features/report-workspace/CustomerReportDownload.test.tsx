import {act, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {beforeEach, expect, it, vi} from 'vitest';
import {downloadStandaloneCustomerReport, readStandaloneCustomerReportJob, type StandaloneCustomerReportJob} from '../../api/client';
import {discardCustomerInput, inspectUploadedCustomerSource, startInspectedCustomerReport, type CustomerInspection} from '../../api/customerContent';
import {CustomerReportDownload} from './CustomerReportDownload';

vi.mock('../../api/client', () => ({downloadStandaloneCustomerReport:vi.fn(),readStandaloneCustomerReportJob:vi.fn()}));
vi.mock('../../api/customerContent', () => ({discardCustomerInput:vi.fn(),inspectUploadedCustomerSource:vi.fn(),startInspectedCustomerReport:vi.fn()}));
vi.mock('../../api/reportAuthoring', () => ({downloadReportArtifact:vi.fn(),generateCustomerReviewCopy:vi.fn()}));
const selection: CustomerInspection = {input_id:'inputA',source_sha256:'s',fields:[{id:'pcb',kind:'sample',label:'Test PCB'},
  {id:'housing',kind:'material',label:'Customer-facing material',depends_on:'pcb',value:'Unclassified'}],
  samples:[{description:'Test PCB',part_number:'P1',decision_id:'pcb',base_material:'Copper Alloy',housing_material:'',housing_decision_id:'housing'}],
  temperatures:[],decisions:{}};
const completed: StandaloneCustomerReportJob = {operation_id:'j1',status:'completed',stage:'done',elapsed_seconds:1,message:null};
const choose = () => fireEvent.change(screen.getByLabelText('Select Internal Report'),{target:{files:[new File(['bytes'],'Report.docx')]}});
beforeEach(() => {
  vi.resetAllMocks();
  vi.mocked(inspectUploadedCustomerSource).mockResolvedValue(selection);
  vi.mocked(discardCustomerInput).mockResolvedValue(undefined);
  vi.mocked(startInspectedCustomerReport).mockResolvedValue(completed);
  vi.mocked(downloadStandaloneCustomerReport).mockResolvedValue({blob:new Blob(['word']),fileName:'Customer.docx'});
  vi.spyOn(HTMLAnchorElement.prototype,'click').mockImplementation(() => undefined);
  vi.stubGlobal('URL',{createObjectURL:vi.fn(() => 'blob:report'),revokeObjectURL:vi.fn()});
});

it('uses one decision window, requires customer wording for a kept sample, and reuses saved choices on repeat', async () => {
  render(<CustomerReportDownload tools />);
  choose();
  await screen.findByRole('dialog');
  expect(startInspectedCustomerReport).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('radio',{name:'Keep'}));
  const generate = screen.getByRole('button',{name:'Generate Word copy'});
  expect(generate.matches(':disabled')).toBe(true);
  fireEvent.change(screen.getByRole('textbox'),{target:{value:'Ceramic'}});
  fireEvent.click(generate);
  await screen.findByRole('status',{name:'Downloaded File'});
  expect(startInspectedCustomerReport).toHaveBeenCalledWith('inputA',{pcb:'keep',housing:'Ceramic'});
  const remembered = {...selection, input_id:'inputB',decisions:{pcb:'keep',housing:'Ceramic'}};
  vi.mocked(inspectUploadedCustomerSource).mockResolvedValue(remembered);
  choose();
  await waitFor(() => expect(startInspectedCustomerReport).toHaveBeenCalledWith('inputB',remembered.decisions));
  await screen.findByRole('status',{name:'Downloaded File'});
  expect(screen.queryByRole('dialog')).toBeNull();
  fireEvent.click(screen.getByRole('button',{name:'Review customer content…'}));
  expect((await screen.findByRole('textbox') as HTMLInputElement).value).toBe('Ceramic');
  fireEvent.click(screen.getByRole('button',{name:'Cancel'}));
  expect(discardCustomerInput).toHaveBeenCalledWith('inputB');
  expect(startInspectedCustomerReport).toHaveBeenCalledTimes(2);
});

it('cancels the inspection without generating and starts normally with the next selected report', async () => {
  render(<CustomerReportDownload tools />);
  choose();
  fireEvent.keyDown(await screen.findByRole('dialog'),{key:'Escape'});
  expect(startInspectedCustomerReport).not.toHaveBeenCalled();
  expect(discardCustomerInput).toHaveBeenCalledWith('inputA');
  vi.mocked(inspectUploadedCustomerSource).mockResolvedValue({...selection,fields:[],samples:[]});
  choose();
  expect((await screen.findByRole('status',{name:'Downloaded File'})).textContent).toBe('Customer.docx');
});

it('retries status and download independently without starting a second Word conversion', async () => {
  vi.mocked(inspectUploadedCustomerSource).mockResolvedValue({...selection,fields:[]});
  vi.mocked(startInspectedCustomerReport).mockResolvedValue({...completed,status:'running'});
  vi.mocked(readStandaloneCustomerReportJob).mockRejectedValueOnce(new Error('Connection interrupted')).mockResolvedValue(completed);
  vi.mocked(downloadStandaloneCustomerReport).mockRejectedValueOnce(new Error('Download interrupted'));
  render(<CustomerReportDownload tools />);
  choose();
  fireEvent.click(await screen.findByRole('button',{name:'Retry status check'}));
  fireEvent.click(await screen.findByRole('button',{name:'Retry download'}));
  await screen.findByRole('status',{name:'Downloaded File'});
  expect(startInspectedCustomerReport).toHaveBeenCalledTimes(1);
  expect(downloadStandaloneCustomerReport).toHaveBeenCalledTimes(2);
});

it('releases an unanswered temporary input on unmount', async () => {
  const view=render(<CustomerReportDownload tools />);
  choose();
  await screen.findByRole('dialog');
  await act(async () => { view.unmount(); });
  expect(discardCustomerInput).toHaveBeenCalledWith('inputA');
  expect(startInspectedCustomerReport).not.toHaveBeenCalled();
});

it('retries an unacknowledged generation with the same checked input and decisions', async () => {
  vi.mocked(inspectUploadedCustomerSource).mockResolvedValue({...selection,decisions:{pcb:'omit'}});
  vi.mocked(startInspectedCustomerReport).mockRejectedValueOnce(new TypeError('Connection interrupted'));
  render(<CustomerReportDownload tools />);
  choose();
  const retry = await screen.findByRole('button',{name:'Retry generation request'});
  expect(discardCustomerInput).not.toHaveBeenCalled();
  expect(screen.getByRole('button',{name:'Generate Customer Report'}).matches(':disabled')).toBe(true);
  fireEvent.click(retry);
  await screen.findByRole('status',{name:'Downloaded File'});
  expect(inspectUploadedCustomerSource).toHaveBeenCalledTimes(1);
  expect(startInspectedCustomerReport).toHaveBeenNthCalledWith(1,'inputA',{pcb:'omit'});
  expect(startInspectedCustomerReport).toHaveBeenNthCalledWith(2,'inputA',{pcb:'omit'});
});
