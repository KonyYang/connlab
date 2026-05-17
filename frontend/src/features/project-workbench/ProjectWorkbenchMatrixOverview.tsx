import type { ReactElement } from "react";
import type {
  ProjectTestPlanDraft,
  RuntimeProjectionMatrixToken,
  RuntimeProjectionSnapshotResponse
} from "../../api/client";

type ProjectWorkbenchMatrixOverviewProps = {
  draft: ProjectTestPlanDraft;
  snapshot?: RuntimeProjectionSnapshotResponse;
  selectedTokenReference?: string | null;
  onTokenSelect?: (value: string) => void;
};

type MockMatrixRow = {
  id: number;
  testItem: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
  groups: string[];
};

const MOCK_GROUPS = Array.from({ length: 12 }, (_, index) => `G${index + 1}`);

const MOCK_MATRIX_ROWS: MockMatrixRow[] = [
  {
    id: 1,
    testItem: "Examination of Product",
    section: "5.4",
    method: "EIA-364-18B",
    condition: "10x min magnification",
    requirement: "No detrimental condition",
    groups: ["1,8", "1,14", "1,10", "1,10", "1,9", "1,4", "1,5", "1,3", "1", "1,8", "1", "1,3"]
  },
  {
    id: 2,
    testItem: "LLCR",
    section: "6.1",
    method: "EIA-364-23E",
    condition: "20mV max, 100mA max",
    requirement: "Initial <= 0.40mO; After test <= 0.40mO",
    groups: ["2 5 7", "2 5 9 11", "2 5 7 9", "2 5 7 9", "3 7", "-", "-", "-", "2 4", "-", "-", "2 5 7"]
  },
  {
    id: 3,
    testItem: "Contact Resistance",
    section: "6.2",
    method: "EIA-364-06C",
    condition: "340A",
    requirement: "<= 0.20mO",
    groups: ["-", "-", "-", "-", "3", "-", "-", "-", "-", "-", "3", "-"]
  },
  {
    id: 4,
    testItem: "Dielectric Withstanding Voltage",
    section: "6.3",
    method: "EIA-364-20F",
    condition: "3500V/AC, 1min, mated",
    requirement: "No arcing, insulation breakdown, or leakage current > 5mA",
    groups: ["-", "-", "-", "-", "6 12", "-", "-", "-", "6 12", "-", "-", "-"]
  },
  {
    id: 5,
    testItem: "Insulation Resistance",
    section: "6.4",
    method: "EIA-364-21F",
    condition: "500V/DC, 2min, mated",
    requirement: ">= 1000MO (1GO)",
    groups: ["-", "-", "7 13", "-", "-", "-", "-", "-", "2 7", "-", "-", "-"]
  },
  {
    id: 6,
    testItem: "Current Rating",
    section: "6.5",
    method: "EIA-364-70D",
    condition: "Method 2, 300A/340A",
    requirement: "Delta T <= 30C @300A; Delta T <= 45C @340A",
    groups: ["-", "-", "-", "-", "-", "-", "-", "-", "2", "-", "-", "-"]
  },
  {
    id: 7,
    testItem: "Mating/Un-mating Force",
    section: "7.1",
    method: "EIA-364-13E",
    condition: "12.7mm/min",
    requirement: "Mating <= 150N; Un-mating >= 20N",
    groups: ["-", "-", "-", "-", "-", "-", "-", "-", "4 6", "-", "-", "2"]
  },
  {
    id: 8,
    testItem: "Durability(Pre.)",
    section: "7.2",
    method: "EIA-364-09D",
    condition: "20 cycles, 5 cycles/min",
    requirement: "No damage",
    groups: ["3(a)", "3(a)", "3(a)", "3(a)", "3(a)", "3(a)", "3(a)", "-", "-", "-", "-", "-"]
  },
  {
    id: 9,
    testItem: "Durability(100 cycles)",
    section: "7.2",
    method: "EIA-364-09D",
    condition: "100 cycles, 5 cycles/min",
    requirement: "No damage",
    groups: ["-", "-", "-", "-", "-", "-", "5", "-", "-", "-", "-", "-"]
  },
  {
    id: 10,
    testItem: "Contact Retention Force",
    section: "7.3",
    method: "EIA-364-29E",
    condition: "12.7mm/min",
    requirement: ">=200N",
    groups: ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "2"]
  },
  {
    id: 11,
    testItem: "Reseating",
    section: "7.4",
    method: "EIA-364-32G",
    condition: "Manually mated/un-mated",
    requirement: "No damage",
    groups: ["6", "10", "-", "8", "-", "-", "-", "6", "10", "-", "-", "-"]
  },
  {
    id: 12,
    testItem: "Thermal Shock",
    section: "8.1",
    method: "EIA-364-32G",
    condition: "-40C~125C, 60min dwell, 5 cycles",
    requirement: "No damage",
    groups: ["4", "-", "-", "-", "-", "-", "-", "4", "-", "-", "-", "-"]
  },
  {
    id: 13,
    testItem: "Cycling Temperature & Humidity",
    section: "8.2",
    method: "EIA-364-31F",
    condition: "Method IV without step 7a, 24H/cycle, 10 cycles",
    requirement: "No damage",
    groups: ["8", "-", "-", "-", "-", "-", "-", "8", "-", "-", "-", "-"]
  },
  {
    id: 14,
    testItem: "High temperature Life",
    section: "8.3",
    method: "EIA-364-17C",
    condition: "125C, 250 hours",
    requirement: "No damage",
    groups: ["4", "-", "4(b)", "-", "-", "-", "-", "4", "-", "-", "-", "-"]
  }
];

export function ProjectWorkbenchMatrixOverview({
  draft,
  snapshot,
  selectedTokenReference,
  onTokenSelect
}: ProjectWorkbenchMatrixOverviewProps): ReactElement {
  if (!snapshot) {
    return (
      <section className="matrix-overview-panel matrix-runtime-overview-panel">
        <header className="matrix-overview-heading">
          <div>
            <h4>Matrix Overview</h4>
            <p>Placeholder runtime projection from Matrix v{draft.version}</p>
          </div>
          <span>{MOCK_MATRIX_ROWS.length} test row(s)</span>
        </header>
        <MockMatrixTable
          selectedTokenReference={selectedTokenReference ?? null}
          onTokenSelect={onTokenSelect ?? (() => undefined)}
        />
      </section>
    );
  }

  return (
    <section className="matrix-overview-panel matrix-runtime-overview-panel">
      <header className="matrix-overview-heading">
        <div>
          <h4>Matrix Overview</h4>
          <p>
            Runtime projection from {draft.status} Matrix v{draft.version}
          </p>
        </div>
        <span>{snapshot.matrix_overview.group_count} group(s)</span>
      </header>

      {snapshot.parser_warnings.length > 0 ? (
        <div className="matrix-runtime-warning-list">
          {snapshot.parser_warnings.map((warning) => (
            <span key={warning}>{warning}</span>
          ))}
        </div>
      ) : null}

      <div className="matrix-runtime-grid" role="list">
        {snapshot.matrix_overview.groups.map((group) => (
          <article className="matrix-runtime-group" key={group.group_identity} role="listitem">
            <header>
              <strong>{group.group_label}</strong>
              <span>
                {group.total_tokens} token(s), {group.unique_sequences} sequence(s)
              </span>
            </header>
            <div className="matrix-runtime-token-list">
              {group.tokens.map((token) => (
                <RuntimeTokenButton
                  key={token.token_reference}
                  selected={selectedTokenReference === token.token_reference}
                  token={token}
                  onTokenSelect={onTokenSelect ?? (() => undefined)}
                />
              ))}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

function MockMatrixTable({
  selectedTokenReference,
  onTokenSelect
}: {
  selectedTokenReference: string | null;
  onTokenSelect: (value: string) => void;
}): ReactElement {
  return (
    <div className="matrix-runtime-table-wrap">
      <table className="matrix-runtime-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Test Item</th>
            <th>Section</th>
            <th>Test Method</th>
            <th>Condition</th>
            <th>Requirement</th>
            {MOCK_GROUPS.map((group) => (
              <th key={group}>{group}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {MOCK_MATRIX_ROWS.map((row) => (
            <tr key={row.id}>
              <td>{row.id}</td>
              <td>{row.testItem}</td>
              <td>{row.section}</td>
              <td>{row.method}</td>
              <td>{row.condition}</td>
              <td>{row.requirement}</td>
              {row.groups.map((value, index) => {
                const group = MOCK_GROUPS[index];
                const tokenRef = `mock:${group}:${firstToken(value)}`;
                return (
                  <td key={`${row.id}-${group}`}>
                    {value === "-" ? (
                      <span className="matrix-runtime-empty-cell">-</span>
                    ) : (
                      <button
                        className={`matrix-runtime-cell-token${selectedTokenReference === tokenRef ? " is-selected" : ""}`}
                        type="button"
                        onClick={() => onTokenSelect(tokenRef)}
                      >
                        {renderTokenParts(value)}
                      </button>
                    )}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function firstToken(value: string): string {
  return value.split(/\s|,/).find(Boolean) ?? value;
}

function renderTokenParts(value: string): ReactElement[] {
  return value.split(" ").map((part, index) => (
    <span className={tokenPartClass(part)} key={`${part}-${index}`}>
      {part}
    </span>
  ));
}

function tokenPartClass(value: string): string {
  if (/[79]/.test(value)) {
    return "matrix-runtime-token-part matrix-runtime-token-part-danger";
  }
  if (/[25]/.test(value)) {
    return "matrix-runtime-token-part matrix-runtime-token-part-current";
  }
  return "matrix-runtime-token-part matrix-runtime-token-part-success";
}

function RuntimeTokenButton({
  token,
  selected,
  onTokenSelect
}: {
  token: RuntimeProjectionMatrixToken;
  selected: boolean;
  onTokenSelect: (value: string) => void;
}): ReactElement {
  return (
    <button
      className={`matrix-runtime-token${selected ? " matrix-runtime-token-selected" : ""}`}
      type="button"
      onClick={() => onTokenSelect(token.token_reference)}
    >
      <span className="matrix-runtime-token-main">
        <strong>{token.raw_token}</strong>
        <em>{token.lifecycle_projection ?? "unknown"}</em>
      </span>
      <span className="matrix-runtime-token-markers">
        <small>{token.attention_projection ?? "none"}</small>
        <small>{token.report_sync_projection ?? "report unknown"}</small>
        <small>{token.evidence_projection ?? "evidence unknown"}</small>
      </span>
    </button>
  );
}
