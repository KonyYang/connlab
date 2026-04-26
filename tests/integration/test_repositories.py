from pathlib import Path

from sqlalchemy import inspect

from backend.domain import (
    ApplicationForm,
    IssueCategory,
    IssueLevel,
    PrecheckIssue,
    PrecheckResult,
    PrecheckStatus,
    Project,
    ProjectStatus,
    SampleInfo,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories import (
    ApplicationFormRepository,
    PrecheckResultRepository,
    ProjectRepository,
    SampleInfoRepository,
)
from backend.shared.config import Settings


def test_init_db_creates_mvp_tables(tmp_path: Path) -> None:
    engine = _create_temp_engine(tmp_path)

    try:
        init_db(engine)

        assert set(inspect(engine).get_table_names()) == {
            "application_forms",
            "file_assets",
            "ltr_records",
            "precheck_issues",
            "precheck_results",
            "project_folder_records",
            "projects",
            "sample_infos",
        }
    finally:
        engine.dispose()


def test_project_repository_create_get_list_update(tmp_path: Path) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)

    try:
        with session_factory() as session:
            repository = ProjectRepository(session)
            project = Project(
                project_id="project-1",
                project_no="PRJ-001",
                product_name="Connector",
                requestor="Alice",
                status=ProjectStatus.DRAFT,
            )

            repository.create(project)
            session.commit()

            stored = repository.get("project-1")
            updated = project.with_status(ProjectStatus.CONFIRMED)
            repository.update(updated)
            session.commit()

            assert stored == project
            assert repository.get("project-1") == updated
            assert repository.list() == [updated]
    finally:
        engine.dispose()


def test_store_application_form_with_sample_rows(tmp_path: Path) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)

    try:
        with session_factory() as session:
            ProjectRepository(session).create(
                Project(
                    project_id="project-1",
                    project_no="PRJ-001",
                    product_name="Connector",
                    requestor="Alice",
                )
            )
            form = ApplicationForm(
                form_id="form-1",
                project_id="project-1",
                form_no="E-3718",
                revision="H",
                requester="Alice",
                requested_testing="Salt spray test",
                subcontract_allowed=False,
            )
            sample = SampleInfo(
                sample_id="sample-1",
                project_id="project-1",
                product_name="Connector",
                part_number="PN-001",
                quantity=12,
            )

            ApplicationFormRepository(session).create_with_samples(form, (sample,))
            session.commit()

            assert ApplicationFormRepository(session).get("form-1") == form
            assert SampleInfoRepository(session).list_by_project("project-1") == [sample]
    finally:
        engine.dispose()


def test_store_precheck_result_with_issues(tmp_path: Path) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)

    try:
        with session_factory() as session:
            ProjectRepository(session).create(
                Project(
                    project_id="project-1",
                    project_no="PRJ-001",
                    product_name="Connector",
                    requestor="Alice",
                )
            )
            ApplicationFormRepository(session).create(
                ApplicationForm(
                    form_id="form-1",
                    project_id="project-1",
                    form_no="E-3718",
                    revision="H",
                    requester="Alice",
                )
            )
            result = PrecheckResult(
                result_id="result-1",
                application_form_id="form-1",
                status=PrecheckStatus.FAILED,
                issues=(
                    PrecheckIssue(
                        issue_id="issue-1",
                        category=IssueCategory.REQUESTOR,
                        level=IssueLevel.ERROR,
                        message="Requester email is missing.",
                        field_name="email",
                    ),
                ),
            )

            PrecheckResultRepository(session).create(result)
            session.commit()

            stored = PrecheckResultRepository(session).get("result-1")

            assert stored == result
            assert stored is not None
            assert stored.has_errors() is True
    finally:
        engine.dispose()


def _create_temp_engine(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path / "data",
        projects_dir=tmp_path / "projects",
        templates_dir=tmp_path / "templates",
        database_path=tmp_path / "connlab.sqlite3",
    )
    return create_database_engine(settings)
