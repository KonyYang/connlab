"""SQLite database foundation for ConnLab."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.infrastructure.storage.matrix_schedule_schema_migration import (
    migrate_matrix_schedule_planning_columns,
)
from backend.infrastructure.storage.matrix_contact_measurement_schema_migration import (
    migrate_matrix_contact_measurement_columns,
)
from backend.infrastructure.storage.contact_measurement_plan_authority_schema_migration import (
    migrate_contact_measurement_plan_authority_schema,
)
from backend.infrastructure.storage.contact_point_profile_schema_migration import (
    bootstrap_contact_point_profile_schema, migrate_contact_point_profile_schema,
)
from backend.infrastructure.storage.database_general_migrations import (
    _migrate_file_asset_provenance_columns,
    _migrate_ltr_duplicate_resolution_tables,
    _migrate_project_basic_information_records_table,
    _migrate_report_sample_authority_columns,
    _migrate_project_lifecycle_columns,
    _migrate_project_no_optional,
    _migrate_project_output_record_file_metadata,
)
from backend.infrastructure.storage.database_matrix_migrations import (
    _migrate_confirmed_matrix_supersession_columns,
    _migrate_project_matrix_draft_lineage_columns_optional,
    _migrate_project_matrix_draft_record_revision_columns,
    _migrate_project_matrix_draft_row_detail_columns,
    _migrate_source_matrix_import_commit_fingerprint,
    _migrate_source_matrix_import_preview_payload,
    _migrate_source_matrix_row_detail_columns,
)
from backend.shared.config import Settings
from backend.infrastructure.storage.standard_record_method_sync_schema_migration import (
    migrate_standard_record_method_sync_schema,
)


class Base(DeclarativeBase):
    """Base class for future SQLAlchemy ORM models."""


def build_sqlite_url(database_path: Path) -> str:
    """Build a SQLAlchemy SQLite URL from a filesystem path."""
    return f"sqlite:///{database_path.as_posix()}"


def create_database_engine(
    settings: Settings | None = None,
    **engine_options: Any,
) -> Engine:
    """Create a SQLAlchemy engine using the configured SQLite database path."""
    resolved_settings = settings or Settings.load()
    resolved_settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(
        build_sqlite_url(resolved_settings.database_path),
        future=True,
        **engine_options,
    )


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create the application session factory for a SQLAlchemy engine."""
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    """Create all registered SQLAlchemy tables for the supplied engine."""
    from backend.infrastructure.storage import models  # noqa: F401
    from backend.infrastructure.storage import models_confirmed_matrix_authority  # noqa: F401
    from backend.infrastructure.storage import models_project_matrix_draft  # noqa: F401
    from backend.infrastructure.storage import models_matrix_source  # noqa: F401
    from backend.infrastructure.storage import models_contact_measurement_plan_authority  # noqa: F401
    from backend.infrastructure.storage import models_contact_point_profile  # noqa: F401
    from backend.infrastructure.storage.matrix_duration_authority_schema import (
        MATRIX_DURATION_AUTHORITY_TABLES,
        bootstrap_matrix_duration_authority_schema,
    )

    dedicated_tables = {
        "contact_point_profile_roots", "contact_point_profile_revisions", "contact_point_profile_categories",
        "contact_point_profile_cr_category_selections",
        *MATRIX_DURATION_AUTHORITY_TABLES,
    }
    # Fail closed on an incompatible authority shape before generic startup DDL.
    bootstrap_matrix_duration_authority_schema(engine)
    general_tables = [
        table for table in Base.metadata.tables.values() if table.name not in dedicated_tables
    ]
    Base.metadata.create_all(bind=engine, tables=general_tables)
    migrate_standard_record_method_sync_schema(engine)
    _migrate_project_no_optional(engine)
    _migrate_file_asset_provenance_columns(engine)
    _migrate_project_output_record_file_metadata(engine)
    _migrate_confirmed_matrix_supersession_columns(engine)
    _migrate_project_matrix_draft_record_revision_columns(engine)
    _migrate_project_matrix_draft_lineage_columns_optional(engine)
    _migrate_project_matrix_draft_row_detail_columns(engine)
    migrate_matrix_schedule_planning_columns(engine)
    migrate_matrix_contact_measurement_columns(engine)
    migrate_contact_measurement_plan_authority_schema(engine)
    bootstrap_contact_point_profile_schema(engine)
    _migrate_source_matrix_import_commit_fingerprint(engine)
    _migrate_source_matrix_import_preview_payload(engine)
    _migrate_source_matrix_row_detail_columns(engine)
    _migrate_project_basic_information_records_table(engine)
    _migrate_report_sample_authority_columns(engine)
    _migrate_project_lifecycle_columns(engine)
    _migrate_ltr_duplicate_resolution_tables(engine)
