import { useMemo, useState } from 'react';
import type { DataSelection, WorkbookTable } from '../../api/temperature';
import { CURRENT_USER_DISPLAY_NAME } from '../../currentUser';
import { emptyReportInfo, sourceReportDefaults, type ReportInfoFields } from './reportInfo';

export function useTemperatureReportInfo(table: WorkbookTable | null, selection: DataSelection | null) {
  const [overrides, setOverrides] = useState<Partial<ReportInfoFields>>({});
  const sourceDefaults = useMemo(() => sourceReportDefaults(table, selection), [table, selection]);
  // These fixed report values do not replace the ambient readings used in calculations.
  const values: ReportInfoFields = { ...emptyReportInfo, ...sourceDefaults,
    tested_by: CURRENT_USER_DISPLAY_NAME, ...overrides,
    test_date: sourceDefaults.test_date ?? '', ambient_temperature: '23', relative_humidity: '50' };
  return { values,
    edit: (key: keyof ReportInfoFields, value: string) => setOverrides(old => ({ ...old, [key]: value })),
  };
}
