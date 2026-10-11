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

function Editor({ withParameters = false, source = table, starting = initial, importedLayout = layout }: {
  withParameters?: boolean; source?: WorkbookTable; starting?: DataSelection; importedLayout?: ChannelLayout;
}) {
  const [selection, setSelection] = useState(starting);
  return <>{withParameters && <label>Ambient Role<select value={selection.ambient_column} onChange={event => {
    const ambient_column = Number(event.target.value);
    setSelection(old => ({ ...old, ambient_column, temperature_columns: old.temperature_columns.filter(column => column !== ambient_column) }));
  }}>{source.rows[0].map((_, index) => <option key={index} value={index + 1}>{index + 1}</option>)}</select></label>}
    <DataPreview table={source} selection={selection} layout={importedLayout} issues={[]} disabled={false}
    onChange={patch => setSelection(old => ({ ...old, ...patch }))} />
    <output aria-label="Prepared Selection">{JSON.stringify(selection)}</output></>;
}
function selected() { return JSON.parse(screen.getByLabelText('Prepared Selection').textContent!) as DataSelection; }
function columnHeader(letter: string) { return screen.getByRole('columnheader', { name: new RegExp(`^Source Column ${letter.charCodeAt(0) - 64}: `) }); }
function openColumn(letter: string) { fireEvent.contextMenu(columnHeader(letter)); }

describe('column header selection', () => {
  it('distinguishes current ambient from unused temperatures and permits normal operations after a role switch', async () => {
    const user = userEvent.setup();
    render(<Editor withParameters />);
    expect(columnHeader('G').getAttribute('aria-description')).toBe('Ambient Temperature (Protected)');
    expect(columnHeader('I').getAttribute('aria-description')).toBe('Unused Temperature');
    await user.click(columnHeader('G'));
    openColumn('G');
    expect(screen.queryByRole('dialog')).toBeNull();
    expect((screen.getByRole('button', { name: 'Exclude Selected' }) as HTMLButtonElement).disabled).toBe(true);
    await user.selectOptions(screen.getByLabelText('Ambient Role'), '3');
    expect(columnHeader('C').getAttribute('aria-description')).toBe('Ambient Temperature (Protected)');
    expect(columnHeader('G').getAttribute('aria-description')).toBe('Unused Temperature');
    await user.click(columnHeader('G'));
    expect(columnHeader('G').getAttribute('aria-selected')).toBe('true');
    openColumn('G');
    await user.click(screen.getByRole('button', { name: 'Exclude Column', exact: true }));
    expect(columnHeader('G').getAttribute('aria-description')).toBe('Excluded');
    expect(selected().temperature_columns).toEqual([4, 5, 6]);
    openColumn('G');
    await user.click(screen.getByRole('button', { name: 'Restore Column', exact: true }));
    expect(columnHeader('G').getAttribute('aria-description')).toBe('Unused Temperature');
    expect(selected().temperature_columns).toEqual([4, 5, 6]);
    openColumn('G');
    await user.click(screen.getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menuitem', { name: '102 1_B', exact: true }));
    expect(selected().temperature_columns).toEqual([7, 4, 5, 6]);
    expect(selected().sample_groups).toEqual([[7, 4], [5, 6]]);
    expect(columnHeader('G').getAttribute('aria-description')).toBe('Sample 1');
    expect(screen.queryByText(/Incomplete sample group/)).toBeNull();
    expect(selected().ambient_column).toBe(3);
  });

  it('selects with click, toggles nonadjacent columns with Ctrl and keeps the batch for right-click exclusion and undo', () => {
    render(<Editor />);
    expect(within(columnHeader('C')).queryByRole('checkbox')).toBeNull();
    fireEvent.click(columnHeader('C'));
    fireEvent.click(columnHeader('E'), { ctrlKey: true });
    expect(screen.getByText('2 Selected')).toBeTruthy();
    fireEvent.click(columnHeader('E'), { ctrlKey: true });
    expect(columnHeader('E').getAttribute('aria-selected')).toBe('false');
    fireEvent.click(columnHeader('E'), { ctrlKey: true });
    fireEvent.contextMenu(columnHeader('C'));
    fireEvent.click(within(screen.getByRole('dialog')).getByRole('button', { name: 'Exclude Columns' }));
    expect(selected().temperature_columns).toEqual([4, 6]);
    fireEvent.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected()).toEqual(initial);
    fireEvent.click(columnHeader('C'));
    fireEvent.click(columnHeader('F'));
    expect(columnHeader('C').getAttribute('aria-selected')).toBe('false');
    expect(columnHeader('F').getAttribute('aria-selected')).toBe('true');
  });

  it('extends forward and reverse Shift ranges by displayed order, skips protected roles and resets after row selection', () => {
    render(<Editor />);
    fireEvent.click(columnHeader('F'));
    fireEvent.click(columnHeader('C'), { shiftKey: true });
    expect(screen.getByText('4 Selected')).toBeTruthy();
    fireEvent.click(columnHeader('E'), { shiftKey: true });
    expect(screen.getByText('2 Selected')).toBeTruthy();
    fireEvent.click(columnHeader('E'));
    fireEvent.click(columnHeader('I'), { shiftKey: true });
    expect(screen.getByText('3 Selected')).toBeTruthy();
    for (const letter of ['G', 'H', 'J']) {
      expect(columnHeader(letter).getAttribute('aria-selected')).toBeNull();
      fireEvent.click(columnHeader(letter), { ctrlKey: true });
    }
    expect(screen.getByText('3 Selected')).toBeTruthy();
    fireEvent.click(screen.getByLabelText('Select Scan 1'));
    fireEvent.click(columnHeader('D'), { shiftKey: true });
    expect(screen.getByText('1 Selected')).toBeTruthy();
    expect((screen.getByLabelText('Select Scan 1') as HTMLInputElement).checked).toBe(false);
    fireEvent.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().temperature_columns).toEqual([3, 5, 6]);
  });

  it('supports additive ranges and Meta toggling while disabled headers cannot alter selection or open actions', () => {
    const { rerender } = render(<DataPreview table={table} selection={initial} layout={layout} issues={[]}
      disabled={false} onChange={() => undefined} />);
    fireEvent.click(columnHeader('C'));
    fireEvent.click(columnHeader('E'), { metaKey: true });
    fireEvent.click(columnHeader('F'), { ctrlKey: true, shiftKey: true });
    expect(screen.getByText('3 Selected')).toBeTruthy();
    rerender(<DataPreview table={table} selection={initial} layout={layout} issues={[]}
      disabled={true} onChange={() => undefined} />);
    fireEvent.click(columnHeader('D'));
    fireEvent.keyDown(columnHeader('D'), { key: 'Enter' });
    fireEvent.contextMenu(columnHeader('D'));
    expect(screen.getByText('3 Selected')).toBeTruthy();
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(columnHeader('D').getAttribute('tabindex')).toBeNull();
  });

  it('uses keyboard selection and Shift+F10 for a movable block, then ranges in its new displayed order', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    columnHeader('E').focus();
    fireEvent.keyDown(columnHeader('E'), { key: ' ' });
    fireEvent.keyDown(columnHeader('F'), { key: 'Enter', shiftKey: true });
    fireEvent.keyDown(columnHeader('E'), { key: 'F10', shiftKey: true });
    const menu = screen.getByRole('dialog', { name: 'Column 5 Actions' });
    expect(screen.getByText('2 Selected')).toBeTruthy();
    await user.click(within(menu).getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menuitem', { name: '101 1_A' }));
    expect(selected().temperature_columns).toEqual([5, 6, 3, 4]);
    fireEvent.click(columnHeader('F'));
    fireEvent.click(columnHeader('C'), { shiftKey: true });
    expect(screen.getByText('2 Selected')).toBeTruthy();
    expect(columnHeader('E').getAttribute('aria-selected')).toBe('false');
    expect(columnHeader('D').getAttribute('aria-selected')).toBe('false');
  });
});

function FourThermocoupleEditor({ withParameters = false }: { withParameters?: boolean }) {
  const source: WorkbookTable = { ...table, rows: [
    ['Scan', 'Time', ...Array.from({ length: 12 }, (_, index) =>
      `${101 + index} <${Math.floor(index / 4) + 1}_T${index % 4 + 1}> (C)`), 'Ambient (C)', 'Current (VDC)'],
    [1, '18:00', 21, 99, 23, 24, 31, 99, 33, 34, 41, 99, 43, 44, 20, 10],
  ] };
  const starting = { ...initial, end_row: 2, temperature_columns: [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14],
    thermocouples_per_sample: 4, ambient_column: 15, current_column: 16 };
  return <Editor withParameters={withParameters} source={source} starting={starting} importedLayout={{ ...layout, ...starting,
    current_columns: [16], stable_current_columns: [],
    sample_groups: [{ sample_id: '1', columns: [3, 4, 5, 6] }, { sample_id: '2', columns: [7, 8, 9, 10] },
      { sample_id: '3', columns: [11, 12, 13, 14] }] }} />;
}

function LongEditor({ end = 900 }: { end?: number }) {
  const [selection, setSelection] = useState({ ...initial, start_row: 774, end_row: end });
  const source = { ...table, rows: [table.rows[0], ...Array.from({ length: end - 1 }, (_, index) =>
    [index + 1, '18:00', 24, 25, 26, 27, 20, 10, 28, 3])] };
  return <><DataPreview table={source} selection={selection} layout={layout} issues={[]} disabled={false}
    onChange={patch => setSelection(old => ({ ...old, ...patch }))} />
    <output aria-label="Prepared Selection">{JSON.stringify(selection)}</output></>;
}

describe('continuous source row selection', () => {
  it('preserves balanced exclusions and original sample ownership through repeated ambient-role changes', async () => {
    const user = userEvent.setup();
    render(<FourThermocoupleEditor withParameters />);
    for (const letter of ['D', 'H', 'L']) fireEvent.click(columnHeader(letter), { ctrlKey: true });
    fireEvent.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    for (let cycle = 0; cycle < 3; cycle++) {
      await user.selectOptions(screen.getByLabelText('Ambient Role'), '3');
      expect(selected().sample_groups).toEqual([[5, 6], [7, 9, 10], [11, 13, 14]]);
      await user.selectOptions(screen.getByLabelText('Ambient Role'), '15');
      expect(selected().sample_groups).toEqual([[3, 5, 6], [7, 9, 10], [11, 13, 14]]);
      expect(selected().thermocouples_per_sample).toBe(3);
      expect(screen.queryByRole('alert')).toBeNull();
    }
    for (const letter of ['D', 'H', 'L']) fireEvent.click(columnHeader(letter), { ctrlKey: true });
    fireEvent.click(screen.getByRole('button', { name: 'Restore' }));
    expect(selected().sample_groups).toEqual([[3, 4, 5, 6], [7, 8, 9, 10], [11, 12, 13, 14]]);
    expect(selected().thermocouples_per_sample).toBe(4);
  });
  it('preserves three original samples when their second thermocouples are excluded, restores them and undoes both count changes', () => {
    render(<FourThermocoupleEditor />);
    for (const letter of ['D', 'H', 'L']) fireEvent.click(columnHeader(letter), { ctrlKey: true });
    fireEvent.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().thermocouples_per_sample).toBe(3);
    expect(selected().temperature_columns).toEqual([3, 5, 6, 7, 9, 10, 11, 13, 14]);
    expect(selected().sample_groups).toEqual([[3, 5, 6], [7, 9, 10], [11, 13, 14]]);
    expect(screen.getByText('3 Samples · 3 TC/Sample · 9 Channels')).toBeTruthy();
    expect(screen.queryByRole('alert')).toBeNull();
    const headers = screen.getAllByRole('columnheader');
    expect(headers.slice(-3)).toEqual(['D', 'H', 'L'].map(columnHeader));
    for (const letter of ['D', 'H', 'L']) fireEvent.click(columnHeader(letter), { ctrlKey: true });
    fireEvent.click(screen.getByRole('button', { name: 'Restore' }));
    expect(selected().thermocouples_per_sample).toBe(4);
    expect(selected().temperature_columns).toEqual([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]);
    fireEvent.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected().thermocouples_per_sample).toBe(3);
    fireEvent.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected().thermocouples_per_sample).toBe(4);
  });
  it('keeps each temperature sample contiguous, followed by ambient, main current and other currents, without a second header band', () => {
    const source = { ...table, rows: [
      ['Scan', 'Time', '101 <1_A> (C)', '102 <1_B> (C)', 'Ambient (C)', 'Current (VDC)',
        '103 <2_A> (C)', '104 <2_B> (C)', 'Aux (VDC)', 'Spare (C)'],
      [1, '18:00', 24, 25, 20, 10, 26, 27, 3, 28],
    ] };
    const starting = { ...initial, end_row: 2, temperature_columns: [3, 4, 7, 8], ambient_column: 5, current_column: 6 };
    render(<Editor source={source} starting={starting} importedLayout={{ ...layout, ...starting,
      current_columns: [6, 9], stable_current_columns: [9],
      sample_groups: [{ sample_id: '1', columns: [3, 4] }, { sample_id: '2', columns: [7, 8] }] }} />);
    const headers = within(screen.getByRole('region', { name: 'Scanner Data Preview' })).getAllByRole('columnheader');
    expect(within(headers[1]).queryByText('A', { exact: true })).toBeNull();
    expect(within(headers[2]).queryByText('B', { exact: true })).toBeNull();
    expect(headers.slice(3)).toEqual(['C', 'D', 'G', 'H', 'E', 'F', 'I', 'J'].map(columnHeader));
    expect(screen.queryByText('Sample 1', { exact: true })).toBeNull();
    expect(headers[3].getAttribute('aria-description')).toBe('Sample 1');
    expect(headers[5].getAttribute('aria-description')).toBe('Sample 2');
    expect(selected()).toEqual(starting);
  });
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
    fireEvent.click(columnHeader('C'));
    fireEvent.keyDown(screen.getByLabelText('Select Scan 781'), { key: ' ', shiftKey: true });
    expect(screen.getByText('1 Selected')).toBeTruthy();
    expect(columnHeader('C').getAttribute('aria-selected')).toBe('false');
    fireEvent.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().excluded_rows).toEqual([782]);
  });
});

describe('unified scanner data editing', () => {
  it('moves before an excluded destination at its displayed tail position rather than its original slot', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    openColumn('C');
    await user.click(screen.getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menuitem', { name: '102 1_B' }));
    expect(selected().temperature_columns).toEqual([5, 6, 3]);
    expect(selected().sample_groups).toEqual([[5, 6], [3]]);
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Restore' }));
    expect(selected().temperature_columns).toEqual([5, 6, 3, 4]);
    expect(selected().sample_groups).toEqual([[5, 6], [3, 4]]);
    expect(screen.queryByRole('alert')).toBeNull();
  });
  it('restores the last effective channel after a move and repeated ambient suspension without losing its name', async () => {
    const user = userEvent.setup();
    render(<Editor withParameters starting={{ ...initial, temperature_columns: [3], sample_groups: [[3]], thermocouples_per_sample: 1 }} />);
    fireEvent.change(screen.getByLabelText('Measurement Name, Channel 101'), { target: { value: 'Renamed (VDC)' } });
    openColumn('C');
    await user.click(screen.getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menuitem', { name: 'End Of Temperature Columns' }));
    for (let cycle = 0; cycle < 3; cycle++) {
      await user.selectOptions(screen.getByLabelText('Ambient Role'), '3');
      expect(selected().temperature_columns).toEqual([]);
      await user.selectOptions(screen.getByLabelText('Ambient Role'), '7');
      expect(selected().temperature_columns).toEqual([3]);
      expect(selected().sample_groups).toEqual([[3]]);
      expect(screen.getByLabelText('Measurement Name, Channel 101').getAttribute('value')).toBe('Renamed (VDC)');
    }
    expect(table.rows[0][2]).toBe('101 <1_A> (C)');
  });
  it('uses consecutive effective columns after an incomplete cross-sample move and restoration, with undo', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    openColumn('C');
    await user.click(screen.getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menuitem', { name: '104 2_B' }));
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Restore', exact: true }));
    expect(selected().temperature_columns).toEqual([5, 3, 6, 4]);
    expect(selected().sample_groups).toEqual([[5, 3], [6, 4]]);
    expect(selected().thermocouples_per_sample).toBe(2);
    expect(screen.queryByRole('alert')).toBeNull();
    await user.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected().temperature_columns).toEqual([5, 3, 6]);
    expect(screen.getByRole('alert').textContent).toContain('Incomplete sample group');
    await user.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected().temperature_columns).toEqual([3, 5, 6]);
  });
  it('opens move destinations as a submenu without changing data and supports keyboard return and selection', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    openColumn('E');
    const move = screen.getByRole('button', { name: 'Move Before', exact: true });
    expect(move.getAttribute('aria-expanded')).toBe('false');
    expect(screen.queryByRole('menu', { name: 'Move Before Destinations' })).toBeNull();
    move.focus();
    await user.keyboard('{ArrowRight}');
    const destinations = screen.getByRole('menu', { name: 'Move Before Destinations' });
    expect(move.getAttribute('aria-expanded')).toBe('true');
    expect(selected()).toEqual(initial);
    expect(document.activeElement).toBe(within(destinations).getByRole('menuitem', { name: '101 1_A' }));
    await user.tab({ shift: true });
    expect(document.activeElement).toBe(move);
    await user.keyboard('{ArrowRight}');
    expect(document.activeElement).toBe(within(destinations).getByRole('menuitem', { name: '101 1_A' }));
    await user.keyboard('{ArrowDown}');
    expect(document.activeElement).toBe(within(destinations).getByRole('menuitem', { name: '102 1_B' }));
    await user.keyboard('{ArrowLeft}');
    expect(screen.queryByRole('menu')).toBeNull();
    expect(document.activeElement).toBe(move);
    await user.click(move);
    await user.keyboard('{End}');
    expect(document.activeElement).toBe(screen.getByRole('menuitem', { name: 'End Of Temperature Columns' }));
    await user.keyboard('{Home}');
    expect(document.activeElement).toBe(screen.getByRole('menuitem', { name: '101 1_A' }));
    await user.keyboard('{Escape}');
    expect(screen.queryByRole('menu')).toBeNull();
    expect(screen.getByRole('dialog')).toBeTruthy();
    expect(document.activeElement).toBe(move);
    await user.click(move);
    fireEvent.scroll(screen.getByRole('menu'), { target: { scrollTop: 100 } });
    expect(screen.getByRole('menu')).toBeTruthy();
    await user.click(screen.getByRole('menuitem', { name: '101 1_A' }));
    expect(selected().temperature_columns).toEqual([5, 3, 4, 6]);
    expect(screen.queryByRole('dialog')).toBeNull();
    await user.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected()).toEqual(initial);
  });

  it('keeps move destinations to the right and within narrow viewport bounds near its right edge', async () => {
    const user = userEvent.setup();
    const originalWidth = window.innerWidth;
    Object.defineProperty(window, 'innerWidth', { configurable: true, value: 360 });
    try {
      render(<Editor />);
      fireEvent.contextMenu(columnHeader('E'), { clientX: 350, clientY: 500 });
      await user.click(screen.getByRole('button', { name: 'Move Before', exact: true }));
      const menu = screen.getByRole('dialog') as HTMLElement;
      const destinations = screen.getByRole('menu') as HTMLElement;
      const mainLeft = Number.parseFloat(menu.style.left);
      const mainRight = mainLeft + Number.parseFloat(menu.style.width);
      const targetLeft = Number.parseFloat(destinations.style.left);
      const targetRight = targetLeft + Number.parseFloat(destinations.style.width);
      expect(mainLeft).toBeGreaterThanOrEqual(0);
      expect(targetLeft).toBeGreaterThan(mainRight);
      expect(targetRight).toBeLessThanOrEqual(window.innerWidth);
      expect(selected()).toEqual(initial);
    } finally {
      Object.defineProperty(window, 'innerWidth', { configurable: true, value: originalWidth });
    }
  });

  it('moves immediately when a destination is chosen, closes the menu and supports undo and end placement', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    openColumn('E');
    const menu = screen.getByRole('dialog', { name: 'Column 5 Actions' });
    const destination = within(menu).getByRole('button', { name: 'Move Before', exact: true });
    expect(destination.getAttribute('aria-expanded')).toBe('false');
    expect(within(menu).queryByText('Choose Column', { exact: true })).toBeNull();
    expect(selected()).toEqual(initial);
    expect(within(menu).queryByRole('button', { name: 'Move', exact: true })).toBeNull();
    await user.click(destination);
    await user.click(screen.getByRole('menuitem', { name: '101 1_A' }));
    expect(selected().temperature_columns).toEqual([5, 3, 4, 6]);
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(document.activeElement).toBe(columnHeader('E'));
    await user.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected()).toEqual(initial);
    openColumn('C');
    await user.click(screen.getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menuitem', { name: 'End Of Temperature Columns' }));
    expect(selected().temperature_columns).toEqual([4, 5, 6, 3]);
    expect(selected().ambient_column).toBe(7);
    expect(selected().current_column).toBe(8);
    expect(screen.queryByRole('dialog')).toBeNull();
    await user.click(screen.getByRole('button', { name: 'Undo' }));
    expect(selected()).toEqual(initial);
  });

  it('dismisses the compact column menu by outside click or Escape and keeps keyboard focus within its actions', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    openColumn('C');
    const menu = screen.getByRole('dialog', { name: 'Column 3 Actions' });
    expect(within(menu).queryByText('101 1_A', { exact: true })).toBeNull();
    expect(within(menu).queryByRole('button', { name: 'Close Column Actions' })).toBeNull();
    const exclude = within(menu).getByRole('button', { name: 'Exclude Column', exact: true });
    expect(document.activeElement).toBe(exclude);
    await user.tab({ shift: true });
    expect(document.activeElement).toBe(within(menu).getByRole('button', { name: 'Move Before', exact: true }));
    await user.tab();
    expect(document.activeElement).toBe(exclude);
    await user.click(screen.getByRole('heading', { name: 'Data Preview' }));
    expect(screen.queryByRole('dialog')).toBeNull();
    openColumn('C');
    await user.keyboard('{Escape}');
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(document.activeElement).toBe(columnHeader('C'));
    expect(selected()).toEqual(initial);
  });

  it('places protected-column units immediately after the scanner channel number', () => {
    const source = structuredClone(table);
    source.rows[0][6] = '318 <Ambient T> (C)';
    source.rows[0][7] = '320 <Current> (VDC)';
    source.rows[0][9] = '315 <High Power> (VDC)';
    render(<DataPreview table={source} selection={initial} layout={layout} issues={[]} disabled={false} onChange={() => undefined} />);
    const ambient = screen.getByRole('columnheader', { name: 'Source Column 7: 318 (°C) Ambient T' });
    const current = screen.getByRole('columnheader', { name: 'Source Column 8: 320 (A) Current' });
    const auxiliary = screen.getByRole('columnheader', { name: 'Source Column 10: 315 (A) High Power' });
    expect(within(ambient).getByText('318 (°C)')).toBeTruthy();
    expect(within(ambient).getByDisplayValue('Ambient T')).toBeTruthy();
    expect(within(current).getByText('320 (A)')).toBeTruthy();
    expect(within(auxiliary).getByText('315 (A)')).toBeTruthy();
    expect(source.rows[0][6]).toBe('318 <Ambient T> (C)');
  });

  it('shows Celsius for ambient and amperes for every current column without inactive controls or repeated role captions', () => {
    render(<Editor />);
    const ambient = screen.getByRole('columnheader', { name: 'Source Column 7: Ambient (°C)', exact: true });
    const current = screen.getByRole('columnheader', { name: 'Source Column 8: Current (A)', exact: true });
    const auxiliary = screen.getByRole('columnheader', { name: 'Source Column 10: Aux (A)', exact: true });
    for (const header of [ambient, current, auxiliary]) {
      expect(within(header).queryByRole('checkbox')).toBeNull();
      expect(header.getAttribute('tabindex')).toBeNull();
      expect(header.getAttribute('aria-selected')).toBeNull();
      fireEvent.contextMenu(header);
      expect(screen.queryByRole('dialog')).toBeNull();
    }
    expect(within(ambient).getByDisplayValue('Ambient')).toBeTruthy();
    expect(within(ambient).getByText('(°C)')).toBeTruthy();
    expect(within(ambient).queryByText('Ambient', { exact: true })).toBeNull();
    expect(within(current).getByText('Current (A)')).toBeTruthy();
    expect(within(current).queryByText('Current', { exact: true })).toBeNull();
    expect(within(auxiliary).getByText('Aux (A)')).toBeTruthy();
    expect(within(auxiliary).queryByText('Retained', { exact: true })).toBeNull();
    expect(table.rows[0][9]).toBe('Aux (VDC)');
    expect(selected()).toEqual(initial);
    expect(columnHeader('C').getAttribute('tabindex')).toBe('0');
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
    const header = columnHeader('C');
    expect(header.textContent).not.toContain('(C)');
    expect(header.textContent).not.toContain('Sample 1 / TC 1');
    const currentHeader = screen.getByRole('columnheader', { name: 'Source Column 8: High Power (A)' });
    expect(currentHeader.textContent).toContain('High Power (A)');
    expect(currentHeader.textContent).not.toContain('VDC');
    expect(source.rows[1][2]).toBe(24.987654);
    expect(source.rows[1][3]).toBe('-2.34567');
    expect(source.rows[1][7]).toBe(0.009999);
  });

  it('opens column operations by right-click without dropdown buttons and preserves a selected block', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    expect(screen.queryByRole('button', { name: 'Column 3 Actions' })).toBeNull();
    const header = columnHeader('C');
    fireEvent.click(header);
    expect(header.getAttribute('aria-selected')).toBe('true');
    fireEvent.click(columnHeader('D'), { ctrlKey: true });
    fireEvent.contextMenu(header, { clientX: 200, clientY: 120 });
    const menu = screen.getByRole('dialog', { name: 'Column 3 Actions' });
    expect(screen.getByText('2 Selected')).toBeTruthy();
    await user.click(within(menu).getByRole('button', { name: 'Exclude Columns' }));
    expect(selected().temperature_columns).toEqual([5, 6]);
    header.focus();
    fireEvent.keyDown(header, { key: 'F10', shiftKey: true });
    expect(screen.getByRole('dialog', { name: 'Column 3 Actions' })).toBeTruthy();
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(document.activeElement).toBe(header);
    fireEvent.contextMenu(screen.getByRole('cell', { name: '24.1', exact: true }), { clientX: 180, clientY: 220 });
    expect(screen.getByRole('dialog', { name: 'Column 3 Actions' })).toBeTruthy();
  });

  it('keeps A/B as index-only columns without selection or move controls and omits Original Row', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    expect(screen.queryByRole('columnheader', { name: 'Original Row' })).toBeNull();
    expect(screen.queryByLabelText('Select Column A')).toBeNull();
    expect(screen.queryByLabelText('Select Column B')).toBeNull();
    expect(screen.queryByRole('button', { name: 'Column 1 Actions' })).toBeNull();
    expect(screen.queryByRole('button', { name: 'Column 2 Actions' })).toBeNull();
    expect(screen.getByRole('columnheader', { name: 'Source Column 1: Scan' })).toBeTruthy();
    expect(screen.getByRole('columnheader', { name: 'Source Column 2: Time' })).toBeTruthy();
    for (const name of ['Source Column 1: Scan', 'Source Column 2: Time']) {
      const header = screen.getByRole('columnheader', { name });
      fireEvent.click(header, { ctrlKey: true });
      expect(header.getAttribute('aria-selected')).toBeNull();
      expect(header.getAttribute('tabindex')).toBeNull();
    }
    openColumn('I');
    await user.click(screen.getByRole('button', { name: 'Move Before', exact: true }));
    const destination = screen.getByRole('menu', { name: 'Move Before Destinations' });
    for (const name of ['Scan', 'Time', 'Ambient (°C)', 'Current (A)', 'Spare', 'Aux (A)']) {
      expect(within(destination).queryByRole('menuitem', { name, exact: true })).toBeNull();
    }
    expect(selected().temperature_columns).toEqual([3, 4, 5, 6]);
  });

  it('clears temporary row and column highlights outside the editor while retaining checked rows and their Shift anchor', async () => {
    const user = userEvent.setup();
    render(<><Editor /><button type="button">Outside Editor</button></>);
    await user.click(columnHeader('C'));
    await user.click(screen.getByRole('cell', { name: '24.1', exact: true }));
    const firstRow = screen.getByLabelText('Select Scan 1').closest('tr')!;
    expect(firstRow.getAttribute('aria-current')).toBe('true');
    await user.click(screen.getByRole('button', { name: 'Outside Editor' }));
    expect(firstRow.getAttribute('aria-current')).toBeNull();
    expect(columnHeader('C').getAttribute('aria-selected')).toBe('false');
    fireEvent.click(columnHeader('E'), { shiftKey: true });
    expect(columnHeader('E').getAttribute('aria-selected')).toBe('true');
    expect(columnHeader('C').getAttribute('aria-selected')).toBe('false');
    expect(columnHeader('D').getAttribute('aria-selected')).toBe('false');
    await user.click(screen.getByLabelText('Select Scan 1'));
    await user.click(screen.getByRole('button', { name: 'Outside Editor' }));
    expect(firstRow.getAttribute('aria-current')).toBeNull();
    expect((screen.getByLabelText('Select Scan 1') as HTMLInputElement).checked).toBe(true);
    fireEvent.click(screen.getByLabelText('Select Scan 2'), { shiftKey: true });
    expect((screen.getByLabelText('Select Scan 1') as HTMLInputElement).checked).toBe(true);
    expect((screen.getByLabelText('Select Scan 2') as HTMLInputElement).checked).toBe(true);
    expect(screen.getByText('2 Selected')).toBeTruthy();
    expect(selected()).toEqual(initial);
  });

  it('retains temporary highlights for name edits, editor controls and the portalled column menu and submenu', async () => {
    const user = userEvent.setup();
    render(<><Editor /><button type="button">Outside Editor</button></>);
    await user.click(columnHeader('C'));
    await user.click(screen.getByRole('cell', { name: '24.1', exact: true }));
    const firstRow = screen.getByLabelText('Select Scan 1').closest('tr')!;
    await user.click(screen.getByLabelText('Measurement Name, Channel 101'));
    await user.type(screen.getByLabelText('Measurement Name, Channel 101'), '-edited');
    await user.click(screen.getByRole('button', { name: 'Undo' }));
    expect(firstRow.getAttribute('aria-current')).toBe('true');
    expect(columnHeader('C').getAttribute('aria-selected')).toBe('true');
    openColumn('C');
    await user.click(screen.getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menu', { name: 'Move Before Destinations' }));
    expect(firstRow.getAttribute('aria-current')).toBe('true');
    expect(columnHeader('C').getAttribute('aria-selected')).toBe('true');
    expect(screen.getByText('1 Selected')).toBeTruthy();
    await user.click(screen.getByRole('button', { name: 'Outside Editor' }));
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(firstRow.getAttribute('aria-current')).toBeNull();
    expect(columnHeader('C').getAttribute('aria-selected')).toBe('false');
    expect(selected().temperature_columns).toEqual(initial.temperature_columns);
    expect(selected().channel_names).toEqual({ 3: '1_A-edited' });
    await user.click(columnHeader('C'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().temperature_columns).toEqual([4, 5, 6]);
    openColumn('C');
    await user.click(screen.getByRole('button', { name: 'Restore Column', exact: true }));
    expect(selected().temperature_columns).toEqual(initial.temperature_columns);
    openColumn('C');
    await user.click(screen.getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menuitem', { name: 'End Of Temperature Columns' }));
    expect(selected().temperature_columns).toEqual([4, 5, 6, 3]);
  });

  it('highlights the whole clicked row without changing batch selection or prepared data', () => {
    render(<Editor />);
    fireEvent.click(columnHeader('C'));
    fireEvent.click(screen.getByRole('cell', { name: '24.1', exact: true }));
    const firstRow = screen.getByLabelText('Select Scan 1').closest('tr')!;
    expect(firstRow.getAttribute('aria-current')).toBe('true');
    expect((screen.getByLabelText('Select Scan 1') as HTMLInputElement).checked).toBe(false);
    expect(columnHeader('C').getAttribute('aria-selected')).toBe('true');
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

  it('shows source metadata and electrical units without a separate sample heading band', () => {
    render(<Editor />);
    const grid = screen.getByRole('region', { name: 'Scanner Data Preview' });
    expect(within(grid).getByText('Scan')).toBeTruthy();
    expect(within(grid).getByText('Time')).toBeTruthy();
    expect(within(grid).queryByText('Sample 1', { exact: true })).toBeNull();
    expect(within(grid).queryByText('Sample 2', { exact: true })).toBeNull();
    expect(within(grid).getByText('Aux (A)')).toBeTruthy();
    expect(within(grid).getByText('0.01').title).toBe('0.009999');
    expect(screen.queryByText('All Source Columns')).toBeNull();
    expect(screen.queryByRole('button', { name: /Replace|Adjust Channels|View Channels/ })).toBeNull();
  });

  it('excludes the failed column and moves a whole spare column into its position without changing source values', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().temperature_columns).toEqual([3, 5, 6]);
    expect(screen.getByRole('alert').textContent).toContain('Incomplete sample group');
    expect(screen.queryByText('Sample 2 / TC 1')).toBeNull();
    openColumn('I');
    const menu = screen.getByRole('dialog', { name: 'Column 9 Actions' });
    await user.click(within(menu).getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menuitem', { name: '103 2_A' }));
    expect(selected().temperature_columns).toEqual([3, 9, 5, 6]);
    expect(screen.queryByRole('alert')).toBeNull();
    const cells = within(screen.getByRole('region', { name: 'Scanner Data Preview' })).getAllByRole('row')[1].querySelectorAll('td');
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
    await user.click(columnHeader('E'));
    fireEvent.click(columnHeader('F'), { ctrlKey: true });
    openColumn('E');
    const menu = screen.getByRole('dialog', { name: 'Column 5 Actions' });
    expect(screen.getByText('2 Selected')).toBeTruthy();
    await user.click(within(menu).getByRole('button', { name: 'Move Before', exact: true }));
    await user.click(screen.getByRole('menuitem', { name: '101 1_A' }));
    expect(selected().temperature_columns).toEqual([5, 6, 3, 4]);
    expect(selected().ambient_column).toBe(7);
    expect(selected().current_column).toBe(8);
  });

  it('restores rows and columns, keeps row and column selection mutually exclusive, and closes the menu with Escape', async () => {
    const user = userEvent.setup();
    render(<Editor />);
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Restore' }));
    expect(selected().temperature_columns).toEqual([3, 4, 5, 6]);
    await user.click(columnHeader('C'));
    await user.click(screen.getByLabelText('Select Scan 1'));
    expect(columnHeader('C').getAttribute('aria-selected')).toBe('false');
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    expect(selected().excluded_rows).toEqual([2]);
    await user.click(screen.getByLabelText('Select Scan 1'));
    await user.click(screen.getByRole('button', { name: 'Restore' }));
    expect(selected().excluded_rows).toEqual([]);
    openColumn('C');
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(screen.queryByRole('dialog')).toBeNull();
    expect(document.activeElement).toBe(columnHeader('C'));
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
    await user.click(columnHeader('D'));
    await user.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.selectOptions(screen.getByLabelText('Ambient Role'), '4');
    expect(screen.queryByLabelText('Select Column D')).toBeNull();
    expect((screen.getByRole('button', { name: 'Undo' }) as HTMLButtonElement).disabled).toBe(true);
    expect(screen.getByRole('columnheader', { name: 'Source Column 4: 102 (°C) 1_B' })).toBeTruthy();
    expect(screen.getByRole('columnheader', { name: 'Source Column 4: 102 (°C) 1_B' }).getAttribute('aria-selected')).toBeNull();
    expect(screen.queryByText('Excluded')).toBeNull();
    expect(selected().ambient_column).toBe(4);
  });

  it('can still restore a different excluded thermocouple after an ambient role decision', async () => {
    const user = userEvent.setup();
    render(<Editor withParameters />);
    for (const letter of ['D', 'F']) fireEvent.click(columnHeader(letter), { ctrlKey: true });
    fireEvent.click(screen.getByRole('button', { name: 'Exclude Selected' }));
    await user.selectOptions(screen.getByLabelText('Ambient Role'), '4');
    fireEvent.click(columnHeader('F'));
    fireEvent.click(screen.getByRole('button', { name: 'Restore' }));
    expect(selected().temperature_columns).toEqual([3, 5, 6]);
    expect(screen.getByRole('alert').textContent).toContain('Incomplete sample group');
  });
});
