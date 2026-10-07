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
function openColumn(letter: string) { fireEvent.contextMenu(screen.getByLabelText(`Select Column ${letter}`).closest('th')!); }

function LongEditor({ end = 900 }: { end?: number }) {
  const [selection, setSelection] = useState({ ...initial, start_row: 774, end_row: end });
  const source = { ...table, rows: [table.rows[0], ...Array.from({ length: end - 1 }, (_, index) =>
    [index + 1, '18:00', 24, 25, 26, 27, 20, 10, 28, 3])] };
  return <><DataPreview table={source} selection={selection} layout={layout} issues={[]} disabled={false}
    onChange={patch => setSelection(old => ({ ...old, ...patch }))} />
    <output aria-label="Prepared Selection">{JSON.stringify(selection)}</output></>;
}

describe('continuous source row selection', () => {
  it('selects both endpoints and offscreen rows using Shift, then excludes and undoes the whole interval', () => {
    render(<LongEditor />);
    fireEvent.click(screen.getByLabelText('Select Scan 773'));
    const viewport = screen.getByRole('region', { name: 'Scanner Data Preview' });
    fireEvent.scroll(viewport, { target: { scrollTop: 1000 } });
    fireEvent.click(screen.getByLabelText('Select Scan 799'), { shiftKey: true });
    expect(screen.getByText('27 Selected')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().excluded_rows).toHaveLength(27);
    expect(selected().excluded_rows[0]).toBe(774);
    expect(selected().excluded_rows.at(-1)).toBe(800);
    fireEvent.scroll(viewport, { target: { scrollTop: 0 } });
    expect(screen.getByLabelText('Select Scan 773').closest('tr')?.getAttribute('aria-label')).toContain('Excluded');
    fireEvent.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected().excluded_rows).toEqual([]);
    expect(screen.queryByRole('button', { name: 'Next' })).toBeNull();
  });

  it('supports reverse Shift checkbox selection and Shift deselection', () => {
    render(<LongEditor />);
    const viewport = screen.getByRole('region', { name: 'Scanner Data Preview' });
    fireEvent.scroll(viewport, { target: { scrollTop: 1000 } });
    fireEvent.click(screen.getByLabelText('Select Scan 799'));
    fireEvent.scroll(viewport, { target: { scrollTop: 0 } });
    fireEvent.click(screen.getByLabelText('Select Scan 773'), { shiftKey: true });
    expect(screen.getByText('27 Selected')).toBeTruthy();
    fireEvent.click(screen.getByLabelText('Select Scan 773'));
    fireEvent.scroll(viewport, { target: { scrollTop: 1000 } });
    fireEvent.click(screen.getByLabelText('Select Scan 799'), { shiftKey: true });
    expect((screen.getByRole('button', { name: 'Exclude Selected' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('reaches the final source row by scrolling without mounting the whole large workbook', () => {
    render(<LongEditor end={20000} />);
    const viewport = screen.getByRole('region', { name: 'Scanner Data Preview' });
    expect(within(viewport).getAllByRole('checkbox').length).toBeLessThan(100);
    fireEvent.click(screen.getByLabelText('Select Scan 773'));
    fireEvent.scroll(viewport, { target: { scrollTop: 1000000 } });
    expect(screen.getByLabelText('Select Scan 19999')).toBeTruthy();
    expect(within(viewport).getAllByRole('checkbox').length).toBeLessThan(100);
    fireEvent.scroll(viewport, { target: { scrollTop: 0 } });
    expect((screen.getByLabelText('Select Scan 773') as HTMLInputElement).checked).toBe(true);
  });

  it('selects all source rows rather than only rendered rows and supports clearing the whole selection', () => {
    render(<LongEditor />);
    fireEvent.click(screen.getByLabelText('Select Scan 773'));
    const all = screen.getByLabelText('Select All Rows') as HTMLInputElement;
    expect(all.indeterminate).toBe(true);
    fireEvent.click(all);
    expect(screen.getByText('127 Selected')).toBeTruthy();
    fireEvent.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().excluded_rows).toHaveLength(127);
    expect(selected().excluded_rows.at(-1)).toBe(900);
    fireEvent.click(all);
    fireEvent.click(all);
    expect((screen.getByRole('button', { name: 'Restore' }) as HTMLButtonElement).disabled).toBe(true);
  });

  it('supports Shift+Space and resets the anchor when switching to column editing', () => {
    render(<LongEditor />);
    fireEvent.click(screen.getByLabelText('Select Scan 773'));
    fireEvent.keyDown(screen.getByLabelText('Select Scan 779'), { key: ' ', shiftKey: true });
    expect(screen.getByText('7 Selected')).toBeTruthy();
    fireEvent.click(screen.getByLabelText('Select Column C'));
    fireEvent.keyDown(screen.getByLabelText('Select Scan 781'), { key: ' ', shiftKey: true });
    expect(screen.getByText('1 Selected')).toBeTruthy();
    expect((screen.getByLabelText('Select Column C') as HTMLInputElement).checked).toBe(false);
    fireEvent.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().excluded_rows).toEqual([782]);
  });
});

describe('unified scanner data editing', () => {
  it('places protected-column units immediately after the scanner channel number', () => {
    const source = structuredClone(table);
    source.rows[0][6] = '318 <Ambient T> (C)';
    source.rows[0][7] = '320 <Current> (VDC)';
    source.rows[0][9] = '315 <High Power> (VDC)';
    render(<DataPreview table={source} selection={initial} layout={layout} issues={[]} disabled={false} onChange={() => undefined} />);
    const ambient = screen.getByRole('columnheader', { name: 'G — 318 (°C) Ambient T' });
    const current = screen.getByRole('columnheader', { name: 'H — 320 (A) Current' });
    const auxiliary = screen.getByRole('columnheader', { name: 'J — 315 (A) High Power' });
    expect(within(ambient).getByText('318 (°C)')).toBeTruthy();
    expect(within(ambient).getByText('Ambient T')).toBeTruthy();
    expect(within(current).getByText('320 (A)')).toBeTruthy();
    expect(within(auxiliary).getByText('315 (A)')).toBeTruthy();
    expect(source.rows[0][6]).toBe('318 <Ambient T> (C)');
  });

  it('shows Celsius for ambient and amperes for every current column without inactive controls or repeated role captions', () => {
    render(<Editor />);
    const ambient = screen.getByRole('columnheader', { name: 'G — Ambient (°C)', exact: true });
    const current = screen.getByRole('columnheader', { name: 'H — Current (A)', exact: true });
    const auxiliary = screen.getByRole('columnheader', { name: 'J — Aux (A)', exact: true });
    for (const header of [ambient, current, auxiliary]) {
      expect(within(header).queryByRole('checkbox')).toBeNull();
      fireEvent.contextMenu(header);
      expect(screen.queryByRole('dialog')).toBeNull();
    }
    expect(within(ambient).getByText('Ambient (°C)')).toBeTruthy();
    expect(within(ambient).queryByText('Ambient', { exact: true })).toBeNull();
    expect(within(current).getByText('Current (A)')).toBeTruthy();
    expect(within(current).queryByText('Current', { exact: true })).toBeNull();
    expect(within(auxiliary).getByText('Aux (A)')).toBeTruthy();
    expect(within(auxiliary).queryByText('Retained', { exact: true })).toBeNull();
    expect(table.rows[0][9]).toBe('Aux (VDC)');
    expect(selected()).toEqual(initial);
    expect(screen.getByLabelText('Select Column C')).toBeTruthy();
  });

  it('shows compact unit-free headers and rounded readings while retaining the exact source values', () => {
    const source = structuredClone(table);
    source.rows[0][6] = 'Ambient (C)';
    source.rows[0][7] = 'High Power (VDC)';
    source.rows[1][2] = 24.987654;
    source.rows[1][3] = '-2.34567';
    render(<DataPreview table={source} selection={initial} layout={layout} issues={[]} disabled={false} onChange={() => undefined} />);
    const row = screen.getByLabelText('Select Scan 1').closest('tr')!;
    expect(within(row).getByRole('cell', { name: '25.0', exact: true })).toBeTruthy();
    expect(within(row).getByRole('cell', { name: '-2.3', exact: true })).toBeTruthy();
    expect(within(row).getByRole('cell', { name: '0.01', exact: true }).title).toBe('0.009999');
    expect(within(row).getByRole('cell', { name: '3.00', exact: true })).toBeTruthy();
    const header = screen.getByLabelText('Select Column C').closest('th')!;
    expect(header.textContent).not.toContain('(C)');
    expect(header.textContent).not.toContain('Sample 1 / TC 1');
    const currentHeader = screen.getByRole('columnheader', { name: 'H — High Power (A)' });
    expect(currentHeader.textContent).toContain('High Power (A)');
    expect(currentHeader.textContent).not.toContain('VDC');
    expect(source.rows[1][2]).toBe(24.987654);
    expect(source.rows[1][3]).toBe('-2.34567');
    expect(source.rows[1][7]).toBe(0.009999);
  });

  it('opens column operations by right-click without dropdown buttons and preserves a selected block', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    expect(screen.queryByRole('button', { name: 'Column C Actions' })).toBeNull();
    const header = screen.getByLabelText('Select Column C').closest('th')!;
    fireEvent.click(header);
    expect((screen.getByLabelText('Select Column C') as HTMLInputElement).checked).toBe(true);
    await user.click(screen.getByLabelText('Select Column D'));
    fireEvent.contextMenu(header, { clientX: 200, clientY: 120 });
    const menu = screen.getByRole('dialog', { name: 'Column C Actions' });
    expect(within(menu).getByText('2 Columns Selected')).toBeTruthy();
    await user.click(within(menu).getByRole('button', { name: 'Exclude Columns' }));
    expect(selected().temperature_columns).toEqual([5, 6]);
    header.focus();
    fireEvent.keyDown(header, { key: 'F10', shiftKey: true });
    expect(screen.getByRole('dialog', { name: 'Column C Actions' })).toBeTruthy();
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(document.activeElement).toBe(header);
    fireEvent.contextMenu(screen.getByRole('cell', { name: '24.1', exact: true }), { clientX: 180, clientY: 220 });
    expect(screen.getByRole('dialog', { name: 'Column C Actions' })).toBeTruthy();
  });

  it('keeps A/B as index-only columns without selection or move controls and omits Original Row', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    expect(screen.queryByRole('columnheader', { name: 'Original Row' })).toBeNull();
    expect(screen.queryByLabelText('Select Column A')).toBeNull();
    expect(screen.queryByLabelText('Select Column B')).toBeNull();
    expect(screen.queryByRole('button', { name: 'Column A Actions' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Column B Actions' })).toBeNull();
    expect(screen.getByRole('columnheader', { name: 'A Scan' })).toBeTruthy();
    expect(screen.getByRole('columnheader', { name: 'B Time' })).toBeTruthy();
    openColumn('I');
    const destination = within(screen.getByRole('dialog')).getByLabelText('Move Before');
    expect(within(destination).queryByRole('option', { name: 'A — Scan' })).toBeNull();
    expect(within(destination).queryByRole('option', { name: 'B — Time' })).toBeNull();
    expect(selected().temperature_columns).toEqual([3, 4, 5, 6]);
  });

  it('highlights the whole clicked row without changing batch selection or prepared data', () => {
    render(<Editor />);
    fireEvent.click(screen.getByLabelText('Select Column C'));
    fireEvent.click(screen.getByRole('cell', { name: '24.1', exact: true }));
    const firstRow = screen.getByLabelText('Select Scan 1').closest('tr')!;
    expect(firstRow.getAttribute('aria-current')).toBe('true');
    expect((screen.getByLabelText('Select Scan 1') as HTMLInputElement).checked).toBe(false);
    expect((screen.getByLabelText('Select Column C') as HTMLInputElement).checked).toBe(true);
    fireEvent.click(screen.getByRole('cell', { name: '18:01', exact: true }));
    expect(firstRow.getAttribute('aria-current')).toBeNull();
    expect(screen.getByLabelText('Select Scan 2').closest('tr')?.getAttribute('aria-current')).toBe('true');
    expect(selected()).toEqual(initial);
  });

  it('retains the highlighted source row across virtual scrolling independently of range selection', () => {
    render(<LongEditor />);
    const viewport = screen.getByRole('region', { name: 'Scanner Data Preview' });
    fireEvent.click(within(viewport).getByRole('cell', { name: '773', exact: true }));
    fireEvent.scroll(viewport, { target: { scrollTop: 1000 } });
    fireEvent.scroll(viewport, { target: { scrollTop: 0 } });
    expect(screen.getByLabelText('Select Scan 773').closest('tr')?.getAttribute('aria-current')).toBe('true');
    expect((screen.getByLabelText('Select Scan 773') as HTMLInputElement).checked).toBe(false);
  });

  it('shows source metadata, sample groups and electrical units directly in the grid', () => {
    render(<Editor />);
    const grid = screen.getByRole('region', { name: 'Scanner Data Preview' });
    expect(within(grid).getByText('Scan')).toBeTruthy();
    expect(within(grid).getByText('Time')).toBeTruthy();
    expect(within(grid).getByText('Sample 1')).toBeTruthy();
    expect(within(grid).getByText('Sample 2')).toBeTruthy();
    expect(within(grid).getByText('Aux (A)')).toBeTruthy();
    expect(within(grid).getByText('0.01').title).toBe('0.009999');
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
    openColumn('I');
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
    expect(screen.queryByLabelText('Select Column G')).toBeNull();
    expect(screen.queryByLabelText('Select Column H')).toBeNull();
    await user.click(screen.getByLabelText('Select Column E'));
    await user.click(screen.getByLabelText('Select Column F'));
    openColumn('E');
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
    await user.click(screen.getByLabelText('Select Scan 1'));
    expect((screen.getByLabelText('Select Column C') as HTMLInputElement).checked).toBe(false);
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().excluded_rows).toEqual([2]);
    await user.click(screen.getByLabelText('Select Scan 1'));
    await user.click(screen.getByRole('button', { name: 'Restore' }));
    expect(selected().excluded_rows).toEqual([]);
    openColumn('C');
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(document.activeElement).toBe(screen.getByLabelText('Select Column C').closest('th'));
  });

  it('removes the row-number range form while retaining reversible Shift selection', () => {
    render(<Editor />);
    expect(screen.queryByText('Select Rows By Range')).toBeNull();
    expect(screen.queryByLabelText('Rows To Select')).toBeNull();
    expect(screen.queryByRole('button', { name: 'Select Rows', exact: true })).toBeNull();
    const first = screen.getByLabelText('Select Scan 1');
    expect(first.getAttribute('title')).toBe('Scan 1');
    fireEvent.click(first);
    fireEvent.click(screen.getByLabelText('Select Scan 2'), { shiftKey: true });
    expect(selected().excluded_rows).toEqual([]);
    fireEvent.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().excluded_rows).toEqual([2, 3]);
    fireEvent.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected().excluded_rows).toEqual([]);
  });

  it('keeps a later role decision protected from old exclusion and undo history', async () => {
    const user = userEvent.setup();
    render(<Editor withParameters />);
    await user.click(screen.getByLabelText('Select Column D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.selectOptions(screen.getByLabelText('Ambient Role'), '4');
    expect(screen.queryByLabelText('Select Column D')).toBeNull();
    expect((screen.getByRole('button', { name: 'Undo' }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getByRole('columnheader', { name: 'D — 102 (°C) 1_B' })).toBeTruthy();
    expect(screen.queryByText('Excluded')).toBeNull();
    expect(selected().ambient_column).toBe(4);
  });
});
