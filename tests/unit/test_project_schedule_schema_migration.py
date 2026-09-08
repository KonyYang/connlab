import pytest
from sqlalchemy import create_engine, inspect, text

from backend.infrastructure.storage.project_schedule_schema_migration import (
    bootstrap_project_schedule_schema,
)


def test_bootstrap_creates_project_schedule_authority_table() -> None:
    engine = create_engine("sqlite://", future=True)

    bootstrap_project_schedule_schema(engine)

    assert "project_schedule_revisions" in inspect(engine).get_table_names()


def test_bootstrap_rejects_incompatible_existing_project_schedule_table() -> None:
    engine = create_engine("sqlite://", future=True)
    with engine.begin() as connection:
        connection.execute(text("create table project_schedule_revisions (revision_id text primary key)"))

    with pytest.raises(RuntimeError, match="authority_corrupt: Project Schedule"):
        bootstrap_project_schedule_schema(engine)
