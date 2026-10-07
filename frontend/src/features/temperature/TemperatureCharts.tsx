import type { Coefficients, DeratingAnalysis, TemperatureAnalysis, WorkbookTable } from '../../api/temperature';
import { sourceScan } from './sourceScan';

type Point = { x: number; y: number };
type Trace = { name: string; color: string; points: Point[]; markers?: boolean; line?: boolean };
const MAX_COLOR = '#dc7021', AVG_COLOR = '#1f66d1';
const polynomial = (coef: Coefficients, x: number) => (coef.a * x + coef.b) * x + coef.c;
const equation = (coef: Coefficients) => `${coef.a.toFixed(6)} I² ${coef.b < 0 ? '−' : '+'} ${Math.abs(coef.b).toFixed(6)} I ${coef.c < 0 ? '−' : '+'} ${Math.abs(coef.c).toFixed(6)}`;

/** The SVG is a numeric XY plot of the current calculation, not decorative artwork. */
function XYChart({ title, xTitle, yTitle, traces, guide, xLimit }: {
  title: string; xTitle: string; yTitle: string; traces: Trace[]; xLimit?: number;
  guide?: { x: number; labels: { y: number; text: string; color: string }[] };
}) {
  const all = traces.flatMap(trace => trace.points);
  const maxX = xLimit ?? Math.max(1, ...all.map(point => point.x)) * 1.06;
  const minY = Math.min(0, ...all.map(point => point.y));
  const maxY = Math.max(1, ...all.map(point => point.y)) * 1.12;
  const x = (value: number) => 66 + value / maxX * 454;
  const y = (value: number) => 280 - (value - minY) / (maxY - minY) * 240;
  return <div className="temperature-chart">
    <svg viewBox="0 0 560 335" role="img" aria-label={title}>
      <title>{title}</title><desc>{traces.map(trace => trace.name).join(', ')}. See the results table for exact values.</desc>
      <text x="280" y="19" textAnchor="middle" className="chart-title">{title}</text>
      {Array.from({ length: 6 }, (_, i) => {
        const tickX = maxX * i / 5, tickY = minY + (maxY - minY) * i / 5;
        return <g key={i}>
          <line x1={x(tickX)} x2={x(tickX)} y1="40" y2="280" className="chart-grid" />
          <line x1="66" x2="520" y1={y(tickY)} y2={y(tickY)} className="chart-grid" />
          <text x={x(tickX)} y="299" textAnchor="middle">{tickX.toFixed(0)}</text>
          <text x="56" y={y(tickY) + 4} textAnchor="end">{tickY.toFixed(0)}</text>
        </g>;
      })}
      <line x1="66" y1="40" x2="66" y2="280" className="chart-axis" />
      <line x1="66" y1="280" x2="520" y2="280" className="chart-axis" />
      {traces.map(trace => <g key={trace.name}>
        {trace.line && <polyline fill="none" stroke={trace.color} strokeWidth="2" points={trace.points.map(point => `${x(point.x)},${y(point.y)}`).join(' ')} />}
        {trace.markers && trace.points.map((point, i) => <circle key={i} cx={x(point.x)} cy={y(point.y)} r="4" fill={trace.color}><title>{`${trace.name}: ${point.x.toFixed(3)}, ${point.y.toFixed(3)}`}</title></circle>)}
      </g>)}
      {guide && <g><line x1={x(guide.x)} x2={x(guide.x)} y1="40" y2="280" stroke="#647084" strokeDasharray="6 4" />
        {guide.labels.map((label, index) => <g key={`${label.color}-${index}`}><circle cx={x(guide.x)} cy={y(label.y)} r="5" fill={label.color} />
          <text x={x(guide.x) + (guide.x > maxX * .75 ? -10 : 10)} y={index === 0 ? Math.min(y(label.y), 260) - 8 : Math.min(y(label.y) + 32, 276)} textAnchor={guide.x > maxX * .75 ? 'end' : 'start'} fill={label.color}>{label.text}</text></g>)}
      </g>}
      <text x="293" y="326" textAnchor="middle">{xTitle}</text>
      <text transform="translate(17,160) rotate(-90)" textAnchor="middle">{yTitle}</text>
    </svg>
  </div>;
}

export function RiseChart({ analysis, table }: { analysis: TemperatureAnalysis; table: WorkbookTable | null }) {
  const max = Math.max(...analysis.points.map(point => point.current));
  const fitPoints = (coef: Coefficients) => Array.from({ length: 101 }, (_, i) => ({ x: max * i / 100, y: polynomial(coef, max * i / 100) }));
  const traces: Trace[] = [
    { name: 'Max ΔT', color: MAX_COLOR, markers: true, points: analysis.points.map(point => ({ x: point.current, y: point.maximum })) },
    { name: 'Avg Of Max ΔT', color: AVG_COLOR, markers: true, points: analysis.points.map(point => ({ x: point.current, y: point.average })) },
    { name: 'Max Fit', color: MAX_COLOR, line: true, points: fitPoints(analysis.maximum_fit.fitted_coefficients) },
    { name: 'Avg Fit', color: AVG_COLOR, line: true, points: fitPoints(analysis.average_fit.fitted_coefficients) },
  ];
  return <><XYChart title="Temperature Rise vs Current" xTitle="Current (A)" yTitle="Temperature Rise (°C)" traces={traces} />
    <div className="temperature-equations"><p style={{ color: MAX_COLOR }}>Max ΔT = {equation(analysis.maximum_fit.coefficients)}<br />R² = {analysis.maximum_fit.r_squared.toFixed(6)}</p>
      <p style={{ color: AVG_COLOR }}>Avg Of Max ΔT = {equation(analysis.average_fit.coefficients)}<br />R² = {analysis.average_fit.r_squared.toFixed(6)}</p></div>
    <details className="temperature-detail"><summary>Stage Results</summary><div className="temperature-table-scroll"><table><thead><tr><th>Scan</th><th>Current (A)</th><th>Max ΔT (°C)</th><th>Avg Of Max ΔT (°C)</th></tr></thead>
      <tbody>{analysis.points.map((point, i) => <tr key={i}><td>{point.source_row === null ? 'Origin' : sourceScan(table, point.source_row) ?? 'Unavailable'}</td><td>{point.current.toFixed(3)}</td><td>{point.maximum.toFixed(3)}</td><td>{point.average.toFixed(3)}</td></tr>)}</tbody></table></div></details>
  </>;
}

export function DeratingChart({ result }: { result: DeratingAnalysis }) {
  return <><XYChart title="Current vs Ambient Temperature" xTitle="Ambient Temperature (°C)" yTitle="Current (A)" xLimit={result.max_temperature}
    traces={[{ name: 'Basic (100%)', color: '#be3030', line: true, points: result.points.map(point => ({ x: point.ambient, y: point.basic })) },
      { name: '80% Derating', color: MAX_COLOR, line: true, points: result.points.map(point => ({ x: point.ambient, y: point.derated })) }]}
    guide={{ x: result.annotation.ambient, labels: [{ y: result.annotation.basic, text: `${result.annotation.basic.toFixed(2)} A`, color: '#be3030' },
      { y: result.annotation.derated, text: `${result.annotation.derated.toFixed(2)} A`, color: MAX_COLOR }] }} />
    <div className="temperature-equations"><p style={{ color: '#be3030' }}>Basic (100%)</p><p style={{ color: MAX_COLOR }}>80% Derating</p></div>
    <p className="temperature-result">At {result.annotation.ambient}°C: Basic {result.annotation.basic.toFixed(2)} A / Derated {result.annotation.derated.toFixed(2)} A</p>
  </>;
}
