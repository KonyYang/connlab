import { useEffect, useId, useRef, useState } from "react";
import "./reportAuthoringPanel.css";
import { ReportFactUpdates } from "./ReportFactUpdates";
import { ReportResultsImport } from "./ReportResultsImport";
import { ReportResultUpdate } from "./ReportResultUpdate";
import { ReportPhotoSlots } from "./ReportPhotoSlots";
import { ReportCustomerCopy } from "./ReportCustomerCopy";
import {
  getReportAuthoring, uploadReportSource, saveReportMapping, selectReportBase, downloadReportArtifact,
  type ReportAuthoringState, type ReportSourceRole, type ReportMapping, type ReportMappingInput,
} from "../../api/reportAuthoring";

const roles: [ReportSourceRole, string][] = [
  ["original", "This project's Internal Report"], ["layout_reference", "Approved report / layout reference"],
  ["specification", "Specification"], ["temperature", "Temperature measurements"], ["cr", "Contact resistance"],
  ["mechanical", "Mechanical Force Summary"], ["photo", "Photo"], ["evidence", "Supporting evidence"],
];
const emptyMapping = (): Omit<ReportMappingInput, "expected_revision" | "source_id"> => ({
  kind: "specification", label: "", source_locator: "", value: "", reason: "", status: "pending",
  group_id: "", row_id: "", step_token: "", sample_ids: [],
  report_text: "",
});

export function ReportAuthoringPanel({ projectId, disabled = false, onOperationStart }: {
  projectId: string; disabled?: boolean; onOperationStart?: () => (() => void) | null;
}) {
  const [open, setOpen] = useState(false);
  const panelId = useId();
  const entryHeading = useRef<HTMLHeadingElement | null>(null);
  const [focusTarget, setFocusTarget] = useState<0 | 1 | 2 | null>(null);
  const sectionHeadings = useRef<Array<HTMLHeadingElement | null>>([]);
  const [state, setState] = useState<ReportAuthoringState | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [role, setRole] = useState<ReportSourceRole>("original");
  const [sourceId, setSourceId] = useState("");
  const [mapping, setMapping] = useState(emptyMapping);
  const sequence = useRef(0);
  const operation = useRef<{ releaseOutside: () => void } | null>(null);
  const currentProject = useRef(projectId);
  currentProject.current = projectId;
  useEffect(() => {
    operation.current?.releaseOutside(); operation.current = null;
    sequence.current += 1; setState(null); setOpen(false); setFocusTarget(null); setBusy(false); setError("");
    setFile(null); setSourceId(""); setMapping(emptyMapping());
    return () => { sequence.current += 1; operation.current?.releaseOutside(); operation.current = null; };
  }, [projectId]);
  useEffect(() => {
    if (!open || !state || focusTarget === null) return;
    const heading = sectionHeadings.current[focusTarget];
    if (!heading) return;
    heading.focus({ preventScroll: true });
    heading.scrollIntoView?.({ block: "start", behavior: "auto" });
    setFocusTarget(null);
  }, [open, state, focusTarget]);

  function beginOperation(): (() => void) | null {
    if (operation.current || disabled || currentProject.current !== projectId) return null;
    const releaseOutside = onOperationStart ? onOperationStart() : () => undefined;
    if (!releaseOutside) return null;
    const token = { releaseOutside };
    operation.current = token; setBusy(true);
    return () => {
      if (operation.current !== token) return;
      operation.current = null; releaseOutside(); setBusy(false);
    };
  }

  function acceptChanged(next: ReportAuthoringState) {
    if (currentProject.current === projectId && next.project_id === projectId) setState(next);
  }

  async function run(operation: () => Promise<ReportAuthoringState>) {
    const release = beginOperation(); if (!release) return;
    const request = ++sequence.current; const owner = projectId;
    setBusy(true); setError("");
    try {
      const result = await operation();
      if (request !== sequence.current || owner !== currentProject.current) return;
      setState(result);
      setSourceId(previous => result.sources.some(source => source.source_id === previous) ? previous : result.sources[0]?.source_id || "");
    } catch (reason) {
      if (request === sequence.current && owner === currentProject.current)
        setError(reason instanceof Error ? reason.message : "Report preparation failed. Reload and retry.");
    } finally {
      release();
    }
  }

  async function download(url: string) {
    const release = beginOperation(); if (!release) return;
    const request = ++sequence.current; const owner = projectId;
    setBusy(true); setError("");
    try {
      const result = await downloadReportArtifact(url);
      if (request !== sequence.current || owner !== currentProject.current) return;
      const href = URL.createObjectURL(result.blob); const link = document.createElement("a");
      link.href = href; link.download = result.fileName || "Report_Draft.docx"; link.click();
      setTimeout(() => URL.revokeObjectURL(href), 1000);
    } catch (reason) {
      if (request === sequence.current && owner === currentProject.current)
        setError(reason instanceof Error ? reason.message : "Download failed. Retry the download.");
    } finally { release(); }
  }

  function edit(item: ReportMapping) {
    setSourceId(item.source_id);
    const { mapping_id, kind, label, source_locator, value, status, reason, group_id, row_id, step_token, sample_ids, report_text } = item;
    setMapping({ mapping_id, kind, label, source_locator, value, status, reason, group_id, row_id, step_token, sample_ids, report_text: report_text || "" });
  }

  const locked = busy || disabled;
  const latest = state?.outputs[state.outputs.length - 1];
  const customer = state?.customer_outputs?.[state.customer_outputs.length - 1];
  const pendingCount = state?.mappings.filter(item => item.status !== "confirmed").length || 0;
  const steps = [
    { title: "Choose report base", purpose: "Retain an original or approved layout, then confirm sources and project mappings.",
      status: state ? `${state.sources.length} retained sources · ${latest ? "Working copy available" : "Report base needed"}` : "Open to load saved sources." },
    { title: "Update report content", purpose: "Update project facts, temperature / CR results, mechanical results and photos.",
      status: state ? `${pendingCount} mappings pending confirmation · ${latest ? "Working copy available" : "Choose a base first"}` : "Open to load saved content." },
    { title: "Review customer copy", purpose: "Generate a separate customer copy and check content and disclosure before delivery.",
      status: state ? (customer ? (customer.status === "package_checked" ? "Package checked · not formal approval" : "Customer copy needs review") : "No customer review copy yet") : "Open to load customer review status." },
  ];
  function openSection(index: 0 | 1 | 2) {
    setOpen(true); setFocusTarget(index);
    if (!state) void run(() => getReportAuthoring(projectId));
  }
  function backToSteps() {
    entryHeading.current?.focus({ preventScroll: true });
    entryHeading.current?.scrollIntoView?.({ block: "start", behavior: "auto" });
  }
  return <section className="report-workspace-card report-preparation" aria-label="Report sources and mappings">
    <h2 ref={entryHeading} tabIndex={-1}>Report preparation</h2>
    <p className="report-workspace-note">Prepare a new report copy from retained evidence. Original files stay unchanged; checks do not formally release a report.</p>
    <ol className="report-preparation-actions">
      {steps.map((step, index) => <li key={step.title}>
        <button type="button" className="secondary-action" disabled={locked} aria-controls={`${panelId}-section-${index}`} aria-expanded={open}
          onClick={() => openSection(index as 0 | 1 | 2)}><span aria-hidden="true">{index + 1}. </span>{step.title}</button>
        <p>{step.purpose}</p><small>{step.status}</small>
      </li>)}
    </ol>
    {open && <button type="button" aria-controls={`${panelId}-details`} aria-expanded={open} disabled={locked}
      onClick={() => { setOpen(false); setFocusTarget(null); }}>Hide preparation tools</button>}
    {open && <div id={`${panelId}-details`}>
      <p className="report-workspace-note">Use a retained original or approved report as the base. Only new copies are produced; original files are not changed or formally released.</p>
      {error && <p role="alert">{error}</p>}
      {busy && <p role="status">Preparing report evidence...</p>}
      <button type="button" disabled={locked} onClick={() => void run(() => getReportAuthoring(projectId))}>Reload saved evidence</button>
      {state && <>
        <section className="report-preparation-region" id={`${panelId}-section-0`} aria-labelledby={`${panelId}-heading-0`}>
        <h3 id={`${panelId}-heading-0`} ref={element => { sectionHeadings.current[0] = element; }} tabIndex={-1}>1. Choose report base</h3>
        <button type="button" className="report-preparation-back" onClick={backToSteps}>Back to report steps</button>
        {!latest && <p className="report-preparation-guidance">Retain this project's report or an approved layout reference, then select Use as report base to create a working copy.</p>}
        <fieldset disabled={locked}>
          <legend>Retain a source</legend>
          <label>Source role <select value={role} onChange={event => setRole(event.target.value as ReportSourceRole)}>
            {roles.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select></label>
          <label>Source file <input type="file" accept=".docx,.xlsx,.csv,.pdf,.png,.jpg,.jpeg,.txt"
            onChange={event => setFile(event.target.files?.[0] || null)} /></label>
          <button type="button" disabled={!file} onClick={() => file && void run(() => uploadReportSource(projectId, file, role, state.revision))}>Retain source copy</button>
        </fieldset>
        <ul>{state.sources.map(source => <li key={source.source_id}>
          <span>{source.file_name}</span> — {roles.find(([value]) => value === source.role)?.[1]}
          <button type="button" disabled={locked} onClick={() => void download(source.download_url)}>Download source</button>
          {(source.role === "original" || source.role === "layout_reference") && <button type="button" disabled={locked}
            onClick={() => void run(() => selectReportBase(projectId, source.source_id, state.revision))}>Use as report base</button>}
        </li>)}</ul>
        {latest && <div>
          <p>Working copy: {latest.file_name} — {latest.status === "needs_review" ? "Needs review" : latest.status}</p>
          <ul>{latest.issues.map((issue, index) => <li key={index}>{issue}</li>)}</ul>
          <button type="button" disabled={locked} onClick={() => void download(latest.download_url)}>Download {latest.file_name}</button>
        </div>}
        {state.sources.length > 0 && <fieldset disabled={locked}>
          <legend>Confirmed mappings and project decisions</legend>
          <label>Mapping source <select value={sourceId} onChange={event => setSourceId(event.target.value)}>
            {state.sources.map(source => <option key={source.source_id} value={source.source_id}>{source.file_name}</option>)}
          </select></label>
          <label>Mapping type <select value={mapping.kind} onChange={event => setMapping({ ...mapping, kind: event.target.value as ReportMapping["kind"] })}>
            {["specification", "identity", "temperature", "cr", "mechanical", "photo", "acceptance"].map(kind => <option key={kind}>{kind}</option>)}
          </select></label>
          <label>Mapping label <input value={mapping.label} onChange={event => setMapping({ ...mapping, label: event.target.value })} /></label>
          <label>Source location <input placeholder="Sheet / cells, PDF page or photo identifier" value={mapping.source_locator}
            onChange={event => setMapping({ ...mapping, source_locator: event.target.value })} /></label>
          <label>Matrix Group / Step <select value={state.context.steps.findIndex(step => step.group_id === mapping.group_id && step.row_id === mapping.row_id && step.step_token === mapping.step_token)}
            onChange={event => { const step = state.context.steps[Number(event.target.value)]; setMapping({ ...mapping,
              group_id: step?.group_id || "", row_id: step?.row_id || "", step_token: step?.step_token || "" }); }}>
            <option value={-1}>Not a step-specific mapping</option>
            {state.context.steps.map((step, index) => <option key={index} value={index}>Group {step.group_label} / {step.step_token} / {step.test_item}</option>)}
          </select></label>
          <label>Sample IDs <input value={mapping.sample_ids.join(", ")} onChange={event => setMapping({ ...mapping, sample_ids: event.target.value.split(",").map(item => item.trim()).filter(Boolean) })} /></label>
          <label>Confirmed value <input value={mapping.value} onChange={event => setMapping({ ...mapping, value: event.target.value })} /></label>
          {["identity", "specification"].includes(mapping.kind) && <label>Exact old report text (optional replacement)
            <input value={mapping.report_text || ""} onChange={event => setMapping({ ...mapping, report_text: event.target.value })} />
          </label>}
          <label>Evidence / decision reason <textarea value={mapping.reason} onChange={event => setMapping({ ...mapping, reason: event.target.value })} /></label>
          <label><input type="checkbox" checked={mapping.status === "confirmed"} onChange={event => setMapping({ ...mapping, status: event.target.checked ? "confirmed" : "pending" })} />I have checked this mapping for this project</label>
          <p>Leave unresolved decisions pending. Previous projects' Pass and special acceptance reasons are not approvals for this project.</p>
          <button type="button" disabled={!mapping.label.trim() || !mapping.source_locator.trim()} onClick={() => void run(() => saveReportMapping(projectId, {
            ...mapping, source_id: sourceId, expected_revision: state.revision,
          }))}>Save mapping</button>
          {mapping.mapping_id && <button type="button" onClick={() => setMapping(emptyMapping())}>New mapping</button>}
        </fieldset>}
        <ul>{state.mappings.map(item => <li key={item.mapping_id}><strong>{item.label}</strong> — {item.status === "confirmed" ? "Confirmed" : "Pending confirmation"}: {item.value || "No decision"}
          <small> ({item.source_locator})</small> <button disabled={locked} type="button" onClick={() => edit(item)}>Edit mapping</button></li>)}</ul>
        </section>
        <section className="report-preparation-region" id={`${panelId}-section-1`} aria-labelledby={`${panelId}-heading-1`}>
        <h3 id={`${panelId}-heading-1`} ref={element => { sectionHeadings.current[1] = element; }} tabIndex={-1}>2. Update report content</h3>
        <button type="button" className="report-preparation-back" onClick={backToSteps}>Back to report steps</button>
        {!latest && <p className="report-preparation-guidance">Choose a report base before updating content.</p>}
        <ReportFactUpdates projectId={projectId} state={state} disabled={locked} beginOperation={beginOperation} onChanged={acceptChanged} />
        <ReportResultsImport key={projectId} projectId={projectId} state={state} disabled={locked} beginOperation={beginOperation} onChanged={acceptChanged} />
        <ReportResultUpdate projectId={projectId} state={state} disabled={locked} beginOperation={beginOperation} onChanged={acceptChanged} />
        <ReportPhotoSlots projectId={projectId} state={state} disabled={locked} beginOperation={beginOperation} onChanged={acceptChanged} />
        </section>
        <section className="report-preparation-region" id={`${panelId}-section-2`} aria-labelledby={`${panelId}-heading-2`}>
        <h3 id={`${panelId}-heading-2`} ref={element => { sectionHeadings.current[2] = element; }} tabIndex={-1}>3. Review customer copy</h3>
        <button type="button" className="report-preparation-back" onClick={backToSteps}>Back to report steps</button>
        {!latest ? <p className="report-preparation-guidance">Create a working copy and confirm its content before generating a customer review copy.</p>
          : !customer && <p className="report-preparation-guidance">Check the working copy, then generate a customer review copy below. No report is formally released by these checks.</p>}
        <ReportCustomerCopy projectId={projectId} state={state} disabled={locked} beginOperation={beginOperation} onChanged={acceptChanged} />
        </section>
      </>}
    </div>}
  </section>;
}
