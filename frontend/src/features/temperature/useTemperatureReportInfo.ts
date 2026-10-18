import { useLayoutEffect, useMemo, useState } from 'react';
import type { DataSelection, WorkbookTable } from '../../api/temperature';
import { CURRENT_USER_DISPLAY_NAME, useCurrentProfile } from '../../currentUser';
import { emptyReportInfo, sourceReportDefaults, type ReportInfoFields } from './reportInfo';
import { useTemperatureWorkspace } from './temperatureWorkspace';

export function useTemperatureReportInfo(table: WorkbookTable | null, selection: DataSelection | null) {
  const workspace = useTemperatureWorkspace();
  const [overrides, setOverrides] = useState<Partial<ReportInfoFields>>(() => workspace?.initial?.report ?? {});
  useLayoutEffect(() => { workspace?.update({ report: overrides }); }, [overrides, workspace?.update]);
  const identity = useCurrentProfile();
  const sourceDefaults = useMemo(() => sourceReportDefaults(table, selection), [table, selection]);
  // These fixed report values do not replace the ambient readings used in calculations.
  const values: ReportInfoFields = { ...emptyReportInfo, ...sourceDefaults, ...overrides,
    tested_by: identity.profile?.display_name ?? CURRENT_USER_DISPLAY_NAME,
    test_date: sourceDefaults.test_date ?? '', ambient_temperature: '23', relative_humidity: '50' };
  return { values,
    edit: (key: keyof ReportInfoFields, value: string) => setOverrides(old => ({ ...old, [key]: value })),
  };
}
