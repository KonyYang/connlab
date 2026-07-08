import type { MatrixStepQuantityItem } from "../../api/client";
import type { MatrixStepQuantityEditableField } from "./matrixStepQuantitySelectors";

type MatrixStepQuantityPanelProps = {
  items: MatrixStepQuantityItem[];
  loading: boolean;
  saving: boolean;
  readOnly: boolean;
  message: string | null;
  error: string | null;
  onFieldChange: (
    item: MatrixStepQuantityItem,
    field: MatrixStepQuantityEditableField,
    value: string
  ) => void;
  onSave: () => void;
};

export function MatrixStepQuantityPanel({
  items,
  loading,
  saving,
  readOnly,
  message,
  error,
  onFieldChange,
  onSave
}: MatrixStepQuantityPanelProps) {
  const disabled = readOnly || loading || saving;
  return (
    <section className="matrix-step-quantity-panel" aria-label="Step quantity setup">
      <div className="matrix-step-quantity-header">
        <h4>Step quantity setup</h4>
        <button
          type="button"
          className="matrix-step-quantity-save"
          disabled={disabled || items.length === 0}
          onClick={onSave}
        >
          {saving ? "Saving" : "Save quantities"}
        </button>
      </div>
      {loading ? (
        <p className="matrix-step-quantity-muted">Loading Step quantities.</p>
      ) : items.length === 0 ? (
        <p className="matrix-step-quantity-muted">No Step quantities for this group.</p>
      ) : (
        <table className="matrix-step-quantity-table">
          <thead>
            <tr>
              <th>Step</th>
              <th>Test item</th>
              <th>Test points / sample</th>
              <th>Readings / point</th>
              <th>Contact points / sample</th>
              <th>Total readings</th>
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr
                key={`${item.draft_group_id}-${item.draft_row_id}-${item.step_sequence}-${item.step_suffix_note ?? ""}`}
              >
                <td>{item.raw_token ?? item.step_sequence}</td>
                <td>{item.test_item}</td>
                <td>
                  <input
                    aria-label={`Step ${item.step_sequence} test points per sample`}
                    disabled={disabled}
                    value={item.test_points_per_sample ?? ""}
                    onChange={(event) =>
                      onFieldChange(item, "test_points_per_sample", event.target.value)
                    }
                  />
                </td>
                <td>
                  <input
                    aria-label={`Step ${item.step_sequence} readings per point`}
                    disabled={disabled}
                    value={item.readings_per_point ?? ""}
                    onChange={(event) =>
                      onFieldChange(item, "readings_per_point", event.target.value)
                    }
                  />
                </td>
                <td>
                  <input
                    aria-label={`Step ${item.step_sequence} contact points per sample`}
                    disabled={disabled}
                    value={item.contact_points_per_sample ?? ""}
                    onChange={(event) =>
                      onFieldChange(item, "contact_points_per_sample", event.target.value)
                    }
                  />
                </td>
                <td>{item.total_readings ?? "-"}</td>
                <td>
                  <span className="matrix-step-quantity-source">{formatSource(item.source)}</span>
                  {item.review_required ? (
                    <span className="matrix-step-quantity-review">
                      {item.review_reason ?? "Review required"}
                    </span>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {message ? <p className="matrix-step-quantity-message">{message}</p> : null}
      {error ? <p className="matrix-step-quantity-error">{error}</p> : null}
    </section>
  );
}

function formatSource(source: string): string {
  switch (source) {
    case "basic_information_confirmed":
      return "Basic Information";
    case "basic_information_draft":
      return "Basic Information draft";
    case "matrix_step_override":
      return "Matrix Step";
    case "confirmed_matrix_carry_forward":
      return "Carried forward";
    default:
      return "Manual";
  }
}
