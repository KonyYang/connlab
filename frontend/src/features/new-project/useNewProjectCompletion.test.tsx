import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import {
  ApiRequestError,
  completeNewProject,
  type CompleteNewProject,
  type IntakeCaseReviewItem,
  type LocalLtrDuplicateConflictDetail
} from "../../api/client";
import {
  useNewProjectCompletion
} from "./useNewProjectCompletion";
import type { NewProjectSetupConfirmationValues } from "./NewProjectSetupConfirmationPanel";

vi.mock("../../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../../api/client")>();
  return {
    ...actual,
    completeNewProject: vi.fn()
  };
});

describe("useNewProjectCompletion duplicate confirmation busy lock", () => {
  it("keeps completionLoading true while duplicate confirmation is in flight", async () => {
    const completeNewProjectMock = vi.mocked(completeNewProject);
    let resolveConfirmation: (value: CompleteNewProject) => void = () => {};
    completeNewProjectMock
      .mockRejectedValueOnce(
        new ApiRequestError("Local LTR duplicate", 409, conflict)
      )
      .mockImplementationOnce(
        () =>
          new Promise<CompleteNewProject>((resolve) => {
            resolveConfirmation = resolve;
          })
      );
    const onCompleted = vi.fn();
    const { result } = renderHook(() =>
      useNewProjectCompletion({
        activeCase,
        resetKey: "case-1",
        setupValues,
        onCompleted
      })
    );

    await act(async () => {
      await result.current.complete();
    });

    expect(result.current.localDuplicateConflict).toEqual(conflict);
    expect(result.current.completionLoading).toBe(false);

    let confirmationPromise: Promise<void> | undefined;
    await act(async () => {
      confirmationPromise = result.current.confirmDuplicateResolution({
        action: "replace_local_association",
        token: "token-1",
        acknowledged: true,
        reason: "Confirmed by lab coordinator"
      });
    });

    await waitFor(() => {
      expect(result.current.duplicateConfirming).toBe(true);
      expect(result.current.completionLoading).toBe(true);
    });

    await act(async () => {
      resolveConfirmation({
        project_id: "project-new",
        project_status: "ltr_registered",
        ltr_number: "DL-2026-05-777"
      });
      await confirmationPromise;
    });

    expect(result.current.duplicateConfirming).toBe(false);
    expect(result.current.completionLoading).toBe(false);
    expect(onCompleted).toHaveBeenCalledWith("project-new");
  });

  it("uses the duplicate conflict case id when the active case is unavailable", async () => {
    const completeNewProjectMock = vi.mocked(completeNewProject);
    completeNewProjectMock
      .mockRejectedValueOnce(
        new ApiRequestError("Local LTR duplicate", 409, conflict)
      )
      .mockResolvedValueOnce({
        project_id: "project-new",
        project_status: "ltr_registered",
        ltr_number: "DL-2026-05-777"
      });
    const onCompleted = vi.fn();
    const { result, rerender } = renderHook(
      ({ currentActiveCase }: { currentActiveCase: IntakeCaseReviewItem | null }) =>
        useNewProjectCompletion({
          activeCase: currentActiveCase,
          resetKey: "case-1",
          setupValues,
          onCompleted
        }),
      { initialProps: { currentActiveCase: activeCase as IntakeCaseReviewItem | null } }
    );

    await act(async () => {
      await result.current.complete();
    });

    expect(result.current.localDuplicateConflict).toEqual(conflict);

    rerender({ currentActiveCase: null });

    await act(async () => {
      await result.current.confirmDuplicateResolution({
        action: "replace_local_association",
        token: "token-1",
        acknowledged: true,
        reason: "Confirmed after reopening the intake draft"
      });
    });

    expect(completeNewProject).toHaveBeenLastCalledWith(
      "case-1",
      expect.objectContaining({
        duplicate_resolution: expect.objectContaining({
          action: "replace_local_association",
          reason: "Confirmed after reopening the intake draft"
        })
      })
    );
    expect(onCompleted).toHaveBeenCalledWith("project-new");
  });
});

const activeCase: IntakeCaseReviewItem = {
  case_id: "case-1",
  status: "ready",
  selected_form_asset_id: "asset-1",
  selected_asset_name: "request.docx",
  confirmed_project_id: null,
  operator_notes: null,
  missing_required_fields: [],
  confirm_allowed: true,
  fields: [],
  sample_rows: [],
  requested_testing_rows: [],
  project_setup: {},
  precheck_issues: []
};

const setupValues: NewProjectSetupConfirmationValues = {
  ltrMode: "auto",
  specifiedLtrNumber: "",
  testItem: "Qualification",
  sampleDescription: "Connector",
  testTypeInSheet: "Qualification",
  projectLeader: "Lab User",
  labPerformingTests: "Dongguan"
};

const conflict: LocalLtrDuplicateConflictDetail = {
  code: "LOCAL_LTR_DUPLICATE",
  message: "This LTR number already has a local ConnLab owner.",
  ltr_number: "DL-2026-05-777",
  existing: {
    ltr_id: "ltr-old",
    project_id: "project-old",
    display_project_id: "DL-2026-05-777",
    project_name: "Existing project",
    product_name: "Existing Connector",
    requester: "Alice",
    registered_on: "2026-05-07",
    project_status: "ltr_registered",
    lifecycle_state: "active",
    has_local_folder: true,
    has_matrix: false,
    has_outputs: false
  },
  current: {
    case_id: "case-1",
    project_id: "project-new",
    project_name: "Current project",
    requester: "Bob"
  },
  resolution: {
    token: "token-1",
    expires_at: "2026-07-02T12:00:00Z",
    allowed_actions: ["open_existing", "cancel", "replace_local_association"],
    requires_second_confirmation: true
  }
};
