"""Fail-closed bootstrap for ResultDataset and Report Draft revision tables."""

from __future__ import annotations

from sqlalchemy.engine import Engine

from backend.infrastructure.storage.database import Base
from backend.infrastructure.storage.models_result_dataset import (
    ReportDraftRevisionModel,
    ResultDatasetRevisionModel,
)


RESULT_DATASET_TABLES = {
    ResultDatasetRevisionModel.__tablename__,
    ReportDraftRevisionModel.__tablename__,
}


def bootstrap_result_dataset_schema(engine: Engine) -> None:
    """Create the additive revision tables on existing ConnLab databases."""
    Base.metadata.create_all(
        bind=engine,
        tables=[
            ResultDatasetRevisionModel.__table__,
            ReportDraftRevisionModel.__table__,
        ],
    )
