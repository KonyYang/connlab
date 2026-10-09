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

export function retainExcludedSlots(groups: number[][], previous: number[][], excluded: number[]): number[][] {
  const next = groups.map(group => [...group]);
  previous.forEach((group, index) => {
    const owner = next.findIndex(candidate => candidate.some(column => group.includes(column)));
    const target = next[owner < 0 ? Math.min(index, next.length - 1) : owner];
    if (!target) return;
    group.forEach((column, position) => {
      if (!excluded.includes(column)) return;
      const following = group.slice(position + 1).find(item => target.includes(item));
      target.splice(following === undefined ? target.length : target.indexOf(following), 0, column);
    });
  });
  return next;
}

// Explicit moves may regroup complete blocks. While repairing an incomplete block,
// the destination's retained slot identifies its sample (even for an excluded column).
export function moveSampleSlots(slots: number[][], moving: number[], destination: number | null,
  active: number[], orderedActive: number[], count: number): number[][] {
  if (equalSampleSize(includedSamples(slots, active)) === count && moving.every(column => active.includes(column))) {
    const regrouped = partitionSamples(orderedActive, count);
    return retainExcludedSlots(regrouped, slots, slots.flat().filter(column => !active.includes(column)));
  }
  const owner = destination === null ? slots.length - 1 : slots.findIndex(group => group.includes(destination));
  const target = owner < 0 ? slots.length - 1 : owner;
  const next = slots.map(group => group.filter(column => !moving.includes(column)));
  if (target < 0) return [moving];
  const position = destination === null ? -1 : next[target].indexOf(destination);
  next[target].splice(position < 0 ? next[target].length : position, 0, ...moving);
  return next;
}
