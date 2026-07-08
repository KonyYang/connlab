from __future__ import annotations

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from backend.application.project_basic_information_service import (
    ProjectBasicInformationRecord,
    ProjectBasicInformationVersionConflictError,
)
from backend.infrastructure.storage.database import init_db
from backend.infrastructure.storage.repositories.project_basic_information import (
    ProjectBasicInformationRepository,
)


def test_project_basic_information_repository_creates_and_updates_draft() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    with Session(engine) as session:
        repository = ProjectBasicInformationRepository(session)

        repository.save_draft(
            _record(
                "draft-1",
                status="draft",
                version=0,
                values={"project_type": "NPD"},
                updated_at="2026-06-20T09:00:00+00:00",
            )
        )
        repository.save_draft(
            _record(
                "draft-1",
                status="draft",
                version=0,
                values={"project_type": "PEX"},
                updated_at="2026-06-20T10:00:00+00:00",
            )
        )

        draft = repository.get_latest_draft("P1")

    assert draft is not None
    assert draft.record_id == "draft-1"
    assert draft.values == {"project_type": "PEX"}
    assert draft.updated_at == "2026-06-20T10:00:00+00:00"


def test_project_basic_information_repository_creates_multiple_confirmed_versions() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    with Session(engine) as session:
        repository = ProjectBasicInformationRepository(session)

        first = repository.create_confirmed(
            _record(
                "confirmed-1",
                status="confirmed",
                version=1,
                values={"project_type": "NPD"},
            )
        )
        second = repository.create_confirmed(
            _record(
                "confirmed-2",
                status="confirmed",
                version=2,
                values={"project_type": "PEX"},
            )
        )

        latest = repository.get_latest_confirmed("P1")
        versions = repository.list_confirmed_by_project("P1")

    assert versions == [first, second]
    assert latest == second
    assert latest is not None
    assert latest.values["project_type"] == "PEX"


def test_project_basic_information_repository_round_trips_quantity_defaults() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    values = {
        "project_type": "NPD",
        "test_points_per_sample": "3",
        "readings_per_point": "2",
        "contact_points_per_sample": "4",
    }
    with Session(engine) as session:
        repository = ProjectBasicInformationRepository(session)

        repository.save_draft(
            _record("draft-1", status="draft", version=0, values=values)
        )
        repository.create_confirmed(
            _record("confirmed-1", status="confirmed", version=1, values=values)
        )

        draft = repository.get_latest_draft("P1")
        confirmed = repository.get_latest_confirmed("P1")

    assert draft is not None
    assert draft.values == values
    assert confirmed is not None
    assert confirmed.values == values


def test_project_basic_information_repository_returns_next_confirmed_version() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    with Session(engine) as session:
        repository = ProjectBasicInformationRepository(session)

        assert repository.next_confirmed_version("P1") == 1
        repository.create_confirmed(
            _record("confirmed-1", status="confirmed", version=1, values={})
        )

        assert repository.next_confirmed_version("P1") == 2


def test_project_basic_information_repository_translates_duplicate_version() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)
    init_db(engine)
    with Session(engine) as session:
        repository = ProjectBasicInformationRepository(session)
        repository.create_confirmed(
            _record("confirmed-1", status="confirmed", version=1, values={})
        )

        try:
            repository.create_confirmed(
                _record("confirmed-duplicate", status="confirmed", version=1, values={})
            )
        except ProjectBasicInformationVersionConflictError as exc:
            assert "already exists" in str(exc)
        else:
            raise AssertionError("Expected duplicate confirmed version to fail")


def test_init_db_creates_project_basic_information_records_table() -> None:
    engine = create_engine("sqlite:///:memory:", future=True)

    init_db(engine)

    assert inspect(engine).has_table("project_basic_information_records") is True


def _record(
    record_id: str,
    *,
    status: str,
    version: int,
    values: dict[str, str],
    updated_at: str = "2026-06-20T09:00:00+00:00",
) -> ProjectBasicInformationRecord:
    return ProjectBasicInformationRecord(
        record_id=record_id,
        project_id="P1",
        status=status,
        version=version,
        values=values,
        source_signature="{}",
        created_at="2026-06-20T09:00:00+00:00",
        updated_at=updated_at,
        confirmed_at=(
            "2026-06-20T09:00:00+00:00" if status == "confirmed" else None
        ),
        confirmed_by="Lab User" if status == "confirmed" else None,
    )
