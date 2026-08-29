from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from backend.domain.result_dataset_models import (
    LlcrDatasetPayload,
    LlcrMeasurement,
    LlcrResultEntry,
    ReportDraftRevision,
    ResultDatasetRevision,
    ResultDatasetSourceIdentity,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.repositories.result_dataset import (
    ResultDatasetRepository,
)
from backend.shared.config import Settings


def test_repository_persists_immutable_dataset_and_report_revisions(tmp_path) -> None:
    engine = create_database_engine(
        Settings(data_dir=tmp_path, projects_dir=tmp_path, templates_dir=tmp_path, database_path=tmp_path / "db.sqlite3")
    )
    init_db(engine)
    sessions = create_session_factory(engine)
    first = _dataset("dataset-1", 1)
    with sessions.begin() as session:
        repository = ResultDatasetRepository(session)
        repository.create_dataset(first)
        repository.create_report_revision(_report("report-1", 1, "dataset-1"))

    with sessions() as session:
        repository = ResultDatasetRepository(session)
        stored = repository.get_dataset("dataset-1")
        assert stored == first
        assert repository.next_dataset_revision("P1", "llcr") == 2
        assert repository.latest_report_revision("P1").result_dataset_id == "dataset-1"
        assert repository.next_report_revision("P1") == 2

    with pytest.raises(IntegrityError):
        with sessions.begin() as session:
            ResultDatasetRepository(session).create_dataset(
                replace(first, dataset_id="dataset-duplicate")
            )


def _dataset(dataset_id: str, revision: int) -> ResultDatasetRevision:
    measurement = LlcrMeasurement(
        1, "SIG1", Decimal("0.198"), "mΩ", "SIG", "K10",
        Decimal("0.248"), "mΩ", "D10",
    )
    entry = LlcrResultEntry(
        result_id="group-1:row-1:2",
        confirmed_group_id="group-1",
        group_label="1",
        confirmed_row_id="row-1",
        matrix_step_sequence=2,
        matrix_step_token="2",
        stage="initial",
        stage_label="Initial LLCR",
        requirement="≤0.25mΩ",
        requirement_comparator="<=",
        requirement_limit=Decimal("0.25"),
        requirement_unit="mΩ",
        measurements=(measurement,),
        summary_min=Decimal("0.198"),
        summary_max=Decimal("0.198"),
        summary_average=Decimal("0.198"),
        provisional_outcome="pass",
        confirmed_outcome="pass",
        source_range="SIG!K10:K10",
    )
    return ResultDatasetRevision(
        dataset_id=dataset_id,
        dataset_type="llcr",
        revision=revision,
        project_id="P1",
        confirmed_matrix_id="matrix-1",
        confirmed_matrix_revision=3,
        source=ResultDatasetSourceIdentity("LLCR.xlsx", "a" * 64, 512),
        imported_at="2026-08-29T08:00:00Z",
        imported_by="Even Yang",
        confirmed_at="2026-08-29T08:01:00Z",
        confirmed_by="Even Yang",
        parser_profile_version="connlab-llcr-macro-v1",
        validation_status="confirmed",
        payload=LlcrDatasetPayload((entry,)),
    )


def _report(report_id: str, revision: int, dataset_id: str | None) -> ReportDraftRevision:
    return ReportDraftRevision(
        report_revision_id=report_id,
        project_id="P1",
        revision=revision,
        file_name=f"report-r{revision}.docx",
        file_path=f"C:/reports/report-r{revision}.docx",
        file_sha256="b" * 64,
        size_bytes=2048,
        confirmed_matrix_id="matrix-1",
        result_dataset_id=dataset_id,
        base_report_revision_id=None,
        created_at="2026-08-29T08:02:00Z",
        created_by="Even Yang",
    )
