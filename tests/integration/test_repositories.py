from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy import text

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

        assert {
            "application_forms",
            "file_assets",
            "ltr_records",
            "precheck_issues",
            "precheck_results",
            "project_folder_records",
            "projects",
            "sample_infos",
        }.issubset(set(inspect(engine).get_table_names()))
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


def test_project_no_is_optional_and_not_unique(tmp_path: Path) -> None:
    engine = _create_temp_engine(tmp_path)
    init_db(engine)
    session_factory = create_session_factory(engine)

    try:
        with session_factory() as session:
            repository = ProjectRepository(session)
            repository.create(
                Project(
                    project_id="project-1",
                    project_no=None,
                    product_name="Connector A",
                    requestor="Alice",
                )
            )
            repository.create(
                Project(
                    project_id="project-2",
                    project_no=None,
                    product_name="Connector B",
                    requestor="Bob",
                )
            )
            session.commit()

            assert [project.project_no for project in repository.list()] == [None, None]
    finally:
        engine.dispose()


def test_init_db_relaxes_legacy_project_no_constraint(tmp_path: Path) -> None:
    engine = _create_temp_engine(tmp_path)

    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE TABLE projects (
                        project_id VARCHAR(64) NOT NULL,
                        project_no VARCHAR(128) NOT NULL UNIQUE,
                        product_name VARCHAR(255) NOT NULL,
                        requestor VARCHAR(255) NOT NULL,
                        status VARCHAR(64) NOT NULL,
                        business_unit VARCHAR(255),
                        created_on DATE,
                        PRIMARY KEY (project_id)
                    )
                    """
                )
            )
            connection.execute(
                text(
                    """
                    INSERT INTO projects (
                        project_id,
                        project_no,
                        product_name,
                        requestor,
                        status
                    ) VALUES (
                        'project-legacy',
                        'PRJ-OLD',
                        'Connector',
                        'Alice',
                        'draft'
                    )
                    """
                )
            )

        init_db(engine)
        columns = inspect(engine).get_columns("projects")
        project_no_column = next(column for column in columns if column["name"] == "project_no")
        session_factory = create_session_factory(engine)
        with session_factory() as session:
            repository = ProjectRepository(session)
            repository.create(
                Project(
                    project_id="project-new-1",
                    project_no=None,
                    product_name="Connector A",
                    requestor="Bob",
                )
            )
            repository.create(
                Project(
                    project_id="project-new-2",
                    project_no=None,
                    product_name="Connector B",
                    requestor="Carol",
                )
            )
            session.commit()

        assert project_no_column["nullable"] is True
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


def test_sample_repository_preserves_inserted_sample_row_order(tmp_path: Path) -> None:
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
            samples = (
                SampleInfo(
                    sample_id="sample-z",
                    project_id="project-1",
                    product_name="Top row",
                    part_number="PN-TOP",
                ),
                SampleInfo(
                    sample_id="sample-a",
                    project_id="project-1",
                    product_name="Bottom row",
                    part_number="PN-BOTTOM",
                ),
            )

            for sample in samples:
                SampleInfoRepository(session).create(sample)
            session.commit()

            assert SampleInfoRepository(session).list_by_project("project-1") == list(samples)
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
