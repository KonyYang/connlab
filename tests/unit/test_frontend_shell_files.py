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
        "src/pages/SettingsPage.tsx",
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
        "src/features/project-workbench/ProjectFolderCreationPanel.tsx",
        "src/features/project-workbench/ProjectWorkbenchDocumentStatusPanel.tsx",
        "src/features/project-workbench/ProjectWorkbenchMatrixReviewPanel.tsx",
        "src/features/project-workbench/ProjectWorkbenchMatrixStarter.tsx",
        "src/features/project-workbench/ProjectWorkbenchMatrixAuthorityBar.tsx",
        "src/features/project-workbench/ProjectWorkbenchMatrixOverview.tsx",
        "src/features/project-workbench/ProjectWorkbenchMatrixInspector.tsx",
        "src/features/project-workbench/projectWorkbenchMatrixHelpers.ts",
        "src/features/project-workbench/projectWorkbenchVersionSelectors.ts",
        "src/features/settings/SettingsExternalResourcesPanel.tsx",
        "src/features/settings/settingsResourceConfig.ts",
        "src/features/settings/settingsSelectors.ts",
        "src/components/precheck/PrecheckSummary.tsx",
        "src/components/precheck/PrecheckIssueCard.tsx",
        "src/components/precheck/IssueSeverityBadge.tsx",
        "src/styles.css",
        "src/project-dashboard.css",
        "src/workbench.css",
        "src/settings.css",
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
    workbench_model_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "useProjectWorkbenchModel.ts"
    ).read_text(encoding="utf-8")

    assert 'pathname === "/projects"' in app_source
    assert "/projects/" in app_source
    assert "listProjects" in list_page_source
    assert "getProject" in workbench_model_source
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
    """Workbench keeps intake/LTR creation out while exposing folder workspace setup."""
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    project_folder_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectFolderCreationPanel.tsx"
    ).read_text(encoding="utf-8")

    if "Project workbench boundary" in workbench_source or "runtime-console-shell" in layout_source:
        for blocked_term in [
            "uploadApplicationForm",
            "runPrecheck",
            "getLtrReadiness",
            "previewLtrRegistration",
            "commitLtrLocally",
            "resolvePrecheckIssue",
            "ApplicationFormActionPanel",
            "LtrActionPanel",
            "FolderActionPanel",
        ]:
            assert blocked_term not in workbench_source
        for term in [
            "ProjectLookupPanel",
            "ProjectFolderCreationPanel",
            "previewEvidencePlacement",
            "placeEvidence",
        ]:
            assert term not in layout_source
        assert "previewFolder" in project_folder_source
        assert "generateFolder" in project_folder_source
        assert "getLatestProjectFolder" in project_folder_source
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
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
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
    assert "latestLtr" in layout_source
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


def test_task149_settings_external_resources_ui_is_wired() -> None:
    """TASK_149 exposes registry-backed external resources through Settings UI."""
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    sidebar_source = (
        FRONTEND_ROOT / "src" / "components" / "layout" / "Sidebar.tsx"
    ).read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    page_source = (
        FRONTEND_ROOT / "src" / "pages" / "SettingsPage.tsx"
    ).read_text(encoding="utf-8")
    panel_source = (
        FRONTEND_ROOT / "src" / "features" / "settings" / "SettingsExternalResourcesPanel.tsx"
    ).read_text(encoding="utf-8")
    config_source = (
        FRONTEND_ROOT / "src" / "features" / "settings" / "settingsResourceConfig.ts"
    ).read_text(encoding="utf-8")
    selectors_source = (
        FRONTEND_ROOT / "src" / "features" / "settings" / "settingsSelectors.ts"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "settings.css").read_text(
        encoding="utf-8"
    )

    assert 'pathname === "/settings"' in app_source
    assert "SettingsPage" in app_source
    assert '{ label: "Settings", route: "settings", hint: null, icon: "settings" }' in sidebar_source
    assert '"/api/external-resources"' in client_source
    assert "listExternalResources" in client_source
    assert "saveExternalResource" in client_source
    assert "validateExternalResource" in client_source
    assert "fetch(" not in page_source
    assert "fetch(" not in panel_source
    assert "project_output_root" in config_source
    assert "Project output root" in config_source
    assert "Shared resources" in config_source
    assert "Local machine paths" in config_source
    assert "LTR workbook backup directory" in config_source
    assert "Configured by local TOML or environment settings" in config_source
    assert "Use local paths during development" in panel_source
    assert "Browse for" in panel_source
    assert "Desktop path browsing will open a Windows" in panel_source
    assert "type=\"file\"" not in panel_source
    assert "webkitdirectory" not in panel_source
    assert "buildSettingsResourceRows" in selectors_source
    assert ".settings-resource-row" in styles_source
    assert ".settings-path-control" in styles_source
    assert ".settings-browse-hint" in styles_source
    assert ".settings-status-success" in styles_source


def test_task150_workbench_folder_uses_configured_resources() -> None:
    """TASK_150 removes normal raw path entry and resolves folder resources from Settings."""
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    model_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "useProjectWorkbenchModel.ts"
    ).read_text(encoding="utf-8")
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    folder_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectFolderCreationPanel.tsx"
    ).read_text(encoding="utf-8")
    selector_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "projectFolderResourceSelectors.ts"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "useProjectWorkbenchModel" in workbench_source
    assert "listExternalResources" in model_source
    assert "configuredFolderResources" in model_source
    assert "ProjectFolderCreationPanel" not in layout_source
    assert "configuredTemplate" in folder_panel_source
    assert "configuredOutputRoot" in folder_panel_source
    assert "Project folder template" in folder_panel_source
    assert "Project output root" in folder_panel_source
    assert "Configure Project folder template in Settings" in folder_panel_source
    assert "Configure Project output root in Settings" in folder_panel_source
    assert "Project folder template path" not in folder_panel_source
    assert "Project folder target root" not in folder_panel_source
    assert "configured-resource-grid" in folder_panel_source
    assert "configuredFolderResources" in selector_source
    assert "resourceBlockedReason" in selector_source
    assert ".configured-resource-grid" in styles_source
    assert ".configured-resource-card" in styles_source


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
    assert "showCancelled" in list_page_source
    assert "visibleRowsForScope" in list_page_source
    assert "cancelledRowCount" in list_page_source
    assert "Show cancelled" in list_page_source
    assert "cancelled project" in list_page_source
    assert "No active projects in this view" in list_page_source
    assert 'Enable "Show cancelled" to inspect cancelled projects.' in list_page_source
    assert ".project-table" in styles_source
    assert ".project-metric-card" in styles_source
    assert ".progress-cell" in styles_source
    assert ".registry-tools" in styles_source
    assert ".toolbar-button" in styles_source
    assert ".registry-scope-toggle" in styles_source
    assert ".registry-scope-note" in styles_source
    assert "@media (min-width: 761px) and (max-width: 1366px)" in styles_source


def test_project_workbench_uses_sequential_stepper() -> None:
    """Workbench keeps either legacy stepper or TASK_100 post-creation status surface."""
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
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

    if "runtime-console-shell" in layout_source:
        assert "WorkflowStepper" not in workbench_source
        assert "NextActionPanel" not in workbench_source
        assert "Runtime Console" in layout_source
        assert ".runtime-console-shell" in styles_source
        return

    if "Project workbench boundary" in workbench_source or "Project workbench boundary" in layout_source:
        assert "WorkflowStepper" not in workbench_source
        assert "NextActionPanel" not in workbench_source
        assert "project-workbench-status" in layout_source or "project-workbench-status" in workbench_source
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

    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")

    if "runtime-console-shell" in layout_source:
        assert "PrecheckSummary" not in workbench_source
        assert "PrecheckIssueCard" not in workbench_source
        assert "resolvePrecheckIssue" not in workbench_source
    elif "Project workbench boundary" in workbench_source:
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
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    if "runtime-console-shell" in layout_source:
        assert "ApplicationFormActionPanel" not in workbench_source
        assert "LtrActionPanel" not in workbench_source
        assert "FolderActionPanel" not in workbench_source
    elif "Project workbench boundary" in workbench_source or "Project workbench boundary" in layout_source:
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
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    if "Project workbench boundary" not in workbench_source and "runtime-console-shell" not in layout_source:
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
        assert "Apply LTR Number" in inbox_source + "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((FRONTEND_ROOT / "src" / "features" / "new-project").glob("*.tsx"))
        )
        assert "Apply LTR Number and Create Folder" not in inbox_source
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
        assert "Apply LTR Number" in "\n".join(
            path.read_text(encoding="utf-8")
            for path in sorted((FRONTEND_ROOT / "src" / "features" / "new-project").glob("*.tsx"))
        )
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
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    model_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "useProjectWorkbenchModel.ts"
    ).read_text(encoding="utf-8")
    evidence_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchEvidencePanel.tsx"
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
        assert term in model_source or term in evidence_panel_source or term in workbench_source

    if "Project workbench boundary" in workbench_source or "Project workbench boundary" in evidence_panel_source:
        for term in [
            "Evidence placement",
            "Preview evidence placement",
            "Place evidence",
            "Project folder is not recorded for this project.",
        ]:
            assert term in workbench_source or term in evidence_panel_source
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
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
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

    assert "ProjectLookupPanel" not in layout_source

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


def test_projects_page_removes_drafts_surface_after_task163() -> None:
    """Projects page is project-only; draft management is no longer rendered here."""
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

    for term in ["Drafts / In Progress", "Drafts are separate from confirmed Projects"]:
        assert term not in project_list_source

    assert "onOpenProject" in project_list_source
    assert "Open" in project_list_source
    assert "onContinueDraft" not in project_list_source
    assert "getIntakePackageDetail" not in app_source


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
    sample_table_source = (
        FRONTEND_ROOT / "src" / "features" / "precheck" / "PrecheckSampleTable.tsx"
    ).read_text(encoding="utf-8")
    required_state_source = (
        FRONTEND_ROOT / "src" / "features" / "new-project" / "newProjectRequiredState.ts"
    ).read_text(encoding="utf-8")
    inbox_styles = (FRONTEND_ROOT / "src" / "intake-inbox.css").read_text(
        encoding="utf-8"
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
        "Apply LTR Number",
        "NewProjectCompletionDock",
        "isValidSpecifiedLtrInput",
        "required fields remaining",
    ]:
        assert term in new_project_source

    for term in [
        "projectSetupPayload",
        "setupValuesFromProjectSetup",
        "setupValuesRef",
        "project_setup: projectSetupPayload(setupValuesRef.current)",
    ]:
        assert term in page_source

    for term in [
        "sample-cell-required-missing",
    ]:
        assert term in sample_table_source

    for term in [
        "rowsWithAnyContent",
        "rowHasAnySampleValue",
        "`${rowIndex}:product_name`",
        "`${rowIndex}:quantity`",
    ]:
        assert term in required_state_source

    for term in [
        ".sample-cell-required-missing",
        "box-shadow: inset 0 0 0 1px rgba(194, 65, 58, 0.44)",
    ]:
        assert term in inbox_styles

    assert "/application-draft" in client_source
    assert "project_setup?: Record<string, unknown>" in client_source
    assert "project_setup?: Record<string, string | null>" in client_source
    assert 'navigate("/intake")' in app_source
    assert "Continue to Precheck" not in page_source
    assert "AttachmentPreviewPanel" not in page_source
    assert "Draft saved automatically" not in page_source
    assert "Draft changes save automatically while you edit this package." not in page_source
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
    selectors_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "intakeSelectors.ts"
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
        "applySelectedDraft(selection, asset.original_name)",
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
    assert "resolution_action: resolution?.action ?? null" in client_source
    assert "downloadIntakeAsset" in client_source
    assert "requestBlob" in client_source


def test_task142_draft_duplicate_resolution_is_business_readable() -> None:
    """TASK_142 resolves duplicate drafts at draft identity boundaries."""
    page_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    source_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "IntakeSourcePanel.tsx"
    ).read_text(encoding="utf-8")
    attachment_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "AttachmentList.tsx"
    ).read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )

    assert "DraftDuplicateCheck" in client_source
    assert "exact_existing_application_draft" in client_source
    assert "exact_existing_no_form_draft" in client_source
    assert "Duplicate draft detected." in client_source
    assert "draftDuplicateConflictFromError" in page_source
    assert "ensureNewProjectApplicationDraft(duplicateDraft.packageId, resolution)" in page_source
    assert "selectIntakeApplicationForm(" in page_source
    assert "This application draft already exists" in attachment_source
    assert "This application draft already exists" not in source_panel_source
    assert "This email already has a no-form draft" not in source_panel_source + attachment_source
    assert "All draft identity fields match" not in source_panel_source + attachment_source
    assert "Create separate draft" not in source_panel_source + attachment_source
    assert "Load existing" in attachment_source
    assert "Reinitialize" in attachment_source
    assert "Open existing draft" not in attachment_source
    assert "Replace existing draft" not in attachment_source
    assert "JSON.stringify(error)" not in page_source


def test_task143_email_import_waits_for_application_form_selection() -> None:
    """TASK_143 keeps duplicate checks at the selected application-form boundary."""
    page_source = (
        FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx"
    ).read_text(encoding="utf-8")
    source_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "IntakeSourcePanel.tsx"
    ).read_text(encoding="utf-8")
    attachment_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "AttachmentList.tsx"
    ).read_text(encoding="utf-8")
    selectors_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "intakeSelectors.ts"
    ).read_text(encoding="utf-8")

    assert "defaultApplicationFormAsset" in page_source
    assert "selectDefaultApplicationForm" in page_source
    assert "visibleIntakeAttachments(imported)" in page_source
    assert "compareAttachments" in selectors_source
    assert "attachmentKindRank" in selectors_source
    assert "Source file" in source_panel_source
    assert "source_original_name" in source_panel_source
    assert "email-source-filename" in source_panel_source
    assert "source_stored_path" not in source_panel_source
    assert "selectedAssetId: firstApplicationForm?.asset_id ?? null" in page_source
    assert "loadSelectedReview" in page_source
    assert "Unable to load the selected application draft." in page_source
    assert 'packageImport.source_type === "outlook_msg"' in page_source
    assert "Unable to select the first application form." in page_source
    assert "applySelectedDraft(selection, asset.original_name)" in page_source
    assert "applySelectedDraft(selection, selectedDefaultFormAsset.original_name)" in page_source
    assert "applySelectedDraft(selection, duplicateDraft.asset.original_name)" in page_source
    assert page_source.count("setDuplicateDraft(null)") >= 6
    assert "duplicateDraft={duplicateDraft?.check ?? null}" in page_source
    assert "onDuplicateAction={(action) => void handleResolveDuplicateDraft(action)}" in page_source
    assert "This application draft already exists" not in source_panel_source
    assert "This application draft already exists" in attachment_source
    assert attachment_source.index("Reinitialize") < attachment_source.index("Load existing")
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in (
        FRONTEND_ROOT / "src" / "intake-inbox.css"
    ).read_text(encoding="utf-8")
    assert "email-duplicate-facts" not in attachment_source


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


def test_task146_new_project_applies_ltr_before_project_handoff() -> None:
    """TASK_146 keeps New Project completion scoped to LTR application."""
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
    dock_source = (
        FRONTEND_ROOT / "src" / "features" / "new-project" / "NewProjectCompletionDock.tsx"
    ).read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )

    for term in [
        "commitLtrWorkbookWrite",
        "/ltr-workbook/write-commit",
        "LTR workbook",
        "Backup:",
        "NewProjectCompletionDock",
        "isValidSpecifiedLtrInput",
        "Applying LTR number...",
        "Apply LTR Number",
        "DL-YYYY-MM-NNN or A1",
        "Valid specified LTR input",
        "Suffix only: A, AA, A1, or SAMPLE2",
        "Suffixes must start with a letter",
        "DL-2026-05-001123 are invalid",
    ]:
        assert term in page_source + setup_source + editor_source + hook_source + dock_source + client_source

    assert "workbook_write_acknowledged" not in page_source + setup_source
    assert "I confirm ConnLab may write this LTR registration" not in setup_source
    assert "Auto assign next LTR number" not in setup_source
    assert "Use specified LTR number" not in setup_source
    assert "Apply LTR Number and Create Folder" not in dock_source
    assert "Writing LTR and creating folder" not in dock_source
    assert "confirmIntakeCase(activeCase.case_id)" not in hook_source
    assert "commitLtrWorkbookWrite(projectId" not in hook_source
    assert "preview_acknowledged: true" not in hook_source
    assert "export type CompleteNewProject = {" in client_source
    assert "project_id: string;" in client_source
    assert "project_status: string;" in client_source
    assert "ltr_number: string;" in client_source

    assert hook_source.count("completeNewProject(activeCase.case_id") == 1


def test_new_project_duplicate_scope_is_draft_only() -> None:
    """Confirmed Project/LTR duplicate reminder branch is removed from New Project."""
    attachment_source = (
        FRONTEND_ROOT / "src" / "features" / "intake" / "AttachmentList.tsx"
    ).read_text(encoding="utf-8")
    page_source = (FRONTEND_ROOT / "src" / "pages" / "IntakeInboxPage.tsx").read_text(
        encoding="utf-8"
    )
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )

    assert "existing_confirmed_project_ltr" not in client_source + attachment_source
    assert "This application already has a project" not in attachment_source
    assert "Open project" not in attachment_source
    assert "onOpenConfirmedProject" not in page_source + attachment_source


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
    """Workbench stays bounded while TASK_148 adds folder creation to the workspace."""
    project_list_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectListPage.tsx"
    ).read_text(encoding="utf-8")
    workbench_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    model_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "useProjectWorkbenchModel.ts"
    ).read_text(encoding="utf-8")
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )
    project_folder_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectFolderCreationPanel.tsx"
    ).read_text(encoding="utf-8")

    for term in ["Open", "onOpenProject"]:
        assert term in project_list_source
    for term in ["Continue", "onContinueDraft"]:
        assert term not in project_list_source

    assert (
        "Project workbench boundary" in workbench_source
        or "Project workbench boundary" in layout_source
        or "runtime-console-shell" in layout_source
    )
    for term in ["previewEvidencePlacement", "placeEvidence"]:
        assert term in model_source or term in workbench_source
    for term in ["ProjectFolderCreationPanel"]:
        assert term not in layout_source + workbench_source

    for removed_term in [
        "uploadApplicationForm",
        "runPrecheck",
        "commitLtrLocally",
        "ApplicationFormActionPanel",
        "LtrActionPanel",
        "FolderActionPanel",
    ]:
        assert removed_term not in workbench_source

    assert "previewFolder" in project_folder_source
    assert "generateFolder" in project_folder_source
    assert "Create project folder" in project_folder_source
    assert ".project-workbench-status" in styles_source or ".runtime-console-shell" in styles_source
    assert ".project-folder-workbench-panel" in styles_source


def test_task186_workbench_matrix_review_surface_is_feature_wired() -> None:
    """TASK_186 adds Matrix-first review surface from existing test-plan draft APIs."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    model_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "useProjectWorkbenchModel.ts"
    ).read_text(encoding="utf-8")
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    matrix_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixReviewPanel.tsx"
    ).read_text(encoding="utf-8")
    matrix_inspector_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixInspector.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "/api/projects/" in client_source
    assert "/test-plan/drafts" in client_source
    assert "listProjectTestPlanDrafts" in client_source
    assert "getProjectTestPlanDraft" in client_source

    assert "listProjectTestPlanDrafts" in model_source
    assert "getProjectTestPlanDraft" in model_source
    assert "matrixDraft" in model_source
    assert "matrixDraftLoading" in model_source
    assert "matrixDraftError" in model_source

    if "runtime-console-shell" in layout_source:
        assert "ProjectWorkbenchMatrixOverview" in layout_source
        assert "runtimeProjectionSnapshot" in layout_source
        assert "matrixDraftError" in layout_source
        assert "matrixDraftLoading" in layout_source
    else:
        assert "ProjectWorkbenchMatrixReviewPanel" in layout_source
        assert "draft={matrixDraft}" in layout_source
        assert "error={matrixDraftError}" in layout_source
        assert "loading={matrixDraftLoading}" in layout_source

    assert "Matrix review" in matrix_panel_source
    if "ProjectWorkbenchMatrixStarter" in matrix_panel_source:
        assert "onPreviewStarterFromPath" in matrix_panel_source
        assert "onCreateManualDraft" in matrix_panel_source
    else:
        assert "No active Project test-plan draft is available yet." in matrix_panel_source
    assert "Draft warnings" in matrix_panel_source

    assert ".matrix-review-panel" in styles_source or ".runtime-console-main" in styles_source
    assert ".matrix-review-summary" in styles_source or ".runtime-console-summary" in styles_source
    assert ".matrix-review-step-list" in styles_source or ".matrix-runtime-token-list" in styles_source


def test_task187_workbench_document_pipeline_autofill_is_feature_wired() -> None:
    """TASK_187 auto-fills approval-package inputs from Workbench context with manual override."""
    model_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "useProjectWorkbenchModel.ts"
    ).read_text(encoding="utf-8")
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    panel_source = (
        FRONTEND_ROOT / "src" / "components" / "workflow" / "ApprovalPackagePanel.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "approvalInputSources" in model_source
    assert "deriveApprovalInputAutofill" in model_source
    assert "mergeApprovalInput" in model_source
    assert "getLatestProjectFolder" in model_source
    assert "setApprovalInputSources" in model_source
    assert "manual" in model_source
    assert "auto" in model_source

    assert "inputSources={approvalInputSources}" not in layout_source
    assert "ApprovalInputSources" in panel_source
    assert "Evidence source paths (" in panel_source
    assert "Completed application form (" in panel_source
    assert ".approval-input-field" in styles_source


def test_task188_workbench_version_and_stale_status_is_feature_wired() -> None:
    """TASK_188 reads persisted output-status summary and renders downstream status."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    model_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "useProjectWorkbenchModel.ts"
    ).read_text(encoding="utf-8")
    selector_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "projectWorkbenchVersionSelectors.ts"
    ).read_text(encoding="utf-8")
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    matrix_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixReviewPanel.tsx"
    ).read_text(encoding="utf-8")
    status_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchDocumentStatusPanel.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "deriveWorkbenchVersionStatus" in model_source
    assert "getProjectOutputStatusSummary" in model_source
    assert "/output-records/status" in client_source
    assert "trackedDraftVersion" in model_source
    assert "versionStatus" in model_source

    assert "WorkbenchDocumentFreshness" in selector_source
    assert "current" in selector_source
    assert "stale" in selector_source
    assert "missing" in selector_source
    assert "manual" in selector_source
    assert "failed" in selector_source

    assert "ProjectWorkbenchDocumentStatusPanel" not in layout_source
    assert "status={versionStatus}" not in layout_source
    assert "versionStatus={versionStatus}" in layout_source or "RuntimeAttentionSurface" in layout_source
    assert "Downstream outputs are stale" in matrix_panel_source
    assert "Derived outputs" in status_panel_source or "Downstream status" in status_panel_source
    assert ".workbench-document-status-panel" in styles_source
    assert ".workbench-status-stale" in styles_source


def test_task189_workbench_matrix_edit_and_confirm_is_feature_wired() -> None:
    """TASK_189 adds Matrix group/step edit, validation, and confirm wiring."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    model_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "useProjectWorkbenchModel.ts"
    ).read_text(encoding="utf-8")
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    matrix_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixReviewPanel.tsx"
    ).read_text(encoding="utf-8")
    matrix_inspector_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixInspector.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "updateProjectTestPlanMatrixDraft" in client_source
    assert "validateProjectTestPlanMatrixDraft" in client_source
    assert "confirmProjectTestPlanMatrixDraft" in client_source
    assert "/matrix/validate" in client_source
    assert "/matrix/confirm" in client_source

    assert "matrixDraftEditableGroups" in model_source
    assert "matrixAuthorityDraft" in model_source
    assert "matrixCandidateDraft" in model_source
    assert "matrixValidation" in model_source
    assert "onSaveMatrixDraft" in model_source
    assert "onValidateMatrixDraft" in model_source
    assert "onConfirmMatrixDraft" in model_source

    if "runtime-console-shell" in layout_source:
        assert "editableGroups={matrixDraftEditableGroups}" not in layout_source
        assert "onSaveDraft={onSaveMatrixDraft}" not in layout_source
        assert "onValidateDraft={onValidateMatrixDraft}" not in layout_source
        assert "onConfirmDraft={onConfirmMatrixDraft}" not in layout_source
    else:
        assert "editableGroups={matrixDraftEditableGroups}" in layout_source
        assert "onSaveDraft={onSaveMatrixDraft}" in layout_source
        assert "onValidateDraft={onValidateMatrixDraft}" in layout_source
        assert "onConfirmDraft={onConfirmMatrixDraft}" in layout_source

    assert "ProjectWorkbenchMatrixInspector" in matrix_panel_source
    assert "Validation blockers" in matrix_panel_source
    assert "Group detail" in matrix_inspector_source
    assert "Confirm Matrix" in matrix_inspector_source
    assert "matrix-group-step-list" in matrix_inspector_source

    assert ".matrix-edit-surface" in styles_source
    assert ".matrix-group-nav" in styles_source
    assert ".matrix-step-editor" in styles_source


def test_task190_matrix_authority_workspace_is_primary_and_supporting_workflows_are_demoted() -> None:
    """TASK_190 makes Matrix authority workspace primary and keeps other workflows as supporting."""
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    matrix_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixReviewPanel.tsx"
    ).read_text(encoding="utf-8")
    matrix_overview_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixOverview.tsx"
    ).read_text(encoding="utf-8")
    matrix_inspector_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixInspector.tsx"
    ).read_text(encoding="utf-8")
    matrix_authority_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixAuthorityBar.tsx"
    ).read_text(encoding="utf-8")
    status_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchDocumentStatusPanel.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    if "runtime-console-shell" in layout_source:
        assert "runtime-console-shell" in layout_source
        assert "ProjectWorkbenchMatrixOverview" in layout_source
        assert "runtimeProjectionSnapshot" in layout_source
        assert "Step Workspace" in layout_source
        assert "RuntimeAttentionSurface" in layout_source
        assert "ProjectWorkbenchDocumentStatusPanel" not in layout_source
        assert "ProjectFolderCreationPanel" not in layout_source
        assert "ApprovalPackagePanel" not in layout_source
        assert "ProjectWorkbenchMatrixInspector" not in layout_source
        assert ".runtime-console-shell" in styles_source
        assert ".runtime-console-step-workspace" in styles_source
        return

    assert "project-workbench-matrix-primary" in layout_source
    assert "project-workbench-supporting" in layout_source
    assert "workbench-supporting-panel" in layout_source
    assert "Matrix authority workspace" in layout_source
    assert "ProjectWorkbenchDocumentStatusPanel" in layout_source
    assert "Project folder workspace" in layout_source
    assert 'className="workbench-supporting-panel" open' not in layout_source
    assert layout_source.index('className="project-workbench-matrix-primary"') < layout_source.index(
        "Project folder workspace"
    )

    assert "ProjectWorkbenchMatrixOverview" in matrix_panel_source
    assert "ProjectWorkbenchMatrixInspector" in matrix_panel_source
    assert "ProjectWorkbenchMatrixAuthorityBar" in matrix_panel_source
    assert "Matrix overview" in matrix_overview_source
    assert "groupColumns.map((column)" in matrix_overview_source
    assert "<th key={column.key}>{column.label}</th>" in matrix_overview_source
    assert "aggregateRowGroupCellTokens" in matrix_overview_source
    assert "rowGroupCellTokens" in matrix_overview_source
    assert "Group</th>" not in matrix_overview_source
    assert "Step token</th>" not in matrix_overview_source
    assert "Confirmed authority v" in matrix_authority_source
    assert "Editing candidate v" in matrix_authority_source
    assert "Group detail" in matrix_inspector_source
    assert "Confirm Matrix" in matrix_inspector_source

    assert "Derived outputs" in status_panel_source or "Downstream status" in status_panel_source

    assert ".project-workbench-matrix-primary" in styles_source
    assert ".project-workbench-supporting" in styles_source
    assert ".workbench-supporting-panel" in styles_source
    assert ".matrix-workspace" in styles_source
    assert ".matrix-overview-table" in styles_source

    for forbidden in ["AI review", "Report generation", "Historical reuse"]:
        assert forbidden not in layout_source + matrix_panel_source


def test_task219d_lightweight_material_drop_surface_is_secondary_and_preview_first() -> None:
    """TASK_219D adds lightweight Other materials support surface without runtime evidence domain expansion."""
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    panel_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMaterialDropPanel.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "ProjectWorkbenchMaterialDropPanel" not in layout_source
    assert "Other materials" in panel_source
    assert "Drop files here (desktop workspace)" in panel_source
    assert "Browser mode does not expose trusted local absolute paths" in panel_source
    assert "Preview placement" in panel_source
    assert "Confirm placement" in panel_source
    assert "Step evidence persistence" not in panel_source
    assert "report binding" not in panel_source
    assert ".material-drop-panel" in styles_source


def test_task219e_runtime_console_regression_guards_keep_workbench_boundary() -> None:
    """TASK_219E keeps Workbench as runtime console and Matrix editing outside Workbench."""
    app_source = (FRONTEND_ROOT / "src" / "App.tsx").read_text(encoding="utf-8")
    workbench_page_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectWorkbenchPage.tsx"
    ).read_text(encoding="utf-8")
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    workbench_model_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "useProjectWorkbenchModel.ts"
    ).read_text(encoding="utf-8")
    matrix_editor_page_source = (
        FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx"
    ).read_text(encoding="utf-8")
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )

    assert "runtime-console-shell" in layout_source
    assert "ProjectWorkbenchMatrixOverview" in layout_source
    assert "Step Workspace" in layout_source
    assert "RuntimeAttentionSurface" in layout_source

    assert "Advanced support: folder, approval, evidence, lookup" not in layout_source
    assert "Setup Manager: project folder" not in layout_source
    assert "Output Status: approval package" not in layout_source
    assert "Legacy: evidence placement detail" not in layout_source
    assert "Read-only lookup" not in layout_source

    assert "ProjectWorkbenchMatrixInspector" not in layout_source
    assert "onSaveDraft={onSaveMatrixDraft}" not in layout_source
    assert "onValidateDraft={onValidateMatrixDraft}" not in layout_source
    assert "onConfirmDraft={onConfirmMatrixDraft}" not in layout_source

    assert "pathname.match(/^\\/projects\\/([^/]+)\\/matrix-editor$/)" in app_source
    assert "ProjectMatrixEditorPage" in app_source
    assert "<h2>Matrix Editor</h2>" in matrix_editor_page_source

    assert "fetch(" not in workbench_page_source
    assert "fetch(" not in layout_source
    assert "fetch(" not in workbench_model_source
    assert 'fetch(`${API_BASE}${path}`' in client_source


def test_task219f_removes_legacy_support_surfaces_from_workbench() -> None:
    """TASK_219F removes legacy support surfaces from visible Workbench UI."""
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")

    for removed_label in [
        "Advanced support: folder, approval, evidence, lookup",
        "Setup Manager: project folder",
        "Output Status: approval package",
        "Legacy: evidence placement detail",
        "Read-only lookup",
    ]:
        assert removed_label not in layout_source

    for removed_component in [
        "ProjectFolderCreationPanel",
        "ApprovalPackagePanel",
        "ProjectWorkbenchEvidencePanel",
        "ProjectLookupPanel",
    ]:
        assert removed_component not in layout_source

    for removed_runtime_label in [
        "Derived outputs",
        "Runtime Support",
        "Project setup status",
        "Other materials",
        "Drop files here (desktop workspace)",
        "Preview placement",
        "Confirm placement",
        "Input paths",
        "Preview items",
        "Placed files",
    ]:
        assert removed_runtime_label not in layout_source

    for removed_runtime_component in [
        "ProjectWorkbenchMaterialDropPanel",
        "ProjectWorkbenchDocumentStatusPanel",
        "RuntimeSupportCard",
    ]:
        assert removed_runtime_component not in layout_source

    assert "runtime-support-shell" not in layout_source
    assert "ProjectWorkbenchMatrixOverview" in layout_source


def test_task220_target_ui_alignment_structure_is_present() -> None:
    """TASK_220 aligns runtime console structure to target workbench UI contract."""
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_label in [
        "Project Workbench",
        "Project readiness status",
        "Actionable",
        "Open Setup Manager",
        "Runtime execution map",
        "Step Workspace",
        "Project issues / reminders",
        "Recent activity",
        "Fee estimate",
    ]:
        assert required_label in layout_source

    for required_style in [
        ".runtime-console-readiness-title",
        ".runtime-console-setup-button",
        ".runtime-console-filter-nav",
        ".runtime-console-step-breadcrumb",
    ]:
        assert required_style in styles_source

    for forbidden_legacy in [
        "Derived outputs",
        "Runtime Support",
        "Project setup status",
        "Other materials",
    ]:
        assert forbidden_legacy not in layout_source


def test_task221_matrix_editor_converges_to_definition_studio_structure() -> None:
    """TASK_221 aligns Matrix Editor to definition-studio workflow structure."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_label in [
        "Matrix Editor",
        "Definition Studio",
        "Back to Workbench",
        "Templates",
        "Reference Library",
        "Projection Ref:",
    ]:
        assert required_label in matrix_editor_source

    assert (
        "Publish for approval" in matrix_editor_source
        or "Confirm revision" in matrix_editor_source
    )

    assert (
        "No group selected" in matrix_editor_source
        or "Group ${selectedGroup ? selectedGroup.name || \"Unnamed\" : \"-\"}" in matrix_editor_source
    )
    assert ("Step preview" in matrix_editor_source or "matrix-editor-step-header" in matrix_editor_source)

    for required_style in [
        ".matrix-editor-target-header",
        ".matrix-editor-actionbar",
        ".matrix-editor-studio",
        ".matrix-editor-grid-surface",
        ".matrix-editor-step-workspace",
        ".matrix-editor-supporting",
        ".matrix-editor-templates",
        ".matrix-editor-reference-library",
    ]:
        assert required_style in styles_source

    for removed_dashboard_label in [
        "Authority Status",
        "Step Identity Preview",
        "Runtime Mapping Notes",
        "Selected Definition (Placeholder)",
    ]:
        assert removed_dashboard_label not in matrix_editor_source


def test_task222_matrix_editor_pixel_tuning_preserves_definition_studio_priority() -> None:
    """TASK_222 keeps definition-studio hierarchy while tuning UI density."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_selector in [
        ".matrix-editor-target-shell",
        ".matrix-editor-target-header",
        ".matrix-editor-actionbar",
        ".matrix-editor-studio",
        ".matrix-editor-main-table-wrap",
        ".matrix-editor-step-workspace",
        ".matrix-editor-supporting",
    ]:
        assert required_selector in styles_source

    for required_label in [
        "Import Matrix",
        "Group Step Workspace",
        "Templates",
        "Reference Library",
    ]:
        assert required_label in matrix_editor_source

    assert "runtime-console-shell" not in matrix_editor_source


def test_task224_matrix_editor_structural_edit_interactions_are_present() -> None:
    """TASK_224 adds guarded row/group structural editing interactions."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_label in [
        "Import Matrix",
        "Undo",
        "Insert left",
        "Insert right",
        "Move left",
        "Move right",
        "At least one group column is required",
        "At least one test item row is required",
    ]:
        assert required_label in matrix_editor_source

    for required_selector in [
        ".matrix-editor-context-actions",
        ".matrix-editor-context-menu",
    ]:
        assert required_selector in styles_source


def test_task225_matrix_editor_uses_context_menu_without_inline_action_columns() -> None:
    """TASK_225 moves structural editing to right-click menus to preserve grid density."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "openRowContextMenu" in matrix_editor_source
    assert "openGroupContextMenu(event, group.id)" in matrix_editor_source
    assert "MatrixContextMenu" in matrix_editor_source
    assert "Delete group" in matrix_editor_source
    assert "Delete row" in matrix_editor_source
    assert ".matrix-editor-context-menu" in styles_source

    for removed_inline_control in [
        "matrix-editor-control-header",
        "matrix-editor-row-controls",
        "matrix-editor-row-menu",
        "matrix-editor-group-head",
        "matrix-editor-group-menu",
    ]:
        assert removed_inline_control not in matrix_editor_source
        assert f".{removed_inline_control}" not in styles_source


def test_task226_matrix_editor_row_selector_and_selection_highlight_are_wired() -> None:
    """TASK_226 adds row-number selection and matching row/group highlight targeting."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_source in [
        "matrix-editor-row-selector-head",
        "matrix-editor-row-selector-cell",
        "matrix-editor-row-selector-button",
        "onClick={() => selectRow(row.id)}",
        "onContextMenu={(event) => openRowContextMenu(event, rowIndex)}",
        "onClick={() => selectGroup(group.id)}",
        "matrix-editor-row-selected",
        "matrix-editor-group-selected",
        "matrix-editor-group-selected-cell",
    ]:
        assert required_source in matrix_editor_source

    for required_style in [
        ".matrix-editor-row-selector-head",
        ".matrix-editor-row-selector-cell",
        ".matrix-editor-row-selector-button",
        ".matrix-editor-row-selected",
        ".matrix-editor-group-selected",
        ".matrix-editor-group-selected-cell",
        ".matrix-editor-main-table th:nth-child(n + 7)",
    ]:
        assert required_style in styles_source

    for removed_inline_control in [
        "matrix-editor-control-header",
        "matrix-editor-row-controls",
        "matrix-editor-row-menu",
        "matrix-editor-group-head",
        "matrix-editor-group-menu",
    ]:
        assert removed_inline_control not in matrix_editor_source
        assert f".{removed_inline_control}" not in styles_source


def test_task227_matrix_editor_group_headers_are_editable() -> None:
    """TASK_227 makes group header names editable with stable column ids."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )

    for required_source in [
        "type GroupColumn = {",
        "name: string;",
        "groupId: string",
        "onChange={(event) => updateGroupName(group.id, event.target.value)}",
    ]:
        assert required_source in matrix_editor_source
    assert (
        '{ id: nextId, name: "" }' in matrix_editor_source
        or "draftGroupId: null" in matrix_editor_source
    )

def test_task228_matrix_editor_uses_direct_group_header_selection_without_index_row() -> None:
    """TASK_228 removes A/B/C index row and uses direct group header context menu."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_source in [
        "onClick={() => selectGroup(group.id)}",
        "onContextMenu={(event) => openGroupContextMenu(event, group.id)}",
        "onClick={(event) => event.stopPropagation()}",
        "matrix-editor-group-name-input",
    ]:
        assert required_source in matrix_editor_source

    for removed_source in [
        "toColumnLabel(",
        "matrix-editor-group-index",
        "key={`index-${group.id}`}",
        "{toColumnLabel(groupIndex)}",
    ]:
        assert removed_source not in matrix_editor_source

    assert ".matrix-editor-group-name-input" in styles_source


def test_task229_matrix_editor_group_name_uniqueness_guard_is_wired() -> None:
    """Group names are required and unique (case-insensitive) in Matrix Editor."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_source in [
        "normalizeGroupName(",
        "Group names duplicated:",
        "Group name is required",
        "duplicateGroupIds",
        "hasGroupNameError",
        "hasGroupNameError || hasStepTokenError",
        'is-duplicate',
    ]:
        assert required_source in matrix_editor_source

    assert ".matrix-editor-group-name-input.is-duplicate" in styles_source


def test_task230_matrix_editor_step_token_validation_guards_are_wired() -> None:
    """TASK_230 enforces step token format and group sequence rules in matrix cells."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_source in [
        "function parseStepTokens(",
        "Only digits and commas are allowed",
        "missing:",
        "duplicates:",
        "stepCellErrorMessageByKey",
        "errorMessage={cellErrorMessage}",
        "invalidStepFormatCellKeys",
        "groupStepSequenceErrorIds",
        "groupStepSequenceErrorCellKeys",
        "const groupCellClass = `matrix-editor-inline-input",
        "invalidStepFormatCellKeys.has(cellKey) || groupStepSequenceErrorCellKeys.has(cellKey)",
        'value={row.groups[group.id] ?? ""}',
        '[nextId]: ""',
    ]:
        assert required_source in matrix_editor_source

    assert ".matrix-editor-inline-input.is-invalid" in styles_source


def test_task231_matrix_editor_step_preview_derives_selected_group_output_rows() -> None:
    """TASK_231 derives selected-group preview rows and keeps output fields editable."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_source in [
        "type StepOutputOverride",
        "function stepOutputKey(",
        "function buildSelectedGroupStepPreviewRows(",
        "const [stepOutputOverrides, setStepOutputOverrides]",
        "const selectedGroupStepRows = buildSelectedGroupStepPreviewRows(",
        "parseStepTokens(row.groups[selectedGroup.id] ?? \"\")",
        "requirementValue: override?.requirement ?? row.requirement",
        "descriptionValue: override?.description",
        "updateStepOutputOverride(row.key, \"requirement\", value)",
        "updateStepOutputOverride(row.key, \"description\", value)",
        "Step Description",
    ]:
        assert required_source in matrix_editor_source

    for removed_placeholder in [
        "STEP_WORKSPACE_ROWS",
        "Group contains LLCR steps",
        "Fee/Time",
        "Apply to Matrix",
    ]:
        assert removed_placeholder not in matrix_editor_source

    assert ".matrix-editor-step-output-table" in styles_source
    assert ".matrix-editor-step-output-textarea" in styles_source


def test_task232_matrix_editor_step_description_defaults_from_test_item_and_removes_test_item_column() -> None:
    """TASK_232 sets Step Description default from Matrix Test Item and removes preview Test Item column."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_source in [
        "sourceTestItem: row.item",
        "requirementValue: override?.requirement ?? row.requirement",
        "descriptionValue: override?.description ?? row.item",
        "<th>Step</th>",
        "<th>Requirement</th>",
        "<th>Step Description</th>",
    ]:
        assert required_source in matrix_editor_source

    for removed_source in [
        "<th>Step</th>\n                  <th>Test Item</th>",
        "matrix-editor-step-output-test-item",
    ]:
        assert removed_source not in matrix_editor_source

    assert "matrix-editor-step-output-test-item" not in styles_source


def test_task233_matrix_editor_step_description_special_family_rules_are_wired() -> None:
    """TASK_233 adds alias-ready family mapping and staged special description defaults."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )

    for required_source in [
        "type StepDescriptionFamily",
        "STEP_DESCRIPTION_FAMILY_ALIASES",
        "low level contact resistance",
        'LLCR: ["llcr", "cr", "low level contact resistance"]',
        "detectStepDescriptionFamily(",
        "containsAliasToken(",
        "STEP_DESCRIPTION_FAMILY_LABELS",
        "specialFamilyRowIndexes",
        "Initial ${familyLabel}",
        "Final ${familyLabel}",
        "After ${previousStepItem}",
        "stepItemByNumber.get(row.stepNo - 1)",
        "stepOutputOverrides[row.key]?.description",
    ]:
        assert required_source in matrix_editor_source


def test_task234_matrix_editor_requirement_split_rules_are_wired() -> None:
    """TASK_234 adds Initial/After requirement split defaults for repeated special-family steps."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )

    for required_source in [
        "function trySplitInitialAfterRequirement(",
        "const initialMatch = normalized.match(/initial\\b/i)",
        "const afterMarkerRegex = /\\bafter(?:\\s+test)?\\b\\s*:?/i",
        "const initialPart = normalized.slice(initialStart, afterStart).trim().replace(/[;:\\s]+$/g, \"\")",
        "const followPart = normalized.slice(afterStart + afterMatch[0].length).trim().replace(/^[;:\\s]+/g, \"\")",
        "followPart",
        "splitByRowId",
        "stepOutputOverrides[row.key]?.requirement",
        "row.requirementValue = indexInFamily === 0 ? split.initialPart : split.followPart",
        "row.requirementValue = split.initialPart",
    ]:
        assert required_source in matrix_editor_source


def test_task235_matrix_editor_requirement_split_colon_variant_support_is_wired() -> None:
    """TASK_235 keeps full initial/after blocks for colon-heavy multi-clause requirements."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )

    for required_source in [
        "const afterMarkerRegex = /\\bafter(?:\\s+test)?\\b\\s*:?/i",
        "afterStart <= initialStart",
        "replace(/[;:\\s]+$/g, \"\")",
        "replace(/^[;:\\s]+/g, \"\")",
    ]:
        assert required_source in matrix_editor_source


def test_task236_matrix_editor_main_table_widths_rebalance_for_condition() -> None:
    """TASK_236 narrows Test Item/Section/Method and widens Condition in matrix main table."""
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_source in [
        ".matrix-editor-main-table th:nth-child(2)",
        "width: 124px;",
        ".matrix-editor-main-table th:nth-child(3)",
        "width: 48px;",
        ".matrix-editor-main-table th:nth-child(4)",
        "width: 88px;",
        ".matrix-editor-main-table th:nth-child(5)",
        "width: 162px;",
    ]:
        assert required_source in styles_source


def test_task237_matrix_editor_fixed_columns_bg_and_group_header_density_are_wired() -> None:
    """TASK_237 adds fixed-column background and denser group-header capsule with larger outer click area."""
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_source in [
        ".matrix-editor-main-table th:nth-child(-n + 6)",
        "background: #f5f9ff;",
        ".matrix-editor-group-band",
        "padding: 6px 4px !important;",
        ".matrix-editor-group-name-input",
        "min-height: 18px;",
        "padding: 2px 6px;",
        "font-size: 8px;",
    ]:
        assert required_source in styles_source


def test_task238_matrix_editor_step_preview_dedupes_duplicate_step_numbers() -> None:
    """TASK_238 dedupes repeated step numbers in preview derivation."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )

    for required_source in [
        "const dedupedBaseRows = baseRows.filter(",
        "candidate.stepNo === row.stepNo",
        "return dedupedBaseRows.map(({ rowIndex: _rowIndex, ...row }) => row);",
    ]:
        assert required_source in matrix_editor_source


def test_task239_matrix_editor_editing_step_cell_auto_selects_group_column() -> None:
    """TASK_239 editing a group step cell auto-selects its group column."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )
    for required_source in [
        "setSelectedGroupId(group.id);",
        "onFocus={() => {",
        "setSelectedRowId(null);",
        "setContextMenu(null);",
        "event.stopPropagation();",
        "onChange={(event) => updateGroupName(group.id, event.target.value)}",
        "updateGroupField(rowIndex, group.id, value);",
    ]:
        assert required_source in matrix_editor_source


def test_task240_matrix_editor_new_row_empty_field_guards_are_wired() -> None:
    """TASK_240 adds empty required-field and empty-step-row warning classes."""
    matrix_editor_source = (
        (FRONTEND_ROOT / "src" / "pages" / "ProjectMatrixEditorPage.tsx").read_text(encoding="utf-8")
        + "\n"
        + (FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx").read_text(encoding="utf-8")
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_source in [
        "const rowHasNoGroupSteps = groupColumns.every((group) => (row.groups[group.id] ?? \"\").trim() === \"\")",
        "className={row.item.trim() === \"\" ? \"is-empty-required\" : undefined}",
        "className={row.method.trim() === \"\" ? \"is-empty-required\" : undefined}",
        "className={row.condition.trim() === \"\" ? \"is-empty-required\" : undefined}",
        "className={row.requirement.trim() === \"\" ? \"is-empty-required\" : undefined}",
        "is-step-missing",
        "title={rowHasNoGroupSteps ? \"Missing step number\" : undefined}",
    ]:
        assert required_source in matrix_editor_source

    for required_style in [
        ".matrix-editor-inline-textarea.is-empty-required",
        ".matrix-editor-row-selector-button.is-step-missing",
    ]:
        assert required_style in styles_source


def test_task243_matrix_editor_starts_with_minimal_valid_grid() -> None:
    """TASK_243 keeps the Matrix Editor initial grid to one row and one group."""
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")

    for required_source in [
        '{ label: "Groups", value: "1" }',
        'groups: { "group-1": "" }',
    ]:
        assert required_source in matrix_editor_source
    assert (
        'return [{ id: "group-1", name: "1" }];' in matrix_editor_source
        or 'id: "group-1",' in matrix_editor_source
    )

    for removed_seed_value in [
        "Examination of Product",
        "Contact Resistance - Low Level Circuit",
        "Visual / Dimensional",
    ]:
        assert removed_seed_value not in matrix_editor_source


def test_task244_matrix_editor_starts_with_two_row_seed_and_optional_section() -> None:
    """TASK_244 seeds a practical first row, keeps a blank second row, and makes Section optional."""
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")

    for required_source in [
        '{ label: "Steps", value: "1" }',
        '{ label: "Items", value: "2" }',
        'id: "matrix-row-0"',
        'item: "Visual Examination"',
        'method: "EIA-364-18B"',
        'condition: "10x min magnification"',
        'requirement: "No detrimental condition"',
        'groups: { "group-1": "1" }',
        'id: "matrix-row-1"',
        'groups: { "group-1": "" }',
        'ariaLabel={`Row ${rowIndex + 1} section`}',
        'onChange={(value) => updateTextField(rowIndex, "section", value)}',
        'className={row.item.trim() === "" ? "is-empty-required" : undefined}',
        'className={row.method.trim() === "" ? "is-empty-required" : undefined}',
        'className={row.condition.trim() === "" ? "is-empty-required" : undefined}',
        'className={row.requirement.trim() === "" ? "is-empty-required" : undefined}',
    ]:
        assert required_source in matrix_editor_source


def test_task249_matrix_editor_removes_grid_toolbar_and_selection_hint() -> None:
    """TASK_249 removes grid toolbar and selection hint strip in matrix editor edit area."""
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")

    for removed_source in [
        "Matrix Version",
        "All groups",
        "All sections",
        "Selection: none",
        "Header and first five columns are structurally fixed.",
    ]:
        assert removed_source not in matrix_editor_source

    assert 'className={row.section.trim() === "" ? "is-empty-required" : undefined}' not in matrix_editor_source


def test_task252ck_matrix_editor_step_notes_use_preview_payload_and_concise_item_section() -> None:
    """TASK_252CK wires Step preview notes to import payload and keeps concise Item/Section notes."""
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")

    for required_source in [
        "function buildPreviewStepNoteLookup(",
        "sourceNote: step.source_note ?? null",
        "sourceItemSectionNote: step.source_item_section_note ?? null",
        "sampleNote: previewGroup.sample_note ?? null",
        "function formatConciseItemSectionNote(stepNo: number, noteText: string): string",
        "const withoutTestItem = normalized.replace(/^Test Item:",
        "return `Step ${stepNo} | Section:${sectionPayload}`;",
        "const selectedGroupPreviewNotes = buildPreviewStepNoteLookup(importPreview, selectedGroup);",
        "const rawNote = mapped?.sourceNote ?? row.sourceStepNote;",
        "const markerNote = marker ? selectedGroupPreviewNotes.itemSectionByMarker.get(marker) ?? null : null;",
        "const rawNote = mapped?.sourceItemSectionNote ?? (markerNote ? replaceItemSectionNoteSection(markerNote, row.sourceSection) : row.sourceItemSectionNote);",
        "const concise = formatConciseItemSectionNote(row.stepNo, rawNote);",
        "const selectedGroupSampleNotes = [",
        "selectedGroupPreviewNotes.sampleNote ?? (sampleMarker ? `${sampleMarker[0]}` : null),",
    ]:
        assert required_source in matrix_editor_source


def test_task252cl_matrix_editor_step_notes_prefix_and_note_cards_are_wired() -> None:
    """TASK_252CL prefixes Step Notes with token and restores note card visual variants."""
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(encoding="utf-8")

    for required_source in [
        "function stripLeadingMarkerPrefix(noteText: string): string",
        ".replace(/^\\((?:\\d*\\s*)?[a-z]\\)\\s*/i, \"\")",
        "return body.length > 0 ? `${row.rawToken} ${body}` : row.rawToken;",
        "const dedupedSelectedGroupStepNotes = [...new Set(selectedGroupStepNotes)];",
        "dedupedSelectedGroupStepNotes.map((note, index)",
    ]:
        assert required_source in matrix_editor_source

    for required_style in [
        ".matrix-editor-notes-card {",
        ".matrix-editor-notes-card-step {",
        ".matrix-editor-notes-card-item-section {",
        ".matrix-editor-notes-card-samples {",
        "background: #fff7e6;",
        "background: #f1effb;",
    ]:
        assert required_style in styles_source


def test_task252cn_matrix_editor_reuses_symbol_item_section_note_for_local_rows() -> None:
    """TASK_252CN lets local section-marker rows reuse imported symbol note bodies."""
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")

    for required_source in [
        "itemSectionByMarker: Map<string, string>;",
        "const itemSectionByMarker = new Map<string, string>();",
        "const sectionMarker = extractMarkerKey(step.source_section ?? null);",
        "itemSectionByMarker.set(sectionMarker, itemSectionNote);",
        "function replaceItemSectionNoteSection(noteText: string, sourceSection: string): string",
        "replaceItemSectionNoteSection(markerNote, row.sourceSection)",
        'sourceItemSectionNote: itemSectionMarker ? `Section: ${row.section}` : null',
    ]:
        assert required_source in matrix_editor_source


def test_task252co_matrix_editor_samples_inline_and_notes_label_minified() -> None:
    """TASK_252CO keeps Samples label/input on one row and shortens notes heading."""
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(encoding="utf-8")

    for required_source in [
        "className=\"matrix-editor-samples-inline\"",
        "className=\"matrix-editor-inline-input matrix-editor-samples-inline-input\"",
        "<h5>Notes</h5>",
    ]:
        assert required_source in matrix_editor_source

    assert "<h5>Samples Notes</h5>" not in matrix_editor_source

    for required_style in [
        ".matrix-editor-samples-inline {",
        "display: flex;",
        "flex-wrap: nowrap;",
        ".matrix-editor-samples-inline-input {",
        "min-width: 0;",
    ]:
        assert required_style in styles_source


def test_task252cp_matrix_editor_samples_row_label_center_and_wrapped_editor() -> None:
    """TASK_252CP centers sample-row label and uses autogrow textarea in group sample cells."""
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(encoding="utf-8")

    for required_source in [
        '<td className="matrix-editor-sample-label-cell">Samples Quantity (PCS)</td>',
        "className=\"matrix-editor-sample-textarea\"",
        "ariaLabel={`Samples ${group.name || \"group\"}`}",
    ]:
        assert required_source in matrix_editor_source

    assert "matrix-editor-inline-input matrix-editor-sample-input" not in matrix_editor_source

    for required_style in [
        ".matrix-editor-sample-label-cell {",
        "vertical-align: middle !important;",
        ".matrix-editor-sample-textarea {",
        "overflow-wrap: anywhere;",
    ]:
        assert required_style in styles_source


def test_task252cq_matrix_editor_identical_sample_rows_merge_note_is_wired() -> None:
    """TASK_252CQ shows a right-side note when identical imported sample rows are merged."""
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")

    for required_source in [
        "sampleMergeNotes: Record<string, string>;",
        "const sampleMergeNotes: Record<string, string> = {};",
        "const sampleEntries = sampleRows",
        "const uniqueSampleValues = [...new Set(sampleEntries.map((entry) => entry.value))];",
        "sampleMergeNotes[groupId] = `${uniqueLabels.join(\" / \")} share the same sample quantity.`;",
        "const [sampleMergeNotes, setSampleMergeNotes] = useState<Record<string, string>>({});",
        "const selectedGroupSampleMergeNote = selectedGroup ? sampleMergeNotes[selectedGroup.id] ?? null : null;",
        "const { [group.id]: _removed, ...next } = previous;",
        "const { [selectedGroup.id]: _removed, ...next } = previous;",
    ]:
        assert required_source in matrix_editor_source


def test_task252cr_matrix_import_preview_layout_and_reparse_style_are_wired() -> None:
    """TASK_252CR keeps import title+filename inline, uses viewer fit-width fragment, and aligns reparse styling."""
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(encoding="utf-8")

    for required_source in [
        "className=\"matrix-editor-import-header-inline\"",
        "title={importPreview?.source_document_name ?? importFile?.name ?? \"Selected file\"}",
        "const previewPdfSrc = importPreview?.preview_pdf_token",
        "#page=${previewOpenPage}&zoom=page-width&pagemode=thumbs",
        "className=\"matrix-editor-import-controls-row\"",
    ]:
        assert required_source in matrix_editor_source

    for required_style in [
        ".matrix-editor-import-header-inline {",
        "align-items: baseline;",
        "text-overflow: ellipsis;",
        ".matrix-editor-import-controls-row {",
        "grid-template-columns: 1fr 1fr;",
        ".matrix-editor-import-reparse-button {",
        "height: 42px;",
        "font-size: 18px;",
        ".matrix-editor-import-reparse-button:disabled {",
    ]:
        assert required_style in styles_source


def test_task252cs_matrix_editor_step_preview_header_and_samples_card_color_are_wired() -> None:
    """TASK_252CS uses Group-prefixed step header, removes redundant labels, and applies distinct samples card color."""
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(encoding="utf-8")

    for required_source in [
        "className=\"matrix-editor-step-header\"",
        "className=\"matrix-editor-step-header-text\"",
        "{`Group ${selectedGroup ? selectedGroup.name || \"Unnamed\" : \"-\"}: ${selectedGroupStepRows.length} steps`}",
    ]:
        assert required_source in matrix_editor_source

    for removed_source in [
        "<h3>Step preview</h3>",
        "Selected group",
        "Select group",
    ]:
        assert removed_source not in matrix_editor_source

    for required_style in [
        ".matrix-editor-step-header-text {",
        "font-size: 20px;",
        ".matrix-editor-notes-card-samples {",
        "background: #eef9f4;",
        "border-color: #bfe1d1;",
    ]:
        assert required_style in styles_source


def test_task245_matrix_editor_table_columns_have_fixed_min_widths() -> None:
    """TASK_245 fixes Matrix Editor column widths so extra groups scroll instead of shrinking."""
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_source in [
        "width: max-content;",
        "width: 38px;",
        "min-width: 38px;",
        "width: 124px;",
        "min-width: 124px;",
        "width: 48px;",
        "min-width: 48px;",
        "width: 88px;",
        "min-width: 88px;",
        "width: 162px;",
        "min-width: 162px;",
        "width: 116px;",
        "min-width: 116px;",
        "width: 44px;",
        "min-width: 44px;",
    ]:
        assert required_source in styles_source

    assert styles_source.count("width: max-content;") >= 2
    assert styles_source.count("min-width: 44px;") >= 2


def test_task246_matrix_editor_table_uses_compact_fixed_column_widths() -> None:
    """TASK_246 removes the broad table minimum and caps columns at their fixed widths."""
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "min-width: max(1180px, 100%);" not in styles_source

    for required_source in [
        "width: max-content;",
        "max-width: 38px;",
        "max-width: 124px;",
        "max-width: 48px;",
        "max-width: 88px;",
        "max-width: 162px;",
        "max-width: 116px;",
        "max-width: 44px;",
    ]:
        assert required_source in styles_source

    assert styles_source.count("width: max-content;") >= 2
    assert styles_source.count("max-width: 44px;") >= 2


def test_task248_matrix_editor_group_name_wrap_reverted_to_single_line() -> None:
    """TASK_248 restores single-line clipping for group header names."""
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )
    group_input_block = styles_source.split(".matrix-editor-group-name-input {", 1)[1].split("}", 1)[0]

    for required_source in [
        "white-space: nowrap;",
        "overflow: hidden;",
        "text-overflow: ellipsis;",
        "width: 44px;",
        "min-width: 44px;",
        "max-width: 44px;",
    ]:
        assert required_source in styles_source

    assert "white-space: normal;" not in group_input_block
    assert "overflow-wrap: anywhere;" not in group_input_block
    assert "word-break: break-word;" not in group_input_block


def test_task191_matrix_starter_import_and_manual_empty_state_is_feature_wired() -> None:
    """TASK_191 adds Matrix starter actions for draftless projects in matrix workspace."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    model_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "useProjectWorkbenchModel.ts"
    ).read_text(encoding="utf-8")
    matrix_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixReviewPanel.tsx"
    ).read_text(encoding="utf-8")
    starter_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixStarter.tsx"
    ).read_text(encoding="utf-8")
    helper_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "projectWorkbenchMatrixHelpers.ts"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "/api/test-plan/matrix-preview-from-path" in client_source
    assert "previewProjectTestPlanMatrixFromPath" in client_source
    assert "createProjectTestPlanDraft" in client_source
    assert "/test-plan/drafts" in client_source

    assert "matrixStarterSourcePath" in model_source
    assert "matrixStarterPreview" in model_source
    assert "matrixStarterPreviewing" in model_source
    assert "matrixStarterCreatingFromPreview" in model_source
    assert "matrixStarterCreatingManual" in model_source
    assert "onPreviewMatrixStarterFromPath" in model_source
    assert "onCreateMatrixDraftFromPreview" in model_source
    assert "onCreateManualMatrixDraft" in model_source


def test_task256_matrix_editor_save_to_project_matrix_draft_wiring_is_present() -> None:
    """TASK_256 wires Matrix Editor Save to structured Project Matrix Draft API client."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")
    backend_root = Path(__file__).resolve().parents[2] / "backend"
    route_source = (backend_root / "api" / "routes_project_matrix_drafts.py").read_text(
        encoding="utf-8"
    )
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    for required_client_symbol in [
        "listProjectMatrixDrafts",
        "getProjectMatrixDraft",
        "saveProjectMatrixDraft",
        "/api/projects/${encodeURIComponent(projectId)}/matrix-drafts",
    ]:
        assert required_client_symbol in client_source

    for required_editor_symbol in [
        "projectMatrixDraftId",
        "saveState",
        "buildDraftSavePayload",
        "currentSavePayload",
        "hasUnsavedChanges",
        "Saving...",
        "Unsaved changes",
        "saveProjectMatrixDraft(projectId, projectMatrixDraftId, currentSavePayload)",
    ]:
        assert required_editor_symbol in matrix_editor_source

    for required_route_symbol in [
        "@router.put(\"/{project_matrix_draft_id}\"",
        "def save_project_matrix_draft(",
        "@router.get(\"\", response_model=list[ProjectMatrixDraftSummaryResponse])",
    ]:
        assert required_route_symbol in route_source

    assert ".matrix-editor-save-status" in styles_source


def test_task259_matrix_editor_revision_actions_wiring_is_present() -> None:
    """TASK_259 wires revision create/confirm actions with draft-kind guards and fixed MVP confirmed_by."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")

    for required_client_symbol in [
        "source_import_id: string | null;",
        "base_confirmed_matrix_id: string | null;",
        "export type ConfirmProjectMatrixRevisionDraftInput = {",
        "confirmed_by: string;",
        "createMatrixRevisionDraft",
        "confirmProjectMatrixRevisionDraft",
        "/matrix-revisions",
        "/confirm-revision",
    ]:
        assert required_client_symbol in client_source

    for required_editor_symbol in [
        'const MVP_REVISION_CONFIRMED_BY = "connlab-operator";',
        "buildConfirmRevisionGuard(",
        "projectMatrixDraftBaseConfirmedMatrixId",
        "Revision already confirmed.",
        "Current draft is not a revision draft.",
        "Save changes before creating revision draft.",
        "Save changes before confirming revision.",
        "Revision draft loaded.",
        "const onCreateRevisionDraft = async (): Promise<void> => {",
        "const onConfirmRevision = async (): Promise<void> => {",
        "confirmProjectMatrixRevisionDraft(projectId, projectMatrixDraftId, {",
        "confirmed_by: MVP_REVISION_CONFIRMED_BY,",
        "Confirm revision",
        "Create revision draft",
    ]:
        assert required_editor_symbol in matrix_editor_source


def test_task262_matrix_import_group_selection_view_and_commit_wiring_is_present() -> None:
    """TASK_262 adds Group Selection gate and TASK_261 commit API wiring."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    matrix_editor_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixEditorWorkspace.tsx"
    ).read_text(encoding="utf-8")
    selection_mode_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "MatrixImportSelectionMode.tsx"
    ).read_text(encoding="utf-8")
    selectors_source = (
        FRONTEND_ROOT / "src" / "features" / "matrix-editor" / "matrixImportSelectionSelectors.ts"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(encoding="utf-8")

    for required_client_symbol in [
        "export type MatrixImportCommitRequest = {",
        "export type MatrixImportCommitResponse = {",
        "selected_group_keys: string[];",
        "commitMatrixImport(",
        "/matrix-import/commit",
    ]:
        assert required_client_symbol in client_source

    for required_editor_symbol in [
        "showImportSelectionMode",
        "groupSelectionKeys",
        "openGroupSelection",
        "onCommitImportedGroups",
        "buildMatrixImportSelectionViewModel(importPreview)",
        "buildMatrixImportSelectionDisabledReason(",
        "commitMatrixImport(projectId, {",
        "setShowImportSelectionMode(true);",
        "<MatrixImportSelectionMode",
        "Replace",
        "Append",
    ]:
        assert required_editor_symbol in matrix_editor_source

    for required_selection_view_symbol in [
        "Import Selection Mode",
        "Confirm selected groups",
        "Append Matrix (Future)",
        "Test Item",
        "const visibleStatusMessage = disabledReason || statusMessage;",
        "aria-live=\"polite\"",
    ]:
        assert required_selection_view_symbol in selection_mode_source

    for forbidden_symbol in [
        "Section",
        "Method",
        "Condition",
        "Requirement",
    ]:
        assert forbidden_symbol not in selection_mode_source

    for required_selector_symbol in [
        "buildMatrixImportSelectableGroups(",
        "buildMatrixImportSelectionViewModel(",
        "buildDefaultSelectedGroupKeys(",
        "buildMatrixImportSelectionDisabledReason(",
        "return `group_",
    ]:
        assert required_selector_symbol in selectors_source

    for required_style_symbol in [
        ".matrix-editor-selection-mode {",
        ".matrix-editor-selection-table",
        ".matrix-editor-selection-mode-pill {",
        ".matrix-editor-group-selection-status {",
    ]:
        assert required_style_symbol in styles_source

def test_task192_matrix_source_candidates_and_browse_fallback_are_feature_wired() -> None:
    """TASK_192 prioritizes project source candidates before external/manual fallback."""
    client_source = (FRONTEND_ROOT / "src" / "api" / "client.ts").read_text(
        encoding="utf-8"
    )
    model_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "useProjectWorkbenchModel.ts"
    ).read_text(encoding="utf-8")
    layout_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchLayout.tsx"
    ).read_text(encoding="utf-8")
    matrix_panel_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixReviewPanel.tsx"
    ).read_text(encoding="utf-8")
    starter_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "ProjectWorkbenchMatrixStarter.tsx"
    ).read_text(encoding="utf-8")
    helper_source = (
        FRONTEND_ROOT / "src" / "features" / "project-workbench" / "projectWorkbenchMatrixHelpers.ts"
    ).read_text(encoding="utf-8")
    styles_source = (FRONTEND_ROOT / "src" / "workbench.css").read_text(
        encoding="utf-8"
    )

    assert "/test-plan/source-candidates" in client_source
    assert "listProjectTestPlanSourceCandidates" in client_source
    assert "previewProjectTestPlanMatrixFromSourceCandidate" in client_source

    assert "matrixSourceCandidates" in model_source
    assert "matrixSelectedSourceAssetId" in model_source
    assert "matrixStarterBrowseHint" in model_source
    assert "onPreviewMatrixStarterFromCandidate" in model_source
    assert "onBrowseMatrixStarterFallback" in model_source
    assert "listProjectTestPlanSourceCandidates" in model_source
    assert "previewProjectTestPlanMatrixFromSourceCandidate" in model_source

    if "runtime-console-shell" in layout_source:
        assert "sourceCandidates={matrixSourceCandidates}" not in layout_source
        assert "ProjectWorkbenchMatrixStarter" in matrix_panel_source
    else:
        assert "sourceCandidates={matrixSourceCandidates}" in layout_source
        assert "onPreviewStarterFromCandidate={onPreviewMatrixStarterFromCandidate}" in layout_source
        assert "ProjectWorkbenchMatrixStarter" in matrix_panel_source

    assert "Candidate source files from this project" in starter_source
    assert "Preview selected source" in starter_source
    assert "External source fallback" in starter_source
    assert "Browse..." in starter_source
    assert "Create manual Matrix" in starter_source

    assert "source_asset_id: sourceAssetId" in helper_source

    assert ".matrix-source-candidate-list" in styles_source
    assert ".matrix-source-candidate-row" in styles_source
    assert ".matrix-starter-card-secondary" in styles_source
