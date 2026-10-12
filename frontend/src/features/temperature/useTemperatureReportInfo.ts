import { useMemo, useState } from 'react';
import type { DataSelection, WorkbookTable } from '../../api/temperature';
import { emptyReportInfo, sourceReportDefaults, type ReportInfoFields } from './reportInfo';

export function useTemperatureReportInfo(table: WorkbookTable | null, selection: DataSelection | null) {
  const [overrides, setOverrides] = useState<Partial<ReportInfoFields>>({});
  const sourceDefaults = useMemo(() => sourceReportDefaults(table, selection), [table, selection]);
  const values: ReportInfoFields = { ...emptyReportInfo, ...sourceDefaults, ...overrides };
  return { values,
    edit: (key: keyof ReportInfoFields, value: string) => setOverrides(old => ({ ...old, [key]: value })),
  };
}
