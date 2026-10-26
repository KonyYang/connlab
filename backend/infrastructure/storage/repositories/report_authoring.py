"""Persist immutable report preparation revisions with optimistic concurrency."""
from dataclasses import asdict, replace
import json
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from backend.domain.report_authoring import ReportAuthoringState, ReportSource, ReportMapping, ReportAuthoringConflict
from backend.infrastructure.storage.models_report_authoring import ReportAuthoringRevisionModel


class ReportAuthoringRepository:
    def __init__(self, session):
        self._session = session

    def get(self, project_id: str) -> ReportAuthoringState:
        row = self._session.scalar(select(ReportAuthoringRevisionModel).where(
            ReportAuthoringRevisionModel.project_id == project_id
        ).order_by(ReportAuthoringRevisionModel.revision.desc()).limit(1))
        if row is None:
            return ReportAuthoringState(project_id)
        data = json.loads(row.payload_json)
        return ReportAuthoringState(project_id, row.revision,
            tuple(ReportSource(**item) for item in data["sources"]),
            tuple(ReportMapping(**{**item, "sample_ids": tuple(item["sample_ids"])}) for item in data["mappings"]),
            data.get("base_source_id"), tuple(data.get("outputs", [])), tuple(data.get("results", [])),
            tuple(data.get('customer_outputs', [])))

    def save(self, state: ReportAuthoringState, expected_revision: int) -> ReportAuthoringState:
        if self.get(state.project_id).revision != expected_revision:
            raise ReportAuthoringConflict("Report sources changed. Reload and review your changes again.")
        updated = replace(state, revision=expected_revision + 1)
        try:
            with self._session.begin_nested():
                self._session.add(ReportAuthoringRevisionModel(project_id=state.project_id,
                    revision=updated.revision, payload_json=json.dumps(asdict(updated), ensure_ascii=False)))
                self._session.flush()
        except IntegrityError as exc:
            raise ReportAuthoringConflict("Another report edit completed first. Reload before saving.") from exc
        return updated
