from __future__ import annotations

from pathlib import Path


FRONTEND_ROOT = Path(__file__).resolve().parents[2] / "frontend"


def test_frontend_shell_core_files_exist() -> None:
    """Minimal React shell files are present."""
    expected_files = [
        "package.json",
        "index.html",
        "tsconfig.json",
        "vite.config.ts",
        "public/connlab-icon.svg",
        "src/main.tsx",
        "src/App.tsx",
        "src/api/client.ts",
        "src/components/layout/AppShell.tsx",
        "src/components/layout/Sidebar.tsx",
        "src/components/layout/TopBar.tsx",
        "src/components/project/ProjectStatusBadge.tsx",
        "src/components/common/EmptyState.tsx",
        "src/components/common/ErrorMessage.tsx",
        "src/components/common/LoadingState.tsx",
        "src/components/common/UiIcon.tsx",
        "src/components/workflow/WorkflowStepper.tsx",
        "src/components/workflow/WorkflowStepCard.tsx",
        "src/components/workflow/NextActionPanel.tsx",
        "src/components/workflow/ApplicationFormActionPanel.tsx",
        "src/components/workflow/LtrActionPanel.tsx",
        "src/components/workflow/FolderActionPanel.tsx",
        "src/components/workflow/workflowState.ts",
        "src/components/project/ProjectSummaryPanel.tsx",
        "src/components/precheck/PrecheckSummary.tsx",
        "src/components/precheck/PrecheckIssueCard.tsx",
        "src/components/precheck/IssueSeverityBadge.tsx",
        "src/styles.css",
        "src/project-dashboard.css",
        "src/workbench.css",
    ]

    for relative_path in expected_files:
        assert (FRONTEND_ROOT / relative_path).is_file()


def test_frontend_shell_uses_api_client_and_mvp_routes() -> None:
    """The shell exposes project routes and keeps API calls in the client layer."""
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    list_page_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectListPage.tsx"
    ).read_text(encoding="utf-8")
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")

    assert 'pathname === "/projects"' in app_source
    assert "/projects/" in app_source
    assert "listProjects" in list_page_source
    assert "getProject" in workbench_source
    assert '"/api/projects"' in client_source
    assert 'fetch(`${API_BASE}${path}`' in client_source


def test_frontend_shell_shows_only_mvp_workflow_steps() -> None:
    """The detail workbench shows only MVP workflow steps."""
    workflow_state_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "workflowState.ts"
    ).read_text(encoding="utf-8")

    assert 'title: "Application Form"' in workflow_state_source
    assert 'title: "Precheck"' in workflow_state_source
    assert 'title: "LTR"' in workflow_state_source
    assert 'title: "Project Folder"' in workflow_state_source
    assert "Matrix" not in workflow_state_source
    assert "Report" not in workflow_state_source


def test_frontend_workflow_integration_calls_mvp_actions() -> None:
    """The workbench wires the visible MVP actions to API client functions."""
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")

    for api_name in [
        "uploadApplicationForm",
        "runPrecheck",
        "getLtrReadiness",
        "previewLtrRegistration",
        "commitLtrLocally",
        "previewFolder",
        "generateFolder",
        "resolvePrecheckIssue",
    ]:
        assert api_name in workbench_source


def test_frontend_app_shell_uses_left_navigation_without_hero_layout() -> None:
    """TASK_017 replaces the prototype hero shell with product navigation."""
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    sidebar_source = (
        FRONTEND_ROOT / "src" / "components" / "layout" / "Sidebar.tsx"
    ).read_text(encoding="utf-8")
    top_bar_source = (
        FRONTEND_ROOT / "src" / "components" / "layout" / "TopBar.tsx"
    ).read_text(encoding="utf-8")
    icon_source = (
        FRONTEND_ROOT / "src" / "components" / "common" / "UiIcon.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "styles.css").read_text(
        encoding="utf-8"
    )
    index_source = (FRONTEND_ROOT / "index.html").read_text(encoding="utf-8")

    assert "AppShell" in app_source
    assert "Connector lab workbench" not in app_source
    assert "Dashboard" in sidebar_source
    assert "Projects" in sidebar_source
    assert "New Project" in sidebar_source
    assert "Precheck" in sidebar_source
    assert "LTR Number" in sidebar_source
    assert "Folders" in sidebar_source
    assert "Settings" in sidebar_source
    assert "UiIcon" in sidebar_source
    assert 'icon: "projects"' in sidebar_source
    assert 'icon: "new-project"' in sidebar_source
    assert 'name="bell"' in top_bar_source
    assert 'name="help"' in top_bar_source
    assert "Lab User" in top_bar_source
    assert "Search projects, LTR Number, product" in top_bar_source
    assert "PATHS" in icon_source
    assert "/connlab-icon.svg" in sidebar_source
    assert "/connlab-icon.svg" in index_source
    assert "disabled" in sidebar_source
    assert "Offline local" in top_bar_source
    assert ".sidebar" in styles_source
    assert ".top-bar" in styles_source
    assert ".top-search" in styles_source
    assert ".top-utilities" in styles_source
    assert ".user-menu" in styles_source
    assert ".ui-icon" in styles_source
    assert ".hero" not in styles_source
    assert "scrollbar-gutter: stable" in styles_source


def test_project_dashboard_uses_dense_registry_components() -> None:
    """TASK_018 turns the project list into a searchable registry dashboard."""
    list_page_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectListPage.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "project-dashboard.css").read_text(
        encoding="utf-8"
    )

    assert "useDeferredValue" in list_page_source
    assert "ProjectStatusBadge" in list_page_source
    assert "EmptyState" in list_page_source
    assert "ErrorMessage" in list_page_source
    assert "LoadingState" in list_page_source
    assert "listProjectLtrs" in list_page_source
    assert "project-metric-grid" in list_page_source
    assert "UiIcon" in list_page_source
    assert "Total projects" in list_page_source
    assert "In progress" in list_page_source
    assert "Pending review" in list_page_source
    assert "Completed" in list_page_source
    assert "Draft" in list_page_source
    assert "<table" in list_page_source
    assert "LTR Number" in list_page_source
    assert "Pending LTR Number" in list_page_source
    assert "Product" in list_page_source
    assert "Requestor" in list_page_source
    assert "Business Unit" in list_page_source
    assert "Status" in list_page_source
    assert "Progress" in list_page_source
    assert "Recent Activity" in list_page_source
    assert "New Project" in list_page_source
    assert "Filter" in list_page_source
    assert "Columns" in list_page_source
    assert "view-toggle" in list_page_source
    assert ".project-table" in styles_source
    assert ".project-metric-card" in styles_source
    assert ".progress-cell" in styles_source
    assert ".registry-tools" in styles_source
    assert ".toolbar-button" in styles_source
    assert "@media (min-width: 761px) and (max-width: 1366px)" in styles_source


def test_project_workbench_uses_sequential_stepper() -> None:
    """TASK_019 replaces parallel cards with a single active workflow panel."""
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    stepper_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "WorkflowStepper.tsx"
    ).read_text(encoding="utf-8")
    summary_source = (
        FRONTEND_ROOT / "src" / "components" / "project" / "ProjectSummaryPanel.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "WorkflowStepper" in workbench_source
    assert "NextActionPanel" in workbench_source
    assert "ProjectSummaryPanel" in workbench_source
    workflow_state_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "workflowState.ts"
    ).read_text(encoding="utf-8")

    assert "buildWorkflowSteps" in workflow_state_source
    assert "getActiveWorkflowStep" in workflow_state_source
    assert "buildWorkflowSteps" in workbench_source
    assert "blocked" in workflow_state_source
    assert "current" in workflow_state_source
    assert "warning" in workflow_state_source
    assert "done" in workflow_state_source
    assert "Project workflow" in stepper_source
    assert "Project Ref." in summary_source
    assert ".workflow-stepper" in styles_source
    assert ".next-action-panel" in styles_source


def test_precheck_issue_experience_uses_business_readable_cards() -> None:
    """TASK_020 shows precheck issues as actionable cards, not raw list rows."""
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    issue_card_source = (
        FRONTEND_ROOT / "src" / "components" / "precheck" / "PrecheckIssueCard.tsx"
    ).read_text(encoding="utf-8")
    summary_source = (
        FRONTEND_ROOT / "src" / "components" / "precheck" / "PrecheckSummary.tsx"
    ).read_text(encoding="utf-8")
    badge_source = (
        FRONTEND_ROOT / "src" / "components" / "precheck" / "IssueSeverityBadge.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "PrecheckSummary" in workbench_source
    assert "PrecheckIssueCard" in workbench_source
    assert "resolvePrecheckIssue" in workbench_source
    assert "/api/precheck-issues/" in client_source
    assert "Field or category" in issue_card_source
    assert "What is wrong" in issue_card_source
    assert "Expected value" in issue_card_source
    assert "Suggested action" in issue_card_source
    assert "Mark reviewed" in issue_card_source
    assert "Errors" in summary_source
    assert "Warnings" in summary_source
    assert "Resolved" in badge_source
    assert ".precheck-issue-card" in styles_source
    assert ".issue-severity-error" in styles_source
    assert ".issue-severity-warning" in styles_source


def test_intake_ltr_folder_panels_show_operator_guidance() -> None:
    """TASK_021 improves the three MVP action panels without new backend scope."""
    application_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "ApplicationFormActionPanel.tsx"
    ).read_text(encoding="utf-8")
    ltr_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "LtrActionPanel.tsx"
    ).read_text(encoding="utf-8")
    folder_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "FolderActionPanel.tsx"
    ).read_text(encoding="utf-8")
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "ApplicationFormActionPanel" in workbench_source
    assert "LtrActionPanel" in workbench_source
    assert "FolderActionPanel" in workbench_source
    assert "Application intake" in application_source
    assert "Requested Testing" in application_source
    assert "next" in application_source.lower()
    assert "Latest local LTR Number" in ltr_source
    assert "LTR Number registered locally" in ltr_source
    assert "Not registered" in ltr_source
    assert "No-write preview" in ltr_source
    assert "does not write the workbook" in ltr_source
    assert "Normal LTR Number allocation" in ltr_source
    assert "folder-tree-preview" in folder_source
    assert "Conflict detected" in folder_source
    assert "folderPlan.conflict || Boolean(folderGenerateBlockReason)" in folder_source
    assert ".operator-panel" in styles_source
    assert ".metadata-grid" in styles_source
    assert ".folder-tree-preview" in styles_source


def test_ltr_frontend_wires_readiness_preview_and_local_commit() -> None:
    """TASK_054 wires existing LTR readiness, preview, and local commit APIs."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    ltr_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "LtrActionPanel.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for term in [
        "/ltr/readiness",
        "/ltr/preview",
        "/ltr/commit",
        "getLtrReadiness",
        "previewLtrRegistration",
        "commitLtrLocally",
    ]:
        assert term in client_source
        assert term in workbench_source or term.startswith("/ltr/")

    for term in [
        "Readiness",
        "Blocking fields",
        "Needs review",
        "Placeholders",
        "No-write preview",
        "Commit locally",
        "I confirm this preview should be committed locally.",
        "Normal LTR Number final allocation requires an enabled Excel write session.",
        "buildLocalCommitRequest",
    ]:
        assert term in ltr_source

    assert "registerLtr(" not in workbench_source
    assert ".readiness-panel" in styles_source
    assert ".ltr-preview-card" in styles_source


def test_intake_exception_frontend_wires_review_outcomes() -> None:
    """TASK_055 wires intake exception outcomes into the frontend."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    package_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakePackageDetailPage.tsx"
    ).read_text(encoding="utf-8")
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")
    package_styles = (FRONTEND_ROOT / "src" / "intake-package-detail.css").read_text(
        encoding="utf-8"
    )
    case_styles = (FRONTEND_ROOT / "src" / "intake-case-review.css").read_text(
        encoding="utf-8"
    )

    for term in [
        "ExceptionWorkflowReview",
        "ExceptionWorkflowIssue",
        "reviewIntakePackageExceptions",
        "/exceptions/review",
    ]:
        assert term in client_source

    for term in [
        "Create review cases",
        "No-form package",
        "Multiple forms",
        "Each candidate form becomes a separate project request",
        "reviewIntakePackageExceptions",
    ]:
        assert term in package_source

    for term in [
        "getIntakeCaseReview",
        "confirmIntakeCase",
        "updateIntakeCaseReviewFields",
        "/case-review",
        "/review-fields",
        "/api/intake-cases/",
    ]:
        assert term in client_source

    for term in [
        "getIntakeCaseReview",
        "confirmIntakeCase",
        "updateIntakeCaseReviewFields",
        "Save corrections",
        "draft-field-input",
        "operatorConfirmed",
        "Confirmation blockers",
        "Backend confirmation rejects missing required project request fields",
        "Confirm into project",
        "source context",
        "selected_asset_name",
        "missing_required_fields",
    ]:
        assert term in case_review_source

    assert ".exception-review-panel" in package_styles
    assert ".exception-issue-list" in package_styles
    assert ".missing-info-panel" in case_styles
    assert ".missing-info-list" in case_styles
    assert ".case-selector-panel" in case_styles
    assert ".confirmation-result" in case_styles
    assert ".draft-field-input" in case_styles
    assert ".draft-save-panel" in case_styles


def test_task067_frontend_uses_new_project_and_ltr_number_language() -> None:
    """TASK_067 keeps user-facing project identity language consistent."""
    sidebar_source = (
        FRONTEND_ROOT / "src" / "components" / "layout" / "Sidebar.tsx"
    ).read_text(encoding="utf-8")
    top_bar_source = (
        FRONTEND_ROOT / "src" / "components" / "layout" / "TopBar.tsx"
    ).read_text(encoding="utf-8")
    list_page_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectListPage.tsx"
    ).read_text(encoding="utf-8")
    ltr_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "LtrActionPanel.tsx"
    ).read_text(encoding="utf-8")
    folder_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "FolderActionPanel.tsx"
    ).read_text(encoding="utf-8")

    for source in [sidebar_source, top_bar_source, list_page_source, ltr_source, folder_source]:
        assert "LTR/DL" not in source
        assert "DL number" not in source
        assert "DL Number" not in source
        assert "DL allocation" not in source

    assert "New Project" in sidebar_source
    assert "New Project" in top_bar_source
    assert "LTR Number" in list_page_source
    assert "Pending LTR Number" in list_page_source
    assert "LTR Number" in ltr_source
    assert "LTR Number" in folder_source


def test_package_detail_frontend_loads_real_package_assets() -> None:
    """TASK_062 replaces static package detail data with real API state."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    package_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakePackageDetailPage.tsx"
    ).read_text(encoding="utf-8")
    package_styles = (FRONTEND_ROOT / "src" / "intake-package-detail.css").read_text(
        encoding="utf-8"
    )

    for term in [
        "IntakePackageDetail",
        "IntakeCaseSummary",
        "getIntakePackageDetail",
        "/api/intake-packages/",
    ]:
        assert term in client_source

    for term in [
        "getIntakePackageDetail",
        "source_stored",
        "candidate_assets",
        "asset_count",
        "case_count",
        "Loading package source and assets",
        "Stored asset list",
    ]:
        assert term in package_source

    assert "const ASSETS" not in package_source
    assert ".asset-role-source" in package_styles


def test_msg_package_import_frontend_wires_intake_step_entry() -> None:
    """TASK_069 keeps `.msg` upload as the Intake step source entry."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    inbox_styles = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
    )

    for term in [
        "IntakePackageImport",
        "IntakeAsset",
        "importMsgPackage",
        "/api/intake-packages/import-msg",
        "responseErrorMessage",
    ]:
        assert term in client_source

    for term in [
        'accept=".msg"',
        "importMsgPackage",
        "selectIntakeApplicationForm",
        "Import email package",
        "Upload application form",
        "Email information",
        "Attachments (",
        "Attachment details",
        "Continue to Precheck",
        "Preparing Precheck...",
        "handleContinueToPrecheck",
        "selectedWordAssetId",
        "selectedPrecheckCaseId",
        "application-form-asset",
        "isWordAsset",
    ]:
        assert term in inbox_source

    assert "fetch(" not in inbox_source
    assert ".new-project-stepper" in inbox_styles
    assert ".intake-step-grid" in inbox_styles
    assert ".attachment-details-panel" in inbox_styles
    assert ".attachment-row-active" in inbox_styles
    assert ".document-preview" in inbox_styles
    assert ".step-footer" in inbox_styles
    assert ".intake-error" in inbox_styles


def test_direct_application_form_entry_is_visible_without_backend_wiring() -> None:
    """TASK_069 shows direct Word intake as an affordance without route changes."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    inbox_styles = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
    )

    for term in [
        "ManualIntakeInput",
        "ManualIntake",
        "createManualIntake",
        "/api/intake-packages/manual",
    ]:
        assert term in client_source

    for term in [
        'accept=".doc,.docx"',
        "Upload application form",
        "directWordName",
        "Direct application form import is visible here but not wired to backend in this task.",
    ]:
        assert term in inbox_source

    assert "fetch(" not in inbox_source
    assert "createManualIntake" not in inbox_source
    assert ".source-button" in inbox_styles
    assert ".attachment-empty" in inbox_styles


def test_task070_precheck_step_matches_reference_workspace() -> None:
    """TASK_070 turns case review into the step-style Precheck workspace."""
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")
    case_styles = (FRONTEND_ROOT / "src" / "intake-case-review.css").read_text(
        encoding="utf-8"
    )

    for term in [
        'import "../intake-case-review.css"',
        "Step 2 of 4: Precheck",
        "Source document & template check",
        "Template version mismatch detected",
        "Lab Test Request Number must be blank",
        "Key Information Edit & Confirm",
        "Test Sample Information",
        "Description of Requested Testing",
        "Additional Information",
        "Send copies of test results/reports to",
        "Confirm & Continue to LTR Number",
        "PROJECT_FIELDS",
        "sample_rows",
    ]:
        assert term in case_review_source

    for term in [
        ".precheck-workflow",
        ".precheck-stepper",
        ".source-template-check",
        ".precheck-blocker-banner",
        ".precheck-form-grid",
        ".precheck-sample-table",
        ".precheck-lower-grid",
        ".recipients-panel",
        ".precheck-footer",
        "@media (min-width: 761px) and (max-width: 1366px)",
    ]:
        assert term in case_styles


def test_task071_intake_session_state_survives_route_changes() -> None:
    """TASK_071 lifts Intake package state to App so step navigation preserves it."""
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")

    for term in [
        "EMPTY_INTAKE_SESSION",
        "type IntakeSessionState",
        "useState<IntakeSessionState>",
        "session={intakeSession}",
        "onSessionChange={setIntakeSession}",
        'navigate(`/intake/${encodeURIComponent(id)}/case-review`)',
        'onBack={() => navigate("/intake")}',
    ]:
        assert term in app_source

    for term in [
        "export type IntakeSessionState",
        "export const EMPTY_INTAKE_SESSION",
        "session: IntakeSessionState",
        "onSessionChange: (session: IntakeSessionState) => void",
        "onSessionChange({",
        "selectedWordAssetId",
    ]:
        assert term in inbox_source


def test_task073_selected_form_precheck_binding_is_explicit() -> None:
    """TASK_073 binds the Intake-selected Word asset to the Precheck case."""
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")

    for term in [
        "SelectedApplicationForm",
        "selectIntakeApplicationForm",
        "/select-form",
        "asset_id",
    ]:
        assert term in client_source

    for term in [
        "selectIntakeApplicationForm",
        "selectedApplicationForm.asset_id",
        "selectedPrecheckCaseId",
        "selection.case_id",
    ]:
        assert term in inbox_source

    for term in [
        "initialCaseId={intakeSession.selectedPrecheckCaseId}",
        "selectedPrecheckCaseId: caseId",
    ]:
        assert term in app_source

    for term in [
        "initialCaseId",
        "preferredCaseId",
        "reference_doc",
        "sample_rows",
        "normalizedOptions",
        "normalizedSampleRows",
        "No additional information extracted from the selected application form.",
    ]:
        assert term in case_review_source


def test_precheck_date_fields_normalize_parser_dates_for_date_inputs() -> None:
    """Precheck date inputs convert Word MM/DD/YYYY values to browser ISO dates."""
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")

    for term in [
        "dateInputValue(value)",
        'type={field.kind === "date" ? "date" : "text"}',
        r"^(\d{1,2})\/(\d{1,2})\/(\d{4})$",
        'return `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`',
    ]:
        assert term in case_review_source


def test_task081_precheck_selects_use_backend_lookup_options() -> None:
    """TASK_081 wires Precheck select fields to backend lookup options."""
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )

    for term in [
        "IntakePrecheckLookupOptions",
        "getIntakePrecheckLookupOptions",
        '"/api/lookups/intake-precheck"',
    ]:
        assert term in client_source

    for term in [
        "lookupGroup: \"business_unit\"",
        "lookupGroup: \"manufacturing_site\"",
        "lookupGroup: \"results_format\"",
        "lookupGroup: \"test_type\"",
        "lookupGroup: \"sample_status\"",
        "lookupGroup: \"project_type\"",
        "lookupGroup: \"post_testing_disposition\"",
        "fieldsWithLookupOptions",
        "getIntakePrecheckLookupOptions",
        "Post-Testing Sample Disposition",
        "ConsentPanel",
        "normalizedOptions",
    ]:
        assert term in case_review_source

    for hardcoded_option in [
        "Power Solutions\", \"RFOB",
        "AAL\", \"AAOP Berlin",
        "Product/Process Development\", \"Product/Process Qualification",
        "<option>Return to requestor</option>",
        "function DispositionPanel",
    ]:
        assert hardcoded_option not in case_review_source


def test_task082_precheck_sample_rows_are_editable_with_icon_actions() -> None:
    """TASK_082 makes sample rows editable and uses compact icon actions."""
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")
    case_styles = (FRONTEND_ROOT / "src" / "intake-case-review.css").read_text(
        encoding="utf-8"
    )
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    icon_source = (
        FRONTEND_ROOT / "src" / "components" / "common" / "UiIcon.tsx"
    ).read_text(encoding="utf-8")

    for term in [
        "SAMPLE_COLUMNS",
        "Part Number / Revision",
        "Traceability Manufacturing Lot Info",
        "sampleRows",
        "sample_rows: sampleRows",
        "onAdd",
        "onChange",
        "onEdit",
        "onCopy",
        "onDelete",
        "focusSampleRow",
        "copySampleRow",
        "deleteSampleRow",
        "mergedPartNumberRevision",
        "mergedTraceabilityLotInfo",
        "rows.length <= 1",
        'name="edit"',
        'name="copy"',
        'name="trash"',
    ]:
        assert term in case_review_source

    for term in [
        ".sample-row-actions",
        ".sample-add-button",
        ".precheck-sample-table input",
    ]:
        assert term in case_styles

    assert "sample_rows?: Record<string, string>[]" in client_source
    assert '| "edit"' in icon_source
    assert '| "copy"' in icon_source
    assert '| "trash"' in icon_source
    assert "Manufacturing Lot/No." not in case_review_source
    assert 'label: "Revision"' not in case_review_source


def test_task083_precheck_shows_section1_issue_summary_and_field_highlights() -> None:
    """TASK_083 surfaces deterministic SECTION 1 precheck issues before confirm."""
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")
    case_styles = (FRONTEND_ROOT / "src" / "intake-case-review.css").read_text(
        encoding="utf-8"
    )
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )

    for term in [
        "DraftPrecheckIssue",
        "precheck_issues",
    ]:
        assert term in client_source

    for term in [
        "PrecheckIssueSummary",
        "issueLevelMap",
        "precheck_issues",
        "SECTION 1 precheck",
        "SECTION 2 lab fields are excluded",
        "precheck-field-error",
        "precheck-field-warning",
        "send_copies_recipients",
    ]:
        assert term in case_review_source

    for term in [
        ".precheck-issue-summary",
        ".precheck-field-error",
        ".precheck-field-warning",
    ]:
        assert term in case_styles

    assert "Andy Liu" not in case_review_source
    assert "Quality Team" not in case_review_source


def test_task075_intake_attachment_preview_prioritizes_docx() -> None:
    """TASK_075 wires selected-attachment preview with DOCX structured view first."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    inbox_styles = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
    )

    for term in [
        "IntakeAssetPreview",
        "IntakeAssetPreviewTable",
        "getIntakeAssetPreview",
        "/api/intake-assets/",
        "/preview",
    ]:
        assert term in client_source

    for term in [
        "getIntakeAssetPreview",
        "AttachmentPreview",
        "DocxApplicationPreview",
        "docx_application_form",
        "Structured Word preview",
        "Loading preview",
        "Preview unavailable",
        "Test Sample Information",
        "PreviewTableSection",
    ]:
        assert term in inbox_source

    for term in [
        ".docx-structured-preview",
        ".docx-field-grid",
        ".preview-table-section",
        ".preview-warning-list",
        ".unsupported-preview",
        ".preview-error-state",
    ]:
        assert term in inbox_styles


def test_folder_evidence_frontend_wires_preview_and_execution() -> None:
    """TASK_056 wires evidence placement preview and no-overwrite execution."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    folder_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "FolderActionPanel.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for term in [
        "EvidencePlacementPlan",
        "EvidencePlacementResult",
        "previewEvidencePlacement",
        "placeEvidence",
        "/evidence/placement-preview",
        "/evidence/place",
    ]:
        assert term in client_source

    for term in [
        "previewEvidencePlacement",
        "placeEvidence",
        "evidencePlan",
        "evidenceResult",
    ]:
        assert term in workbench_source

    for term in [
        "Evidence placement",
        "Source email",
        "selected application form",
        "LTR evidence",
        "correction evidence",
        "No-overwrite copy ready",
        "Place evidence",
        "No existing target files were overwritten.",
    ]:
        assert term in folder_source

    assert ".evidence-placement-panel" in styles_source
    assert ".evidence-plan-conflict" in styles_source
    assert ".evidence-item-list" in styles_source


def test_project_lookup_frontend_wires_read_only_summaries() -> None:
    """TASK_057 wires project lookup, sample summary, and testing summary UI."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    lookup_source = (
        FRONTEND_ROOT / "src" / "components" / "project" / "ProjectLookupPanel.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for term in [
        "ProjectLookupRow",
        "SampleSummary",
        "TestingSummary",
        "lookupProjects",
        "getSampleSummary",
        "getTestingSummary",
        "/api/projects/lookup",
        "/sample-summary",
        "/testing-summary",
    ]:
        assert term in client_source

    assert "ProjectLookupPanel" in workbench_source

    for term in [
        "Read-only lookup",
        "Sample summary",
        "Testing condition and method",
        "Search LTR, part, product, requestor",
        "Requested testing",
        "Sample condition",
        "Specifications",
    ]:
        assert term in lookup_source

    assert ".project-lookup-panel" in styles_source
    assert ".lookup-summary-grid" in styles_source
    assert ".lookup-table" in styles_source


def test_lifecycle_guard_reasons_are_visible_in_frontend() -> None:
    """TASK_058 surfaces lifecycle guard disabled reasons inline."""
    lifecycle_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "lifecycleGuards.ts"
    ).read_text(encoding="utf-8")
    ltr_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "LtrActionPanel.tsx"
    ).read_text(encoding="utf-8")
    folder_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "FolderActionPanel.tsx"
    ).read_text(encoding="utf-8")
    workflow_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "workflowState.ts"
    ).read_text(encoding="utf-8")

    for term in [
        "LTR registration requires confirmed project data",
        "Project folder generation requires a registered LTR first",
        "Evidence placement requires a generated project folder first",
        "Project already has a registered LTR",
        "Project folder has already been created",
    ]:
        assert term in lifecycle_source

    assert "previewBlockReason" in ltr_source
    assert "commitBlockedReason" in ltr_source
    assert "folderPreviewBlockReason" in folder_source
    assert "folderGenerateBlockReason" in folder_source
    assert "evidencePlaceBlockReason" in folder_source
    assert "lifecycleBlockReason" in workflow_source


def test_frontend_api_calls_remain_centralized() -> None:
    """TASK_022 keeps raw fetch usage inside the API client only."""
    src_root = FRONTEND_ROOT / "src"
    files_with_fetch = [
      path.relative_to(FRONTEND_ROOT).as_posix()
      for path in src_root.rglob("*.ts*")
      if "fetch(" in path.read_text(encoding="utf-8")
    ]

    assert files_with_fetch == ["src/api/client.ts"]
