from __future__ import annotations

from pathlib import Path


FRONTEND_ROOT = Path(__file__).resolve().parents[2] / "frontend"


def precheck_feature_source() -> str:
    """Return the current Precheck feature source used by static UI checks."""
    feature_root = FRONTEND_ROOT / "src" / "features" / "precheck"
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(feature_root.glob("*.tsx")) + sorted(feature_root.glob("*.ts"))
    )


def intake_feature_source() -> str:
    """Return the current Intake feature source used by static UI checks."""
    feature_root = FRONTEND_ROOT / "src" / "features" / "intake"
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(feature_root.glob("*.tsx")) + sorted(feature_root.glob("*.ts"))
    )


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
    """Workbench integration follows either legacy wizard or TASK_100 post-creation boundary."""
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")

    if "Project workbench boundary" in workbench_source:
        for blocked_term in [
            "uploadApplicationForm",
            "runPrecheck",
            "getLtrReadiness",
            "previewLtrRegistration",
            "commitLtrLocally",
            "previewFolder",
            "generateFolder",
            "resolvePrecheckIssue",
            "ApplicationFormActionPanel",
            "LtrActionPanel",
            "FolderActionPanel",
        ]:
            assert blocked_term not in workbench_source
        for term in [
            "previewEvidencePlacement",
            "placeEvidence",
            "ProjectLookupPanel",
        ]:
            assert term in workbench_source
        return

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
    intake_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
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
    assert "Precheck" not in sidebar_source
    assert "LTR Number" not in sidebar_source
    assert "Precheck" in intake_review_source
    assert "LTR Number" in workbench_source
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
    """Workbench keeps either legacy stepper or TASK_100 post-creation status surface."""
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

    if "Project workbench boundary" in workbench_source:
        assert "WorkflowStepper" not in workbench_source
        assert "NextActionPanel" not in workbench_source
        assert "project-workbench-status" in workbench_source
        assert ".project-workbench-status" in styles_source
        return

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
    """Precheck issue card assets stay available; Workbench inclusion may change after TASK_100."""
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

    if "Project workbench boundary" in workbench_source:
        assert "PrecheckSummary" not in workbench_source
        assert "PrecheckIssueCard" not in workbench_source
        assert "resolvePrecheckIssue" not in workbench_source
    else:
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
    """Legacy workflow action panels stay defined; Workbench may decouple after TASK_100."""
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

    if "Project workbench boundary" in workbench_source:
        assert "ApplicationFormActionPanel" not in workbench_source
        assert "LtrActionPanel" not in workbench_source
        assert "FolderActionPanel" not in workbench_source
    else:
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
    if "Project workbench boundary" not in workbench_source:
        for term in [
            "getLtrReadiness",
            "previewLtrRegistration",
            "commitLtrLocally",
        ]:
            assert term in workbench_source

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
    ).read_text(encoding="utf-8") + precheck_feature_source()
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
    ).read_text(encoding="utf-8") + intake_feature_source()
    inbox_styles = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
    )
    workflow_styles = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "new-project-workflow.css"
    ).read_text(encoding="utf-8")

    if "NewProjectApplicationEditor" in inbox_source:
        assert "ensureNewProjectApplicationDraft" in inbox_source
        assert "Apply LTR Number and Create Folder" in inbox_source + (
            FRONTEND_ROOT / "src" / "features" / "new-project" / "NewProjectApplicationEditor.tsx"
        ).read_text(encoding="utf-8")
        return

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
        "Import from Outlook",
        "Upload application form",
        "Email information",
        "Attachments (",
        "Attachment details",
        "Continue to Precheck",
        "Preparing Precheck...",
        "handleContinueToPrecheck",
        "selectedWordAssetId",
        "selectedPrecheckCaseId",
        "isWordAsset",
    ]:
        assert term in inbox_source

    assert "fetch(" not in inbox_source
    assert ".new-project-stepper" in workflow_styles
    assert ".intake-step-grid" in inbox_styles
    assert ".attachment-details-panel" in inbox_styles
    assert ".attachment-row-active" in inbox_styles
    assert ".document-preview" in inbox_styles
    assert ".step-footer" in inbox_styles
    assert ".intake-error" in inbox_styles


def test_direct_application_form_entry_imports_through_backend() -> None:
    """TASK_086 wires direct Word intake to the backend import endpoint."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8") + intake_feature_source()
    inbox_styles = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
    )

    if "NewProjectApplicationEditor" in inbox_source:
        assert "importDirectWordApplicationForm(file)" in inbox_source
        return

    for term in [
        "importDirectWordApplicationForm",
        "/api/intake-packages/import-docx",
    ]:
        assert term in client_source

    for term in [
        'accept=".docx"',
        "Upload application form",
        "importDirectWordApplicationForm(file)",
        "directWordName",
        'sourceMode: "word"',
        "Uploading application form...",
        "Direct application form import failed.",
    ]:
        assert term in inbox_source

    assert "fetch(" not in inbox_source
    assert "createManualIntake" not in inbox_source
    assert "not wired to backend" not in inbox_source
    assert ".source-button" in inbox_styles
    assert ".attachment-empty" in inbox_styles


def test_task087_intake_information_density_cleanup() -> None:
    """TASK_087 keeps Intake source review concise and action-focused."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8") + intake_feature_source()
    inbox_styles = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
    )

    for term in [
        "received_at?: string | null",
        "IntakePackageImport",
    ]:
        assert term in client_source

    for term in [
        "senderEmailText",
        "mailDateText",
        "Application form:",
        "Select a .docx Laboratory Testing Request form to continue.",
        "attachmentRoleText",
        "toLocaleString",
    ]:
        assert term in inbox_source

    for removed_term in [
        "senderText",
        "<dt>Source file</dt>",
        'className="attachment-type"',
        'className="attachment-size"',
        'className="attachment-guidance"',
        "Choose one Word document as the application form.",
        "application-form-asset",
        'type="radio"',
        "attachment-selection-mark",
    ]:
        assert removed_term not in inbox_source

    assert "grid-template-columns: 42px minmax(0, 1fr);" in inbox_styles
    assert ".step-footer-guidance" in inbox_styles
    assert ".attachment-title" in inbox_styles
    assert ".attachment-guidance" not in inbox_styles
    assert "grid-template-rows: auto auto;" in inbox_styles
    assert ".intake-attachments-panel" in inbox_styles
    assert "grid-template-rows: auto minmax(0, 1fr);" in inbox_styles
    assert "overflow: auto;" in inbox_styles
    assert "align-content: start;" in inbox_styles


def test_task094_intake_continue_uses_application_form_header_gate() -> None:
    """TASK_094 gates Continue to Precheck on backend application-form eligibility."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8") + intake_feature_source()

    for term in [
        "ApplicationFormEligibility",
        "validateIntakeAssetApplicationForm",
        "/application-form/validate",
    ]:
        assert term in client_source

    if "NewProjectApplicationEditor" in inbox_source:
        assert "ensureNewProjectApplicationDraft" in inbox_source
        assert "validateIntakeAssetApplicationForm" in client_source
        return

    for term in [
        "intakeContinueState",
        "applicationFormEligibility",
        "validatingApplicationForm",
        "continueState.canContinue",
        "selectedWordAssetId: attachment.word ? attachment.asset.asset_id : null",
        "selectedPrecheckCaseId: null",
        "Selected file is not .docx. Select a .docx application form.",
        "Import an email package with an application form or upload the application form.",
        "Header table cell (1,2)",
        "Selected document is not recognized as Laboratory Testing Request.",
        "Select a .docx Laboratory Testing Request form to continue.",
        'asset.extension.toLowerCase() === ".docx"',
    ]:
        assert term in inbox_source

    assert "Select a Word (.docx) file before continuing." not in inbox_source


def test_task095_precheck_uses_single_active_case_without_switcher() -> None:
    """TASK_095 keeps the New Project Precheck page on one active case."""
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8") + intake_feature_source()
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")

    if "NewProjectApplicationEditor" in inbox_source:
        assert "selectedPrecheckCaseId: draft.case_id" in inbox_source
        assert "review.cases.find" in inbox_source
        return

    assert "selectedPrecheckCaseId: null" in inbox_source
    assert inbox_source.count("selectedPrecheckCaseId: null") >= 3
    assert "selectedPrecheckCaseId: selection.case_id" in inbox_source
    assert "review.cases.find((item) => item.case_id === selectedCaseId)" in case_review_source
    assert "Review cases" not in case_review_source
    assert "case-switcher" not in case_review_source
    assert "case-selector-list" not in case_review_source


def test_task087_msg_attachment_hotfix_filters_source_and_labels_msg() -> None:
    """Real Outlook attachments hide source email rows and show `.msg` chips."""
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8") + intake_feature_source()
    inbox_styles = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
    )

    for term in [
        "visibleIntakeAttachments",
        'asset.asset_role !== "email_source"',
        'extension === ".msg"',
        'return "MSG"',
    ]:
        assert term in inbox_source

    assert ".file-chip-msg" in inbox_styles


def test_task070_precheck_step_matches_reference_workspace() -> None:
    """TASK_070 turns case review into the step-style Precheck workspace."""
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8") + precheck_feature_source() + (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "NewProjectWorkflow.tsx"
    ).read_text(encoding="utf-8")
    case_styles = (FRONTEND_ROOT / "src" / "intake-case-review.css").read_text(
        encoding="utf-8"
    )
    workflow_styles = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "new-project-workflow.css"
    ).read_text(encoding="utf-8")

    for term in [
        'import "../intake-case-review.css"',
        'currentStep="precheck"',
        "Source traceability",
        "Confirmed application data is edited below",
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

    assert ".new-project-stepper" in workflow_styles


def test_task089_new_project_workflow_shell_is_shared() -> None:
    """TASK_089 uses one workflow shell across Intake and Precheck."""
    page_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    inbox_source = (
        page_source + intake_feature_source()
    )
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")
    workflow_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "NewProjectWorkflow.tsx"
    ).read_text(encoding="utf-8")
    workflow_styles = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "new-project-workflow.css"
    ).read_text(encoding="utf-8")

    if "NewProjectApplicationEditor" in inbox_source:
        assert "new-project-single-page" in page_source
        assert "AttachmentPreviewPanel" not in page_source
        assert "Apply LTR Number and Create Folder" in (
            FRONTEND_ROOT / "src" / "features" / "new-project" / "NewProjectApplicationEditor.tsx"
        ).read_text(encoding="utf-8")
        return

    for term in [
        "NewProjectWorkflowHeader",
        'currentStep="intake"',
        "Continue to Precheck",
    ]:
        assert term in inbox_source

    assert 'className="secondary-action" disabled type="button">Back' not in inbox_source

    for term in [
        "NewProjectWorkflowHeader",
        'currentStep="precheck"',
        "Confirm & Continue to LTR Number",
    ]:
        assert term in case_review_source

    for term in [
        "aria-label={`",
        "Intake",
        "Precheck",
        "LTR Number",
        "Project Folder",
    ]:
        assert term in workflow_source

    for term in [
        ".new-project-stepper",
        ".new-project-step-complete",
        ".new-project-step-current",
        ".new-project-primary-action",
        ".new-project-secondary-action",
        "overflow-x: auto",
        "white-space: nowrap",
        "grid-template-columns: repeat(4, max-content)",
    ]:
        assert term in workflow_styles


def test_task071_intake_session_state_survives_route_changes() -> None:
    """TASK_071 lifts Intake package state to App so step navigation preserves it."""
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8") + intake_feature_source()
    session_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "intakeSession.ts"
    ).read_text(encoding="utf-8")

    if "NewProjectApplicationEditor" in inbox_source:
        assert 'navigate("/intake")' in app_source
        assert "session={intakeSession}" in app_source
        assert "onSessionChange={setIntakeSession}" in app_source
        return

    for term in [
        "type IntakeSessionState",
        "useState<IntakeSessionState>",
        "session={intakeSession}",
        "onSessionChange={setIntakeSession}",
        'navigate(`/intake/${encodeURIComponent(id)}/case-review`)',
        'onBack={() => navigate("/intake")}',
    ]:
        assert term in app_source

    for term in [
        "session: IntakeSessionState",
        "onSessionChange: (session: IntakeSessionState) => void",
        "onSessionChange({",
        "selectedWordAssetId",
    ]:
        assert term in inbox_source

    for term in [
        "export type IntakeSessionState",
        "export const EMPTY_INTAKE_SESSION",
    ]:
        assert term in session_source


def test_task085_intake_session_persists_to_session_storage() -> None:
    """TASK_085 persists New Project Intake state through browser refresh."""
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    session_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "intakeSession.ts"
    ).read_text(encoding="utf-8")
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")

    for term in [
        "loadIntakeSession",
        "saveIntakeSession",
        "clearIntakeSession",
        "window.sessionStorage",
        "connlab:intake-session",
        "normalizeIntakeSession",
        "EMPTY_INTAKE_SESSION",
    ]:
        assert term in session_source

    for term in [
        "useState<IntakeSessionState>(loadIntakeSession)",
        "saveIntakeSession(intakeSession)",
        "clearIntakeSession();",
        "setIntakeSession(EMPTY_INTAKE_SESSION);",
    ]:
        assert term in app_source

    for term in [
        "onProjectConfirmed?: () => void",
        "onProjectConfirmed?.()",
    ]:
        assert term in case_review_source


def test_task085_precheck_back_preserves_intake_selected_form_session() -> None:
    """TASK_098 supersedes the old Precheck back-navigation hotfix."""
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")

    assert "Back to Intake" not in case_review_source
    assert "PrecheckBackSnapshot" not in case_review_source
    assert "PrecheckBackSnapshot" not in app_source
    assert "Save draft and exit" in case_review_source
    assert "Exit without saving" in case_review_source


def test_task073_selected_form_precheck_binding_is_explicit() -> None:
    """TASK_073 binds the Intake-selected Word asset to the Precheck case."""
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8") + intake_feature_source()
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8") + precheck_feature_source()

    if "NewProjectApplicationEditor" in inbox_source:
        assert "ensureNewProjectApplicationDraft" in inbox_source
        assert "selectedAsset.asset_id" not in inbox_source
        assert "/select-form" in client_source
        return

    for term in [
        "SelectedApplicationForm",
        "selectIntakeApplicationForm",
        "/select-form",
        "asset_id",
    ]:
        assert term in client_source

    for term in [
        "selectIntakeApplicationForm",
        "selectedAsset.asset_id",
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
    ).read_text(encoding="utf-8") + precheck_feature_source()

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
    ).read_text(encoding="utf-8") + precheck_feature_source()
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
        "precheck-consent-row",
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
    ).read_text(encoding="utf-8") + precheck_feature_source()
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
        "onCopy",
        "onDelete",
        "copySampleRow",
        "deleteSampleRow",
        "mergedPartNumberRevision",
        "mergedTraceabilityLotInfo",
        "rows.length <= 1",
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
    assert '| "copy"' in icon_source
    assert '| "trash"' in icon_source
    assert "Manufacturing Lot/No." not in case_review_source
    assert 'label: "Revision"' not in case_review_source


def test_task083_precheck_shows_section1_issue_summary_and_field_highlights() -> None:
    """TASK_083 surfaces deterministic SECTION 1 precheck issues before confirm."""
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8") + precheck_feature_source()
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


def test_task084_precheck_route_uses_feature_boundary_and_style_tokens() -> None:
    """TASK_084 keeps Precheck page logic thin and moves UI details to features."""
    page_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")
    feature_source = precheck_feature_source()
    case_styles = (FRONTEND_ROOT / "src" / "intake-case-review.css").read_text(
        encoding="utf-8"
    )
    inbox_styles = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
    )

    for relative_path in [
        "src/features/precheck/precheckFieldConfig.ts",
        "src/features/precheck/precheckReviewSelectors.ts",
        "src/features/precheck/PrecheckFieldGrid.tsx",
        "src/features/precheck/PrecheckSampleTable.tsx",
        "src/features/precheck/PrecheckIssueSummary.tsx",
        "src/features/precheck/PrecheckSourceCheck.tsx",
    ]:
        assert (FRONTEND_ROOT / relative_path).is_file()

    for term in [
        "PrecheckFieldGrid",
        "PrecheckSampleTable",
        "PrecheckIssueSummary",
        "PrecheckSourceCheck",
        "PrecheckLowerPanels",
        "PrecheckMessages",
    ]:
        assert term in page_source

    for term in [
        "PRECHECK_PROJECT_FIELDS",
        "PRECHECK_SAMPLE_COLUMNS",
        "fieldsWithLookupOptions",
        "normalizedSampleRows",
        "mergedPartNumberRevision",
        "mergedTraceabilityLotInfo",
    ]:
        assert term in feature_source

    assert 'lookupGroup: "business_unit"' not in page_source
    assert "const SAMPLE_COLUMNS" not in page_source
    assert "function ReviewField" not in page_source
    assert "--precheck-data-ink" in case_styles
    assert "--precheck-control-min-width" in case_styles
    assert "--intake-data-ink" in inbox_styles


def test_task075_intake_attachment_preview_prioritizes_docx() -> None:
    """TASK_075 wires selected-attachment preview with DOCX structured view first."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8") + intake_feature_source()
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
        "AttachmentPreview",
        "DocxApplicationPreview",
        "docx_application_form",
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


def test_task088_attachment_details_preview_completion() -> None:
    """TASK_088 renders image previews and metadata-only attachment details."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8") + intake_feature_source()
    inbox_styles = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
    )

    for term in [
        "image_data_url?: string | null",
        "metadata_only",
    ]:
        assert term in client_source + inbox_source

    for term in [
        "ImageAttachmentPreview",
        "MetadataOnlyPreview",
        "image_data_url",
        "assetKindFromPreview",
    ]:
        assert term in inbox_source

    for term in [
        ".image-attachment-preview",
        ".image-preview-frame",
        ".metadata-only-preview",
        ".docx-preview-title-with-actions",
    ]:
        assert term in inbox_styles

    assert "Document structure" not in inbox_source

    assert "AttachmentPreviewActions" in inbox_source
    assert "docx-preview-title-with-actions" in inbox_source
    assert "attachment-details-panel-compact" in inbox_source
    assert "metadata-preview-grid" not in inbox_source
    assert "previewStatusText" not in inbox_source
    assert "formatBytes" not in inbox_source

    # TASK_088 polish: Form No. and Revision moved to end of field grid as merged card
    assert "businessPreviewFields" in inbox_source
    assert "formVersionText" in inbox_source
    assert "Form No./Revision" in inbox_source

    # Requested Testing alignment: application-form table shape, no Send Copies To in attachment details
    assert "RequestedTestingPreviewSection" in inbox_source
    assert "requestedTestingTable" in inbox_source
    assert "additionalInformationTable" in inbox_source
    assert "Description of Requested Testing" in inbox_source
    assert "PreviewTableSection table={requestedTestingTable}" in inbox_source
    assert "No additional information extracted from the selected application form." in inbox_source
    assert ".attachment-requested-testing-stack" in inbox_styles
    assert ".attachment-additional-information-block" in inbox_styles


def test_task090_intake_workflow_structure_extraction() -> None:
    """TASK_090 keeps Intake page thin and moves display logic into feature files."""
    page_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    feature_source = intake_feature_source()

    for term in [
        "IntakeSourcePanel",
        "AttachmentList",
        "buildAttachmentViewModels",
        "visibleIntakeAttachments",
    ]:
        assert term in page_source

    assert "AttachmentPreviewPanel" not in page_source
    assert "selectedIntakeAsset" not in page_source

    for term in [
        "export function visibleIntakeAttachments",
        "export function buildAttachmentViewModels",
        "export function senderEmailText",
        "export function mailDateText",
        "function AttachmentPreview",
        "function DocxApplicationPreview",
        "function PreviewTableSection",
    ]:
        assert term in feature_source

    for removed_term in [
        "function AttachmentPreview(",
        "function senderEmailText(",
        "function mailDateText(",
        "function assetKind(",
        "function formatBytes(",
        "attachments-heading",
        "email-info-list",
    ]:
        assert removed_term not in page_source


def test_task091_intake_precheck_typography_uses_shared_ui_vocabulary() -> None:
    """TASK_091 keeps Intake and Precheck title/action typography maintainable."""
    styles_source = (FRONTEND_ROOT / "src" / "styles.css").read_text(
        encoding="utf-8"
    )
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8") + intake_feature_source()
    precheck_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8") + precheck_feature_source()

    for token in [
        "--font-size-panel-title",
        "--font-size-preview-title",
        "--font-size-section-title",
        "--font-size-label",
        "--font-size-data",
        ".ui-panel-title",
        ".ui-preview-title",
        ".ui-section-title",
        ".ui-primary-action",
        ".ui-secondary-action",
        ".ui-compact-action",
    ]:
        assert token in styles_source

    for term in [
        'className="ui-panel-title">Import source',
        'className="ui-panel-title">Email information',
        'className="ui-panel-title">Attachments',
        'className="ui-preview-title"',
        'className="ui-section-title">{table.title}',
        "secondary-action ui-secondary-action",
        "continue-action ui-primary-action",
    ]:
        if term == "continue-action ui-primary-action" and "NewProjectApplicationEditor" in inbox_source:
            assert "new-project-primary-action ui-primary-action" in inbox_source + (
                FRONTEND_ROOT / "src" / "features" / "new-project" / "NewProjectApplicationEditor.tsx"
            ).read_text(encoding="utf-8")
            continue
        assert term in inbox_source

    for term in [
        'className="ui-panel-title">Source traceability',
        'className="ui-panel-title">Key Information Edit & Confirm',
        'className="ui-section-title">Test Sample Information',
        'className="ui-section-title">Description of Requested Testing',
        'className="ui-section-title">Additional Information',
        "sample-add-button ui-compact-action",
        "requested-testing-add-button ui-compact-action",
        "precheck-confirm-button ui-primary-action",
        "Save draft and exit",
    ]:
        assert term in precheck_source


def test_task092_intake_attachment_download_has_url_helper() -> None:
    """TASK_092 adds intakeAssetDownloadUrl to the API client."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )

    assert "intakeAssetDownloadUrl" in client_source
    assert "/download" in client_source
    assert "intakeAssetDownloadUrl(" in client_source
    assert "${API_BASE}/api/intake-assets/" in client_source


def test_task092_intake_attachment_download_uses_download_link() -> None:
    """TASK_092 replaces disabled Download button with a working blob download."""
    preview_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "AttachmentPreviewPanel.tsx"
    ).read_text(encoding="utf-8")

    for term in [
        "downloadIntakeAsset",
        "className=\"secondary-action ui-secondary-action\"",
        "handleDownload()",
        "createObjectURL",
        "revokeObjectURL",
        "document.body.append",
    ]:
        assert term in preview_source
    assert "intakeAssetDownloadUrl" not in preview_source
    assert "toolbar-button toolbar-icon-button" not in preview_source
    assert "disabled" not in preview_source
    assert 'AttachmentPreviewActions({ assetId' in preview_source


def test_task092_intake_attachment_download_action_accepts_metadata() -> None:
    """TASK_092 passes assetId and originalName to AttachmentPreviewActions."""
    preview_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "AttachmentPreviewPanel.tsx"
    ).read_text(encoding="utf-8")

    assert "assetId={preview.metadata.asset_id}" in preview_source
    assert "originalName={preview.metadata.original_name}" in preview_source
    assert "downloadIntakeAsset" in (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )


def test_task092_intake_inbox_css_supports_anchor_as_secondary_action() -> None:
    """TASK_092 secondary-action CSS supports <a> as a button-like element."""
    inbox_styles = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
    )

    assert "display: inline-grid" in inbox_styles
    assert "text-decoration: none" in inbox_styles


def test_task092_preview_header_and_non_preview_download_availability() -> None:
    """TASK_092 fix: Download is available in loading/error/no-preview branches."""
    preview_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "AttachmentPreviewPanel.tsx"
    ).read_text(encoding="utf-8")

    assert "function PreviewHeader" in preview_source
    assert "preview-loading-outer" in preview_source
    assert "preview-error-outer" in preview_source
    assert "preview-no-preview-outer" in preview_source
    assert "<PreviewHeader asset={asset} />" in preview_source
    assert "AttachmentPreviewActions assetId={asset.asset_id}" in preview_source
    assert "originalName={asset.original_name}" in preview_source


def test_task093_email_package_missing_form_upload_continuation() -> None:
    """TASK_093 keeps supplemental form upload attached to the current email package."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    inbox_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8") + intake_feature_source()
    source_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "IntakeSourcePanel.tsx"
    ).read_text(encoding="utf-8")

    for term in [
        "uploadEmailPackageApplicationForm",
        "/application-form",
        "Promise<SelectedApplicationForm>",
    ]:
        assert term in client_source

    if "NewProjectApplicationEditor" in inbox_source:
        assert "uploadEmailPackageApplicationForm(packageImport.package_id, file)" in inbox_source
        return

    for term in [
        'packageImport?.source_type === "outlook_msg"',
        "uploadEmailPackageApplicationForm(packageImport.package_id, file)",
        "getIntakePackageDetail(packageImport.package_id)",
        "packageDetailToImport",
        "No application form found in this email. Upload the application form to continue with this email package.",
        "selectedPrecheckCaseId: selection.case_id",
    ]:
        assert term in inbox_source

    assert "disabled={importing}" in source_panel_source


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

    if "Project workbench boundary" in workbench_source:
        for term in [
            "Evidence placement",
            "Preview evidence placement",
            "Place evidence",
            "Project folder is not recorded for this project.",
        ]:
            assert term in workbench_source
    else:
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


def test_task096_creation_draft_lifecycle_frontend_actions() -> None:
    """TASK_096 exposes save/discard creation draft actions with operator copy."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    intake_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    precheck_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")

    for term in [
        "ProjectCreationDraftLifecycle",
        "saveProjectCreationDraft",
        "discardUnsavedProjectCreationDraft",
        "/draft/save",
        "/draft/discard",
    ]:
        assert term in client_source

    for source in [intake_source, precheck_source]:
        if "NewProjectApplicationEditor" in source:
            assert "Cancel and remove draft" not in source
            assert "discardUnsavedProjectCreationDraft" not in source
            assert "Draft changes save automatically while you edit this package." in source
            continue
        assert "Save draft and exit" in source
        assert "Exit without saving" in source
        assert "Confirm discard" in source
        assert "ConnLab imported copies" in source or "ConnLab's imported copies" in source


def test_task097_drafts_surface_uses_continue_not_open() -> None:
    """TASK_097 keeps saved drafts separate from confirmed project Open actions."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    project_list_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectListPage.tsx"
    ).read_text(encoding="utf-8")

    for term in [
        "ProjectCreationDraft",
        "listProjectCreationDrafts",
        "discardSavedProjectCreationDraft",
        "/api/project-creation-drafts",
    ]:
        assert term in client_source

    for term in [
        "Drafts / In Progress",
        "Continue",
        "Discard",
        "saved New Project",
        "Drafts are separate from confirmed Projects",
    ]:
        assert term in project_list_source

    assert "onOpenProject" in project_list_source
    assert "Open" in project_list_source
    assert "onContinueDraft" in project_list_source
    assert "getIntakePackageDetail" in app_source


def test_task098_precheck_confirmed_application_editing_boundary() -> None:
    """TASK_098 makes Precheck the confirmed application-data editing surface."""
    case_review_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeCaseReviewPage.tsx"
    ).read_text(encoding="utf-8")
    source_check = (
        FRONTEND_ROOT / "src" / "features" / "precheck" / "PrecheckSourceCheck.tsx"
    ).read_text(encoding="utf-8")
    contract = (FRONTEND_ROOT.parent / "docs" / "intake_precheck_field_contract.md").read_text(
        encoding="utf-8"
    )

    assert "Back to Intake" not in case_review_source
    assert "onBack" not in case_review_source
    assert "Save draft and exit" in case_review_source
    assert "Exit without saving" in case_review_source

    for term in [
        "Source traceability",
        "Confirmed application data is edited below",
        "source file remains attached for traceability",
        "Project creation uses the corrected Precheck values",
    ]:
        assert term in source_check

    for term in [
        "Intake is source selection only",
        "Precheck is the confirmed application-data editing surface",
        "Project creation uses corrected Precheck draft values",
        "does not support switching to another application form",
    ]:
        assert term in contract


def test_task102_new_project_single_page_editor_shell() -> None:
    """TASK_102 keeps source, attachments, and application editor on one page."""
    page_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    new_project_source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((FRONTEND_ROOT / "src" / "features" / "new-project").glob("*.tsx"))
        + sorted((FRONTEND_ROOT / "src" / "features" / "new-project").glob("*.ts"))
    )
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")

    for term in [
        "ensureNewProjectApplicationDraft",
        "getIntakeCaseReview",
        "updateIntakeCaseReviewFields",
        "NewProjectApplicationEditor",
        "AttachmentList",
    ]:
        assert term in page_source

    for term in [
        "Application information",
        "missingRequiredByField",
        "missingSampleCells",
        "Apply LTR Number and Create Folder",
        "required fields remaining",
    ]:
        assert term in new_project_source

    assert "/application-draft" in client_source
    assert 'navigate("/intake")' in app_source
    assert "Continue to Precheck" not in page_source
    assert "AttachmentPreviewPanel" not in page_source
    assert "Draft saved automatically" not in page_source
    assert "No application form imported. Fill SECTION 1 manually." not in new_project_source
    assert "Import application form (next)" not in page_source


def test_task103_application_form_import_is_explicit_and_confirmed() -> None:
    """TASK_103 separates attachment open from explicit application import."""
    page_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    attachment_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "AttachmentList.tsx"
    ).read_text(encoding="utf-8")
    source_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "IntakeSourcePanel.tsx"
    ).read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )

    for term in [
        "selectIntakeApplicationForm",
        "selectIntakeApplicationForm(packageImport.package_id, asset.asset_id, true)",
        "setImportMessage(asset.original_name)",
        "downloadIntakeAsset",
    ]:
        assert term in page_source

    for term in [
        "onDoubleClick",
        "onOpen?.(attachment)",
        "attachment.word && onImport",
        "attachment-import-button",
        "Import",
    ]:
        assert term in attachment_source

    assert "Import application form (next)" not in source_panel_source
    assert "replace_existing" in client_source
    assert "body: JSON.stringify({ asset_id: assetId, replace_existing: replaceExisting })" in client_source
    assert "downloadIntakeAsset" in client_source
    assert "requestBlob" in client_source


def test_task103_new_project_page_chrome_is_minimal() -> None:
    """TASK_103 follow-up trims the New Project page chrome and side preview."""
    page_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    source_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "IntakeSourcePanel.tsx"
    ).read_text(encoding="utf-8")
    editor_source = (
        FRONTEND_ROOT / "src" / "features" / "new-project" / "NewProjectApplicationEditor.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
    )

    for removed_term in [
        "New Project",
        "Confirm request source, attachments, and SECTION 1 application information on one page.",
        "AttachmentPreviewPanel",
        "Draft saved automatically",
        "No application form imported. Fill SECTION 1 manually.",
        "Import application form (next)",
        "new-project-single-heading",
        "new-project-autosave-state",
    ]:
        assert removed_term not in page_source + source_panel_source + editor_source + styles_source

    for term in [
        "Application information",
        "new-project-single-grid",
        "new-project-editor-panel",
        "new-project-editor-heading",
    ]:
        assert term in page_source + editor_source + styles_source


def test_task134_new_project_uses_ltr_workbook_commit_before_folder() -> None:
    """TASK_134 wires external LTR workbook commit into New Project completion."""
    page_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    setup_source = (
        FRONTEND_ROOT / "src" / "features" / "new-project" / "NewProjectSetupConfirmationPanel.tsx"
    ).read_text(encoding="utf-8")
    editor_source = (
        FRONTEND_ROOT / "src" / "features" / "new-project" / "NewProjectApplicationEditor.tsx"
    ).read_text(encoding="utf-8")
    hook_source = (
        FRONTEND_ROOT / "src" / "features" / "new-project" / "useNewProjectCompletion.ts"
    ).read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )

    for term in [
        "commitLtrWorkbookWrite",
        "/ltr-workbook/write-commit",
        "confirmIntakeCase(activeCase.case_id)",
        "workbookWriteAcknowledged",
        "preview_acknowledged: setupValues.workbookWriteAcknowledged",
        "LTR workbook",
        "Backup:",
    ]:
        assert term in page_source + setup_source + editor_source + hook_source + client_source

    assert hook_source.index("confirmIntakeCase(activeCase.case_id)") < hook_source.index(
        "const workbookCommit = await commitLtrWorkbookWrite"
    )
    assert hook_source.index("const workbookCommit = await commitLtrWorkbookWrite") < hook_source.index(
        "completeNewProject(activeCase.case_id"
    )


def test_task099_new_project_editor_exposes_ltr_registered_freeze_state() -> None:
    """TASK_099 freezes normal New Project editor saves after LTR registration."""
    page_source = (FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx").read_text(
        encoding="utf-8"
    )
    editor_source = (
        FRONTEND_ROOT / "src" / "features" / "new-project" / "NewProjectApplicationEditor.tsx"
    ).read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    styles_source = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
    )

    assert "base_editing_frozen" in client_source
    assert "frozen_field_keys" in client_source
    assert "frozen_reason" in client_source
    assert "activeCase.base_editing_frozen" in page_source
    assert "LTR registered. Base application fields require revise/exception handling." in editor_source
    assert "new-project-frozen-notice" in editor_source
    assert ".new-project-frozen-notice" in styles_source


def test_task100_workbench_keeps_post_creation_boundary() -> None:
    """TASK_100 keeps Workbench focused on confirmed project state and evidence management."""
    project_list_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectListPage.tsx"
    ).read_text(encoding="utf-8")
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for term in ["Open", "onOpenProject", "Continue", "onContinueDraft"]:
        assert term in project_list_source

    for term in [
        "Project workbench boundary",
        "previewEvidencePlacement",
        "placeEvidence",
        "Project folder is not recorded for this project.",
    ]:
        assert term in workbench_source

    for removed_term in [
        "uploadApplicationForm",
        "runPrecheck",
        "commitLtrLocally",
        "generateFolder",
        "ApplicationFormActionPanel",
        "LtrActionPanel",
        "FolderActionPanel",
    ]:
        assert removed_term not in workbench_source

    assert ".project-workbench-status" in styles_source
