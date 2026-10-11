import { useEffect, useMemo, useState } from 'react';
import { getProjectBasicInformation, listProjectRegistryRows, type ProjectRegistryRow } from '../../api/client';
import type { DataSelection, WorkbookTable } from '../../api/temperature';
import { emptyReportInfo, sourceReportDefaults, type ReportInfoFields } from './reportInfo';

export function useTemperatureReportInfo(table: WorkbookTable | null, selection: DataSelection | null) {
  const [projects, setProjects] = useState<ProjectRegistryRow[]>([]);
  const [projectId, setProjectId] = useState('');
  const [overrides, setOverrides] = useState<Partial<ReportInfoFields>>({});
  const [projectDefaults, setProjectDefaults] = useState<{ projectId: string; values: Partial<ReportInfoFields> } | null>(null);
  const [listRevision, setListRevision] = useState(0);
  const [lookupRevision, setLookupRevision] = useState(0);
  const [listLoading, setListLoading] = useState(false);
  const [projectLoading, setProjectLoading] = useState(false);
  const [listError, setListError] = useState<string | null>(null);
  const [projectNotice, setProjectNotice] = useState<string | null>(null);
  const enabled = Boolean(table);

  useEffect(() => {
    if (!enabled) return;
    let active = true;
    setListLoading(true);
    setListError(null);
    void listProjectRegistryRows().then(rows => {
      if (active) setProjects(rows.filter(row => !row.registry_state || row.registry_state === 'active'));
    }).catch(() => {
      if (active) setListError('Projects could not be loaded. Retry or enter test information manually.');
    }).finally(() => { if (active) setListLoading(false); });
    return () => { active = false; };
  }, [enabled, listRevision]);

  useEffect(() => {
    setProjectNotice(null);
    setProjectLoading(Boolean(projectId));
    if (!projectId) return;
    let active = true;
    void getProjectBasicInformation(projectId).then(response => {
      if (!active) return;
      const values = response.latest_confirmed?.values;
      setProjectDefaults({ projectId, values: values ? { ltr_number: values.dl_number ?? '', tested_by: values.project_leader ?? '' } : {} });
      if (!values) setProjectNotice('Basic Information is not confirmed. Enter the tester manually.');
    }).catch(() => {
      if (active) {
        setProjectDefaults(null);
        setProjectNotice('Project information could not be loaded. Retry or enter it manually.');
      }
    }).finally(() => { if (active) setProjectLoading(false); });
    return () => { active = false; };
  }, [projectId, lookupRevision]);

  const sourceDefaults = useMemo(() => sourceReportDefaults(table, selection), [table, selection]);
  const project = projects.find(row => row.project_id === projectId);
  const defaults = projectDefaults?.projectId === projectId ? projectDefaults.values : {};
  const values: ReportInfoFields = { ...emptyReportInfo, ...sourceDefaults,
    ltr_number: defaults.ltr_number || project?.registered_ltr_number || project?.ltr_number || '',
    tested_by: defaults.tested_by || '', ...overrides };
  return { values, projects, projectId, listLoading, projectLoading, listError, projectNotice,
    selectProject: setProjectId,
    edit: (key: keyof ReportInfoFields, value: string) => setOverrides(old => ({ ...old, [key]: value })),
    retryProjects: () => setListRevision(old => old + 1),
    retryProject: () => setLookupRevision(old => old + 1),
  };
}
