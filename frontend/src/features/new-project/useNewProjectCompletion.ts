import { useEffect, useState } from "react";

import {
  completeNewProject,
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

  useEffect(() => {
    setCompletionError(null);
    setCompletionResult(null);
  }, [resetKey]);

  async function complete(): Promise<void> {
    if (!activeCase) {
      return;
    }
    setCompletionLoading(true);
    setCompletionError(null);
    setCompletionResult(null);
    try {
      const planDate = new Date().toISOString().slice(0, 10);
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
      storeLastLtrApplyResult({
        project_id: result.project_id,
        ltr_number: result.ltr_number,
        workbook_sheet_name: result.workbook_sheet_name ?? null,
        workbook_row_number: result.workbook_row_number ?? null,
        workbook_backup_path: result.workbook_backup_path ?? null,
        occurred_at: new Date().toISOString()
      });
      setCompletionResult(completionResultText(result));
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

type LastLtrApplyResult = {
  project_id: string;
  ltr_number: string;
  workbook_sheet_name: string | null;
  workbook_row_number: number | null;
  workbook_backup_path: string | null;
  occurred_at: string;
};

const LAST_LTR_APPLY_RESULT_KEY = "connlab:last_ltr_apply_result";

function storeLastLtrApplyResult(payload: LastLtrApplyResult): void {
  try {
    window.sessionStorage.setItem(LAST_LTR_APPLY_RESULT_KEY, JSON.stringify(payload));
  } catch {
    // Ignore storage failures; completion flow should continue.
  }
}

function completionResultText(result: {
  ltr_number: string;
  workbook_sheet_name?: string | null;
  workbook_row_number?: number | null;
  workbook_backup_path?: string | null;
}): string {
  const location =
    result.workbook_sheet_name && result.workbook_row_number
      ? ` at ${result.workbook_sheet_name} row ${result.workbook_row_number}`
      : "";
  const backup = result.workbook_backup_path ? `. Backup: ${result.workbook_backup_path}` : "";
  return `LTR workbook wrote ${result.ltr_number}${location}${backup}`;
}
