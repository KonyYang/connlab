from pathlib import Path

from backend.domain import (
    ApplicationForm,
    FileAsset,
    FileAssetType,
    IssueCategory,
    IssueLevel,
    LtrRecord,
    LtrStatus,
    PrecheckIssue,
    PrecheckResult,
    PrecheckStatus,
    Project,
    ProjectFolderRecord,
    ProjectStatus,
    SampleInfo,
)


def test_domain_enum_values_are_stable() -> None:
    assert ProjectStatus.CONFIRMED == "confirmed"
    assert PrecheckStatus.FAILED == "failed"
    assert IssueLevel.ERROR == "error"
    assert IssueCategory.TESTING_REQUEST == "testing_request"
    assert LtrStatus.REGISTERED == "registered"
    assert FileAssetType.APPLICATION_FORM == "application_form"


def test_project_status_helpers() -> None:
    project = Project(
        project_id="project-1",
        project_no="PRJ-001",
        product_name="Connector",
        requestor="Alice",
    )

    confirmed_project = project.with_status(ProjectStatus.CONFIRMED)

    assert project.can_generate_folder() is False
    assert confirmed_project.can_generate_folder() is True
    assert confirmed_project.status is ProjectStatus.CONFIRMED
    assert project.status is ProjectStatus.DRAFT


def test_mvp_domain_models_construct_without_infrastructure() -> None:
    project = Project(
        project_id="project-1",
        project_no="PRJ-001",
        product_name="Connector",
        requestor="Alice",
    )
    form = ApplicationForm(
        form_id="form-1",
        project_id=project.project_id,
        form_no="E-3718",
        revision="H",
        requester="Alice",
    )
    sample = SampleInfo(
        sample_id="sample-1",
        project_id=project.project_id,
        product_name="Connector",
        part_number="PN-001",
        quantity=12,
    )
    issue = PrecheckIssue(
        issue_id="issue-1",
        category=IssueCategory.REQUESTOR,
        level=IssueLevel.ERROR,
        message="Requester email is missing.",
        field_name="email",
    )
    result = PrecheckResult(
        result_id="result-1",
        application_form_id=form.form_id,
        status=PrecheckStatus.FAILED,
        issues=(issue,),
    )
    ltr = LtrRecord(
        ltr_id="ltr-1",
        project_id=project.project_id,
        ltr_number="LTR-001",
        status=LtrStatus.REGISTERED,
    )
    folder = ProjectFolderRecord(
        folder_id="folder-1",
        project_id=project.project_id,
        folder_path=Path("projects") / "PRJ-001",
    )
    asset = FileAsset(
        asset_id="asset-1",
        project_id=project.project_id,
        asset_type=FileAssetType.APPLICATION_FORM,
        path=Path("forms") / "application.docx",
    )

    assert form.project_id == project.project_id
    assert sample.quantity == 12
    assert result.has_errors() is True
    assert ltr.status is LtrStatus.REGISTERED
    assert folder.folder_path == Path("projects") / "PRJ-001"
    assert asset.asset_type is FileAssetType.APPLICATION_FORM


def test_precheck_result_without_error_issues() -> None:
    warning = PrecheckIssue(
        issue_id="issue-1",
        category=IssueCategory.SAMPLE,
        level=IssueLevel.WARNING,
        message="Sample quantity should be reviewed.",
    )
    result = PrecheckResult(
        result_id="result-1",
        application_form_id="form-1",
        status=PrecheckStatus.WARNING,
        issues=(warning,),
    )

    assert result.has_errors() is False
