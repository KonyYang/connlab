import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type {
  ProjectBasicInformationResponse,
  ProjectLifecycleResponse,
} from "../../api/client";
import { ProjectBasicInformationWorkspace } from "./ProjectBasicInformationWorkspace";

const api = vi.hoisted(() => ({
  getProject: vi.fn(),
  getProjectBasicInformation: vi.fn(),
  getProjectLifecycle: vi.fn(),
  getNewProjectCompletionOptions: vi.fn(),
  isProjectLifecycleReadonlyErrorDetail: vi.fn((detail: unknown) => {
    return (
      Boolean(detail) &&
      typeof detail === "object" &&
      (detail as { code?: unknown }).code === "project_lifecycle_readonly"
    );
  }),
  listProjectLtrs: vi.fn(),
  saveProjectBasicInformationDraft: vi.fn(),
  confirmProjectBasicInformation: vi.fn(),
}));

vi.mock("../../api/client", () => api);

describe("ProjectBasicInformationWorkspace", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    api.getProject.mockResolvedValue(project());
    api.getProjectLifecycle.mockResolvedValue(lifecycleResponse());
    api.getNewProjectCompletionOptions.mockResolvedValue(completionOptions());
    api.listProjectLtrs.mockResolvedValue([{ ltr_number: "DL-2026-05-011" }]);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("loads draft values, auto-saves edits, and keeps DL number in confirm payload", async () => {
    const user = userEvent.setup();
    const onBackToWorkbench = vi.fn();
    api.getProjectBasicInformation.mockResolvedValue(response());
    api.saveProjectBasicInformationDraft.mockResolvedValue(
      response({ project_leader: "Even Yang" })
    );
    api.confirmProjectBasicInformation.mockResolvedValue(
      response({ project_leader: "Even Yang" }, "confirmed")
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={onBackToWorkbench}
      />
    );

    expect(await screen.findByText("DL-2026-05-011")).toBeTruthy();
    expect(screen.queryByText("DL/LTR Number *")).toBeNull();
    expect(screen.queryByText("Project Type *")).toBeNull();
    expect(screen.getByText("Product Description *")).toBeTruthy();
    expect(screen.getByText("Test Item *")).toBeTruthy();
    expect(screen.getByText("Applicable Specifications *")).toBeTruthy();
    expect(screen.getByText("Lab Received Samples *")).toBeTruthy();
    expect(screen.getByText("Estimated Completion *")).toBeTruthy();
    expect(screen.getByDisplayValue("2026-06-20")).toHaveProperty("type", "date");
    const projectTypeSelect = screen.getByLabelText("Project Type");
    expect(projectTypeSelect.tagName).toBe("SELECT");
    expect(
      Array.from(projectTypeSelect.querySelectorAll("option")).map(
        (option) => option.value
      )
    ).toEqual([
      "New Product Development",
      "Product Extension",
      "Innovation",
      "Lab Activities (Lab Use Only)",
      "Operational Support",
      "Cost Reduction",
    ]);
    const testTypeSelect = screen.getByLabelText("Test Type");
    expect(testTypeSelect.tagName).toBe("SELECT");
    expect(
      Array.from(testTypeSelect.querySelectorAll("option")).map(
        (option) => option.value
      )
    ).toEqual([
      "Product/Process Development",
      "Product/Process Qualification",
      "Lab/Failure Analysis",
      "Customer Specific Testing",
    ]);
    const locationSelect = screen.getByLabelText("Mfg. Site");
    expect(locationSelect.tagName).toBe("SELECT");
    expect(
      Array.from(locationSelect.querySelectorAll("option")).map(
        (option) => option.value
      )
    ).toEqual(expect.arrayContaining(["ARFOB", "ASAA", "ASCA", "Dongguan"]));
    const businessUnitSelect = screen.getByLabelText("Business Unit");
    expect(businessUnitSelect.tagName).toBe("SELECT");
    expect(
      Array.from(businessUnitSelect.querySelectorAll("option")).map(
        (option) => option.value
      )
    ).toEqual(expect.arrayContaining(["AAPG", "Power Solutions", "Valley Green"]));
    expect(screen.getByDisplayValue("1252502")).toBeTruthy();
    const resultsFormatSelect = screen.getByLabelText("Results Format");
    expect(resultsFormatSelect.tagName).toBe("SELECT");
    expect(
      Array.from(resultsFormatSelect.querySelectorAll("option")).map(
        (option) => option.value
      )
    ).toEqual(
      expect.arrayContaining([
        "Data and Observations",
        "Formal Report (Internal)",
        "Formal Report (Customer)",
      ])
    );
    expect(screen.getByLabelText("Requested Completion Date")).toHaveProperty(
      "value",
      "2026-07-02"
    );
    expect(screen.getByLabelText("Requested Completion Date")).toHaveProperty(
      "type",
      "date"
    );
    expect(screen.getByLabelText("Test Sample Status").tagName).toBe("SELECT");
    const postTestingDispositionSelect = screen.getByLabelText(
      "Post-Testing Sample Disposition"
    );
    expect(postTestingDispositionSelect.tagName).toBe("SELECT");
    expect(
      Array.from(postTestingDispositionSelect.querySelectorAll("option")).map(
        (option) => option.value
      )
    ).toEqual(["Send Back to Requestor", "Scrap", "Keep in the Lab"]);
    const testResultSelect = screen.getByLabelText("Test Result");
    expect(testResultSelect.tagName).toBe("SELECT");
    expect(
      Array.from(testResultSelect.querySelectorAll("option")).map(
        (option) => option.value
      )
    ).toEqual(["OK", "Ref", "NG", "In progress", "In-waiting"]);
    const testTypeInSheetSelect = screen.getByLabelText("Test Type in sheet");
    expect(testTypeInSheetSelect.tagName).toBe("SELECT");
    expect(
      Array.from(testTypeInSheetSelect.querySelectorAll("option")).map(
        (option) => option.value
      )
    ).toEqual(["Qualification", "Partial Qualification", "Reliability"]);
    const labPerformingSelect = screen.getByLabelText("Lab Performing");
    expect(labPerformingSelect.tagName).toBe("SELECT");
    expect(
      Array.from(labPerformingSelect.querySelectorAll("option")).map(
        (option) => option.value
      )
    ).toEqual(["Dongguan", "Valley Green"]);
    expect(labPerformingSelect).toHaveProperty("value", "Dongguan");
    const sampleConditionSelect = screen.getByLabelText("Condition of Samples");
    expect(sampleConditionSelect.tagName).toBe("SELECT");
    expect(
      Array.from(sampleConditionSelect.querySelectorAll("option")).map(
        (option) => option.value
      )
    ).toEqual(["Acceptable", "Not Acceptable"]);
    expect(sampleConditionSelect).toHaveProperty("value", "Acceptable");
    expect(
      screen.getByDisplayValue("Peter.Hu@fci.com/Yi-Peng.Wu@fci.com")
    ).toBeTruthy();
    const subContractGroup = screen.getByRole("group", { name: "Sub-contract" });
    expect(within(subContractGroup).getByRole("radio", { name: "No" })).toHaveProperty(
      "checked",
      true
    );
    expect(within(subContractGroup).getByRole("radio", { name: "Yes" })).toHaveProperty(
      "checked",
      false
    );
    const confidentialGroup = screen.getByRole("group", {
      name: "Confidential test or samples",
    });
    expect(within(confidentialGroup).getByRole("radio", { name: "Yes" })).toHaveProperty(
      "checked",
      true
    );
    expect(screen.queryByRole("button", { name: "Save Draft" })).toBeNull();
    expect(screen.queryByText(/Draft saves automatically/)).toBeNull();
    await user.selectOptions(projectTypeSelect, "Product Extension");
    await user.selectOptions(testTypeSelect, "Customer Specific Testing");
    await user.selectOptions(locationSelect, "Nantong");
    await user.selectOptions(labPerformingSelect, "Valley Green");
    await user.click(within(subContractGroup).getByRole("radio", { name: "Yes" }));
    await user.clear(screen.getByLabelText("Project Leader"));
    await user.type(screen.getByLabelText("Project Leader"), "Even Yang");

    await waitFor(() =>
      expect(api.saveProjectBasicInformationDraft).toHaveBeenCalledWith("P1", {
        ...response().draft.values,
        project_type: "Product Extension",
        test_type: "Customer Specific Testing",
        location: "Nantong",
        lab_performing_tests: "Valley Green",
        condition_of_samples_when_received: "Acceptable",
        finish_test_date: "2026-07-02",
        report_date: "2026-07-02",
        sub_contract: "Yes",
        project_leader: "Even Yang",
      })
    );
    expect(screen.queryByText("Draft saved automatically.")).toBeNull();
    expect(screen.queryByRole("status")).toBeNull();

    await user.click(screen.getByRole("button", { name: "Confirm" }));

    await waitFor(() =>
      expect(api.confirmProjectBasicInformation).toHaveBeenCalledWith(
        "P1",
        {
          ...response().draft.values,
          project_type: "Product Extension",
          test_type: "Customer Specific Testing",
          location: "Nantong",
          lab_performing_tests: "Valley Green",
          condition_of_samples_when_received: "Acceptable",
          finish_test_date: "2026-07-02",
          report_date: "2026-07-02",
          sub_contract: "Yes",
          project_leader: "Even Yang",
        },
        "Lab User"
      )
    );
    expect(onBackToWorkbench).toHaveBeenCalledWith({ refreshBasicInformation: true });
  });

  it("defaults legacy Lab Performing values to Dongguan", async () => {
    api.getProjectBasicInformation.mockResolvedValue(
      response({ lab_performing_tests: "ConnLab" })
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    const labPerformingSelect = await screen.findByLabelText("Lab Performing");
    expect(
      Array.from(labPerformingSelect.querySelectorAll("option")).map(
        (option) => option.value
      )
    ).toEqual(["Dongguan", "Valley Green"]);
    expect(labPerformingSelect).toHaveProperty("value", "Dongguan");
  });

  it("defaults legacy sample condition placeholders to Acceptable", async () => {
    api.getProjectBasicInformation.mockResolvedValue(
      response({ condition_of_samples_when_received: "Choose an item." })
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    const sampleConditionSelect = await screen.findByLabelText("Condition of Samples");
    expect(
      Array.from(sampleConditionSelect.querySelectorAll("option")).map(
        (option) => option.value
      )
    ).toEqual(["Acceptable", "Not Acceptable"]);
    expect(sampleConditionSelect).toHaveProperty("value", "Acceptable");
  });

  it("defaults missing Confidential test or samples source values to No", async () => {
    api.getProjectBasicInformation.mockResolvedValue(response({ confidential: "" }));

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    const confidentialGroup = await screen.findByRole("group", {
      name: "Confidential test or samples",
    });
    expect(
      within(confidentialGroup).getByRole("radio", { name: "No" })
    ).toHaveProperty("checked", true);
    expect(
      within(confidentialGroup).getByRole("radio", { name: "Yes" })
    ).toHaveProperty("checked", false);
  });

  it("defaults missing Sub-contract source values to No", async () => {
    api.getProjectBasicInformation.mockResolvedValue(response({ sub_contract: "" }));

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    const subContractGroup = await screen.findByRole("group", {
      name: "Sub-contract",
    });
    expect(
      within(subContractGroup).getByRole("radio", { name: "No" })
    ).toHaveProperty("checked", true);
    expect(
      within(subContractGroup).getByRole("radio", { name: "Yes" })
    ).toHaveProperty("checked", false);
  });

  it("defaults Finish Test Date and Report Date to Estimated Completion", async () => {
    api.getProjectBasicInformation.mockResolvedValue(
      response({ finish_test_date: "", report_date: "" })
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    expect(await screen.findByLabelText("Estimated Completion")).toHaveProperty(
      "value",
      "2026-07-02"
    );
    expect(screen.getByLabelText("Finish Test Date")).toHaveProperty(
      "value",
      "2026-07-02"
    );
    expect(screen.getByLabelText("Report Date")).toHaveProperty(
      "value",
      "2026-07-02"
    );
  });

  it("disables confirm while an automatic draft save is pending", async () => {
    const user = userEvent.setup();
    api.getProjectBasicInformation.mockResolvedValue(response());
    api.saveProjectBasicInformationDraft.mockReturnValue(new Promise(() => {}));

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    await screen.findByText("DL-2026-05-011");
    await user.clear(screen.getByLabelText("Project Leader"));
    await user.type(screen.getByLabelText("Project Leader"), "Even Yang");

    await waitFor(() =>
      expect(screen.getByRole("button", { name: "Confirm" })).toHaveProperty(
        "disabled",
        true
      )
    );
  });

  it("returns to Workbench on Cancel without saving or confirming", async () => {
    const user = userEvent.setup();
    const onBackToWorkbench = vi.fn();
    api.getProjectBasicInformation.mockResolvedValue(response());

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={onBackToWorkbench}
      />
    );

    await screen.findByText("DL-2026-05-011");
    await user.click(screen.getByRole("button", { name: "Cancel" }));

    expect(api.saveProjectBasicInformationDraft).not.toHaveBeenCalled();
    expect(api.confirmProjectBasicInformation).not.toHaveBeenCalled();
    expect(onBackToWorkbench).toHaveBeenCalledWith({ refreshBasicInformation: false });
  });

  it("highlights missing required fields and blocks confirm while keeping source review hints", async () => {
    api.getProjectBasicInformation.mockResolvedValue(
      response(
        { project_leader: "" },
        "needs_review",
        ["Project Leader"],
        ["requested_by"]
      )
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    const projectLeaderInput = await screen.findByLabelText("Project Leader");
    expect(screen.queryByText("Missing required fields")).toBeNull();
    expect(
      projectLeaderInput
        .closest(".basic-information-field")
        ?.classList.contains("is-missing-required")
    ).toBe(true);
    expect(screen.getByText("Source review")).toBeTruthy();
    expect(screen.getByText("Requested by changed in source material.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Confirm" })).toHaveProperty(
      "disabled",
      true
    );
  });

  it("treats Applicable Specifications as a required blocking field", async () => {
    api.getProjectBasicInformation.mockResolvedValue(
      response({ applicable_specifications: "" })
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    const applicableSpecificationsInput = await screen.findByLabelText(
      "Applicable Specifications"
    );
    expect(screen.getByText("Applicable Specifications *")).toBeTruthy();
    expect(
      applicableSpecificationsInput
        .closest(".basic-information-field")
        ?.classList.contains("is-missing-required")
    ).toBe(true);
    expect(screen.getByRole("button", { name: "Confirm" })).toHaveProperty(
      "disabled",
      true
    );
  });

  it("treats Product Description as a required blocking field", async () => {
    api.getProjectBasicInformation.mockResolvedValue(
      response({ product_description: "" })
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    const productDescriptionInput = await screen.findByLabelText(
      "Product Description"
    );
    expect(screen.getByText("Product Description *")).toBeTruthy();
    expect(
      productDescriptionInput
        .closest(".basic-information-field")
        ?.classList.contains("is-missing-required")
    ).toBe(true);
    expect(screen.getByRole("button", { name: "Confirm" })).toHaveProperty(
      "disabled",
      true
    );
  });

  it("treats Requested Completion Date as a required blocking field", async () => {
    api.getProjectBasicInformation.mockResolvedValue(
      response({ requested_completion_date: "" })
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    const requestedCompletionDateInput = await screen.findByLabelText(
      "Requested Completion Date"
    );
    expect(screen.getByText("Requested Completion Date *")).toBeTruthy();
    expect(
      requestedCompletionDateInput
        .closest(".basic-information-field")
        ?.classList.contains("is-missing-required")
    ).toBe(true);
    expect(screen.getByRole("button", { name: "Confirm" })).toHaveProperty(
      "disabled",
      true
    );
  });

  it("highlights invalid laboratory date sequence fields and blocks confirm", async () => {
    api.getProjectBasicInformation.mockResolvedValue(
      response({
        date_lab_received_samples: "2026-06-20",
        start_test_date: "2026-06-19",
        requested_completion_date: "2026-06-18",
        estimated_completion_date: "2026-06-18",
        finish_test_date: "2026-06-18",
        report_date: "2026-06-17",
      })
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    const invalidDateLabels = [
      "Lab Received Samples",
      "Start Test Date",
      "Requested Completion Date",
      "Estimated Completion",
      "Finish Test Date",
      "Report Date",
    ];
    for (const label of invalidDateLabels) {
      const field = await screen.findByLabelText(label);
      expect(
        field
          .closest(".basic-information-field")
        ?.classList.contains("is-invalid-sequence")
      ).toBe(true);
    }
    const dateChecks = screen.getByRole("status", { name: "Date validation" });
    expect(dateChecks.textContent).toContain(
      "Lab Received Samples must not be later than Start Test Date."
    );
    expect(dateChecks.textContent).toContain(
      "Start Test Date must not be later than Requested Completion Date."
    );
    expect(dateChecks.textContent).toContain(
      "Finish Test Date must not be earlier than Start Test Date."
    );
    expect(dateChecks.textContent).toContain(
      "Finish Test Date must not be later than Report Date."
    );
    expect(screen.getByRole("button", { name: "Confirm" })).toHaveProperty(
      "disabled",
      true
    );
  });

  it("blocks empty required dates while optional empty dates only warn", async () => {
    api.getProjectBasicInformation.mockResolvedValue(
      response({
        date_lab_received_samples: "",
        estimated_completion_date: "",
        start_test_date: "",
        finish_test_date: "",
        report_date: "",
      })
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    const requiredDate = await screen.findByLabelText("Lab Received Samples");
    const requiredEstimatedDate = await screen.findByLabelText(
      "Estimated Completion"
    );
    expect(screen.getByText("Lab Received Samples *")).toBeTruthy();
    expect(screen.getByText("Estimated Completion *")).toBeTruthy();
    expect(
      requiredDate
        .closest(".basic-information-field")
        ?.classList.contains("is-missing-required")
    ).toBe(true);
    expect(
      requiredEstimatedDate
        .closest(".basic-information-field")
        ?.classList.contains("is-missing-required")
    ).toBe(true);
    expect(
      requiredDate
        .closest(".basic-information-field")
        ?.classList.contains("is-missing-date")
    ).toBe(true);
    expect(
      requiredEstimatedDate
        .closest(".basic-information-field")
        ?.classList.contains("is-missing-date")
    ).toBe(true);
    const missingDateLabels = [
      "Start Test Date",
      "Finish Test Date",
      "Report Date",
    ];
    for (const label of missingDateLabels) {
      const field = await screen.findByLabelText(label);
      expect(
        field
          .closest(".basic-information-field")
          ?.classList.contains("is-missing-date")
      ).toBe(true);
      expect(
        field
          .closest(".basic-information-field")
          ?.classList.contains("is-invalid-sequence")
      ).toBe(false);
    }
    expect(screen.queryByRole("status", { name: "Date validation" })).toBeNull();
    expect(screen.getByRole("button", { name: "Confirm" })).toHaveProperty(
      "disabled",
      true
    );
  });

  it("splits Basic Information into product/request and laboratory execution panels", async () => {
    api.getProjectBasicInformation.mockResolvedValue(response());

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    const productPanel = await screen.findByRole("region", {
      name: "Product and request",
    });
    const laboratoryPanel = screen.getByRole("region", {
      name: "Laboratory execution",
    });

    expect(document.querySelector(".basic-information-header")).toBeNull();
    expect(
      screen.queryByRole("heading", { name: "Product and request" })
    ).toBeNull();
    expect(
      screen.queryByRole("heading", { name: "Laboratory execution" })
    ).toBeNull();
    expect(
      screen.queryByText(
        "Application-form source values for product scope and requester details."
      )
    ).toBeNull();
    expect(
      screen.queryByText(
        "Lab ownership, result/commercial status, and schedule dates."
      )
    ).toBeNull();
    const ltrCard = screen.getByRole("region", { name: "LTR information" });
    const identity = ltrCard.querySelector(".basic-information-panel-identity");
    expect(identity?.tagName).toBe("SPAN");
    expect(identity?.textContent).toBe("DL-2026-05-011");
    expect(productPanel.querySelector(".basic-information-panel-identity")).toBeNull();
    expect(
      within(ltrCard).queryByRole("button", { name: "Update LTR" })
    ).toBeNull();
    const productDescriptionField = screen
      .getByLabelText("Product Description")
      .closest(".basic-information-field");
    const testItemField = screen
      .getByLabelText("Test Item")
      .closest(".basic-information-field");
    const applicableSpecificationsField = screen
      .getByLabelText("Applicable Specifications")
      .closest(".basic-information-field");
    const descriptionPnField = screen
      .getByLabelText("Description P/N")
      .closest(".basic-information-field");
    const projectTypeField = screen
      .getByLabelText("Project Type")
      .closest(".basic-information-field");
    const testTypeField = screen
      .getByLabelText("Test Type")
      .closest(".basic-information-field");
    const subContractField = screen
      .getByRole("group", { name: "Sub-contract" })
      .closest(".basic-information-field");
    const requestedByField = screen
      .getByLabelText("Requested by")
      .closest(".basic-information-field");
    const phoneField = screen.getByLabelText("Phone").closest(".basic-information-field");
    const requestorEmailField = screen
      .getByLabelText("E-mail of Requestor")
      .closest(".basic-information-field");
    const locationField = screen
      .getByLabelText("Mfg. Site")
      .closest(".basic-information-field");
    const sendCopiesField = screen
      .getByLabelText("Send copies of test results/reports to")
      .closest(".basic-information-field");
    const confidentialField = screen
      .getByRole("group", { name: "Confidential test or samples" })
      .closest(".basic-information-field");
    const projectLeaderField = screen
      .getByLabelText("Project Leader")
      .closest(".basic-information-field");
    const labPerformingField = screen
      .getByLabelText("Lab Performing")
      .closest(".basic-information-field");
    const testResultField = screen
      .getByLabelText("Test Result")
      .closest(".basic-information-field");
    const dateLabReceivedSamplesField = screen
      .getByLabelText("Lab Received Samples")
      .closest(".basic-information-field");
    const estimatedCompletionDateField = screen
      .getByLabelText("Estimated Completion")
      .closest(".basic-information-field");
    const testFeeField = screen
      .getByLabelText("Test Fee")
      .closest(".basic-information-field");
    const startTestDateField = screen
      .getByLabelText("Start Test Date")
      .closest(".basic-information-field");
    const finishTestDateField = screen
      .getByLabelText("Finish Test Date")
      .closest(".basic-information-field");
    const reportDateField = screen
      .getByLabelText("Report Date")
      .closest(".basic-information-field");
    const remarksPoField = screen
      .getByLabelText("Remarks (PO)")
      .closest(".basic-information-field");
    const failedItemField = screen
      .getByLabelText("Failed item")
      .closest(".basic-information-field");
    const testTypeInSheetField = screen
      .getByLabelText("Test Type in sheet")
      .closest(".basic-information-field");
    const sampleDepositionField = screen
      .getByLabelText("Sample deposition")
      .closest(".basic-information-field");
    const sampleConditionField = screen
      .getByLabelText("Condition of Samples")
      .closest(".basic-information-field");
    const productDescriptionInput = screen.getByLabelText("Product Description");
    const projectLeaderInput = screen.getByLabelText("Project Leader");
    const testFeeInput = screen.getByLabelText("Test Fee");
    const productPanelText = productPanel.textContent ?? "";
    const laboratoryPanelText = laboratoryPanel.textContent ?? "";
    expect(productDescriptionField?.classList.contains("is-compact")).toBe(true);
    expect(testItemField?.classList.contains("is-compact")).toBe(true);
    expect(applicableSpecificationsField?.classList.contains("is-compact")).toBe(
      true
    );
    expect(descriptionPnField?.classList.contains("is-compact")).toBe(true);
    expect(projectTypeField?.classList.contains("is-third")).toBe(true);
    expect(testTypeField?.classList.contains("is-third")).toBe(true);
    expect(subContractField?.classList.contains("is-third")).toBe(true);
    expect(requestedByField?.classList.contains("is-quarter")).toBe(true);
    expect(phoneField?.classList.contains("is-quarter")).toBe(true);
    expect(requestorEmailField?.classList.contains("is-wide-quarter")).toBe(true);
    expect(locationField?.classList.contains("is-narrow-quarter")).toBe(true);
    expect(sendCopiesField?.classList.contains("is-two-thirds")).toBe(true);
    expect(confidentialField?.classList.contains("is-inline-third")).toBe(true);
    expect(projectLeaderField?.classList.contains("is-quarter")).toBe(true);
    expect(labPerformingField?.classList.contains("is-quarter")).toBe(true);
    expect(sampleConditionField?.classList.contains("is-quarter")).toBe(true);
    expect(testResultField?.classList.contains("is-quarter")).toBe(true);
    expect(dateLabReceivedSamplesField?.classList.contains("is-quarter")).toBe(true);
    expect(estimatedCompletionDateField?.classList.contains("is-quarter")).toBe(
      true
    );
    expect(testFeeField?.classList.contains("is-quarter")).toBe(true);
    expect(startTestDateField?.classList.contains("is-quarter")).toBe(true);
    expect(finishTestDateField?.classList.contains("is-quarter")).toBe(true);
    expect(reportDateField?.classList.contains("is-quarter")).toBe(true);
    expect(remarksPoField?.classList.contains("is-quarter")).toBe(true);
    expect(failedItemField?.classList.contains("is-wide-remainder")).toBe(true);
    expect(testTypeInSheetField?.classList.contains("is-narrow-quarter")).toBe(true);
    expect(sampleDepositionField?.classList.contains("is-quarter")).toBe(true);
    expect(productDescriptionInput).toHaveProperty("rows", 1);
    expect(projectLeaderInput.tagName).toBe("TEXTAREA");
    expect(projectLeaderInput).toHaveProperty("rows", 1);
    expect(testFeeInput.tagName).toBe("TEXTAREA");
    expect(testFeeInput).toHaveProperty("rows", 1);
    expect(productPanelText.indexOf("Product Description")).toBeLessThan(
      productPanelText.indexOf("Test Item")
    );
    expect(productPanelText.indexOf("Test Item")).toBeLessThan(
      productPanelText.indexOf("Applicable Specifications")
    );
    expect(productPanelText.indexOf("Applicable Specifications")).toBeLessThan(
      productPanelText.indexOf("Description P/N")
    );
    expect(productPanelText.indexOf("Description P/N")).toBeLessThan(
      productPanelText.indexOf("Project Type")
    );
    expect(productPanelText.indexOf("Project Type")).toBeLessThan(
      productPanelText.indexOf("Test Type")
    );
    expect(productPanelText.indexOf("Test Type")).toBeLessThan(
      productPanelText.indexOf("Sub-contract")
    );
    expect(productPanelText.indexOf("Sub-contract")).toBeLessThan(
      productPanelText.indexOf("Requested by")
    );
    expect(productPanelText.indexOf("Requested by")).toBeLessThan(
      productPanelText.indexOf("E-mail of Requestor")
    );
    expect(productPanelText.indexOf("E-mail of Requestor")).toBeLessThan(
      productPanelText.indexOf("Phone")
    );
    expect(productPanelText.indexOf("Phone")).toBeLessThan(
      productPanelText.indexOf("Mfg. Site")
    );
    expect(productPanelText.indexOf("Mfg. Site")).toBeLessThan(
      productPanelText.indexOf("Results Format")
    );
    expect(productPanelText.indexOf("Results Format")).toBeLessThan(
      productPanelText.indexOf("Business Unit")
    );
    expect(productPanelText.indexOf("Business Unit")).toBeLessThan(
      productPanelText.indexOf("Project #")
    );
    expect(productPanelText.indexOf("Project #")).toBeLessThan(
      productPanelText.indexOf("Requested Completion Date")
    );
    expect(productPanelText.indexOf("Requested Completion Date")).toBeLessThan(
      productPanelText.indexOf("Test Sample Status")
    );
    expect(productPanelText.indexOf("Test Sample Status")).toBeLessThan(
      productPanelText.indexOf("Post-Testing Sample Disposition")
    );
    expect(productPanelText.indexOf("Post-Testing Sample Disposition")).toBeLessThan(
      productPanelText.indexOf("Send copies of test results/reports to")
    );
    expect(
      productPanelText.indexOf("Send copies of test results/reports to")
    ).toBeLessThan(productPanelText.indexOf("Confidential test or samples"));
    expect(laboratoryPanelText.indexOf("Lab Performing")).toBeLessThan(
      laboratoryPanelText.indexOf("Project Leader")
    );
    expect(laboratoryPanelText.indexOf("Project Leader")).toBeLessThan(
      laboratoryPanelText.indexOf("Condition of Samples")
    );
    expect(laboratoryPanelText.indexOf("Condition of Samples")).toBeLessThan(
      laboratoryPanelText.indexOf("Test Result")
    );
    expect(laboratoryPanelText.indexOf("Test Result")).toBeLessThan(
      laboratoryPanelText.indexOf("Lab Received Samples")
    );
    expect(laboratoryPanelText.indexOf("Lab Received Samples")).toBeLessThan(
      laboratoryPanelText.indexOf("Estimated Completion")
    );
    expect(laboratoryPanelText.indexOf("Estimated Completion")).toBeLessThan(
      laboratoryPanelText.indexOf("Sample deposition")
    );
    expect(laboratoryPanelText.indexOf("Sample deposition")).toBeLessThan(
      laboratoryPanelText.indexOf("Test Fee")
    );
    expect(laboratoryPanelText.indexOf("Test Fee")).toBeLessThan(
      laboratoryPanelText.indexOf("Start Test Date")
    );
    expect(laboratoryPanelText.indexOf("Start Test Date")).toBeLessThan(
      laboratoryPanelText.indexOf("Finish Test Date")
    );
    expect(laboratoryPanelText.indexOf("Finish Test Date")).toBeLessThan(
      laboratoryPanelText.indexOf("Report Date")
    );
    expect(laboratoryPanelText.indexOf("Report Date")).toBeLessThan(
      laboratoryPanelText.indexOf("Remarks (PO)")
    );
    expect(laboratoryPanelText.indexOf("Remarks (PO)")).toBeLessThan(
      laboratoryPanelText.indexOf("Failed item")
    );
    expect(laboratoryPanelText.indexOf("Failed item")).toBeLessThan(
      laboratoryPanelText.indexOf("Test Type in sheet")
    );
    expect(
      screen.queryByRole("heading", { name: "Product information" })
    ).toBeNull();
    expect(
      screen.queryByRole("heading", { name: "Requester information" })
    ).toBeNull();
    expect(
      screen.queryByRole("heading", { name: "Application details" })
    ).toBeNull();
    expect(
      screen.queryByRole("heading", { name: "Laboratory ownership" })
    ).toBeNull();
    expect(
      screen.queryByRole("heading", { name: "Result and commercial" })
    ).toBeNull();
    expect(screen.queryByRole("heading", { name: "Schedule" })).toBeNull();
    expect(productPanel.textContent).toContain("Requested by");
    expect(productPanel.textContent).toContain("Sub-contract");
    expect(laboratoryPanel.textContent).toContain("Project Leader");
    expect(laboratoryPanel.textContent).toContain("Test Result");
    expect(laboratoryPanel.textContent).toContain("Test Type in sheet");
    expect(laboratoryPanel.textContent).toContain("Estimated Completion");
  });

  it("keeps closed projects readable while blocking Basic Information writes", async () => {
    const user = userEvent.setup();
    api.getProjectBasicInformation.mockResolvedValue(response());
    api.getProjectLifecycle.mockResolvedValue(
      lifecycleResponse({
        lifecycle_state: "closed",
        closure_type: "completed",
        status: "closed",
        readonly: true,
        allowed_actions: [],
      })
    );

    render(
      <ProjectBasicInformationWorkspace
        projectId="P1"
        onBackToWorkbench={vi.fn()}
      />
    );

    expect(await screen.findByText("Project closed as completed")).toBeTruthy();
    const projectLeader = screen.getByLabelText("Project Leader");
    expect(projectLeader).toHaveProperty("disabled", true);
    await user.type(projectLeader, "Blocked");
    expect(api.saveProjectBasicInformationDraft).not.toHaveBeenCalled();
    const confirmButton = screen.getByRole("button", { name: "Confirm" });
    expect(confirmButton).toHaveProperty("disabled", true);
    await user.click(confirmButton);
    expect(api.confirmProjectBasicInformation).not.toHaveBeenCalled();
  });
});

function completionOptions() {
  return {
    location_options: ["Dongguan"],
    test_type_in_sheet_options: [
      "Qualification",
      "Partial Qualification",
      "Reliability",
    ],
    default_project_leader: "Lab User",
  };
}

function response(
  overrides: Record<string, string> = {},
  status: ProjectBasicInformationResponse["status"] = "unconfirmed",
  missingLabels: string[] = [],
  changedFields: string[] = []
): ProjectBasicInformationResponse {
  const values = {
    dl_number: "DL-2026-05-011",
    project_type: "New Product Development",
    description_pn: "PN-123",
    product_description: "Coolpower HDF",
    test_item: "Qualification Testing",
    applicable_specifications: "EIA-364",
    requested_by: "MP Cao",
    project_leader: "MP Cao",
    lab_performing_tests: "Dongguan",
    date_lab_received_samples: "20 Jun 2026",
    estimated_completion_date: "2026-07-02",
    test_type: "Product/Process Qualification",
    test_type_in_sheet: "Qualification",
    sub_contract: "No",
    business_unit: "Power Solutions",
    project_no: "1252502",
    results_format: "Formal Report (Internal)",
    requested_completion_date: "2026-07-02",
    sample_status: "Pre-production",
    post_testing_disposition: "Send Back to Requestor",
    send_copies_recipients: "Peter.Hu@fci.com/Yi-Peng.Wu@fci.com",
    confidential: "Yes",
    test_result: "In progress",
    ...overrides,
  };
  return {
    project_id: "P1",
    status,
    draft: { values },
    latest_confirmed:
      status === "confirmed"
        ? {
            record_id: "BASIC-1",
            project_id: "P1",
            status: "confirmed",
            version: 1,
            values,
            source_signature: "{}",
            created_at: "2026-06-20T09:00:00+00:00",
            updated_at: "2026-06-20T09:00:00+00:00",
            confirmed_at: "2026-06-20T09:00:00+00:00",
            confirmed_by: "Lab User",
          }
        : null,
    field_suggestions: {
      requested_by: {
        field_key: "requested_by",
        source: "application_form",
        source_value: "Changed Requester",
        needs_review: changedFields.includes("requested_by"),
      },
    },
    changed_source_fields: changedFields,
    missing_required_fields: missingLabels.map((label) => label.toLowerCase()),
    missing_required_labels: missingLabels,
    blockers: [],
    warnings: [],
  };
}

function project() {
  return {
    project_id: "P1",
    project_no: "DL-2026-05-011",
    sample_description: "Coolpower HDF 3.40mm pin",
    product_name: "Coolpower fallback",
    test_item: "Qualification Testing",
    requestor: "MP Cao",
    status: "ltr_registered",
  };
}

function lifecycleResponse(
  overrides: Partial<ProjectLifecycleResponse> = {}
): ProjectLifecycleResponse {
  return {
    project_id: "P1",
    lifecycle_state: "active",
    closure_type: null,
    status: "ltr_registered",
    status_label: "Active",
    stopped_at: null,
    closed_at: null,
    allowed_actions: ["stop", "close_completed", "close_administrative"],
    readonly: false,
    warnings: [],
    ...overrides,
  };
}
