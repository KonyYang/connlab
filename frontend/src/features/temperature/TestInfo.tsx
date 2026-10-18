import type { ReportInfoFields } from './reportInfo';
import type { useTemperatureReportInfo } from './useTemperatureReportInfo';

type Props = { info: ReturnType<typeof useTemperatureReportInfo>; disabled: boolean;
  onEdit: (key: keyof ReportInfoFields, value: string) => void };

export function TestInfo({ info, disabled, onEdit }: Props) {
  const field = (key: keyof ReportInfoFields, label: string, maxLength: number, placeholder?: string) =>
    <label>{label}<input value={info.values[key]} disabled={disabled} maxLength={maxLength}
      placeholder={placeholder} onChange={event => onEdit(key, event.target.value)} /></label>;
  return <div className="temperature-test-info" role="group" aria-label="Report information">
    <div className="temperature-test-info-fields">
      {field('ltr_number', 'LTR', 200)}
      {field('equipment_id', 'Test Equipment ID', 500)}
      {field('test_condition', 'Test Condition', 500)}
    </div>
  </div>;
}
