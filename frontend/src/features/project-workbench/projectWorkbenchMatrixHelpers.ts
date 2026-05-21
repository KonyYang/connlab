import type {
  MatrixPreviewResponse,
  ProjectTestPlanDraftCreateRequest,
  ProjectTestPlanDraftGroup,
  ProjectTestPlanDraftPayload,
  ProjectTestPlanDraftStep
} from "../../api/client";

export type MatrixSummary = {
  groupCount: number;
  stepCount: number;
  warningCount: number;
};

export function buildMatrixSummary(groups: ProjectTestPlanDraftGroup[] | undefined, warningCount: number): MatrixSummary {
  const normalizedGroups = groups ?? [];
  const stepCount = normalizedGroups.reduce((total, group) => total + (group.steps?.length ?? 0), 0);
  return {
    groupCount: normalizedGroups.length,
    stepCount,
    warningCount
  };
}

export function durationText(step: ProjectTestPlanDraftStep): string {
  if (step.estimated_duration_hint) {
    return step.estimated_duration_hint;
  }
  if (step.duration_hint) {
    return step.duration_hint;
  }
  if (typeof step.estimated_duration_days === "number") {
    return `${step.estimated_duration_days} day(s)`;
  }
  if (typeof step.duration_days === "number") {
    return `${step.duration_days} day(s)`;
  }
  if (typeof step.estimated_duration_hours === "number") {
    return `${step.estimated_duration_hours} hour(s)`;
  }
  return "Duration pending";
}

export function updateStepField(
  groups: ProjectTestPlanDraftGroup[],
  groupIndex: number,
  stepIndex: number,
  key: "raw_token" | "test_item" | "method_summary" | "judgement_criteria" | "condition_summary",
  value: string
): ProjectTestPlanDraftGroup[] {
  return groups.map((group, currentGroupIndex) => {
    if (currentGroupIndex !== groupIndex) {
      return group;
    }
    return {
      ...group,
      steps: (group.steps ?? []).map((step, currentStepIndex) => {
        if (currentStepIndex !== stepIndex) {
          return step;
        }
        return { ...step, [key]: value };
      })
    };
  });
}

export function removeStep(
  groups: ProjectTestPlanDraftGroup[],
  groupIndex: number,
  stepIndex: number
): ProjectTestPlanDraftGroup[] {
  return groups.map((group, currentGroupIndex) => {
    if (currentGroupIndex !== groupIndex) {
      return group;
    }
    return {
      ...group,
      steps: (group.steps ?? []).filter((_, currentStepIndex) => currentStepIndex !== stepIndex)
    };
  });
}

export function addStep(groups: ProjectTestPlanDraftGroup[], groupIndex: number): ProjectTestPlanDraftGroup[] {
  return groups.map((group, currentGroupIndex) => {
    if (currentGroupIndex !== groupIndex) {
      return group;
    }
    return {
      ...group,
      steps: [
        ...(group.steps ?? []),
        {
          raw_token: "",
          test_item: "",
          method_summary: "",
          judgement_criteria: "",
          condition_summary: ""
        }
      ]
    };
  });
}

export function mapPreviewToDraftPayload(preview: MatrixPreviewResponse): ProjectTestPlanDraftPayload {
  return {
    groups: preview.groups.map((group) => ({
      group_key: group.group_key,
      group_label: group.group_label,
      sample_size: group.sample_size ?? null,
      source_table_index: group.source_table_index,
      steps: group.steps.map((step) => ({
        raw_token: step.raw_token,
        suffix_note: step.suffix_note ?? null,
        sequence: step.sequence,
        test_item: step.test_item,
        source_section: step.source_section,
        condition_summary: step.condition_summary,
        method_summary: step.method_summary,
        reference_standard: step.reference_standard,
        judgement_criteria: step.judgement_criteria,
        estimated_duration_hint: step.estimated_duration_hint,
        source_table_index: step.source_table_index,
        source_row_index: step.source_row_index,
        note: step.source_note ?? (step.warnings.length > 0 ? step.warnings.join(" | ") : null)
      }))
    })),
    warnings: [...preview.warnings],
    blockers: [...preview.blockers]
  };
}

export function buildDraftCreateRequestFromPreview(
  preview: MatrixPreviewResponse,
  sourceAssetId: string | null = null
): ProjectTestPlanDraftCreateRequest {
  return {
    source_document_path: preview.source_document_path,
    source_document_name: preview.source_document_name,
    source_format: preview.source_format,
    payload: mapPreviewToDraftPayload(preview),
    source_asset_id: sourceAssetId,
    status: "draft"
  };
}

export function buildManualStarterDraftCreateRequest(): ProjectTestPlanDraftCreateRequest {
  return {
    source_document_path: "manual://project-matrix",
    source_document_name: "Manual Matrix",
    source_format: "manual",
    payload: {
      groups: [
        {
          group_key: "group_1",
          group_label: "Group 1",
          sample_size: null,
          steps: []
        }
      ],
      warnings: [
        "Manual Matrix draft was created without source document extraction."
      ],
      blockers: []
    },
    status: "draft"
  };
}
