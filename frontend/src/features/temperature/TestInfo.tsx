import { useState } from 'react';
import { reportHumidityIssue, type ReportInfoFields } from './reportInfo';
import type { useTemperatureReportInfo } from './useTemperatureReportInfo';

type Props = { info: ReturnType<typeof useTemperatureReportInfo>; disabled: boolean;
  onEdit: (key: keyof ReportInfoFields, value: string) => void; onProject: (id: string) => void };

export function TestInfo({ info, disabled, onEdit, onProject }: Props) {
  const [open, setOpen] = useState(true);
  const field = (key: keyof ReportInfoFields, label: string, maxLength: number, placeholder?: string) =>
    <label>{label}<input value={info.values[key]} disabled={disabled} maxLength={maxLength}
      placeholder={placeholder} onChange={event => onEdit(key, event.target.value)} /></label>;
  const humidityIssue = reportHumidityIssue(info.values.relative_humidity);
  const summary = [info.values.ltr_number, info.values.test_date, info.values.tested_by].filter(Boolean).join(' · ');
  return <details className="temperature-test-info" open={open} onToggle={event => setOpen(event.currentTarget.open)}>
    <summary>Test Info{!open && summary && <span>{summary}</span>}{!open && humidityIssue && <span className="temperature-error">Check relative humidity</span>}</summary>
    <div className="temperature-test-info-fields">
      <label>Project (optional)<select value={info.projectId} disabled={disabled || info.listLoading}
        onChange={event => onProject(event.target.value)}>
        <option value="">No project — enter manually</option>
        {info.projects.map(project => <option key={project.project_id} value={project.project_id}>
          {project.display_project_id}{project.sample_description ? ` — ${project.sample_description}` : ''}
        </option>)}
      </select></label>
      {field('ltr_number', 'LTR', 200)}
      {field('tested_by', 'Tested By', 200)}
      {field('test_date', 'Test Date', 80, 'YYYY-MM-DD or date range')}
      {field('ambient_temperature', 'Amb Temp. (°C)', 80)}
      <label>Rel. Hum. (%RH)<input type="number" min="0" max="100" step="any"
        value={info.values.relative_humidity} disabled={disabled} aria-invalid={Boolean(humidityIssue)}
        onChange={event => onEdit('relative_humidity', event.target.value)} /></label>
    </div>
    {info.listLoading && <p className="temperature-hint" role="status">Loading projects…</p>}
    {info.listError && <p className="temperature-error" role="alert">{info.listError} <button type="button" disabled={disabled} onClick={info.retryProjects}>Retry Projects</button></p>}
    {info.projectLoading && <p className="temperature-hint" role="status">Loading project information…</p>}
    {info.projectNotice && <p className="temperature-hint">{info.projectNotice} <button type="button" disabled={disabled} onClick={info.retryProject}>Retry Project Info</button></p>}
    {humidityIssue && <p className="temperature-error" role="alert">{humidityIssue}</p>}
    <p className="temperature-hint">Date and temperature are suggested from included readings. Edit these report values without changing the calculations.</p>
    <details className="temperature-test-info-more"><summary>More Information</summary>
      <div className="temperature-test-info-fields">
        {field('equipment_id', 'Test Equipment ID', 500)}
        {field('test_condition', 'Test Condition', 500)}
        {field('remark', 'Remark', 500)}
      </div>
    </details>
  </details>;
}
