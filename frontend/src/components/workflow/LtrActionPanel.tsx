import type { FormEvent, ReactElement } from "react";
import type { LtrRecord } from "../../api/client";

type LtrActionPanelProps = {
  ltrNumber: string;
  ltrs: LtrRecord[];
  onSubmitLtr: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  setLtrNumber: (value: string) => void;
};

export function LtrActionPanel({
  ltrNumber,
  ltrs,
  onSubmitLtr,
  setLtrNumber
}: LtrActionPanelProps): ReactElement {
  const latest = ltrs[0] ?? null;

  return (
    <div className="action-panel-body">
      <div className="operator-panel">
        <div>
          <p className="eyebrow">LTR registration</p>
          <h4>{latest ? "LTR registered" : "Register LTR number"}</h4>
          <p>
            {latest
              ? "Confirm the latest LTR number before preparing the project folder."
              : "Enter the lab tracking reference assigned for this request."}
          </p>
        </div>
        <form className="card-form ltr-registration-panel" onSubmit={onSubmitLtr}>
          <input
            required
            placeholder="LTR number"
            value={ltrNumber}
            onChange={(event) => setLtrNumber(event.target.value)}
          />
          <button className="primary-action" type="submit">Register LTR</button>
        </form>
      </div>

      <div className="latest-ltr-card">
        <span>{latest ? "Latest LTR registered" : "Not registered"}</span>
        <strong>{latest?.ltr_number ?? "No LTR number yet"}</strong>
        <p>Status: {latest?.status ?? "waiting for registration"}</p>
      </div>
    </div>
  );
}
