import { useEffect, useState, type CSSProperties } from "react";
import { browseReferenceFiles, type BrowseFile, type BrowseResult } from "../../api/referenceLibrary";
import { UiIcon } from "../../components/common/UiIcon";
import "./material-file-tree.css";

type ListProps = {
  projectKey: string;
  rows: BrowseFile[];
  selectedPath?: string;
  showPaths: boolean;
  onSelect: (file: BrowseFile) => void;
  onOpen: (file: BrowseFile) => void;
  onOpenContaining: (file: BrowseFile) => void;
  onCollapse: (folder: string) => void;
};
type DirectoryProps = Omit<ListProps, "rows"> & { directory: BrowseFile; depth: number };

function FolderContents({ directory, depth, ...actions }: DirectoryProps) {
  const [result, setResult] = useState<BrowseResult | null>(null);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setResult(null);
    setError("");
    browseReferenceFiles(actions.projectKey, directory.relative_path, controller.signal).then(data => {
      if (!controller.signal.aborted) setResult(data);
    }).catch(reason => {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : "Could not read this folder.");
    });
    return () => controller.abort();
  }, [actions.projectKey, directory.relative_path, attempt]);

  if (error) return <div className="material-tree-note" role="alert">{error} <button onClick={() => setAttempt(value => value + 1)}>Retry</button></div>;
  if (!result) return <p className="material-tree-note" role="status">Loading files…</p>;
  return <>
    {result.warnings.map(note => <p className="material-tree-note" key={note} role="status">{note}</p>)}
    {result.items.length ? <MaterialFileList {...actions} rows={result.items} depth={depth + 1} />
      : !result.warnings.length && <p className="material-tree-note">This folder is empty.</p>}
  </>;
}

function FolderRow(props: DirectoryProps) {
  const [expanded, setExpanded] = useState(false);
  return <li>
    <button type="button" className="material-tree-row" aria-expanded={expanded} onClick={() => {
      if (expanded) props.onCollapse(props.directory.relative_path);
      setExpanded(!expanded);
    }}>
      <span className="material-tree-chevron" aria-hidden="true"><UiIcon name="chevron-down" /></span>
      <span className="file-folder"><UiIcon name="folder" /></span><span>{props.directory.name}</span>
    </button>
    {expanded && <FolderContents {...props} />}
  </li>;
}

function FileRow({file, showPaths, selectedPath, onOpen, onSelect, onOpenContaining}:
  Omit<ListProps, "rows" | "projectKey" | "onCollapse"> & {file: BrowseFile}) {
  return <li>
    <div className="material-file-line">
      <button type="button" className="material-tree-row" aria-pressed={selectedPath === file.relative_path}
        onClick={() => onSelect(file)} onDoubleClick={() => onOpen(file)}
        onKeyDown={event => {
          if (event.key === "Enter") {
            event.preventDefault();
            if (!event.repeat) onOpen(file);
          }
        }}>
        <span className="material-tree-spacer" aria-hidden="true" />
        <span className="file-symbol"><UiIcon name="file" /></span>
        <span>{file.name}{showPaths && <small>{file.relative_path}</small>}</span>
      </button>
      <button type="button" className="material-file-trigger" title="Open containing folder"
        aria-label={`Open containing folder for ${file.name}`}
        onClick={() => onOpenContaining(file)}><UiIcon name="folder" /></button>
    </div>
  </li>;
}

export function MaterialFileList({ rows, depth = 0, ...actions }: ListProps & {depth?:number}) {
  return <ul className="material-tree" style={{"--folder-depth": depth} as CSSProperties}
    aria-label={depth === 0 ? "Project material files" : undefined}>
    {rows.map(file => file.is_directory
      ? <FolderRow {...actions} key={file.relative_path} directory={file} depth={depth} />
      : <FileRow key={file.relative_path} file={file} {...actions} />)}
  </ul>;
}
