import { useLayoutEffect, useRef, useState, type MouseEvent, type ReactElement } from "react";
import { LoadingState } from "../components/common/LoadingState";
import { useProjectRuntimeConsoleModel } from "../features/project-workbench/useProjectRuntimeConsoleModel";
import "../workbench.css";

type ProjectMatrixEditorPageProps = {
  projectId: string;
  onBackToWorkbench: () => void;
};

const GROUP_COLUMNS = ["G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9", "G10", "G11", "G12"];
const HEADER_METRICS = [
  { label: "Groups", value: "12" },
  { label: "Steps", value: "186" },
  { label: "Items", value: "20" }
];
const MATRIX_ROWS = [
  { item: "Examination of Product", section: "5.4", method: "EIA-364-18B", condition: "10x min magnification", requirement: "No detrimental condition" },
  { item: "LLCR", section: "6.1", method: "EIA-364-23E", condition: "20mV max, 100mA max", requirement: "Initial <= 0.40mO; After test <= 0.40mO" },
  { item: "Contact Resistance", section: "6.2", method: "EIA-364-06C", condition: "340A", requirement: "<= 0.20mO" },
  { item: "Dielectric Withstanding Voltage", section: "6.3", method: "EIA-364-20F", condition: "3500V/AC, 1min, mated", requirement: "No arcing or breakdown; leakage < 5mA" },
  { item: "Insulation Resistance", section: "6.4", method: "EIA-364-21F", condition: "500V/DC, 2min", requirement: ">= 1000MO (1GO)" },
  { item: "Current Rating", section: "6.5", method: "EIA-364-70D", condition: "Method 2, 300A/340A", requirement: "Delta T <= 30C @300A; <= 45C @340A" },
  { item: "Mating/Un-mating Force", section: "7.1", method: "EIA-364-13E", condition: "12.7mm/min", requirement: "Mating <= 150N; Un-mating >= 20N" },
  { item: "Durability(Pre.)", section: "7.2", method: "EIA-364-09D", condition: "20 cycles, 5 cycles/min", requirement: "No damage" },
  { item: "Durability(100 cycles)", section: "7.2", method: "EIA-364-09D", condition: "100 cycles, 5 cycles/min", requirement: "No damage" },
  { item: "Contact Retention Force", section: "7.3", method: "EIA-364-29E", condition: "12.7mm/min", requirement: ">= 200N" },
  { item: "Reseating", section: "7.4", method: "EIA-364-32G", condition: "Manual mated/un-mated", requirement: "No damage" },
  { item: "Thermal Shock", section: "8.1", method: "EIA-364-32G", condition: "-40C~125C, 60min dwell", requirement: "No damage" }
];

type EditableMatrixRow = {
  id: string;
  item: string;
  section: string;
  method: string;
  condition: string;
  requirement: string;
  groups: Record<string, string>;
};

type MatrixSnapshot = {
  rows: EditableMatrixRow[];
  groups: string[];
};

type MatrixContextMenu =
  | { kind: "row"; rowIndex: number; x: number; y: number }
  | { kind: "group"; group: string; x: number; y: number };

type MatrixAutoGrowTextareaProps = {
  ariaLabel: string;
  className?: string;
  value: string;
  onChange: (value: string) => void;
};

function buildInitialMatrixRows(): EditableMatrixRow[] {
  return MATRIX_ROWS.map((row, rowIndex) => {
    const groups: Record<string, string> = {};
    GROUP_COLUMNS.forEach((column, groupIndex) => {
      groups[column] = (rowIndex + groupIndex) % 4 === 0 ? "1,3" : "-";
    });
    return {
      id: `matrix-row-${rowIndex}`,
      ...row,
      groups
    };
  });
}

function cloneRows(rows: EditableMatrixRow[]): EditableMatrixRow[] {
  return rows.map((row) => ({
    ...row,
    groups: { ...row.groups }
  }));
}

function buildEmptyRow(groups: string[], rowIndex: number): EditableMatrixRow {
  const groupValues: Record<string, string> = {};
  groups.forEach((group) => {
    groupValues[group] = "-";
  });
  return {
    id: `matrix-row-new-${Date.now()}-${rowIndex}`,
    item: "",
    section: "",
    method: "",
    condition: "",
    requirement: "",
    groups: groupValues
  };
}

function nextGroupName(groups: string[]): string {
  let max = 0;
  groups.forEach((group) => {
    const match = group.match(/^G(\d+)$/i);
    if (!match) {
      return;
    }
    const value = Number(match[1]);
    if (value > max) {
      max = value;
    }
  });
  return `G${max + 1}`;
}

function MatrixAutoGrowTextarea({
  ariaLabel,
  className,
  value,
  onChange
}: MatrixAutoGrowTextareaProps): ReactElement {
  const ref = useRef<HTMLTextAreaElement | null>(null);

  useLayoutEffect(() => {
    const element = ref.current;
    if (!element) {
      return;
    }
    element.style.height = "auto";
    element.style.height = `${element.scrollHeight + 4}px`;
  }, [value]);

  return (
    <textarea
      ref={ref}
      aria-label={ariaLabel}
      className={className ? `matrix-editor-inline-textarea ${className}` : "matrix-editor-inline-textarea"}
      rows={1}
      value={value}
      onChange={(event) => onChange(event.target.value)}
    />
  );
}

const TEST_LIBRARY_GROUPS = [
  {
    title: "Common templates",
    items: ["EIA-364 Standard", "USCAR-2", "LV214", "Custom connector set"]
  },
  {
    title: "Recently used",
    items: ["EIA-364 Connector Template", "High Current Connector", "General Qualification"]
  },
  {
    title: "My favorites",
    items: ["LLCR", "Contact Resistance", "Current Rating"]
  }
];

const TEST_LIBRARY_CATEGORIES = [
  { label: "Electrical", count: 7 },
  { label: "Mechanical", count: 5 },
  { label: "Environmental", count: 6 },
  { label: "Material/Process", count: 2 },
  { label: "Dimension/Appearance", count: 0 },
  { label: "Protective Function", count: 0 },
  { label: "Others", count: 0 }
];

const QUICK_ACTIONS = [
  "Batch requirement fill",
  "Batch condition fill",
  "Batch method fill",
  "Batch step sort",
  "Inspect empty cells"
];

const STEP_WORKSPACE_ROWS = [
  { order: "1", token: "1", item: "Examination of Product", method: "EIA-364-18B" },
  { order: "2", token: "2", item: "LLCR", method: "EIA-364-23E" },
  { order: "3", token: "5", item: "LLCR", method: "EIA-364-23E" },
  { order: "4", token: "7", item: "LLCR", method: "EIA-364-23E" },
  { order: "5", token: "9", item: "LLCR", method: "EIA-364-23E" },
  { order: "6", token: "11", item: "LLCR", method: "EIA-364-23E" },
  { order: "7", token: "3(a)", item: "Durability(Pre.)", method: "EIA-364-09D" },
  { order: "8", token: "3(b)", item: "Durability(Pre.)", method: "EIA-364-09D" },
  { order: "9", token: "3", item: "Thermal Shock", method: "EIA-364-32G" }
];

const TEMPLATE_CARDS = [
  { name: "EIA-364 Connector Template", summary: "20 items / 12 groups / 186 steps", tags: ["General"] },
  { name: "High Current Connector", summary: "18 items / 10 groups / 152 steps", tags: ["Power"] },
  { name: "General Qualification", summary: "16 items / 8 groups / 120 steps", tags: ["Qual"] }
];

const REFERENCE_ROWS = [
  { name: "EIA-364-23E LLCR method", type: "Method", source: "EIA-364", updated: "2024-12-01" },
  { name: "EIA-364-21F insulation method", type: "Method", source: "EIA-364", updated: "2024-11-20" },
  { name: "20mV max, 100mA max condition", type: "Condition", source: "EIA-364-23E", updated: "2024-10-15" },
  { name: "Initial <= 0.40mO", type: "Requirement", source: "Customer spec", updated: "2025-01-10" }
];

export function ProjectMatrixEditorPage({
  projectId,
  onBackToWorkbench
}: ProjectMatrixEditorPageProps): ReactElement {
  const model = useProjectRuntimeConsoleModel(projectId);
  const [editableRows, setEditableRows] = useState<EditableMatrixRow[]>(() => buildInitialMatrixRows());
  const [groupColumns, setGroupColumns] = useState<string[]>(() => [...GROUP_COLUMNS]);
  const [selectedRowId, setSelectedRowId] = useState<string | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<string | null>(null);
  const [lastMessage, setLastMessage] = useState<string>("");
  const [undoStack, setUndoStack] = useState<MatrixSnapshot[]>([]);
  const [contextMenu, setContextMenu] = useState<MatrixContextMenu | null>(null);

  if (!model.project && !model.error) {
    return <LoadingState label="Loading matrix editor..." />;
  }

  const projectLabel = model.project?.product_name ?? "Connector Project";
  const ltr = model.latestLtr ?? "Not registered";
  const bu = model.project?.business_unit || "Not set";
  const requester = model.project?.requestor || "Not set";
  const projectionRef = model.runtimeAuthoritySync.projectionMatrixReference ?? "not loaded";

  const pushSnapshot = (): void => {
    setUndoStack((previous) => [
      ...previous,
      {
        rows: cloneRows(editableRows),
        groups: [...groupColumns]
      }
    ]);
  };

  const getSelectedRowIndex = (): number => editableRows.findIndex((row) => row.id === selectedRowId);

  const updateTextField = (
    rowIndex: number,
    field: keyof Omit<EditableMatrixRow, "groups" | "id">,
    value: string
  ): void => {
    setEditableRows((previous) =>
      previous.map((row, index) => (index === rowIndex ? { ...row, [field]: value } : row))
    );
  };

  const updateGroupField = (rowIndex: number, column: string, value: string): void => {
    setEditableRows((previous) =>
      previous.map((row, index) =>
        index === rowIndex
          ? {
              ...row,
              groups: {
                ...row.groups,
                [column]: value
              }
            }
          : row
      )
    );
  };

  const addRow = (): void => {
    pushSnapshot();
    setEditableRows((previous) => [...previous, buildEmptyRow(groupColumns, previous.length)]);
    setLastMessage("Test item row added");
  };

  const insertRow = (rowIndex: number, direction: "above" | "below"): void => {
    pushSnapshot();
    const insertAt = direction === "above" ? rowIndex : rowIndex + 1;
    setEditableRows((previous) => {
      const next = [...previous];
      next.splice(insertAt, 0, buildEmptyRow(groupColumns, insertAt));
      return next;
    });
    setLastMessage(direction === "above" ? "Row inserted above" : "Row inserted below");
  };

  const duplicateRow = (rowIndex: number): void => {
    pushSnapshot();
    setEditableRows((previous) => {
      const next = [...previous];
      const source = previous[rowIndex];
      const duplicated: EditableMatrixRow = {
        ...source,
        id: `matrix-row-copy-${Date.now()}-${rowIndex}`,
        groups: { ...source.groups }
      };
      next.splice(rowIndex + 1, 0, duplicated);
      return next;
    });
    setLastMessage("Row duplicated");
  };

  const deleteRow = (rowIndex: number): void => {
    if (editableRows.length <= 1) {
      setLastMessage("At least one test item row is required");
      return;
    }
    pushSnapshot();
    const deletingId = editableRows[rowIndex].id;
    setEditableRows((previous) => previous.filter((row) => row.id !== deletingId));
    setSelectedRowId((previous) => (previous === deletingId ? null : previous));
    setLastMessage("Row deleted");
  };

  const moveRow = (rowIndex: number, direction: "up" | "down"): void => {
    if (direction === "up" && rowIndex === 0) {
      setLastMessage("First row cannot move up");
      return;
    }
    if (direction === "down" && rowIndex === editableRows.length - 1) {
      setLastMessage("Last row cannot move down");
      return;
    }
    pushSnapshot();
    setEditableRows((previous) => {
      const next = [...previous];
      const target = direction === "up" ? rowIndex - 1 : rowIndex + 1;
      const [row] = next.splice(rowIndex, 1);
      next.splice(target, 0, row);
      return next;
    });
    setLastMessage(direction === "up" ? "Row moved up" : "Row moved down");
  };

  const addGroup = (): void => {
    pushSnapshot();
    const nextName = nextGroupName(groupColumns);
    setGroupColumns((previous) => [...previous, nextName]);
    setEditableRows((previous) =>
      previous.map((row) => ({
        ...row,
        groups: {
          ...row.groups,
          [nextName]: "-"
        }
      }))
    );
    setLastMessage(`${nextName} added`);
  };

  const insertGroup = (group: string, direction: "left" | "right"): void => {
    const currentIndex = groupColumns.indexOf(group);
    if (currentIndex < 0) {
      return;
    }
    pushSnapshot();
    const nextName = nextGroupName(groupColumns);
    const insertAt = direction === "left" ? currentIndex : currentIndex + 1;
    setGroupColumns((previous) => {
      const next = [...previous];
      next.splice(insertAt, 0, nextName);
      return next;
    });
    setEditableRows((previous) =>
      previous.map((row) => ({
        ...row,
        groups: {
          ...row.groups,
          [nextName]: "-"
        }
      }))
    );
    setLastMessage(`${nextName} inserted`);
  };

  const duplicateGroup = (group: string): void => {
    const currentIndex = groupColumns.indexOf(group);
    if (currentIndex < 0) {
      return;
    }
    pushSnapshot();
    const nextName = nextGroupName(groupColumns);
    setGroupColumns((previous) => {
      const next = [...previous];
      next.splice(currentIndex + 1, 0, nextName);
      return next;
    });
    setEditableRows((previous) =>
      previous.map((row) => ({
        ...row,
        groups: {
          ...row.groups,
          [nextName]: row.groups[group]
        }
      }))
    );
    setLastMessage(`${group} duplicated`);
  };

  const deleteGroup = (group: string): void => {
    if (groupColumns.length <= 1) {
      setLastMessage("At least one group column is required");
      return;
    }
    pushSnapshot();
    setGroupColumns((previous) => previous.filter((value) => value !== group));
    setEditableRows((previous) =>
      previous.map((row) => {
        const groups = { ...row.groups };
        delete groups[group];
        return { ...row, groups };
      })
    );
    setSelectedGroup((previous) => (previous === group ? null : previous));
    setLastMessage(`${group} deleted`);
  };

  const moveGroup = (group: string, direction: "left" | "right"): void => {
    const currentIndex = groupColumns.indexOf(group);
    if (currentIndex < 0) {
      return;
    }
    if (direction === "left" && currentIndex === 0) {
      setLastMessage("First group cannot move left");
      return;
    }
    if (direction === "right" && currentIndex === groupColumns.length - 1) {
      setLastMessage("Last group cannot move right");
      return;
    }
    pushSnapshot();
    setGroupColumns((previous) => {
      const next = [...previous];
      const target = direction === "left" ? currentIndex - 1 : currentIndex + 1;
      const [item] = next.splice(currentIndex, 1);
      next.splice(target, 0, item);
      return next;
    });
    setLastMessage(direction === "left" ? `${group} moved left` : `${group} moved right`);
  };

  const undoLast = (): void => {
    setUndoStack((previous) => {
      if (previous.length === 0) {
        setLastMessage("Nothing to undo");
        return previous;
      }
      const snapshot = previous[previous.length - 1];
      setEditableRows(cloneRows(snapshot.rows));
      setGroupColumns([...snapshot.groups]);
      setSelectedRowId(null);
      setSelectedGroup(null);
      setLastMessage("Last structural action reverted");
      return previous.slice(0, -1);
    });
  };

  const openRowContextMenu = (event: MouseEvent, rowIndex: number): void => {
    event.preventDefault();
    setSelectedRowId(editableRows[rowIndex].id);
    setSelectedGroup(null);
    setContextMenu({ kind: "row", rowIndex, x: event.clientX, y: event.clientY });
  };

  const openGroupContextMenu = (event: MouseEvent, group: string): void => {
    event.preventDefault();
    setSelectedGroup(group);
    setSelectedRowId(null);
    setContextMenu({ kind: "group", group, x: event.clientX, y: event.clientY });
  };

  const runContextAction = (action: () => void): void => {
    action();
    setContextMenu(null);
  };

  const selectRow = (rowId: string): void => {
    setSelectedRowId(rowId);
    setSelectedGroup(null);
    setContextMenu(null);
  };

  const selectGroup = (group: string): void => {
    setSelectedGroup(group);
    setSelectedRowId(null);
    setContextMenu(null);
  };

  return (
    <section className="workbench-page matrix-editor-shell matrix-editor-target-shell" onClick={() => setContextMenu(null)}>
      <section className="matrix-editor-target-header">
        <div className="matrix-editor-target-title">
          <button className="matrix-editor-link-button" type="button" onClick={onBackToWorkbench}>
            Back to Workbench
          </button>
          <h2>Matrix Editor</h2>
          <p>Definition Studio</p>
        </div>
        <div className="matrix-editor-target-project">
          <strong>{projectLabel}</strong>
          <span>LTR Registered</span>
          <p>LTR: {ltr}</p>
          <p>BU: {bu}</p>
          <p>Requester: {requester}</p>
        </div>
        <div className="matrix-editor-target-metrics">
          {HEADER_METRICS.map((metric) => (
            <article key={metric.label}>
              <span>{metric.label}</span>
              <strong>{metric.value}</strong>
            </article>
          ))}
        </div>
        <div className="matrix-editor-target-actions">
          <button disabled type="button">Save</button>
          <button className="matrix-editor-primary-action" disabled type="button">Publish for approval</button>
          <button disabled type="button">More</button>
        </div>
      </section>

      <section className="matrix-editor-actionbar">
        <div className="matrix-editor-actionbar-main">
          <button type="button" onClick={addRow}>Add test item</button>
          <button type="button" onClick={addGroup}>Add group</button>
          <button type="button" onClick={undoLast} disabled={undoStack.length === 0}>Undo</button>
        </div>
        <div className="matrix-editor-actionbar-side">
          <button disabled type="button">Display options</button>
          <button disabled type="button">Filter</button>
          <input placeholder="Search conditions/items..." type="text" />
        </div>
      </section>

      <section className="matrix-editor-studio">
        <aside className="matrix-editor-test-library" aria-label="Test Library">
          <header>
            <h3>Test Library</h3>
            <input placeholder="Search method/condition..." type="text" />
          </header>
          {TEST_LIBRARY_GROUPS.map((group) => (
            <section key={group.title}>
              <h4>{group.title}</h4>
              <ul>
                {group.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </section>
          ))}
          <section>
            <h4>All test items (20)</h4>
            <ul className="matrix-editor-test-library-categories">
              {TEST_LIBRARY_CATEGORIES.map((category) => (
                <li key={category.label}>
                  <span>{category.label}</span>
                  <strong>{category.count}</strong>
                </li>
              ))}
            </ul>
          </section>
          <section>
            <h4>Quick actions</h4>
            <ul>
              {QUICK_ACTIONS.map((action) => (
                <li key={action}>{action}</li>
              ))}
            </ul>
          </section>
        </aside>

        <section className="matrix-editor-grid-surface">
          <div className="matrix-editor-grid-toolbar">
            <label>
              Matrix Version
              <select defaultValue="v1">
                <option value="v1">v1</option>
              </select>
            </label>
            <label>
              Group
              <select defaultValue="all">
                <option value="all">All groups</option>
              </select>
            </label>
            <label>
              Filter
              <input placeholder="Search test item..." type="text" />
            </label>
            <label>
              Section
              <select defaultValue="all">
                <option value="all">All sections</option>
              </select>
            </label>
          </div>

          <div className="matrix-editor-main-table-wrap">
            <div className="matrix-editor-context-actions" aria-live="polite">
              <strong>
                {selectedRowId ? "Row selected" : selectedGroup ? `Group selected: ${selectedGroup}` : "Selection: none"}
              </strong>
              <span>{lastMessage || "Header and first five columns are structurally fixed."}</span>
            </div>
            <table className="matrix-editor-main-table">
              <thead>
                <tr>
                  <th className="matrix-editor-row-selector-head">No.</th>
                  <th>Test Item</th>
                  <th>Section</th>
                  <th>Method</th>
                  <th>Condition</th>
                  <th>Requirement</th>
                  {groupColumns.map((column) => (
                    <th
                      className={`matrix-editor-group-band${selectedGroup === column ? " matrix-editor-group-selected" : ""}`}
                      key={column}
                      onClick={() => selectGroup(column)}
                      onContextMenu={(event) => openGroupContextMenu(event, column)}
                    >
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {editableRows.map((row, rowIndex) => (
                  <tr
                    className={selectedRowId === row.id ? "matrix-editor-row-selected" : undefined}
                    key={row.id}
                  >
                    <td className="matrix-editor-row-selector-cell">
                      <button
                        type="button"
                        className="matrix-editor-row-selector-button"
                        aria-label={`Select row ${rowIndex + 1}`}
                        onClick={() => selectRow(row.id)}
                        onContextMenu={(event) => openRowContextMenu(event, rowIndex)}
                      >
                        {rowIndex + 1}
                      </button>
                    </td>
                    <td>
                      <MatrixAutoGrowTextarea
                        ariaLabel={`Row ${rowIndex + 1} test item`}
                        value={row.item}
                        onChange={(value) => updateTextField(rowIndex, "item", value)}
                      />
                    </td>
                    <td>
                      <MatrixAutoGrowTextarea
                        ariaLabel={`Row ${rowIndex + 1} section`}
                        value={row.section}
                        onChange={(value) => updateTextField(rowIndex, "section", value)}
                      />
                    </td>
                    <td>
                      <MatrixAutoGrowTextarea
                        ariaLabel={`Row ${rowIndex + 1} method`}
                        value={row.method}
                        onChange={(value) => updateTextField(rowIndex, "method", value)}
                      />
                    </td>
                    <td>
                      <MatrixAutoGrowTextarea
                        ariaLabel={`Row ${rowIndex + 1} condition`}
                        value={row.condition}
                        onChange={(value) => updateTextField(rowIndex, "condition", value)}
                      />
                    </td>
                    <td>
                      <MatrixAutoGrowTextarea
                        ariaLabel={`Row ${rowIndex + 1} requirement`}
                        value={row.requirement}
                        onChange={(value) => updateTextField(rowIndex, "requirement", value)}
                      />
                    </td>
                    {groupColumns.map((column) => (
                      <td
                        className={selectedGroup === column ? "matrix-editor-group-selected-cell" : undefined}
                        key={`${column}-${rowIndex}`}
                      >
                        <MatrixAutoGrowTextarea
                          ariaLabel={`Row ${rowIndex + 1} ${column}`}
                          className="matrix-editor-inline-input"
                          value={row.groups[column]}
                          onChange={(value) => updateGroupField(rowIndex, column, value)}
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {contextMenu ? (
              <div
                className="matrix-editor-context-menu"
                style={{ left: contextMenu.x, top: contextMenu.y }}
                onClick={(event) => event.stopPropagation()}
              >
                {contextMenu.kind === "row" ? (
                  <>
                    <button type="button" onClick={() => runContextAction(() => insertRow(contextMenu.rowIndex, "above"))}>Insert above</button>
                    <button type="button" onClick={() => runContextAction(() => insertRow(contextMenu.rowIndex, "below"))}>Insert below</button>
                    <button type="button" onClick={() => runContextAction(() => duplicateRow(contextMenu.rowIndex))}>Duplicate row</button>
                    <button
                      type="button"
                      disabled={contextMenu.rowIndex === 0}
                      title={contextMenu.rowIndex === 0 ? "First row cannot move up" : ""}
                      onClick={() => runContextAction(() => moveRow(contextMenu.rowIndex, "up"))}
                    >
                      Move up
                    </button>
                    <button
                      type="button"
                      disabled={contextMenu.rowIndex === editableRows.length - 1}
                      title={contextMenu.rowIndex === editableRows.length - 1 ? "Last row cannot move down" : ""}
                      onClick={() => runContextAction(() => moveRow(contextMenu.rowIndex, "down"))}
                    >
                      Move down
                    </button>
                    <button
                      type="button"
                      disabled={editableRows.length <= 1}
                      title={editableRows.length <= 1 ? "At least one test item row is required" : ""}
                      onClick={() => runContextAction(() => deleteRow(contextMenu.rowIndex))}
                    >
                      Delete row
                    </button>
                  </>
                ) : (
                  <>
                    <button type="button" onClick={() => runContextAction(() => insertGroup(contextMenu.group, "left"))}>Insert left</button>
                    <button type="button" onClick={() => runContextAction(() => insertGroup(contextMenu.group, "right"))}>Insert right</button>
                    <button type="button" onClick={() => runContextAction(() => duplicateGroup(contextMenu.group))}>Duplicate group</button>
                    <button
                      type="button"
                      disabled={groupColumns.indexOf(contextMenu.group) === 0}
                      title={groupColumns.indexOf(contextMenu.group) === 0 ? "First group cannot move left" : ""}
                      onClick={() => runContextAction(() => moveGroup(contextMenu.group, "left"))}
                    >
                      Move left
                    </button>
                    <button
                      type="button"
                      disabled={groupColumns.indexOf(contextMenu.group) === groupColumns.length - 1}
                      title={groupColumns.indexOf(contextMenu.group) === groupColumns.length - 1 ? "Last group cannot move right" : ""}
                      onClick={() => runContextAction(() => moveGroup(contextMenu.group, "right"))}
                    >
                      Move right
                    </button>
                    <button
                      type="button"
                      disabled={groupColumns.length <= 1}
                      title={groupColumns.length <= 1 ? "At least one group column is required" : ""}
                      onClick={() => runContextAction(() => deleteGroup(contextMenu.group))}
                    >
                      Delete group
                    </button>
                  </>
                )}
              </div>
            ) : null}
          </div>
        </section>

        <aside className="matrix-editor-step-workspace" aria-label="Group Step Workspace">
          <header>
            <p>Group 3</p>
            <h3>Step preview</h3>
          </header>
          <div className="matrix-editor-step-meta">
            <span>14 steps</span>
            <em>Defined</em>
          </div>
          <nav>
            {["Step order", "Group info", "Fee/Time", "History"].map((item, index) => (
              <button className={index === 0 ? "is-active" : ""} disabled key={item} type="button">
                {item}
              </button>
            ))}
          </nav>
          <table>
            <thead>
              <tr>
                <th>Order</th>
                <th>Token</th>
                <th>Item</th>
                <th>Method</th>
              </tr>
            </thead>
            <tbody>
              {STEP_WORKSPACE_ROWS.map((row) => (
                <tr key={`${row.order}-${row.token}`}>
                  <td>{row.order}</td>
                  <td>{row.token}</td>
                  <td>{row.item}</td>
                  <td>{row.method}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="matrix-editor-step-note">
            <strong>Suggestion</strong>
            <p>Group contains LLCR steps, verify sample split before fee confirmation.</p>
          </div>
          <dl className="matrix-editor-step-kpi">
            <div><dt>Sample count</dt><dd>5</dd></div>
            <div><dt>Expected completion</dt><dd>2025-06-16</dd></div>
            <div><dt>Est. fee (group)</dt><dd>RMB 600.00</dd></div>
          </dl>
          <label>
            Group note
            <textarea placeholder="Enter group note..." />
          </label>
          <button className="matrix-editor-primary-action" disabled type="button">Apply to Matrix</button>
        </aside>
      </section>

      <section className="matrix-editor-supporting">
        <section className="matrix-editor-templates" aria-label="Templates">
          <header>
            <h3>Templates</h3>
            <button disabled type="button">More templates</button>
          </header>
          <input placeholder="Search templates..." type="text" />
          <div className="matrix-editor-template-grid">
            {TEMPLATE_CARDS.map((card) => (
              <article key={card.name}>
                <h4>{card.name}</h4>
                <p>{card.summary}</p>
                <div>
                  {card.tags.map((tag) => (
                    <span key={tag}>{tag}</span>
                  ))}
                </div>
                <footer>
                  <button disabled type="button">Preview</button>
                  <button disabled type="button">Use</button>
                </footer>
              </article>
            ))}
            <article className="matrix-editor-template-create">
              <h4>Create custom template</h4>
            </article>
          </div>
        </section>

        <section className="matrix-editor-reference-library" aria-label="Reference Library">
          <header>
            <h3>Reference Library</h3>
            <button disabled type="button">More references</button>
          </header>
          <nav>
            {["Method standards", "Conditions", "Requirements", "Spec clauses"].map((tab, index) => (
              <button className={index === 0 ? "is-active" : ""} disabled key={tab} type="button">
                {tab}
              </button>
            ))}
          </nav>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Source</th>
                <th>Updated</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {REFERENCE_ROWS.map((row) => (
                <tr key={row.name}>
                  <td>{row.name}</td>
                  <td>{row.type}</td>
                  <td>{row.source}</td>
                  <td>{row.updated}</td>
                  <td>
                    <button disabled type="button">Use</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="matrix-editor-projection-note">
            Projection Ref: {projectionRef}
          </p>
        </section>
      </section>
    </section>
  );
}

