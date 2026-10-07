import { fireEvent, render, screen, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useState } from 'react';
import { describe, expect, it } from 'vitest';
import type { ChannelLayout, DataSelection, WorkbookTable } from '../../api/temperature';
import { DataPreview } from './DataPreview';

const table: WorkbookTable = { file_name: 'scanner.csv', sheet_name: 'Data', sheet_names: ['Data'], rows: [
  ['Scan', 'Time', '101 <1_A> (C)', '102 <1_B> (C)', '103 <2_A> (C)', '104 <2_B> (C)', 'Ambient', 'Current', 'Spare (C)', 'Aux (VDC)'],
  [1, '18:00', 24.1, 25.2, 26.3, 27.4, 20.5, 0.009999, 28.5, 3],
  [2, '18:01', 34.1, 35.2, 36.3, 37.4, 20.6, 10.012345, 38.5, 3],
] };
const initial: DataSelection = { header_row: 1, start_row: 2, end_row: 3, temperature_columns: [3, 4, 5, 6],
  thermocouples_per_sample: 2, ambient_column: 7, current_column: 8, excluded_rows: [], current_multiplier: 1 };
const layout: ChannelLayout = { ...initial, current_columns: [8, 10], stable_current_columns: [10],
  sample_groups: [{ sample_id: '1', columns: [3, 4] }, { sample_id: '2', columns: [5, 6] }],
  issues: [], zero_intercept_default: false };

function Editor({ withParameters = false }: { withParameters?: boolean }) {
  const [selection, setSelection] = useState(initial);
  return <>{withParameters && <label>Ambient Role<select value={selection.ambient_column} onChange={event => {
    const ambient_column = Number(event.target.value);
    setSelection(old => ({ ...old, ambient_column, temperature_columns: old.temperature_columns.filter(column => column !== ambient_column) }));
  }}>{table.rows[0].map((_, index) => <option key={index} value={index + 1}>{index + 1}</option>)}</select></label>}
    <DataPreview table={table} selection={selection} layout={layout} issues={[]} disabled={false}
    onChange={patch => setSelection(old => ({ ...old, ...patch }))} />
    <output aria-label="Prepared Selection">{JSON.stringify(selection)}</output></>;
}
function selected() { return JSON.parse(screen.getByLabelText('Prepared Selection').textContent!) as DataSelection; }

describe('unified scanner data editing', () => {
  it('shows source metadata, sample groups and retained electrical roles directly in the grid', () => {
    render(<Editor />);
    const grid = screen.getByRole('region', { name: 'Scanner Data Preview' });
    expect(within(grid).getByText('Scan')).toBeTruthy();
    expect(within(grid).getByText('Time')).toBeTruthy();
    expect(within(grid).getByText('Sample 1')).toBeTruthy();
    expect(within(grid).getByText('Sample 2')).toBeTruthy();
    expect(within(grid).getByText('Retained / Not Plotted · Stable')).toBeTruthy();
    expect(within(grid).getByText('0.009999')).toBeTruthy();
    expect(screen.queryByText('All Source Columns')).toBeNull();
    expect(screen.queryByRole('button', { name: /Replace|Adjust Channels|View Channels/ })).toBeNull();
  });

  it('excludes the failed column and moves a whole spare column into its position without changing source values', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    await user.click(screen.getByLabelText('Select Column D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().temperature_columns).toEqual([3, 5, 6]);
    expect(screen.getByRole('alert').textContent).toContain('Incomplete sample group');
    expect(screen.queryByText('Sample 2 / TC 1')).toBeNull();
    await user.click(screen.getByRole('button', { name: 'Column I Actions' }));
    const menu = screen.getByRole('dialog', { name: 'Column I Actions' });
    await user.selectOptions(within(menu).getByLabelText('Move Before'), '4');
    await user.click(within(menu).getByRole('button', { name: 'Move' }));
    expect(selected().temperature_columns).toEqual([3, 9, 5, 6]);
    expect(screen.queryByRole('alert')).toBeNull();
    const cells = within(screen.getByRole('region', { name: 'Scanner Data Preview' })).getAllByRole('row')[2].querySelectorAll('td');
    expect(Array.from(cells).map(cell => cell.textContent)).toContain('28.5');
    expect(table.rows[1]).toEqual([1, '18:00', 24.1, 25.2, 26.3, 27.4, 20.5, 0.009999, 28.5, 3]);
    await user.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected().temperature_columns).toEqual([3, 5, 6]);
    await user.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected().temperature_columns).toEqual([3, 4, 5, 6]);
  });

  it('moves multiple selected temperature columns as an ordered block, excluding role columns', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    expect((screen.getByLabelText('Select Column G') as HTMLInputElement).disabled).toBe(true);
    expect((screen.getByLabelText('Select Column H') as HTMLInputElement).disabled).toBe(true);
    await user.click(screen.getByLabelText('Select Column E'));
    await user.click(screen.getByLabelText('Select Column F'));
    await user.click(screen.getByRole('button', { name: 'Column E Actions' }));
    const menu = screen.getByRole('dialog', { name: 'Column E Actions' });
    expect(within(menu).getByText('2 Columns Selected')).toBeTruthy();
    await user.selectOptions(within(menu).getByLabelText('Move Before'), '3');
    await user.click(within(menu).getByRole('button', { name: 'Move' }));
    expect(selected().temperature_columns).toEqual([5, 6, 3, 4]);
    expect(selected().ambient_column).toBe(7);
    expect(selected().current_column).toBe(8);
  });

  it('restores rows and columns, keeps row and column selection mutually exclusive, and closes the menu with Escape', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    await user.click(screen.getByLabelText('Select Column D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.click(screen.getByLabelText('Select Column D'));
    await user.click(screen.getByRole('button', { name: 'Restore' }));
    expect(selected().temperature_columns).toEqual([3, 4, 5, 6]);
    await user.click(screen.getByLabelText('Select Column C'));
    await user.click(screen.getByLabelText('Select Row 2'));
    expect((screen.getByLabelText('Select Column C') as HTMLInputElement).checked).toBe(false);
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().excluded_rows).toEqual([2]);
    await user.click(screen.getByLabelText('Select Row 2'));
    await user.click(screen.getByRole('button', { name: 'Restore' }));
    expect(selected().excluded_rows).toEqual([]);
    await user.click(screen.getByRole('button', { name: 'Column C Actions' }));
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(document.activeElement).toBe(screen.getByRole('button', { name: 'Column C Actions' }));
  });

  it('selects explicit row ranges without deleting them, rejects out-of-region ranges, and undoes exclusion', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    await user.click(screen.getByText('Select Rows By Range'));
    await user.type(screen.getByLabelText('Rows To Select'), '1-3');
    await user.click(screen.getByRole('button', { name: 'Select Rows' }));
    expect(screen.getByRole('alert').textContent).toContain('Choose rows 2–3');
    await user.clear(screen.getByLabelText('Rows To Select'));
    await user.type(screen.getByLabelText('Rows To Select'), '2-3');
    await user.click(screen.getByRole('button', { name: 'Select Rows' }));
    expect(selected().excluded_rows).toEqual([]);
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().excluded_rows).toEqual([2, 3]);
    await user.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected().excluded_rows).toEqual([]);
  });

  it('keeps a later role decision protected from old exclusion and undo history', async () => {
    const user = userEvent.setup();
    render(<Editor withParameters />);
    await user.click(screen.getByLabelText('Select Column D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.selectOptions(screen.getByLabelText('Ambient Role'), '4');
    expect((screen.getByLabelText('Select Column D') as HTMLInputElement).disabled).toBe(true);
    expect((screen.getByRole('button', { name: 'Undo' }) as HTMLButtonElement).disabled).toBe(true);
    expect(within(screen.getByRole('columnheader', { name: 'Select Column D D 102 1_B (C) Ambient' })).getByText('Ambient')).toBeTruthy();
    expect(screen.queryByText('Excluded')).toBeNull();
    expect(selected().ambient_column).toBe(4);
  });
});
