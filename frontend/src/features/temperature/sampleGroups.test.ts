import { describe, expect, it } from 'vitest';
import { partitionBySampleCount, sampleGroups } from './sampleGroups';
import { incompleteSampleGroups } from './sourceColumns';
import type { DataSelection } from '../../api/temperature';

const selection: DataSelection = { header_row: 1, start_row: 2, end_row: 3, ambient_column: 7, current_column: 8,
  temperature_columns: [3, 4, 5, 6], thermocouples_per_sample: 1, sample_count: 3, excluded_rows: [], current_multiplier: 1 };
describe('requested sample count', () => {
  it('keeps every source channel when the count cannot divide evenly and blocks confirmation', () => {
    expect(partitionBySampleCount([3, 4, 5, 6], 3)).toEqual([[3, 4], [5], [6]]);
    expect(incompleteSampleGroups(selection)).toBe(true);
    expect(sampleGroups(selection).flat()).toEqual([3, 4, 5, 6]);
    expect(incompleteSampleGroups({ ...selection, sample_count: 1, thermocouples_per_sample: 4 })).toBe(false);
  });
  it('uses explicit sample ownership and supports more than three samples', () => {
    const groups = [[3], [4], [5], [6]];
    expect(sampleGroups({ ...selection, sample_count: 4, sample_groups: groups })).toEqual(groups);
    expect(incompleteSampleGroups({ ...selection, sample_count: 4, sample_groups: groups })).toBe(false);
  });
});
