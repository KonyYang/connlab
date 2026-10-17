import { useEffect, useRef, useState } from "react";
import { pickLegacyProjectDirectory, previewLegacyProjects, type LegacyProjectPreviewResult } from "../../api/legacyProjects";
import "./legacy-project-preview.css";

export function LegacyProjectPreview({ onBack }: { onBack: () => void }) {
  const [roots, setRoots] = useState<string[]>([]);
  const [manual, setManual] = useState("");
  const [result, setResult] = useState<LegacyProjectPreviewResult | null>(null);
  const [selected, setSelected] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [picking, setPicking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const request = useRef<AbortController | null>(null);
  const live = useRef(true);
  useEffect(() => {
    live.current = true;
    return () => { live.current = false; request.current?.abort(); };
  }, []);

  function changeRoots(next: string[]) {
    setRoots(next); setResult(null); setSelected([]); setError(null); setMessage("");
  }
  function addRoot(path: string) {
    const clean = path.trim().replace(/^"|"$/g, "");
    if (clean && !roots.includes(clean)) changeRoots([...roots, clean]);
  }
  async function choose() {
    if (picking) return;
    setPicking(true); setError(null);
    try {
      const path = await pickLegacyProjectDirectory();
      if (live.current && path) addRoot(path);
    } catch (cause) { if (live.current) setError((cause as Error).message); }
    finally { if (live.current) setPicking(false); }
  }
  async function preview() {
    if (request.current || !roots.length) return;
    const current = new AbortController();
    request.current = current; setBusy(true); setError(null); setResult(null); setSelected([]); setMessage("");
    try {
      const next = await previewLegacyProjects(roots, current.signal);
      if (!live.current || request.current !== current) return;
      setResult(next); setSelected(next.projects.filter(item => item.status === "ready").map(item => item.folder));
    } catch (cause) {
      if (live.current && request.current === current && !current.signal.aborted) setError((cause as Error).message);
    } finally {
      if (live.current && request.current === current) { request.current = null; setBusy(false); }
    }
  }
  function stop() {
    request.current?.abort(); request.current = null; setBusy(false);
    setMessage("已停止预览，所选目录保留，可重新开始。");
  }
  return <section className="legacy-preview" aria-label="旧项目只读批量预览">
    <header className="legacy-preview-heading">
      <div><h1>导入旧项目</h1><p>只读预览 · 原文件和目录结构保持不变</p></div>
      <button type="button" className="ui-secondary-action" disabled={picking} onClick={onBack}>返回 Tools</button>
    </header>
    <section className="legacy-preview-panel" aria-label="选择旧项目目录">
      <h2>1. 选择目录</h2>
      <p>选择一个旧项目，或包含多个项目的父目录。可继续添加其他位置。</p>
      <div className="legacy-preview-actions">
        <button type="button" className="primary-action" disabled={busy || picking || roots.length >= 20} onClick={() => void choose()}>{picking ? "等待选择目录…" : "选择目录"}</button>
        <span>最多添加 20 个位置；每个位置可包含多个项目。</span>
      </div>
      <details><summary>手动填写目录</summary>
        <div className="legacy-preview-manual"><label>目录位置<input value={manual} maxLength={4096} disabled={busy || picking} onChange={event => setManual(event.target.value)} placeholder="粘贴本机可访问的文件夹位置" /></label>
          <button type="button" disabled={busy || picking || !manual.trim() || roots.length >= 20} onClick={() => { addRoot(manual); setManual(""); }}>添加目录</button></div>
      </details>
      {roots.length > 0 && <ul className="legacy-preview-roots">{roots.map(path => <li key={path}><span>{path}</span><button type="button" disabled={busy || picking} aria-label={`移除 ${path}`} onClick={() => changeRoots(roots.filter(item => item !== path))}>移除</button></li>)}</ul>}
      <div className="legacy-preview-actions">
        <button type="button" className="primary-action" disabled={!roots.length || busy || picking} onClick={() => void preview()}>开始预览</button>
        {busy && <><span role="status">正在检查所选目录和项目边界…</span><button type="button" onClick={stop}>停止预览</button></>}
      </div>
      {error && <p role="alert">{error}</p>}{message && <p role="status">{message}</p>}
    </section>
    {result && <section className="legacy-preview-panel" aria-label="预览检查结果">
      <h2>2. 核对项目</h2>
      <p>发现 {result.projects.length} 个项目，已选 {selected.length} 个。当前仅供核对，不会登记项目。</p>
      <p className="legacy-preview-help">重复与冲突提示仅比较本次所选目录；未查询业务库中的既有项目。旧标记只作参考。</p>
      {result.duplicate_roots > 0 && <p>已合并 {result.duplicate_roots} 个重复或重叠的目录选择。</p>}
      {result.truncated && <p role="alert">结果不完整：已达到本次读取限制。请选择更具体的目录后重新预览。</p>}
      {result.diagnostics.length > 0 && <details><summary>查看无法读取或跳过的目录（{result.diagnostics.length}）</summary><ul>{result.diagnostics.map((text, i) => <li key={i}>{text}</li>)}</ul></details>}
      {!result.projects.length ? <p>没有发现项目资料。可以直接选择具体项目目录后重试。</p> : <>
        <div className="legacy-preview-actions">
          <button type="button" onClick={() => setSelected(result.projects.filter(item => item.status === "ready").map(item => item.folder))}>选择无冲突项目</button>
          <button type="button" onClick={() => setSelected([])}>清空选择</button>
        </div>
        <div className="legacy-preview-table"><table aria-label="旧项目预览"><thead><tr><th>选择</th><th>建议编号 / 项目名称</th><th>所在文件夹</th><th>检查结果</th></tr></thead><tbody>{result.projects.map(item => <tr key={item.folder}>
          <td><input type="checkbox" aria-label={`选择 ${item.name}`} checked={selected.includes(item.folder)} onChange={event => setSelected(values => event.target.checked ? [...values, item.folder] : values.filter(value => value !== item.folder))} /></td>
          <td><strong>{item.number || "编号待补充"}</strong><span>{item.name}</span></td><td className="legacy-preview-folder">{item.folder}</td>
          <td><strong className={item.status === "review" ? "legacy-preview-review" : "legacy-preview-ready"}>{item.status === "review" ? "需要核对" : "可预览"}</strong>
            {item.notes.length > 0 && <ul>{item.notes.map((note, i) => <li key={i}>{note}</li>)}</ul>}
            {item.duplicate_folders.length > 0 && <details><summary>其他相同编号或旧标记目录：{item.duplicate_count} 个（最多展示 5 个）</summary><ul>{item.duplicate_folders.map(path => <li key={path}>{path}</li>)}</ul></details>}</td>
        </tr>)}</tbody></table></div>
      </>}
    </section>}
  </section>;
}
