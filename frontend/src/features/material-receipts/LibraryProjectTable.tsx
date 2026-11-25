import { useEffect, useRef } from "react";
import type { ReferenceProject } from "../../api/referenceLibrary";
import "./library-project-table.css";

const pageSize = 20;

type Props = {
  projects: ReferenceProject[];
  selectedKey: string;
  onSelect: (key: string) => void;
  onResume: (operationId: string) => void;
  receiving: boolean;
};

export function LibraryProjectTable({ projects, selectedKey, onSelect, onResume, receiving }: Props) {
  const selectedIndex = projects.findIndex(row => row.key === selectedKey);
  const page = Math.floor(Math.max(0, selectedIndex) / pageSize);
  const start = page * pageSize;
  const rows = projects.slice(start, start + pageSize);
  const pageCount = Math.ceil(projects.length / pageSize);
  const scroller = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scroller.current) scroller.current.scrollTop = 0;
  }, [page]);

  return <>
    <div className="library-table-scroll" ref={scroller}>
      <table className="library-project-table" aria-label="Project materials">
        <colgroup><col className="library-id-column" /><col /></colgroup>
        <thead><tr><th scope="col">Project ID</th><th scope="col">Sample Description</th></tr></thead>
        <tbody>{rows.map(row => {
          const number = row.number || "—";
          const title = row.title || "—";
          const active = row.key === selectedKey;
          return <tr key={row.key} className={active ? "is-selected" : undefined}
            onClick={() => onSelect(row.key)}>
            <td><button type="button" className="library-id-button" aria-pressed={active}
              aria-label={number + " " + title}>{number}</button></td>
            <td>{title}
              {row.operation_id && row.intake_status !== "completed" && <div className="library-receipt-recovery">
                <span>Receipt incomplete</span>
                <button type="button" disabled={receiving} onClick={event => {
                  event.stopPropagation();
                  onResume(row.operation_id!);
                }}>Continue receipt</button>
              </div>}
            </td>
          </tr>;
        })}</tbody>
      </table>
    </div>
    {pageCount > 0 && <footer className="library-project-pager">
      <span>Showing {start + 1}-{start + rows.length} of {projects.length}</span>
      <nav aria-label="Project materials pages">
        <button type="button" disabled={page === 0} onClick={() => onSelect(projects[start - pageSize].key)}>Prev</button>
        <span>Page {page + 1} / {pageCount}</span>
        <button type="button" disabled={page + 1 >= pageCount} onClick={() => onSelect(projects[start + pageSize].key)}>Next</button>
      </nav>
    </footer>}
  </>;
}
