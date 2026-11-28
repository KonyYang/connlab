from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
import json

import pytest
from sqlalchemy.exc import IntegrityError

from backend.application.report_authoring.llcr_projection import dataset_sha256
from backend.domain.result_dataset_models import (
    LlcrDatasetPayload,
    LlcrMeasurement,
    LlcrResultEntry,
    LlcrSummaryRow,
    ReportDraftRevision,
    ResultDatasetRevision,
    ResultDatasetSourceIdentity,
)
from backend.infrastructure.storage.database import (
    create_database_engine,
    create_session_factory,
    init_db,
)
from backend.infrastructure.storage.models_result_dataset import ResultDatasetRevisionModel
from backend.infrastructure.office.test_report_document_gateway import llcr_dataset_sha256
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


def test_repository_reads_legacy_llcr_payload_without_summary_rows(tmp_path) -> None:
    engine = create_database_engine(
        Settings(
            data_dir=tmp_path,
            projects_dir=tmp_path,
            templates_dir=tmp_path,
            database_path=tmp_path / "legacy.sqlite3",
        )
    )
    init_db(engine)
    sessions = create_session_factory(engine)
    with sessions.begin() as session:
        ResultDatasetRepository(session).create_dataset(_dataset("legacy-dataset", 1))
    with sessions.begin() as session:
        row = session.get(ResultDatasetRevisionModel, "legacy-dataset")
        payload = json.loads(row.payload_json)
        payload.pop("summary_rows")
        measurement = payload["entries"][0]["measurements"][0]
        for key in ("raw_value", "raw_unit", "raw_source_cell"):
            measurement.pop(key)
        row.payload_json = json.dumps(payload)

    with sessions() as session:
        stored = ResultDatasetRepository(session).get_dataset("legacy-dataset")

    assert stored is not None
    assert stored.payload.summary_rows == ()
    assert len(stored.payload.entries) == 1
    legacy = stored.payload.entries[0].measurements[0]
    assert legacy.value == Decimal("0.198")
    assert legacy.raw_value is None
    assert legacy.raw_source_cell == ""
    # Fingerprint recorded by both report assembly and Word updates before raw readings were exposed.
    applied_sha256 = "e8452da19289b097c7e36f2f5cb23ad216c59db694786f4e40c53e6d4a2e3b10"
    assert dataset_sha256(stored) == llcr_dataset_sha256(stored) == applied_sha256
    entry = stored.payload.entries[0]
    for changed in (replace(legacy, value=Decimal("0.199")), replace(legacy, raw_value=Decimal("0.249"))):
        revised = replace(stored, payload=replace(stored.payload, entries=(replace(entry, measurements=(changed,)),)))
        assert dataset_sha256(revised) == llcr_dataset_sha256(revised) != applied_sha256


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
        payload=LlcrDatasetPayload(
            (entry,),
            (
                LlcrSummaryRow(
                    group_label="1",
                    stage_label="Initial LLCR",
                    summary_min=Decimal("0.198"),
                    summary_max=Decimal("0.198"),
                    summary_average=Decimal("0.198"),
                    summary_stdev=Decimal("0"),
                    source_row=3,
                    fill_color="FFFACD",
                ),
            ),
        ),
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
