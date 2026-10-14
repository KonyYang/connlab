import { useEffect, useMemo, useRef, useState } from 'react';
import type { DataSelection, WorkbookTable } from '../../api/temperature';
import { CURRENT_USER_DISPLAY_NAME, useCurrentProfile } from '../../currentUser';
import { emptyReportInfo, sourceReportDefaults, type ReportInfoFields } from './reportInfo';

export function useTemperatureReportInfo(table: WorkbookTable | null, selection: DataSelection | null) {
  const [overrides, setOverrides] = useState<Partial<ReportInfoFields>>({});
  const identity = useCurrentProfile();
  const [defaultTester, setDefaultTester] = useState(CURRENT_USER_DISPLAY_NAME);
  const importedTable = useRef<WorkbookTable | null>(null);
  const assigned = useRef(false);
  useEffect(() => {
    if (table !== importedTable.current) {
      importedTable.current = table;
      assigned.current = identity.loaded;
      setDefaultTester(identity.profile?.display_name ?? CURRENT_USER_DISPLAY_NAME);
    } else if (table && !assigned.current && identity.loaded) {
      assigned.current = true;
      setDefaultTester(identity.profile?.display_name ?? CURRENT_USER_DISPLAY_NAME);
    }
  }, [table, identity.profile, identity.loaded]);
  const sourceDefaults = useMemo(() => sourceReportDefaults(table, selection), [table, selection]);
  // These fixed report values do not replace the ambient readings used in calculations.
  const values: ReportInfoFields = { ...emptyReportInfo, ...sourceDefaults,
    tested_by: defaultTester, ...overrides,
    test_date: sourceDefaults.test_date ?? '', ambient_temperature: '23', relative_humidity: '50' };
  return { values,
    edit: (key: keyof ReportInfoFields, value: string) => setOverrides(old => ({ ...old, [key]: value })),
  };
}
