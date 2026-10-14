import { act, renderHook } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { useTemperatureReportInfo } from './useTemperatureReportInfo';
import type { WorkbookTable } from '../../api/temperature';
let identity = { user: null as { display_name: string } | null, loaded: false };
vi.mock('../../currentUser', () => ({ CURRENT_USER_DISPLAY_NAME: 'Lab User', useCurrentIdentity: () => identity }));
const table: WorkbookTable = { file_name: 'data.csv', sheet_names: ['Data'], sheet_name: 'Data', rows: [] };
it('snapshots the imported tester, permits late bootstrap, and retains manual blank overrides', () => {
  const { result, rerender } = renderHook(({ source }) => useTemperatureReportInfo(source, null), { initialProps: { source: table } });
  identity = { user: { display_name: 'Alice' }, loaded: true }; rerender({ source: table });
  expect(result.current.values.tested_by).toBe('Alice');
  identity = { user: { display_name: 'Bob' }, loaded: true }; rerender({ source: table });
  expect(result.current.values.tested_by).toBe('Alice');
  rerender({ source: { ...table, file_name: 'new.csv' } });
  expect(result.current.values.tested_by).toBe('Bob');
  act(() => result.current.edit('tested_by', ''));
  identity = { user: { display_name: 'Carol' }, loaded: true }; rerender({ source: { ...table } });
  expect(result.current.values.tested_by).toBe('');
});
