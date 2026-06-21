import { useEffect, useRef, useState } from "react";
import {
  confirmProjectBasicInformation,
  getProject,
  getProjectBasicInformation,
  listProjectLtrs,
  saveProjectBasicInformationDraft,
  type Project,
  type ProjectBasicInformationResponse,
} from "../../api/client";
import { buildProjectIdentityLine } from "../projectIdentity";
import { getBasicInformationConfirmedBy } from "./currentUserDisplay";
import { normalizeBasicInformationFieldValues } from "./basicInformationFieldConfig";

export type BackToWorkbenchOptions = {
  refreshBasicInformation: boolean;
};

export type ProjectBasicInformationModel = {
  response: ProjectBasicInformationResponse | null;
  values: Record<string, string>;
  identityLabel: string;
  loading: boolean;
  saving: boolean;
  confirming: boolean;
  error: string | null;
  savedMessage: string | null;
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
    void getProjectBasicInformation(projectId)
      .then((nextResponse) => {
        if (cancelled) {
          return;
        }
        setResponse(nextResponse);
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
            setError(err instanceof Error ? err.message : "Failed to save Basic Information draft.");
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
  }, [draftDirty, projectId, values]);

  function updateValue(key: string, value: string): void {
    setSavedMessage(null);
    autosaveRevisionRef.current += 1;
    setValues((previous) => ({ ...previous, [key]: value }));
    setDraftDirty(true);
  }

  async function confirm(): Promise<void> {
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
      setError(err instanceof Error ? err.message : "Failed to confirm Basic Information.");
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
    updateValue,
    confirm,
    cancel,
  };
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
    testItemFallback: values.test_item,
  });
}
