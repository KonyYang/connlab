import { useEffect, useState, type FormEvent, type ReactElement } from "react";
import {
  generateFolder,
  getLatestPrecheck,
  getProject,
  listProjectLtrs,
  previewFolder,
  registerLtr,
  runPrecheck,
  uploadApplicationForm,
  type ApplicationForm,
  type FolderGeneration,
  type FolderPlan,
  type FolderRequest,
  type LtrRecord,
  type PrecheckResult,
  type Project
} from "../api/client";

type ProjectWorkbenchPageProps = {
  projectId: string;
  onBack: () => void;
};

const EMPTY_FOLDER: FolderRequest = {
  template_path: "",
  target_root: "",
  dl_number: "",
  plan_date: new Date().toISOString().slice(0, 10)
};

export function ProjectWorkbenchPage({
  projectId,
  onBack
}: ProjectWorkbenchPageProps): ReactElement {
  const [project, setProject] = useState<Project | null>(null);
  const [formRecord, setFormRecord] = useState<ApplicationForm | null>(null);
  const [precheck, setPrecheck] = useState<PrecheckResult | null>(null);
  const [ltrs, setLtrs] = useState<LtrRecord[]>([]);
  const [folderInput, setFolderInput] = useState<FolderRequest>(EMPTY_FOLDER);
  const [folderPlan, setFolderPlan] = useState<FolderPlan | null>(null);
  const [folderGeneration, setFolderGeneration] = useState<FolderGeneration | null>(null);
  const [ltrNumber, setLtrNumber] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void loadWorkbench();
  }, [projectId]);

  async function loadWorkbench(): Promise<void> {
    try {
      setProject(await getProject(projectId));
      setLtrs(await listProjectLtrs(projectId));
      try {
        setPrecheck(await getLatestPrecheck(projectId));
      } catch {
        setPrecheck(null);
      }
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function uploadForm(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    const fileInput = event.currentTarget.elements.namedItem("applicationForm");
    const file = fileInput instanceof HTMLInputElement ? fileInput.files?.[0] : null;
    if (!file) {
      setError("Choose an application form first.");
      return;
    }

    try {
      const uploaded = await uploadApplicationForm(projectId, file);
      setFormRecord(uploaded);
      setPrecheck(null);
      setMessage(`Application form ${uploaded.form_no} Rev ${uploaded.revision} uploaded.`);
      setError(null);
      await loadWorkbench();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function runPrecheckNow(): Promise<void> {
    if (!formRecord) {
      setError("Upload an application form before running precheck.");
      return;
    }
    try {
      const result = await runPrecheck(formRecord.form_id);
      setPrecheck(result);
      setMessage(`Precheck status: ${result.status}`);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function submitLtr(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    try {
      const record = await registerLtr(projectId, { ltr_number: ltrNumber });
      setLtrNumber("");
      setLtrs((current) => [record, ...current]);
      setMessage(`LTR registered: ${record.ltr_number}`);
      setError(null);
      await loadWorkbench();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function previewFolderNow(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    try {
      const plan = await previewFolder(projectId, folderInput);
      setFolderPlan(plan);
      setFolderGeneration(null);
      setMessage(plan.conflict ? "Folder preview has conflicts." : "Folder preview is clear.");
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function generateFolderNow(): Promise<void> {
    try {
      const generated = await generateFolder(projectId, folderInput);
      setFolderGeneration(generated);
      setMessage(`Folder generated: ${generated.project_folder_path}`);
      setError(null);
      await loadWorkbench();
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <section className="panel">
      <button className="text-button" type="button" onClick={onBack}>
        Back to projects
      </button>
      {error && <p className="error">Workflow error: {error}</p>}
      {message && <p className="success">{message}</p>}
      {project && (
        <>
          <div className="section-heading">
            <p className="eyebrow">Workbench</p>
            <h2>{project.product_name}</h2>
            <p>
              {project.project_no} · {project.requestor} · status: {project.status}
            </p>
          </div>

          <div className="task-grid">
            <ApplicationFormCard formRecord={formRecord} onSubmit={uploadForm} />
            <PrecheckCard precheck={precheck} onRun={runPrecheckNow} disabled={!formRecord} />
            <LtrCard ltrs={ltrs} ltrNumber={ltrNumber} setLtrNumber={setLtrNumber} onSubmit={submitLtr} />
            <FolderCard
              folderInput={folderInput}
              folderPlan={folderPlan}
              folderGeneration={folderGeneration}
              setFolderInput={setFolderInput}
              onPreview={previewFolderNow}
              onGenerate={generateFolderNow}
            />
          </div>
        </>
      )}
    </section>
  );
}

function ApplicationFormCard({
  formRecord,
  onSubmit
}: {
  formRecord: ApplicationForm | null;
  onSubmit: (event: FormEvent<HTMLFormElement>) => Promise<void>;
}): ReactElement {
  return (
    <article className="task-card">
      <h3>Application Form</h3>
      <p>Status: {formRecord ? `${formRecord.form_no} Rev ${formRecord.revision}` : "not uploaded"}</p>
      <form className="card-form" onSubmit={onSubmit}>
        <input name="applicationForm" type="file" accept=".docx" />
        <button className="primary-action" type="submit">Upload form</button>
      </form>
    </article>
  );
}

function PrecheckCard({
  precheck,
  disabled,
  onRun
}: {
  precheck: PrecheckResult | null;
  disabled: boolean;
  onRun: () => Promise<void>;
}): ReactElement {
  return (
    <article className="task-card">
      <h3>Precheck</h3>
      <p>Status: {precheck?.status ?? "not run"}</p>
      <button className="primary-action" disabled={disabled} type="button" onClick={() => void onRun()}>
        Run precheck
      </button>
      <ul className="issue-list">
        {precheck?.issues.map((issue) => (
          <li key={issue.issue_id}>{issue.level}: {issue.message}</li>
        ))}
      </ul>
    </article>
  );
}

function LtrCard({
  ltrs,
  ltrNumber,
  setLtrNumber,
  onSubmit
}: {
  ltrs: LtrRecord[];
  ltrNumber: string;
  setLtrNumber: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => Promise<void>;
}): ReactElement {
  return (
    <article className="task-card">
      <h3>LTR</h3>
      <p>Status: {ltrs[0]?.status ?? "not registered"}</p>
      <form className="card-form" onSubmit={onSubmit}>
        <input
          required
          placeholder="LTR number"
          value={ltrNumber}
          onChange={(event) => setLtrNumber(event.target.value)}
        />
        <button className="primary-action" type="submit">Register LTR</button>
      </form>
      {ltrs[0] && <p>Latest: {ltrs[0].ltr_number}</p>}
    </article>
  );
}

function FolderCard({
  folderInput,
  folderPlan,
  folderGeneration,
  setFolderInput,
  onPreview,
  onGenerate
}: {
  folderInput: FolderRequest;
  folderPlan: FolderPlan | null;
  folderGeneration: FolderGeneration | null;
  setFolderInput: (value: FolderRequest) => void;
  onPreview: (event: FormEvent<HTMLFormElement>) => Promise<void>;
  onGenerate: () => Promise<void>;
}): ReactElement {
  return (
    <article className="task-card wide-card">
      <h3>Project Folder</h3>
      <p>Status: {folderGeneration ? "generated" : folderPlan ? "previewed" : "not previewed"}</p>
      <form className="card-form" onSubmit={onPreview}>
        <input
          required
          placeholder="Template path"
          value={folderInput.template_path}
          onChange={(event) => setFolderInput({ ...folderInput, template_path: event.target.value })}
        />
        <input
          required
          placeholder="Target root"
          value={folderInput.target_root}
          onChange={(event) => setFolderInput({ ...folderInput, target_root: event.target.value })}
        />
        <input
          placeholder="DL number"
          value={folderInput.dl_number ?? ""}
          onChange={(event) => setFolderInput({ ...folderInput, dl_number: event.target.value })}
        />
        <button className="primary-action" type="submit">Preview folder</button>
      </form>
      {folderPlan && (
        <div className="folder-result">
          <p>Target: {folderPlan.project_folder_path}</p>
          <p>Conflict: {String(folderPlan.conflict)}</p>
          <button
            className="primary-action"
            disabled={folderPlan.conflict}
            type="button"
            onClick={() => void onGenerate()}
          >
            Generate folder
          </button>
        </div>
      )}
      {folderGeneration && <p>Generated paths: {folderGeneration.generated_paths.length}</p>}
    </article>
  );
}
