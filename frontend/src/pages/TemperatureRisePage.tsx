import { useMemo, useRef, type ReactElement } from 'react';
import { createPortal } from 'react-dom';
import { UiIcon } from '../components/common/UiIcon';
import { useTopBarActionsRoot } from '../components/layout/TopBarActionsContext';
import { incompleteSampleGroups } from '../features/temperature/sourceColumns';
import { sourceColumnOptions } from '../features/temperature/sourcePresentation';
import { scanMessage } from '../features/temperature/sourceScan';
import { DataPreview } from '../features/temperature/DataPreview';
import { DataRegionCorrection } from '../features/temperature/DataRegionCorrection';
import { RiseChart, DeratingChart } from '../features/temperature/TemperatureCharts';
import { useTemperatureTool } from '../features/temperature/useTemperatureTool';
import '../features/temperature/temperature.css';

export function TemperatureRisePage({ onBack }: { onBack: () => void }): ReactElement {
  const topBarRoot = useTopBarActionsRoot();
  const fileInput = useRef<HTMLInputElement>(null);
  const tool = useTemperatureTool();
  const s = tool.state;
  const busy = Boolean(s.busy);
  const columns = useMemo(() => s.table && s.selection ? sourceColumnOptions(s.table, s.selection, s.channel_layout) : [],
    [s.table, s.selection?.header_row, s.selection?.ambient_column, s.selection?.current_column, s.selection?.temperature_columns, s.channel_layout]);
  const ambientValid = columns.some(column => column.id === s.selection?.ambient_column && column.kind === 'temperature');
  const currentValid = columns.some(column => column.id === s.selection?.current_column && column.kind === 'current');
  const roleIssue = s.selection && (!ambientValid || !currentValid)
    ? `Choose ${[!ambientValid && 'Ambient Column (temperature)', !currentValid && 'Current Column (current)'].filter(Boolean).join(' and ')} to match the source units.`
    : null;
  const backButton = <button type="button" className="temperature-tools-return" onClick={onBack}
    aria-label="Back To Tools" title="Back To Tools"><UiIcon name="tools" /></button>;
  const headerActions = <div className="temperature-header-actions">
    {backButton}
    <button type="button" className="temperature-load-initial-data" onClick={() => fileInput.current?.click()}>Load Initial Data</button>
  </div>;
  return <section className="temperature-page" aria-label="Temperature Rise & Derating">
    {topBarRoot && createPortal(headerActions, topBarRoot)}
    {!topBarRoot && headerActions}
    <input ref={fileInput} type="file" hidden aria-label="Load Initial Data" accept=".xls,.xlsx,.xlsm,.csv"
      onChange={event => {
        const file = event.target.files?.[0];
        if (file) tool.load(file);
        event.target.value = '';
      }} />
    {s.file && <section className="temperature-panel temperature-initial">
      <div className="temperature-file">
        <span className="temperature-file-name">{s.file.name}</span>
      </div>
      {s.table && <div className="temperature-import-fields">
          <label>Sheet Name<select value={s.table.sheet_name} disabled={busy} onChange={event => tool.load(s.file, event.target.value)}>{s.table.sheet_names.map(name => <option key={name}>{name}</option>)}</select></label>
          {s.selection && <>
            <label>Ambient Column<select value={ambientValid ? s.selection.ambient_column : ''} disabled={busy} onChange={event => tool.changeData({ ambient_column: Number(event.target.value) })}>{!ambientValid && <option value="" disabled>Choose Ambient Column</option>}{columns.filter(col => col.kind === 'temperature').map(col => <option key={col.id} value={col.id} title={col.original}>{col.label}</option>)}</select></label>
            <label>Current Column<select value={currentValid ? s.selection.current_column : ''} disabled={busy} onChange={event => tool.changeData({ current_column: Number(event.target.value) })}>{!currentValid && <option value="" disabled>Choose Current Column</option>}{columns.filter(col => col.kind === 'current').map(col => <option key={col.id} value={col.id} title={col.original}>{col.label}</option>)}</select></label>
            <label className="temperature-sample-count">Thermocouples/Sample<input type="number" min="1" max="254" value={s.selection.thermocouples_per_sample} disabled={busy} onChange={event => tool.changeData({ thermocouples_per_sample: Number(event.target.value) })} /></label>
          </>}
      </div>}
      {roleIssue && <p role="alert" className="temperature-error">{roleIssue}</p>}
      {s.table && s.region_issue && <DataRegionCorrection table={s.table} message={s.region_issue}
        disabled={busy} onApply={tool.correctRegion} />}
      {s.table && s.selection && <>
        {s.channel_layout?.current_issue && !s.confirmed && <p className="temperature-hint">{s.channel_layout.current_issue}</p>}
        <DataPreview key={`preview-${s.table.sheet_name}-${s.table.file_name}-${s.selection.header_row}-${s.selection.start_row}-${s.selection.end_row}`}
          table={s.table} selection={s.selection} layout={s.channel_layout} issues={s.review?.issues ?? []} onChange={tool.changeData} disabled={busy} />
        {Boolean(s.review?.issues.length) && <section className="temperature-review" aria-label="Data Needs Review">
          <h4>Data Needs Review</h4><div className="temperature-issue-list">{s.review?.issues.map((issue, index) => <p key={index} className={issue.severity === 'error' ? 'temperature-error' : undefined}>{scanMessage(s.table, issue.message, issue.source_row)}</p>)}</div>
          {!s.review?.issues.some(issue => issue.severity === 'error') && <label className="temperature-check"><input type="checkbox" checked={s.acknowledged} disabled={busy} onChange={event => tool.acknowledge(event.target.checked)} />Keep Flagged Rows</label>}
        </section>}
        <div className="temperature-confirm"><span className={s.confirmed ? 'temperature-success' : 'temperature-hint'} role="status">{s.confirmed ? 'Data Confirmed' : ''}</span>
          <button type="button" className="primary-action" disabled={busy || s.confirmed || Boolean(roleIssue) || incompleteSampleGroups(s.selection, s.channel_layout)} onClick={() => void tool.confirm()}>Confirm Data</button></div>
      </>}
    </section>}
    <div className="temperature-analysis-grid">
      <section className="temperature-panel">
        <h3>Temperature Rise (T-riseChart)</h3>
        <div className="temperature-actions"><label className="temperature-check"><input type="checkbox" checked={s.zeroIntercept} disabled={busy} onChange={event => tool.zeroIntercept(event.target.checked)} />Zero Intercept</label>
          <button type="button" disabled={busy || !s.confirmed} onClick={() => void tool.analyze()}>Generate T-riseChart</button></div>
        {Boolean(s.channel_layout?.stable_current_columns.some(column => column !== s.selection?.current_column && column !== s.selection?.ambient_column)) && !s.manualZeroIntercept &&
          <p className="temperature-hint">Extra stable current detected; Zero Intercept defaults off.</p>}
        {!s.confirmed && <p className="temperature-hint">Confirm Initial Data to generate the chart.</p>}
        {s.analysis ? <RiseChart analysis={s.analysis} table={s.table} /> : <p className="temperature-chart-empty">The temperature-rise chart will appear here.</p>}
        <div className="temperature-actions"><label>Target Rise (°C)<input type="number" min="0" step="any" value={s.targetRise} disabled={busy} onChange={event => tool.editParameter('targetRise', event.target.value)} /></label>
          <button type="button" disabled={busy || !s.maximum} onClick={() => void tool.current()}>Calculate Current</button>
          {s.current !== null && <output aria-label="Calculated Current" className="temperature-result">{s.current.toFixed(2)} A</output>}</div>
      </section>
      <section className="temperature-panel">
        <h3>Derating</h3>
        <div className="temperature-derating-fields">
          <label>Max Working Temp (°C)<input type="number" min="0" step="any" value={s.maxTemperature} disabled={busy} onChange={event => tool.editParameter('maxTemperature', event.target.value)} /></label>
          <label>Step (°C)<input type="number" min="0" step="any" value={s.step} disabled={busy} onChange={event => tool.editParameter('step', event.target.value)} /></label>
          <label>Ambient Point (°C)<input type="number" min="0" step="any" value={s.ambientPoint} disabled={busy} onChange={event => tool.editParameter('ambientPoint', event.target.value)} /></label>
          <button type="button" disabled={busy || !s.average || !s.zeroIntercept} onClick={() => void tool.derating()}>Generate Derating</button>
        </div>
        {!s.zeroIntercept ? <p className="temperature-hint">Enable Zero Intercept and regenerate T-riseChart to use Derating.</p>
          : !s.average && <p className="temperature-hint">Generate T-riseChart first.</p>}
        {s.derating ? <DeratingChart result={s.derating} /> : <p className="temperature-chart-empty">The Basic and 80% Derating curves will appear here.</p>}
      </section>
    </div>
    <footer className="temperature-footer"><div aria-live="polite">
      {s.busy && <p role="status">{s.busy}</p>}
      {s.error && <p role="alert" className="temperature-error">{scanMessage(s.table, s.error)}</p>}
      {s.downloaded && <p role="status" className="temperature-success">{s.downloaded}</p>}
    </div><button type="button" className="primary-action" disabled={busy || !s.analysis} onClick={() => void tool.download()}>Download Excel</button></footer>
  </section>;
}
