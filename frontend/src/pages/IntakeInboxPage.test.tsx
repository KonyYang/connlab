import { useState } from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import {
  ApiRequestError,
  completeNewProject,
  getIntakeCaseReview,
  getIntakePrecheckLookupOptions,
  getNewProjectCompletionOptions,
  previewSpecifiedLtrWorkbookAuthority,
  type IntakeCaseReview,
  type IntakeCaseReviewItem,
  type IntakePackageImport,
  type LocalLtrDuplicateConflictDetail
} from "../api/client";
import {
  EMPTY_INTAKE_SESSION,
  type IntakeSessionState
} from "../features/intake/intakeSession";
import { IntakeInboxPage } from "./IntakeInboxPage";

vi.mock("../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../api/client")>();
  return {
    ...actual,
    completeNewProject: vi.fn(),
    getIntakeCaseReview: vi.fn(),
    getIntakePrecheckLookupOptions: vi.fn(),
    getNewProjectCompletionOptions: vi.fn(),
    previewSpecifiedLtrWorkbookAuthority: vi.fn(),
    updateIntakeCaseReviewFields: vi.fn()
  };
});

describe("IntakeInboxPage local LTR duplicate cancel recovery", () => {
  const locationAssign = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    locationAssign.mockReset();
    vi.stubGlobal("location", {
      ...window.location,
      assign: locationAssign
    });
    vi.mocked(getIntakePrecheckLookupOptions).mockResolvedValue({
      business_unit: [],
      manufacturing_site: [],
      results_format: [],
      test_type: [],
      sample_status: [],
      project_type: [],
      post_testing_disposition: []
    });
    vi.mocked(getNewProjectCompletionOptions).mockResolvedValue({
      location_options: [],
      test_type_in_sheet_options: ["Qualification"],
      default_project_leader: "Lab User"
    });
    vi.mocked(getIntakeCaseReview).mockResolvedValue(reviewWithCase);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("restores the imported case and apply readiness when local duplicate cancel closes the conflict", async () => {
    const user = userEvent.setup();
    vi.mocked(completeNewProject).mockRejectedValueOnce(
      new ApiRequestError("Local LTR duplicate", 409, duplicateConflict)
    );

    render(<Harness />);

    const applyButton = await screen.findByRole("button", { name: /Apply LTR Number/ });
    await waitFor(() => {
      expect((applyButton as HTMLButtonElement).disabled).toBe(false);
    });

    await user.click(applyButton);

    expect(await screen.findByRole("alertdialog")).toBeTruthy();
    expect(
      screen.getByText("DL-2026-05-777 Existing sample assembly Qualification")
    ).toBeTruthy();

    vi.mocked(getIntakeCaseReview).mockResolvedValueOnce(reviewWithoutCases);
    await user.click(screen.getByRole("button", { name: "Simulate review refresh without cases" }));

    await waitFor(() => {
      expect((screen.getByRole("button", { name: /Apply LTR Number/ }) as HTMLButtonElement).disabled)
        .toBe(true);
    });

    await user.click(screen.getByRole("button", { name: "Cancel" }));

    await waitFor(() => {
      expect(screen.queryByRole("alertdialog")).toBeNull();
    });
    const restoredApplyButton = await screen.findByRole("button", { name: /Apply LTR Number/ });
    expect((restoredApplyButton as HTMLButtonElement).disabled).toBe(false);
    expect(screen.getAllByDisplayValue("Connector sample").length).toBeGreaterThan(0);
    expect(vi.mocked(completeNewProject)).toHaveBeenCalledTimes(1);
  });

  it("opens the existing project without clearing the current intake session", async () => {
    const user = userEvent.setup();
    const onSessionChange = vi.fn();
    vi.mocked(completeNewProject).mockRejectedValueOnce(
      new ApiRequestError("Local LTR duplicate", 409, duplicateConflict)
    );

    render(<Harness onSessionChangeSpy={onSessionChange} />);

    const applyButton = await screen.findByRole("button", { name: /Apply LTR Number/ });
    await waitFor(() => {
      expect((applyButton as HTMLButtonElement).disabled).toBe(false);
    });

    await user.click(applyButton);
    await screen.findByRole("alertdialog");

    vi.mocked(getIntakeCaseReview).mockResolvedValueOnce(reviewWithoutCases);
    await user.click(screen.getByRole("button", { name: "Simulate review refresh without cases" }));

    await waitFor(() => {
      expect((screen.getByRole("button", { name: /Apply LTR Number/ }) as HTMLButtonElement).disabled)
        .toBe(true);
    });

    await user.click(screen.getByRole("button", { name: "Open existing project" }));

    expect(locationAssign).toHaveBeenCalledWith("/projects/project-old");
    expect(onSessionChange).not.toHaveBeenCalledWith(EMPTY_INTAKE_SESSION);
    expect(screen.queryByRole("alertdialog")).toBeNull();
    expect((await screen.findByRole("button", { name: /Apply LTR Number/ }) as HTMLButtonElement).disabled)
      .toBe(false);
    expect(screen.getAllByDisplayValue("Connector sample").length).toBeGreaterThan(0);
  });

  it("previews the workbook row before completing a full specified LTR", async () => {
    const user = userEvent.setup();
    vi.mocked(getIntakeCaseReview).mockResolvedValue(reviewWithSpecifiedCase);
    vi.mocked(previewSpecifiedLtrWorkbookAuthority).mockResolvedValue(workbookPreviewFound);
    vi.mocked(completeNewProject).mockResolvedValue({
      project_id: "project-new",
      project_status: "ltr_registered",
      ltr_number: "DL-2026-05-011",
      workbook_path: "D:/PublicProject/LTR.xlsx",
      workbook_sheet_name: "2026",
      workbook_row_number: 12,
      workbook_backup_path: "D:/PublicProject/backups/LTR.xlsx"
    });

    render(<Harness />);

    const applyButton = await screen.findByRole("button", { name: /Apply LTR Number/ });
    await waitFor(() => {
      expect((applyButton as HTMLButtonElement).disabled).toBe(false);
    });

    await user.click(applyButton);

    await waitFor(() => {
      expect(previewSpecifiedLtrWorkbookAuthority).toHaveBeenCalledWith("case-1", {
        specified_ltr_number: "DL-2026-05-011"
      });
    });
    expect(completeNewProject).not.toHaveBeenCalled();
    const dialog = await screen.findByRole("dialog", { name: "Confirm LTR workbook row" });
    expect(dialog.getAttribute("aria-modal")).toBe("true");
    expect(dialog.closest(".specified-ltr-preview-modal")).toBeTruthy();
    expect(screen.getByText("PwrBlade Ultra Pro")).toBeTruthy();
    await waitFor(() => {
      expect(document.activeElement).toBe(screen.getByRole("button", { name: "Use this LTR number" }));
    });
    expect((screen.getByRole("button", { name: /Apply LTR Number/ }) as HTMLButtonElement).disabled)
      .toBe(true);

    await user.click(screen.getByRole("button", { name: "Use this LTR number" }));

    await waitFor(() => {
      expect(completeNewProject).toHaveBeenCalledWith(
        "case-1",
        expect.objectContaining({
          ltr_mode: "specified",
          specified_ltr_number: "DL-2026-05-011",
          specified_ltr_workbook_preview_ack: workbookPreviewFound.preview_ack
        })
      );
    });
  });

  it("blocks completion when the specified LTR is missing from the workbook", async () => {
    const user = userEvent.setup();
    vi.mocked(getIntakeCaseReview).mockResolvedValue(reviewWithSpecifiedCase);
    vi.mocked(previewSpecifiedLtrWorkbookAuthority).mockResolvedValue(workbookPreviewNotFound);

    render(<Harness />);

    const applyButton = await screen.findByRole("button", { name: /Apply LTR Number/ });
    await waitFor(() => {
      expect((applyButton as HTMLButtonElement).disabled).toBe(false);
    });

    await user.click(applyButton);

    const alertDialog = await screen.findByRole("alertdialog", { name: "Confirm LTR workbook row" });
    expect(alertDialog.getAttribute("aria-modal")).toBe("true");
    expect(alertDialog.closest(".specified-ltr-preview-modal")).toBeTruthy();
    expect(await screen.findByText("LTR workbook 中不存在该编号")).toBeTruthy();
    expect(screen.queryByRole("button", { name: "Use this LTR number" })).toBeNull();
    await waitFor(() => {
      expect(document.activeElement).toBe(screen.getByRole("button", { name: "Close" }));
    });
    expect(completeNewProject).not.toHaveBeenCalled();
    await user.click(screen.getByRole("button", { name: "Close" }));

    await waitFor(() => {
      expect(screen.queryByText("LTR workbook 中不存在该编号")).toBeNull();
    });
    expect((await screen.findByRole("button", { name: /Apply LTR Number/ }) as HTMLButtonElement).disabled)
      .toBe(false);
  });

  it("closes the specified LTR workbook modal with Escape without completing", async () => {
    const user = userEvent.setup();
    vi.mocked(getIntakeCaseReview).mockResolvedValue(reviewWithSpecifiedCase);
    vi.mocked(previewSpecifiedLtrWorkbookAuthority).mockResolvedValue(workbookPreviewFound);

    render(<Harness />);

    const applyButton = await screen.findByRole("button", { name: /Apply LTR Number/ });
    await waitFor(() => {
      expect((applyButton as HTMLButtonElement).disabled).toBe(false);
    });

    await user.click(applyButton);

    const dialog = await screen.findByRole("dialog", { name: "Confirm LTR workbook row" });
    expect(dialog.getAttribute("aria-modal")).toBe("true");

    await user.keyboard("{Escape}");

    await waitFor(() => {
      expect(screen.queryByRole("dialog", { name: "Confirm LTR workbook row" })).toBeNull();
    });
    expect(completeNewProject).not.toHaveBeenCalled();
    expect((await screen.findByRole("button", { name: /Apply LTR Number/ }) as HTMLButtonElement).disabled)
      .toBe(false);
  });

  it("hands off to local duplicate conflict after workbook preview confirmation", async () => {
    const user = userEvent.setup();
    vi.mocked(getIntakeCaseReview).mockResolvedValue(reviewWithSpecifiedCase);
    vi.mocked(previewSpecifiedLtrWorkbookAuthority).mockResolvedValue(workbookPreviewFound);
    vi.mocked(completeNewProject).mockRejectedValueOnce(
      new ApiRequestError("Local LTR duplicate", 409, duplicateConflict)
    );

    render(<Harness />);

    const applyButton = await screen.findByRole("button", { name: /Apply LTR Number/ });
    await waitFor(() => {
      expect((applyButton as HTMLButtonElement).disabled).toBe(false);
    });

    await user.click(applyButton);
    await screen.findByText("Confirm LTR workbook row");
    await user.click(screen.getByRole("button", { name: "Use this LTR number" }));

    expect(await screen.findByRole("alertdialog")).toBeTruthy();
    expect(screen.queryByText("Confirm LTR workbook row")).toBeNull();
    expect(screen.getByText("DL-2026-05-777 Existing sample assembly Qualification"))
      .toBeTruthy();
  });
});

function Harness({
  onSessionChangeSpy
}: {
  onSessionChangeSpy?: (session: IntakeSessionState) => void;
}) {
  const [session, setSession] = useState<IntakeSessionState>(loadedSession);
  const handleSessionChange = (nextSession: IntakeSessionState) => {
    onSessionChangeSpy?.(nextSession);
    setSession(nextSession);
  };
  return (
    <>
      <button
        type="button"
        onClick={() =>
          setSession((current) => ({
            ...current,
            selectedPrecheckCaseId: "missing-case"
          }))
        }
      >
        Simulate review refresh without cases
      </button>
      <IntakeInboxPage
        session={session}
        onExit={vi.fn()}
        onProjectCreated={vi.fn()}
        onSessionChange={handleSessionChange}
      />
    </>
  );
}

const packageImport: IntakePackageImport = {
  package_id: "package-1",
  source_type: "msg",
  package_status: "reviewed",
  source_original_name: "request.msg",
  subject: "Connector qualification",
  sender_name: "Lab Requester",
  sender_email: "requester@example.test",
  received_at: "2026-07-03T01:00:00Z",
  asset_count: 1,
  candidate_count: 1,
  next_action: "review",
  assets: [
    {
      asset_id: "asset-1",
      original_name: "request.docx",
      extension: ".docx",
      mime_type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      size_bytes: 128,
      asset_role: "application_form",
      candidate_score: 1
    }
  ]
};

const loadedSession: IntakeSessionState = {
  packageImport,
  selectedAssetId: "asset-1",
  selectedWordAssetId: "asset-1",
  selectedPrecheckCaseId: "case-1",
  sourceMode: "msg",
  directWordName: null
};

const activeCase: IntakeCaseReviewItem = {
  case_id: "case-1",
  status: "ready",
  selected_form_asset_id: "asset-1",
  selected_asset_name: "request.docx",
  confirmed_project_id: null,
  operator_notes: null,
  missing_required_fields: [],
  confirm_allowed: true,
  fields: [
    field("requester", "Requested By", "Bob"),
    field("phone", "Phone #", "123456"),
    field("request_date", "Date", "2026-07-03"),
    field("email", "Email", "bob@example.test"),
    field("business_unit", "Business Unit", "BU"),
    field("manufacturing_site", "Mfg. Site", "DG"),
    field("results_format", "Results Format", "Report"),
    field("requested_completion_date", "Requested Completion Date", "2026-07-30"),
    field("test_type", "Test Type", "Qualification"),
    field("sample_status", "Test Sample Status", "New"),
    field("project_type", "Project Type", "Qualification"),
    field("post_testing_disposition", "Post-Testing Sample Disposition", "Return"),
    field("send_copies_recipients", "Send copies of test results/reports to", "Bob"),
    field("confidential", "Confidential", "No"),
    field("subcontract", "Subcontract", "No")
  ],
  sample_rows: [
    {
      product_name: "Connector sample",
      part_number: "PN-1",
      lot_or_traceability: "LOT-1",
      material: "Copper",
      plating: "Tin",
      lubricant: "",
      housing_material: "Plastic",
      quantity: "5"
    }
  ],
  requested_testing_rows: [
    {
      test_to_be_performed: "Qualification testing",
      applicable_specification: "EIA-364"
    }
  ],
  project_setup: {
    ltr_mode: "auto",
    test_item: "Qualification",
    sample_description: "Connector sample",
    test_type_in_sheet: "Qualification",
    project_leader: "Lab User",
    lab_performing_tests: "Dongguan"
  },
  precheck_issues: []
};

const reviewWithCase: IntakeCaseReview = {
  package_id: "package-1",
  source_type: "msg",
  package_status: "reviewed",
  source_original_name: "request.msg",
  subject: "Connector qualification",
  sender_name: "Lab Requester",
  sender_email: "requester@example.test",
  cases: [activeCase]
};

const reviewWithSpecifiedCase: IntakeCaseReview = {
  ...reviewWithCase,
  cases: [
    {
      ...activeCase,
      project_setup: {
        ...activeCase.project_setup,
        ltr_mode: "specified",
        specified_ltr_number: "DL-2026-05-011"
      }
    }
  ]
};

const reviewWithoutCases: IntakeCaseReview = {
  ...reviewWithCase,
  cases: []
};

const duplicateConflict: LocalLtrDuplicateConflictDetail = {
  code: "LOCAL_LTR_DUPLICATE",
  message: "This LTR number already has a local ConnLab owner.",
  ltr_number: "DL-2026-05-777",
  existing: {
    ltr_id: "ltr-old",
    project_id: "project-old",
    display_project_id: "DL-2026-05-777",
    project_name: "Existing project",
    product_name: "Existing Connector",
    sample_description: "Existing sample assembly",
    test_item: "Qualification",
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
    expires_at: "2026-07-03T12:00:00Z",
    allowed_actions: ["open_existing", "cancel", "replace_local_association"],
    requires_second_confirmation: true
  }
};

const workbookPreviewFound = {
  status: "found" as const,
  ltr_number: "DL-2026-05-011",
  message: "LTR workbook row found.",
  workbook_path: "D:/PublicProject/LTR.xlsx",
  sheet_name: "2026",
  row_number: 12,
  row_values: [
    {
      field_name: "project_type",
      label: "Project Type",
      value: "Qualification",
      is_blank: false
    },
    {
      field_name: "description_pn",
      label: "Description P/N",
      value: "PwrBlade Ultra Pro",
      is_blank: false
    }
  ],
  preview_ack: {
    acknowledged: true,
    ltr_number: "DL-2026-05-011",
    sheet_name: "2026",
    row_number: 12,
    preview_token: "preview-token",
    row_fingerprint: "row-fingerprint"
  },
  blockers: [],
  warnings: []
};

const workbookPreviewNotFound = {
  status: "not_found" as const,
  ltr_number: "DL-2026-05-011",
  message: "LTR workbook 中不存在该编号",
  workbook_path: "D:/PublicProject/LTR.xlsx",
  sheet_name: "2026",
  row_number: null,
  row_values: [],
  preview_ack: null,
  blockers: [],
  warnings: []
};

function field(key: string, label: string, value: string) {
  return {
    key,
    label,
    value,
    required: true,
    missing: false
  };
}
