import { useRef, type ReactElement } from 'react';
import { createPortal } from 'react-dom';
import type { Coefficients } from '../api/temperature';
import { UiIcon } from '../components/common/UiIcon';
import { useTopBarActionsRoot } from '../components/layout/TopBarActionsContext';
import { ChannelMapping, sourceColumns } from '../features/temperature/ChannelMapping';
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
  const columns = s.table && s.selection ? sourceColumns(s.table, s.selection.header_row) : [];
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
            <label>Ambient Column<select value={s.selection.ambient_column} disabled={busy} onChange={event => tool.changeData({ ambient_column: Number(event.target.value) })}>{columns.map(col => <option key={col.id} value={col.id}>{col.label}</option>)}</select></label>
            <label>Current Column<select value={s.selection.current_column} disabled={busy} onChange={event => tool.changeData({ current_column: Number(event.target.value) })}>{columns.map(col => <option key={col.id} value={col.id}>{col.label}</option>)}</select></label>
            <label className="temperature-sample-count">Thermocouples/Sample<input type="number" min="1" max="254" value={s.selection.thermocouples_per_sample} disabled={busy} onChange={event => tool.changeData({ thermocouples_per_sample: Number(event.target.value) })} /></label>
          </>}
      </div>}
      {s.table && s.region_issue && <DataRegionCorrection table={s.table} message={s.region_issue}
        disabled={busy} onApply={tool.correctRegion} />}
      {s.table && s.selection && <>
        <ChannelMapping key={`mapping-${s.table.sheet_name}-${s.table.file_name}`} table={s.table} selection={s.selection} onChange={tool.changeData} disabled={busy} />
        <DataPreview key={`preview-${s.table.sheet_name}-${s.table.file_name}`} table={s.table} selection={s.selection} issues={s.review?.issues ?? []} onChange={tool.changeData} disabled={busy} />
        {Boolean(s.review?.issues.length) && <section className="temperature-review" aria-label="Data Needs Review">
          <h4>Data Needs Review</h4><div className="temperature-issue-list">{s.review?.issues.map((issue, index) => <p key={index} className={issue.severity === 'error' ? 'temperature-error' : undefined}>{issue.message}</p>)}</div>
          {!s.review?.issues.some(issue => issue.severity === 'error') && <label className="temperature-check"><input type="checkbox" checked={s.acknowledged} disabled={busy} onChange={event => tool.acknowledge(event.target.checked)} />Keep Flagged Rows</label>}
        </section>}
        <div className="temperature-confirm"><span className={s.confirmed ? 'temperature-success' : 'temperature-hint'} role="status">{s.confirmed ? 'Data Confirmed' : 'Review the channel mapping and data rows, then confirm.'}</span>
          <button type="button" className="primary-action" disabled={busy || s.confirmed} onClick={() => void tool.confirm()}>Confirm Data</button></div>
      </>}
    </section>}
    <div className="temperature-analysis-grid">
      <section className="temperature-panel">
        <h3>Temperature Rise (T-riseChart)</h3>
        <div className="temperature-actions"><label className="temperature-check"><input type="checkbox" checked={s.zeroIntercept} disabled={busy} onChange={event => tool.zeroIntercept(event.target.checked)} />Zero Intercept</label>
          <button type="button" disabled={busy || !s.confirmed} onClick={() => void tool.analyze()}>Generate T-riseChart</button></div>
        {!s.confirmed && <p className="temperature-hint">Confirm Initial Data to generate the chart.</p>}
        <div className="temperature-coefficients">
          <div className="temperature-section-heading"><span>Polynomial Coefficients (ΔT = aI² + bI + c)</span><button type="button" disabled={busy || !s.analysis} onClick={tool.getCoefficients}>Get Coefficients</button></div>
          <table><thead><tr><th>Curve</th><th>a</th><th>b</th><th>c</th></tr></thead><tbody>
            {(['maximum', 'average'] as const).map(curve => <tr key={curve}><th>{curve === 'maximum' ? 'MAX' : 'AVG'}</th>
              {(['a', 'b', 'c'] as (keyof Coefficients)[]).map(key => <td key={key}><input type="number" step="any" aria-label={`${curve === 'maximum' ? 'MAX' : 'AVG'} Coefficient ${key}`}
                value={s[curve]?.[key] ?? ''} placeholder="—" disabled={busy || !s[curve] || (key === 'c' && s.zeroIntercept)} onChange={event => tool.editCoefficient(curve, key, event.target.value)} /></td>)}
            </tr>)}
          </tbody></table>
        </div>
        {s.analysis ? <RiseChart analysis={s.analysis} /> : <p className="temperature-chart-empty">The temperature-rise chart will appear here.</p>}
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
        </div>
        <div className="temperature-actions"><button type="button" disabled={busy || !s.average || !s.zeroIntercept} onClick={() => void tool.derating()}>Generate Derating</button></div>
        {!s.zeroIntercept ? <p className="temperature-hint">Enable Zero Intercept, regenerate T-riseChart and get its coefficients to use Derating.</p>
          : !s.average && <p className="temperature-hint">Get AVG coefficients from T-riseChart first.</p>}
        {s.derating ? <DeratingChart result={s.derating} /> : <p className="temperature-chart-empty">The Basic and 80% Derating curves will appear here.</p>}
      </section>
    </div>
    <footer className="temperature-footer"><div aria-live="polite">
      {s.busy && <p role="status">{s.busy}</p>}
      {s.error && <p role="alert" className="temperature-error">{s.error}</p>}
      {s.downloaded && <p role="status" className="temperature-success">{s.downloaded}</p>}
    </div><button type="button" className="primary-action" disabled={busy || !s.analysis} onClick={() => void tool.download()}>Download Excel</button></footer>
  </section>;
}
