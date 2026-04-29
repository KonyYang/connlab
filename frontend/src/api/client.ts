export type Project = {
  project_id: string;
  project_no?: string | null;
  product_name: string;
  requestor: string;
  status: string;
  business_unit?: string | null;
  created_on?: string | null;
};

export type ProjectCreateInput = {
  project_no?: string | null;
  product_name: string;
  requestor: string;
  business_unit?: string;
};

export type ApplicationForm = {
  form_id: string;
  project_id: string;
  form_no: string;
  revision: string;
  requester: string;
  email?: string | null;
  project_number?: string | null;
  requested_testing?: string | null;
};

export type PrecheckIssue = {
  issue_id: string;
  category: string;
  level: string;
  message: string;
  field_name?: string | null;
  resolved: boolean;
};

export type PrecheckResult = {
  result_id: string;
  application_form_id: string;
  status: string;
  checked_on?: string | null;
  issues: PrecheckIssue[];
};

export type LtrRecord = {
  ltr_id: string;
  project_id: string;
  ltr_number: string;
  status: string;
  registered_on?: string | null;
  requested_by?: string | null;
  requested_date?: string | null;
  notes?: string | null;
};

export type FolderPlanItem = {
  source_path: string;
  target_path: string;
  item_type: string;
  conflict: boolean;
};

export type FolderPlan = {
  project_folder_path: string;
  conflict: boolean;
  items: FolderPlanItem[];
};

export type FolderGeneration = {
  folder_id: string;
  project_folder_path: string;
  generated_paths: string[];
};

export type FolderRequest = {
  template_path: string;
  target_root: string;
  dl_number?: string;
  plan_date?: string;
};

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...init?.headers
    }
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function listProjects(): Promise<Project[]> {
  return requestJson<Project[]>("/api/projects");
}

export function createProject(input: ProjectCreateInput): Promise<Project> {
  return requestJson<Project>("/api/projects", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function getProject(projectId: string): Promise<Project> {
  return requestJson<Project>(`/api/projects/${encodeURIComponent(projectId)}`);
}

export function uploadApplicationForm(
  projectId: string,
  file: File
): Promise<ApplicationForm> {
  const formData = new FormData();
  formData.append("file", file);
  return requestJson<ApplicationForm>(
    `/api/projects/${encodeURIComponent(projectId)}/application-form`,
    {
      method: "POST",
      body: formData
    }
  );
}

export function runPrecheck(applicationFormId: string): Promise<PrecheckResult> {
  return requestJson<PrecheckResult>(
    `/api/application-forms/${encodeURIComponent(applicationFormId)}/precheck/run`,
    { method: "POST" }
  );
}

export function getLatestPrecheck(projectId: string): Promise<PrecheckResult> {
  return requestJson<PrecheckResult>(
    `/api/projects/${encodeURIComponent(projectId)}/prechecks/latest`
  );
}

export function resolvePrecheckIssue(issueId: string): Promise<PrecheckIssue> {
  return requestJson<PrecheckIssue>(
    `/api/precheck-issues/${encodeURIComponent(issueId)}/resolve`,
    { method: "PATCH" }
  );
}

export function registerLtr(
  projectId: string,
  input: { ltr_number: string; requested_by?: string; notes?: string }
): Promise<LtrRecord> {
  return requestJson<LtrRecord>(`/api/projects/${encodeURIComponent(projectId)}/ltr`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function listProjectLtrs(projectId: string): Promise<LtrRecord[]> {
  return requestJson<LtrRecord[]>(`/api/projects/${encodeURIComponent(projectId)}/ltr`);
}

export function previewFolder(projectId: string, input: FolderRequest): Promise<FolderPlan> {
  return requestJson<FolderPlan>(`/api/projects/${encodeURIComponent(projectId)}/folder/preview`, {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function generateFolder(
  projectId: string,
  input: FolderRequest
): Promise<FolderGeneration> {
  return requestJson<FolderGeneration>(
    `/api/projects/${encodeURIComponent(projectId)}/folder/generate`,
    {
      method: "POST",
      body: JSON.stringify(input)
    }
  );
}
