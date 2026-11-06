import type { FolderAnalysis, FolderReview, FolderSection, ReportTable } from '../../api/mechanicalSummary';
export const informationFields = ['LTR', 'Test Date', 'Tested By', 'Amb Temp. and Rel. Hum.', 'Test Equipment ID', 'Test Condition', 'Item/Process', 'Remark'];
export const qualitative = (section: FolderSection) => ['qualitative', 'polarisation', 'protection'].includes(section.kind);
export function tableReady(table: ReportTable): boolean {
  return Boolean(table.title.trim() && table.samples.length && table.columns.length &&
    (!table.diagonal || table.samples.length === table.columns.length) &&
    table.results.length === table.samples.length && table.results.every((row, i) => row.length === table.columns.length &&
      row.every((value, j) => table.diagonal && i !== j ? value === '' : ['Pass', 'Fail', 'N/A'].includes(value))));
}
export function sectionReady(section: FolderSection): boolean {
  if (qualitative(section)) return Boolean(section.kind !== 'qualitative' && section.qualitative_confirmed && section.tables.length && section.tables.every(tableReady));
  return Boolean(section.rows.length && section.rows.every(row => row.sample.trim()) &&
    (!section.force_fields.length || section.force_fields.includes(section.force_field)));
}
export function reviewFor(analysis: FolderAnalysis): FolderReview {
  return { project: analysis.project, sections: Object.fromEntries(analysis.sections.map(section => [section.id, {
    information: section.information,
    ...(qualitative(section) ? { kind: section.kind, tables: section.tables, qualitative_confirmed: section.qualitative_confirmed === true } : {
      rows: section.rows.map(({ curve, sample, colour, part }) => ({ curve, sample, colour, part })),
      ...(section.force_field ? { force_field: section.force_field } : {}), withdraw_magnitude: section.withdraw_magnitude,
    }),
  }])) };
}
const storageKey = (project: string) => `connlab.mechanical-folder.v1.${project}`;
export function savedReview(analysis: FolderAnalysis): FolderReview | undefined {
  if (!analysis.project) return undefined;
  try {
    const stored: FolderReview = JSON.parse(localStorage.getItem(storageKey(analysis.project)) || 'null');
    if (!stored || stored.project !== analysis.project || typeof stored.sections !== 'object') return undefined;
    const sections = Object.fromEntries(analysis.sections.filter(s => stored.sections[s.id]).map(s => [s.id, stored.sections[s.id]]));
    return Object.keys(sections).length ? { project: analysis.project, sections } : undefined;
  } catch { return undefined; }
}
export function saveReview(analysis: FolderAnalysis): boolean {
  if (!analysis.project) return false;
  try { localStorage.setItem(storageKey(analysis.project), JSON.stringify(reviewFor(analysis))); return true; }
  catch { return false; }
}
export function resizeTable(table: ReportTable, samples: string[], columns: string[], diagonal = table.diagonal): ReportTable {
  return { ...table, samples, columns, diagonal, curves: [], results: samples.map((sample, i) => columns.map((column, j) => {
    if (diagonal && i !== j) return '';
    return table.results[table.samples.indexOf(sample)]?.[table.columns.indexOf(column)] || '';
  })) };
}
