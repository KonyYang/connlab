import type { ReactElement } from "react";

type PrecheckLowerPanelsProps = {
  additionalInformation: string;
  confidential: string;
  requestedTesting: string;
  subcontract: string;
};

export function PrecheckLowerPanels({
  additionalInformation,
  confidential,
  requestedTesting,
  subcontract
}: PrecheckLowerPanelsProps): ReactElement {
  return (
    <div className="precheck-lower-grid">
      <ConsentPanel confidential={confidential} subcontract={subcontract} />
      <RequestedTestingPanel value={requestedTesting} />
      <AdditionalInfoPanel value={additionalInformation} />
    </div>
  );
}

function ConsentPanel({
  confidential,
  subcontract
}: {
  confidential: string;
  subcontract: string;
}): ReactElement {
  return (
    <section className="precheck-subpanel">
      <RadioLine label="Confidential test or samples?" value={confidential} />
      <RadioLine label="Can testing be subcontracted?" value={subcontract} />
    </section>
  );
}

function RadioLine({
  label,
  value
}: {
  label: string;
  value: string;
}): ReactElement {
  const normalized = value.trim().toLowerCase();
  const yes = ["yes", "y", "true", "1", "是"].includes(normalized);
  const no = value ? ["no", "n", "false", "0", "否"].includes(normalized) : false;
  return <div className="radio-line"><strong>{label}<b>*</b></strong><label><input checked={yes} readOnly name={label} type="radio" />Yes</label><label><input checked={no} readOnly name={label} type="radio" />No</label></div>;
}

function RequestedTestingPanel({ value }: { value: string }): ReactElement {
  return (
    <section className="precheck-subpanel requested-testing-panel">
      <h4>Description of Requested Testing</h4>
      <table><tbody><tr><td>Qualification test</td><td>{value || "QG-03-016_Rev1"}</td></tr><tr><td>Defect/Performance test</td><td>DG-00-048_Rev2</td></tr><tr><td>Environmental test</td><td>QG-03-016E_Rev2</td></tr></tbody></table>
      <button className="secondary-button" type="button">+ Add Row</button>
    </section>
  );
}

function AdditionalInfoPanel({ value }: { value: string }): ReactElement {
  return <section className="precheck-subpanel"><h4>Additional Information</h4><textarea value={value} readOnly placeholder="No additional information extracted from the selected application form." /></section>;
}
