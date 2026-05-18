import type { ApprovalPackageRequest, ApprovalPackageResponse } from "../../api/client";
import type { ProjectOutputStatusSummary } from "../../api/client";
import type { ApprovalInputSources } from "./useProjectWorkbenchModel";

export type WorkbenchDocumentFreshness = "current" | "stale" | "missing" | "manual" | "failed";

export type WorkbenchDocumentStatus = {
  key: "section2" | "test_record" | "fee_evaluation" | "approval_package";
  label: string;
  freshness: WorkbenchDocumentFreshness;
  path: string | null;
  reason: string;
};

export type WorkbenchVersionStatus = {
  activeDraftVersion: number | null;
  trackedDraftVersion: number | null;
  hasStaleOutputs: boolean;
  downstream: WorkbenchDocumentStatus[];
};

type DeriveVersionStatusInput = {
  activeDraftVersion: number | null;
  trackedDraftVersion: number | null;
  outputStatusSummary: ProjectOutputStatusSummary | null;
  approvalInput: ApprovalPackageRequest;
  approvalInputSources: ApprovalInputSources;
  approvalPreview: ApprovalPackageResponse | null;
  approvalResult: ApprovalPackageResponse | null;
};

export function deriveWorkbenchVersionStatus(
  input: DeriveVersionStatusInput
): WorkbenchVersionStatus {
  if (input.outputStatusSummary) {
    return fromPersistedSummary(input.outputStatusSummary);
  }
  const staleByDraft =
    input.activeDraftVersion !== null &&
    input.trackedDraftVersion !== null &&
    input.activeDraftVersion !== input.trackedDraftVersion;

  const section2 = classifyPathStatus({
    key: "section2",
    label: "Section 2 completion",
    path: input.approvalInput.completed_application_form_path,
    source: input.approvalInputSources.completed_application_form_path,
    staleByDraft
  });
  const testRecord = classifyPathStatus({
    key: "test_record",
    label: "Test record",
    path: input.approvalInput.test_record_output_path,
    source: input.approvalInputSources.test_record_output_path,
    staleByDraft
  });
  const fee = classifyPathStatus({
    key: "fee_evaluation",
    label: "Fee evaluation",
    path: input.approvalInput.fee_evaluation_output_path ?? "",
    source: input.approvalInputSources.fee_evaluation_output_path,
    staleByDraft
  });
  const approvalPackage = classifyApprovalPackageStatus(
    staleByDraft,
    input.approvalPreview,
    input.approvalResult
  );
  const downstream = [section2, testRecord, fee, approvalPackage];

  return {
    activeDraftVersion: input.activeDraftVersion,
    trackedDraftVersion: input.trackedDraftVersion,
    hasStaleOutputs: downstream.some((item) => item.freshness === "stale"),
    downstream
  };
}

function fromPersistedSummary(summary: ProjectOutputStatusSummary): WorkbenchVersionStatus {
  const keyMap: Record<string, WorkbenchDocumentStatus["key"]> = {
    section2_write_back: "section2",
    test_record_form: "test_record",
    fee_evaluation: "fee_evaluation",
    approval_package: "approval_package"
  };
  const labelMap: Record<WorkbenchDocumentStatus["key"], string> = {
    section2: "Section 2 completion",
    test_record: "Test record",
    fee_evaluation: "Fee evaluation",
    approval_package: "Approval package"
  };
  const downstream = summary.items
    .map((item) => {
      const key = keyMap[item.output_kind];
      if (!key) {
        return null;
      }
      return {
        key,
        label: labelMap[key],
        freshness: item.status,
        path: item.output_path,
        reason: item.reason
      } as WorkbenchDocumentStatus;
    })
    .filter((item): item is WorkbenchDocumentStatus => item !== null);

  return {
    activeDraftVersion: summary.active_draft_version,
    trackedDraftVersion: null,
    hasStaleOutputs: downstream.some((item) => item.freshness === "stale"),
    downstream
  };
}

function classifyPathStatus(input: {
  key: "section2" | "test_record" | "fee_evaluation";
  label: string;
  path: string;
  source: "auto" | "manual";
  staleByDraft: boolean;
}): WorkbenchDocumentStatus {
  const normalizedPath = input.path.trim();
  if (!normalizedPath) {
    return {
      key: input.key,
      label: input.label,
      freshness: "missing",
      path: null,
      reason: "No output path is available yet."
    };
  }
  if (input.source === "manual") {
    return {
      key: input.key,
      label: input.label,
      freshness: "manual",
      path: normalizedPath,
      reason: "Manual output reference is present; automatic authority linkage is not verified."
    };
  }
  if (input.staleByDraft) {
    return {
      key: input.key,
      label: input.label,
      freshness: "stale",
      path: normalizedPath,
      reason: "Output reference was captured before the current authority version."
    };
  }
  return {
    key: input.key,
    label: input.label,
    freshness: "current",
    path: normalizedPath,
    reason: "Output reference is aligned with the current authority context."
  };
}

function classifyApprovalPackageStatus(
  staleByDraft: boolean,
  preview: ApprovalPackageResponse | null,
  result: ApprovalPackageResponse | null
): WorkbenchDocumentStatus {
  const latest = result ?? preview;
  if (!latest) {
    return {
      key: "approval_package",
      label: "Approval package",
      freshness: "missing",
      path: null,
      reason: "Approval package output state is not generated yet."
    };
  }
  if (staleByDraft) {
    return {
      key: "approval_package",
      label: "Approval package",
      freshness: "stale",
      path: latest.project_folder_path,
      reason: "Package state was produced before the current authority version."
    };
  }
  if (latest.blockers.length > 0) {
    return {
      key: "approval_package",
      label: "Approval package",
      freshness: "failed",
      path: latest.project_folder_path,
      reason: "Current package projection has blockers and cannot proceed."
    };
  }
  return {
    key: "approval_package",
    label: "Approval package",
    freshness: "current",
    path: latest.project_folder_path,
    reason: result ? "Package output state is current for this authority." : "Package preview state is current for this authority."
  };
}
