import { useEffect, useRef, useState } from "react";
import {
  confirmProjectBasicInformation,
  getNewProjectCompletionOptions,
  getProject,
  getProjectBasicInformation,
  getProjectLifecycle,
  isProjectLifecycleReadonlyErrorDetail,
  listProjectLtrs,
  saveProjectBasicInformationDraft,
  type NewProjectCompletionOptions,
  type Project,
  type ProjectBasicInformationResponse,
  type ProjectLifecycleResponse,
} from "../../api/client";
import {
  deriveProjectLifecycleReadonlyView,
  deriveReadonlyApiErrorMessage,
  type ProjectLifecycleReadonlyView,
} from "../project-lifecycle/projectLifecycleReadonlyModel";
import { buildProjectIdentityLine } from "../projectIdentity";
import { getBasicInformationConfirmedBy } from "./currentUserDisplay";
import { normalizeBasicInformationFieldValues } from "./basicInformationFieldConfig";

export type BackToWorkbenchOptions = {
  refreshBasicInformation: boolean;
};

export type ProjectBasicInformationModel = {
  response: ProjectBasicInformationResponse | null;
  values: Record<string, string>;
  testTypeInSheetOptions: string[];
  identityLabel: string;
  loading: boolean;
  saving: boolean;
  confirming: boolean;
  error: string | null;
  savedMessage: string | null;
  lifecycleReadonlyView: ProjectLifecycleReadonlyView;
  updateValue: (key: string, value: string) => void;
  confirm: () => Promise<void>;
  cancel: () => void;
};

export function useProjectBasicInformationModel({
  projectId,
  onBackToWorkbench,
}: {
  projectId: string;
  onBackToWorkbench: (options: BackToWorkbenchOptions) => void;
}): ProjectBasicInformationModel {
  const [response, setResponse] = useState<ProjectBasicInformationResponse | null>(null);
  const [values, setValues] = useState<Record<string, string>>({});
  const [completionOptions, setCompletionOptions] =
    useState<NewProjectCompletionOptions | null>(null);
  const [lifecycle, setLifecycle] = useState<ProjectLifecycleResponse | null>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [latestLtr, setLatestLtr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [savedMessage, setSavedMessage] = useState<string | null>(null);
  const [draftDirty, setDraftDirty] = useState(false);
  const autosaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const autosaveRevisionRef = useRef(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    void Promise.all([
      getProjectBasicInformation(projectId),
      getProjectLifecycle(projectId),
      getNewProjectCompletionOptions(),
    ])
      .then(([nextResponse, nextLifecycle, nextCompletionOptions]) => {
        if (cancelled) {
          return;
        }
        setResponse(nextResponse);
        setLifecycle(nextLifecycle);
        setCompletionOptions(nextCompletionOptions);
        setValues(normalizeBasicInformationFieldValues(nextResponse.draft.values));
        setDraftDirty(false);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load Basic Information.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  useEffect(() => {
    let cancelled = false;
    void Promise.allSettled([getProject(projectId), listProjectLtrs(projectId)]).then(
      ([projectResult, ltrResult]) => {
        if (cancelled) {
          return;
        }
        if (projectResult.status === "fulfilled") {
          setProject(projectResult.value);
        }
        if (ltrResult.status === "fulfilled") {
          const ltrs = ltrResult.value;
          setLatestLtr(ltrs.length > 0 ? ltrs[ltrs.length - 1].ltr_number : null);
        }
      }
    );
    return () => {
      cancelled = true;
    };
  }, [projectId]);

  useEffect(() => {
    if (lifecycle?.readonly) {
      return;
    }
    if (!draftDirty) {
      return;
    }
    if (autosaveTimerRef.current) {
      clearTimeout(autosaveTimerRef.current);
    }
    autosaveTimerRef.current = setTimeout(() => {
      const revision = autosaveRevisionRef.current;
      const draftValues = { ...values };
      setSaving(true);
      setError(null);
      void saveProjectBasicInformationDraft(projectId, draftValues)
        .then((nextResponse) => {
          if (autosaveRevisionRef.current !== revision) {
            return;
          }
          setResponse(nextResponse);
          setSavedMessage("Draft saved automatically.");
          setDraftDirty(false);
        })
        .catch((err) => {
          if (autosaveRevisionRef.current === revision) {
            setError(readonlyAwareErrorMessage(err, "Failed to save Basic Information draft."));
          }
        })
        .finally(() => {
          if (autosaveRevisionRef.current === revision) {
            setSaving(false);
          }
        });
    }, 500);
    return () => {
      if (autosaveTimerRef.current) {
        clearTimeout(autosaveTimerRef.current);
      }
    };
  }, [draftDirty, lifecycle, projectId, values]);

  function updateValue(key: string, value: string): void {
    if (lifecycle?.readonly) {
      return;
    }
    setSavedMessage(null);
    autosaveRevisionRef.current += 1;
    setValues((previous) => {
      const nextValues = { ...previous, [key]: value };
      if (key === "post_testing_disposition") {
        const previousDisposition = previous.post_testing_disposition?.trim() ?? "";
        const previousSampleDeposition = previous.sample_deposition?.trim() ?? "";
        if (
          !previousSampleDeposition ||
          previousSampleDeposition === previousDisposition
        ) {
          nextValues.sample_deposition = value;
        }
      }
      return nextValues;
    });
    setDraftDirty(true);
  }

  async function confirm(): Promise<void> {
    if (lifecycle?.readonly) {
      setError(deriveProjectLifecycleReadonlyView(lifecycle).message);
      return;
    }
    if (autosaveTimerRef.current) {
      clearTimeout(autosaveTimerRef.current);
    }
    setConfirming(true);
    setError(null);
    try {
      const nextValues = normalizeBasicInformationFieldValues(values);
      const nextResponse = await confirmProjectBasicInformation(
        projectId,
        nextValues,
        getBasicInformationConfirmedBy()
      );
      setResponse(nextResponse);
      setValues(normalizeBasicInformationFieldValues(nextResponse.draft.values));
      onBackToWorkbench({ refreshBasicInformation: true });
    } catch (err) {
      setError(readonlyAwareErrorMessage(err, "Failed to confirm Basic Information."));
    } finally {
      setConfirming(false);
    }
  }

  function cancel(): void {
    onBackToWorkbench({ refreshBasicInformation: false });
  }

  return {
    response,
    values,
    testTypeInSheetOptions: completionOptions?.test_type_in_sheet_options ?? [],
    identityLabel: buildBasicInformationIdentityLabel({
      latestLtr,
      project,
      values,
      projectId,
    }),
    loading,
    saving,
    confirming,
    error,
    savedMessage,
    lifecycleReadonlyView: deriveProjectLifecycleReadonlyView(lifecycle),
    updateValue,
    confirm,
    cancel,
  };
}

function readonlyAwareErrorMessage(err: unknown, fallback: string): string {
  const detail =
    err && typeof err === "object" && "detail" in err
      ? (err as { detail: unknown }).detail
      : null;
  if (
    isProjectLifecycleReadonlyErrorDetail(detail)
  ) {
    return deriveReadonlyApiErrorMessage(detail);
  }
  return err instanceof Error ? err.message : fallback;
}

function buildBasicInformationIdentityLabel({
  latestLtr,
  project,
  values,
  projectId,
}: {
  latestLtr: string | null;
  project: Project | null;
  values: Record<string, string>;
  projectId: string;
}): string {
  return buildProjectIdentityLine({
    project,
    latestLtr,
    projectId,
    productFallback: values.product_description,
    testItemFallback: values.test_item || values.tests_to_be_performed,
  });
}
