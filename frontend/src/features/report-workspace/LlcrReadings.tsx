import { useMemo, useState } from "react";
import type { LlcrSampleReading } from "../../api/client";
import "./llcrReadings.css";

type SampleRow = { sample: number; point: string; sheet: string; byStep: Map<string, LlcrSampleReading> };

function groupReadings(readings: LlcrSampleReading[]) {
  const groups = new Map<string, { stages: Map<string, LlcrSampleReading>; rows: Map<string, SampleRow> }>();
  for (const reading of readings) {
    const group = groups.get(reading.group_label) ?? { stages: new Map(), rows: new Map() };
    groups.set(reading.group_label, group);
    group.stages.set(reading.step_token, reading);
    const rowKey = JSON.stringify([reading.source_sheet, reading.sample_index, reading.position]);
    const row = group.rows.get(rowKey) ?? {
      sample: reading.sample_index, point: reading.position, sheet: reading.source_sheet, byStep: new Map(),
    };
    row.byStep.set(reading.step_token, reading);
    group.rows.set(rowKey, row);
  }
  return groups;
}

export function LlcrReadings({ readings }: { readings: LlcrSampleReading[] }) {
  const groups = useMemo(() => groupReadings(readings), [readings]);
  const [selection, setSelection] = useState("");
  const [reportValues, setReportValues] = useState(false);
  const groupLabel = groups.has(selection) ? selection : groups.keys().next().value;
  if (groupLabel === undefined) return null;
  const group = groups.get(groupLabel)!;
  const stages = Array.from(group.stages.values()).sort((a, b) => a.step_token.localeCompare(b.step_token, "en", { numeric: true }));
  const rows = Array.from(group.rows.entries()).sort(([, a], [, b]) => a.sample - b.sample);
  const showSheets = new Set(rows.map(([, row]) => row.sheet)).size > 1;
  const showPoints = showSheets || new Set(rows.map(([, row]) => row.point)).size > 1;
  return <div className="llcr-readings">
    <div className="llcr-reading-controls">
      {groups.size > 1 ? <label>Group <select aria-label="Group" value={groupLabel} onChange={event => setSelection(event.target.value)}>
        {Array.from(groups.keys(), label => <option key={label} value={label}>{label}</option>)}
      </select></label> : <strong>Group {groupLabel}</strong>}
      {!showPoints && <span>{rows[0][1].sheet} · Point {rows[0][1].point}</span>}
      <label>Values <select aria-label="Values" value={reportValues ? "report" : "workbook"} onChange={event => setReportValues(event.target.value === "report")}>
        <option value="workbook">Workbook readings</option>
        <option value="report">Report values</option>
      </select></label>
    </div>
    <div className="llcr-reading-scroll" tabIndex={0} role="region" aria-label={`Group ${groupLabel} readings`}>
      <table aria-label={`Group ${groupLabel} sample readings`}>
        <thead><tr><th scope="col">Sample</th>{showPoints && <th scope="col">Point</th>}
          {stages.map(stage => <th scope="col" key={stage.step_token}>{stage.stage_label}
            <small>Step {stage.step_token}{reportValues && (stage.stage === "initial" ? " · Corrected" : " · ΔR")}</small>
          </th>)}
        </tr></thead>
        <tbody>{rows.map(([key, row]) => <tr key={key}>
          <th scope="row">{String(row.sample).padStart(2, "0")}</th>{showPoints && <td>{row.point}{showSheets && <small>{row.sheet}</small>}</td>}
          {stages.map(stage => <ReadingCell key={stage.step_token} reading={row.byStep.get(stage.step_token)} reportValues={reportValues} />)}
        </tr>)}</tbody>
      </table>
    </div>
  </div>;
}

function ReadingCell({ reading, reportValues }: { reading?: LlcrSampleReading; reportValues: boolean }) {
  if (!reading) return <td aria-label="No reading mapped to this step">—</td>;
  if (!reportValues && reading.raw_status === "unavailable") return <td>Not recorded</td>;
  const value = reportValues ? reading.value : reading.raw_value;
  const cell = reportValues ? reading.source_cell : reading.raw_source_cell;
  const locator = cell ? `${reading.source_sheet}!${cell}` : undefined;
  if (value === null) {
    const label = reportValues ? "Unavailable" : reading.raw_status === "invalid" ? "Invalid" : "Missing";
    return <td className="llcr-reading-missing">{label} <small>{locator}</small></td>;
  }
  return <td title={locator}>{value} {reportValues ? reading.unit : reading.raw_unit}</td>;
}
