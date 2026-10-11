import type { ChannelLayout, DataSelection } from '../../api/temperature';

export function partitionSamples(columns: number[], count: number): number[][] {
  if (!Number.isInteger(count) || count < 1) return [columns];
  return Array.from({ length: Math.ceil(columns.length / count) }, (_, index) => columns.slice(index * count, (index + 1) * count));
}

export function sampleGroups(selection: DataSelection, layout?: ChannelLayout | null): number[][] {
  if (selection.sample_groups) return selection.sample_groups;
  if (layout && selection.thermocouples_per_sample === layout.thermocouples_per_sample
    && selection.temperature_columns.join(',') === layout.temperature_columns.join(',')
    && layout.sample_groups.flatMap(group => group.columns).join(',') === selection.temperature_columns.join(',')) {
    return layout.sample_groups.map(group => group.columns);
  }
  return partitionSamples(selection.temperature_columns, selection.thermocouples_per_sample);
}

export function includedSamples(slots: number[][], active: number[]) {
  const included = new Set(active);
  return slots.map(group => group.filter(column => included.has(column)));
}

export function equalSampleSize(groups: number[][]): number | null {
  const count = groups[0]?.length;
  return count && groups.every(group => group.length === count) ? count : null;
}

export function retainInactiveSlots(groups: number[][], previous: number[][], inactive: number[]): number[][] {
  // With all channels temporarily suspended there is no new group to own their slots.
  // Retain the last layout so returning a role cannot permanently lose the last channel.
  if (!groups.length) return previous.map(group => [...group]);
  const next = groups.map(group => [...group]);
  previous.forEach((group, index) => {
    const owner = next.findIndex(candidate => candidate.some(column => group.includes(column)));
    const target = next[owner < 0 ? Math.min(index, next.length - 1) : owner];
    if (!target) return;
    group.forEach((column, position) => {
      if (!inactive.includes(column)) return;
      const following = group.slice(position + 1).find(item => target.includes(item));
      target.splice(following === undefined ? target.length : target.indexOf(following), 0, column);
    });
  });
  return next;
}
