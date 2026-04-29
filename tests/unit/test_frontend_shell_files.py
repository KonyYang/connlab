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
        "registerLtr",
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
    styles_source = (FRONTEND_ROOT / "src" / "styles.css").read_text(
        encoding="utf-8"
    )
    index_source = (FRONTEND_ROOT / "index.html").read_text(encoding="utf-8")

    assert "AppShell" in app_source
    assert "Connector lab workbench" not in app_source
    assert "Dashboard" in sidebar_source
    assert "Projects" in sidebar_source
    assert "Intake" in sidebar_source
    assert "Precheck" in sidebar_source
    assert "LTR" in sidebar_source
    assert "Folders" in sidebar_source
    assert "Settings" in sidebar_source
    assert "/connlab-icon.svg" in sidebar_source
    assert "/connlab-icon.svg" in index_source
    assert "disabled" in sidebar_source
    assert "Offline local" in top_bar_source
    assert ".sidebar" in styles_source
    assert ".top-bar" in styles_source
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
    assert "<table" in list_page_source
    assert "Project No. (optional)" in list_page_source
    assert "Product" in list_page_source
    assert "Requestor" in list_page_source
    assert "Business Unit" in list_page_source
    assert "Status" in list_page_source
    assert "Create project" in list_page_source
    assert ".project-table" in styles_source
    assert ".new-project-panel" in styles_source


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
    assert "Latest LTR" in ltr_source
    assert "registered" in ltr_source
    assert "Not registered" in ltr_source
    assert "folder-tree-preview" in folder_source
    assert "Conflict detected" in folder_source
    assert "disabled={folderPlan.conflict}" in folder_source
    assert ".operator-panel" in styles_source
    assert ".metadata-grid" in styles_source
    assert ".folder-tree-preview" in styles_source


def test_frontend_api_calls_remain_centralized() -> None:
    """TASK_022 keeps raw fetch usage inside the API client only."""
    src_root = FRONTEND_ROOT / "src"
    files_with_fetch = [
      path.relative_to(FRONTEND_ROOT).as_posix()
      for path in src_root.rglob("*.ts*")
      if "fetch(" in path.read_text(encoding="utf-8")
    ]

    assert files_with_fetch == ["src/api/client.ts"]
