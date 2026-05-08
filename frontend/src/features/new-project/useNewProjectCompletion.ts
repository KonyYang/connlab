import { useEffect, useState } from "react";

import {
  completeNewProject,
  commitLtrWorkbookWrite,
  confirmIntakeCase,
  type IntakeCaseReviewItem
} from "../../api/client";
import type { NewProjectSetupConfirmationValues } from "./NewProjectSetupConfirmationPanel";

type UseNewProjectCompletionInput = {
  activeCase: IntakeCaseReviewItem | null;
  resetKey: string | null;
  setupValues: NewProjectSetupConfirmationValues;
  onCompleted: (projectId: string) => void;
};

export type NewProjectCompletionModel = {
  completionError: string | null;
  completionLoading: boolean;
  completionResult: string | null;
  complete: () => Promise<void>;
};

export function useNewProjectCompletion({
  activeCase,
  resetKey,
  setupValues,
  onCompleted
}: UseNewProjectCompletionInput): NewProjectCompletionModel {
  const [completionLoading, setCompletionLoading] = useState(false);
  const [completionError, setCompletionError] = useState<string | null>(null);
  const [completionResult, setCompletionResult] = useState<string | null>(null);
  const [completionProjectId, setCompletionProjectId] = useState<string | null>(null);
  const [completionWorkbookNumber, setCompletionWorkbookNumber] = useState<string | null>(null);

  useEffect(() => {
    setCompletionError(null);
    setCompletionResult(null);
    setCompletionProjectId(null);
    setCompletionWorkbookNumber(null);
  }, [resetKey]);

  async function complete(): Promise<void> {
    if (!activeCase) {
      return;
    }
    setCompletionLoading(true);
    setCompletionError(null);
    if (!completionWorkbookNumber) {
      setCompletionResult(null);
    }
    try {
      const projectId =
        completionProjectId
        ?? activeCase.confirmed_project_id
        ?? (await confirmIntakeCase(activeCase.case_id)).project_id;
      setCompletionProjectId(projectId);
      const planDate = new Date().toISOString().slice(0, 10);
      if (!completionWorkbookNumber) {
        const workbookCommit = await commitLtrWorkbookWrite(projectId, {
          plan_date: planDate,
          operator_confirmed: true,
          preview_acknowledged: true,
          number_input:
            setupValues.ltrMode === "specified" ? setupValues.specifiedLtrNumber.trim() : null,
          test_item: setupValues.testItem,
          sample_description: setupValues.sampleDescription,
          location: setupValues.location,
          test_type_in_sheet: setupValues.testTypeInSheet,
          project_leader: setupValues.projectLeader,
          requested_date: planDate,
          operator_note: "new_project_external_ltr_workbook_commit"
        });
        setCompletionWorkbookNumber(workbookCommit.ltr_number);
        setCompletionResult(
          `LTR workbook ${workbookActionLabel(workbookCommit.action)} ${workbookCommit.ltr_number} at ${workbookCommit.sheet_name} row ${workbookCommit.row_number}. Backup: ${workbookCommit.backup_path}`
        );
      }
      const result = await completeNewProject(activeCase.case_id, {
        ltr_mode: setupValues.ltrMode,
        specified_ltr_number:
          setupValues.ltrMode === "specified" ? setupValues.specifiedLtrNumber.trim() : null,
        operator_confirmed: true,
        plan_date: planDate,
        test_item: setupValues.testItem,
        sample_description: setupValues.sampleDescription,
        location: setupValues.location,
        test_type_in_sheet: setupValues.testTypeInSheet,
        project_leader: setupValues.projectLeader
      });
      onCompleted(result.project_id);
    } catch (error) {
      setCompletionError(
        error instanceof Error ? error.message : "Unable to complete project creation."
      );
    } finally {
      setCompletionLoading(false);
    }
  }

  return {
    completionError,
    completionLoading,
    completionResult,
    complete
  };
}

function workbookActionLabel(action: string): string {
  if (action === "replace_existing") {
    return "replaced";
  }
  return "wrote";
}
