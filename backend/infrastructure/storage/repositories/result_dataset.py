"""Persistence adapter for immutable result and report draft revisions."""

from __future__ import annotations

from dataclasses import asdict
from decimal import Decimal
import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.domain.result_dataset_models import (
    LlcrDatasetPayload,
    LlcrMeasurement,
    LlcrResultEntry,
    ReportDraftRevision,
    ResultDatasetRevision,
    ResultDatasetSourceIdentity,
)
from backend.infrastructure.storage.models_result_dataset import (
    ReportDraftRevisionModel,
    ResultDatasetRevisionModel,
)


class ResultDatasetRepository:
    """Store append-only dataset and report revisions."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create_dataset(self, revision: ResultDatasetRevision) -> ResultDatasetRevision:
        self._session.add(_dataset_model(revision))
        self._session.flush()
        return revision

    def commit(self) -> None:
        """Finalize one dataset/report revision transaction before file cleanup."""
        self._session.commit()

    def rollback(self) -> None:
        """Discard the current uncommitted dataset/report revision transaction."""
        self._session.rollback()

    def get_dataset(self, dataset_id: str) -> ResultDatasetRevision | None:
        row = self._session.get(ResultDatasetRevisionModel, dataset_id)
        return _dataset_domain(row) if row is not None else None

    def list_datasets(self, project_id: str) -> tuple[ResultDatasetRevision, ...]:
        rows = self._session.scalars(
            select(ResultDatasetRevisionModel)
            .where(ResultDatasetRevisionModel.project_id == project_id)
            .order_by(ResultDatasetRevisionModel.revision.asc())
        ).all()
        return tuple(_dataset_domain(row) for row in rows)

    def next_dataset_revision(self, project_id: str, dataset_type: str) -> int:
        latest = self._session.scalar(
            select(func.max(ResultDatasetRevisionModel.revision)).where(
                ResultDatasetRevisionModel.project_id == project_id,
                ResultDatasetRevisionModel.dataset_type == dataset_type,
            )
        )
        return int(latest or 0) + 1

    def create_report_revision(self, revision: ReportDraftRevision) -> ReportDraftRevision:
        self._session.add(_report_model(revision))
        self._session.flush()
        return revision

    def list_report_revisions(self, project_id: str) -> tuple[ReportDraftRevision, ...]:
        rows = self._session.scalars(
            select(ReportDraftRevisionModel)
            .where(ReportDraftRevisionModel.project_id == project_id)
            .order_by(ReportDraftRevisionModel.revision.asc())
        ).all()
        return tuple(_report_domain(row) for row in rows)

    def get_report_revision(self, report_revision_id: str) -> ReportDraftRevision | None:
        row = self._session.get(ReportDraftRevisionModel, report_revision_id)
        return _report_domain(row) if row is not None else None

    def latest_report_revision(self, project_id: str) -> ReportDraftRevision | None:
        row = self._session.scalar(
            select(ReportDraftRevisionModel)
            .where(ReportDraftRevisionModel.project_id == project_id)
            .order_by(ReportDraftRevisionModel.revision.desc())
            .limit(1)
        )
        return _report_domain(row) if row is not None else None

    def next_report_revision(self, project_id: str) -> int:
        latest = self._session.scalar(
            select(func.max(ReportDraftRevisionModel.revision)).where(
                ReportDraftRevisionModel.project_id == project_id
            )
        )
        return int(latest or 0) + 1


def _dataset_model(value: ResultDatasetRevision) -> ResultDatasetRevisionModel:
    return ResultDatasetRevisionModel(
        dataset_id=value.dataset_id,
        dataset_type=value.dataset_type,
        revision=value.revision,
        project_id=value.project_id,
        confirmed_matrix_id=value.confirmed_matrix_id,
        confirmed_matrix_revision=value.confirmed_matrix_revision,
        source_file_name=value.source.file_name,
        source_sha256=value.source.sha256,
        source_size_bytes=value.source.size_bytes,
        imported_at=value.imported_at,
        imported_by=value.imported_by,
        confirmed_at=value.confirmed_at,
        confirmed_by=value.confirmed_by,
        parser_profile_version=value.parser_profile_version,
        validation_status=value.validation_status,
        payload_json=json.dumps(asdict(value.payload), default=_json_default, ensure_ascii=False),
    )


def _dataset_domain(row: ResultDatasetRevisionModel) -> ResultDatasetRevision:
    payload = json.loads(row.payload_json)
    entries = []
    for item in payload["entries"]:
        measurements = tuple(
            LlcrMeasurement(
                sample_index=measurement["sample_index"],
                position=measurement["position"],
                value=Decimal(measurement["value"]),
                unit=measurement["unit"],
                source_sheet=measurement["source_sheet"],
                source_cell=measurement["source_cell"],
                raw_value=Decimal(measurement.get("raw_value", measurement["value"])),
                raw_unit=measurement.get("raw_unit", measurement["unit"]),
                raw_source_cell=measurement.get(
                    "raw_source_cell",
                    measurement["source_cell"],
                ),
            )
            for measurement in item["measurements"]
        )
        entries.append(
            LlcrResultEntry(
                result_id=item["result_id"],
                confirmed_group_id=item["confirmed_group_id"],
                group_label=item["group_label"],
                confirmed_row_id=item["confirmed_row_id"],
                matrix_step_sequence=item["matrix_step_sequence"],
                matrix_step_token=item["matrix_step_token"],
                stage=item["stage"],
                stage_label=item["stage_label"],
                requirement=item["requirement"],
                requirement_comparator=item["requirement_comparator"],
                requirement_limit=Decimal(item["requirement_limit"]),
                requirement_unit=item["requirement_unit"],
                measurements=measurements,
                summary_min=Decimal(item["summary_min"]),
                summary_max=Decimal(item["summary_max"]),
                summary_average=Decimal(item["summary_average"]),
                provisional_outcome=item["provisional_outcome"],
                confirmed_outcome=item["confirmed_outcome"],
                override_reason=item["override_reason"],
                source_range=item["source_range"],
            )
        )
    return ResultDatasetRevision(
        dataset_id=row.dataset_id,
        dataset_type=row.dataset_type,
        revision=row.revision,
        project_id=row.project_id,
        confirmed_matrix_id=row.confirmed_matrix_id,
        confirmed_matrix_revision=row.confirmed_matrix_revision,
        source=ResultDatasetSourceIdentity(
            row.source_file_name,
            row.source_sha256,
            row.source_size_bytes,
        ),
        imported_at=row.imported_at,
        imported_by=row.imported_by,
        confirmed_at=row.confirmed_at,
        confirmed_by=row.confirmed_by,
        parser_profile_version=row.parser_profile_version,
        validation_status=row.validation_status,
        payload=LlcrDatasetPayload(tuple(entries)),
    )


def _report_model(value: ReportDraftRevision) -> ReportDraftRevisionModel:
    return ReportDraftRevisionModel(**asdict(value))


def _report_domain(row: ReportDraftRevisionModel) -> ReportDraftRevision:
    return ReportDraftRevision(
        report_revision_id=row.report_revision_id,
        project_id=row.project_id,
        revision=row.revision,
        file_name=row.file_name,
        file_path=row.file_path,
        file_sha256=row.file_sha256,
        size_bytes=row.size_bytes,
        confirmed_matrix_id=row.confirmed_matrix_id,
        result_dataset_id=row.result_dataset_id,
        base_report_revision_id=row.base_report_revision_id,
        created_at=row.created_at,
        created_by=row.created_by,
    )


def _json_default(value):
    if isinstance(value, Decimal):
        return str(value)
    raise TypeError(f"Unsupported result dataset value: {type(value).__name__}")
