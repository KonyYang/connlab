import {fireEvent, render, screen, within} from '@testing-library/react';
import {expect, it, vi} from 'vitest';
import {CustomerContentDialog} from './CustomerContentDialog';

it('requires an explicit sample choice and previews only included rows and the selected measured maximum', () => {
  const onGenerate = vi.fn();
  render(<CustomerContentDialog name="Internal.docx" onGenerate={onGenerate} onCancel={vi.fn()} inspection={{
    source_sha256: 'abc', decisions: {}, fields: [
      {id:'s1', kind:'sample', label:'Fixture PCB', part_number:'P-1'},
      {id:'m1', kind:'material', label:'Housing material', value:'Unclassified', depends_on:'s1'},
      {id:'t1', kind:'temperature', label:'Group A, 50 A', options:[{value:'r3',label:'Max measured: 31 °C'}]},
    ],
    samples:[{description:'Fixture PCB',part_number:'P-1',decision_id:'s1',base_material:'Copper Alloy',housing_material:'',housing_decision_id:'m1'}],
    temperatures:[{label:'Group A, 50 A',headers:['Measurement'],rows:[],decision_id:'t1',options:[{value:'r3',label:'Max measured: 31 °C',cells:['31 °C']}]}],
  }} />);
  const generate = screen.getByRole('button', {name:'Generate Word copy'});
  expect(generate).toHaveProperty('disabled', true);
  fireEvent.click(screen.getByRole('radio', {name:'Omit'}));
  expect(screen.queryByRole('textbox')).toBeNull();
  fireEvent.change(screen.getByRole('combobox'), {target:{value:'r3'}});
  fireEvent.click(screen.getByText('Preview customer content'));
  const preview = screen.getByRole('region', {name:'Customer content preview'});
  expect(within(preview).queryByText('Fixture PCB')).toBeNull();
  expect(within(preview).getByText('31 °C')).toBeTruthy();
  fireEvent.click(generate);
  expect(onGenerate).toHaveBeenCalledWith({s1:'omit',t1:'r3'});
});

it('previews the selected vertical maximum column for every measured condition', () => {
  const points = [['50 A','18 °C'],['100 A','27 °C']];
  const option = {value:'c2',label:'Reading B',cells:points[0],rows:points};
  render(<CustomerContentDialog name="Report.docx" onGenerate={vi.fn()} onCancel={vi.fn()} inspection={{
    source_sha256:'s',decisions:{},fields:[{id:'t',kind:'temperature',label:'Temperature rise',options:[option]}],
    samples:[],temperatures:[{label:'Measured rise',headers:['Current','Maximum'],rows:[],decision_id:'t',options:[option]}],
  }}/>);
  fireEvent.change(screen.getByRole('combobox'),{target:{value:'c2'}});
  fireEvent.click(screen.getByText('Preview customer content'));
  const table = screen.getByRole('table',{name:'Measured rise'});
  expect(within(table).getAllByRole('row')).toHaveLength(3);
  for (const point of points.flat()) expect(within(table).getByRole('cell',{name:point})).toBeTruthy();
});
